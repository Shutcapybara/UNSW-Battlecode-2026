// anna chassis — NAVIGATION: one flood fill (BFS) through portals and wrap.
//
// API used by the other C1 tasks:
//   Grid g; dist(w, from, mask, g);        // BFS from `from`
//   g.d[c]      steps to c (-1 unreached)
//   g.first[c]  first direction taken from `from` on a shortest path (-1 at from)
//   g.order     cells in BFS order (nearest first)
//   g.dives     unpaired portals met: {cell, dir, depth after crossing, first dir}
//   path(w, g, to) -> directions from `from` to `to` (empty if unreached)
//
// mask[c] = t blocks cell c for arrival depths < t (0 = free). Depth 1 is the
// cell entered by this turn's first step. Own segment i from the tail is free
// from depth i + 2 (the tail is blocked for the step that moves it), so a
// body mask is: mask[body[i]] = i + 2. build_block_mask() does that plus the
// other dragons' visible segments.
//
// Terrain is optimistic: an unknown edge is open to its torus neighbour; kelp
// blocks; an unpaired portal blocks (landing unknown). Cost ~O(reached cells).
#pragma once

#include <array>
#include <cstdint>
#include <vector>

#include "params.hpp"
#include "world.hpp"

namespace ares {

struct Grid {
    std::vector<int16_t> d;
    std::vector<int8_t> first;
    std::vector<uint8_t> first_mask;
    std::vector<int> parent;
    std::vector<int> order;
    // Unpaired portals met by the search: {cell, dir, depth after crossing, first dir}.
    std::vector<std::array<int, 4>> dives;
    int from = -1;
};

// cap: stop after this many cells; max_depth: do not expand cells at this depth;
// stop_at: optional cells (up to 4) -- stop once all of them are reached.
inline void dist(const World& w, int from, const std::vector<uint16_t>& mask, Grid& g,
                 int cap = 1 << 30, int max_depth = 1 << 30, const int* stop_at = nullptr,
                 int n_stop = 0) {
    if (static_cast<int>(g.d.size()) != w.NC) {
        g.d.assign(w.NC, -1);
        g.first.assign(w.NC, -1);
        g.first_mask.assign(w.NC, 0);
        g.parent.assign(w.NC, -1);
    } else {
        for (int c : g.order) {
            g.d[c] = -1;
            g.first[c] = -1;
            g.first_mask[c] = 0;
            g.parent[c] = -1;
        }
    }
    g.order.clear();
    g.dives.clear();
    g.from = from;
    g.d[from] = 0;
    g.first_mask[from] = 0;
    g.order.push_back(from);
    for (size_t qi = 0; qi < g.order.size() && static_cast<int>(g.order.size()) < cap; qi++) {
        int c = g.order[qi];
        if (g.d[c] >= max_depth) break;
        if (n_stop) {
            int left = 0;
            for (int i = 0; i < n_stop; i++) left += stop_at[i] >= 0 && g.d[stop_at[i]] < 0;
            if (!left) break;
        }
        int t = g.d[c] + 1;
        int fc = g.first[c];
        for (int dd = 0; dd < 4; dd++) {
            int n = w.step_opt(c, dd);
            if (n == UNPAIRED) {
                g.dives.push_back({c, dd, t, fc < 0 ? dd : fc});
                continue;
            }
            if (n < 0) continue;
            if (mask[n] > t) continue;
            int first = fc < 0 ? dd : fc;
            if (g.d[n] >= 0) {
                if (g.d[n] == t) g.first_mask[n] |= static_cast<uint8_t>(1U << first);
                continue;
            }
            g.d[n] = static_cast<int16_t>(t);
            g.first[n] = static_cast<int8_t>(first);
            g.first_mask[n] = static_cast<uint8_t>(1U << first);
            g.parent[n] = c * 4 + dd;
            g.order.push_back(n);
        }
    }
}

inline std::vector<int> path(const World& w, const Grid& g, int to) {
    std::vector<int> out;
    if (to < 0 || g.d[to] < 0) return out;
    (void)w;
    for (int c = to; c != g.from;) {
        int p = g.parent[c];
        out.push_back(p & 3);
        c = p >> 2;
    }
    return {out.rbegin(), out.rend()};
}

// Terrain-only BFS distances to `target` (portals two-way, kelp symmetric), for
// ranking every candidate step, not only the best one. Other dragons ignored.
inline void rev_dist(const World& w, int target, Grid& g, int cap = 1 << 30, int max_depth = 1 << 30,
                     const int* stop_at = nullptr, int n_stop = 0) {
    static std::vector<uint16_t> none;
    if (static_cast<int>(none.size()) != w.NC) none.assign(w.NC, 0);
    dist(w, target, none, g, cap, max_depth, stop_at, n_stop);
}

// Standard planning mask: own body segment i vacates at depth i + 2, other
// visible segments at their Part::vac (see World::vacancy).
inline void build_block_mask(const World& w, std::vector<uint16_t>& mask) {
    mask.assign(w.NC, 0);
    for (size_t i = 0; i + 1 < w.body.size(); i++) mask[w.body[i]] = static_cast<uint16_t>(i + w.body_offset + 2);
    for (int c : w.own_cells)
        if (w.own[c] == 255) mask[c] = 1000;
    for (auto const& p : w.parts) mask[p.cell] = static_cast<uint16_t>(p.vac);
}

}  // namespace ares
