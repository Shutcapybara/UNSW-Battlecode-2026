// Tyr V12 policy parameters on the Anna A02 C++ chassis. Keep tunables
// together so this snapshot can be reviewed and reproduced.
//
// Override at build time with -DANNA_<NAME>=value is deliberately not wired:
// a variant is a new bot directory with an edited copy of this file, so the
// measured source is always the shipped source.
#pragma once

namespace ares {

struct Params {
    // ---------------------------------------------------------------- split
    // Split only while length >= this (child 2 + parent >= 2).
    static constexpr int split_min_len = 4;
    // Child size taken from the rear.
    static constexpr int split_child = 2;
    // Split only in rounds strictly before this.
    static constexpr int split_until_round = 380;
    // Do not split (the parent stands still for a turn) while an enemy head is
    // within this Chebyshev distance of our head.

    // -------------------------------------------------------------- targets
    // A remembered pearl we cannot currently see is trusted for this many rounds.
    static constexpr int pearl_ttl = 40;
    // A bed is a target if its pearl will exist when we land on it:
    // spawn_round <= arrival_round + bed_wait_max. 0 = "ripe by arrival".
    static constexpr int bed_wait_max = 0;
    // Tie-break in path steps: a pearl on the ground beats a bed at equal cost.
    // Costs are compared as steps * 4 + (bed ? bed_tie : 0).
    static constexpr int bed_tie = 1;
    // Skip a visible pearl when a visible ally head is strictly nearer to it
    // (torus Manhattan). 0 disables.
    static constexpr int ally_yield = 1;
    // Exploring: an unpaired portal (landing unknown) costs this many extra
    // steps compared with walking to the nearest never-seen cell.
    static constexpr int dive_cost = 4;
    // No ordinary exploring dive in the first rounds of a dragon's life.
    static constexpr int dive_min_age = 3;
    // When there is no fresh pearl target, scout a reachable unpaired portal
    // ahead of ordinary unseen ground. Known pearl and bed targets still win.
    static constexpr double no_pearl_dive_target_value = 6.0;
    // A split child that receives a known portal edge follows it promptly, then
    // drops the waypoint after crossing or timeout.
    static constexpr int newborn_portal_handoff_age = 1;
    static constexpr int newborn_portal_route_turns = 12;
    static constexpr double newborn_portal_commit_bonus = 20.0;
    // Score penalty for a step whose landing (through a paired portal) is out
    // of view: terrain remembered, occupancy unknown. 16 = one path step.
    static constexpr int blind_landing_penalty = 8;
    // First target-search pass stops at this depth; a second whole-map pass
    // runs only if the first finds no pearl, bed, unseen cell or dive.
    static constexpr int search_depth1 = 20;
    // BFS horizon (cells expanded) for target search; the whole map if larger.
    static constexpr int search_cap = 256; // Robert V01 deeper bounded target search
    static constexpr int search_cap_saturated = 96;
    static constexpr int search_cap_born = 80;
    static constexpr int frontier_search_depth = 6;
    static constexpr int search_cap_late_from = 40;
    static constexpr int search_cap_late = 48;
    static constexpr int search_cap_sparse_from = 150;
    static constexpr int search_cap_sparse_units = 20;
    static constexpr int search_cap_sparse = 64;

    // ------------------------------------------------------------- blocking
    // Another dragon's visible segment blocks planning paths while depth < this
    // (it will usually have moved on by then).
    static constexpr int other_block_t = 99;
    // A visible chain whose rear sits on the view rim is assumed to continue
    // for this many hidden segments (they vacate later).
    static constexpr int hidden_tail = 6;

