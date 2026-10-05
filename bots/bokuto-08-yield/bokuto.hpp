// bokuto-02: survival guard (time-aware vacancy of other dragons' segments) on top of the carthage-05 policy.
//
// Two failure modes of the base bot are fixed here, both found in live replays (5 Oct 2026):
//  1. Dead ends (Weakhold, Trauma): the policy walks into one-exit pockets to eat ("farm"), then
//     escape-splits and the head part dies against kelp; the child walks into the same pocket.
//     Fix: an exact K-turn survival search over the own body; a chosen move that cannot survive K
//     turns is replaced by one that can.
//  2. Cages (Schooltime): the starting dragons sit in a closed 2x2 kelp box. The base moves into
//     its own neck and the queen dies on round 0; every opponent keeps a length-3 queen circling
//     in the box and wins the round-limit tiebreak. Fix: when no move survives, split so that the
//     head part can circle.
#pragma once

#include <algorithm>
#include <cstdint>
#include <vector>

#include "bokuto_branch.hpp"
#include "policy.hpp"
#include "world.hpp"

namespace bokuto {

struct Guard {
    int depth_cap = 2;        // turns of survival demanded
    int node_cap = 6000;      // search effort per question
    int nodes = 0;
    std::vector<uint8_t> occ; // own body occupancy during the search

    struct Line { int turns = 0; int eats = 0; };

    static bool better(const Line& a, const Line& b) {
        return a.turns > b.turns || (a.turns == b.turns && a.eats > b.eats);
    }

    // body: tail..head, occ marks its cells. Longest survivable line of one-step moves, up to K turns.
    // Other dragons' parts are fixed obstacles, unknown edges open, an unpaired portal an escape.
    // depth: arrival depth of the next step (1 = the first move of the line being searched + offset)
    bool rescue_ok = false;   // set per question: may a stuck head part be left behind by an escape split?
    bool queen_mode = false;  // the queen keeps clear of every other head
    std::vector<uint8_t> head_adj;   // cells next to (or under) another dragon's head
    std::vector<uint8_t> enemy_reach; // cells an enemy head can reach this round (sprint-aware)

    void mark_heads(const ares::World& w) {
        if (static_cast<int>(head_adj.size()) != w.NC) head_adj.assign(w.NC, 0);
        else std::fill(head_adj.begin(), head_adj.end(), 0);
        if (static_cast<int>(enemy_reach.size()) != w.NC) enemy_reach.assign(w.NC, 0);
        else std::fill(enemy_reach.begin(), enemy_reach.end(), 0);
        for (const ares::Part& p : w.parts) {
            if (!p.head) continue;
            head_adj[p.cell] = 1;
            for (int d = 0; d < 4; d++) {
                int n = w.dest(p.cell, d);
                if (n == ares::UNKNOWN) n = w.nbr(p.cell, d);
                if (n >= 0) head_adj[n] = 1;
            }
            if (p.ally) continue;
            // enemy reach: free sprint steps = ceil(len/4); length unknown beyond view -> assume up to 2 steps
            auto it = w.mem.find(p.id);
            int len = it == w.mem.end() ? 4 : std::max(2, it->second.vis_len + (it->second.cut ? 4 : 0));
            int reach = std::min(3, (len + 3) / 4);
            std::vector<int> frontier{p.cell}, next;
            for (int k = 0; k < reach; k++) {
                next.clear();
                for (int c : frontier) for (int d = 0; d < 4; d++) {
                    int n = w.dest(c, d);
                    if (n == ares::UNKNOWN) n = w.nbr(c, d);
                    if (n < 0 || enemy_reach[n]) continue;
                    if (w.occ[n] >= 0 && k == 0) continue;
                    enemy_reach[n] = 1; next.push_back(n);
                }
                frontier.swap(next);
            }
        }
    }

