"""Build Kenma 04: pocket rescue plus the small keeper-queen action clone."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(ROOT/'tools/learn'))
import export_gbt
out=MAIN/'build/kenma/queen-action-v1'
dst=ROOT/'bots/kenma-04-keeper-action'
shutil.copytree(ROOT/'bots/kenma-03-pocket-queen',dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__'))
shutil.copy2(ROOT/'tools/learn/cpp/gbt_compact.hpp',dst/'gbt_compact.hpp')
info=export_gbt.emit(export_gbt.from_lgb(str(out/'model.txt')),str(dst/'kenma_queen_model.hpp'),'kenma_queen')
(dst/'kenma_action.hpp').write_text('''// Queen-only action clone from five keeper teams. All inputs are current legal HB-1 features.
#pragma once
#include "policy.hpp"
#include "gbt_compact.hpp"
#include "kenma_queen_model.hpp"
namespace kenma {
inline void learned_queen(ares::World const& w, ares::Policy& pol, hb1::Row const& row, ares::Decision& out) {
    static hb1::Bound const bound{hb1::dirc_bind};
    auto x=bound.vec(row);
    double p[7];
    GBT_PROBA(kenma_queen,x.data(),p);
    double best=-1.0;
    ares::Decision selected=out;
    for (int rel=0; rel<4; ++rel) {
        int d=(w.face+rel)&3;
        auto sim=pol.simulate(w,{d});
        if (sim.status!=ares::Policy::SimStatus::OK && sim.status!=ares::Policy::SimStatus::DIVE) continue;
        if (p[rel]>best) {
            best=p[rel]; selected.act=ares::Act::MOVE; selected.dirs={d}; selected.why='k';
            // Retain a fully checked, free sprint from the parent when its first step agrees.
            if (out.act==ares::Act::MOVE && !out.dirs.empty() && out.dirs.front()==d &&
                static_cast<int>(out.dirs.size())<=(w.len+3)/4 &&
                pol.simulate(w,out.dirs).status==ares::Policy::SimStatus::OK) selected.dirs=out.dirs;
        }
    }
    if (w.len>=4 && w.units<w.limit) {
        int children[3]={2,w.len-2,std::clamp(w.len/2,2,w.len-2)};
        for (int k=0; k<3; ++k) if (p[k+4]>best) {
            best=p[k+4]; selected.act=ares::Act::SPLIT; selected.split=children[k]; selected.why='k';
        }
    }
    if (best>=0) out=selected;
}
}
''')
p=dst/'main.cpp'
s=p.read_text().replace('#include "kenma_pocket.hpp"','#include "kenma_pocket.hpp"\n#include "kenma_action.hpp"')
s=s.replace('            kenma::queen(w,pol,dec);','''            if (w.me<=1 && pol.hb_row && !kenma::pocket_size(w))
                kenma::learned_queen(w,pol,*pol.hb_row,dec);
            kenma::queen(w,pol,dec);''')
p.write_text(s)
sha=hashlib.sha256((out/'model.txt').read_bytes()).hexdigest()
(dst/'README.md').write_text('''# Kenma 04 — keeper action clone\n\nParent: kenma-03-pocket-queen, exact pocket behavior and one reserved slot retained. Outside sealed pockets, original queens use a seven-class action model: F/R/B/L, split two, retain two, split half. Immediately lethal single steps are masked; the parent supplies a safe free sprint when its first step agrees. Other dragons use the parent unchanged.\n\nTraining: 26,820 oracle queen turns from keeper teams 91, 213, 507, 842, 55, training split only, no map-identity inputs. The same 270 HB-1 inputs are bound in the verified parent order. A fixed 128-round, 15-leaf LightGBM model scored 81.75% action accuracy on 7,223 rows from 17 held-out development series (majority 32.71%), then refit on all 26,820 rows. This is offline imitation evidence, not play strength.\n\nModel SHA-256: '''+sha+'''. Reproduce with tools/kenma/queen_train.py and prepare_queen.py; output main build/kenma/queen-action-v1/.\n\nStatus: unmeasured candidate; head-to-head and deployment checks required.\n''')
with zipfile.ZipFile(out/'kenma-04-keeper-action.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(dst.iterdir()):
        if p.is_file():z.write(p,p.name)
size=(out/'kenma-04-keeper-action.zip').stat().st_size
print(json.dumps(dict(export=info,zip_bytes=size,under_limit=size<=4*1024**2)),flush=True)
(out/'export.json').write_text(json.dumps(dict(export=info,zip_bytes=size,model_sha256=sha),indent=2)+'\n')
assert size<=4*1024**2
