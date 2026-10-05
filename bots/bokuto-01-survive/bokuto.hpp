// bokuto-01: survival guard on top of the carthage-05 policy.
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

#include "policy.hpp"
#include "world.hpp"

namespace bokuto {

struct Guard {
    int depth_cap = 7;        // turns of survival demanded
    int node_cap = 6000;      // search effort per question
    int nodes = 0;
    std::vector<uint8_t> occ; // own body occupancy during the search

    struct Line { int turns = 0; int eats = 0; };

    static bool better(const Line& a, const Line& b) {
        return a.turns > b.turns || (a.turns == b.turns && a.eats > b.eats);
    }

    // body: tail..head, occ marks its cells. Longest survivable line of one-step moves, up to K turns.
    // Other dragons' parts are fixed obstacles, unknown edges open, an unpaired portal an escape.
    Line survive(const ares::World& w, std::vector<int>& body, int K) {
        Line best;
        if (K == 0) return best;
        nodes++;
        int head = body.back();
        for (int d = 0; d < 4; d++) {
            int n = w.dest(head, d);
            if (n == ares::UNKNOWN) n = w.nbr(head, d);
            if (n == ares::UNPAIRED) { Line l; l.turns = K; if (better(l, best)) best = l; continue; }
            if (n < 0 || w.occ[n] >= 0 || occ[n]) continue;
            bool pearl = w.pearl_seen[n] == w.rnd;
            body.push_back(n); occ[n] = 1;
            int popped = -1;
            if (!pearl) { popped = body.front(); body.erase(body.begin()); occ[popped] = 0; }
            Line sub;
            if (nodes > node_cap) sub.turns = K - 1;     // out of effort: assume the rest is fine
            else sub = survive(w, body, K - 1);
            body.pop_back(); occ[n] = 0;
            if (popped >= 0) { body.insert(body.begin(), popped); occ[popped] = 1; }
            Line l; l.turns = 1 + sub.turns; l.eats = (pearl ? 1 : 0) + sub.eats;
            if (better(l, best)) best = l;
            if (best.turns >= K && best.eats > 0) break;
        }
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
        Line l = survive(w, body, K);
        l.eats += eats;
        return l;
    }

    // Survival of the head part after SPLIT s (the child's cells count as free: it moves or dies first).
    Line after_split(const ares::World& w, int s, int K) {
        std::vector<int> parent(w.body.begin() + s, w.body.end());
        mark(w, parent);
        nodes = 0;
        return survive(w, parent, K);
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

    // Returns true and fills `out` when the policy's action should be replaced. tag: G guard move,
    // C cage split, g longest-lived move when nothing survives.
    bool apply(const ares::World& w, const ares::Decision& dec, ares::Decision& out, char& tag) {
        if (w.body.size() < 2 || static_cast<int>(w.body.size()) != w.len) return false;  // body not fully known
        if (dec.why == 'f') return false;   // a feeder dying into the crown on purpose
        const int K = depth_cap;
        const bool queen = (w.me & 4095) <= 1;
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