    // The queen's first step must not end where an enemy head can reach this round, nor next to any head,
    // when such a step exists. Returns the replacement direction or -1.
    int queen_dodge(const ares::World& w, const ares::Decision& dec) {
        if (dec.act != ares::Act::MOVE || dec.dirs.empty()) return -1;
        auto landing = [&](int d) {
            int n = w.dest(w.head, d);
            if (n == ares::UNKNOWN) n = w.nbr(w.head, d);
            return n;
        };
        auto legal = [&](int n) { return n >= 0 && w.occ[n] < 0 && !w.own[n]; };
        auto risk = [&](int n) { return (enemy_reach[n] ? 2 : 0) + (head_adj[n] ? 1 : 0) + (w.in_vision(n) ? 0 : 3); };
        int cur = landing(dec.dirs.front());
        if (cur < 0 || !legal(cur) || risk(cur) == 0) return -1;
        int best = -1, best_risk = risk(cur), best_turns = -1;
        for (int d = 0; d < 4; d++) {
            int n = landing(d);
            if (!legal(n)) continue;
            int r = risk(n);
            if (r > best_risk) continue;
            Line l = after_path(w, {d}, 3);
            if (l.turns < 2) continue;
            if (r < best_risk || (r == best_risk && l.turns > best_turns)) { best = d; best_risk = r; best_turns = l.turns; }
        }
        if (best >= 0 && best != dec.dirs.front() && best_risk < risk(cur)) return best;
        return -1;
    }

    // A stuck dragon that can escape-split (child = tail part walks out) counts as surviving when the pocket
    // is one it was allowed to enter.
    bool rescued(const ares::World& w, const std::vector<int>& body) const {
        if (!rescue_ok || body.size() < 4) return false;
        int head = body.back();
        if (!g_br || g_br->id[head] < 0) return false;
        if (!g_br->allowed(w, head)) return false;
        int tail = body.front();
        for (int d = 0; d < 4; d++) {
            int n = w.dest(tail, d);
            if (n == ares::UNKNOWN) n = w.nbr(tail, d);
            if (n >= 0 && !occ[n] && w.occ[n] < 0) return true;
        }
        return false;
    }

    Line survive(const ares::World& w, std::vector<int>& body, int K, int depth = 1) {
        Line best;
        if (K == 0) return best;
        nodes++;
        int head = body.back();
        for (int d = 0; d < 4; d++) {
            int n = w.dest(head, d);
            if (n == ares::UNKNOWN) n = w.nbr(head, d);
            if (n == ares::UNPAIRED) { Line l; l.turns = K; if (better(l, best)) best = l; continue; }
            if (n < 0 || occ[n]) continue;
            if (w.occ[n] >= 0 && (w.parts[w.occ[n]].head || w.parts[w.occ[n]].vac > depth)) continue;
            if (queen_mode && depth >= 2 && head_adj[n]) continue;
            bool pearl = w.pearl_seen[n] == w.rnd;
            body.push_back(n); occ[n] = 1;
            int popped = -1;
            if (!pearl) { popped = body.front(); body.erase(body.begin()); occ[popped] = 0; }
            Line sub;
            if (nodes > node_cap) sub.turns = K - 1;     // out of effort: assume the rest is fine
            else sub = survive(w, body, K - 1, depth + 1);
            body.pop_back(); occ[n] = 0;
            if (popped >= 0) { body.insert(body.begin(), popped); occ[popped] = 1; }
            Line l; l.turns = 1 + sub.turns; l.eats = (pearl ? 1 : 0) + sub.eats;
            if (better(l, best)) best = l;
            if (best.turns >= K && best.eats > 0) break;
        }
        if (best.turns == 0 && rescued(w, body)) { best.turns = K; best.eats = -2; }
        return best;
    }

    void mark(const ares::World& w, const std::vector<int>& body) {
        if (static_cast<int>(occ.size()) != w.NC) occ.assign(w.NC, 0);
        else std::fill(occ.begin(), occ.end(), 0);
        for (int c : body) occ[c] = 1;
    }

