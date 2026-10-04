// Ares V06 — pure Tyr V12 policy port on the Anna A02 C++ runtime scaffold.
//
// Target choice, candidate scoring, split choices and radio decisions follow
// Tyr V12. Anna supplies the C++ protocol adapter and persistent world model.
#pragma once

#include "helper.hpp"
#include "hb1_features.hpp"
#include "hb1_gbt.hpp"
#include "hb1_compact.hpp"

namespace hb1 {
inline std::string edge_token(unswbc::Edge const& e) {
    if (e.get_edge_type() == unswbc::EdgeType::KELP) return "w";
    if (e.get_edge_type() == unswbc::EdgeType::PORTAL) return std::to_string(e.get_portal_id());
    return ".";
}
// The round block exactly as features_view.parse_block sees it (same as hb1-01-structured/hb1_policy.hpp).
inline Block block_from(unswbc::Controller const& ct, unswbc::Game const& game) {
    Block b;
    b.round = game.get_round_num(); b.dir = ct.get_dir().value; b.length = ct.get_length();
    b.units = ct.get_unit_count(); b.n_msgs = int(ct.sonar_messages.size());
    auto const e = ct.get_sonar_echoes();
    b.has_echoes = true;
    b.echoes = {e.kelp, e.ally, e.ally_head, e.enemy, e.enemy_head};
    auto const& tiles = ct.get_tiles();
    for (int k = 0; k < 49; k++) {
        auto const& t = tiles[k];
        b.tiles[k] = {t.position.x, t.position.y, t.has_pearl() ? 1 : 0, t.get_pearl_time()};
        if (auto const* p = t.get_dragon())
            b.bodies.push_back({p->team.value, p->dragon_id, t.position.x, t.position.y, p->dir.value, p->is_head()});
    }
    for (int r = 0; r < 7; r++)
        for (int c = 0; c < 7; c++) {
            b.Hm[r][c] = edge_token(tiles[r * 7 + c].edges[0]);
            b.Vm[r][c] = edge_token(tiles[r * 7 + c].edges[3]);
        }
    for (int c = 0; c < 7; c++) b.Hm[7][c] = edge_token(tiles[6 * 7 + c].edges[2]);
    for (int r = 0; r < 7; r++) b.Vm[r][7] = edge_token(tiles[r * 7 + 6].edges[1]);
    return b;
}
}  // namespace hb1

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <unordered_set>
#include <unordered_map>
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
    char why = '-';         // p pearl, b bed, x explore, h prey, e escape, s split
};

struct Policy {
    Grid fwd, rev, room;
    std::vector<uint16_t> mask;
    std::vector<uint8_t> danger;
    std::vector<int> danger_cells;
    struct EnemyThreat { int steps = 0, id = -1, length = 1; };
    std::vector<std::vector<EnemyThreat>> threats;
    std::unordered_map<int, int> threat_support;
    std::vector<uint16_t> room_mask;
    std::vector<uint8_t> visits;
    std::array<double, 4> momentum{};
    int previous_target = -1;

    struct DensityReport {
        double x = 0.0, y = 0.0, allies = 1.0, enemies = 0.0;
        int rnd = -1;
        uint64_t packet = 0;
    };
    std::unordered_map<int, DensityReport> density_reports;
    std::vector<int> density_order; // Python REPORTS insertion order for stable field sums
    bool have_local_density = false;
    double local_x = 0.0, local_y = 0.0, local_allies = 1.0, local_enemies = 0.0;
    int local_density_round = -1, local_head = -1;
    int crown_id = -1, crown_cell = -1, crown_len = 0, crown_round = -1;
    int last_crown_round = 0;
    bool role_crown = false, role_feeder = false, inherit_pending = false;
    int prey_id = -1, prey_cell = -1, prey_len = 0, prey_round = -1;
    std::array<uint64_t, 4> sonar_out{};
    std::vector<int> sonar_order;
    bool escape_active = false, escape_packet_seen = false;
    int escape_parent = -1, escape_origin = -1, escape_start = -1, escape_waypoint = -1;
    int escape_pause_used = 0;
    uint64_t pending_handoff = 0;
    int pending_handoff_round = -1;
    std::vector<int> escape_origin_dist;
    std::vector<uint8_t> escape_plan_mask;
    std::vector<int16_t> escape_plan_dist;
    bool birth_packet_seen = false;
    int escape_plan_target = -1;

    // H-S1: relay portal transits, and treat a stale transit with no later
    // team report from its dragon as a possible three-round death. All state
    // is process-local; the packets below carry source id and original round.
    struct PortalEvent { int pid = -1, actor = -1, round = -1; bool resolved = false; };
    std::vector<PortalEvent> portal_events;
    std::vector<int> portal_alive_round = std::vector<int>(8192, -1);
    std::vector<int> portal_last_transit_round = std::vector<int>(256, -1);
    std::vector<int> portal_trauma_round = std::vector<int>(256, -1);
    uint64_t portal_relay_packet = 0;
    int portal_relay_round = -1;

    struct Search {
        std::vector<int> dist;
        std::vector<uint8_t> mask;
        std::vector<int> order;
    };
    struct Topology {
        int area = 0, branches = 0, degree = 0, max_degree = 0;
    };

    void bounded_search(const World& w, int start, int max_depth, int cap,
                        const std::vector<int>* body, Search& out) const {
        out.dist.assign(w.NC, -1); out.mask.assign(w.NC, 0); out.order.clear();
        if (start < 0 || start >= w.NC) return;
        std::vector<int> own_index(w.NC, -1);
        if (body) for (size_t i = 0; i < body->size(); i++) own_index[(*body)[i]] = static_cast<int>(i);
        out.dist[start] = 0; out.order.push_back(start);
        for (size_t qi = 0; qi < out.order.size() && static_cast<int>(out.order.size()) < cap; qi++) {
            int c = out.order[qi], nd = out.dist[c] + 1;
            if (nd > max_depth) continue;
            for (int d = 0; d < 4; d++) {
                int n = w.step_opt(c, d);
                if (n < 0 || n == c) continue;
                if (body) {
                    int i = own_index[n];
                    if (i >= 0 && nd < i + 2) continue;
                    const Part* p = w.part_at(n);
                    if (p && nd < p->vac) continue;
                }
                uint8_t first = c == start ? static_cast<uint8_t>(1U << d) : out.mask[c];
                if (out.dist[n] >= 0) {
                    if (out.dist[n] == nd) out.mask[n] |= first;
                    continue;
                }
                out.dist[n] = nd; out.mask[n] = first; out.order.push_back(n);
            }
        }
    }

    Topology topology(const World& w, int start, int depth, int cap) const {
        Topology t;
        if (start < 0 || start >= w.NC || cap <= 0) return t;
        std::vector<int> dist(w.NC, -1), queue{start};
        dist[start] = 0;
        for (size_t qi = 0; qi < queue.size(); qi++) {
            int c = queue[qi];
            std::vector<int> adjacent;
            for (int d = 0; d < 4; d++) {
                int n = w.step_opt(c, d);
                if (n >= 0 && n != c &&
                    std::find(adjacent.begin(), adjacent.end(), n) == adjacent.end())
                    adjacent.push_back(n);
            }
            int degree = static_cast<int>(adjacent.size());
            if (c == start) t.degree = degree;
            t.max_degree = std::max(t.max_degree, degree);
            if (degree >= 3) t.branches++;
            if (dist[c] >= depth) continue;
            for (int n : adjacent) {
                if (dist[n] >= 0) continue;
                dist[n] = dist[c] + 1;
                queue.push_back(n);
                // Match Tyr _topology(): return immediately once the cap is
                // reached, including the just-added cell but no later edges.
                if (static_cast<int>(queue.size()) >= cap) {
                    t.area = static_cast<int>(queue.size());
                    return t;
                }
            }
        }
        t.area = static_cast<int>(queue.size());
        return t;
    }

    bool should_escape_spawn(const World& w, int cell) const {
        Topology t = topology(w, cell, 3, 64);
        return t.degree <= 2 && (t.area <= Params::escape_spawn_area ||
                                 t.branches <= Params::escape_spawn_branches);
    }

    double escape_resource_value(const World& w, int cell) const {
        int r = w.pearl_seen[cell];
        if (r >= 0) {
            if (r == w.rnd) return Params::pearl_value;
            if (w.rnd - r <= Params::memory_ttl) return Params::memory_value;
            return 0.0;
        }
        if (w.bed[cell] == 1 && w.spawn_at[cell] >= w.rnd) {
            if (Params::bed_wait > 0.0)
                return Params::bed_value * std::max(0.0, 1.0 - (w.spawn_at[cell] - w.rnd) / Params::bed_wait);
            // A zero wait horizon means a bed is valuable only if due now.
            return w.spawn_at[cell] == w.rnd ? Params::bed_value : 0.0;
        }
        if (!w.seen[cell]) return Params::unseen_value * 0.35;
        return 0.0;
    }

    double escape_local_resource(const World& w, int cell) const {
        double best = escape_resource_value(w, cell);
        for (int d = 0; d < 4; d++) {
            int n = w.step_opt(cell, d);
            if (n >= 0) best = std::max(best, escape_resource_value(w, n));
        }
        return best;
    }

    double escape_waypoint_score(const World& w, int cell, int route_distance) const {
        Topology t = topology(w, cell, 2, 40);
        int od = cell < static_cast<int>(escape_origin_dist.size()) ? escape_origin_dist[cell] : -1;
        int away = std::max(0, (od < 0 ? 0 : od) - Params::escape_min_distance);
        return Params::escape_open_weight * std::min(t.area, 16) +
            Params::escape_branch_weight * std::min(t.branches, 4) +
            Params::escape_exit_weight * std::max(0, t.max_degree - 2) +
            Params::escape_distance_weight * std::min(away, 8) +
            Params::escape_resource_weight * escape_local_resource(w, cell) -
            Params::escape_route_cost * route_distance;
    }

