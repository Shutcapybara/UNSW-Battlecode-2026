// cx-b01-router — C1-B route finding and bed assignment on the anna chassis.
//
// Per turn, for this dragon (each dragon is its own process):
//   1. terrain analysis (cached per step-table version): peel the terrain to its
//      2-core; peeled cells are dead-end trees, with a depth and a tree id.
//   2. arrival maps: our BFS (time-aware body mask, = Dijkstra with unit steps),
//      the enemy's (multi-source from visible + recently seen enemy heads), and
//      one per nearby visible ally (the nearest ally_cap).
//   3. bed values: pearls we can eat at a bed before the enemy's earliest
//      arrival, over the horizon, discounted, including the next ripenings
//      (observed gap), plus a share of the bed cluster around it.
//   4. assignment: greedy on value over (me + visible allies) x beds with
//      spacing between targets, then a pair-swap pass for me.
//   5. movement: the chassis' exact one-step simulation and room tiers keep the
//      final say; within a tier the score is timing toward the target (patrol:
//      arrive when the pearl spawns), de-convergence from allies' planned
//      paths, dead-end depth, enemy proximity.
//   6. splits are pearl-gated (len >= split_len) and need a first target for the
//      child; trapped dragons split so the child from the tail gets len - 2.
// Every horizon and cap is a function of measured structure (tile count, units,
// visible dragons); nothing depends on map identity.
#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

#include "nav.hpp"
#include "params.hpp"
#include "policy.hpp"
#include "world.hpp"

namespace anna {

struct Router : Policy {
    // ---- terrain analysis (cached)
    int an_version = -1;
    std::vector<uint8_t> dead;     // dead-end depth, 0 = in the 2-core
    std::vector<int> tree;         // dead-end tree id (the tree's first cell), -1 core
    std::vector<int> deg_;
    std::vector<int> q_;

    // ---- per turn
    Grid enemy_g, child_g;
    std::vector<Grid> ally_g;
    std::vector<uint16_t> zero_mask;
    std::vector<double> tree_val;  // per tree id (indexed by cell), expected pearls inside
    std::vector<int> tree_cells_;
    std::vector<int16_t> deconv;   // per cell: earliest step an ally's planned path uses it (0 none)
    std::vector<int> deconv_cells_;
    int H = 30;
    int cur_tree = -1;             // tree id of our head's cell (-1 in the core)
    int prev_target = -1;          // last turn's assigned cluster anchor (hysteresis)

    // Debug/trace
    double last_value = 0;
    int last_first_event = -1;

    int horizon(const World& w) const {
        int h = static_cast<int>(Params::horizon_k * std::sqrt(static_cast<double>(w.NC)));
        return std::clamp(h, Params::horizon_min, Params::horizon_max);
    }

    // Terrain 2-core peel. Unknown edges count as open (optimistic, like the
    // planner), unpaired portals count as an exit that is never removed.
    void analyse(const World& w) {
        if (an_version == w.dest_version) return;
        an_version = w.dest_version;
        const int NC = w.NC;
        deg_.assign(NC, 0);
        dead.assign(NC, 0);
        tree.assign(NC, -1);
        std::vector<uint8_t> removed(NC, 0);
        for (int c = 0; c < NC; c++) {
            int k = 0;
            for (int d = 0; d < 4; d++) {
                int n = w.dest(c, d);
                if (n >= 0 || n == UNKNOWN || n == UNPAIRED) k++;
            }
            deg_[c] = k;
        }
        q_.clear();
        for (int c = 0; c < NC; c++)
            if (deg_[c] <= 1) q_.push_back(c);
        for (size_t qi = 0; qi < q_.size(); qi++) {
            int c = q_[qi];
            if (removed[c]) continue;
            removed[c] = 1;
            for (int d = 0; d < 4; d++) {
                int n = w.dest(c, d);
                if (n == UNKNOWN) n = w.nbr(c, d);
                if (n < 0 || removed[n]) continue;
                if (--deg_[n] <= 1) q_.push_back(n);
            }
        }
        // depth from the core into each tree; tree id = the tree's cell next to the core
        q_.clear();
        std::vector<int16_t> dd(NC, -1);
        for (int c = 0; c < NC; c++)
            if (!removed[c]) dd[c] = 0;
        for (int c = 0; c < NC; c++) {
            if (removed[c]) continue;
            for (int d = 0; d < 4; d++) {
                int n = w.dest(c, d);
                if (n == UNKNOWN) n = w.nbr(c, d);
                if (n >= 0 && removed[n] && dd[n] < 0) {
                    dd[n] = 1;
                    tree[n] = n;
                    q_.push_back(n);
                }
            }
        }
        for (size_t qi = 0; qi < q_.size(); qi++) {
            int c = q_[qi];
            for (int d = 0; d < 4; d++) {
                int n = w.dest(c, d);
                if (n == UNKNOWN) n = w.nbr(c, d);
                if (n >= 0 && removed[n] && dd[n] < 0) {
                    dd[n] = static_cast<int16_t>(dd[c] + 1);
                    tree[n] = tree[c];
                    q_.push_back(n);
                }
            }
        }
        for (int c = 0; c < NC; c++) {
            if (!removed[c]) continue;
            if (dd[c] < 0) {  // a component with no core at all: all of it is a dead end
                dead[c] = 40;
                tree[c] = c;
            } else {
                dead[c] = static_cast<uint8_t>(std::min<int>(dd[c], 250));
            }
        }
    }

