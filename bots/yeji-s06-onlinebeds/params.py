"""Every tunable of yeji-s01-swarm-dissolve.  One source of truth: main.py
has no defaults of its own.  Variants overwrite this file (tools/yeji/yrun.py
`bot@key=value`).  Role slices use keys "gather.<k>", "crown.<k>".

Neutral settings reproduce the base host (ouroboros-v10-beacon) for each
mechanism: see README "Ablation switches".
"""
PARAMS = {
    # ---- material / value function V(t) ---------------------------------
    "unit_value": 4.0,         # value of being a unit, in length units
    "len_value": 1.0,          # value per segment (lambda_len)
    "len_value_end": 3.0,      # ... ramps to this by r500 from end_start-100
    # ---- threat model (risk term) ----------------------------------------
    "p_strike1": 0.75, "p_strike2": 0.35, "p_strike3": 0.15,
    "w_parity": 0.0,           # Lanchester trade pricing: x unit_value x (N_them/N_us - 1) (0 = base)
    "parity_mem": 30, "parity_min_seen": 3,
    "p_split_child": 0.10, "trade_bias": 1.5, "threat_reach": 3,
    # ---- safety -------------------------------------------------------------
    "w_trap": 12.0, "space_slack": 4, "w_space": 0.08, "w_doom": 1.0,
    "w_tunnel_head": 8.0, "w_tunnel_body": 4.0, "w_tunnel_unknown": 1.0,
    "w_doomed": 8.0, "doom_memory": 200, "w_exit0": 6.0, "w_exit1": 1.5,
    "w_ally_head_adj": 2.5, "w_ally_body_adj": 0.3, "w_crowd": 0.25,
    "w_zone_crowd": 0.4, "waypoint_every": 1,
    # ---- forage / reposition (goal field) --------------------------------------
    "young_turns": 2, "young_bfs_cap": 90, "young_rbfs_cap": 120,   # CPU degradation for newborns (turns 1-2 after birth)
    "bfs_cap": 180, "doom_cap": 40, "doom_skip": 1, "farm_len": 4, "farm_max_len": 5,
    "w_doom_farm": 1.0, "w_emergency_split": 5.0, "rbfs_cap": 260, "w_goal": 1.2,
    "w_goal_sprint": 0.2, "goal_far_w": 0.6, "w_dist": 1.0, "pearl_stale": 40,
    "own_disc": 0.3, "own_enemy": 0, "portal_explore": 2.0, "w_dive": 1.5,
    "dive_risk": 1.0, "w_dive_idle": 2.0, "w_blind_portal": 0.0, "spawn_window": 25,
    "w_blind_occ": 1.0,        # unseen portal landing: x P(occupied) x (value + 2)  (0 = base)
    "blind_body_mem": 4, "blind_body_p": 0.5, "blind_ally_p": 0.3,
    "target_rate_d0": 0.0,     # >0: target score x (1+d0)/(dist+d0) instead of - w_dist*dist
    "map_prior": 0,             # public-map prior OFF: tournament maps are out of sample (no map data shipped)
    "prior_max_cells": 625,    # use the map prior only on maps up to this size (open maps: it hurt, s02/s03)
    "w_field": 12.0,            # move value x (field(after) - field(now)); field = bed potential 0..1 (map prior)
    "field_compact_cells": 625, "w_field_open": 0.0,   # field weight on maps above this size
    "field_until": 150, "field_late": 0.5, "field_crown": 1,            # recognise the public map from the first view and load terrain + fast beds
    "online_beds": 1,          # learn fast beds from countdowns seen (general; replaces the map prior)
    "online_fast_max": 40,     # a bed whose largest seen countdown is <= this counts as fast
    "w_bed_prior": 5.0,        # target value of an unwatched fast bed x P(pearl) (map prior)
    "w_zone_bed": 3.0,         # waypoint pull x sqrt(zone bed rate) (map prior)
    "w_visit": 0.25, "sprint_max": 3, "w_sprint": 1.0,
    # ---- momentum (target hysteresis) -------------------------------------------
    "hysteresis_margin": 1.0,  # keep the current target unless another beats it by this (0 = base)
    # ---- produce (lambda_unit schedule) --------------------------------------------
    "split_min_len": 4,        # never produce below this length
    "split_child_len": 2,      # production child length
    "unit_target": 64,         # production stops at this many units (0 = base host's size table)
    "unit_cells": 0,           # >0: unit target capped at map cells / this (compact maps jam)
    "team_target_small": 26, "team_target_mid": 40, "team_target_big": 60,  # used when unit_target = 0
    "w_split": 6.0,            # value of a new unit at lambda_unit = 1, far below target
    "produce_until": 100,      # lambda_unit = 1 until here ...
    "produce_stop": 380,       # ... then decays linearly to 0 here (no voluntary split after)
    "split_crowd_max": 10,     # no voluntary split with more ally segments in view
    "split_danger_max": 0.3,   # no voluntary split with head risk above this x unit_value
    # ---- roles at birth (gather, hunt, scout) --------------------------------------
    "role_mix_on": 0,          # 0: every child is a gatherer (no scouts, no hunters); 1: base host mix
    "early_end": 120, "mid_end": 360,
    "mix_early": (0.45, 0.25, 0.30), "mix_mid": (0.45, 0.45, 0.10), "mix_late": (0.70, 0.30, 0.00),
    "scout_min_cells": 600, "mix_early_small": (1.0, 0.0, 0.0), "mix_mid_small": (0.7, 0.3, 0.0),
    # ---- crown / endgame (lambda_crown) ------------------------------------------------
    "end_start": 440,
    "crown_elect_from": 200,   # crown election starts
    "crown_min_len": 4,
    "crown_stagger": 1,       # volunteer from crown_elect_from + (id*7919) mod this (1 = base)
    "crown_elect_longest": 0,  # volunteer only if no fresh ally report is longer (0 = base)
    "crown_elect_fresh": 10,   # ... rounds an ally self report counts as fresh
    "crown_trap_mult": 1.0,
    "crown_crowd_mult": 1.0,   # crown: ally-crowding penalty multiplier (1 = base)    # crown: escape-space penalty multiplier (1 = base)
    "crown_memory": 40,
    "crown_kill_round": 380,
    "crown_demote": 3,
    "beacon_ttl": 3,
    "beacon_memory": 6,
    # ---- escort / dissolve (map-conditioned onset) -----------------------------------
    "dissolve_on": 0,          # 0: base host feeding (feed_start/feed_dist, die within feed_dist)
    "onset_portals": 300,      # Portals (32x16 with portal ids >= 4)
    "onset_slithery": 300,     # Slithery Fight (63x27)
    "onset_default": 400,
    "feed_max_len": 3,         # dissolve only if L <= this
    "feed_radius": 30,         # escort only if the crown is within this distance
    "feed_late_round": 0,      # from this round (0 = never) dragons up to feed_late_max_len feed too
    "feed_late_max_len": 20,
    "recipient_eats_first": 1,
    "diss_any": 1,             # dissolve beside ANY longer visible ally head (Vibing++), not only the crown
    "diss_len_margin": 1,      # ... whose visible length >= ours + this
    "diss_enemy_clear": 2,     # ... and no enemy head within this distance # dissolve only with our head adjacent to the crown's visible head
    "feed_start": 400, "feed_max_len_base": 20, "feed_dist": 2,   # base host feeding (dissolve_on = 0)
    # ---- salvage -----------------------------------------------------------------------
    "salvage_on": 1,           # deterministic salvage (split L-2 / head-on / cheapest death), logged
    # ---- messaging -----------------------------------------------------------------------
    "cert_enabled": 1,
    "cert_direct": 1,          # also send the certificate on any straight ray that hits the child         # birth certificate over the backward ray
    "relay_max": 6, "gossip_slots": 2, "enemy_ttl": 2,
    # ---- instrumentation ---------------------------------------------------------------------
    "act_log": 1,              # LOG ACT:<tag> in the turn's single write
    # ---- role slices (gather, hunt, scout, crown) ------------------------------------------------
    "gather.risk": 1.3, "gather.trade_margin": 3, "gather.w_pearl": 10.0, "gather.w_spawn": 6.0,
    "gather.w_frontier": 1.5, "gather.w_enemy": 0.0, "gather.w_stale": 0.0,
    "gather.w_zone_danger": 6.0, "gather.w_spread": 0.25, "gather.strike_bonus": 0.0,
    "hunt.risk": 0.8, "hunt.trade_margin": 0, "hunt.w_pearl": 6.0, "hunt.w_spawn": 3.0,
    "hunt.w_frontier": 2.0, "hunt.w_enemy": 9.0, "hunt.w_stale": 1.0,
    "hunt.w_zone_danger": -2.0, "hunt.w_spread": 0.35, "hunt.strike_bonus": 1.0,
    "scout.risk": 1.0, "scout.trade_margin": 1, "scout.w_pearl": 4.0, "scout.w_spawn": 1.0,
    "scout.w_frontier": 8.0, "scout.w_enemy": 1.0, "scout.w_stale": 4.0,
    "scout.w_zone_danger": 1.0, "scout.w_spread": 0.6, "scout.strike_bonus": 0.5,
    "crown.risk": 1.6, "crown.trade_margin": 3, "crown.w_pearl": 10.0, "crown.w_spawn": 6.0,
    "crown.w_frontier": 0.5, "crown.w_enemy": 0.0, "crown.w_stale": 0.0,
    "crown.w_zone_danger": 3.0, "crown.w_spread": 0.1, "crown.strike_bonus": 0.0,
}
