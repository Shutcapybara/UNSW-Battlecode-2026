"""Behavioral contracts for the finals copy-and-propose bridge and protected sonar."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

CPP = r'''
#include "options.hpp"
#include <cassert>

ares::World fixture(int id = 2, int units = 5, int limit = 64) {
    unswbc::Controller ct(id, unswbc::Team('A'), unswbc::Direction('E'), {}, limit);
    unswbc::Game game(24, 16, limit);
    ares::World w; w.init(ct, game);
    w.rnd=50; w.born=0; w.len=6; w.units=units; w.face=1;
    w.body={123,124,125,126,127,128}; w.head=w.body.back();
    std::fill(w.ek.begin(),w.ek.end(),ares::EK_OPEN); w.rebuild_dest();
    for (int i=0;i<6;i++) { w.own[w.body[i]]=i+1;w.own_cells.push_back(w.body[i]); }
    w.pearl_seen[152]=50; w.pearl_order.push_back(152);
    for (int c=0;c<w.NC;c++) { w.seen[c]=51;w.visible_cells.push_back(c); }
    return w;
}

int main() {
    bokuto::g_br=nullptr;
    auto w=fixture(); ares::Policy p; bokuto::Guard g;
    const auto original_body=w.body, original_seen=w.pearl_seen;
    finals::Turn a(w,p,g); a.propose();
    finals::Turn b(w,p,g); b.propose();
    assert(w.body==original_body && w.pearl_seen==original_seen && p.visits.empty());
    assert(g.prev_head==-1 && g.pending_steps==0);
    assert(a.candidates.size()>=2 && a.candidates.size()==b.candidates.size());
    for (size_t i=0;i<a.candidates.size();i++) {
        assert(finals::same_command(a.candidates[i].decision,b.candidates[i].decision));
        assert(a.candidates[i].features==b.candidates[i].features);
        for (size_t j=0;j<i;j++) assert(!finals::same_command(a.candidates[i].decision,a.candidates[j].decision));
        if (i) {
            auto guard=g; ares::Decision alt;char tag=0;
            assert(!guard.apply(a.world,a.candidates[i].decision,alt,tag) ||
                finals::same_command(alt,a.candidates[i].decision));
        }
    }
    // An alternate selection commits its own action/target, with a single memory update.
    char tag=0;const auto chosen=a.candidates[1].decision;
    auto actual=a.commit(w,p,g,1,tag);
    assert(finals::same_command(actual,chosen) && !a.unexpected_override);
    assert(p.previous_target==chosen.target && p.visits[w.head]==1);
    assert(g.pending_steps==int(actual.dirs.size()));
    bool threw=false;try { a.commit(w,p,g,0,tag); } catch(const std::runtime_error&) { threw=true; }
    assert(threw);
    // Queen and reserved-cap decisions cannot acquire learned alternatives/splits.
    auto qw=fixture(0);ares::Policy qp;bokuto::Guard qg;
    finals::Turn queen(qw,qp,qg);queen.propose();assert(queen.candidates.size()==1);
    auto rw=fixture(2,5,6);ares::Policy rp;bokuto::Guard rg;
    finals::Turn reserve(rw,rp,rg);reserve.propose();
    for(size_t i=1;i<reserve.candidates.size();i++)assert(reserve.candidates[i].decision.act!=ares::Act::SPLIT);
    // Packet identity round-trips; beacons/handoffs cannot be suppressed or rerouted.
    ares::Policy radio;auto vw=fixture();
    radio.sonar_out={ares::Policy::pack(vw,1,123),ares::Policy::pack(vw,7,234),
                     ares::Policy::pack(vw,2,345),ares::Policy::pack(vw,6,456)};
    radio.sonar_order={3,1,0,2};
    const auto original_packets=radio.sonar_out;const auto original_order=radio.sonar_order;
    auto rays=finals::packet_candidates(vw,radio);
    assert(radio.sonar_out==original_packets && radio.sonar_order==original_order);
    assert(rays[0].size()==1 && rays[1].size()==1 && rays[2].size()>1);
    int type=0;uint64_t bits=0;assert(ares::Policy::unpack(vw,rays[2][0].value,type,bits));
    assert(type==2 && bits==345);
    finals::commit_packets(radio,rays,{0,0,0,0});
    assert(radio.sonar_out==original_packets && radio.sonar_order==original_order);
    finals::commit_packets(radio,rays,{0,0,1,0});
    assert(radio.sonar_out[2]==0 && radio.sonar_out[0]==original_packets[0] && radio.sonar_out[1]==original_packets[1]);
}
'''


class Options(unittest.TestCase):
    def test_state_isolation_selection_legality_reserve_and_packet_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'test.cpp'
            executable = Path(directory) / 'test'
            source.write_text(CPP)
            subprocess.run(['g++', '-std=c++20', '-O2', '-I', str(ROOT / 'bots/bokuto-64-option-chassis'),
                            str(source), '-o', str(executable)], check=True, timeout=120)
            subprocess.run([str(executable)], check=True, timeout=10)


if __name__ == '__main__':
    unittest.main()