    // Multi-source BFS over terrain only (sources at depth 0), up to max_depth.
    void msbfs(const World& w, const std::vector<int>& src, Grid& g, int max_depth) {
        if (static_cast<int>(zero_mask.size()) != w.NC) zero_mask.assign(w.NC, 0);
        if (static_cast<int>(g.d.size()) != w.NC) {
            g.d.assign(w.NC, -1);
            g.first.assign(w.NC, -1);
            g.parent.assign(w.NC, -1);
        } else {
            for (int c : g.order) g.d[c] = -1;
        }
        g.order.clear();
        g.dives.clear();
        for (int s : src)
            if (s >= 0 && g.d[s] < 0) {
                g.d[s] = 0;
                g.order.push_back(s);
            }
        for (size_t qi = 0; qi < g.order.size(); qi++) {
            int c = g.order[qi];
            if (g.d[c] >= max_depth) break;
            int t = g.d[c] + 1;
            for (int d = 0; d < 4; d++) {
                int n = w.step_opt(c, d);
                if (n < 0 || g.d[n] >= 0) continue;
                g.d[n] = static_cast<int16_t>(t);
                g.order.push_back(n);
            }
        }
    }

    int bed_gap(const World& w, int b) const {
        int g = w.gap_obs[b];
        if (g <= 0 && w.gap_n > 0) g = static_cast<int>(w.gap_sum / w.gap_n);
        if (g <= 0 && w.atlas >= 0 && !w.atlas_bed.empty() && w.atlas_bed[b] > 0)
            g = 1 << std::min(10, w.atlas_bed[b] - 1);
        if (g <= 0) g = Params::default_gap;
        return std::max(2, g);
    }

    // Pearls a dragon arriving (landing) at step A can eat at bed/pearl cell b
    // before the enemy's earliest arrival E, over the horizon, discounted.
    // first_event: the step of the first pearl it would eat (for patrol timing).
    double cell_value(const World& w, int b, int A, int E, int* first_event = nullptr) const {
        if (A < 1) A = 1;
        double v = 0;
        auto add = [&](int t, double p) {
            if (t >= H) return;
            double wt = t < E ? 1.0 : (1.0 - Params::enemy_conservatism);
            v += std::pow(Params::disc, t) * p * wt;
        };
        bool pearl_now = w.pearl_known(b, Params::pearl_ttl);
        int fe = -1;
        if (w.bed[b] != 1) {  // a pearl on a non-bed cell (death drop)
            if (pearl_now) {
                add(A, Params::pearl_w);
                fe = A;
            }
        } else {
            int gap = bed_gap(w, b);
            int t;
            if (pearl_now) {
                add(A, Params::pearl_w);
                fe = A;
                t = A + gap;
            } else if (w.spawn_at[b] >= 0 && w.spawn_at[b] >= w.rnd) {
                t = std::max(A, w.spawn_at[b] - w.rnd + 1);
                add(t, 1.0);
                fe = t;
                t += gap;
            } else if (w.spawn_at[b] >= 0) {
                // spawn round passed out of view: a pearl may be waiting
                add(A, Params::unseen_bed_p);
                fe = A;
                t = A + gap;
            } else {
                // never seen: the observed share of beds holding a pearl at first sight
                double p = (w.bed_first_pearl + Params::unseen_bed_p * Params::unseen_prior_n) /
                           (w.bed_first_n + Params::unseen_prior_n);
                add(A, p);
                fe = A;
                t = A + gap;
            }
            // later ripenings: a dragon can fetch other pearls meanwhile, so they
            // count only partly (patrol value must not beat a pearl on the ground)
            for (int guard = 0; t < H && guard < 64; guard++, t += gap) add(t, Params::later_event_w);
        }
        if (first_event) *first_event = fe;
        return v;
    }

