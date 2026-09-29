// Ares V02 — Tyr V12 policy translation on the Anna A02 chassis.
//
// Target choice ports Tyr's discounted resource field, ownership/density
// discounts and hysteresis. Candidate actions port momentum, material, Devil,
// threat, crowding, trap, sprint and newborn-separation terms. Anna's hard
// action tiers and room-valid splits remain the safety substrate.
#pragma once

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
    int tier = -1;
    char why = '-';         // p pearl, b bed, x explore, h prey, e escape, s split
};

// Action outcome classes, best first; each candidate may be a one- to three-step sprint.
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
    std::vector<double> threat_costs;
    std::vector<int> danger_cells;
    std::vector<uint16_t> room_mask;
    std::vector<uint8_t> visits;
    std::array<double, 4> momentum{};
    int previous_target = -1;
    double previous_target_value = 0.0;
    int previous_dive_dir = -1;

    struct DensityReport {
        double x = 0.0, y = 0.0, allies = 1.0, enemies = 0.0;
        int rnd = -1;
        uint64_t packet = 0;
    };
    std::unordered_map<int, DensityReport> density_reports;
    bool have_local_density = false;
    double local_x = 0.0, local_y = 0.0, local_allies = 1.0, local_enemies = 0.0;
    int local_density_round = -1, local_head = -1;
    int crown_id = -1, crown_cell = -1, crown_len = 0, crown_round = -1;
    int last_crown_round = 0;
    bool role_crown = false, role_feeder = false;
    int prey_id = -1, prey_cell = -1, prey_len = 0, prey_round = -1;
    std::array<uint64_t, 4> sonar_out{};
    bool escape_active = false, escape_packet_seen = false;
    int escape_parent = -1, escape_origin = -1, escape_start = -1, escape_waypoint = -1;
    int escape_pause_used = 0;
    uint64_t pending_handoff = 0;
    int pending_handoff_round = -1;
    std::vector<int> escape_origin_dist;
    std::vector<uint8_t> escape_plan_mask;
    int escape_plan_target = -1;

    struct Search {
        std::vector<int> dist;
        std::vector<uint8_t> mask;
        std::vector<int> order;
    };
    struct Topology {
        int area = 0, branches = 0, degree = 0;
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
        Search s; bounded_search(w, start, depth, cap, nullptr, s);
        Topology t; t.area = static_cast<int>(s.order.size());
        for (int c : s.order) {
            std::unordered_set<int> adjacent;
            for (int d = 0; d < 4; d++) {
                int n = w.step_opt(c, d);
                if (n >= 0 && n != c) adjacent.insert(n);
            }
            if (c == start) t.degree = static_cast<int>(adjacent.size());
            if (adjacent.size() >= 3) t.branches++;
        }
        return t;
    }

    bool should_escape_spawn(const World& w, int cell) const {
        Topology t = topology(w, cell, 3, 64);
        return t.degree <= 2 && (t.area <= Params::escape_spawn_area ||
                                 t.branches <= Params::escape_spawn_branches);
    }

    double escape_resource_value(const World& w, int cell) const {
        int r = w.pearl_seen[cell];
        if (r >= 0 && r == w.rnd) return Params::pearl_value;
        if (r >= 0 && w.rnd - r <= Params::memory_ttl) return Params::memory_value;
        if (w.bed[cell] == 1 && w.spawn_at[cell] >= w.rnd)
            return Params::bed_value * std::max(0.0, 1.0 - (w.spawn_at[cell] - w.rnd) / Params::bed_wait);
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
            Params::escape_exit_weight * std::max(0, t.degree - 2) +
            Params::escape_distance_weight * std::min(away, 8) +
            Params::escape_resource_weight * escape_local_resource(w, cell) -
            Params::escape_route_cost * route_distance;
    }

    bool plan_escape(World& w, int normal_target, int& target) {
        escape_plan_target = -1;
        escape_plan_mask.assign(w.NC, 0);
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
        bool open = here.degree >= 3 || here.area >= Params::escape_open_area || here.branches >= 2;
        if (age >= 1 && current_dist >= Params::escape_min_distance && open) {
            escape_active = false; escape_waypoint = -1; return false;
        }
        Search routes;
        bounded_search(w, w.head, Params::escape_target_depth, Params::escape_target_nodes,
                       &w.body, routes);
        if (normal_target >= 0 && normal_target < w.NC && routes.dist[normal_target] >= 0 &&
            routes.dist[normal_target] <= Params::escape_valuable_distance &&
            w.pearl_seen[normal_target] == w.rnd &&
            escape_resource_value(w, normal_target) >= Params::escape_valuable_threshold &&
            escape_pause_used < Params::escape_resource_pause_budget) {
            escape_pause_used++;
            target = normal_target; escape_plan_target = normal_target;
            escape_plan_mask = routes.mask;
            return true;
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
        if (escape_waypoint >= 0 && routes.dist[escape_waypoint] >= 0 &&
            std::find(eligible.begin(), eligible.end(), escape_waypoint) != eligible.end()) {
            double old = escape_waypoint_score(w, escape_waypoint, routes.dist[escape_waypoint]);
            if (old >= best_score - Params::escape_waypoint_hysteresis) best = escape_waypoint;
        }
        escape_waypoint = best; escape_plan_target = best; escape_plan_mask = std::move(routes.mask);
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
        double d = std::fmod(b - a + size * 1.5, static_cast<double>(size)) - size * 0.5;
        return d;
    }

    void hear_radio(World& w) {
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
                    if (w.seen[c] && w.seen[c] - 1 >= w.rnd - 8) continue;
                    if (r <= w.rnd) {
                        if (w.rnd - r <= Params::memory_ttl && w.pearl_seen[c] < r)
                            w.pearl_seen[c] = r;
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
                    if (crown_id < 0 || w.rnd - crown_round > Params::crown_ttl ||
                        (id == crown_id && rnd >= crown_round) ||
                        len >= crown_len + 3 || (len == crown_len && id < crown_id)) {
                        crown_id = id; crown_cell = cell; crown_len = len; crown_round = rnd;
                    }
                } else if (type == 4 && w.rnd - rnd <= Params::prey_ttl && len >= 8 &&
                           (prey_id < 0 || w.rnd - prey_round > Params::prey_ttl || len > prey_len ||
                            (id == prey_id && rnd >= prey_round))) {
                    prey_id = id; prey_cell = cell; prey_len = len; prey_round = rnd;
                }
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
                    if (inherit) {
                        crown_id = w.me & 4095; crown_cell = w.head; crown_len = w.len;
                        crown_round = w.rnd; role_crown = true;
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
                density_reports[id] = {static_cast<double>(x), static_cast<double>(y),
                                       static_cast<double>(allies), static_cast<double>(enemies), rnd, msg};
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
        if (crown_id >= 0 && crown_id != (w.me & 4095) && w.rnd - crown_round <= Params::crown_ttl)
            last_crown_round = w.rnd;
        if (crown_id >= 0 && w.rnd - crown_round > Params::crown_ttl) crown_id = -1;
        if (w.dest_dirty) w.rebuild_dest();

        int me = w.me & 4095;
        if (w.rnd >= 250) {
            bool claim = false;
            if (crown_id < 0) {
                int claim_round = std::max(250, last_crown_round) + (w.me * 7919) % Params::crown_claim_spread;
                claim = w.rnd >= claim_round && w.len >= Params::crown_claim_len;
            } else if (crown_id == me) {
                claim = true;
            } else if (w.len >= crown_len + Params::crown_margin || (w.len == crown_len && me < crown_id)) {
                claim = true;
            }
            if (claim) {
                crown_id = me; crown_cell = w.head; crown_len = w.len; crown_round = w.rnd;
                last_crown_round = w.rnd;
            }
        }
        role_crown = crown_id == me && w.rnd >= 250;
        role_feeder = false;
        int feed_from = 500 - Params::feed_base - static_cast<int>((w.W + w.H) * Params::feed_k);
        if (!role_crown && crown_id >= 0 && w.rnd - crown_round <= Params::crown_ttl && w.rnd >= feed_from &&
            crown_len >= Params::feed_min_crown && crown_len > w.len && w.tdist(w.head, crown_cell) <= Params::feed_range)
            role_feeder = true;

        if (prey_id >= 0 && w.rnd - prey_round > Params::prey_ttl) prey_id = -1;
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
            local_x = std::fmod(local_x + gain * wrapped_delta(local_x, x, w.W) + w.W, w.W);
            local_y = std::fmod(local_y + gain * wrapped_delta(local_y, y, w.H) + w.H, w.H);
            local_allies = retain * local_allies + gain * visible_allies;
            local_enemies = retain * local_enemies + gain * visible_enemies;
        }
        have_local_density = true; local_density_round = w.rnd; local_head = w.head;
        for (auto it = density_reports.begin(); it != density_reports.end();) {
            if (w.rnd - it->second.rnd > Params::density_ttl) it = density_reports.erase(it);
            else ++it;
        }
        if (density_reports.size() > static_cast<size_t>(Params::density_sources)) {
            auto oldest = std::min_element(density_reports.begin(), density_reports.end(),
                [](const auto& a, const auto& b) {
                    return a.second.rnd == b.second.rnd ? a.first < b.first : a.second.rnd < b.second.rnd;
                });
            density_reports.erase(oldest);
        }
        if (w.rnd >= Params::hunt_from && w.len <= Params::hunt_max_len) {
            for (int pi : w.enemy_heads) {
                const Part& e = w.parts[pi];
                auto it = w.mem.find(e.id);
                int len = it == w.mem.end() ? 1 : std::max(1, it->second.vis_len);
                if (len >= 8 && (prey_id < 0 || len > prey_len || (e.id & 4095) == prey_id)) {
                    prey_id = e.id & 4095; prey_cell = e.cell; prey_len = len; prey_round = w.rnd;
                }
            }
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
        if (have_local_density) add(local_x, local_y, local_allies, local_enemies, local_density_round);
        for (const auto& row : density_reports)
            add(row.second.x, row.second.y, row.second.allies, row.second.enemies, row.second.rnd);
        double denom = std::max(1.0, total);
        return 1.0 / (1.0 + Params::density_ally_weight * std::max(0.0, allies / denom - 1.0) + Params::density_enemy_weight * enemies / denom);
    }

    void prepare_radio(const World& w, const Decision* decision = nullptr) {
        sonar_out.fill(0);
        std::vector<int> dirs{0, 1, 2, 3};
        if (w.rnd >= 250 && crown_id >= 0 && w.rnd - crown_round <= Params::crown_ttl) {
            uint64_t packet = crown_packet(w, 1, crown_id, crown_cell, crown_len, crown_round);
            std::array<int, 2> pair = (w.rnd % 2 == 0) ? std::array<int, 2>{0, 2} : std::array<int, 2>{1, 3};
            for (int d : pair) { sonar_out[d] = packet; dirs.erase(std::remove(dirs.begin(), dirs.end(), d), dirs.end()); }
        }
        if (prey_id >= 0 && w.rnd - prey_round <= Params::prey_ttl && !dirs.empty()) {
            int d = (w.rnd % 2 == 0) ? dirs.back() : dirs.front();
            sonar_out[d] = crown_packet(w, 4, prey_id, prey_cell, prey_len, prey_round);
            dirs.erase(std::remove(dirs.begin(), dirs.end(), d), dirs.end());
        }
        if (w.rnd % 2 == 0 && !dirs.empty() && 2 * w.NC <= 8192) {
            std::vector<std::pair<int, int>> pairs;
            for (const auto& row : w.pends)
                if (row.second[0] >= 0 && row.second[1] >= 0)
                    pairs.push_back({row.first, row.second[0]});
            if (!pairs.empty()) {
                std::sort(pairs.begin(), pairs.end());
                int index = (w.rnd / 2 + w.me) % static_cast<int>(pairs.size());
                int pid = pairs[index].first;
                auto ends = w.pends.at(pid);
                uint64_t payload = static_cast<uint64_t>(ends[0] & 8191) |
                    (static_cast<uint64_t>(ends[1] & 8191) << 13) |
                    (static_cast<uint64_t>(pid & 255) << 26);
                int d = dirs.back();
                sonar_out[d] = pack(w, 5, payload);
                dirs.pop_back();
            }
        }
        if (w.W <= 64 && w.H <= 64) {
            std::vector<std::pair<int, int>> entries, beds;
            for (int c = 0; c < w.NC; c++) {
                if (w.seen[c] != w.rnd + 1) continue;
                if (w.pearl_seen[c] == w.rnd) entries.push_back({c, w.rnd});
                else if (w.spawn_at[c] > w.rnd && w.spawn_at[c] <= w.rnd + Params::gossip_horizon) beds.push_back({c, w.spawn_at[c]});
            }
            std::sort(beds.begin(), beds.end(), [](auto a, auto b) { return a.second < b.second; });
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
                    sonar_out[d] = pack(w, 2, payload);
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
                    sonar_out[selected[k]] = density_reports.at(id).packet;
                } else sonar_out[selected[k]] = density;
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
                sonar_out[(w.face + 2) & 3] = pending_handoff;
            }
        } else if (pending_handoff && pending_handoff_round >= 0) {
            int age = w.rnd - pending_handoff_round;
            if (age > 0 && age <= Params::escape_handoff_retries)
                sonar_out[(w.face + 2) & 3] = pending_handoff;
            else if (age > Params::escape_handoff_retries) {
                pending_handoff = 0; pending_handoff_round = -1;
            }
        }
    }

    void prepare_radio_for_decision(const World& w, const Decision& d) { prepare_radio(w, &d); }

    void send_radio(unswbc::Controller& ct) const {
        auto directions = unswbc::Direction::get_direction_list();
        for (int d = 0; d < 4; d++) if (sonar_out[d]) ct.send_sonar(directions[d], sonar_out[d]);
    }

    double lv_now(const World& w) const {
        if (role_crown) return 4.0;
        if (w.rnd < Params::grow_from) return 1.0;
        double f = std::clamp((w.rnd - Params::grow_from) / 120.0, 0.0, 1.0);
        return 1.0 + (Params::lv_end - 1.0) * f;
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
        } else if (w.bed[c] == 1 ||
                   (c < static_cast<int>(w.atlas_bed.size()) && w.atlas_bed[c])) {
            int spawn = w.spawn_at[c];
            int arrival = w.rnd + steps;
            if (spawn >= 0 && spawn > arrival) {
                v = Params::bed_value * std::max(0.0, 1.0 - (spawn - arrival) / Params::bed_wait);
            } else if (spawn > w.rnd) {
                v = Params::bed_value;
            } else if (spawn >= 0) {
                int age = w.rnd - spawn;
                v = age <= Params::bed_stale
                    ? Params::bed_value * (1.0 - 0.5 * age / Params::bed_stale)
                    : Params::bed_value * 0.3;
            } else {
                v = Params::bed_value * 0.5;
            }
        } else if (!w.seen[c]) {
            v = Params::unseen_value;
        }
        if (v <= 0.0) return 0.0;
        if (local_crown(w)) return v;
        if (crown_id >= 0 && w.rnd >= 250 && w.rnd - crown_round <= Params::crown_ttl) {
            int radius = w.rnd >= (500 - 40 - static_cast<int>((w.W + w.H) * 0.6)) ? 5 : 3;
            if (w.tdist(c, crown_cell) <= radius) return 0.0;
        }
        if (w.rnd >= 250) {
            for (int pi : w.ally_heads) {
                const Part& p = w.parts[pi];
                auto it = w.mem.find(p.id);
                if (it == w.mem.end() || it->second.vis_len <= w.len) continue;
                int radius = w.rnd >= 396 ? 5 : 3;
                if (w.tdist(c, p.cell) <= radius) return 0.0;
            }
        }
        for (int pi : w.ally_heads) {
            const Part& p = w.parts[pi];
            if (w.tdist(p.cell, c) < steps ||
                (w.tdist(p.cell, c) == steps && (p.id & 4095) < (w.me & 4095))) {
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

    double devil_center_bonus(const World& w, int c) const {
        if (w.W != 32 || w.H != 16 || w.rnd >= Params::devil_center_until || role_crown || role_feeder) return 0.0;
        int x0 = w.W / 2 - 1, x1 = w.W / 2;
        int before = std::min(std::abs(w.head % w.W - x0), std::abs(w.head % w.W - x1));
        int after = std::min(std::abs(c % w.W - x0), std::abs(c % w.W - x1));
        return before > 2 && after < before ? Params::devil_center_weight : 0.0;
    }

    double devil_lane_bonus(const World& w, int c) const {
        if (w.W != 32 || w.H != 16 || w.rnd >= Params::devil_lane_until || role_crown || role_feeder) return 0.0;
        int lane = ((w.me % 6) * w.H / 6 + w.H / 12) % w.H;
        auto dy = [&](int y) { int d = std::abs(y - lane); return std::min(d, w.H - d); };
        return dy(c / w.W) < dy(w.head / w.W) ? Params::devil_lane_weight : 0.0;
    }

    double ally_body_buffer(const World& w, int c) const {
        if (w.W != 32 || w.H != 16) return 0.0;
        int clearance = 99;
        for (const Part& p : w.parts) {
            if (!p.ally || p.head) continue;
            clearance = std::min(clearance, w.tdist(c, p.cell));
        }
        if (clearance <= 1) return Params::devil_ally_body_weight;
        if (clearance == 2) return 0.5 * Params::devil_ally_body_weight;
        return 0.0;
    }

    int emergency_split_size(const World& w) const {
        if (w.len < 4 || w.units >= w.limit || static_cast<int>(w.body.size()) < w.len) return 0;
        int n = w.len - 2;
        std::unordered_set<int> child(w.body.begin(), w.body.begin() + n);
        std::unordered_set<int> parent(w.body.begin() + n, w.body.end());
        int child_head = w.body.front();
        for (int d = 0; d < 4; d++) {
            int c = w.dest(child_head, d);
            if (c >= 0 && !child.count(c) && !parent.count(c) && w.occ[c] < 0) return n;
        }
        return 0;
    }

    void mark_danger(const World& w) {
        if (static_cast<int>(danger.size()) != w.NC) danger.assign(w.NC, 0);
        if (static_cast<int>(threat_costs.size()) != w.NC) threat_costs.assign(w.NC, 0.0);
        for (int c : danger_cells) {
            danger[c] = 0;
            threat_costs[c] = 0.0;
        }
        danger_cells.clear();
        for (int pi : w.enemy_heads) {
            const Part& head = w.parts[pi];
            int src = head.cell;
            auto it = w.mem.find(head.id);
            int enemy_len = it == w.mem.end() ? 1 : std::max(1, it->second.vis_len);
            if (it != w.mem.end() && it->second.vis_len >= 1 &&
                w.cheb(src, w.head) <= unswbc::Constants::VISION_RADIUS)
                enemy_len = std::max(enemy_len, it->second.vis_len);
            int reach = std::clamp(enemy_len - 1, 1, Params::enemy_reach_max);
            std::vector<int> steps(w.NC, -1), frontier{src}, next;
            steps[src] = 0;
            for (int depth = 0; depth < reach; depth++) {
                next.clear();
                for (int c : frontier) {
                    for (int d = 0; d < 4; d++) {
                        int n = w.dest(c, d);
                        if (n < 0 || steps[n] >= 0) continue;
                        steps[n] = depth + 1;
                        if (!danger[n]) danger_cells.push_back(n);
                        danger[n] = 1;
                        double mine = dragon_value(w, w.len);
                        double theirs = dragon_value(w, enemy_len);
                        double probability = w.len > enemy_len ? Params::threat_long
                            : w.len == enemy_len ? Params::threat_equal : Params::threat_short;
                        if (depth + 1 > 1) probability *= Params::threat_sprint_factor;
                        double loss = std::max(1.0, mine - 0.5 * theirs);
                        threat_costs[n] = std::max(threat_costs[n], probability * loss);
                        if (w.occ[n] < 0 && !w.own[n]) next.push_back(n);
                    }
                }
                frontier.swap(next);
            }
        }
    }

    bool should_split(const World& w) const {
        if (w.len < Params::split_min_len) return false;
        if (w.len - Params::split_child < unswbc::Constants::MIN_SIZE) return false;
        if (Params::split_child < unswbc::Constants::MIN_SIZE) return false;
        if (w.units >= w.limit || w.rnd >= Params::split_until_round) return false;
        if (role_crown || role_feeder) return false;
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
        int pearls = 0;
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
                if (w.pearl_seen[n] == w.rnd) pearl_count++;
            }
            credit += cc;
            if (static_cast<int>(room.order.size()) - 1 + credit >= need) break;
        }
        Room r;
        r.cells = static_cast<int>(room.order.size()) - 1 + credit;
        r.pearls = pearl_count;
        // Tail chase counts only in a space at least as big as the body.
        if (r.cells >= static_cast<int>(segs.size()) + 1)
            for (size_t i = 0; i < segs.size() && !r.escape; i++)
                if (room.d[segs[i]] > 0) r.escape = true;
        return r;
    }

    int room_need(int len) const {
        int need = std::max(len + Params::room_margin, Params::room_min);
        int cap = len >= 10 ? 36 : Params::room_cap;
        if (len >= 10) need += len / 3;
        return std::min(need, cap);
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

    enum class SimStatus { OK, DEAD, DIVE, H2H };
    struct SimResult {
        SimStatus status = SimStatus::DEAD;
        std::vector<int> body;
        int offset = 0;
        int eaten = 0;
        int hit_id = -1;
        int blind_cell = -1;
    };

    SimResult simulate(const World& w, const std::vector<int>& path) const {
        SimResult out;
        out.body = w.body;
        out.offset = w.body_offset;
        if (path.empty()) return out;
        std::unordered_set<int> own(out.body.begin(), out.body.end());
        std::unordered_set<int> eaten_cells;
        for (size_t k = 0; k < path.size(); k++) {
            if (k && static_cast<int>(out.body.size()) + out.offset <= 2) return out;
            int head = out.body.empty() ? w.head : out.body.back();
            int n = w.dest(head, path[k]);
            if (n == UNKNOWN) n = w.nbr(head, path[k]);
            if (n == UNPAIRED) {
                out.status = (k == 0) ? SimStatus::DIVE : SimStatus::DEAD;
                return out;
            }
            if (n < 0) return out;
            if (own.count(n) || (w.own[n] == 255 && n != head)) return out;
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
                if (out.offset > 0) out.offset--;
                else if (!out.body.empty()) {
                    own.erase(out.body.front());
                    out.body.erase(out.body.begin());
                }
            }
            if (k > 0) {
                if (out.offset > 0) out.offset--;
                else if (!out.body.empty()) {
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
        return flood_room(w, sim.body.back(), segs, 0, need, nullptr, 0, sim.offset);
    }

    double threat_cost(const World&, int cell, int length) const {
        (void)length;
        if (cell < 0 || cell >= static_cast<int>(threat_costs.size()) || !danger[cell]) return 0.0;
        return threat_costs[cell];
    }

    Decision decide(World& w) {
        Decision out;
        hear_radio(w);
        prepare_radio(w);
        mark_danger(w);
        if (static_cast<int>(visits.size()) != w.NC) visits.assign(w.NC, 0);
        if (w.rnd % 16 == 0) {
            int n = std::min<int>(64, w.trail.size());
            for (int i = static_cast<int>(w.trail.size()) - n; i < static_cast<int>(w.trail.size()); i++)
                if (visits[w.trail[i]]) visits[w.trail[i]]--;
        }
        if (visits[w.head] < 250) visits[w.head]++;

        // Tyr's initial long-dragon rescue leaves a two-segment decoy.
        if (w.rnd <= Params::opening_rescue_until && w.born <= Params::opening_rescue_until &&
            w.len >= Params::opening_rescue_min_len &&
            static_cast<int>(w.body.size()) < w.len &&
            ((w.me & 4095) < Params::opening_initial_id_limit || w.rnd > w.born) &&
            w.units < w.limit) {
            out.act = Act::SPLIT;
            out.split = w.len - 2;
            out.why = 'r';
            return out;
        }

        bool opening_production = w.rnd >= Params::opening_production_start &&
            w.rnd <= Params::opening_production_until &&
            w.units < Params::opening_production_unit_cap;
        if (should_split(w) && (opening_production || w.rnd > Params::opening_production_until) &&
            split_has_room(w)) {
            out.act = Act::SPLIT;
            out.split = Params::split_child;
            out.why = 's';
            return out;
        }

        build_block_mask(w, mask);
        int cap = (w.rnd - w.born < 2) ? 48 : Params::search_cap;
        if (w.units * 10 >= w.limit * 7) cap = std::min(cap, 40);
        dist(w, w.head, mask, fwd, cap);

        int best = -1;
        int dive_dir = -1;
        char why = '-';
        double best_value = 0.0;
        double previous_value = 0.0;
        for (int c : fwd.order) {
            int steps = fwd.d[c];
            if (steps <= 0) continue;
            double value = cell_value(w, c, steps);
            if (value <= 0.0) continue;
            double score = value * std::pow(Params::target_gamma, steps);
            if (c == previous_target) previous_value = score;
            if (score > best_value) {
                best_value = score;
                best = c;
                dive_dir = -1;
                why = w.pearl_known(c, Params::memory_ttl) ? 'p'
                    : (w.bed[c] == 1 ||
                       (c < static_cast<int>(w.atlas_bed.size()) && w.atlas_bed[c])) ? 'b' : 'x';
            }
        }
        if (w.rnd - w.born >= 3 && !local_crown(w)) {
            for (const auto& dv : fwd.dives) {
                double score = Params::dive_value * std::pow(Params::target_gamma, dv[2]);
                if (score > best_value) {
                    best_value = score;
                    best = dv[0];
                    dive_dir = dv[1];
                    why = 'd';
                }
            }
        }
        if (dive_dir < 0 && previous_target >= 0 && previous_value > 0.0 &&
            previous_target != best && previous_value * Params::target_hysteresis >= best_value) {
            best = previous_target;
            best_value = previous_value;
            why = 'm';
        }
        if (role_feeder && crown_cell >= 0) {
            best = crown_cell;
            best_value = 1.0;
            dive_dir = -1;
            why = 'c';
        }
        // If the bounded search found no field, keep moving toward stale food or
        // an unseen tile instead of idling on a fully surveyed patch.
        if (best < 0) {
            for (int c = 0; c < w.NC; c++) {
                if (c == w.head) continue;
                double value = 0.0;
                if (w.pearl_seen[c] >= 0 && w.rnd - w.pearl_seen[c] <= Params::memory_ttl)
                    value = Params::memory_value * std::pow(Params::target_gamma, w.tdist(w.head, c));
                else if (!w.seen[c])
                    value = Params::unseen_value * std::pow(Params::target_gamma, w.tdist(w.head, c));
                if (value > best_value) {
                    best = c;
                    best_value = value;
                    why = w.pearl_seen[c] >= 0 ? 'p' : 'x';
                }
            }
        }
        if (!role_crown && !role_feeder && prey_id >= 0 && w.rnd >= Params::hunt_from && w.len <= Params::hunt_max_len &&
            w.rnd - prey_round <= Params::prey_ttl) {
            int steps = fwd.d[prey_cell] >= 0 ? fwd.d[prey_cell] : w.tdist(w.head, prey_cell) + 2;
            double score = Params::hunt_value * std::min(prey_len, 40) * std::pow(Params::target_gamma, steps);
            if (score > best_value) { best = prey_cell; best_value = score; dive_dir = -1; why = 'h'; }
        }
        previous_target = best;
        previous_target_value = best_value;
        previous_dive_dir = dive_dir;
        int normal_target = best;
        if (plan_escape(w, normal_target, best)) why = 'e';
        out.target = best;
        out.why = why;

        int pref = best >= 0 && best < static_cast<int>(fwd.first.size()) ? fwd.first[best] : -1;
        if (best == w.head && dive_dir >= 0) pref = dive_dir;
        bool route_good[4] = {false, false, false, false};
        if (best >= 0 && best != w.head) {
            int nb[4];
            for (int d = 0; d < 4; d++) nb[d] = w.dest(w.head, d);
            rev_dist(w, best, rev, std::max(cap, 72), 1 << 30, nb, 4);
            if (rev.d[w.head] >= 0) {
                for (int d = 0; d < 4; d++) {
                    int n = w.step_opt(w.head, d);
                    route_good[d] = n >= 0 && rev.d[n] == rev.d[w.head] - 1;
                }
            } else {
                int waypoint = -1, waypoint_cost = 1 << 30;
                for (int c : fwd.order) {
                    if (fwd.d[c] <= 0) continue;
                    int cost = 3 * w.tdist(c, best) + fwd.d[c];
                    if (cost < waypoint_cost) { waypoint_cost = cost; waypoint = c; }
                }
                if (waypoint >= 0 && fwd.first[waypoint] >= 0)
                    route_good[static_cast<int>(fwd.first[waypoint])] = true;
            }
        }

        if (role_feeder && crown_id >= 0) {
            for (int pi : w.ally_heads) {
                const Part& a = w.parts[pi];
                if ((a.id & 4095) != crown_id || w.tdist(w.head, a.cell) > Params::feed_dist) continue;
                int back = (w.face + 2) & 3;
                if (simulate(w, {back}).status == SimStatus::DEAD) {
                    out.dirs = {back}; out.why = 'f'; out.target = crown_cell;
                    return out;
                }
            }
        }

        bool near_threat = false;
        for (int pi : w.enemy_heads)
            if (w.cheb(w.parts[pi].cell, w.head) <= 4) { near_threat = true; break; }
        std::vector<std::vector<int>> paths;
        for (int d = 0; d < 4; d++) paths.push_back({d});
        int sprint_limit = Params::sprint3_limit;
        if (w.units * 10 >= w.limit * 7) sprint_limit = Params::sprint3_saturated_limit;
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

        int best_tier = -1;
        double best_score = -std::numeric_limits<double>::infinity();
        std::vector<int> best_path{w.face};
        double lv = lv_now(w);
        for (const auto& path : paths) {
            SimResult sim = simulate(w, path);
            int tier = T_ILLEGAL;
            int room_n = 0;
            double score = -1000.0;
            int steps = static_cast<int>(path.size());
            int first = path.front();
            int final_head = sim.body.empty() ? w.head : sim.body.back();
            bool attack = false;

            if (sim.status == SimStatus::DIVE) {
                tier = (first == pref && why == 'd' && steps == 1) ? T_SAFE : T_DIVE;
                score = Params::dive_base - Params::p_dive * dragon_value(w, w.len);
                if (first == pref) score += Params::dive_value * 0.5;
                if (escape_active) score += Params::escape_portal_bonus *
                    std::pow(Params::escape_decay, std::max(0, w.rnd - escape_start));
            } else if (sim.status == SimStatus::H2H) {
                auto it = w.mem.find(sim.hit_id);
                int enemy_len = it == w.mem.end() ? 1 : std::max(1, it->second.vis_len);
                int support = 0;
                for (int ai : w.ally_heads)
                    if (w.tdist(w.parts[ai].cell, w.head) <= 3) support++;
                double gain = dragon_value(w, enemy_len) - dragon_value(w, w.len) -
                    Params::sprint_cost * (steps - 1) + 0.5 * std::min(support, 2);
                if (w.units >= Params::attack_min_units && gain >= Params::attack_margin) {
                    attack = true;
                    tier = T_SAFE;
                    score = 2.0 + gain;
                } else {
                    tier = T_DANGER;
                    score = -950.0;
                }
            } else if (sim.status == SimStatus::OK) {
                int final_len = w.len + sim.eaten - (steps - 1);
                if (final_len < 2) continue;
                Room rr = room_for_body(w, sim, room_need(final_len));
                room_n = rr.cells;
                bool cramped = !rr.escape && room_n < room_need(final_len);
                bool threatened = danger[final_head];
                tier = threatened ? (cramped ? T_DANGER_CRAMP : T_DANGER)
                                  : (cramped ? T_CRAMP : T_SAFE);
                int progress = route_good[first] ? 1 : -1;
                score = Params::goal_weight * progress * (steps == 1 ? 1.0 : 0.7);
                score += lv * (final_len - w.len) - Params::sprint_cost * (steps - 1);
                score += 0.5 * sim.eaten;
                score += Params::momentum_weight * momentum[first];
                score += escape_action_bonus(w, final_head, first);
                score += devil_center_bonus(w, final_head);
                score += devil_lane_bonus(w, final_head);
                score -= ally_body_buffer(w, final_head);
                if (role_feeder && crown_id >= 0) {
                    for (const Part& part : w.parts) {
                        if (!part.ally || (part.id & 4095) != crown_id) continue;
                        if (w.tdist(part.cell, final_head) == 1) { score -= 3.0; break; }
                    }
                }
                if (sim.blind_cell >= 0) score -= Params::blind_landing_penalty;
                score -= threat_cost(w, final_head, final_len);
                int md = 99;
                for (int pi : w.enemy_heads)
                    md = std::min(md, w.tdist(final_head, w.parts[pi].cell));
                if (md <= Params::enemy_near)
                    score -= Params::enemy_near_penalty * (Params::enemy_near + 1 - md);
                for (int pi : w.ally_heads) {
                    int dd = w.tdist(w.parts[pi].cell, final_head);
                    if (dd <= 2) score -= Params::crowd_weight * (3 - dd);
                }
                if (final_head < static_cast<int>(visits.size()))
                    score -= Params::visit_weight * visits[final_head];
                if (w.bed[final_head] == 1 && w.spawn_at[final_head] == w.rnd + 1)
                    score -= Params::w_bed_block;
                if (cramped) {
                    int final_need = room_need(final_len);
                    double penalty = Params::trap_weight *
                        std::max(0.0, static_cast<double>(final_need - room_n) / std::max(1, final_need));
                    if (room_n < final_len) penalty += Params::trap_weight;
                    double penalty_scale = dragon_value(w, final_len) / Params::trap_value_reference;
                    if (penalty_scale > 1.0) penalty *= penalty_scale;
                    bool farm_escape = final_len + rr.pearls >= Params::split_min_len &&
                        final_len + rr.pearls > room_n + 1 && w.units < w.limit;
                    if (farm_escape) penalty *= Params::trap_farm_factor;
                    score -= penalty;
                }
            }

            (void)attack;
#ifdef ARES_DEBUG
            fprintf(stderr, "r%d path=%s tier=%d score=%.2f room=%d attack=%d\n",
                    w.rnd, [&]() { static char b[8]; int i=0; for (int d : path) b[i++]=dir_char(d); b[i]=0; return b; }(),
                    tier, score, room_n, int(attack));
#endif
            if (tier > best_tier || (tier == best_tier && score > best_score)) {
                best_tier = tier;
                best_score = score;
                best_path = path;
            }
        }
        out.tier = best_tier;
        out.dirs = best_path;

        // All immediate moves are fatal: shed the rear as an escape child.
        if (best_tier == T_ILLEGAL && Params::split_when_trapped) {
            int size = emergency_split_size(w);
            if (size >= unswbc::Constants::MIN_SIZE &&
                w.len - size >= unswbc::Constants::MIN_SIZE) {
                out.act = Act::SPLIT;
                out.split = size;
                out.why = 't';
                return out;
            }
        }

        if (best_tier >= T_DIVE && !best_path.empty()) {
            int first = best_path.front();
            for (double& m : momentum) m *= Params::momentum_decay;
            momentum[first] += 1.0 - Params::momentum_decay;
        }
        return out;
    }
};

}  // namespace ares
