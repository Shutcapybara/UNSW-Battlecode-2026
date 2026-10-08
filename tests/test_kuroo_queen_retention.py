"""Late queens use legal sprint escapes and obstructing crowns can feed them."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include "bokuto.hpp"
#include <cassert>
int main() {
    ares::Policy p; ares::World w;
    w.W=w.H=12; w.NC=144; w.me=573; w.rnd=436;
    w.len=37; w.head=100; w.body={78,79,100};
    p.role_feeder=true; p.feed_id=p.queen_id=1;
    p.queen_cell=77; p.queen_round=436;
    assert(p.body_blocks_queen_feed(w));
    p.queen_round=433; assert(!p.body_blocks_queen_feed(w));
    p.queen_round=436; p.role_feeder=false; assert(!p.body_blocks_queen_feed(w));
    p.role_feeder=true; p.feed_id=9; assert(!p.body_blocks_queen_feed(w));
    p.feed_id=1; w.rnd=399; assert(!p.body_blocks_queen_feed(w));
    w.rnd=436; w.len=7; assert(!p.body_blocks_queen_feed(w));
    w.len=37; w.me=1; assert(!p.body_blocks_queen_feed(w));
    w.me=573; w.body={90,91,100}; assert(!p.body_blocks_queen_feed(w));

    // A safe two-step endpoint must beat a threatened single-step landing.
    w=ares::World(); w.W=w.H=12; w.NC=144; w.me=1; w.rnd=388;
    w.len=8; w.units=8; w.limit=64; w.head=78; w.face=3;
    w.body={94,93,92,80,68,67,79,78}; w.own.assign(w.NC,0);
    for(int i=0;i<8;i++) w.own[w.body[i]]=i+1;
    w.occ.assign(w.NC,-1); w.pearl_seen.assign(w.NC,-1);
    w.seen.assign(w.NC,w.rnd+1); w.dest_tab.resize(w.NC*4);
    for(int c=0;c<w.NC;c++) for(int d=0;d<4;d++) w.dest_tab[c*4+d]=w.nbr(c,d);
    w.parts={{88,685,false,true,1,3}}; w.enemy_heads={0}; w.occ[88]=0;
    bokuto::Guard g; ares::Decision dec,out; dec.act=ares::Act::MOVE;
    dec.dirs={0}; dec.why='q'; char tag=0;
    assert(g.apply(w,dec,out,tag));
    assert(out.dirs==std::vector<int>({0,0}) && tag=='Q');
    assert(p.simulate(w,out.dirs).status==ares::Policy::SimStatus::OK);
    // The closed four-cell cage still needs a split.
    w.parts.clear(); w.enemy_heads.clear(); w.occ.assign(w.NC,-1);
    w.len=4; w.body={79,91,90,78}; w.own.assign(w.NC,0);
    for(int i=0;i<4;i++) w.own[w.body[i]]=i+1;
    w.dest_tab.assign(w.NC*4,ares::BLOCKED);
    auto edge=[&](int a,int d,int b){w.dest_tab[a*4+d]=b;w.dest_tab[b*4+((d+2)&3)]=a;};
    edge(78,1,79);edge(79,2,91);edge(91,3,90);edge(90,0,78);
    dec.act=ares::Act::SPLIT;dec.split=2;g=bokuto::Guard();
    assert(!g.apply(w,dec,out,tag));
}
'''

class QueenRetentionTest(unittest.TestCase):
    def test_feed_and_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'case.cpp'
            source.write_text(CPP)
            exe = Path(tmp) / 'case'
            subprocess.run(['g++', '-std=c++20', '-O1', '-I',
                            str(ROOT / 'bots/kuroo-03-queen-retention'),
                            str(source), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)

if __name__ == '__main__':
    unittest.main()
