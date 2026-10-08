"""Queen escape regression: a nearby ally can close a two-cell alcove.

Uses synthetic terrain and visible bodies, without archived replay payloads.
"""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include "bokuto.hpp"
#include <cassert>
int main(int argc, char** argv) {
    ares::World w;
    w.W = w.H = 12; w.NC = 144; w.me = 0; w.rnd = 66;
    w.len = 2; w.units = 5; w.limit = 64; w.face = 0;
    auto c = [&](int x, int y) { return y * w.W + x; };
    w.head = c(2,7); w.body = {c(2,8), w.head};
    w.own.assign(w.NC,0); w.own[c(2,8)] = 1; w.own[w.head] = 2;
    w.occ.assign(w.NC,-1); w.pearl_seen.assign(w.NC,-1);
    w.seen.assign(w.NC,w.rnd+1);
    w.dest_tab.resize(w.NC*4);
    for (int n=0;n<w.NC;n++) for(int d=0;d<4;d++)
        w.dest_tab[n*4+d] = w.nbr(n,d);
    auto wall = [&](int n,int d) {
        int other = w.nbr(n,d);
        w.dest_tab[n*4+d] = ares::BLOCKED;
        w.dest_tab[other*4+((d+2)&3)] = ares::BLOCKED;
    };
    // North is an alcove: enter (2,6), then (3,6), then exit (3,7).
    wall(c(2,6),0); wall(c(2,6),3);
    wall(c(3,6),0); wall(c(3,6),1);
    wall(w.head,3);
    w.parts = {{c(4,7),38,true,true,0,3}, {c(4,8),38,true,false,0,2}};
    for(int i=0;i<2;i++) w.occ[w.parts[i].cell]=i;
    w.ally_heads={0};
    bokuto::Guard guard;
    ares::Decision dec,out; dec.act=ares::Act::MOVE; dec.dirs={0};
    char tag=0; bool replaced=guard.apply(w,dec,out,tag);
    int chosen = replaced ? out.dirs.front() : dec.dirs.front();
    assert(chosen == (argv[1][0]=='E' ? 1 : 0));
    if(argv[1][0]=='E') assert(replaced && tag=='G');
}
'''


class QueenEscapeTest(unittest.TestCase):
    def test_small_team_queen_avoids_ally_closed_alcove(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'regression.cpp'
            source.write_text(CPP)
            for bot, expected in [('bokuto-18-queenfeed', 'N'),
                                  ('akaashi-01-queen-escape', 'E'),
                                  ('akaashi-02-queen-strike', 'E'),
                                  ('akaashi-03-threatened-queen-split', 'E'),
                                  ('akaashi-04-visible-body-safety', 'E'),
                                  ('akaashi-05-sprint-queen-escape', 'E')]:
                exe = Path(tmp) / bot
                subprocess.run(['g++', '-std=c++20', '-O1', '-I', str(ROOT / 'bots' / bot),
                                str(source), '-o', str(exe)], check=True)
                subprocess.run([str(exe), expected], check=True)


if __name__ == '__main__':
    unittest.main()
