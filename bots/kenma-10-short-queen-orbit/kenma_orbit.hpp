// Maintain a short original queen in a freshly observed, empty four-cell cycle.
#pragma once
#include "policy.hpp"
namespace kenma {
struct Orbit {
    std::array<int,4> cells{{-1,-1,-1,-1}};
    static int direction(ares::World const& w,int from,int to) {
        for(int d=0;d<4;++d)
            if(w.nbr(from,d)==to && w.ek[w.ekey(from,d)]==ares::EK_OPEN && w.dest(from,d)==to) return d;
        return -1;
    }
    static bool valid(ares::World const& w,std::array<int,4> const& ring) {
        if(w.body.empty()) return false;
        for(int i=0;i<4;++i) {
            int c=ring[i];
            if(c<0 || c>=w.NC || w.seen[c]!=w.rnd || w.bed[c]!=0 || w.pearl_seen[c]==w.rnd) return false;
            for(int j=0;j<i;++j) if(ring[j]==c) return false;
            if(direction(w,c,ring[(i+1)%4])<0) return false;
            for(auto const& part:w.parts) {
                if(part.cell==c || (part.head && part.ally && w.cheb(part.cell,c)<=1)) return false;
            }
        }
        auto it=std::find(ring.begin(),ring.end(),w.head);
        if(it==ring.end()) return false;
        int at=static_cast<int>(it-ring.begin());
        auto body=w.body;
        // Two laps of separate single-step turns, with no growth or sprint cost.
        // This also proves entry when the current tail is outside the cycle.
        for(int k=0;k<8;++k) {
            int next=ring[(at+k+1)%4];
            if(std::find(body.begin(),body.end(),next)!=body.end()) return false;
            body.erase(body.begin()); body.push_back(next);
        }
        return true;
    }
    bool choose(ares::World const& w,ares::Policy const& pol,ares::Decision& out) {
        if(w.me>1 || w.len<2 || w.len>3 || w.units<3 || static_cast<int>(w.body.size())!=w.len || out.act==ares::Act::SPLIT) {
            cells.fill(-1);return false;
        }
        for(int pi:w.enemy_heads) if(w.cheb(w.parts[pi].cell,w.head)<=4) {
            cells.fill(-1);return false;
        }
        if(!valid(w,cells)) {
            cells.fill(-1);
            double best=-1e30;
            for(int d=0;d<4;++d) for(int turn:{1,3}) {
                int e=(d+turn)%4;
                std::array<int,4> ring{{w.head,w.nbr(w.head,d),w.nbr(w.nbr(w.head,d),e),w.nbr(w.head,e)}};
                if(!valid(w,ring)) continue;
                auto sim=pol.simulate(w,{d});
                if(sim.status!=ares::Policy::SimStatus::OK || sim.eaten) continue;
                double score=d==w.face ? 0.01 : 0.0;
                for(int pi:w.ally_heads) {
                    int distance=10;
                    for(int c:ring) distance=std::min(distance,w.cheb(w.parts[pi].cell,c));
                    score-=1.0/(1+distance);
                }
                if(score>best) {best=score;cells=ring;}
            }
        }
        if(cells[0]<0) return false;
        int at=static_cast<int>(std::find(cells.begin(),cells.end(),w.head)-cells.begin());
        int d=direction(w,w.head,cells[(at+1)%4]);
        if(d<0) {cells.fill(-1);return false;}
        auto sim=pol.simulate(w,{d});
        if(sim.status!=ares::Policy::SimStatus::OK || sim.eaten) {cells.fill(-1);return false;}
        out.act=ares::Act::MOVE;out.dirs={d};out.why='o';out.target=w.head;
        return true;
    }
};
}
