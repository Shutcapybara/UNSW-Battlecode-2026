// Mechanism probe only: optimistic short-body survival in observed terrain.
#include <cassert>
#include <iostream>
#include "policy.hpp"
// Unknown terrain/portal pairing remains potentially survivable. Ignore food and
// other dragons, and retain only the neck: failure therefore proves a static trap
// for any legal dragon of length >=2, without assuming temporary cells stay blocked.
bool can_continue(ares::World const& w,int previous,int head,int left) {
    if(left==0)return true;
    for(int d=0;d<4;++d) {
        int next=w.dest(head,d);
        if(next==ares::UNKNOWN || next==ares::UNPAIRED)return true;
        if(next<0 || next==previous)continue;
        if(can_continue(w,head,next,left-1))return true;
    }
    return false;
}
int main() {
    auto [ct,g]=unswbc::init();ares::World w;w.init(ct,g);
    int checked=0;
    while(unswbc::update(ct,g)) {
        w.sense(ct,g);
        if(w.rnd==157) {
            // The final wall is still outside vision at the last branching cell.
            assert(w.head==28 && w.len==2);
            assert(can_continue(w,w.head,w.dest(w.head,3),8));
            assert(can_continue(w,w.head,w.dest(w.head,2),8));
            ++checked;
        }
        if(w.rnd==158) {
            // Once visible, the dead end is proven, but the queen is committed.
            assert(!can_continue(w,w.head,w.dest(w.head,3),8));
            ++checked;
        }
    }
    assert(checked==2);
    std::cout<<"Recorded queen trap: unknown endpoint prevents proof before commitment; known trap detected one turn too late\n";
}
