"""Visible queen trades include pearl-funded sprints and survive guard bypass validation."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include "policy.hpp"
#include <cassert>
ares::World corridor(int length, int steps, bool pearl, int enemy=1) {
    ares::World w; w.W=w.H=12; w.NC=144; w.me=4; w.rnd=46;
    w.len=length; w.units=2; w.limit=64; w.head=26; w.face=1;
    w.dest_tab.assign(4*w.NC,ares::BLOCKED);
    w.own.assign(w.NC,0); w.occ.assign(w.NC,-1);
    w.pearl_seen.assign(w.NC,-1);
    for(int i=length-1;i>=0;i--) { w.body.push_back(w.head-i*12); w.own[w.head-i*12]=1; }
    for(int i=0;i<steps;i++) w.dest_tab[(w.head+i)*4+1]=w.head+i+1;
    int target=w.head+steps;
    w.parts={{target,enemy,false,true,0,3}};w.enemy_heads={0};w.occ[target]=0;
    if(pearl) w.pearl_seen[w.head+1]=w.rnd;
    return w;
}
int main() {
    ares::Policy p; ares::Decision d;
    // Length two can fund the second step with a visible first-step pearl.
    auto w=corridor(2,2,true);
    assert(p.queen_strike(w,d) && d.dirs==std::vector<int>({1,1}));
    assert(p.confirmed_queen_strike(w,d));
    w.pearl_seen[w.head+1]=-1;
    assert(!p.queen_strike(w,d) && !p.confirmed_queen_strike(w,d));
    // Three-step attacks are legal at length three if a pearl funds the extra step.
    w=corridor(3,3,true);
    assert(p.queen_strike(w,d) && d.dirs.size()==3);
    assert(p.confirmed_queen_strike(w,d));
    d.dirs.push_back(1);assert(!p.confirmed_queen_strike(w,d));
    w=corridor(3,3,false);assert(!p.queen_strike(w,d));
    w=corridor(3,2,false,7);assert(!p.queen_strike(w,d));
    w=corridor(3,2,false);w.me=0;assert(!p.queen_strike(w,d));
    w=corridor(3,2,false);w.parts[0].ally=true;w.enemy_heads.clear();
    assert(!p.queen_strike(w,d));
    w=corridor(3,2,false);w.dest_tab[w.head*4+1]=ares::UNKNOWN;
    assert(!p.queen_strike(w,d));
    w=corridor(3,2,false);w.parts.push_back({w.head+1,8,false,false,0,2});
    w.occ[w.head+1]=1;assert(!p.queen_strike(w,d));
}
'''


class QueenStrikeTest(unittest.TestCase):
    def test_visible_legal_queen_trades(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'regression.cpp'
            source.write_text(CPP)
            for bot in ('akaashi-02-queen-strike', 'akaashi-03-threatened-queen-split',
                        'akaashi-04-visible-body-safety', 'akaashi-05-sprint-queen-escape'):
                exe = Path(tmp) / bot
                subprocess.run(['g++', '-std=c++20', '-O1', '-I',
                                str(ROOT / 'bots' / bot), str(source), '-o', str(exe)], check=True)
                subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    unittest.main()
