// ares chassis — CHEAP OPENING POLICY (arm (b) of the C1-B complexity ablation).
//
//   1. SPLIT child_size from the rear while len >= split_min_len, units < limit,
//      round < split_until_round and no enemy head within split_enemy_cheb.
//   2. Otherwise target the cheapest of: a known pearl on the ground, a bed whose
//      pearl will exist when we land (ripe by arrival); ties go to the pearl.
//      No target: the nearest never-seen cell (explore).
//   3. Every candidate step is simulated exactly one step ahead (kelp, own body
//      incl. tail, any dragon part, enemy-head reach, blind portal landing) and
//      room-checked with a time-aware flood; the best tier wins, then progress
//      toward the target.
#pragma once

#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

#include "nav.hpp"
#include "params.hpp"
#include "world.hpp"

namespace ares {

enum class Act { MOVE, SPLIT };

struct Decision {
    Act act = Act::MOVE;
    std::vector<int> dirs;  // MOVE
    int split = 0;          // SPLIT
    int target = -1;
    int tier = -1;
    char why = '-';         // p pearl, b bed, x explore, - none, s split
};

// One-step outcome classes, best first.
enum Tier : int {
    T_ILLEGAL = 0,   // certain death (kelp, body, occupied)
    T_DANGER_CRAMP = 1,
    T_DANGER = 2,    // an enemy head can step there next
    T_CRAMP = 3,     // safe now, but the flood finds too little room
    T_DIVE = 4,      // unpaired portal: landing unknown (SAFE if it is the explore goal)
    T_SAFE = 5,      // includes a paired portal whose (remembered) landing is out of view
};

struct Policy {
    Grid fwd, rev, room;
    std::vector<uint16_t> mask;
    std::vector<uint8_t> danger;
    std::vector<int> danger_cells;
    std::vector<uint16_t> room_mask;

    void mark_danger(const World& w) {
        if (static_cast<int>(danger.size()) != w.NC) danger.assign(w.NC, 0);
        for (int c : danger_cells) danger[c] = 0;
        danger_cells.clear();
        for (int pi : w.enemy_heads) {
            int src = w.parts[pi].cell;
            // An enemy of length L can sprint L-1 steps in one action.
            int reach = Params::enemy_reach;
            auto it = w.mem.find(w.parts[pi].id);
            if (it != w.mem.end() && it->second.vis_len - 1 > reach) reach = it->second.vis_len - 1;
            if (reach > Params::enemy_reach_max) reach = Params::enemy_reach_max;
            std::vector<int> frontier{src}, next;
            for (int s = 0; s < reach; s++) {
                next.clear();
                for (int c : frontier)
                    for (int d = 0; d < 4; d++) {
                        int n = w.dest(c, d);
                        if (n < 0 || danger[n]) continue;
                        danger[n] = 1;
                        danger_cells.push_back(n);
                        if (w.occ[n] < 0 && !w.own[n]) next.push_back(n);
                    }
                frontier.swap(next);
            }
        }
    }

    bool birth_target_is_clear(const World& w, int cell) const {
        for (int pi : w.ally_heads)
            if (w.tdist(w.parts[pi].cell, cell) <= Params::birth_clearance) return false;
        return true;
    }

    // The rear child should start close to a resource site that is not already
    // packed with an allied head. Use only known traversable edges; on a new
    // map, fall back to the scaffold rule until enough of the board is seen.
    bool child_has_nearby_target(const World& w) const {
        if (w.body.empty()) return false;
        const int start = w.body.front();
        std::vector<int16_t> d(w.NC, -1);
        std::vector<int> q;
        q.reserve(w.NC);
        d[start] = 0;
        q.push_back(start);
        bool target = false;
        for (size_t qi = 0; qi < q.size(); qi++) {
            int c = q[qi];
            int depth = d[c];
            if (depth > 0 && (w.bed[c] == 1 || w.pearl_known(c, Params::pearl_ttl)) &&
                birth_target_is_clear(w, c)) {
                target = true;
                break;
            }
            if (depth >= Params::birth_target_horizon) continue;
            for (int dir = 0; dir < 4; dir++) {
                int n = w.dest(c, dir);
                if (n < 0 || d[n] >= 0 || w.own[n] || w.occ[n] >= 0) continue;
                d[n] = static_cast<int16_t>(depth + 1);
                q.push_back(n);
            }
        }
        if (target) return true;
        return w.atlas < 0 && w.seen_count < Params::birth_min_seen;
    }