    // Survival after taking `path` (1..3 steps this turn) from the current state.
    Line after_path(const ares::World& w, const std::vector<int>& path, int K) {
        std::vector<int> body = w.body;
        mark(w, body);
        Line fail;
        const int free_steps = (w.len + 3) / 4;
        int eats = 0;
        for (size_t k = 0; k < path.size(); k++) {
            int head = body.back();
            int n = w.dest(head, path[k]);
            if (n == ares::UNKNOWN) n = w.nbr(head, path[k]);
            if (n == ares::UNPAIRED) { Line l; l.turns = K; return l; }   // a dive: the policy owns it
            if (n < 0 || w.occ[n] >= 0 || occ[n]) return fail;
            bool pearl = w.pearl_seen[n] == w.rnd;
            body.push_back(n); occ[n] = 1;
            if (pearl) eats++; else { occ[body.front()] = 0; body.erase(body.begin()); }
            if (static_cast<int>(k) >= free_steps) {        // paid step
                if (body.size() <= 2) return fail;
                occ[body.front()] = 0; body.erase(body.begin());
            }
        }
        nodes = 0;
        Line l = survive(w, body, K, 2);
        l.eats += eats;
        return l;
    }

    // Survival of the head part after SPLIT s (the child's cells count as free: it moves or dies first).
    Line after_split(const ares::World& w, int s, int K) {
        std::vector<int> parent(w.body.begin() + s, w.body.end());
        mark(w, parent);
        nodes = 0;
        return survive(w, parent, K, 2);
    }

    // Free cells reachable from the head through known terrain (body cells excluded), capped.
    int room(const ares::World& w, int cap) {
        std::vector<int> q{w.head};
        std::vector<uint8_t> vis(w.NC, 0);
        vis[w.head] = 1;
        int count = 0;
        for (size_t i = 0; i < q.size() && count < cap; i++) {
            int c = q[i];
            for (int d = 0; d < 4; d++) {
                int n = w.dest(c, d);
                if (n == ares::UNKNOWN) n = w.nbr(c, d);
                if (n == ares::UNPAIRED) return cap;
                if (n < 0 || vis[n] || w.occ[n] >= 0 || w.own[n]) continue;
                vis[n] = 1; q.push_back(n); count++;
            }
        }
        return count;
    }

    // ---- harvesting: send a child back into the corridor we are leaving
    int prev_head = -1, exit_branch = -1, exit_round = -1, steps_since_exit = 0, pending_steps = 0;

    void track_exit(const ares::World& w) {
        steps_since_exit += pending_steps; pending_steps = 0;
        if (!g_br) return;
        int cur = g_br->id[w.head];
        if (prev_head >= 0 && prev_head != w.head) {
            int prev = g_br->id[prev_head];
            if (prev >= 0 && cur < 0) { exit_branch = prev; exit_round = w.rnd; steps_since_exit = 0; }
        }
        if (cur >= 0) exit_branch = -1;            // back inside a pocket: no pending send-back
        prev_head = w.head;
    }
    void note_decision(const ares::Decision& d) {
        pending_steps = d.act == ares::Act::MOVE ? static_cast<int>(d.dirs.size()) : 0;
    }

    // SPLIT size to send a 2-segment child back into exit_branch, or 0.
    int sendback(const ares::World& w, const ares::Decision& dec) {
        if (!g_br || exit_branch < 0 || exit_branch >= static_cast<int>(g_br->list.size())) return 0;
        if ((w.me & 4095) <= 1) return 0;
        if (w.rnd <= exit_round || w.rnd > 340) return 0;  // the piece left at the dead end dies first; no harvest late
        if (w.len < 4 || w.units > w.limit - 2) return 0;
        int inside = w.len - 1 - steps_since_exit;        // our segments still in the corridor
        if (inside != 2) { if (inside < 2) exit_branch = -1; return 0; }
        if (static_cast<int>(w.body.size()) == w.len) {   // when the body is known, check it agrees
            if (g_br->id[w.body[0]] != exit_branch || g_br->id[w.body[1]] != exit_branch) { exit_branch = -1; return 0; }
            if (g_br->depth[w.body[0]] <= g_br->depth[w.body[1]]) { exit_branch = -1; return 0; }
        }
        const auto& br = g_br->list[exit_branch];
        for (int c : br.cells) if (w.occ[c] >= 0) return 0;   // someone else is in there
        if (g_br->pearls(w, exit_branch) < 3) { exit_branch = -1; return 0; }
        exit_branch = -1;
        return 2;
    }

