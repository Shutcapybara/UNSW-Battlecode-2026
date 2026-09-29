// anna chassis — CHEAP OPENING POLICY (arm (b) of the C1-B complexity ablation).
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

namespace anna {

enum class Act { MOVE, SPLIT };

struct Decision {
    Act act = Act::MOVE;
    std::vector<int> dirs;  // MOVE
    int split = 0;          // SPLIT
    int target = -1;
    int tier = -1;
    char why = '-';         // p pearl, b bed, x explore, e escape, - none, s split
    int sonar_dir = -1;     // f2: probe ray to cast with this action (-1 none)
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

    bool should_split(const World& w) const {
        if (w.len < Params::split_min_len) return false;
        if (w.len - Params::split_child < unswbc::Constants::MIN_SIZE) return false;
        if (Params::split_child < unswbc::Constants::MIN_SIZE) return false;
        if (w.units >= w.limit) return false;
        if (w.rnd >= Params::split_until_round) return false;
        for (int pi : w.enemy_heads)
            if (w.cheb(w.parts[pi].cell, w.head) <= Params::split_enemy_cheb) return false;
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

    // f2: the single sonar ray we cast last turn (at most one a turn so the
    // next turn's echo is attributable to it)
    int probe_dir = -1, probe_round = -1;

    // f2 transit gate for stepping through the portal edge at head+d.
    // n = landing cell, pid = pair id, side = 0/1 by edge key order.
    bool portal_gate(const World& w, int d, int n, int pid, int side) {
        if (n < 0) return false;
        if (w.in_vision(n) && !w.own[n] && w.occ[n] < 0) return true;  // seen free
        // lower-id dragons move first: a head adjacent to the landing now (or
        // seen there within 2 rounds) can occupy it before we emerge
        if (Params::f2_id_sim) {
            for (auto const& p : w.parts) {
                if (!p.head || p.id >= w.me) continue;
                if (w.tdist(p.cell, n) <= Params::f2_id_sim_dist) return false;
            }
            for (auto const& kv : w.mem) {
                const auto& m = kv.second;
                if (m.ally || m.cell < 0 || m.id >= w.me) continue;
                if (w.rnd - m.last_round <= 2 && w.tdist(m.cell, n) <= Params::f2_id_sim_dist)
                    return false;
            }
        }
        // id parity: one direction on even (round+id), the other on odd
        if (Params::f2_parity && ((w.rnd + w.me) % 2 == 0) != (side == 0)) return false;
        auto it = w.pair_mem.find(pid);
        if (it != w.pair_mem.end() && it->second.exit_cell >= 0) {
            if (w.rnd - it->second.blocked_round <= Params::f2_block_ttl) return false;
            if (w.rnd - it->second.last_clear <= Params::f2_exit_fresh) return true;
        }
        // clean probe echo from last turn along this direction
        if (Params::f2_probe && probe_round == w.rnd - 1 && probe_dir == d) {
            const auto& e = w.echoes;
            return e.ally + e.ally_head + e.enemy + e.enemy_head == 0 && e.kelp == 0;
        }
        return false;
    }

    // Room after stepping to n (eats: the tail stays).
    Room room_after(const World& w, int n, bool eats) {
        segs_.assign(w.body.begin() + (eats || w.body.empty() ? 0 : 1), w.body.end());
        return flood_room(w, n, segs_, 0, room_need(w.len + (eats ? 1 : 0)), nullptr, 0,
                          (eats || w.body.empty()) ? w.body_offset : w.body_offset);
    }

    // A split must leave both halves room: the child (head = our tail, neck =
    // body[1], moves later this round) and the parent (stands still this turn).
    bool split_has_room(const World& w) {
        int k = Params::split_child;
        if (static_cast<int>(w.body.size()) < w.len) return false;  // body not fully known
        // child: body[k-1] .. body[0] reversed; its head is body[0]
        std::vector<int> child_segs;
        for (int i = k - 1; i >= 1; i--) child_segs.push_back(w.body[i]);
        std::vector<int> parent(w.body.begin() + k, w.body.end() - 1);  // tail..neck
        Room rc = flood_room(w, w.body[0], child_segs, 0, Params::split_room_min, &parent, 1);
        if (!rc.escape && rc.cells < Params::split_room_min) return false;
        std::vector<int> child_all(w.body.begin(), w.body.begin() + k);
        Room rp = flood_room(w, w.head, parent, 1, room_need(w.len - k), &child_all, 0);
        return rp.escape || rp.cells >= room_need(w.len - k);
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
            if (d * 4 >= best_cost) break;  // BFS order: nothing cheaper later
            if (w.pearl_known(c, Params::pearl_ttl)) {
                if (ally_nearer(w, c, w.tdist(w.head, c))) continue;
                if (d * 4 < best_cost) {
                    best_cost = d * 4;
                    best = c;
                    why = 'p';
                }
            } else if (w.bed[c] == 1 && w.spawn_at[c] >= 0) {
                int land = w.rnd + d - 1;  // round our head lands there
                if (w.spawn_at[c] <= land + Params::bed_wait_max) {
                    int cost = d * 4 + Params::bed_tie;
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
            for (int c : fwd.order)
                if (!w.seen[c]) {
                    best = c;
                    bd = fwd.d[c];
                    why = 'x';
                    break;
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
        for (int pass = 0; pass < 2; pass++) {
        if (pass == 1 && best_tier > T_ILLEGAL) break;  // discipline yields only to certain death
        for (int d = 0; d < 4; d++) {
            // f2: portal crossing discipline (paired, landing known)
            if (pass == 0 && Params::f2_portal && w.is_portal_edge(w.head, d)) {
                int n0 = w.dest(w.head, d);
                if (n0 >= 0) {
                    int k = w.ekey(w.head, d);
                    int pid = w.epid[k];
                    auto it = w.pends.find(pid);
                    int other = -1;
                    if (it != w.pends.end()) other = it->second[0] == k ? it->second[1] : it->second[0];
                    int side = (other >= 0 && k > other) ? 1 : 0;
                    if (!portal_gate(w, d, n0, pid, side)) continue;
                }
            }
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
            if (n >= 0 && !w.in_vision(n)) {
                // f2b: a memory-fresh, verified-clear exit is not blind
                bool fresh_exit = false;
                if (Params::f2_confident && w.is_portal_edge(w.head, d)) {
                    int pid = w.epid[w.ekey(w.head, d)];
                    auto pm = w.pair_mem.find(pid);
                    if (pm != w.pair_mem.end() && pm->second.exit_cell == n &&
                        w.rnd - pm->second.blocked_round > Params::f2_block_ttl &&
                        w.rnd - pm->second.last_clear <= Params::f2_exit_fresh)
                        fresh_exit = true;
                }
                if (!fresh_exit) score -= Params::blind_landing_penalty;
            }
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
#ifdef ANNA_DEBUG
            fprintf(stderr, "r%d d%c n=%d tier=%d score=%d room=%d\n", w.rnd, dir_char(d), n, tier, score, room_n);
#endif
            if (tier > best_tier || (tier == best_tier && score > best_score)) {
                best_tier = tier;
                best_score = score;
                best_d = d;
            }
        }
        }
        out.tier = best_tier;
        out.dirs = {best_d >= 0 ? best_d : w.face};
        // f2: cast one ray through the adjacent blind portal we would most
        // like to cross next, so that turn's echo can clear it. One ray a
        // turn keeps the next echo attributable.
        if (Params::f2_portal && Params::f2_probe && probe_round < w.rnd) {
            int pd = -1, pd_key = 1 << 30;
            for (int d = 0; d < 4; d++) {
                if (!w.is_portal_edge(w.head, d)) continue;
                int n0 = w.dest(w.head, d);
                if (n0 < 0 || w.in_vision(n0)) continue;  // informed already
                int pid = w.epid[w.ekey(w.head, d)];
                auto it = w.pair_mem.find(pid);
                if (it != w.pair_mem.end() && it->second.exit_cell >= 0 &&
                    w.rnd - it->second.blocked_round > Params::f2_block_ttl &&
                    w.rnd - it->second.last_clear <= Params::f2_exit_fresh)
                    continue;  // fresh verified exit: no probe needed
                int key = (best >= 0 ? w.tdist(n0, best) : 0) * 4 + (d == best_d ? 0 : 1);
                if (key < pd_key) { pd_key = key; pd = d; }
            }
            if (pd >= 0) {
                out.sonar_dir = pd;
                probe_dir = pd;
                probe_round = w.rnd;
            }
        }

        // Boxed in: every step is certain death. A split is a legal action that
        // does not move the head; the parent survives the turn and the child
        // starts at our tail, often on the open side.
        if (best_tier == T_ILLEGAL && Params::split_when_trapped &&
            w.len - Params::split_child >= unswbc::Constants::MIN_SIZE && w.units < w.limit) {
            out.act = Act::SPLIT;
            out.split = Params::split_child;
            out.why = 't';
        }
        return out;
    }
};

}  // namespace anna
