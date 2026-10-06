#include <cassert>
#include <iostream>
#include "policy.hpp"
int main() {
    auto [ct,g]=unswbc::init();ares::World w;w.init(ct,g);int checked=0;
    while(unswbc::update(ct,g)) {
        w.sense(ct,g);
        if(w.rnd==157) {
            assert(w.head==28 && w.len==2);
            assert(!kenma::turning_room(w,3));
            assert(kenma::turning_room(w,2));
            ares::Policy pol;
            assert(pol.simulate(w,{2}).status==ares::Policy::SimStatus::OK);
            auto decision=pol.decide(w);
            assert(pol.kenma_corridor_filtered);
            assert(decision.act==ares::Act::MOVE && decision.dirs.front()==2);
            ++checked;
        }
        if(w.rnd==158) {
            // Once committed, no broad safe route remains: preserve fallback.
            ares::Policy pol;pol.decide(w);assert(!pol.kenma_corridor_filtered);++checked;
        }
    }
    assert(checked==2);
    std::cout<<"Corridor caution: recorded avoidable entry redirects south; committed corridor preserves fallback\n";
}