    bool plan_escape(World& w, int normal_target,
                     const std::vector<int16_t>& normal_dist,
                     const std::vector<uint8_t>& normal_mask, int& target) {
        escape_plan_target = -1;
        escape_plan_mask.assign(w.NC, 0);
        escape_plan_dist.assign(w.NC, -1);
        if (!escape_active) { escape_waypoint = -1; return false; }
        int age = std::max(0, w.rnd - escape_start);
        if (age >= Params::escape_max_turns) {
            escape_active = false; escape_waypoint = -1; return false;
        }
        Search from_origin;
        bounded_search(w, escape_origin, Params::escape_origin_depth, Params::escape_origin_nodes,
                       nullptr, from_origin);
        escape_origin_dist = std::move(from_origin.dist);
        int current_dist = escape_origin_dist[w.head] >= 0 ? escape_origin_dist[w.head] : w.tdist(w.head, escape_origin);
        Topology here = topology(w, w.head, 2, 48);
        bool open = here.max_degree >= 3 || here.area >= Params::escape_open_area || here.branches >= 2;
        if (age >= 1 && current_dist >= Params::escape_min_distance && open) {
            escape_active = false; escape_waypoint = -1; return false;
        }
        Search routes;
        bounded_search(w, w.head, Params::escape_target_depth, Params::escape_target_nodes,
                       &w.body, routes);
        if (normal_target >= 0 && normal_target < w.NC &&
            static_cast<int>(normal_dist.size()) == w.NC &&
            static_cast<int>(normal_mask.size()) == w.NC && normal_dist[normal_target] >= 0 &&
            normal_dist[normal_target] <= Params::escape_valuable_distance &&
            w.pearl_seen[normal_target] == w.rnd &&
            escape_resource_value(w, normal_target) >= Params::escape_valuable_threshold &&
            escape_pause_used < Params::escape_resource_pause_budget) {
            // Preserve the intended per-activation budget: allow a newborn to
            // take a few nearby fresh pearls before continuing its escape route.
            ++escape_pause_used;
            escape_plan_target = normal_target;
            escape_plan_dist = normal_dist;
            escape_plan_mask = normal_mask;
            target = normal_target;
            return false;
        }
        std::vector<int> eligible;
        for (int c : routes.order)
            if (c < static_cast<int>(escape_origin_dist.size()) &&
                escape_origin_dist[c] >= Params::escape_min_distance) eligible.push_back(c);
        if (eligible.empty()) {
            int fallback = std::max(2, Params::escape_min_distance / 2);
            for (int c : routes.order)
                if (c < static_cast<int>(escape_origin_dist.size()) && escape_origin_dist[c] >= fallback)
                    eligible.push_back(c);
        }
        if (eligible.empty()) { escape_active = false; escape_waypoint = -1; return false; }
        int best = -1; double best_score = -1e30;
        for (int c : eligible) {
            double score = escape_waypoint_score(w, c, routes.dist[c]);
            if (score > best_score) { best = c; best_score = score; }
        }
        if (escape_waypoint >= 0 && escape_waypoint != w.head && routes.dist[escape_waypoint] >= 0 &&
            std::find(eligible.begin(), eligible.end(), escape_waypoint) != eligible.end()) {
            double old = escape_waypoint_score(w, escape_waypoint, routes.dist[escape_waypoint]);
            if (old >= best_score - Params::escape_waypoint_hysteresis) best = escape_waypoint;
        }
        escape_waypoint = best; escape_plan_target = best; escape_plan_mask = std::move(routes.mask);
        escape_plan_dist.resize(w.NC);
        for (int c = 0; c < w.NC; c++)
            escape_plan_dist[c] = static_cast<int16_t>(routes.dist[c]);
        target = best;
        return true;
    }

    double escape_action_bonus(const World& w, int cell, int first_dir) const {
        if (!escape_active || escape_plan_target < 0) return 0.0;
        int age = std::max(0, w.rnd - escape_start);
        double pressure = std::pow(Params::escape_decay, age);
        uint8_t mask = escape_plan_target < static_cast<int>(escape_plan_mask.size())
            ? escape_plan_mask[escape_plan_target] : 0;
        double score = Params::escape_route_weight * pressure *
            ((mask & (1U << first_dir)) ? 1.0 : -1.0);
        int before = escape_origin_dist.size() > static_cast<size_t>(w.head) && escape_origin_dist[w.head] >= 0
            ? escape_origin_dist[w.head] : w.tdist(w.head, escape_origin);
        int after = escape_origin_dist.size() > static_cast<size_t>(cell) && escape_origin_dist[cell] >= 0
            ? escape_origin_dist[cell] : w.tdist(cell, escape_origin);
        score += Params::escape_push * pressure * std::clamp(after - before, -2, 2);
        if (age >= 2 && after <= 2) score -= Params::escape_origin_cost * pressure;
        bool parent_found = false;
        for (int pi : w.ally_heads) {
            const Part& ally = w.parts[pi];
            if (escape_parent >= 0 && (ally.id & 4095) != escape_parent) continue;
            parent_found = true;
            int d = w.tdist(cell, ally.cell);
            if (d < Params::escape_parent_radius)
                score -= Params::escape_parent_cost * pressure * (Params::escape_parent_radius - d);
            break;
        }
        if (!parent_found && escape_parent < 0 && !w.ally_heads.empty()) {
            int nearest = -1, distance = 1 << 30;
            for (int pi : w.ally_heads) {
                int d = w.tdist(w.head, w.parts[pi].cell);
                if (d < distance) { distance = d; nearest = pi; }
            }
            if (nearest >= 0 && distance <= Params::escape_parent_radius) {
                int d = w.tdist(cell, w.parts[nearest].cell);
                if (d < Params::escape_parent_radius)
                    score -= 0.6 * Params::escape_parent_cost * pressure * (Params::escape_parent_radius - d);
            }
        }
        if (cell >= 0 && cell < static_cast<int>(visits.size()) && visits[cell])
            score -= Params::escape_revisit_weight * pressure * std::min(4, static_cast<int>(visits[cell]));
        return score;
    }

    static uint8_t checksum(uint64_t v) {
        uint64_t h = v * UINT64_C(0x9E3779B97F4A7C15);
        return static_cast<uint8_t>((h >> 56) ^ ((h >> 17) & 0xff));
    }

    static uint64_t pack(const World& w, int type, uint64_t payload) {
        uint64_t tag = w.team == 'A' ? 0xd3 : 0x69;
        uint64_t low = tag | (static_cast<uint64_t>(type) << 8) |
            ((payload & ((UINT64_C(1) << 44) - 1)) << 12);
        return low | (static_cast<uint64_t>(checksum(low)) << 56);
    }

    static bool unpack(const World& w, uint64_t v, int& type, uint64_t& payload) {
        uint64_t low = v & ((UINT64_C(1) << 56) - 1);
        if ((low & 0xff) != (w.team == 'A' ? 0xd3 : 0x69) ||
            static_cast<uint8_t>(v >> 56) != checksum(low)) return false;
        type = static_cast<int>((low >> 8) & 0xf);
        payload = low >> 12;
        return true;
    }

    uint64_t portal_event_packet(const World& w, int pid, int actor, int rnd) const {
        uint64_t payload = static_cast<uint64_t>(pid & 255) |
            (static_cast<uint64_t>(actor & 8191) << 8) |
            (static_cast<uint64_t>(rnd & 511) << 21);
        return pack(w, 8, payload);
    }

    uint64_t portal_trauma_packet(const World& w, int pid, int rnd) const {
        uint64_t payload = static_cast<uint64_t>(pid & 255) |
            (static_cast<uint64_t>(rnd & 511) << 8);
        return pack(w, 10, payload);
    }

    void note_portal_event(int pid, int actor, int rnd) {
        if (pid < 0 || pid >= 256 || actor < 0 || actor >= 8192 || rnd < 0) return;
        portal_last_transit_round[pid] = std::max(portal_last_transit_round[pid], rnd);
        if (portal_trauma_round[pid] < rnd) portal_trauma_round[pid] = -1;
        auto it = std::find_if(portal_events.begin(), portal_events.end(), [&](const PortalEvent& e) {
            return e.pid == pid && e.actor == actor && e.round == rnd;
        });
        if (it == portal_events.end()) portal_events.push_back({pid, actor, rnd, false});
        portal_relay_packet = 0;
        portal_relay_round = -1;
    }

    bool portal_blocked(const World& w, int pid) const {
        return pid >= 0 && pid < static_cast<int>(portal_trauma_round.size()) &&
            portal_trauma_round[pid] >= 0 && w.rnd - portal_trauma_round[pid] <= 30 &&
            portal_last_transit_round[pid] <= portal_trauma_round[pid];
    }

    void hear_portal_radio(World& w) {
        if (w.me >= 0 && w.me < static_cast<int>(portal_alive_round.size()))
            portal_alive_round[w.me] = std::max(portal_alive_round[w.me], w.rnd);

        for (uint64_t msg : w.msgs) {
            int type = 0;
            uint64_t p = 0;
            if (!unpack(w, msg, type, p)) continue;
            if (type == 1) {
                int rnd = (p >> 22) & 511, id = (p >> 31) & 4095;
                if (id < static_cast<int>(portal_alive_round.size()) && rnd <= w.rnd)
                    portal_alive_round[id] = std::max(portal_alive_round[id], rnd);
            } else if (type == 6) {
                int rnd = (p >> 12) & 511, id = (p >> 31) & 8191;
                if (id < static_cast<int>(portal_alive_round.size()) && rnd <= w.rnd)
                    portal_alive_round[id] = std::max(portal_alive_round[id], rnd);
            } else if (type == 8) {
                int pid = p & 255, actor = (p >> 8) & 8191, rnd = (p >> 21) & 511;
                if (rnd <= w.rnd && w.rnd - rnd <= 30) {
                    portal_alive_round[actor] = std::max(portal_alive_round[actor], rnd);
                    note_portal_event(pid, actor, rnd);
                    portal_relay_packet = msg;
                    portal_relay_round = rnd;
                }
            } else if (type == 10) {
                int pid = p & 255, rnd = (p >> 8) & 511;
                if (pid < static_cast<int>(portal_trauma_round.size()) && rnd <= w.rnd &&
                    w.rnd - rnd <= 30 && rnd >= portal_last_transit_round[pid]) {
                    portal_last_transit_round[pid] = rnd;
                    portal_trauma_round[pid] = std::max(portal_trauma_round[pid], rnd);
                }
            }
        }

        for (PortalEvent& e : portal_events) {
            if (e.actor >= 0 && e.actor < static_cast<int>(portal_alive_round.size()) &&
                portal_alive_round[e.actor] >= e.round + 3)
                e.resolved = true;
            if (!e.resolved && w.rnd >= e.round + 4 && w.rnd - e.round <= 30 &&
                portal_last_transit_round[e.pid] == e.round) {
                portal_trauma_round[e.pid] = std::max(portal_trauma_round[e.pid], e.round);
                e.resolved = true;
            }
        }
        portal_events.erase(std::remove_if(portal_events.begin(), portal_events.end(), [&](const PortalEvent& e) {
            return e.resolved || w.rnd - e.round > 30;
        }), portal_events.end());
        if (portal_relay_round >= 0 && w.rnd - portal_relay_round > 3) {
            portal_relay_packet = 0;
            portal_relay_round = -1;
        }
        for (int pid = 0; pid < static_cast<int>(portal_trauma_round.size()); ++pid) {
            if (portal_trauma_round[pid] >= 0 && w.rnd - portal_trauma_round[pid] > 30)
                portal_trauma_round[pid] = -1;
        }
    }