    bool should_split(const World& w) const {
        if (w.len < Params::split_min_len) return false;
        if (w.len - Params::split_child < unswbc::Constants::MIN_SIZE) return false;
        if (Params::split_child < unswbc::Constants::MIN_SIZE) return false;
        if (w.units >= w.limit) return false;
        if (w.rnd >= Params::split_until_round) return false;
        for (int pi : w.enemy_heads)
            if (w.cheb(w.parts[pi].cell, w.head) <= Params::split_enemy_cheb) return false;
        if (!child_has_nearby_target(w)) return false;
        return true;
    }

    bool ally_nearer(const World& w, int c, int my_d) const {
        if (!Params::ally_yield) return false;
        for (int pi : w.ally_heads)
            if (w.tdist(w.parts[pi].cell, c) < my_d) return true;
        return false;
    }

    struct Room {
        int cells = 0;
        bool escape = false;  // reached one of our own vacated segments
    };

    // Time-aware flood from `start`. segs = our body after the action, tail
    // first, start excluded; segment i is free from depth i + 2 + delay.
    // Other dragons' parts free at vac + delay. Stops at need cells.
    Room flood_room(const World& w, int start, const std::vector<int>& segs, int delay, int need,
                    const std::vector<int>* extra = nullptr, int extra_delay = 0, int seg_offset = 0) {
        room_mask.assign(w.NC, 0);
        for (auto const& p : w.parts) room_mask[p.cell] = static_cast<uint16_t>(p.vac + delay);
        for (int c : w.own_cells)
            if (w.own[c] == 255) room_mask[c] = 1000;
        if (extra)
            for (size_t i = 0; i < extra->size(); i++)
                room_mask[(*extra)[i]] = static_cast<uint16_t>(i + 2 + extra_delay);
        for (size_t i = 0; i < segs.size(); i++)
            room_mask[segs[i]] = static_cast<uint16_t>(i + 2 + delay + seg_offset);
        // Any other head may take a neighbouring cell before our next step.
        for (auto const& p : w.parts) {
            if (!p.head) continue;
            for (int d = 0; d < 4; d++) {
                int n = w.dest(p.cell, d);
                if (n >= 0 && room_mask[n] < Params::head_block + 1 + delay)
                    room_mask[n] = static_cast<uint16_t>(Params::head_block + 1 + delay);
            }
        }
        room_mask[start] = 0;
        // BFS over KNOWN terrain; a cell with an unknown edge credits
        // unknown_credit cells, one with an unpaired portal portal_credit.
        if (static_cast<int>(room.d.size()) != w.NC) {
            room.d.assign(w.NC, -1);
            room.first.assign(w.NC, -1);
            room.parent.assign(w.NC, -1);
        } else {
            for (int c : room.order) room.d[c] = -1;
        }
        room.order.clear();
        room.from = start;
        room.d[start] = 0;
        room.order.push_back(start);
        int credit = 0;
        for (size_t qi = 0; qi < room.order.size(); qi++) {
            int c = room.order[qi];
            int t = room.d[c] + 1;
            int cc = 0;
            for (int dd = 0; dd < 4; dd++) {
                int n = w.dest(c, dd);
                if (n == UNKNOWN) {
                    if (cc < Params::unknown_credit) cc = Params::unknown_credit;
                    continue;
                }
                if (n == UNPAIRED) {
                    if (cc < Params::portal_credit) cc = Params::portal_credit;
                    continue;
                }
                if (n < 0 || room.d[n] >= 0 || room_mask[n] > t) continue;
                room.d[n] = static_cast<int16_t>(t);
                room.order.push_back(n);
            }
            credit += cc;
            if (static_cast<int>(room.order.size()) - 1 + credit >= need) break;
        }
        Room r;
        r.cells = static_cast<int>(room.order.size()) - 1 + credit;
        // Tail chase counts only in a space at least as big as the body.
        if (r.cells >= static_cast<int>(segs.size()) + 1)
            for (size_t i = 0; i < segs.size() && !r.escape; i++)
                if (room.d[segs[i]] > 0) r.escape = true;
        return r;
    }

    int room_need(int len) const {
        int need = len + Params::room_margin;
        if (Params::room_len_mult * len > need) need = Params::room_len_mult * len;
        if (Params::room_min > need) need = Params::room_min;
        if (need > Params::room_cap) need = Params::room_cap;
        return need;
    }

    std::vector<int> segs_;

    // Room after stepping to n (eats: the tail stays).
    Room room_after(const World& w, int n, bool eats) {
        segs_.assign(w.body.begin() + (eats || w.body.empty() ? 0 : 1), w.body.end());
        return flood_room(w, n, segs_, 0, room_need(w.len + (eats ? 1 : 0)), nullptr, 0,
                          (eats || w.body.empty()) ? w.body_offset : w.body_offset);
    }

