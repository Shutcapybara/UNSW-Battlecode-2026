"""Compare actual native evaluator outputs for old and lossless HB-1 storage."""
from pathlib import Path
import json
import subprocess
import numpy as np
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
old=ROOT/'bots/kenma-03-pocket-queen';new=ROOT/'bots/kenma-08-lossless-direction'
out=MAIN/'build/kenma/lossless-direction'
s=(old/'hb1_direction_compact.hpp').read_text().replace('namespace hb1 {','namespace legacy {')
(out/'legacy_direction.hpp').write_text(s)
s=(old/'hb1_compact.hpp').read_text().replace('"hb1_direction_compact.hpp"','"legacy_direction.hpp"').replace('namespace hb1 {','namespace legacy { using hb1::Model;')
(out/'legacy_compact.hpp').write_text(s)
features=(MAIN/'build/kenma/queen-action-v1/features.txt').read_text().splitlines()
x=pq.read_table(MAIN/'build/kenma/queen-action-v1/parity_rows.parquet',columns=features,use_threads=False).to_pandas().to_numpy(dtype=np.float32)
rng=np.random.default_rng(73)
extra=rng.uniform(-2,500,size=(1024,len(features))).astype(np.float32)
extra[rng.random(extra.shape)<0.05]=np.nan
x=np.concatenate([x,extra])
x.tofile(out/'rows.f32')
(out/'check.cpp').write_text(r'''
#include <fstream>
#include <iostream>
#include <cstring>
#include "hb1_compact.hpp"
#include "legacy_compact.hpp"
int main(int argc,char** argv) {
    if (argc!=2) return 2;
    std::ifstream in(argv[1],std::ios::binary);
    std::vector<float> x(270);
    int rows=0;
    while(in.read(reinterpret_cast<char*>(x.data()),x.size()*sizeof(float))) {
        auto a=legacy::dirc_proba(x),b=hb1::dirc_proba(x);
        if(std::memcmp(a.data(),b.data(),3*sizeof(double))) {
            std::cerr<<"Mismatch row "<<rows<<"\n"; return 1;
        }
        ++rows;
    }
    if(!in.eof() || rows==0) return 3;
    std::cout<<rows<<" bit-exact probability vectors\n";
}
''')
subprocess.run(['clang++','-O2','-std=c++20','-I'+str(new),str(out/'check.cpp'),'-o',str(out/'check')],check=True)
p=subprocess.run([str(out/'check'),str(out/'rows.f32')],check=True,text=True,capture_output=True)
assert p.stdout.startswith(str(len(x))+' ')
r=json.loads((out/'report.json').read_text());r['native_bit_exact_probability_rows']=len(x);r['synthetic_rows_including_nan']=len(extra)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
print(p.stdout.strip(),flush=True)