    uint64_t crown_packet(const World& w, int type, int id, int cell, int len, int rnd) const {
        uint64_t payload = static_cast<uint64_t>(cell % w.W) |
            (static_cast<uint64_t>(cell / w.W) << 7) |
            (static_cast<uint64_t>(std::min(len, 255)) << 14) |
            (static_cast<uint64_t>(rnd & 511) << 22) |
            (static_cast<uint64_t>(id & 4095) << 31);
        return pack(w, type, payload);
    }

    uint64_t density_packet(const World& w, int id, double x, double y,
                            double allies, double enemies, int rnd) const {
        if (w.W > 64 || w.H > 64 || id < 0 || id >= 8192 || rnd < 0 || rnd >= 500) return 0;
        int xx = (static_cast<int>(x + 0.5) % w.W + w.W) % w.W;
        int yy = (static_cast<int>(y + 0.5) % w.H + w.H) % w.H;
        int aa = std::clamp(static_cast<int>(allies + 0.5), 1, 31);
        int ee = std::clamp(static_cast<int>(enemies + 0.5), 0, 31);
        uint64_t payload = static_cast<uint64_t>(xx) | (static_cast<uint64_t>(yy) << 6) |
            (static_cast<uint64_t>(rnd) << 12) | (static_cast<uint64_t>(aa) << 21) |
            (static_cast<uint64_t>(ee) << 26) | (static_cast<uint64_t>(id) << 31);
        return pack(w, 6, payload);
    }

    double wrapped_delta(double a, double b, int size) const {
        double wrapped = std::fmod(b - a + size * 0.5, static_cast<double>(size));
        if (wrapped < 0.0) wrapped += size;
        return wrapped - size * 0.5;
    }

    static double python_mod(double value, int size) {
        double wrapped = std::fmod(value, static_cast<double>(size));
        if (wrapped < 0.0) wrapped += size;
        return wrapped;
    }

    void hear_radio(World& w) {
        // world.sense() calls see_prey() before radio.hear(); preserve that
        // update order when a visible head and a sonar report compete.
        for (int pi : w.enemy_heads) {
            const Part& e = w.parts[pi];
            int len = enemy_length(w, e.id, true);
            if (len >= Params::prey_min &&
                (prey_id < 0 || w.rnd - prey_round > Params::prey_ttl ||
                 ((e.id & 4095) == prey_id && w.rnd >= prey_round) || len > prey_len)) {
                prey_id = e.id & 4095; prey_cell = e.cell; prey_len = len; prey_round = w.rnd;
            }
        }
        for (uint64_t msg : w.msgs) {
            int type = 0;
            uint64_t p = 0;
            if (!unpack(w, msg, type, p)) continue;
            if (type == 2) {
                constexpr uint64_t empty = 63 | (63ULL << 6) | (511ULL << 12);
                for (int k = 0; k < 2; k++) {
                    uint64_t e = (p >> (21 * k)) & ((1ULL << 21) - 1);
                    if (e == empty) continue;
                    int x = e & 63, y = (e >> 6) & 63, r = (e >> 12) & 511;
                    if (x >= w.W || y >= w.H) continue;
                    int c = y * w.W + x;
                    // Mirror Tyr radio.hear() literally: its seen=0 sentinel
                    // also satisfies this comparison in early rounds, so food
                    // gossip on never-seen cells is ignored for the first turns.
                    if (w.seen[c] - 1 >= w.rnd - Params::gossip_trust) continue;
                    if (r <= w.rnd) {
                        if (w.rnd - r <= Params::memory_ttl && w.pearl_seen[c] < r) {
                            if (w.pearl_seen[c] < 0) w.pearl_order.push_back(c);
                            w.pearl_seen[c] = r;
                        }
                    } else {
                        w.bed[c] = 1;
                        w.spawn_at[c] = r;
                    }
                }
            } else if (type == 1 || type == 4) {
                int x = p & 127, y = (p >> 7) & 127;
                int len = (p >> 14) & 255, rnd = (p >> 22) & 511;
                int id = (p >> 31) & 4095;
                if (x >= w.W || y >= w.H || len < 2 || rnd > w.rnd) continue;
                int cell = y * w.W + x;
                if (type == 1 && w.rnd - rnd <= Params::crown_ttl) {
                    bool replace = crown_id < 0 || w.rnd - crown_round > Params::crown_ttl;
                    if (!replace && id == crown_id) {
                        // Tyr roles.hear(): same-crown refreshes are ordered by
                        // timestamp only; an older, longer beacon cannot rewind it.
                        replace = rnd >= crown_round;
                    } else if (!replace) {
                        replace = len >= crown_len + 3 || (len == crown_len && id < crown_id);
                    }
                    if (replace) {
                        crown_id = id; crown_cell = cell; crown_len = len; crown_round = rnd;
                    }
                } else if (type == 4 && w.rnd - rnd <= Params::prey_ttl && len >= Params::prey_min &&
                           (prey_id < 0 || w.rnd - prey_round > Params::prey_ttl || len > prey_len ||
                            (id == prey_id && rnd >= prey_round))) {
                    prey_id = id; prey_cell = cell; prey_len = len; prey_round = rnd;
                }
            } else if (type == 3) {
                int rnd = (p >> 8) & 511;
                if (w.rnd - rnd >= 0 && w.rnd - rnd <= 1) inherit_pending = true;
            } else if (type == 5) {
                int k1 = p & 8191, k2 = (p >> 13) & 8191, pid = (p >> 26) & 255;
                if (2 * w.NC <= 8192) w.learn_pair(k1, k2, pid);
            } else if (type == 7) {
                int parent = p & 4095, x = (p >> 12) & 127, y = (p >> 19) & 127;
                int rnd = (p >> 26) & 511;
                bool escape = ((p >> 35) & 1) != 0;
                bool inherit = ((p >> 36) & 1) != 0;
                int age = w.rnd - rnd;
                if ((escape || inherit) && parent != (w.me & 4095) &&
                    (w.born == rnd || w.born == rnd + 1) && age >= 0 &&
                    age <= Params::escape_handoff_retries && x < w.W && y < w.H &&
                    w.tdist(w.head, y * w.W + x) <= std::max(1, age)) {
                    birth_packet_seen = true;
                    if (inherit) {
                        inherit_pending = true;
                        escape_active = false;
                        escape_waypoint = -1;
                    } else if (!(escape_packet_seen && escape_parent == parent &&
                                 escape_origin == y * w.W + x && escape_start == rnd)) {
                        escape_packet_seen = true;
                        escape_active = true; escape_parent = parent; escape_origin = y * w.W + x;
                        escape_start = rnd; escape_waypoint = -1; escape_pause_used = 0;
                    }
                }
            } else if (type == 6) {
                int x = p & 63, y = (p >> 6) & 63, rnd = (p >> 12) & 511;
                int allies = (p >> 21) & 31, enemies = (p >> 26) & 31;
                int id = (p >> 31) & 8191;
                if (x >= w.W || y >= w.H || allies < 1 || rnd > w.rnd || w.rnd - rnd > Params::density_ttl || id == w.me)
                    continue;
                auto it = density_reports.find(id);
                if (it != density_reports.end() && rnd <= it->second.rnd) continue;
                if (it == density_reports.end()) density_order.push_back(id);
                density_reports[id] = {static_cast<double>(x), static_cast<double>(y),
                                       static_cast<double>(allies), static_cast<double>(enemies), rnd, msg};
                // density.hear() enforces the source cap after every accepted
                // report, before the next sonar ray is decoded.
                if (density_reports.size() > static_cast<size_t>(Params::density_sources)) {
                    auto oldest = std::min_element(density_reports.begin(), density_reports.end(),
                        [](const auto& a, const auto& b) {
                            return a.second.rnd == b.second.rnd ? a.first < b.first
                                                               : a.second.rnd < b.second.rnd;
                        });
                    int evicted = oldest->first;
                    density_reports.erase(oldest);
                    density_order.erase(std::remove(density_order.begin(), density_order.end(), evicted),
                                         density_order.end());
                }
            }
        }

        // Tyr separation.observe_birth(): infer a constrained newborn when a
        // split handoff packet was lost. Initial round-zero dragons are exempt.
        bool initial_dragon = (w.me & 4095) < Params::opening_initial_id_limit;
        if (!escape_active && !birth_packet_seen && w.born == w.rnd &&
            !(w.rnd == 0 && initial_dragon) && should_escape_spawn(w, w.head)) {
            escape_active = true; escape_origin = w.head; escape_start = w.rnd;
            escape_waypoint = -1; escape_pause_used = 0; escape_parent = -1;
            std::pair<int, int> nearest{std::numeric_limits<int>::max(), std::numeric_limits<int>::max()};
            for (int pi : w.ally_heads) {
                const Part& ally = w.parts[pi];
                std::pair<int, int> candidate{w.tdist(ally.cell, w.head), ally.id & 4095};
                if (candidate.first <= Params::escape_parent_radius && candidate < nearest) {
                    nearest = candidate; escape_parent = candidate.second;
                }
            }
        }

        // Visible heads refresh the elected crown's location and can replace a
        // beacon that has plainly disappeared from its expected vision.
        if (crown_id >= 0 && crown_id != (w.me & 4095)) {
            bool visible = false;
            for (int pi : w.ally_heads) {
                const Part& a = w.parts[pi];
                if ((a.id & 4095) == crown_id) {
                    crown_cell = a.cell; crown_round = w.rnd; visible = true; break;
                }
            }
            if (!visible && crown_cell >= 0 &&
                w.cheb(crown_cell, w.head) + (w.rnd - crown_round) <= 2) {
                crown_id = -1; crown_cell = -1; crown_len = 0; crown_round = -1;
            }
        }
        if (w.rnd >= 250 && crown_id >= 0 && w.rnd - crown_round <= Params::crown_ttl)
            last_crown_round = w.rnd;
        // Tyr retains an expired crown record so a later visible head can
        // refresh it; freshness gates its use, not whether its identity exists.
        if (w.dest_dirty) w.rebuild_dest();

        int me = w.me & 4095;
        bool inherited_now = w.rnd >= 250 && inherit_pending;
        bool claimed_now = false;
        if (inherited_now) {
            crown_id = me; crown_cell = w.head; crown_len = w.len; crown_round = w.rnd;
            inherit_pending = false;
        } else if (w.rnd >= 250) {
            bool claim = false;
            if (crown_id < 0 || w.rnd - crown_round > Params::crown_ttl) {
                int claim_round = std::max(250, last_crown_round) + (w.me * 7919) % Params::crown_claim_spread;
                claim = w.rnd >= claim_round && w.len >= Params::crown_claim_len;
            } else if (crown_id == me) {
                claim = true;
            } else if (w.len >= crown_len + Params::crown_margin || (w.len == crown_len && me < crown_id)) {
                claim = true;
            }
            if (claim) {
                crown_id = me; crown_cell = w.head; crown_len = w.len; crown_round = w.rnd;
                claimed_now = true;
            }
        }
        role_crown = inherited_now || claimed_now;
        role_feeder = false;
        int feed_from = 500 - Params::feed_base - static_cast<int>((w.W + w.H) * Params::feed_k);
        if (!role_crown && crown_id >= 0 && w.rnd - crown_round <= Params::crown_ttl && w.rnd >= feed_from &&
            crown_len >= Params::feed_min_crown && crown_len > w.len && w.tdist(w.head, crown_cell) <= Params::feed_range)
            role_feeder = true;

        int visible_allies = 1, visible_enemies = 0;
        std::unordered_set<int> ally_ids, enemy_ids;
        for (const Part& part : w.parts)
            (part.ally ? ally_ids : enemy_ids).insert(part.id);
        visible_allies += static_cast<int>(ally_ids.size());
        visible_enemies = static_cast<int>(enemy_ids.size());
        double x = static_cast<double>(w.head % w.W), y = static_cast<double>(w.head / w.W);
        if (!have_local_density || local_head < 0 || w.tdist(local_head, w.head) > 3) {
            local_x = x; local_y = y; local_allies = visible_allies; local_enemies = visible_enemies;
        } else {
            double retain = std::pow(0.5, std::max(0, w.rnd - local_density_round) / 4.0);
            double gain = 1.0 - retain;
            local_x = python_mod(local_x + gain * wrapped_delta(local_x, x, w.W), w.W);
            local_y = python_mod(local_y + gain * wrapped_delta(local_y, y, w.H), w.H);
            local_allies = retain * local_allies + gain * visible_allies;
            local_enemies = retain * local_enemies + gain * visible_enemies;
        }
        have_local_density = true; local_density_round = w.rnd; local_head = w.head;
        for (auto it = density_reports.begin(); it != density_reports.end();) {
            if (w.rnd - it->second.rnd > Params::density_ttl) {
                int id = it->first;
                it = density_reports.erase(it);
                density_order.erase(std::remove(density_order.begin(), density_order.end(), id), density_order.end());
            } else ++it;
        }
    }

