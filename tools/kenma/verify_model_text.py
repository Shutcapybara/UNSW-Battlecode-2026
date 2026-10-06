"""Check every decoded node and bit-exact probabilities against Kenma08."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
old=ROOT/'bots/kenma-08-lossless-direction';new=ROOT/'bots/kenma-16-lossless-model-text'
out=MAIN/'build/kenma/lossless-model-text'
s=(old/'hb1_direction_compact.hpp').read_text().replace('namespace hb1 {','namespace legacy {')
(out/'legacy_direction.hpp').write_text(s)
s=(old/'hb1_compact.hpp').read_text().replace('"hb1_direction_compact.hpp"','"legacy_direction.hpp"').replace('namespace hb1 {','namespace legacy { using hb1::Model;')
(out/'legacy_compact.hpp').write_text(s)
(out/'check.cpp').write_text(r'''#include <fstream>
#include <iostream>
#include <cstring>
#include "hb1_compact.hpp"
#include "legacy_compact.hpp"
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    static_assert(hb1::dirc_node_count==sizeof(legacy::dirc_nodes)/sizeof(legacy::dirc_nodes[0]));
    for(int i=0;i<hb1::dirc_node_count;++i)if(hb1::dirc_node(i)!=legacy::dirc_nodes[i]) {
        std::cerr<<"Node mismatch "<<i<<"\n";return 1;
    }
    std::ifstream in(argv[1],std::ios::binary);std::vector<float> x(270);int rows=0;
    while(in.read(reinterpret_cast<char*>(x.data()),x.size()*sizeof(float))) {
        auto a=legacy::dirc_proba(x),b=hb1::dirc_proba(x);
        if(std::memcmp(a.data(),b.data(),3*sizeof(double))) {
            std::cerr<<"Probability mismatch "<<rows<<"\n";return 1;
        }
        ++rows;
    }
    if(!in.eof() || rows!=21024)return 3;
    std::cout<<hb1::dirc_node_count<<" exact nodes; "<<rows<<" bit-exact probability vectors\n";
}
''')
subprocess.run(['clang++','-O2','-std=c++20','-Wno-overlength-strings','-I'+str(new),str(out/'check.cpp'),'-o',str(out/'check')],check=True)
p=subprocess.run([str(out/'check'),str(MAIN/'build/kenma/lossless-direction/rows.f32')],check=True,capture_output=True,text=True)
r=json.loads((out/'report.json').read_text());r['native_exact_nodes']=824580;r['native_bit_exact_probability_rows']=21024;r['synthetic_rows_including_nan']=1024
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(p.stdout.strip(),flush=True)
