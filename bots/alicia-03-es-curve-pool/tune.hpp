// Alicia (RL-1) runtime parameter override, local training only.
//
// ALICIA_PARAMS="name=value;name=value" overrides the exposed Params fields at
// boot. Unset (and in the tournament sandbox, which passes no environment) the
// compiled-in defaults in params.hpp are used, so the shipped path is the
// constants path. Unknown names or unparsable values abort with exit 3, so a
// typo in a training run cannot silently play the defaults.
#pragma once

#include <cstdlib>
#include <cstring>
#include <string>

#include "params.hpp"

namespace ares {

struct TuneEntry {
    const char* name;
    bool is_int;
    int* i;
    double* d;
};

inline const TuneEntry* tune_table(int& n) {
    static const TuneEntry table[] = {
        {"split_min_len", true, &Params::split_min_len, nullptr},
        {"split_until_round", true, &Params::split_until_round, nullptr},
        {"pearl_ttl", true, &Params::pearl_ttl, nullptr},
        {"dive_cost", true, &Params::dive_cost, nullptr},
        {"blind_landing_penalty", true, &Params::blind_landing_penalty, nullptr},
        {"search_cap", true, &Params::search_cap, nullptr},
        {"search_cap_saturated", true, &Params::search_cap_saturated, nullptr},
        {"search_cap_born", true, &Params::search_cap_born, nullptr},
        {"search_cap_late_from", true, &Params::search_cap_late_from, nullptr},
        {"search_cap_late", true, &Params::search_cap_late, nullptr},
        {"search_cap_sparse", true, &Params::search_cap_sparse, nullptr},
        {"opening_rescue_value", false, nullptr, &Params::opening_rescue_value},
        {"opening_production_value", false, nullptr, &Params::opening_production_value},
        {"sprint3_limit", true, &Params::sprint3_limit, nullptr},
        {"sprint3_late_limit", true, &Params::sprint3_late_limit, nullptr},
        {"sprint3_sparse_limit", true, &Params::sprint3_sparse_limit, nullptr},
        {"split_value", false, nullptr, &Params::split_value},
        {"material_unit_value", false, nullptr, &Params::material_unit_value},
        {"lv_end", false, nullptr, &Params::lv_end},
        {"target_gamma", false, nullptr, &Params::target_gamma},
        {"pearl_value", false, nullptr, &Params::pearl_value},
        {"memory_value", false, nullptr, &Params::memory_value},
        {"bed_value", false, nullptr, &Params::bed_value},
        {"bed_wait", false, nullptr, &Params::bed_wait},
        {"bed_stale", true, &Params::bed_stale, nullptr},
        {"unseen_value", false, nullptr, &Params::unseen_value},
        {"dive_value", false, nullptr, &Params::dive_value},
        {"dive_base", false, nullptr, &Params::dive_base},
        {"p_dive", false, nullptr, &Params::p_dive},
        {"memory_ttl", true, &Params::memory_ttl, nullptr},
        {"own_target_discount", false, nullptr, &Params::own_target_discount},
        {"enemy_target_discount", false, nullptr, &Params::enemy_target_discount},
        {"target_hysteresis", false, nullptr, &Params::target_hysteresis},
        {"momentum_weight", false, nullptr, &Params::momentum_weight},
        {"momentum_decay", false, nullptr, &Params::momentum_decay},
        {"visit_weight", false, nullptr, &Params::visit_weight},
        {"goal_weight", false, nullptr, &Params::goal_weight},
        {"sprint_cost", false, nullptr, &Params::sprint_cost},
        {"crowd_weight", false, nullptr, &Params::crowd_weight},
        {"trap_weight", false, nullptr, &Params::trap_weight},
        {"trap_farm_factor", false, nullptr, &Params::trap_farm_factor},
        {"trap_value_reference", false, nullptr, &Params::trap_value_reference},
        {"w_bed_block", false, nullptr, &Params::w_bed_block},
        {"threat_long", false, nullptr, &Params::threat_long},
        {"threat_equal", false, nullptr, &Params::threat_equal},
        {"threat_short", false, nullptr, &Params::threat_short},
        {"threat_sprint_factor", false, nullptr, &Params::threat_sprint_factor},
        {"threat_weight", false, nullptr, &Params::threat_weight},
        {"threat_ally_support", false, nullptr, &Params::threat_ally_support},
        {"threat_support_radius", true, &Params::threat_support_radius, nullptr},
        {"threat_enemy_loss_weight", false, nullptr, &Params::threat_enemy_loss_weight},
        {"threat_base", false, nullptr, &Params::threat_base},
        {"attack_margin", false, nullptr, &Params::attack_margin},
        {"attack_min_units", true, &Params::attack_min_units, nullptr},
        {"devil_center_weight", false, nullptr, &Params::devil_center_weight},
        {"devil_lane_weight", false, nullptr, &Params::devil_lane_weight},
        {"devil_ally_body_weight", false, nullptr, &Params::devil_ally_body_weight},
        {"w_flank", false, nullptr, &Params::w_flank},
        {"density_radius", true, &Params::density_radius, nullptr},
        {"density_half_life", true, &Params::density_half_life, nullptr},
        {"density_ally_weight", false, nullptr, &Params::density_ally_weight},
        {"density_enemy_weight", false, nullptr, &Params::density_enemy_weight},
        {"crown_margin", true, &Params::crown_margin, nullptr},
        {"feed_base", true, &Params::feed_base, nullptr},
        {"feed_k", false, nullptr, &Params::feed_k},
        {"feed_dist", true, &Params::feed_dist, nullptr},
        {"blind_body", false, nullptr, &Params::blind_body},
        {"blind_seen", false, nullptr, &Params::blind_seen},
        {"blind_unseen", false, nullptr, &Params::blind_unseen},
        {"hunt_from", true, &Params::hunt_from, nullptr},
        {"hunt_value", false, nullptr, &Params::hunt_value},
        {"escape_open_weight", false, nullptr, &Params::escape_open_weight},
        {"escape_branch_weight", false, nullptr, &Params::escape_branch_weight},
        {"escape_exit_weight", false, nullptr, &Params::escape_exit_weight},
        {"escape_distance_weight", false, nullptr, &Params::escape_distance_weight},
        {"escape_resource_weight", false, nullptr, &Params::escape_resource_weight},
        {"escape_route_cost", false, nullptr, &Params::escape_route_cost},
        {"escape_waypoint_hysteresis", false, nullptr, &Params::escape_waypoint_hysteresis},
        {"escape_route_weight", false, nullptr, &Params::escape_route_weight},
        {"escape_push", false, nullptr, &Params::escape_push},
        {"escape_decay", false, nullptr, &Params::escape_decay},
        {"escape_origin_cost", false, nullptr, &Params::escape_origin_cost},
        {"escape_parent_cost", false, nullptr, &Params::escape_parent_cost},
        {"escape_valuable_threshold", false, nullptr, &Params::escape_valuable_threshold},
        {"escape_portal_bonus", false, nullptr, &Params::escape_portal_bonus},
        {"escape_revisit_weight", false, nullptr, &Params::escape_revisit_weight},
        {"flood_cap", true, &Params::flood_cap, nullptr},
        {"flood_cap_long", true, &Params::flood_cap_long, nullptr},
        {"keep_facing_bonus", true, &Params::keep_facing_bonus, nullptr},
    };
    n = (int)(sizeof(table) / sizeof(table[0]));
    return table;
}

inline void load_param_overrides() {
    const char* env = std::getenv("ALICIA_PARAMS");
    if (!env || !*env) return;
    std::string s(env);
    int n = 0;
    const TuneEntry* t = tune_table(n);
    size_t pos = 0;
    while (pos < s.size()) {
        size_t end = s.find(';', pos);
        if (end == std::string::npos) end = s.size();
        std::string kv = s.substr(pos, end - pos);
        pos = end + 1;
        if (kv.empty()) continue;
        size_t eq = kv.find('=');
        if (eq == std::string::npos) std::exit(3);
        std::string k = kv.substr(0, eq), v = kv.substr(eq + 1);
        char* stop = nullptr;
        double x = std::strtod(v.c_str(), &stop);
        if (stop == v.c_str() || *stop) std::exit(3);
        bool found = false;
        for (int i = 0; i < n; i++) {
            if (k != t[i].name) continue;
            if (t[i].is_int) *t[i].i = (int)(x < 0 ? x - 0.5 : x + 0.5);
            else *t[i].d = x;
            found = true;
            break;
        }
        if (!found) std::exit(3);
    }
}

}  // namespace ares