    double radio_density_factor(const World& w, int cell) const {
        if (w.seen[cell] == w.rnd + 1) return 1.0;
        double x = cell % w.W, y = cell / w.W;
        double total = 0.0, allies = 0.0, enemies = 0.0;
        auto add = [&](double px, double py, double aa, double ee, int rnd) {
            int age = w.rnd - rnd;
            if (age < 0 || age > Params::density_ttl) return;
            double dx = std::abs(x - px), dy = std::abs(y - py);
            dx = std::min(dx, w.W - dx); dy = std::min(dy, w.H - dy);
            if (dx >= Params::density_radius || dy >= Params::density_radius) return;
            double spatial = (1.0 - dx / Params::density_radius) * (1.0 - dy / Params::density_radius);
            double weight = spatial * std::pow(0.5, age / static_cast<double>(Params::density_half_life));
            total += spatial; allies += weight * aa; enemies += weight * ee;
        };
        for (int id : density_order) {
            const auto& row = density_reports.at(id);
            add(row.x, row.y, row.allies, row.enemies, row.rnd);
        }
        if (have_local_density) add(local_x, local_y, local_allies, local_enemies, local_density_round);
        double denom = std::max(1.0, total);
        return 1.0 / (1.0 + Params::density_ally_weight * std::max(0.0, allies / denom - 1.0) + Params::density_enemy_weight * enemies / denom);
    }

    void prepare_radio(const World& w, const Decision* decision = nullptr) {
        sonar_out.fill(0);
        sonar_order.clear();
        auto set_sonar = [&](int d, uint64_t packet) {
            if (!sonar_out[d]) sonar_order.push_back(d);
            sonar_out[d] = packet;
        };
        std::vector<int> dirs{0, 1, 2, 3};
        if (w.rnd >= 250 && crown_id >= 0 && w.rnd - crown_round <= Params::crown_ttl) {
            uint64_t packet = crown_packet(w, 1, crown_id, crown_cell, crown_len, crown_round);
            std::array<int, 2> pair = (w.rnd % 2 == 0) ? std::array<int, 2>{0, 2} : std::array<int, 2>{1, 3};
            for (int d : pair) { set_sonar(d, packet); dirs.erase(std::remove(dirs.begin(), dirs.end(), d), dirs.end()); }
        }
        if (prey_id >= 0 && w.rnd - prey_round <= Params::prey_ttl && !dirs.empty()) {
            int d = (w.rnd % 2 == 0) ? dirs.back() : dirs.front();
            set_sonar(d, crown_packet(w, 4, prey_id, prey_cell, prey_len, prey_round));
            dirs.erase(std::remove(dirs.begin(), dirs.end(), d), dirs.end());
        }
        if (w.rnd % 2 == 0 && !dirs.empty() && 2 * w.NC <= 8192) {
            std::vector<int> pairs;
            for (int pid : w.portal_order) {
                const auto& ends = w.pends.at(pid);
                if (ends[0] >= 0 && ends[1] >= 0) pairs.push_back(pid);
            }
            if (!pairs.empty()) {
                int index = (w.rnd / 2 + w.me) % static_cast<int>(pairs.size());
                int pid = pairs[index];
                auto ends = w.pends.at(pid);
                uint64_t payload = static_cast<uint64_t>(ends[0] & 8191) |
                    (static_cast<uint64_t>(ends[1] & 8191) << 13) |
                    (static_cast<uint64_t>(pid & 255) << 26);
                int d = dirs.back();
                set_sonar(d, pack(w, 5, payload));
                dirs.pop_back();
            }
        }
        if (w.W <= 64 && w.H <= 64) {
            std::vector<std::pair<int, int>> entries, beds;
            for (int c : w.visible_cells) {
                if (w.pearl_seen[c] == w.rnd) entries.push_back({c, w.rnd});
                else if (w.bed[c] == 1 && w.spawn_at[c] > w.rnd &&
                         w.spawn_at[c] <= w.rnd + Params::gossip_horizon)
                    beds.push_back({c, w.spawn_at[c]});
            }
            std::sort(beds.begin(), beds.end(), [](auto a, auto b) {
                return a.second == b.second ? a.first < b.first : a.second < b.second;
            });
            entries.insert(entries.end(), beds.begin(), beds.end());
            if (!entries.empty() && !dirs.empty()) {
                int count = static_cast<int>(entries.size()), off = (w.rnd * 2) % count, k = 0;
                for (int d : dirs) {
                    if (k >= count) break;
                    uint64_t payload = 0;
                    constexpr uint64_t empty = 63 | (63ULL << 6) | (511ULL << 12);
                    for (int j = 0; j < 2; j++) {
                        uint64_t e = empty;
                        if (k < count) {
                            int c = entries[(off + k++) % count].first;
                            int r = entries[(off + k - 1) % count].second;
                            e = static_cast<uint64_t>(c % w.W) |
                                (static_cast<uint64_t>(c / w.W) << 6) |
                                (static_cast<uint64_t>(r & 511) << 12);
                        }
                        payload |= e << (21 * j);
                    }
                    set_sonar(d, pack(w, 2, payload));
                }
            }
        }
        uint64_t density = have_local_density
            ? density_packet(w, w.me, local_x, local_y, local_allies, local_enemies, local_density_round) : 0;
        if (density) {
            std::vector<int> order{(w.rnd + w.me) % 4, (w.rnd + w.me + 1) % 4,
                                   (w.rnd + w.me + 2) % 4, (w.rnd + w.me + 3) % 4};
            std::vector<int> selected;
            for (int d : order) if (!sonar_out[d]) selected.push_back(d);
            for (int d : order) {
                if (selected.size() >= 2) break;
                int type = static_cast<int>((sonar_out[d] >> 8) & 15);
                if (type != 1 && type != 4 && std::find(selected.begin(), selected.end(), d) == selected.end())
                    selected.push_back(d);
            }
            for (size_t k = 0; k < selected.size(); k++) {
                if (k == 1 && !density_reports.empty() && w.rnd % 2) {
                    std::vector<int> ids;
                    for (const auto& row : density_reports) ids.push_back(row.first);
                    std::sort(ids.begin(), ids.end());
                    int id = ids[(w.rnd / 2 + w.me) % static_cast<int>(ids.size())];
                    set_sonar(selected[k], density_reports.at(id).packet);
                } else set_sonar(selected[k], density);
            }
        }
        if (decision && decision->act == Act::SPLIT && !w.body.empty()) {
            bool inherit = role_crown && decision->split > w.len - decision->split;
            bool escape = !inherit && !role_crown && !role_feeder &&
                static_cast<int>(w.body.size()) >= w.len && should_escape_spawn(w, w.body.front());
            if (inherit || escape) {
                int cell = w.body.front();
                uint64_t payload = static_cast<uint64_t>(w.me & 4095) |
                    (static_cast<uint64_t>(cell % w.W) << 12) |
                    (static_cast<uint64_t>(cell / w.W) << 19) |
                    (static_cast<uint64_t>(w.rnd & 511) << 26) |
                    (static_cast<uint64_t>(escape) << 35) | (static_cast<uint64_t>(inherit) << 36);
                pending_handoff = pack(w, 7, payload);
                pending_handoff_round = w.rnd;
                set_sonar((w.face + 2) & 3, pending_handoff);
            }
        } else if (pending_handoff && pending_handoff_round >= 0) {
            int age = w.rnd - pending_handoff_round;
            if (age > 0 && age <= Params::escape_handoff_retries)
                set_sonar((w.face + 2) & 3, pending_handoff);
            else if (age > Params::escape_handoff_retries) {
                pending_handoff = 0; pending_handoff_round = -1;
            }
        }

        // Report every known portal pair crossed by this move. Sonar only
        // exists after a surviving action, so a move that kills its dragon
        // cannot announce its own transit (the replay metric accounts for it).
        std::vector<uint64_t> own_portal_packets;
        if (decision && decision->act == Act::MOVE && !decision->dirs.empty()) {
            int cell = w.head;
            for (int dir : decision->dirs) {
                if (w.is_portal_edge(cell, dir)) {
                    int pid = w.epid[w.ekey(cell, dir)];
                    if (pid >= 0 && pid < 256) {
                        bool duplicate = std::any_of(own_portal_packets.begin(), own_portal_packets.end(),
                            [&](uint64_t packet) {
                                int type = 0; uint64_t payload = 0;
                                return unpack(w, packet, type, payload) && (payload & 255) == pid;
                            });
                        if (!duplicate) {
                            note_portal_event(pid, w.me, w.rnd);
                            uint64_t packet = portal_event_packet(w, pid, w.me, w.rnd);
                            own_portal_packets.push_back(packet);
                            portal_relay_packet = packet;
                            portal_relay_round = w.rnd;
                        }
                    }
                }
                int next = w.dest(cell, dir);
                if (next < 0) break;
                cell = next;
            }
        }

        // H-S1 traffic takes one available ray, preferring a free direction
        // and otherwise replacing food/topology/density gossip. Crown, prey,
        // and split handoff messages keep their existing slots.
        std::array<bool, 4> portal_slots{};
        auto set_portal_packet = [&](uint64_t packet) {
            std::array<int, 4> order{(w.rnd + w.me) & 3, (w.rnd + w.me + 1) & 3,
                                     (w.rnd + w.me + 2) & 3, (w.rnd + w.me + 3) & 3};
            int chosen = -1;
            for (int d : order) if (!sonar_out[d] && !portal_slots[d]) { chosen = d; break; }
            if (chosen < 0) for (int d : order) {
                if (portal_slots[d]) continue;
                int type = static_cast<int>((sonar_out[d] >> 8) & 15);
                if (type != 1 && type != 4 && type != 7) { chosen = d; break; }
            }
            if (chosen >= 0) {
                set_sonar(chosen, packet);
                portal_slots[chosen] = true;
            }
        };
        for (uint64_t packet : own_portal_packets) set_portal_packet(packet);
        if (own_portal_packets.empty() && portal_relay_packet && portal_relay_round >= 0 &&
            w.rnd - portal_relay_round <= 3)
            set_portal_packet(portal_relay_packet);

        int trauma_pid = -1, trauma_round = -1;
        for (int pid = 0; pid < static_cast<int>(portal_trauma_round.size()); ++pid) {
            if (portal_trauma_round[pid] >= 0 && w.rnd - portal_trauma_round[pid] <= 30 &&
                portal_trauma_round[pid] > trauma_round) {
                trauma_pid = pid; trauma_round = portal_trauma_round[pid];
            }
        }
        if (trauma_pid >= 0) set_portal_packet(portal_trauma_packet(w, trauma_pid, trauma_round));
    }

