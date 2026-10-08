"""Late valuable heads dodge sprint threats even with incomplete own-body chains."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
CPP=r'''
#include "bokuto.hpp"
#include <cassert>
ares::World world() {
    ares::World w;w.W=w.H=12;w.NC=144;w.me=1590;w.rnd=494;
    w.len=72;w.units=3;w.limit=64;w.head=78;w.face=3;
    w.body={81,80,79,78};w.own.assign(w.NC,0);
    for(int i=0;i<4;i++)w.own[w.body[i]]=i+1;
    w.visible_own=w.body;w.occ.assign(w.NC,-1);w.pearl_seen.assign(w.NC,-1);
    w.seen.assign(w.NC,w.rnd+1);w.dest_tab.resize(w.NC*4);
    for(int c=0;c<w.NC;c++)for(int d=0;d<4;d++)w.dest_tab[c*4+d]=w.nbr(c,d);
    w.parts={{88,1795,false,true,1,3}};w.enemy_heads={0};w.occ[88]=0;
    return w;
}
int main(int argc,char**argv) {
    auto w=world();bokuto::Guard g;ares::Decision dec,out;
    dec.act=ares::Act::MOVE;dec.dirs={0};dec.why='p';char tag=0;
    bool changed=g.apply(w,dec,out,tag);
    if(argv[1][0]=='P'){assert(!changed);return 0;}
    assert(changed && out.dirs==std::vector<int>({0,0}) && tag=='L');
    w=world();w.rnd=379;g=bokuto::Guard();assert(!g.apply(w,dec,out,tag));
    w=world();w.len=11;g=bokuto::Guard();assert(!g.apply(w,dec,out,tag));
    w=world();dec.why='f';g=bokuto::Guard();assert(!g.apply(w,dec,out,tag));
    // Visible disconnected own cells are obstacles to the continuation search.
    w=world();w.visible_own.push_back(66);g=bokuto::Guard();
    assert(g.after_path(w,{0},6).turns==0);
}
'''
class LateMaterialTest(unittest.TestCase):
    def test_partial_asset_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'test.cpp';source.write_text(CPP)
            for bot,mode in [('akaashi-05-sprint-queen-escape','P'),('akaashi-06-late-material-safety','F')]:
                exe=Path(tmp)/bot
                subprocess.run(['g++','-std=c++20','-O1','-I',str(ROOT/'bots'/bot),str(source),'-o',str(exe)],check=True)
                subprocess.run([str(exe),mode],check=True)
if __name__=='__main__':unittest.main()
