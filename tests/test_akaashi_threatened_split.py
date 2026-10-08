"""Threatened queens should dodge instead of shedding; cages retain escape splits."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include "bokuto.hpp"
#include <cassert>
ares::World world() {
    ares::World w; w.W=w.H=12; w.NC=144; w.me=0; w.rnd=109;
    w.len=4; w.units=1; w.limit=64; w.head=78; w.face=3;
    w.body={81,80,79,78}; w.own.assign(w.NC,0);
    for(int i=0;i<4;i++) w.own[w.body[i]]=i+1;
    w.occ.assign(w.NC,-1);w.pearl_seen.assign(w.NC,-1);
    w.seen.assign(w.NC,w.rnd+1); w.dest_tab.resize(w.NC*4);
    for(int c=0;c<w.NC;c++) for(int d=0;d<4;d++) w.dest_tab[c*4+d]=w.nbr(c,d);
    return w;
}
int main(int argc,char** argv) {
    auto w=world();
    w.parts={{114,51,false,true,0,3}};w.enemy_heads={0};w.occ[114]=0;
    ares::DragonMem enemy;enemy.id=51;enemy.vis_len=2;enemy.cut=true;
    w.mem[51]=enemy;
    ares::Decision dec,out;dec.act=ares::Act::SPLIT;dec.split=2;dec.why='s';
    bokuto::Guard g;char tag=0;bool changed=g.apply(w,dec,out,tag);
    if(argv[1][0]=='S') {assert(!changed);return 0;}
    assert(changed && out.act==ares::Act::MOVE);
    assert(out.dirs==(argv[1][0]=='B' ? std::vector<int>({0,0}) : std::vector<int>({0})));
    assert(tag=='Q');
    // No observed danger: retain the ordinary split.
    w=world();g=bokuto::Guard();tag=0;assert(!g.apply(w,dec,out,tag));
    // Four-cell cage: the full body cannot move, but splitting permits circling.
    w=world();w.dest_tab.assign(w.NC*4,ares::BLOCKED);
    auto edge=[&](int a,int d,int b){w.dest_tab[a*4+d]=b;w.dest_tab[b*4+((d+2)&3)]=a;};
    edge(78,1,79);edge(79,2,91);edge(91,3,90);edge(90,0,78);
    w.body={79,91,90,78};w.own.assign(w.NC,0);
    for(int i=0;i<4;i++) w.own[w.body[i]]=i+1;
    g=bokuto::Guard();tag=0;assert(!g.apply(w,dec,out,tag));
    // Unknown length gets four-step threat coverage.
    w=world();w.parts={{82,51,false,true,0,3}};w.enemy_heads={0};w.occ[82]=0;
    g=bokuto::Guard();g.mark_heads(w);assert(g.enemy_reach[78]);
    // One enemy's marked cells must not obstruct another enemy's BFS.
    w=world();w.parts={{77,10,false,true,0,3},{80,51,false,true,0,3}};
    w.enemy_heads={0,1};w.occ[77]=0;w.occ[80]=1;
    g=bokuto::Guard();g.mark_heads(w);assert(g.enemy_reach[83]);
}
'''


class ThreatenedSplitTest(unittest.TestCase):
    def test_split_dodge_and_threat_union(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'regression.cpp'
            source.write_text(CPP)
            for bot, expected in [('akaashi-02-queen-strike', 'S'),
                                  ('akaashi-03-threatened-queen-split', 'N'),
                                  ('akaashi-04-visible-body-safety', 'N'),
                                  ('akaashi-05-sprint-queen-escape', 'B')]:
                exe = Path(tmp) / bot
                subprocess.run(['g++', '-std=c++20', '-O1', '-I', str(ROOT / 'bots' / bot),
                                str(source), '-o', str(exe)], check=True)
                subprocess.run([str(exe), expected], check=True)


if __name__ == '__main__':
    unittest.main()