    // Other dragons' visible parts within Chebyshev r of c (heads count double).
    int crowd(const World& w, int c, int r) const {
        int k = 0;
        for (auto const& p : w.parts)
            if (w.cheb(p.cell, c) <= r) k += p.head ? 2 : 1;
        return k;
    }

    bool is_target_cell(const World& w, int c) const {
        return w.bed[c] == 1 || w.pearl_known(c, Params::pearl_ttl);
    }

    // Value of targeting b for a dragon whose arrival grid is g.
    double target_value(const World& w, const Grid& g, int b, int* fe = nullptr) const {
        int A = g.d[b];
        if (A < 0 || A >= H) return -1;
        int E = enemy_g.d.empty() || enemy_g.d[b] < 0 ? 1 << 20 : enemy_g.d[b];
        double v = cell_value(w, b, A, E, fe);
        // cluster share
        const int r = Params::cluster_r;
        int bx = b % w.W, by = b / w.W;
        for (int dy = -r; dy <= r; dy++)
            for (int dx = -r; dx <= r; dx++) {
                int m = std::abs(dx) + std::abs(dy);
                if (m == 0 || m > r) continue;
                int x = ((bx + dx) % w.W + w.W) % w.W, y = ((by + dy) % w.H + w.H) % w.H;
                int c = y * w.W + x;
                if (!is_target_cell(w, c)) continue;
                int E2 = enemy_g.d.empty() || enemy_g.d[c] < 0 ? 1 << 20 : enemy_g.d[c];
                v += Params::cluster_w * cell_value(w, c, A + m, E2);
            }
        // crowding: a bed inside a knot of dragons is worth less (and dangerous)
        v /= 1.0 + Params::crowd_w * crowd(w, b, 2);
        // dead-end trees: only worth it when the tree holds enough to pay the exit split
        if (dead[b] > 0 && tree[b] != cur_tree) {  // entering: already inside costs nothing more
            int t = tree[b];
            double tv = t >= 0 ? tree_val[t] : 0;
            if (tv < Params::dead_end_min_value || w.len + tv < 4) v *= 0.1;
        }
        return v;
    }

    void compute_tree_values(const World& w) {
        if (static_cast<int>(tree_val.size()) != w.NC) tree_val.assign(w.NC, 0);
        for (int c : tree_cells_) tree_val[c] = 0;
        tree_cells_.clear();
        for (int c = 0; c < w.NC; c++) {
            if (!dead[c] || tree[c] < 0) continue;
            double p = 0;
            // what a dragon walking in can actually eat: pearls there now, and beds
            // that spawn before it passes (it cannot wait inside a 1-wide tree)
            if (w.pearl_known(c, Params::pearl_ttl)) p = 1;
            else if (w.bed[c] == 1 && w.spawn_at[c] >= 0 &&
                     w.spawn_at[c] - w.rnd <= dead[c] + Params::tree_ripe_slack) p = 0.8;
            else if (w.bed[c] == 1 && w.spawn_at[c] < 0) p = Params::unseen_bed_p;
            if (p > 0) {
                int t = tree[c];
                if (tree_val[t] == 0) tree_cells_.push_back(t);
                tree_val[t] += p;
            }
        }
    }

