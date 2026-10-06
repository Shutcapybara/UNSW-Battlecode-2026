// Queen-only action clone from five keeper teams. All inputs are current legal HB-1 features.
#pragma once
#include "policy.hpp"
#include "gbt_compact.hpp"
#include "kenma_queen_model.hpp"
namespace kenma {
inline void learned_queen(ares::World const& w, ares::Policy& pol, hb1::Row const& row, ares::Decision& out) {
    if (out.act==ares::Act::SPLIT) return; // Preserve parent expansion and escape splits.
    static hb1::Bound const bound{hb1::dirc_bind};
    auto x=bound.vec(row);
    double p[7];
    GBT_PROBA(kenma_queen,x.data(),p);
    double best=-1.0;
    ares::Decision selected=out;
    for (int rel=0; rel<4; ++rel) {
        int d=(w.face+rel)&3;
        auto sim=pol.simulate(w,{d});
        if (sim.status!=ares::Policy::SimStatus::OK && sim.status!=ares::Policy::SimStatus::DIVE) continue;
        if (p[rel]>best) {
            best=p[rel]; selected.act=ares::Act::MOVE; selected.dirs={d}; selected.why='k';
            // Retain a fully checked, free sprint from the parent when its first step agrees.
            if (out.act==ares::Act::MOVE && !out.dirs.empty() && out.dirs.front()==d &&
                static_cast<int>(out.dirs.size())<=(w.len+3)/4 &&
                pol.simulate(w,out.dirs).status==ares::Policy::SimStatus::OK) selected.dirs=out.dirs;
        }
    }
    if (best>=0) out=selected;
}
}
