"""Capacity pressure preserves sprint thresholds without blocking terminal rescue."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include "policy.hpp"
#include <cassert>
int main() {
    ares::Policy p; ares::World w;
    w.W=w.H=12; w.NC=144; w.me=405; w.rnd=199;
    w.len=7; w.units=56; w.limit=64; w.head=78; w.face=3;
    w.body={84,83,82,81,80,79,78};
    w.own.assign(w.NC,0); w.occ.assign(w.NC,-1);
    w.pearl_seen.assign(w.NC,-1); w.dest_tab.assign(w.NC*4,ares::BLOCKED);
    for(int i=0;i<7;i++) w.own[w.body[i]]=i+1;
    w.dest_tab[84*4]=72; // tail escape
    ares::Decision d; d.act=ares::Act::MOVE; d.dirs={0};
    assert(p.split_capacity_cost(w,2)==0);
    w.units=60; assert(p.split_capacity_cost(w,2)==8);
    w.units=63; assert(p.split_capacity_cost(w,2)==14);
    assert(p.reserved_slot_escape(w,d)==5);
    w.units=64; assert(p.reserved_slot_escape(w,d)==0);
    w.units=63; w.me=0; assert(p.reserved_slot_escape(w,d)==0);
    w.me=405; d.why='f'; assert(p.reserved_slot_escape(w,d)==0);
    d.why='-';w.dest_tab[78*4+3]=77;assert(p.reserved_slot_escape(w,d)==0);
    w.dest_tab[78*4+3]=ares::BLOCKED;w.dest_tab[84*4]=ares::BLOCKED;
    assert(p.reserved_slot_escape(w,d)==0);
    w.len=5;assert(p.split_capacity_cost(w,2)==17.5); // loses the second free step
    w.len=6;assert(p.split_capacity_cost(w,2)==17.5);
    w.len=8;assert(p.split_capacity_cost(w,2)==14); // keeps two free steps
    w.limit=4;w.units=3;assert(p.split_capacity_cost(w,2)==0);
}
'''

class SoftReserveTest(unittest.TestCase):
    def test_pressure_and_emergency_exclusions(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'case.cpp';source.write_text(CPP)
            for bot in ('kuroo-01-soft-reserve','kuroo-02-escort-soft-reserve'):
                exe=Path(tmp)/bot
                subprocess.run(['g++','-std=c++20','-O1','-I',str(ROOT/'bots'/bot),str(source),'-o',str(exe)],check=True)
                subprocess.run([str(exe)],check=True)

if __name__=='__main__':
    unittest.main()
