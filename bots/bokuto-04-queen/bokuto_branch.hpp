// bokuto-03: dead-end branches of the known terrain, and whether harvesting one pays.
//
// On most live maps the richest beds (gap 1-1: a pearl every round) sit in one-exit corridors. A dragon that
// walks in cannot turn round: it eats the pearls, and at the end must split (the head part of 2 dies and
// drops one pearl, the rest walks out backwards). A visit therefore nets (pearls eaten - 2). The top teams
// run this cycle all game; carthage-05 did it by accident, at a loss, and with the queen.
#pragma once

#include <algorithm>
#include <vector>

#include "world.hpp"

namespace bokuto {

struct Branches {
    int NC = 0;
    std::vector<int> id;      // per cell: branch index or -1
    std::vector<int> depth;   // per cell: 1 at the cell next to the junction, growing inwards
    struct Branch { int junction = -1; std::vector<int> cells; int depth_max = 0; };
    std::vector<Branch> list;
    int built_seen = -1, built_rnd = -1000;
    std::vector<int> deg_, queue_;

    static int nb(const ares::World& w, int c, int d) {
        int n = w.dest(c, d);
        if (n == ares::UNKNOWN) return w.nbr(c, d);       // optimistic: unknown edges are open
        if (n == ares::UNPAIRED) return -2;                 // a portal with an unknown exit: counts as an exit
        return n;                                            // >= 0 landing, -1 kelp
    }

    void update(const ares::World& w) {
        if (NC != w.NC) { NC = w.NC; id.assign(NC, -1); depth.assign(NC, 0); built_seen = -1; }
        if (built_seen == w.seen_count && w.rnd - built_rnd < 16) return;
        built_seen = w.seen_count; built_rnd = w.rnd;
        std::fill(id.begin(), id.end(), -1);
        std::fill(depth.begin(), depth.end(), 0);
        list.clear();
        deg_.assign(NC, 0);
        std::vector<uint8_t> alive(NC, 1);
        for (int c = 0; c < NC; c++) {
            int k = 0, seen_n[4];
            for (int d = 0; d < 4; d++) {
                int n = nb(w, c, d);
                if (n == -1) continue;
                if (n == -2) { k = 9; break; }                // unpaired portal: never a leaf
                bool dup = false;
                for (int j = 0; j < k; j++) if (seen_n[j] == n) dup = true;
                if (!dup) seen_n[k++] = n;
            }
            deg_[c] = k;
        }
        queue_.clear();
        for (int c = 0; c < NC; c++) if (deg_[c] <= 1) queue_.push_back(c);
        for (size_t qi = 0; qi < queue_.size(); qi++) {
            int c = queue_[qi];
            if (!alive[c]) continue;
            alive[c] = 0;
            for (int d = 0; d < 4; d++) {
                int n = nb(w, c, d);
                if (n < 0 || !alive[n]) continue;
                if (--deg_[n] <= 1) queue_.push_back(n);
            }
        }
        // group pruned cells into components, each hanging off one alive junction
        std::vector<int> comp(NC, -1);
        std::vector<int> stack;
        for (int c0 = 0; c0 < NC; c0++) {
            if (alive[c0] || comp[c0] >= 0) continue;
            int b = static_cast<int>(list.size());
            list.emplace_back();
            Branch& br = list.back();
            stack.assign(1, c0); comp[c0] = b;
            while (!stack.empty()) {
                int c = stack.back(); stack.pop_back();
                br.cells.push_back(c);
                for (int d = 0; d < 4; d++) {
                    int n = nb(w, c, d);
                    if (n < 0) continue;
                    if (alive[n]) { if (br.junction < 0) br.junction = n; else if (br.junction != n) br.junction = -2; }
                    else if (comp[n] < 0) { comp[n] = b; stack.push_back(n); }
                }
            }
            if (br.junction < 0 || br.cells.size() > 64) {   // an isolated tree region, or a huge one: not a pocket
                for (int c : br.cells) comp[c] = -1;
                list.pop_back();
                continue;
            }
            for (int c : br.cells) id[c] = b;
            // depth by BFS from the junction
            std::vector<int> q;
            for (int d = 0; d < 4; d++) {
                int n = nb(w, br.junction, d);
                if (n >= 0 && id[n] == b && depth[n] == 0) { depth[n] = 1; q.push_back(n); }
            }
            for (size_t qi = 0; qi < q.size(); qi++) {
                int c = q[qi];
                for (int d = 0; d < 4; d++) {
                    int n = nb(w, c, d);
                    if (n >= 0 && id[n] == b && depth[n] == 0) { depth[n] = depth[c] + 1; q.push_back(n); }
                }
            }
            for (int c : br.cells) br.depth_max = std::max(br.depth_max, depth[c]);
        }
    }

    // Pearls a walker arriving within `horizon` rounds will find in branch b (seen, remembered or due to spawn).
    int pearls(const ares::World& w, int b, int horizon = 8) const {
        if (b < 0 || b >= static_cast<int>(list.size())) return 0;
        int n = 0;
        for (int c : list[b].cells) {
            if (w.occ[c] >= 0) continue;
            if (w.pearl_seen[c] == w.rnd) { n++; continue; }
            bool visible = w.in_vision(c);
            if (visible) {   // seen empty now: only a spawn due within the horizon counts
                if (w.bed[c] == 1 && w.spawn_at[c] >= 0 && w.spawn_at[c] <= w.rnd + horizon) n++;
                continue;
            }
            if (w.pearl_seen[c] >= 0 && w.rnd - w.pearl_seen[c] <= 60) { n++; continue; }
            if (w.bed[c] == 1 && w.spawn_at[c] >= 0 && w.spawn_at[c] <= w.rnd + horizon) { n++; continue; }
            // never observed but known fast bed from the atlas (class 1 = mean gap 1)
            if (w.spawn_at[c] < 0 && !w.atlas_bed.empty() && w.atlas_bed[c] == 1) n++;
        }
        return n;
    }

    bool is_queen(const ares::World& w) const { return (w.me & 4095) <= 1; }

    // Net pearls of one harvesting visit, or a large negative when this dragon must not go in.
    int profit(const ares::World& w, int b) const {
        if (b < 0) return 0;
        if (is_queen(w)) return -99;
        if (w.rnd > 340) return -99;                       // endgame: convert, do not harvest
        if (w.units > w.limit - 2) return -99;             // the escape split at the end needs a unit slot
        int p = pearls(w, b);
        if (w.len + p < 4) return -99;                     // could not even split at the end
        return p - 2;
    }

    // May this dragon target / step into cell c?
    bool allowed(const ares::World& w, int c) const {
        if (c < 0 || c >= NC || id[c] < 0) return true;
        int b = id[c];
        if (w.head >= 0 && w.head < NC && id[w.head] == b) return true;   // already inside: committed
        return profit(w, b) >= 1;
    }
};

inline Branches* g_br = nullptr;

inline bool branch_allowed(const ares::World& w, int c) { return !g_br || g_br->allowed(w, c); }

}  // namespace bokuto
