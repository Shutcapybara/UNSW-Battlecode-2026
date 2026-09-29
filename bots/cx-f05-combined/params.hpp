// anna-a01-chassis parameters. One place for every tunable; each has a default
// and a comment. Other tasks append their own block at the bottom.
//
// Override at build time with -DANNA_<NAME>=value is deliberately not wired:
// a variant is a new bot directory with an edited copy of this file, so the
// measured source is always the shipped source.
#pragma once

namespace anna {

struct Params {
    // ---------------------------------------------------------------- atlas
    // Terrain atlas of the public maps, matched on the first view. The
    // out-of-sample rule (29 Sep) makes it a switch: the bot with this off
    // must be complete and measured on the generalisation panel.
    static constexpr bool ATLAS_ENABLED = true;

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

    // ------------------------------------------------ C1-F fix 2: portal exit discipline
    // C1-D: we die at 28.2 deaths per 100 portal steps (team 306: 12.5);
    // 623 wall+self deaths within two rounds of a transit in 35 games vs 2;
    // 548 same-pair friendly double deaths. Rules, each ablatable:
    //  (a) exit memory per pair (survived transit = exit verified clear;
    //      exit seen blocked = pair bad for f2_block_ttl rounds)
    //  (b) sonar probe along the entry direction the turn before a blind
    //      transit; transit only on a clean echo (no dragons, no kelp on the
    //      far line) — echoes arrive the turn after the ray
    //  (c) id parity: enter via the pair's lower edge key on rounds where
    //      (round + id) % 2 == 0, via the higher key on odd rounds
    //  (d) exit-cell simulation in id order: no transit when a lower-id head
    //      (move order) is adjacent to the landing now or was within 2 rounds
    // A visible, free landing or a fresh verified-clear memory needs no probe.
    // Discipline yields only when every other step is certain death.
    // Measured configuration (see findings): every transit-gating variant
    // (full / confident / swarmwise / memory-only) was a volume throttle with
    // no per-step safety gain, and confidence-only was bit-identical to the
    // chassis. The gates ship OFF; the memory + probe plumbing + exit_known()
    // stay for C1-B's router.
    static constexpr bool f2_portal = false;
    static constexpr int f2_exit_fresh = 8;    // rounds a survived/verified exit stays trusted
    static constexpr int f2_block_ttl = 6;     // rounds a seen-blocked exit bans the pair
    static constexpr bool f2_probe = false;
    static constexpr bool f2_parity = false;
    static constexpr bool f2_id_sim = false;
    static constexpr int f2_id_sim_dist = 1;   // lower-id head within this tdist of the landing blocks

    // ------------------------------------------------ C1-F fix 3: sprint discipline
    // The chassis never sprints (sprint/pearl = 0); our live submissions grew
    // it to 0.029-0.044 length per pearl — the only pooled outside-band effort
    // leak. A k-step sprint costs k-1 segments, so it pays only when it wins a
    // race: sprint toward the target pearl/bed only when some enemy head
    // reaches it no later than we do walking, and the sprint makes us arrive
    // strictly first. Path legality is the exact engine simulation (tail
    // vacates step by step; each step after the first cuts one segment), plus
    // no danger-marked cell on the path and a room check at the landing.
    // Measured negative (both trigger variants); the governor ships OFF.
    static constexpr bool f3_sprint = false;
    static constexpr int f3_max = 3;                 // longest sprint (steps)
    static constexpr int f3_window = 24;             // rate-cap window (rounds)
    static constexpr int f3_max_per_window = 4;      // sprints allowed per window
    static constexpr bool f3_contested_only = true;  // false = sprint any safe path (ablation)

    // ------------------------------------------------ C1-F fix 4: kelp cost on tight ground
    // Slithery wall deaths (ours 25.8/1k live vs band 8.9; the chassis keeps
    // the habit): on tight ground a kelp-adjacent step is one mistake from
    // death. Only when the room flood behind the step is small does each
    // kelp edge around the landing cost f4_penalty score units (6 = 3/4 of a
    // path step).
    static constexpr bool f4_kelp = true;
    static constexpr int f4_penalty = 6;

    // ------------------------------------------------------------ debugging
    // Emit an INDICATOR line per turn (costs ~4k points per byte).
    static constexpr bool indicator = false;

    // ------------------------------------------------ C1-F fix 1: trapped/mill escape
    // The ledger's #1 leak (trapped length lost per 1k: Portals 125.9 vs band
    // 63.4, Slithery 111.4 vs 88.2, Schooltime 24.9 vs 3.6). Three parts:
    //  (a) enclosure probe each turn (reach flood from the head, current
    //      body); when reach < room need and no tail-chase escape, the dragon
    //      is in escape mode: no target, no split, room dominates the score.
    //  (b) in escape mode the room flood runs to escape_cap cells so a step
    //      toward the bulge (or the unknown edge) measurably beats a step
    //      deeper into a dead-end arm; escape_room_weight makes one room cell
    //      worth one path step.
    //  (c) the boxed-in split (why='t') fires only when both halves have room
    //      (a02 lesson: trapped-split children died in the trap; wall deaths
    //      rose 4.65 -> 11.7 per 1k).
    static constexpr bool f1_escape = true;
    // Escape fires when reach < min(room_need, len + escape_margin) and no
    // tail-chase cycle exists: the dragon cannot unspool and cannot circle,
    // i.e. it is actually trapped, not merely on tight ground. A floor was
    // measured harmful on Slithery (small dragons shunned pearls in narrow
    // arms: eat100 45 vs the chassis's 249).
    static constexpr int escape_margin = 2;
    static constexpr int escape_floor = 0;
    static constexpr int escape_cap = 192;
    static constexpr int escape_room_weight = 16;
    static constexpr bool f1_trap_split_room = true;
};

}  // namespace anna