    // Mark the first deconv_k cells of an ally's planned path.
    void mark_path(const World& w, const Grid& g, int from, int to) {
        std::vector<int> dirs = path(w, g, to);
        int c = from;
        for (int s = 0; s < static_cast<int>(dirs.size()) && s < Params::deconv_k; s++) {
            int n = w.dest(c, dirs[s]);
            if (n < 0) n = w.nbr(c, dirs[s]);
            if (deconv[n] == 0 || deconv[n] > s + 1) {
                if (deconv[n] == 0) deconv_cells_.push_back(n);
                deconv[n] = static_cast<int16_t>(s + 1);
            }
            c = n;
        }
    }

    Decision decide_router(World& w) {
        Decision out;
        H = horizon(w);
        mark_danger(w);
        analyse(w);
        compute_tree_values(w);
        // Committed to a dead-end tree only when no legal step leads back toward
        // its mouth (a newborn at the rear of a feeding parent usually can leave).
        cur_tree = -1;
        if (dead[w.head] > 0) {
            bool can_leave = false;
            for (int d = 0; d < 4; d++) {
                int n = w.dest(w.head, d);
                if (n >= 0 && !w.own[n] && w.occ[n] < 0 && dead[n] < dead[w.head]) can_leave = true;
            }
            if (!can_leave) cur_tree = tree[w.head];
        }
        if (static_cast<int>(deconv.size()) != w.NC) deconv.assign(w.NC, 0);
        for (int c : deconv_cells_) deconv[c] = 0;
        deconv_cells_.clear();

        // ---- arrival maps
        build_block_mask(w, mask);
        dist(w, w.head, mask, fwd, 1 << 30, H);
        std::vector<int> esrc;
        for (int pi : w.enemy_heads) esrc.push_back(w.parts[pi].cell);
        for (auto const& kv : w.mem) {
            const DragonMem& m = kv.second;
            if (!m.ally && m.cell >= 0 && m.last_round < w.rnd && w.rnd - m.last_round <= Params::enemy_mem_ttl)
                esrc.push_back(m.cell);
        }
        if (!esrc.empty()) msbfs(w, esrc, enemy_g, H);
        else {
            if (static_cast<int>(enemy_g.d.size()) != w.NC) enemy_g.d.assign(w.NC, -1);
            else for (int c : enemy_g.order) enemy_g.d[c] = -1;
            enemy_g.order.clear();
        }

        // nearest visible allies
        std::vector<int> allies;  // part indices
        for (int pi : w.ally_heads) allies.push_back(pi);
        std::sort(allies.begin(), allies.end(), [&](int a, int b) {
            int da = w.tdist(w.parts[a].cell, w.head), db = w.tdist(w.parts[b].cell, w.head);
            return da != db ? da < db : w.parts[a].id < w.parts[b].id;
        });
        if (static_cast<int>(allies.size()) > Params::ally_cap) allies.resize(Params::ally_cap);
        if (ally_g.size() < allies.size()) ally_g.resize(allies.size());
        for (size_t i = 0; i < allies.size(); i++) dist(w, w.parts[allies[i]].cell, mask, ally_g[i], 1 << 30, H);

        // ---- candidate targets
        const int bed_cap = w.NC > Params::big_map_tiles ? Params::bed_cap_large : Params::bed_cap_small;
        std::vector<int> cand;
        std::vector<uint8_t> in_cand;  // tiny maps: dedupe via linear search is fine
        auto add_cands = [&](const Grid& g, int cap) {
            int k = 0;
            for (int c : g.order) {
                if (k >= cap) break;
                if (g.d[c] == 0 || !is_target_cell(w, c)) continue;
                if (std::find(cand.begin(), cand.end(), c) == cand.end()) cand.push_back(c);
                k++;
            }
        };
        add_cands(fwd, bed_cap);
        for (size_t i = 0; i < allies.size(); i++) add_cands(ally_g[i], 8);

        // ---- assignment: greedy on value, spacing between targets
        struct Pair {
            double v;
            int dragon;  // 0 = me, i+1 = allies[i]
            int id;
            int cell;
        };
        std::vector<Pair> pairs;
        const int nd = 1 + static_cast<int>(allies.size());
        std::vector<std::vector<double>> val(nd, std::vector<double>(cand.size(), -1));
        for (size_t j = 0; j < cand.size(); j++) {
            val[0][j] = target_value(w, fwd, cand[j]);
            if (prev_target >= 0 && w.tdist(cand[j], prev_target) <= Params::cluster_r)
                val[0][j] *= Params::target_hysteresis;
            if (val[0][j] > 0) pairs.push_back({val[0][j], 0, w.me, cand[j]});
            for (size_t i = 0; i < allies.size(); i++) {
                val[i + 1][j] = target_value(w, ally_g[i], cand[j]);
                if (val[i + 1][j] > 0) pairs.push_back({val[i + 1][j], static_cast<int>(i) + 1, w.parts[allies[i]].id, cand[j]});
            }
        }
        std::sort(pairs.begin(), pairs.end(), [](const Pair& a, const Pair& b) {
            if (a.v != b.v) return a.v > b.v;
            if (a.id != b.id) return a.id < b.id;
            return a.cell < b.cell;
        });
        std::vector<int> assigned(nd, -1);
        std::vector<int> taken;
        auto spaced = [&](int c) {
            for (int t : taken)
                if (w.tdist(t, c) < Params::spacing_r) return false;
            return true;
        };
        for (auto const& p : pairs) {
            if (assigned[p.dragon] >= 0) continue;
            if (!spaced(p.cell)) continue;
            assigned[p.dragon] = p.cell;
            taken.push_back(p.cell);
            if (assigned[0] >= 0 && p.dragon == 0) {
                // keep going only far enough to know the allies' routes near us
            }
        }
        // pair-swap for me
        auto vidx = [&](int dragon, int cell) {
            for (size_t j = 0; j < cand.size(); j++)
                if (cand[j] == cell) return val[dragon][j];
            return -1.0;
        };
        if (assigned[0] >= 0) {
            for (int i = 1; i < nd; i++) {
                if (assigned[i] < 0) continue;
                double cur = vidx(0, assigned[0]) + vidx(i, assigned[i]);
                double sw = vidx(0, assigned[i]) + vidx(i, assigned[0]);
                if (sw > cur + 1e-9) std::swap(assigned[0], assigned[i]);
            }
        }
        for (int i = 1; i < nd; i++)
            if (assigned[i] >= 0) mark_path(w, ally_g[i - 1], w.parts[allies[i - 1]].cell, assigned[i]);

        int target = assigned[0];
        // move toward the best single cell of the assigned cluster (earliest pearl)
        if (target >= 0) {
            prev_target = target;
            const int r = Params::cluster_r;
            int tx = target % w.W, ty = target / w.W;
            double bestv = -1;
            int bestc = target;
            for (int dy = -r; dy <= r; dy++)
                for (int dx = -r; dx <= r; dx++) {
                    if (std::abs(dx) + std::abs(dy) > r) continue;
                    int x = ((tx + dx) % w.W + w.W) % w.W, y = ((ty + dy) % w.H + w.H) % w.H;
                    int c = y * w.W + x;
                    if (!is_target_cell(w, c) || fwd.d[c] <= 0) continue;
                    int E = enemy_g.d.empty() || enemy_g.d[c] < 0 ? 1 << 20 : enemy_g.d[c];
                    double v = cell_value(w, c, fwd.d[c], E);
                    if (v > bestv) {
                        bestv = v;
                        bestc = c;
                    }
                }
            target = bestc;
        } else {
            prev_target = -1;
        }
        char why = target >= 0 ? (w.pearl_known(target, Params::pearl_ttl) ? 'p' : 'b') : '-';
        int first_event = -1;
        if (target >= 0) last_value = target_value(w, fwd, target, &first_event);
        last_first_event = first_event;

        // ---- split (pearl-gated; the child needs a first target)
        if (w.len >= Params::split_len && w.units < w.limit && w.rnd < Params::split_round_max &&
            w.len - Params::split_child >= unswbc::Constants::MIN_SIZE) {
            bool enemy_close = false;
            for (int pi : w.enemy_heads)
                if (w.cheb(w.parts[pi].cell, w.head) <= Params::split_enemy_cheb) enemy_close = true;
            int near_heads = 0;
            for (auto const& p : w.parts)
                if (p.head && w.cheb(p.cell, w.head) <= 3) near_heads++;
            if (!enemy_close && near_heads <= Params::split_crowd_max && split_has_room(w) &&
                child_has_target(w, target)) {
                out.act = Act::SPLIT;
                out.split = Params::split_child;
                out.why = 's';
                out.target = target;
                return out;
            }
        }

        // ---- no target: explore like the chassis (unseen cell / dive)
        int dive_dir = -1;
        if (target < 0) {
            int bd = 1 << 30;
            for (int c : fwd.order)
                if (!w.seen[c]) {
                    target = c;
                    bd = fwd.d[c];
                    why = 'x';
                    break;
                }
            if (w.rnd - w.born >= Params::dive_min_age)
                for (auto const& dv : fwd.dives) {
                    int cost = dv[2] + Params::dive_cost;
                    if (cost < bd) {
                        bd = cost;
                        target = dv[0];
                        dive_dir = dv[1];
                        why = 'd';
                    }
                }
            if (target < 0) {
                // nothing within the horizon: whole-map search for anything
                dist(w, w.head, mask, fwd);
                for (int c : fwd.order)
                    if (fwd.d[c] > 0 && (is_target_cell(w, c) || !w.seen[c])) {
                        target = c;
                        why = 'f';
                        break;
                    }
            }
        }
        out.target = target;
        out.why = why;
        int pref = target >= 0 && fwd.d[target] >= 0 ? fwd.first[target] : -1;
        if (target == w.head && dive_dir >= 0) pref = dive_dir;
        if (target >= 0) {
            int nb[4];
            for (int d = 0; d < 4; d++) nb[d] = w.dest(w.head, d);
            rev_dist(w, target, rev, 1 << 30, 1 << 30, nb, 4);
        }
        // timing: desired distance to the target after this move
        int want = 0;
        bool patrol = false;
        if (target >= 0 && (why == 'b' || why == 'p') && first_event > 0) {
            int cur = rev.d[w.head] >= 0 ? rev.d[w.head] : 999;
            int slack = first_event - 1;  // steps we may spend before landing
            want = std::min(slack, Params::patrol_r);
            if (cur - 1 > want) want = cur - 1;  // still approaching
            patrol = slack > 0;
        }
        bool in_tree_target = target >= 0 && dead[target] > 0 && tree[target] >= 0 &&
                              (tree[target] == cur_tree ||
                               (tree_val[tree[target]] >= Params::dead_end_min_value &&
                                w.len + tree_val[tree[target]] >= 4));

#ifdef ANNA_DEBUG
        fprintf(stderr, "T r%d head=%d dead=%d tree=%d tgt=%d tdead=%d ttree=%d tval=%.2f intree=%d fe=%d val=%.3f\n",
                w.rnd, w.head, dead[w.head], cur_tree, target, target >= 0 ? dead[target] : -1,
                target >= 0 ? tree[target] : -1, target >= 0 && tree[target] >= 0 ? tree_val[tree[target]] : -1.0,
                (int)in_tree_target, first_event, last_value);
#endif
        // ---- candidates: chassis tiers, router score
        int best_d = -1, best_tier = -1, best_score = -(1 << 30);
        for (int d = 0; d < 4; d++) {
            int n = w.dest(w.head, d);
            int tier;
            int room_n = 0;
            if (n == BLOCKED || n == UNKNOWN) {
                tier = T_ILLEGAL;
            } else if (n == UNPAIRED) {
                tier = (d == pref && why == 'd') ? T_SAFE : T_DIVE;
            } else if (w.own[n] || w.occ[n] >= 0) {
                tier = T_ILLEGAL;
            } else {
                bool eats = w.pearl_seen[n] == w.rnd;
                int heads2 = 0;
                for (auto const& p : w.parts)
                    if (p.head && w.cheb(p.cell, n) <= 2) heads2++;
                int need = std::min(Params::room_cap, room_need(w.len + (eats ? 1 : 0)) + Params::crowd_room_k * heads2);
                segs_.assign(w.body.begin() + (eats || w.body.empty() ? 0 : 1), w.body.end());
                Room rr = flood_room(w, n, segs_, 0, need, nullptr, 0, w.body_offset);
                room_n = rr.cells;
                bool cramped = !rr.escape && rr.cells < need;
                // planned dead-end feeding: the exit is a split, so a cramped step
                // into the target's own tree is acceptable
                if (cramped && in_tree_target && dead[n] > 0 && tree[n] == tree[target]) cramped = false;
                if (danger.size() && danger[n])
                    tier = cramped ? T_DANGER_CRAMP : T_DANGER;
                else
                    tier = cramped ? T_CRAMP : T_SAFE;
                if (!w.in_vision(n)) {
                    // landing through a paired portal, out of view
                    int open = 0;
                    for (int e = 0; e < 4; e++) open += w.dest(n, e) >= 0 || w.dest(n, e) == UNKNOWN;
                    bool route = Params::portal_route_safe && d == pref && open >= Params::blind_landing_min_exits &&
                                 dead[n] == 0;
                    if (!route && tier == T_SAFE) tier = T_DIVE;
                }
            }
            int score = 0;
            if (n >= 0 && !w.in_vision(n)) score -= Params::blind_landing_penalty;
            if (n >= 0 && target >= 0) {
                int rd = rev.d[n];
                if (rd < 0) rd = 999;
                if (why == 'b' || why == 'p') {
                    score -= 16 * std::abs(rd - want);
                    if (patrol && rd == 0 && first_event > 1) score -= Params::early_on_bed_pen;
                } else {
                    score -= 16 * rd;
                }
            }
            if (n >= 0) {
                int md = 99;
                for (int pi : w.enemy_heads) {
                    int dd = w.tdist(n, w.parts[pi].cell);
                    if (dd < md) md = dd;
                }
                if (md <= Params::enemy_near) score -= Params::enemy_near_penalty * (Params::enemy_near + 1 - md);
                if (deconv[n]) score -= Params::deconv_w * (Params::deconv_k + 1 - deconv[n]) / Params::deconv_k *
                                        (deconv[n] == 1 ? 3 : 1);
                if (dead[n] > 0 && !(in_tree_target && tree[n] == tree[target]))
                    score -= Params::dead_end_pen * std::min<int>(dead[n], 8);
            }
            if (d == pref) score += 8;
            if (d == w.face) score += Params::keep_facing_bonus;
            score += std::min(room_n, 16);
#ifdef ANNA_DEBUG
            fprintf(stderr, "r%d d%c n=%d tier=%d score=%d room=%d\n", w.rnd, dir_char(d), n, tier, score, room_n);
#endif
            if (tier > best_tier || (tier == best_tier && score > best_score)) {
                best_tier = tier;
                best_score = score;
                best_d = d;
            }
        }
        out.tier = best_tier;
        out.dirs = {best_d >= 0 ? best_d : w.face};

        // Trapped: every step is death -> split, the child (from the tail) takes len - 2.
        // Inside a dead-end tree with nothing left to eat ahead -> the same, proactively.
        bool dead_end_exit = dead[w.head] > 0 && !(in_tree_target && tree[w.head] == tree[target]) &&
                             best_tier <= T_CRAMP;
        if ((best_tier == T_ILLEGAL || dead_end_exit) && Params::split_when_trapped && w.len >= 4 &&
            w.units < w.limit) {
            out.act = Act::SPLIT;
            out.split = Params::trapped_big_child ? w.len - 2 : Params::split_child;
            out.why = 't';
        }
        return out;
    }

    // The child (head = our tail) must have a target it reaches before us and
    // before any visible ally, within the horizon, away from our own target.
    bool child_has_target(World& w, int my_target) {
        if (!Params::split_needs_target || w.len >= Params::split_force_len) return true;
        if (w.rnd < Params::split_open_rounds) return true;  // the opening: split the starters at once
        if (w.body.empty()) return false;
        int c0 = w.body[0];
        dist(w, c0, mask, child_g, 1 << 30, H);
        for (int c : child_g.order) {
            int dc = child_g.d[c];
            if (dc == 0 || !is_target_cell(w, c)) continue;
            if (my_target >= 0 && w.tdist(c, my_target) < Params::spacing_r) continue;
            int dm = fwd.d[c] >= 0 ? fwd.d[c] : 1 << 20;
            if (dc > dm) continue;
            bool ally_first = false;
            for (int pi : w.ally_heads)
                if (w.tdist(w.parts[pi].cell, c) < dc) ally_first = true;
            if (ally_first) continue;
            int E = enemy_g.d.empty() || enemy_g.d[c] < 0 ? 1 << 20 : enemy_g.d[c];
            if (cell_value(w, c, dc, E) > 0.05) return true;
        }
        return false;
    }
};

}  // namespace anna