    // Returns true and fills `out` when the policy's action should be replaced. tag: G guard move,
    // C cage split, g longest-lived move when nothing survives.
    bool apply(const ares::World& w, const ares::Decision& dec, ares::Decision& out, char& tag) {
        bool r = apply_impl(w, dec, out, tag);
        note_decision(r ? out : dec);
        return r;
    }

    bool apply_impl(const ares::World& w, const ares::Decision& dec, ares::Decision& out, char& tag) {
        track_exit(w);
        if (dec.act != ares::Act::SPLIT && dec.why != 'f') {
            int k = sendback(w, dec);
            if (k > 0) { out = dec; out.act = ares::Act::SPLIT; out.split = k; out.why = 'h'; tag = 'H'; return true; }
        }
        if (w.body.size() < 2 || static_cast<int>(w.body.size()) != w.len) {
            // body not fully known (a long child born in a corridor): only the stuck case is handled here
            if (dec.act == ares::Act::SPLIT || dec.why == 'f') return false;
            bool any = false;
            for (int d = 0; d < 4 && !any; d++) {
                int n = w.dest(w.head, d);
                if (n == ares::UNKNOWN) n = w.nbr(w.head, d);
                if (n == ares::UNPAIRED) any = true;
                else if (n >= 0 && w.occ[n] < 0 && !w.own[n]) any = true;
            }
            if (!any && w.len >= 4 && w.units < w.limit) {
                out = dec; out.act = ares::Act::SPLIT; out.split = w.len - 2; out.why = 't'; tag = 'E';
                return true;
            }
            return false;
        }
        if (dec.why == 'f') return false;   // a feeder dying into the crown on purpose
        if (dec.act == ares::Act::MOVE && !dec.dirs.empty()) {   // a deliberate head-on strike is the policy's call
            int n = w.dest(w.head, dec.dirs.front());
            if (n >= 0 && w.occ[n] >= 0 && w.parts[w.occ[n]].head && !w.parts[w.occ[n]].ally && (w.me & 4095) > 1) return false;
        }
        const bool queen = (w.me & 4095) <= 1;
        const int K = queen ? 4 : depth_cap;
        queen_mode = queen;
        if (!queen && dec.act == ares::Act::MOVE && !dec.dirs.empty()) {
            // bokuto-08: yield to our queen — never end a turn next to her head when another safe step exists
            int qcell = -1;
            for (int pi : w.ally_heads) if ((w.parts[pi].id & 4095) <= 1) qcell = w.parts[pi].cell;
            if (qcell >= 0) {
                auto near_q = [&](int c) { return c >= 0 && w.tdist(c, qcell) <= 1; };
                std::vector<int> body = w.body; mark(w, body);
                int cur = w.dest(w.head, dec.dirs.front());
                if (cur == ares::UNKNOWN) cur = w.nbr(w.head, dec.dirs.front());
                if (near_q(cur) && static_cast<int>(w.body.size()) == w.len) {
                    int best = -1; Line bl;
                    for (int d = 0; d < 4; d++) {
                        int n = w.dest(w.head, d);
                        if (n == ares::UNKNOWN) n = w.nbr(w.head, d);
                        if (n < 0 || near_q(n) || w.occ[n] >= 0 || w.own[n]) continue;
                        Line l = after_path(w, {d}, 3);
                        if (l.turns >= 3 && (best < 0 || better(l, bl))) { best = d; bl = l; }
                    }
                    if (best >= 0) { out = dec; out.act = ares::Act::MOVE; out.dirs = {best}; tag = 'Y'; return true; }
                }
            }
        }
        if (queen) {
            mark_heads(w);
            int d = queen_dodge(w, dec);
            if (d >= 0) { out = dec; out.act = ares::Act::MOVE; out.dirs = {d}; tag = 'Q'; return true; }
        }
        rescue_ok = !queen && w.units <= w.limit - 2;
        Line cur;
        bool reserve_block = false;
        if (dec.act == ares::Act::SPLIT) {
            if (dec.split < 2 || w.len - dec.split < 2) return false;
            // keep one unit slot for the queen (a caged queen survives by splitting at length 4)
            if (!queen && w.units >= w.limit - 1) { reserve_block = true; cur = Line{}; }
            else cur = after_split(w, dec.split, K);
        } else {
            cur = after_path(w, dec.dirs, K);
        }
        // confined (a cage or a pocket): never pay segments for sprint steps there
        bool confined = room(w, 8) < 8;
        bool paid_sprint = dec.act == ares::Act::MOVE && static_cast<int>(dec.dirs.size()) > (w.len + 3) / 4;
        bool force = (confined && paid_sprint) || reserve_block;
        if (cur.turns >= K && !force) return false;

        // single-step alternatives
        int pref0 = dec.act == ares::Act::MOVE && !dec.dirs.empty() ? dec.dirs.front() : w.face;
        int order[4] = {pref0, w.face, (w.face + 1) & 3, (w.face + 3) & 3};
        Line best_mv; int best_d = -1;
        for (int i = 0; i < 4; i++) {
            int d = order[i];
            bool dup = false;
            for (int j = 0; j < i; j++) if (order[j] == d) dup = true;
            if (dup) continue;
            Line l = after_path(w, {d}, K);
            if (best_d < 0 || better(l, best_mv)) { best_mv = l; best_d = d; }
        }
        for (int d = 0; d < 4; d++) {          // any direction not in the order list
            bool seen = false;
            for (int j = 0; j < 4; j++) if (order[j] == d) seen = true;
            if (seen) continue;
            Line l = after_path(w, {d}, K);
            if (better(l, best_mv)) { best_mv = l; best_d = d; }
        }
        // splits whose head part survives; prefer the largest surviving parent
        Line best_sp; int best_s = -1;
        if (w.len >= 4 && w.units < w.limit && (queen || w.units < w.limit - 1)) {
            for (int s = 2; s <= w.len - 2; s++) {
                Line l = after_split(w, s, K);
                if (best_s < 0 || l.turns > best_sp.turns) { best_sp = l; best_s = s; }
            }
        }
        if (queen && best_mv.turns < K && cur.turns < K) {
            // the strict rule (no cell next to any head) finds nothing: relax it and look again
            queen_mode = false;
            cur = dec.act == ares::Act::SPLIT ? after_split(w, dec.split, K) : after_path(w, dec.dirs, K);
            if (cur.turns >= K) return false;
            best_d = -1; best_mv = Line{};
            for (int d = 0; d < 4; d++) {
                Line l = after_path(w, {d}, K);
                if (best_d < 0 || better(l, best_mv)) { best_mv = l; best_d = d; }
            }
        }
        if (best_d >= 0 && best_mv.turns >= K && (force || better(best_mv, cur))) {
            out = dec; out.act = ares::Act::MOVE; out.dirs = {best_d}; tag = 'G';
            return true;
        }
        if (best_s > 0 && best_sp.turns >= K && (dec.act != ares::Act::SPLIT || dec.split != best_s)) {
            out = dec; out.act = ares::Act::SPLIT; out.split = best_s; tag = 'C';
            return true;
        }
        if (dec.act == ares::Act::SPLIT && !reserve_block) return false;   // a doomed split still saves the child
        if (reserve_block && best_d >= 0) {
            out = dec; out.act = ares::Act::MOVE; out.dirs = {best_d}; tag = 'R';
            return true;
        }
        if (best_d >= 0 && better(best_mv, cur)) {
            out = dec; out.act = ares::Act::MOVE; out.dirs = {best_d}; tag = 'g';
            return true;
        }
        return false;
    }
};

}  // namespace bokuto