    // A split must leave both halves room: the child (head = our tail, neck =
    // body[1], moves later this round) and the parent (stands still this turn).
    bool split_has_room(const World& w, int k = Params::split_child) {
        if (static_cast<int>(w.body.size()) < w.len) return false;  // body not fully known
        // child: body[k-1] .. body[0] reversed; its head is body[0]
        std::vector<int> child_segs;
        for (int i = k - 1; i >= 1; i--) child_segs.push_back(w.body[i]);
        std::vector<int> parent(w.body.begin() + k, w.body.end());  // remaining parent body
        Room rc = flood_room(w, w.body[0], child_segs, 0, room_need(k), &parent, 1);
        if (!rc.escape && rc.cells < Params::split_room_min) return false;
        std::vector<int> child_all(w.body.begin(), w.body.begin() + k);
        Room rp = flood_room(w, w.head, parent, 1, room_need(w.len - k), &child_all, 0);
        return rp.escape || rp.cells >= room_need(w.len - k);
    }

    // If every head step is blocked, shed the smallest front section that
    // leaves the largest viable child at the tail. That child can retreat out
    // of a pocket while the trapped parent absorbs the unavoidable loss.
    int emergency_split_size(World& w) {
        if (w.len < 2 * unswbc::Constants::MIN_SIZE || w.body.empty()) return 0;
        if (static_cast<int>(w.body.size()) < w.len) return Params::split_child;
        int largest_viable = 0;
        int best_fallback = unswbc::Constants::MIN_SIZE;
        int best_margin = -(1 << 30);
        for (int k = unswbc::Constants::MIN_SIZE; k <= w.len - unswbc::Constants::MIN_SIZE; k++) {
            std::vector<int> child_segs;
            for (int i = k - 1; i >= 1; i--) child_segs.push_back(w.body[i]);
            std::vector<int> parent(w.body.begin() + k, w.body.end());
            Room rc = flood_room(w, w.body[0], child_segs, 0, room_need(k), &parent, 1);
            int margin = rc.escape ? Params::room_cap : rc.cells - room_need(k);
            if (margin >= 0) {
                if (k > largest_viable) largest_viable = k;
            } else if (largest_viable == 0 && margin > best_margin) {
                best_margin = margin;
                best_fallback = k;
            }
        }
        return largest_viable > 0 ? largest_viable : best_fallback;
    }

    bool route_uses_portal(const World& w, const Grid& g, int target) const {
        for (int c = target; c != g.from;) {
            int link = g.parent[c];
            if (link < 0) return false;
            int prev = link >> 2;
            int dir = link & 3;
            if (w.is_portal_edge(prev, dir)) return true;
            c = prev;
        }
        return false;
    }

    int target_tie_bonus(const World& w, const Grid& g, int target) const {
        int bonus = 0;
        const int lane = (w.me + (w.team == 'B' ? 2 : 0)) & 3;
        if (w.rnd < Params::opening_lane_rounds && g.first[target] == lane)
            bonus += Params::opening_lane_bonus;
        if (w.rnd < Params::portal_scout_rounds && Params::portal_scout_stride > 0 &&
            w.me % Params::portal_scout_stride == 0 && route_uses_portal(w, g, target))
            bonus += Params::portal_scout_bonus;
        return bonus;
    }

    bool recent_portal_return(const World& w, int dir) const {
        if (!w.is_portal_edge(w.head, dir) || w.last_exit_portal < 0 || w.last_exit_cell < 0 ||
            w.rnd - w.last_exit_round > Params::portal_return_window ||
            w.rnd < w.last_exit_round) return false;
        int key = w.ekey(w.head, dir);
        int previous_id = w.epid[w.last_exit_portal];
        if (previous_id < 0 || w.epid[key] != previous_id) return false;
        return w.tdist(w.head, w.last_exit_cell) <= Params::portal_return_radius;
    }

