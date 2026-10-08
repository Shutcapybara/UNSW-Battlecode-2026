"""Reserve defenders while surplus collectors seek a less crowded resource."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include "policy.hpp"
#include <cassert>
ares::World world() {
    ares::World w; w.W=w.H=25; w.NC=625; w.me=20; w.rnd=100;
    w.head=12*25+12; w.len=4; w.units=12;
    w.pearl_seen.assign(w.NC,-1); w.bed.assign(w.NC,0);
    w.spawn_at.assign(w.NC,-1); w.seen.assign(w.NC,w.rnd+1);
    // Crowded pearl is four steps away, alternate is eight steps away.
    int c=12*25+16;
    w.parts={{c,2,true,true,0},{c-1,4,true,true,0},
             {c-2,6,true,true,0},{c-3,8,true,true,0}};
    w.ally_heads={0,1,2,3};
    w.pearl_seen[c]=w.pearl_seen[12*25+4]=w.rnd;
    w.pearl_order={c,12*25+4}; return w;
}
int main(int argc,char**argv) {
    auto w=world(); ares::Policy p; int c=12*25+16;
    if(argv[1][0]=='P' || argv[1][0]=='I') { assert(p.far_target(w)==c); if(argv[1][0]=='P') return 0; }
    double surplus_factor=argv[1][0]=='I'?1.0:(argv[1][0]=='G'?0.45:(argv[1][0]=='H'?0.12:0.03));
    assert(p.hotspot_capacity_factor(w,c)==surplus_factor);
    assert(p.far_target(w)==12*25+4);
    // Current visibility used to bypass radio density. It must not bypass capacity.
    assert(p.local_density_factor(w,c)==surplus_factor);
    assert(p.crowded_production(w));
    w.head=c-1; w.parts[1].cell=c-4; assert(p.hotspot_capacity_factor(w,c)==1.0); // second incumbent
    w=world(); w.parts.push_back({c+25,21,false,true,0}); w.enemy_heads={4};
    w.parts.push_back({c+50,23,false,true,0}); w.enemy_heads.push_back(5);
    w.head=c-3; w.parts[3].cell=c-4;
    assert(p.hotspot_capacity_factor(w,c)==1.0); // fourth defender under pressure
    w=world(); w.ally_heads={0,1};
    assert(p.hotspot_capacity_factor(w,c)==1.0); assert(!p.crowded_production(w));
    w=world(); w.rnd=49; assert(p.hotspot_capacity_factor(w,c)==1.0); assert(!p.crowded_production(w));
    w.rnd=290; assert(p.hotspot_capacity_factor(w,c)==1.0); assert(!p.crowded_production(w));
    w=world(); w.me=0; assert(p.hotspot_capacity_factor(w,c)==1.0); assert(!p.crowded_production(w));
    w=world(); p.role_feeder=true; assert(p.hotspot_capacity_factor(w,c)==1.0); assert(!p.crowded_production(w));
    p.role_feeder=false; p.role_crown=true; assert(p.hotspot_capacity_factor(w,c)==1.0);
    // Equal-distance reservation uses stable IDs, including wrapped map distance.
    p=ares::Policy(); w=world(); w.head=c-2; w.parts[0].cell=c+2; w.parts[1].cell=c+1;
    assert(p.hotspot_capacity_factor(w,c)==surplus_factor);
}
'''

class HotspotCapacityTest(unittest.TestCase):
    def test_reservation_and_redirect(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'test.cpp'
            source.write_text(CPP)
            for bot, mode in [('akaashi-06-late-material-safety', 'P'),
                              ('akaashi-07-hotspot-capacity', 'F'),
                              ('akaashi-09-adaptive-capacity', 'G'),
                              ('akaashi-10-ranked-capacity', 'H'),
                              ('akaashi-11-escort-expansion', 'I')]:
                # Parent only exercises the shared target interface.
                content = CPP if mode == 'F' else CPP[:CPP.index('    assert(p.hotspot_capacity_factor')] + '\n}\n'
                source.write_text(content)
                exe = Path(tmp) / bot
                subprocess.run(['g++', '-std=c++20', '-O1', '-I', str(ROOT / 'bots' / bot),
                                str(source), '-o', str(exe)], check=True)
                subprocess.run([str(exe), mode], check=True)

if __name__ == '__main__':
    unittest.main()
