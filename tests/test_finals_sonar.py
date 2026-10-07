"""Packet features use chosen-action geometry and actual previous sends."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = r'''
#include "packet_features.hpp"
#include <cassert>
int main() {
    unswbc::Controller ct(2,unswbc::Team('A'),unswbc::Direction('E'),{},64);
    unswbc::Game game(24,16,64);ares::World w;w.init(ct,game);
    w.rnd=50;w.born=0;w.len=6;w.units=5;w.face=1;
    w.body={123,124,125,126,127,128};w.head=128;
    std::fill(w.ek.begin(),w.ek.end(),ares::EK_OPEN);w.rebuild_dest();
    for(int i=0;i<6;i++){w.own[w.body[i]]=i+1;w.own_cells.push_back(w.body[i]);}
    ares::Part ally;ally.id=4;ally.cell=153;ally.head=true;ally.ally=true;
    w.parts.push_back(ally);w.occ[153]=0;w.ally_heads.push_back(0);
    ares::Policy p;ares::Decision action;action.dirs={2};
    uint64_t value=ares::Policy::pack(w,2,123);
    finals::PacketCandidate east{finals::PacketOption::BASELINE,1,value,2,false};
    std::array<uint64_t,4> previous{0,value,0,0};
    auto f=finals::packet_features(w,p,action,east,previous);
    assert(f[16]==0 && f[17]==1.0f/32); // MOVE S landing, in the pre-action E-facing frame
    assert(f[21]==1 && f[22]==0 && f[23]==1.0f/32); // ally is E of new landing, not old head
    assert(f[25]==1);previous[1]=0;
    assert(finals::packet_features(w,p,action,east,previous)[25]==0);
    auto north=east;north.ray=0;
    assert(finals::packet_features(w,p,action,north,previous)[20]==1); // post-move own neck contact
}
'''


class Sonar(unittest.TestCase):
    def test_post_action_geometry_and_previous_send_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'test.cpp'
            executable = Path(directory) / 'test'
            source.write_text(CPP)
            subprocess.run(['g++', '-std=c++20', '-O2', '-I', str(ROOT / 'bots/bokuto-68-sonar-history'),
                            str(source), '-o', str(executable)], check=True, timeout=120)
            subprocess.run([str(executable)], check=True, timeout=10)


if __name__ == '__main__':
    unittest.main()