    void prepare_radio_for_decision(const World& w, const Decision& d) { prepare_radio(w, &d); }

    void send_radio(unswbc::Controller& ct) const {
        auto directions = unswbc::Direction::get_direction_list();
        for (int d : sonar_order) if (sonar_out[d]) ct.send_sonar(directions[d], sonar_out[d]);
    }

    double lv_now(const World& w) const {
        if (role_crown) return 4.0;
        if (w.rnd < Params::grow_from) return 1.0;
        double f = std::clamp((w.rnd - Params::grow_from) / 120.0, 0.0, 1.0);
        return 1.0 + (Params::lv_end - 1.0) * f;
    }

    // Segments a move of `steps` steps costs this dragon (carthage-04).
    int sprint_paid(const World& w, int steps) const {
        return Params::sprint_rules_123 ? std::max(0, steps - (w.len + 3) / 4) : steps - 1;
    }

    double dragon_value(const World& w, int length) const {
        return Params::material_unit_value + lv_now(w) * length;
    }

    bool local_crown(const World& w) const {
        return role_crown && crown_id == (w.me & 4095);
    }

    double local_density_factor(const World& w, int c) const {
        return radio_density_factor(w, c);
    }

    double cell_value(const World& w, int c, int steps) const {
        double v = 0.0;
        int pr = w.pearl_seen[c];
        if (pr >= 0) {
            if (pr == w.rnd) v = Params::pearl_value;
            else if (w.rnd - pr <= Params::memory_ttl) v = Params::memory_value;
        } else if (w.bed[c] == 1 && w.spawn_at[c] >= 0) {
            int spawn = w.spawn_at[c];
            int arrival = w.rnd + steps;
            if (spawn > arrival) {
                if (Params::bed_wait > 0.0)
                    v = Params::bed_value * std::max(0.0, 1.0 - (spawn - arrival) / Params::bed_wait);
            } else if (spawn > w.rnd) {
                v = Params::bed_value;
            } else {
                int age = w.rnd - spawn;
                v = age <= Params::bed_stale
                    ? Params::bed_value * (1.0 - 0.5 * age / Params::bed_stale)
                    : Params::bed_value * 0.3;
            }
        } else if (!w.seen[c]) {
            v = Params::unseen_value;
        }
        if (v <= 0.0) return 0.0;
        if (local_crown(w)) return v;
        if (crown_id >= 0 && w.rnd >= 250 && w.rnd - crown_round <= Params::crown_ttl) {
            int feed_from = 500 - Params::feed_base - static_cast<int>((w.W + w.H) * Params::feed_k);
            int radius = w.rnd >= feed_from ? 5 : 3;
            if (w.tdist(c, crown_cell) <= radius) return 0.0;
        }
        for (int pi : w.ally_heads) {
            const Part& p = w.parts[pi];
            int distance = w.tdist(p.cell, c);
            if (distance < steps || (distance == steps && (p.id & 4095) < (w.me & 4095))) {
                v *= Params::own_target_discount;
                break;
            }
        }
        for (int pi : w.enemy_heads)
            if (w.tdist(w.parts[pi].cell, c) < steps) {
                v *= Params::enemy_target_discount;
                break;
            }
        return v * local_density_factor(w, c);
    }

    double blind_risk(const World& w, int cell) const {
        int cutoff = w.rnd - Params::blind_fresh;
        if (cell >= 0 && w.body_seen[cell] >= cutoff) return Params::blind_body;
        for (int d = 0; d < 4; d++) {
            int n = w.nbr(cell, d);
            if (w.body_seen[n] >= cutoff) return Params::blind_body;
        }
        if (w.seen[cell] && w.rnd - (w.seen[cell] - 1) <= Params::blind_fresh)
            return Params::blind_seen;
        return Params::blind_unseen;
    }

    int enemy_length(const World& w, int id, bool prey = false) const {
        auto it = w.mem.find(id);
        if (it == w.mem.end()) return 1;
        return std::max(1, it->second.vis_len +
            (it->second.cut ? (prey ? Params::prey_cut_extra : Params::cut_extra) : 0));
    }

    int visible_length(const World& w, int id) const {
        auto it = w.mem.find(id);
        return it == w.mem.end() ? 1 : std::max(1, it->second.vis_len);
    }

    int sector_target(const World& w) const {
        int best = -1, best_distance = std::numeric_limits<int>::max();
        int n = w.sectors_w * w.sectors_h;
        int offset = n ? (w.me * 7) % n : 0;
        for (int k = 0; k < n; k++) {
            int sector = (k + offset) % n;
            if (w.sector_unseen[sector] <= 0) continue;
            int x = std::min(w.W - 1, (sector % w.sectors_w) * World::sector_size + World::sector_size / 2);
            int y = std::min(w.H - 1, (sector / w.sectors_w) * World::sector_size + World::sector_size / 2);
            int distance = w.tdist(w.head, y * w.W + x);
            if (distance < best_distance) { best_distance = distance; best = y * w.W + x; }
        }
        return best;
    }

    int far_target(const World& w) const {
        int best = -1;
        double best_value = 0.0;
        for (int c : w.pearl_order) {
            int seen_round = w.pearl_seen[c];
            if (seen_round < 0 || w.rnd - seen_round > Params::memory_ttl || c == w.head) continue;
            double value = Params::memory_value * std::pow(Params::target_gamma, w.tdist(c, w.head));
            if (value > best_value) { best_value = value; best = c; }
        }
        return best >= 0 ? best : sector_target(w);
    }

    int flood_need(const World& w, int length) const {
        int need = std::max(length + Params::slack, Params::min_area);
        if (length >= 10) {
            int cap = Params::flood_cap_long;
            if (w.rnd >= Params::flood_cap_late_from) cap = std::min(cap, Params::flood_cap_long_late);
            if (w.rnd >= Params::flood_cap_late_from && w.units <= Params::search_cap_sparse_units)
                cap = std::max(cap, Params::flood_cap_long_sparse);
            need = std::min(need + length / 3, cap);
        } else {
            need = std::min(need, Params::flood_cap);
        }
        return need;
    }

