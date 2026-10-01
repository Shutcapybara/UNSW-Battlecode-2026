#pragma once

#include "world.hpp"

namespace ares {

// Congestion evidence only: an observed allied head occupies this cell or
// has a known one-step landing here. dest includes paired portal crossings.
// All four headings are considered conservatively; this is not an ally-policy
// prediction. Unknown edges, unseen allies and multi-step sprints are excluded.
inline bool mouth_contested(const World& w, int cell) {
    if (cell < 0) return false;
    for (int pi : w.ally_heads) {
        int head = w.parts[pi].cell;
        if (head == cell) return true;
        for (int d = 0; d < 4; ++d)
            if (w.dest(head, d) == cell) return true;
    }
    return false;
}

}  // namespace ares
