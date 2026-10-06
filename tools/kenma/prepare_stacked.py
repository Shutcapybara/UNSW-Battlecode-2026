"""Build the existing A5 development fold0 prior on the lossless text control."""
from pathlib import Path
import json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
out=MAIN/'build/kenma/stacked-prior'
dst=ROOT/'bots/kenma-17-stacked-direction-prior'
assert not dst.exists()
shutil.copytree(ROOT/'bots/kenma-16-lossless-model-text',dst)
for f in ('learn_helper.hpp','learn_encode.hpp','gbt_compact.hpp'):
    shutil.copy2(ROOT/'bots/kageyama-01-p1-slot'/f,dst/f)
shutil.copy2(out/'A5-400-f0.hpp',dst/'kenma_stacked_model.hpp')
(dst/'kenma_stacked.hpp').write_text(r'''// Combined legal observation inputs, in verified training order.
#pragma once
#include <array>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include "learn_helper.hpp"
#include "gbt_compact.hpp"
#include "kenma_stacked_model.hpp"
namespace kenma {
static_assert(learn::N_X==1193 && kenma_stacked::N_FEAT==1466 && kenma_stacked::K==4);
struct Stacked {
    learn::Encoder enc;
    std::array<float,1466> x{};
    std::array<double,4> p{};
    Stacked(unswbc::Controller const& ct,unswbc::Game const& game):enc(learn::spawn_from(ct,game)){}
    void observe(unswbc::Controller const& ct,unswbc::Game const& game,hb1::Row const* row) {
        auto const& ex=enc.observe(learn::block_from(ct,game));
        if(!row)throw std::runtime_error("missing HB row");
        static hb1::Bound const bound{hb1::dirc_bind};
        auto hx=bound.vec(*row);
        auto hp=hb1::dirc_proba(hx);
        for(int i=0;i<learn::N_X;++i)x[i]=static_cast<float>(ex[i]);
        for(int i=0;i<270;++i)x[1193+i]=hx[i];
        for(int i=0;i<3;++i) {
            char text[32];std::snprintf(text,sizeof(text),"%.6f",hp[i]);
            x[1463+i]=std::strtof(text,nullptr);
        }
        GBT_PROBA(kenma_stacked,x.data(),p.data());
    }
    void act(int kind,int first_rel,int steps,int round){enc.act(kind,first_rel,steps,round);}
};
}
''')
p=dst/'policy.hpp';s=p.read_text().replace('    hb1::Row const* hb_row = nullptr;', '    double const* kenma_stacked_p = nullptr;\n    hb1::Row const* hb_row = nullptr;')
s=s.replace('''        if (Params::hb1_dir_lambda > 0 && hb_row) {
            static hb1::Bound const dir_bound''','''        if (Params::hb1_dir_lambda > 0 && kenma_stacked_p) {
            double z=kenma_stacked_p[0]+kenma_stacked_p[1]+kenma_stacked_p[3];
            for(int rel:{0,1,3}) {
                int d=(w.face+rel)&3;
                hb_logp[d]=Params::hb1_dir_lambda*std::log(std::max(kenma_stacked_p[rel]/std::max(z,1e-30),1e-4));
            }
        } else if (Params::hb1_dir_lambda > 0 && hb_row) {
            static hb1::Bound const dir_bound''')
assert s.count('double z=kenma_stacked_p')==1;p.write_text(s)
p=dst/'main.cpp';s=p.read_text().replace('#include "kenma_pocket.hpp"','#include "kenma_pocket.hpp"\n#include "kenma_stacked.hpp"')
s=s.replace('    w.init(ct, game);','    w.init(ct, game);\n    kenma::Stacked stacked(ct,game);')
s=s.replace('        bool ok = true;',r'''        pol.kenma_stacked_p=nullptr;
        try {
            stacked.observe(ct,game,pol.hb_row);
            pol.kenma_stacked_p=stacked.p.data();
        } catch (...) {
            std::cout << "LOG kenma_stacked_fallback\n";
        }
        bool ok = true;''')
s=s.replace('''            if (kenma::donor(w)) {
                std::cout''','''            if (kenma::donor(w)) {
                stacked.act(3,-1,0,game.get_round_num());
                std::cout''')
s=s.replace('''            std::cout << "MOVE " << ares::dir_char(fallback_dir)''','''            stacked.act(1,(fallback_dir-ares::dir_index(ct.get_dir())+4)&3,1,game.get_round_num());
            std::cout << "MOVE " << ares::dir_char(fallback_dir)''')
s=s.replace('''        if (dec.act == ares::Act::SPLIT) {
            hproc.record_split(dec.split);''','''        if (dec.act==ares::Act::SPLIT) stacked.act(2,-1,0,game.get_round_num());
        else if(!dec.dirs.empty()) stacked.act(1,(dec.dirs.front()-ares::dir_index(ct.get_dir())+4)&3,static_cast<int>(dec.dirs.size()),game.get_round_num());
        else stacked.act(3,-1,0,game.get_round_num());
        if (dec.act == ares::Act::SPLIT) {
            hproc.record_split(dec.split);''')
p.write_text(s)
(dst/'README.md').write_text('''# Kenma17 — combined learned direction prior

Parent: kenma-16-lossless-model-text, strategy equivalent to03. Replace the search's first-step prior with Hinata's existing A5 development fold0, explicitly truncated to400 rounds. Inputs:1193 encoder-v1 values,270 HB values in verified parent binding order, and three parent HB probabilities rounded as the training exporter (six decimal places then float32). All118 HB side-file hashes match the training manifest; encoder allowlist order matches the C++ twin. Four classes F/R/B/L; search normalizes F/R/L and leaves reverse at the parent's zero prior. Weight1.0 unchanged. Parent fallback is logged explicitly. No new fit or map identity inputs.

The combined prior requires the original HB model as an input. Kenma16's lossless text encoding makes both models fit in4MiB. Original pocket-rescue, donor, slot-reserve, path-scoring and split logic remain; no orbit or corridor caution.

Model provenance: existing A5-u model_f0.txt reconstructed from verified archive parts; SHA6695befe886641235869dfea42d51f42816dec17eb621b037963f230d23b899b. This is a development-fold model, not a full-data fit. Pooled five-fold A5-400 offline accuracy72.67% is a source result, not a playing-strength claim for this snapshot.

Status: prepared, unmeasured. Full runtime feature/prediction parity, fallback audit and exact-source sandbox cost remain required. Reserved seeds11–13/new maps untouched. Generator tools/kenma/prepare_stacked.py; evidence main build/kenma/stacked-prior/.
''')
with zipfile.ZipFile(out/f'{dst.name}.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(dst.iterdir()):
        if p.is_file():z.write(p,p.name)
report={'bot':dst.name,'zip_bytes':(out/f'{dst.name}.zip').stat().st_size,'features':1466,'classes':['F','R','B','L'],'trees':1600,'status':'prepared, parity and sandbox cost unverified'}
assert report['zip_bytes']<=4*1024**2
(out/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
