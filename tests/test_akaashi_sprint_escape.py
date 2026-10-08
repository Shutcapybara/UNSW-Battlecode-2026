"""Queen safety compares sprint endpoints, while retaining legal body/length limits."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
CPP=r'''
#include "bokuto.hpp"
#include <cassert>
int main(int argc,char**argv) {
    ares::World w;w.W=w.H=12;w.NC=144;w.me=0;w.rnd=388;
    w.len=8;w.units=8;w.limit=64;w.head=78;w.face=3;
    w.body={94,93,92,80,68,67,79,78};w.own.assign(w.NC,0);
    for(int i=0;i<8;i++)w.own[w.body[i]]=i+1;
    w.occ.assign(w.NC,-1);w.pearl_seen.assign(w.NC,-1);
    w.seen.assign(w.NC,w.rnd+1);w.dest_tab.resize(w.NC*4);
    for(int c=0;c<w.NC;c++)for(int d=0;d<4;d++)w.dest_tab[c*4+d]=w.nbr(c,d);
    w.parts={{88,685,false,true,1,3}};w.enemy_heads={0};w.occ[88]=0;
    bokuto::Guard g;ares::Decision dec,out;dec.act=ares::Act::MOVE;dec.dirs={0};dec.why='q';char tag=0;
    bool changed=g.apply(w,dec,out,tag);
    if(argv[1][0]=='P'){assert(!changed);return 0;}
    assert(changed && out.dirs==std::vector<int>({0,0}) && tag=='Q');
    // No threat: preserve the incumbent move, avoiding gratuitous paid sprints.
    w.parts.clear();w.enemy_heads.clear();w.occ[88]=-1;g=bokuto::Guard();tag=0;
    assert(!g.apply(w,dec,out,tag));
}
'''
class SprintEscapeTest(unittest.TestCase):
    def test_endpoint_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'test.cpp';source.write_text(CPP)
            for bot,mode in [('akaashi-04-visible-body-safety','P'),('akaashi-05-sprint-queen-escape','F')]:
                exe=Path(tmp)/bot
                subprocess.run(['g++','-std=c++20','-O1','-I',str(ROOT/'bots'/bot),str(source),'-o',str(exe)],check=True)
                subprocess.run([str(exe),mode],check=True)
if __name__=='__main__':unittest.main()
