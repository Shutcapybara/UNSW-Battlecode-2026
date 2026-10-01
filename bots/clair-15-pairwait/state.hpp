// clair-15 (H-1) — minimal per-dragon parts tracker: the ally/enemy parts visible last turn, kept so the
// policy can detect an ally head that vanished from view on a portal-mouth cell (a transit into the pair).
#pragma once

#include <vector>

#include "world.hpp"

namespace ares {

struct State {
    struct Prev { int cell, id; bool head; };
    std::vector<Prev> prev_parts;

    void update(const World& w) {
        prev_parts.clear();
        prev_parts.reserve(w.parts.size());
        for (const Part& q : w.parts) prev_parts.push_back({q.cell, q.id, q.head});
    }
    const std::vector<Prev>& prev_parts_back() const { return prev_parts; }
};

}  // namespace ares
