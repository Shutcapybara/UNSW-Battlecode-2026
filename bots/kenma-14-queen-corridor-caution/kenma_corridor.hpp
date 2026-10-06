// Prefer visible turning room over an unverified single-file corridor.
#pragma once
#include "world.hpp"
namespace kenma {
inline bool turning_room(ares::World const& w,int first) {
    int cell=w.dest(w.head,first),previous=w.head;
    // Keep uncertain first steps and portal entries in the parent's choice set.
    if(cell<0 || w.ek[w.ekey(w.head,first)]!=ares::EK_OPEN || w.seen[cell]!=w.rnd+1)return true;
    std::array<int,9> visited;visited.fill(-1);visited[0]=w.head;int used=1;
    for(int step=0;step<8;++step) {
        if(cell<0 || w.seen[cell]!=w.rnd+1)return false;
        if(std::find(visited.begin(),visited.begin()+used,cell)!=visited.begin()+used)return true;
        visited[used++]=cell;
        std::array<int,4> exits;exits.fill(-1);int count=0;
        for(int d=0;d<4;++d) {
            if(w.ek[w.ekey(cell,d)]==ares::EK_PORTAL)return true;
            int next=w.dest(cell,d);
            if(next<0 || next==previous || next==cell)continue;
            if(std::find(exits.begin(),exits.begin()+count,next)==exits.begin()+count)exits[count++]=next;
        }
        if(count>=2)return true;
        if(count==0)return false;
        previous=cell;cell=exits[0];
    }
    return false;
}
}
