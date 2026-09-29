// anna-a01-chassis parameters. One place for every tunable; each has a default
// and a comment. Other tasks append their own block at the bottom.
//
// Override at build time with -DANNA_<NAME>=value is deliberately not wired:
// a variant is a new bot directory with an edited copy of this file, so the
// measured source is always the shipped source.
#pragma once

namespace anna {

struct Params {
    // ---------------------------------------------------------------- split
    // Split only while length >= this (child 2 + parent >= 2).
    static constexpr int split_min_len = 4;
    // Child size taken from the rear.
    static constexpr int split_child = 2;
    // Split only in rounds strictly before this.
    static constexpr int split_until_round = 100;
    // Do not split (the parent stands still for a turn) while an enemy head is
    // within this Chebyshev distance of our head.
    static constexpr int split_enemy_cheb = 2;

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
    // No exploring dive in the first rounds of a dragon's life.
    static constexpr int dive_min_age = 3;
    // Score penalty for a step whose landing (through a paired portal) is out
    // of view: terrain remembered, occupancy unknown. 16 = one path step.
    static constexpr int blind_landing_penalty = 8;
    // First target-search pass stops at this depth; a second whole-map pass
    // runs only if the first finds no pearl, bed, unseen cell or dive.
    static constexpr int search_depth1 = 16;
    // BFS horizon (cells expanded) for target search; the whole map if larger.
    static constexpr int search_cap = 4096;

    // ------------------------------------------------------------- blocking
    // Another dragon's visible segment blocks planning paths while depth < this
    // (it will usually have moved on by then).
    static constexpr int other_block_t = 4;
    // A visible chain whose rear sits on the view rim is assumed to continue
    // for this many hidden segments (they vacate later).
    static constexpr int hidden_tail = 4;

    // --------------------------------------------------------------- safety
    // Room check after a candidate move: the time-aware flood must reach
    // need = min(room_cap, max(len + room_margin, room_len_mult * len, room_min))
    // cells, or reach one of our own vacated segments (tail chase = a cycle),
    // otherwise the move is "cramped". A 1-wide dead end fails this test.
    static constexpr int room_margin = 2;
    static constexpr int room_len_mult = 2;
    static constexpr int room_min = 10;
    // The room flood walks known terrain only; a reached cell with an unknown
    // edge credits unknown_credit cells (a corridor we cannot see the end of is
    // not free room), one with an unpaired portal portal_credit.
    static constexpr int unknown_credit = 4;
    static constexpr int portal_credit = 2;
    // Cap on the flood (cells) for the room check.
    static constexpr int room_cap = 64;
    // When every step is certain death, split instead (legal, head stays put).
    static constexpr bool split_when_trapped = true;
    // A split needs the child's flood (from our tail) to reach this many cells.
    static constexpr int split_room_min = 10;
    // In the room flood, cells next to any other head (ally or enemy) are
    // blocked for depth <= head_block (it may step there before we do).
    static constexpr int head_block = 1;
    // Enemy head reach in steps used for danger (1 = its next single step).
    static constexpr int enemy_reach = 1;
    // ... extended to its sprint reach, min(visible length - 1, enemy_reach_max).
    static constexpr int enemy_reach_max = 2;

    // Keep clear of enemy heads: a step landing within enemy_near (torus
    // Manhattan) of one loses enemy_near_penalty per step of closeness.
    static constexpr int enemy_near = 3;
    static constexpr int enemy_near_penalty = 6;

    // ----------------------------------------------------------- tie-breaks
    // Score bonus for keeping the current facing (anti-dither), in score units
    // where one path step toward the target = 16.
    static constexpr int keep_facing_bonus = 2;

    // ------------------------------------------------------------ debugging
    // Emit an INDICATOR line per turn (costs ~4k points per byte).
    static constexpr bool indicator = false;

    // ================================================================ C1-B router
    // (cx-b01-router). Everything below keys on structure measured in play:
    // tile count NC = W*H (turn 1), beds and spawn gaps seen, units, visible
    // dragons. No map identity anywhere.
#ifndef CX_ATLAS
#define CX_ATLAS 0
#endif
    // Hard switch for the public-map atlas (out-of-sample rule 2). Build the
    // atlas-off twin with tools/cx/variant.py ... CX_ATLAS=0.
    static constexpr bool atlas_enabled = CX_ATLAS != 0;
    // Master switch: false = the chassis cheap policy (for A/B inside one binary).
    static constexpr bool router = true;