    // ------------------------------------------------------ Tyr V01/V12 policy
    static constexpr int opening_production_start = 1;
    static constexpr int opening_production_until = 30;
    static constexpr int opening_production_unit_cap = 32;
    static constexpr int opening_rescue_until = 1;
    static constexpr int opening_rescue_min_len = 8;
    static constexpr int opening_initial_id_limit = 6;
    static constexpr double opening_rescue_value = 8.0;
    static constexpr double opening_production_value = 8.0;
    static constexpr int sprint3_limit = 12; // restore the longer Tyr V09/V10 candidate horizon
    static constexpr int sprint3_saturated_limit = 4;
    static constexpr int sprint3_late_from = 150;
    static constexpr int sprint3_late_limit = 5;
    static constexpr int sprint3_sparse_limit = 8;
    static constexpr double split_value = 8.0;
    static constexpr double material_unit_value = 3.0;
    static constexpr double lv_end = 3.0;
    static constexpr int grow_from = 380;
    static constexpr double target_gamma = 0.93;
    static constexpr double pearl_value = 10.0;
    static constexpr double memory_value = 6.0;
    static constexpr double bed_value = 8.0;
    static constexpr double bed_wait = 0.0; // Tyr V12 active override.py
    static constexpr int bed_stale = 60;
    static constexpr double unseen_value = 5.0;
    static constexpr double dive_value = 3.0; // Tyr V12 active override.py
    static constexpr double dive_base = -0.5;
    static constexpr double p_dive = 0.1;
    static constexpr int memory_ttl = 40;
    static constexpr double own_target_discount = 0.15;
    static constexpr double enemy_target_discount = 0.60;
    static constexpr double target_hysteresis = 1.25;
    static constexpr double momentum_weight = 0.6;
    static constexpr double momentum_decay = 0.6;
    static constexpr int visit_ttl_count = 32;
    static constexpr double visit_weight = 0.15;
    static constexpr double goal_weight = 1.2;
    // One extra move consumes one segment, represented by simulated body loss.
    static constexpr int pearl_denial_radius = 2;
    // Without a nearby rival, taking a pearl on a dash gives up its later
    // growth opportunity. Keep that future-economy cost small.
    static constexpr double uncontested_sprint_pearl_cost = 0.25;
    static constexpr double crowd_weight = 0.6;
    static constexpr double trap_weight = 30.0;
    static constexpr double trap_farm_factor = 0.15;
    static constexpr double trap_value_reference = 8.0;
    static constexpr double w_bed_block = 0.5;
    static constexpr double threat_long = 0.9;
    static constexpr double threat_equal = 0.7;
    static constexpr double threat_short = 0.1;
    static constexpr double threat_sprint_factor = 0.8;
    static constexpr double threat_weight = 1.0;
    static constexpr double threat_ally_support = 0.25; // Fafnir size-matched counter-threat support
    static constexpr int threat_support_radius = 3;
    static constexpr double threat_enemy_loss_weight = 0.5;
    static constexpr double threat_base = 1.0;
    static constexpr double attack_margin = 0.5;
    static constexpr int attack_min_units = 3;
    static constexpr double devil_center_weight = 2.8;
    static constexpr int devil_center_until = 42;
    static constexpr double devil_lane_weight = 0.75;
    static constexpr int devil_lane_until = 100;
    static constexpr double devil_ally_body_weight = 2.5;
    static constexpr double w_flank = 3.0;
    static constexpr int density_radius = 7;
    static constexpr int density_half_life = 4;
    static constexpr int density_ttl = 16;
    static constexpr int density_sources = 32;
    static constexpr double density_ally_weight = 0.10; // Tyr V12 active override.py
    static constexpr double density_enemy_weight = 0.40;
    static constexpr int gossip_trust = 8;
    static constexpr int gossip_horizon = 30;
    static constexpr int crown_ttl = 20;
    static constexpr int crown_margin = 3;
    static constexpr int crown_claim_spread = 120;
    static constexpr int crown_claim_len = 3;
    static constexpr int feed_base = 40;
    static constexpr double feed_k = 0.6;
    static constexpr int feed_dist = 4;
    static constexpr int feed_min_crown = 4;
    static constexpr int feed_range = 16;
    static constexpr int prey_ttl = 15;
    static constexpr int prey_min = 8;
    static constexpr int cut_extra = 1;
    static constexpr int prey_cut_extra = 2;
    static constexpr int blind_fresh = 12;
    static constexpr double blind_body = 1.0;
    static constexpr double blind_seen = 0.15;
    static constexpr double blind_unseen = 0.15; // Tyr V12 active override.py
    static constexpr int hunt_from = 200;
    static constexpr int hunt_max_len = 5;
    static constexpr double hunt_value = 1.0;
    static constexpr int escape_spawn_area = 11;
    static constexpr int escape_spawn_branches = 1;
    static constexpr int escape_handoff_retries = 2;
    static constexpr int escape_max_turns = 18;
    static constexpr int escape_target_depth = 12;
    static constexpr int escape_target_nodes = 120;
    static constexpr int escape_origin_depth = 18;
    static constexpr int escape_origin_nodes = 180;
    static constexpr int escape_min_distance = 5;
    static constexpr int escape_open_area = 8;
    static constexpr double escape_open_weight = 1.6;
    static constexpr double escape_branch_weight = 2.5;
    static constexpr double escape_exit_weight = 1.0;
    static constexpr double escape_distance_weight = 0.7;
    static constexpr double escape_resource_weight = 0.18;
    static constexpr double escape_route_cost = 0.85;
    static constexpr double escape_waypoint_hysteresis = 2.5;
    static constexpr double escape_route_weight = 3.5;
    static constexpr double escape_push = 2.2;
    static constexpr double escape_decay = 0.91;
    static constexpr double escape_origin_cost = 2.0;
    static constexpr int escape_parent_radius = 4;
    static constexpr double escape_parent_cost = 1.2;
    static constexpr int escape_valuable_distance = 2;
    static constexpr double escape_valuable_threshold = 8.0;
    static constexpr int escape_resource_pause_budget = 6;
    static constexpr double escape_portal_bonus = 1.5;
    static constexpr double escape_revisit_weight = 1.4;

    // ---------------------------------------------------------- Tyr V12 flood
    static constexpr int slack = 3;
    static constexpr int min_area = 5;
    static constexpr int flood_cap = 32; // deeper room valuation, still bounded
    static constexpr int flood_cap_long = 48;
    static constexpr int flood_cap_late_from = 150;
    static constexpr int flood_cap_long_late = 24;
    static constexpr int flood_cap_long_sparse = 32;
    static constexpr int flood_credit = 2;
    static constexpr int flood_portal_credit = 6;
    static constexpr int child_area = 4;
    static constexpr int head_block = 0;

    // ------------------------------------------------------- enclosure escape
    static constexpr int enclosure_reach_steps = 5;
    static constexpr int enclosure_critical_cells = 8;

    // ----------------------------------------------------------- tie-breaks
    // Score bonus for keeping the current facing (anti-dither), in score units
    // where one path step toward the target = 16.
    static constexpr int keep_facing_bonus = 2;

    // ------------------------------------------------------------ debugging
    // Emit an INDICATOR line per turn (costs ~4k points per byte).
    static constexpr bool indicator = false;
};

}  // namespace ares