    Decision decide(World& w) {
        Decision out;
        mark_danger(w);

        if (should_split(w) && split_has_room(w)) {
            out.act = Act::SPLIT;
            out.split = Params::split_child;
            out.why = 's';
            return out;
        }

        // ---- target
        build_block_mask(w, mask);
        // Two passes: a shallow search usually finds a target; the whole map
        // only when it does not (keeps the typical turn cheap).
        int best = -1, best_cost = 1 << 30;
        char why = '-';
        for (int pass = 0; pass < 2 && best < 0; pass++) {
        int depth = pass == 0 ? Params::search_depth1 : (1 << 30);
        dist(w, w.head, mask, fwd, Params::search_cap, depth);
        for (int c : fwd.order) {
            int d = fwd.d[c];
            if (d == 0) continue;
            if (d * 4 - Params::opening_lane_bonus - Params::portal_scout_bonus > best_cost) break;
            int tie_bonus = target_tie_bonus(w, fwd, c);
            if (w.pearl_known(c, Params::pearl_ttl)) {
                if (ally_nearer(w, c, w.tdist(w.head, c))) continue;
                int cost = d * 4 - tie_bonus;
                if (cost < best_cost) {
                    best_cost = cost;
                    best = c;
                    why = 'p';
                }
            } else if (w.bed[c] == 1 && w.spawn_at[c] >= 0) {
                int land = w.rnd + d - 1;  // round our head lands there
                if (w.spawn_at[c] <= land + Params::bed_wait_max) {
                    int cost = d * 4 + Params::bed_tie - tie_bonus;
                    if (cost < best_cost) {
                        best_cost = cost;
                        best = c;
                        why = 'b';
                    }
                }
            }
        }
        if (best < 0 && pass == 0 && static_cast<int>(fwd.order.size()) < Params::search_cap) {
            // shallow pass found nothing: an unseen cell or dive within reach will do
            bool near = false;
            for (int c : fwd.order) near = near || !w.seen[c];
            if (near || !fwd.dives.empty()) break;
        }
        }
        int dive_dir = -1;  // first step toward the chosen dive, if exploring by portal
        if (best < 0) {
            int bd = 1 << 30;
            for (int c : fwd.order) {
                if (w.seen[c]) continue;
                int cost = fwd.d[c] * 4 - target_tie_bonus(w, fwd, c);
                if (cost < bd) {
                    best = c;
                    bd = cost;
                    why = 'x';
                }
            }
            // A newborn knows no portal pairs yet: its parent's body may be
            // just across (dive_min_age).
            if (w.rnd - w.born >= Params::dive_min_age)
            for (auto const& dv : fwd.dives) {
                int cost = dv[2] + Params::dive_cost;
                if (cost < bd) {
                    bd = cost;
                    best = dv[0];  // walk to the portal cell, then cross
                    dive_dir = dv[1];
                    why = 'd';
                }
            }
        }
        out.target = best;
        out.why = why;
        int pref = best >= 0 ? fwd.first[best] : -1;
        if (best == w.head && dive_dir >= 0) pref = dive_dir;
        if (best >= 0) {
            int nb[4];
            for (int d = 0; d < 4; d++) nb[d] = w.dest(w.head, d);
            rev_dist(w, best, rev, Params::search_cap, 1 << 30, nb, 4);
        }

        // ---- candidates
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
            } else if (!w.in_vision(n)) {
                // paired portal, landing remembered but not visible: occupancy unknown
                tier = T_DIVE;
            } else {
                bool eats = w.pearl_seen[n] == w.rnd;
                Room rr = room_after(w, n, eats);
                room_n = rr.cells;
                bool cramped = !rr.escape && rr.cells < room_need(w.len + (eats ? 1 : 0));
                if (danger.size() && danger[n])
                    tier = cramped ? T_DANGER_CRAMP : T_DANGER;
                else
                    tier = cramped ? T_CRAMP : T_SAFE;
            }
            int score = 0;
            if (n >= 0 && !w.in_vision(n)) score -= Params::blind_landing_penalty;
            if (recent_portal_return(w, d)) score -= Params::portal_return_penalty;
            if (n >= 0 && best >= 0) {
                int rd = rev.d[n];
                score -= 16 * (rd >= 0 ? rd : 999);
            }
            if (n >= 0) {
                int md = 99;
                for (int pi : w.enemy_heads) {
                    int dd = w.tdist(n, w.parts[pi].cell);
                    if (dd < md) md = dd;
                }
                if (md <= Params::enemy_near) score -= Params::enemy_near_penalty * (Params::enemy_near + 1 - md);
            }
            if (d == pref) score += 8;
            if (d == w.face) score += Params::keep_facing_bonus;
            score += room_n;  // among cramped moves prefer the roomier
#ifdef ARES_DEBUG
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
        // Boxed in: every step is certain death. A split is a legal action that
        // does not move the head; the parent survives the turn and the child
        // starts at our tail, often on the open side.
        if (best_tier == T_ILLEGAL && Params::split_when_trapped && w.units < w.limit) {
            int k = emergency_split_size(w);
            if (k >= unswbc::Constants::MIN_SIZE && w.len - k >= unswbc::Constants::MIN_SIZE) {
                out.act = Act::SPLIT;
                out.split = k;
                out.why = 't';
            }
        }
        return out;
    }
};

}  // namespace ares
