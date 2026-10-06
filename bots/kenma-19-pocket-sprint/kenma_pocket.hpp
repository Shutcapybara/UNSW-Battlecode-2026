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
        // Keep two segments when possible, leaving slack for the next pearl.
        // Simulation charges sprint tax after each paid step and checks collision first.
        double score=-10.0*sim.body.size()-sim.eaten-0.1*path.size()
                     +(path.front()==w.face ? 0.01 : 0.0);
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
