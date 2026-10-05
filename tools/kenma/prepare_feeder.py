"""Export the fixed donor classifier into a new snapshot and verify native parity."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile
import numpy as np
import lightgbm as lgb
import pyarrow.parquet as pq
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(ROOT/'tools/learn'))
import export_gbt
src=ROOT/'bots/kenma-08-lossless-direction';dst=ROOT/'bots/kenma-09-learned-donors'
out=MAIN/'build/kenma/feeder-v1'
assert not dst.exists(), 'Never overwrite a snapshot'
report=json.loads((out/'report.json').read_text())
assert report['fixed_play_threshold']==0.9
assert hashlib.sha256((out/'model.txt').read_bytes()).hexdigest()==report['model_sha256']
shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__'))
shutil.copy2(ROOT/'tools/learn/cpp/gbt_compact.hpp',dst/'gbt_compact.hpp')
info=export_gbt.emit(export_gbt.from_lgb(str(out/'model.txt')),str(dst/'kenma_feed_model.hpp'),'kenma_feed')
assert info['K']==1
(dst/'kenma_feed.hpp').write_text('''// Donor classifier: only current legal HB-1 features; original queens excluded.
#pragma once
#include "policy.hpp"
#include "gbt_compact.hpp"
#include "kenma_feed_model.hpp"
namespace kenma {
inline double donor_probability(float const* x) {
    double margin[1];
    gbt::margins(kenma_feed::K,kenma_feed::N_TREES,kenma_feed::CMP,kenma_feed::BASE,
        kenma_feed::TREE_NODE,kenma_feed::TREE_LEAF,kenma_feed::THR,kenma_feed::F,
        kenma_feed::T,kenma_feed::R,kenma_feed::LEAF,x,margin);
    return 1.0/(1.0+std::exp(-margin[0])); // Binary margin; multiclass softmax would be wrong here.
}
inline bool learned_donor(ares::World const& w,hb1::Row const& row) {
    if (w.me<=1 || w.len>8 || w.units<2 || w.ally_heads.empty()) return false;
    static hb1::Bound const bound{hb1::dirc_bind};
    auto x=bound.vec(row);
    return donor_probability(x.data())>=0.9;
}
}
''')
p=dst/'main.cpp';s=p.read_text().replace('#include "kenma_pocket.hpp"','#include "kenma_pocket.hpp"\n#include "kenma_feed.hpp"')
needle='            const int real_limit=w.limit;'
assert needle in s
s=s.replace(needle,'''            if (pol.hb_row && kenma::learned_donor(w,*pol.hb_row)) {
                std::cout << "SPLIT 1\\nLOG kenma_learned_donor\\nPROTOCOL 3\\nENDTURN\\n" << std::flush;
                continue;
            }
'''+needle);p.write_text(s)
features=(out/'features.txt').read_text().splitlines()
X=pq.read_table(out/'parity_rows.parquet',columns=features,use_threads=False).to_pandas().to_numpy(dtype=np.float32)
X.tofile(out/'parity.f32')
(out/'parity.cpp').write_text(r'''
#include <fstream>
#include <iostream>
#include <iomanip>
#include "kenma_feed.hpp"
int main(int argc,char**argv) {
    if(argc!=2)return 2;
    std::ifstream in(argv[1],std::ios::binary);std::vector<float>x(270);
    std::cout<<std::setprecision(17);
    while(in.read(reinterpret_cast<char*>(x.data()),x.size()*sizeof(float)))std::cout<<kenma::donor_probability(x.data())<<"\n";
    return in.eof()?0:3;
}
''')
subprocess.run(['clang++','-O2','-std=c++20','-I'+str(dst),str(out/'parity.cpp'),'-o',str(out/'parity')],check=True)
p=subprocess.run([str(out/'parity'),str(out/'parity.f32')],check=True,text=True,capture_output=True)
native=np.fromstring(p.stdout,sep='\n')
model=lgb.Booster(model_file=str(out/'model.txt'));ref=model.predict(X,num_threads=1)
assert len(native)==len(ref) and np.array_equal(native>=0.9,ref>=0.9)
error=float(np.max(np.abs(native-ref)));assert error<1e-6
(dst/'README.md').write_text('''# Kenma 09 — learned nonqueen donors

Parent: kenma-08-lossless-direction (Kenma 03 strategy with exact smaller direction storage). Adds a binary LightGBM clone of teacher 306's invalid-command donor actions. Original queens are excluded; eligibility is length <= 8, at least two team units and a visible allied head. Probability >= 0.9 emits SPLIT 1 to deliberately die and leave food. Existing sealed-pocket donors run first; all other parent decisions are preserved.

Training: 208,158 eligible oracle turns, 4,311 culls, original train split only, held-out maps excluded. Fixed 160 rounds, 31 leaves, no class reweighting. Development validation holds out 12 series (46,316 rows) from 48 training series: at the preselected 0.9 threshold, 653 TP, 2 FP, 231 FN, 45,430 TN (precision 99.69%, recall 73.87%). These numbers do not establish playing strength or calibration on this bot's own states. Final model refits the fixed settings on all eligible rows.

Model SHA-256: '''+report['model_sha256']+'''. Uses only the same 270 legal HB-1 inputs; no map identity. Reproduce with tools/kenma/feeder_train.py and prepare_feeder.py, output main build/kenma/feeder-v1/. Binary inference applies sigmoid to the raw margin, not the generic multiclass softmax.

Export verification: '''+str(len(X))+''' native rows, all threshold decisions equal, maximum probability error '''+str(error)+'''. Status: unmeasured, not best. Full native comparison and exact-source sandbox checks required. Seeds 11–13/new maps remain reserved.
''')
with zipfile.ZipFile(out/f'{dst.name}.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(dst.iterdir()):
        if p.is_file() and (p.suffix in ('.cpp','.hpp','.h','.cc','.toml','.md') or p.name=='.gitignore'):z.write(p,p.name)
meta=dict(export=info,parity_rows=len(X),all_threshold_decisions_equal=True,max_probability_error=error,zip_bytes=(out/f'{dst.name}.zip').stat().st_size)
(out/'export.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True)