    // --- horizon and frugality: functions of tile count
    // Planning horizon (steps) = clamp(horizon_k * sqrt(NC), horizon_min, horizon_max).
    static constexpr double horizon_k = 1.0;
    static constexpr int horizon_min = 20;
    static constexpr int horizon_max = 60;
    // Beds valued per turn: the nearest bed_cap_small on maps up to 1200 tiles,
    // bed_cap_large above; allies in the assignment: the nearest ally_cap.
    static constexpr int bed_cap_small = 64;
    static constexpr int bed_cap_large = 40;
    static constexpr int big_map_tiles = 1200;
    static constexpr int ally_cap = 6;

    // --- bed valuation
    // Discount per step of delay (value of a pearl eaten t steps from now = disc^t).
    static constexpr double disc = 0.95;
    // Weight of a pearl event after the enemy's earliest arrival (enemy conservatism:
    // 0 = ignore the enemy, 1 = the enemy always takes it first).
    static constexpr double enemy_conservatism = 0.7;
    // Enemy heads remembered for this many rounds as arrival sources.
    static constexpr int enemy_mem_ttl = 8;
    // Respawn gap when none has been observed at a bed: observed mean if any,
    // else the atlas bed class, else default_gap.
    static constexpr int default_gap = 24;
    // A bed never seen with a countdown (atlas only) holds a pearl with this probability.
    static constexpr double unseen_bed_p = 0.3;
    // ... blended with the share observed in play (prior weight in beds).
    static constexpr double unseen_prior_n = 5.0;
    // Cluster: beds within cluster_r (torus Manhattan) add cluster_w of their value.
    static constexpr int cluster_r = 2;
    static constexpr double cluster_w = 0.6;
    // A pearl on the ground: value multiplier (certain now vs predicted).
    static constexpr double pearl_w = 1.2;

    // --- assignment and spacing
    // Our previous target's cluster keeps a value bonus (anti-dither).
    static constexpr double target_hysteresis = 1.3;
    // Two own dragons' targets must be at least spacing_r apart (torus Manhattan).
    static constexpr int spacing_r = 3;
    // A target this close to a visible ally head (and nearer to it) goes to the ally.
    static constexpr int ally_claim_r = 2;

    // --- crowding (the Schooltime pockets: own swarms box themselves in)
    // Target value divided by 1 + crowd_w * (parts within 2 of the bed, heads x2).
    static constexpr double crowd_w = 0.0;
    // No split while more than this many other heads are within 3.
    static constexpr int split_crowd_max = 99;
    // Room need grows by this per other head within 2 of the landing cell.
    static constexpr int crowd_room_k = 0;

    // --- movement
    // Patrol: an early dragon keeps its distance to the bed equal to the time
    // left before the spawn, capped at patrol_r (it circles, eats on spawn).
    static constexpr int patrol_r = 3;
    // Score units: 16 = one step of distance.
    // Penalty for stepping onto the bed before it spawns (blocks the spawn).
    static constexpr int early_on_bed_pen = 24;
    // De-convergence: penalty for a step onto a cell an ally's planned path
    // uses within deconv_k steps (x deconv_w, decaying with time).
    static constexpr int deconv_k = 6;
    static constexpr int deconv_w = 12;
    // Dead ends (cells peeled from the terrain's 2-core): per unit of depth.
    static constexpr int dead_end_pen = 10;
    // Enter a dead-end tree only if the pearls expected inside reach this.
    static constexpr double dead_end_min_value = 3.0;
    // A bed inside a tree counts if it ripens within its depth + this many rounds
    // (a dragon can wait at the mouth, not inside).
    static constexpr int tree_ripe_slack = 8;

    // --- splits (pearl-gated)
    static constexpr int split_len = 4;          // split the moment length reaches this
    static constexpr int split_round_max = 200;  // early game only (no crown logic here)
    // No split unless the child (head at our tail) has a target it reaches
    // first within the horizon; forced anyway at split_force_len.
    static constexpr bool split_needs_target = true;
    static constexpr int split_force_len = 7;
    // Trapped (every step is death): split so the child (from the tail) gets
    // len - 2 segments.
    static constexpr bool trapped_big_child = true;
    // Blind landing through a paired portal: SAFE when it is the route's first
    // step and the landing room check passes.
    static constexpr bool portal_route_safe = true;
    // ... and only if the landing cell has this many open sides (not a pocket;
    // its occupants are unknown) and lies outside every dead-end tree.
    static constexpr int blind_landing_min_exits = 2;
};

}  // namespace anna
