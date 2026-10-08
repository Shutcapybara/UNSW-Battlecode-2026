"""A partial own-body chain cannot hide visible obstacles or masquerade as a tail."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include "policy.hpp"
#include <cassert>
int main(int argc,char** argv) {
    ares::World w;w.W=w.H=12;w.NC=144;w.head=26;w.len=16;
    w.body={24,25,26};w.occ.assign(w.NC,-1);w.pearl_seen.assign(w.NC,-1);
    w.dest_tab.resize(w.NC*4);
    for(int c=0;c<w.NC;c++) for(int d=0;d<4;d++)w.dest_tab[c*4+d]=w.nbr(c,d);
    #ifdef FIXED
    w.visible_own={24,25,26,27};
#endif
    ares::Policy p;bool fixed=argv[1][0]=='F';
    assert((p.simulate(w,{1}).status==ares::Policy::SimStatus::DEAD)==fixed);
    #ifdef FIXED
    w.visible_own.pop_back();
#endif
    assert((p.simulate(w,{0,3,2}).status==ares::Policy::SimStatus::DEAD)==fixed);
    // Fully known bodies still release their actual tail, retaining legal routes.
    w.len=8;w.body={24,25,37,38,39,40,41,26};
#ifdef FIXED
    w.visible_own.clear();
#endif
    assert(p.simulate(w,{0,3,2}).status==ares::Policy::SimStatus::OK);
    assert(p.simulate(w,{0}).status==ares::Policy::SimStatus::OK);
}
'''
class VisibleBodyTest(unittest.TestCase):
    def test_partial_and_complete_bodies(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'test.cpp';source.write_text(CPP)
            for bot,mode in [('akaashi-03-threatened-queen-split','P'),('akaashi-04-visible-body-safety','F'),('akaashi-05-sprint-queen-escape','F')]:
                exe=Path(tmp)/bot
                subprocess.run(['g++','-std=c++20','-O1','-I',str(ROOT/'bots'/bot),str(source),'-o',str(exe)]+(['-DFIXED'] if mode=='F' else []),check=True)
                subprocess.run([str(exe),mode],check=True)
if __name__=='__main__':unittest.main()
