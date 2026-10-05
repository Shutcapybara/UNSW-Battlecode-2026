#pragma once
#include "kenma_pocket.hpp"
namespace kenma {
// Terrain is fixed. Nine open-connected cells or an incident portal prove that
// the queen cannot inhabit a closed <=8-cell, portal-free component now or later.
inline bool queen_component_open(ares::World const& w,int start) {
    std::vector<int> cells{start};
    for(size_t i=0;i<cells.size();++i)for(int d=0;d<4;++d){
        auto kind=w.ek[w.ekey(cells[i],d)];
        if(kind==ares::EK_PORTAL)return true;
        if(kind!=ares::EK_OPEN)continue;
        int n=w.nbr(cells[i],d);
        if(std::find(cells.begin(),cells.end(),n)==cells.end()){
            cells.push_back(n);if(cells.size()>8)return true;
        }
    }
    return false;
}
struct ReserveState {
    bool released=false;
    void observe(ares::World& w){
        // High type bit is an envelope flag. Preserve all 44 payload bits,
        // including the high density-report id bit, and repair the checksum.
        for(auto& msg:w.msgs){int type=0;uint64_t payload=0;
            if(!ares::Policy::unpack(w,msg,type,payload))continue;
            if((type&8) && (type&7)){
                released=true;msg=ares::Policy::pack(w,type&7,payload);
            }
        }
        if(released)return;
        if(w.me<=1 && queen_component_open(w,w.head))released=true;
        for(int pi:w.ally_heads){auto const& q=w.parts[pi];
            if(q.id<=1 && queen_component_open(w,q.cell))released=true;
        }
    }
    void tag(ares::World const& w,ares::Policy& pol)const{
        if(!released)return;
        for(auto& msg:pol.sonar_out){if(!msg)continue;int type=0;uint64_t payload=0;
            if(ares::Policy::unpack(w,msg,type,payload) && type>=1 && type<=7)
                msg=ares::Policy::pack(w,type|8,payload);
        }
    }
};
}