    double devil_center_bonus(const World& w, int c) const {
        if (!Params::shape_terms) return 0.0;
        if (w.W != 32 || w.H != 16 || w.rnd >= Params::devil_center_until || role_crown || role_feeder) return 0.0;
        int x0 = w.W / 2 - 1, x1 = w.W / 2;
        int before = std::min(std::abs(w.head % w.W - x0), std::abs(w.head % w.W - x1));
        int after = std::min(std::abs(c % w.W - x0), std::abs(c % w.W - x1));
        return before > 2 && after < before ? Params::devil_center_weight : 0.0;
    }

    double devil_lane_bonus(const World& w, int c) const {
        if (!Params::shape_terms) return 0.0;
        if (w.W != 32 || w.H != 16 || w.rnd >= Params::devil_lane_until || role_crown || role_feeder) return 0.0;
        int lane = ((w.me % 6) * w.H / 6 + w.H / 12) % w.H;
        auto dy = [&](int y) { int d = std::abs(y - lane); return std::min(d, w.H - d); };
        return dy(c / w.W) < dy(w.head / w.W) ? Params::devil_lane_weight : 0.0;
    }

    double ally_body_buffer(const World& w, int c) const {
        if (!Params::shape_terms) return 0.0;
        if (w.W != 32 || w.H != 16) return 0.0;
        int clearance = 99;
        for (const Part& p : w.parts) {
            if (!p.ally) continue;
            clearance = std::min(clearance, w.tdist(c, p.cell));
        }
        if (clearance <= 1) return Params::devil_ally_body_weight;
        if (clearance == 2) return 0.5 * Params::devil_ally_body_weight;
        return 0.0;
    }

    void mark_danger(const World& w) {
        if (static_cast<int>(danger.size()) != w.NC) danger.assign(w.NC, 0);
        if (static_cast<int>(threats.size()) != w.NC) threats.resize(w.NC);
        for (int c : danger_cells) { danger[c] = 0; threats[c].clear(); }
        danger_cells.clear();
        threat_support.clear();
        for (int pi : w.enemy_heads) {
            const Part& head = w.parts[pi];
            if (w.cheb(head.cell, w.head) > 7) continue;
            int enemy_len = enemy_length(w, head.id);
            int supporters = 0;
            for (int ai : w.ally_heads) {
                const Part& ally = w.parts[ai];
                if (visible_length(w, ally.id) >= enemy_len &&
                    w.tdist(ally.cell, head.cell) <= Params::threat_support_radius)
                    ++supporters;
            }
            if (supporters) threat_support[head.id] = supporters;
            int reach = std::clamp(enemy_len - 1, 1, 3);
            std::vector<int> steps(w.NC, -1), frontier{head.cell}, next;
            steps[head.cell] = 0;
            for (int depth = 0; depth < reach; depth++) {
                next.clear();
                for (int c : frontier) {
                    for (int d = 0; d < 4; d++) {
                        int n = w.dest(c, d);
                        if (n < 0 || steps[n] >= 0 || w.occ[n] >= 0) continue;
                        steps[n] = depth + 1;
                        if (threats[n].empty()) danger_cells.push_back(n);
                        danger[n] = 1;
                        threats[n].push_back({depth + 1, head.id, enemy_len});
                        next.push_back(n);
                    }
                }
                frontier.swap(next);
            }
        }
    }

    struct Room {
        int cells = 0;
        int pearls = 0;
    };

