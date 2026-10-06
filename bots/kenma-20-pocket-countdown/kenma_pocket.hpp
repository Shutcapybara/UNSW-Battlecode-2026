// A pocket is proven from observed terrain, never inferred from map identity.
#pragma once
#include "policy.hpp"
namespace kenma {
inline int pocket_size(ares::World const& w, int target=-1) {
    std::vector<int> cells{w.head};
    for (size_t i=0; i<cells.size(); ++i) {
        for (int d=0; d<4; ++d) {
            int edge=w.ekey(cells[i],d);
            if (w.ek[edge]==ares::EK_UNK || w.ek[edge]==ares::EK_PORTAL) return 0;
            if (w.ek[edge]==ares::EK_KELP) continue;
            int n=w.nbr(cells[i],d);
            if (std::find(cells.begin(),cells.end(),n)==cells.end()) {
                cells.push_back(n);
                if (cells.size()>8) return 0;
            }
        }
    }
    if (target>=0 && std::find(cells.begin(),cells.end(),target)==cells.end()) return 0;
    return static_cast<int>(cells.size());
}
// Return true only for a donor trapped in the original queen's sealed pocket.
inline bool donor(ares::World const& w) {
    if (w.me<=1 || !pocket_size(w)) return false;
    for (int pi:w.ally_heads) if (w.parts[pi].id<=1 && pocket_size(w,w.parts[pi].cell)) return true;
    return false;
}
// Only current legal observations are used: no atlas fertility or future RNG.
inline bool growth_pressure(ares::World const& w,std::vector<int> const& path) {
    std::vector<int> visited;int head=w.head;
    for(int d:path){head=w.dest(head,d);visited.push_back(head);}
    std::vector<int> cells{w.head};
    for(size_t i=0;i<cells.size();++i){
        int c=cells[i];
        if(w.seen[c]!=w.rnd+1)return true;
        if(w.pearl_seen[c]==w.rnd && std::find(visited.begin(),visited.end(),c)==visited.end())return true;
        if(w.bed[c]==1 && w.spawn_at[c]<=w.rnd+1)return true;
        for(int d=0;d<4;++d){int n=w.dest(c,d);if(n>=0 && std::find(cells.begin(),cells.end(),n)==cells.end())cells.push_back(n);}
        if(cells.size()>8)return true;
    }
    return false;
}
inline bool queen(ares::World const& w, ares::Policy& pol, ares::Decision& out) {
    if (w.me>1 || !pocket_size(w) || static_cast<int>(w.body.size())!=w.len) return false;
    if (w.len>=4 && w.units<w.limit) {
        out.act=ares::Act::SPLIT; out.split=w.len-2; out.why='q'; out.target=w.head;
        return true;
    }
    double best=-1e30;
    std::vector<int> best_path;
    auto consider=[&](std::vector<int> const& path) {
        auto sim=pol.simulate(w,path);
        if (sim.status!=ares::Policy::SimStatus::OK) return;
        // Preserve a viable length-three queen unless observed food/countdowns
        // require slack. On the final turn, growth no longer needs an exit next turn.
        int length=static_cast<int>(sim.body.size());
        bool final_turn=w.rnd>=unswbc::Constants::MAX_ROUNDS-1;
        double score=(final_turn ? 10.0*length : -10.0*std::abs(length-3))
                     -(!final_turn && length>=3 && growth_pressure(w,path) ? 100.0 : 0.0)
                     -0.1*path.size()+(path.front()==w.face ? 0.01 : 0.0);
        if (score>best) { best=score; best_path=path; }
    };
    for (int d=0; d<4; ++d) {
        consider({d});
        if(w.len==2 || w.len==3)for(int e=0;e<4;++e)consider({d,e});
    }
    if (best_path.empty()) return false;
    out.act=ares::Act::MOVE; out.dirs=best_path; out.why='q'; out.target=w.head;
    return true;
}
}
