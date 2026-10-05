"""Create a separate Carthage-based sealed-pocket keeper, before measuring it."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
dst=root/'bots/kenma-03-pocket-queen'
shutil.copytree(root/'bots/carthage-05-free-sprint',dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__','CANDIDATE.toml'))
(dst/'kenma_pocket.hpp').write_text('''// A pocket is proven from observed terrain, never inferred from map identity.
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
    int dir=-1;
    for (int d=0; d<4; ++d) {
        auto sim=pol.simulate(w,{d});
        if (sim.status!=ares::Policy::SimStatus::OK) continue;
        // Prefer an empty step; collecting a pearl is still legal and can fund the next split.
        double score=-sim.eaten + (d==w.face ? 0.01 : 0.0);
        if (score>best) { best=score; dir=d; }
    }
    if (dir<0) return false;
    out.act=ares::Act::MOVE; out.dirs={dir}; out.why='q'; out.target=w.head;
    return true;
}
}
''')
p=dst/'main.cpp'; s=p.read_text().replace('#include "world.hpp"','#include "world.hpp"\n#include "kenma_pocket.hpp"')
s=s.replace('            dec = pol.decide(w);','''            // A split child acts this round, before its parent next acts. Clear trapped donors now.
            if (kenma::donor(w)) {
                std::cout << "SPLIT 1\\nLOG kenma_pocket_donor\\nPROTOCOL 3\\nENDTURN\\n" << std::flush;
                continue;
            }
            const int real_limit=w.limit;
            if (w.me>1) w.limit=std::max(1,real_limit-1);
            dec = pol.decide(w);
            w.limit=real_limit;
            kenma::queen(w,pol,dec);''')
p.write_text(s)
(dst/'README.md').write_text('''# Kenma 03 — sealed-pocket queen\n\nParent: carthage-05-free-sprint at ea8ada4e2. Independent of Kenma 01/02.\n\nProves a connected component of at most eight cells from known nonportal terrain. In such a pocket, original queens (id 0/1, as in the current engine maps) split down to length two whenever possible and otherwise take a safe single step. Nonqueen dragons seeing the original queen in their sealed pocket deliberately cull using SPLIT 1, before the queen next moves. Other dragons reserve one population slot for emergency queen splits. No map identity condition.\n\nPrecedent: Rome 06 cage E1; this variant confines donor culling and queen movement to observed sealed pockets and selects the complete single-step action instead of truncating a scored sprint.\n\nStatus: unmeasured; native and sandbox checks required.\n''')
print(dst)