    // Time-aware flood from `start`. segs = our body after the action, tail
    // first, start excluded; segment i is free from depth i + 2 + delay.
    // Other dragons' parts free at vac + delay. Stops at need cells.
    Room flood_room(const World& w, int start, const std::vector<int>& segs, int delay, int need) {
        room_mask.assign(w.NC, 0);
        for (auto const& p : w.parts) room_mask[p.cell] = static_cast<uint16_t>(p.vac + delay);
        for (size_t i = 0; i < segs.size(); i++)
            room_mask[segs[i]] = static_cast<uint16_t>(i + 2 + delay);
        // Any other head may take a neighbouring cell before our next step.
        if (Params::head_block > 0) {
            for (auto const& p : w.parts) {
                if (!p.head) continue;
                for (int d = 0; d < 4; d++) {
                    int n = w.dest(p.cell, d);
                    if (n >= 0 && room_mask[n] < Params::head_block + 1 + delay)
                        room_mask[n] = static_cast<uint16_t>(Params::head_block + 1 + delay);
                }
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
        int pearl_count = 0;
        for (size_t qi = 0; qi < room.order.size(); qi++) {
            int c = room.order[qi];
            int t = room.d[c] + 1;
            int cc = 0;
            for (int dd = 0; dd < 4; dd++) {
                int n = w.dest(c, dd);
                if (n == UNKNOWN) {
                    if (cc < Params::flood_credit) cc = Params::flood_credit;
                    continue;
                }
                if (n == UNPAIRED) {
                    if (cc < Params::flood_portal_credit) cc = Params::flood_portal_credit;
                    continue;
                }
                if (n < 0 || room.d[n] >= 0 || room_mask[n] > t) continue;
                room.d[n] = static_cast<int16_t>(t);
                room.order.push_back(n);
                if (w.pearl_seen[n] == w.rnd) pearl_count++;
            }
            credit += cc;
            if (static_cast<int>(room.order.size()) - 1 + credit >= need) break;
        }
        Room r;
        r.cells = static_cast<int>(room.order.size()) - 1 + credit;
        r.pearls = pearl_count;
        return r;
    }

    enum class SimStatus { OK, DEAD, DIVE, H2H, PORTAL };
    struct SimResult {
        SimStatus status = SimStatus::DEAD;
        std::vector<int> body;

        int eaten = 0;
        int hit_id = -1;
        int blind_cell = -1;
    };

    SimResult simulate(const World& w, const std::vector<int>& path) const {
        SimResult out;
        out.body = w.body;

        if (path.empty()) return out;
        std::unordered_set<int> own(out.body.begin(), out.body.end());
        std::unordered_set<int> eaten_cells;
        const int free_steps = Params::sprint_rules_123 ? (w.len + 3) / 4 : 1;
        for (size_t k = 0; k < path.size(); k++) {
            const bool paid = static_cast<int>(k) >= free_steps;
            if (paid && static_cast<int>(out.body.size()) <= 2) return out;
            int head = out.body.empty() ? w.head : out.body.back();
            if (w.is_portal_edge(head, path[k])) {
                int pid = w.epid[w.ekey(head, path[k])];
                if (portal_blocked(w, pid)) {
                    out.status = SimStatus::PORTAL;
                    return out;
                }
            }
            int n = w.dest(head, path[k]);
            if (n == UNKNOWN) n = w.nbr(head, path[k]);
            if (n == UNPAIRED) {
                out.status = (k == 0) ? SimStatus::DIVE : SimStatus::DEAD;
                return out;
            }
            if (n < 0) return out;
            if (own.count(n)) return out;
            if (w.occ[n] >= 0) {
                const Part& hit = w.parts[w.occ[n]];
                if (hit.head) {
                    out.status = SimStatus::H2H;
                    out.hit_id = hit.id;
                }
                return out;
            }
            if (out.blind_cell < 0 && w.cheb(n, w.head) > unswbc::Constants::VISION_RADIUS)
                out.blind_cell = n;
            out.body.push_back(n);
            own.insert(n);
            bool eats = w.pearl_seen[n] == w.rnd && !eaten_cells.count(n);
            if (eats) {
                eaten_cells.insert(n);
                out.eaten++;
            } else {
                if (!out.body.empty()) {
                    own.erase(out.body.front());
                    out.body.erase(out.body.begin());
                }
            }
            if (paid) {
                if (!out.body.empty()) {
                    own.erase(out.body.front());
                    out.body.erase(out.body.begin());
                }
            }
        }
        out.status = SimStatus::OK;
        return out;
    }

    Room room_for_body(const World& w, const SimResult& sim, int need) {
        if (sim.body.empty()) return {};
        std::vector<int> segs(sim.body.begin(), sim.body.end() - 1);
        return flood_room(w, sim.body.back(), segs, 0, need);
    }

    double threat_cost(const World& w, int cell, int length) const {
        if (cell < 0 || cell >= static_cast<int>(threats.size()) || threats[cell].empty()) return 0.0;
        const double mine = dragon_value(w, length);
        double cost = 0.0;
        for (const EnemyThreat& threat : threats[cell]) {
            const double theirs = dragon_value(w, threat.length);
            double probability = length > threat.length ? Params::threat_long
                : length == threat.length ? Params::threat_equal : Params::threat_short;
            if (threat.steps > 1) probability *= Params::threat_sprint_factor;
            const double loss = std::max(Params::threat_base,
                mine - Params::threat_enemy_loss_weight * theirs);
            double threat_value = probability * loss;
            auto supporters = threat_support.find(threat.id);
            if (supporters != threat_support.end())
                threat_value *= std::max(0.25, std::pow(1.0 - Params::threat_ally_support, supporters->second));
            cost = std::max(cost, threat_value);
        }
        return Params::threat_weight * cost;
    }

    bool tyr_split_option(World& w, double& score) {
        const int length = w.len;
        const int child_size = Params::split_child;
        if (length < Params::split_min_len || length - child_size < 2 || w.units >= w.limit ||
            w.rnd >= Params::split_until_round || role_crown || role_feeder ||
            static_cast<int>(w.body.size()) < length) return false;

        std::vector<int> child{w.body[1], w.body[0]};
        std::unordered_set<int> child_cells(child.begin(), child.end());
        std::unordered_set<int> parent_cells(w.body.begin() + child_size, w.body.end());
        int child_head = child.back();
        int exits = 0;
        for (int d = 0; d < 4; d++) {
            int cell = w.dest(child_head, d);
            if (cell >= 0 && !child_cells.count(cell) && !parent_cells.count(cell) && w.occ[cell] < 0)
                exits++;
        }
        if (!exits) return false;
        std::vector<int> child_segs{w.body[1]};
        if (flood_room(w, child_head, child_segs, 0, Params::child_area).cells < Params::child_area)
            return false;

        std::vector<int> parent_segs(w.body.begin() + child_size, w.body.end() - 1);
        int parent_need = std::min(std::max(length - child_size + Params::slack, Params::min_area), Params::flood_cap);
        int area = flood_room(w, w.head, parent_segs, 0, parent_need).cells;
        score = Params::split_value;
        if (area < parent_need)
            score -= Params::trap_weight * static_cast<double>(parent_need - area) / parent_need;
        score -= threat_cost(w, w.head, length - child_size);
        if (child_head >= 0 && child_head < static_cast<int>(danger.size()) && danger[child_head]) score -= 1.0;
        return true;
    }

    bool tyr_opening_split(const World& w, int& size, double& score, char& why) const {
        const int length = w.len;
        if (w.units >= w.limit || w.rnd >= Params::split_until_round || w.rnd >= Params::grow_from ||
            role_crown || role_feeder || static_cast<int>(w.body.size()) >= length) return false;
        if (length >= Params::opening_rescue_min_len && w.rnd <= Params::opening_rescue_until &&
            w.born <= Params::opening_rescue_until &&
            ((w.me & 4095) < Params::opening_initial_id_limit || w.rnd > w.born)) {
            size = length - 2;
            score = Params::opening_rescue_value + 0.1 * (length - Params::opening_rescue_min_len);
            why = 'r';
            return true;
        }
        if (w.rnd < Params::opening_production_start || w.rnd > Params::opening_production_until ||
            length < Params::split_min_len || w.units >= Params::opening_production_unit_cap) return false;
        size = Params::split_child;
        score = Params::opening_production_value;
        why = 's';
        return true;
    }

    int tyr_escape_split(const World& w) const {
        if (w.len < 4 || w.units >= w.limit || static_cast<int>(w.body.size()) < w.len) return 0;
        int size = w.len - 2;
        std::unordered_set<int> child(w.body.begin(), w.body.begin() + size);
        std::unordered_set<int> parent(w.body.begin() + size, w.body.end());
        int child_head = w.body.front();
        for (int d = 0; d < 4; d++) {
            int cell = w.dest(child_head, d);
            if (cell >= 0 && !child.count(cell) && !parent.count(cell) && w.occ[cell] < 0) return size;
        }
        return 0;
    }

    hb1::Row const* hb_row = nullptr;   // HB-1 Q5: this turn's v5 row, or null

    Decision decide(World& w) {
        Decision out;
        hear_radio(w);
        hear_portal_radio(w);
        mark_danger(w);
        if (static_cast<int>(visits.size()) != w.NC) visits.assign(w.NC, 0);
        if (visits[w.head] < 250) visits[w.head]++;
        if (w.rnd % 16 == 0) {
            std::unordered_set<int> recent;
            int n = std::min<int>(64, w.trail.size());
            for (int i = static_cast<int>(w.trail.size()) - n; i < static_cast<int>(w.trail.size()); i++)
                recent.insert(w.trail[i]);
            for (int cell : recent) if (visits[cell]) visits[cell]--;
        }

        build_block_mask(w, mask);
        const int age = w.rnd - w.born;
        int cap = age < 2 ? Params::search_cap_born : Params::search_cap;
        if (age >= 2 && w.units * 10 >= w.limit * 7)
            cap = std::min(cap, Params::search_cap_saturated);
        if (w.rnd >= Params::search_cap_late_from) cap = std::min(cap, Params::search_cap_late);
        if (age >= 2 && w.rnd >= Params::search_cap_sparse_from &&
            w.units <= Params::search_cap_sparse_units)
            cap = std::max(cap, Params::search_cap_sparse);
        fwd.d.assign(w.NC, -1); fwd.first.assign(w.NC, -1);
        fwd.first_mask.assign(w.NC, 0); fwd.parent.assign(w.NC, -1);
        if (Params::free_sprint) { fwd.pm2.assign(w.NC, 0); fwd.pm3.assign(w.NC, 0); }
        fwd.order.clear(); fwd.dives.clear(); fwd.from = w.head;
        fwd.d[w.head] = 0; fwd.order.push_back(w.head);

        bool feeder = role_feeder;
        bool crown = role_crown;
        double vmax = Params::unseen_value;
        bool have_memory = false, have_bed = false;
        for (int c = 0; c < w.NC; c++) {
            have_memory = have_memory || w.pearl_seen[c] >= 0;
            have_bed = have_bed || w.spawn_at[c] >= 0;
        }
        if (have_memory) vmax = Params::pearl_value;
        else if (have_bed && Params::bed_value > vmax) vmax = Params::bed_value;
        if (!w.pends.empty() && Params::dive_value > vmax) vmax = Params::dive_value;

        int target = -1, dive_dir = -1;
        char target_why = '-';
        double best_value = 0.0, previous_value = 0.0, disc = 1.0;
        int previous_target_local = previous_target;
        int last_t = 0;
        int qi = 0;
        while (qi < static_cast<int>(fwd.order.size()) && static_cast<int>(fwd.order.size()) < cap) {
            int c = fwd.order[qi++];
            int t = fwd.d[c] + 1;
            if (t != last_t) {
                last_t = t;
                disc = std::pow(Params::target_gamma, t);
                if (t > Params::frontier_search_depth && !feeder && vmax * disc <= best_value) break;
            }
            for (int d = 0; d < 4; d++) {
                int n = w.step_opt(c, d);
                if (n < 0) {
                    if (n == UNPAIRED && !crown && !feeder) {
                        double value = Params::dive_value;
                        for (int pi : w.ally_heads)
                            if (w.tdist(w.parts[pi].cell, c) < t - 1) {
                                value *= Params::own_target_discount;
                                break;
                            }
                        double score = value * disc;
                        if (score > best_value) {
                            best_value = score; target = c; dive_dir = d; target_why = 'd';
                        }
                    }
                    continue;
                }
                uint8_t first_mask = c == w.head ? static_cast<uint8_t>(1U << d) : fwd.first_mask[c];
                uint16_t p2 = 0; uint64_t p3 = 0;
                if (Params::free_sprint && c != w.head) {
                    if (t == 2) {
                        for (int d1 = 0; d1 < 4; d1++) if (first_mask & (1U << d1)) p2 |= static_cast<uint16_t>(1U << (d1 * 4 + d));
                    } else {
                        p2 = fwd.pm2[c];
                        if (t == 3) {
                            for (int b = 0; b < 16; b++) if (p2 & (1U << b)) p3 |= 1ULL << (b * 4 + d);
                        } else p3 = fwd.pm3[c];
                    }
                }
                int old_dist = fwd.d[n];
                if (old_dist >= 0) {
                    if (old_dist == t) {
                        fwd.first_mask[n] |= first_mask;
                        if (Params::free_sprint) { fwd.pm2[n] |= p2; fwd.pm3[n] |= p3; }
                    }
                    continue;
                }
                if (mask[n] > t) continue;
                fwd.d[n] = t;
                fwd.first_mask[n] = first_mask;
                if (Params::free_sprint) { fwd.pm2[n] = p2; fwd.pm3[n] = p3; }
                fwd.first[n] = static_cast<int8_t>(c == w.head ? d : fwd.first[c]);
                fwd.parent[n] = c * 4 + d;
                fwd.order.push_back(n);
                if (feeder) continue;
                if (w.pearl_seen[n] < 0 && w.bed[n] != 1 && w.seen[n] != 0) continue;
                double value = cell_value(w, n, t);
                if (value <= 0.0) continue;
                double score = value * disc;
                if (n == previous_target_local) previous_value = score;
                if (score > best_value) {
                    best_value = score; target = n; dive_dir = -1;
                    target_why = w.pearl_known(n, Params::memory_ttl) ? 'p'
                        : (w.bed[n] == 1 ? 'b' : 'x');
                }
            }
            if (feeder && crown_cell >= 0 && fwd.d[crown_cell] >= 0) break;
        }

        if (feeder) {
            target = crown_cell; best_value = 1.0; dive_dir = -1; target_why = 'c';
        } else {
            if (dive_dir < 0 && previous_target_local >= 0 && previous_value > 0.0 &&
                previous_target_local != target && previous_value * Params::target_hysteresis >= best_value) {
                target = previous_target_local; best_value = previous_value; target_why = 'm';
            }
            if (target < 0) target = far_target(w);
            if (!role_crown && !role_feeder && prey_id >= 0 &&
                w.rnd >= Params::hunt_from && w.len <= Params::hunt_max_len &&
                w.rnd - prey_round <= Params::prey_ttl) {
                int steps = prey_cell >= 0 && fwd.d[prey_cell] >= 0
                    ? fwd.d[prey_cell] : w.tdist(w.head, prey_cell) + 2;
                double score = Params::hunt_value * std::min(prey_len, 40) *
                    std::pow(Params::target_gamma, steps);
                if (score > best_value) {
                    best_value = score; target = prey_cell; dive_dir = -1; target_why = 'h';
                }
            }
        }
        previous_target = target;

        int normal_target = target;
        bool escaping = plan_escape(w, normal_target, fwd.d, fwd.first_mask, target);
        if (escaping) target_why = 'e';
        out.target = target; out.why = target_why;

        const std::vector<int16_t>* route_dist = &fwd.d;
        const std::vector<uint8_t>* route_mask = &fwd.first_mask;
        if (escape_active && escape_plan_target == target &&
            static_cast<int>(escape_plan_dist.size()) == w.NC) {
            route_dist = &escape_plan_dist;
            route_mask = &escape_plan_mask;
        }
        int progress[4] = {0, 0, 0, 0};
        int route_ref = -1;   // carthage-05: the cell whose shortest-route prefixes a free sprint must follow
        if (target >= 0 && target != w.head) {
            if ((*route_dist)[target] >= 0) {
                uint8_t m = (*route_mask)[target];
                for (int d = 0; d < 4; d++) progress[d] = (m & (1U << d)) ? 1 : -1;
                route_ref = target;
            } else {
                int waypoint = -1, cost = std::numeric_limits<int>::max();
                for (int c : fwd.order) {
                    int steps = fwd.d[c];
                    if (!steps) continue;
                    int candidate = 3 * w.tdist(c, target) + steps;
                    if (candidate < cost) { cost = candidate; waypoint = c; }
                }
                if (waypoint >= 0) {
                    uint8_t m = fwd.first_mask[waypoint];
                    for (int d = 0; d < 4; d++) progress[d] = (m & (1U << d)) ? 1 : -1;
                    route_ref = waypoint;
                }
            }
        }

        // Foragers feed the crown only when its head is visible and nearby.
        if (feeder && crown_id >= 0) {
            int visible_crown = -1;
            for (int pi : w.ally_heads)
                if ((w.parts[pi].id & 4095) == crown_id) { visible_crown = w.parts[pi].cell; break; }
            if (visible_crown >= 0 && w.tdist(visible_crown, w.head) <= Params::feed_dist) {
                int back = opposite(w.face);
                int order[] = {back, 0, 1, 2, 3};
                for (int d : order) {
                    if (simulate(w, {d}).status == SimStatus::DEAD) {
                        out.act = Act::MOVE; out.dirs = {d}; out.why = 'f'; out.target = target;
                        for (double& m : momentum) m *= Params::momentum_decay;
                        momentum[d] += 1.0 - Params::momentum_decay;
                        return out;
                    }
                }
            }
        }

        std::unordered_set<int> crown_flank;
        if (feeder && crown_id >= 0) {
            for (const Part& part : w.parts) {
                if (!part.ally || (part.id & 4095) != crown_id) continue;
                for (int d = 0; d < 4; d++) {
                    int n = w.dest(part.cell, d);
                    if (n >= 0) crown_flank.insert(n);
                }
            }
        }
        bool near_threat = false;
        for (int pi : w.enemy_heads)
            if (w.cheb(w.parts[pi].cell, w.head) <= 4) { near_threat = true; break; }
        std::vector<std::vector<int>> paths;
        for (int d = 0; d < 4; d++) paths.push_back({d});
        int sprint_limit = w.units * 10 >= w.limit * 7
            ? Params::sprint3_saturated_limit : Params::sprint3_limit;
        if (w.rnd >= Params::sprint3_late_from)
            sprint_limit = std::min(sprint_limit, Params::sprint3_late_limit);
        if (w.rnd >= Params::sprint3_late_from && w.units <= Params::search_cap_sparse_units)
            sprint_limit = std::max(sprint_limit, Params::sprint3_sparse_limit);
        const int free_steps = Params::sprint_rules_123 ? (w.len + 3) / 4 : 1;
        const bool free_route = Params::free_sprint && route_ref >= 0 && route_mask == &fwd.first_mask &&
            static_cast<int>(fwd.pm2.size()) == w.NC;
        if (free_route && !near_threat && free_steps >= 2 && fwd.d[route_ref] >= 2) {
            uint16_t m2 = fwd.pm2[route_ref];
            for (int b = 0; b < 16; b++) if (m2 & (1U << b)) paths.push_back({b / 4, b % 4});
            if (free_steps >= 3 && fwd.d[route_ref] >= 3) {
                uint64_t m3 = fwd.pm3[route_ref];
                for (int b = 0; b < 64; b++) if (m3 & (1ULL << b)) paths.push_back({b / 16, (b / 4) % 4, b % 4});
            }
        }
        if (near_threat && w.len >= 3) {
            for (int d1 = 0; d1 < 4; d1++) {
                for (int d2 = 0; d2 < 4; d2++) {
                    if (d2 == ((d1 + 2) & 3)) continue;
                    paths.push_back({d1, d2});
                    if (w.len >= 4 && w.len < sprint_limit) {
                        for (int d3 = 0; d3 < 4; d3++) {
                            if (d3 == ((d2 + 2) & 3)) continue;
                            paths.push_back({d1, d2, d3});
                        }
                    }
                }
            }
        }

        int need = flood_need(w, w.len);
        // HB-1 Q5 (hb1-12): Heartbreaker's direction model as a prior on the first step (absolute dir -> log p).
        double hb_logp[4] = {0.0, 0.0, 0.0, 0.0};
        if (Params::hb1_dir_lambda > 0 && hb_row) {
            static hb1::Bound const dir_bound{hb1::dirc_bind};
            auto p = hb1::dirc_proba(dir_bound.vec(*hb_row));
            static constexpr char RELS[3] = {'F', 'R', 'L'};
            char const fc = dir_char(w.face);
            for (int i = 0; i < 3; i++) {
                char a = hb1::rel_to_abs(fc, RELS[hb1::dirc_classes[i]]);
                int d = a == 'N' ? 0 : a == 'E' ? 1 : a == 'S' ? 2 : 3;
                hb_logp[d] = Params::hb1_dir_lambda * std::log(std::max(p[i], 1e-4));
            }
        }
        double best_score = -1e30;
        Decision selected;
        selected.act = Act::MOVE; selected.target = target;
        for (int d = 0; d < 4; d++) {
            int pid = w.is_portal_edge(w.head, d) ? w.epid[w.ekey(w.head, d)] : -1;
            if (!portal_blocked(w, pid)) { selected.dirs = {d}; break; }
        }
        if (selected.dirs.empty()) selected.dirs = {w.face};
        for (const auto& path : paths) {
            SimResult sim = simulate(w, path);
            if (sim.status == SimStatus::PORTAL) continue;
            int steps = static_cast<int>(path.size());
            int first = path.front();
            double score = -1000.0 - steps;
            if (sim.status == SimStatus::DIVE) {
                score = Params::dive_base - Params::p_dive * dragon_value(w, w.len);
                if (dive_dir == first && target == w.head) score += Params::dive_value * 0.5;
                score -= threat_cost(w, w.head, w.len) * 0.5;
                score += hb_logp[first];
                score += escape_active ? Params::escape_portal_bonus *
                    std::pow(Params::escape_decay, std::max(0, w.rnd - escape_start)) : 0.0;
            } else if (sim.status == SimStatus::H2H) {
                bool enemy_head = false;
                for (int pi : w.enemy_heads) if (w.parts[pi].id == sim.hit_id) { enemy_head = true; break; }
                double strike = -std::numeric_limits<double>::infinity();
                if (enemy_head && Params::attack_min_units <= w.units) {
                    int their_len = enemy_length(w, sim.hit_id);
                    int support = 0;
                    for (int ai : w.ally_heads)
                        if (w.tdist(w.parts[ai].cell, w.head) <= 3) support++;
                    double gain = dragon_value(w, their_len) - dragon_value(w, w.len) -
                        Params::sprint_cost * sprint_paid(w, steps) + 0.5 * std::min(support, 2);
                    if (gain >= Params::attack_margin) strike = 2.0 + gain;
                }
                score = std::isfinite(strike) ? strike : (enemy_head ? -950.0 : -1100.0);
            } else if (sim.status == SimStatus::OK) {
                // Tyr's simulator preserves only the represented body cells,
                // which can be partial after a trail reset. Its material term
                // is len(simulated_body) - observed_length; keep that exact
                // calculation instead of treating the partial body as full.
                int simulated_len = static_cast<int>(sim.body.size());
                int final_head = sim.body.back();
                int body_count = simulated_len;
                Room area = room_for_body(w, sim, need);
                score = Params::goal_weight * progress[first] * (steps == 1 ? 1.0 : 0.7);
                if (steps > 1 && free_route && steps <= free_steps && fwd.d[route_ref] >= steps &&
                    (steps == 2 ? (fwd.pm2[route_ref] >> (path[0] * 4 + path[1])) & 1U
                                : (fwd.pm3[route_ref] >> (path[0] * 16 + path[1] * 4 + path[2])) & 1ULL))
                    score = Params::goal_weight * steps;
                score += lv_now(w) * (simulated_len - w.len) - Params::sprint_cost * sprint_paid(w, steps);
                score += 0.5 * sim.eaten;
                if (sim.blind_cell >= 0) score -= blind_risk(w, sim.blind_cell) * dragon_value(w, simulated_len);
                score += devil_center_bonus(w, final_head);
                score += devil_lane_bonus(w, final_head);
                score -= ally_body_buffer(w, final_head);
                score += escape_action_bonus(w, final_head, first);
                score += hb_logp[first];
                if (crown_flank.count(final_head)) score -= Params::w_flank;
                score -= threat_cost(w, final_head, simulated_len);
                for (int pi : w.ally_heads) {
                    int distance = w.tdist(w.parts[pi].cell, final_head);
                    if (distance <= 2) score -= Params::crowd_weight * (3 - distance);
                }
                if (final_head >= 0 && final_head < static_cast<int>(visits.size()))
                    score -= Params::visit_weight * visits[final_head];
                if (Params::momentum_weight) score += Params::momentum_weight * momentum[first];
                if (w.bed[final_head] == 1 && w.spawn_at[final_head] == w.rnd + 1)
                    score -= Params::w_bed_block;
                if (area.cells < need) {
                    double penalty = Params::trap_weight *
                        static_cast<double>(need - area.cells) / std::max(1, need);
                    if (area.cells < body_count) penalty += Params::trap_weight;
                    double value_scale = dragon_value(w, simulated_len) / Params::trap_value_reference;
                    if (value_scale > 1.0) penalty *= value_scale;
                    bool farm = body_count + area.pearls >= Params::split_min_len &&
                        body_count + area.pearls > area.cells + 1 && w.units < w.limit;
                    if (farm) penalty *= Params::trap_farm_factor;
                    score -= penalty;
                }
            }
            if (score > best_score) {
                best_score = score;
                selected.act = Act::MOVE; selected.dirs = path; selected.target = target;
                selected.why = target_why;
            }
        }

        double split_score = 0.0;
        if (tyr_split_option(w, split_score) && split_score > best_score) {
            best_score = split_score;
            selected.act = Act::SPLIT; selected.split = Params::split_child;
            selected.target = target; selected.why = 's';
        }
        int opening_size = 0; double opening_score = 0.0; char opening_why = 's';
        if (tyr_opening_split(w, opening_size, opening_score, opening_why) && opening_score > best_score) {
            best_score = opening_score;
            selected.act = Act::SPLIT; selected.split = opening_size;
            selected.target = target; selected.why = opening_why;
        }
        if (best_score < -900.0) {
            int escape_size = tyr_escape_split(w);
            if (escape_size > 0 && -500.0 > best_score) {
                best_score = -500.0;
                selected.act = Act::SPLIT; selected.split = escape_size;
                selected.target = target; selected.why = 't';
            }
        }
        if (selected.act == Act::MOVE) {
            for (double& m : momentum) m *= Params::momentum_decay;
            if (!selected.dirs.empty()) momentum[selected.dirs.front()] += 1.0 - Params::momentum_decay;
        }
        selected.target = target;
        return selected;
    }

};

}  // namespace ares
