"""Every tunable number of the Monte Christo policy.  Units: one segment of length = 1.

Experiment variants add override.py: OVERRIDE = {...}.
"""
P = {
    "density_half_life": 4.0,
    "density_radius": 7.0,    # separable triangular kernel, toroidal tiles
    "density_sources": 32,    # hard bound on retained unique reporters
    "density_remote": 1,
    "density_policy": 1,     # 0 off, 1 resource discount, 2 control gradient
    "density_ally": 0.25,
    "density_enemy": 0.40,
    "density_gradient": 0.65,
    "info_aggro_push": 0.0, # early saturated push toward enemy density; 0 disables
    "info_aggro_until": 200,
    "info_aggro_sat": 0.7,
    "info_room_cap": 12,
    "info_room_norm": 12.0,
    "density_period": 1,
    "density_rays": 2,       # reserved rays, plus any otherwise unused rays
    "density_relay": 1,
    "density_trace": 0,
    "sprint3_limit": 10,   # bound expensive long-body 3-step searches
    "sprint3_saturated_limit": 4,  # preserve triples only for length-4/5 dragons when dense
    "training_trace": 0,   # native data collection only; never deploy enabled
    # --- material ---------------------------------------------------------
    "lv": 1.0,             # value of one segment of our length
    "unit": 3.0,           # value of one dragon (unit) beyond its length
    # --- production ---------------------------------------------------------
    "split_min": 4,        # split when length >= this
    "child": 2,            # child size
    "split_val": 8.0,      # stronger early unit-production pressure
    "split_stop": 380,     # no production splits from this round
    # --- newborn separation in constrained topology ----------------------
    "escape_spawn_area": 11,
    "escape_spawn_branches": 1,
    "escape_handoff_retries": 2,
    "escape_max_turns": 18,
    "escape_target_depth": 12,
    "escape_target_nodes": 120,
    "escape_origin_depth": 18,
    "escape_origin_nodes": 180,
    "escape_min_distance": 5,
    "escape_open_area": 8,
    "escape_open_weight": 1.6,
    "escape_branch_weight": 2.5,
    "escape_exit_weight": 1.0,
    "escape_distance_weight": 0.7,
    "escape_resource_weight": 0.18,
    "escape_route_cost": 0.85,
    "escape_waypoint_hysteresis": 2.5,
    "escape_route_weight": 3.5,
    "escape_push": 2.2,
    "escape_decay": 0.91,
    "escape_origin_cost": 2.0,
    "escape_parent_radius": 4,
    "escape_parent_cost": 1.2,
    "escape_valuable_distance": 2,
    "escape_valuable_threshold": 8.0,
    "escape_resource_pause_budget": 6,
    "escape_portal_bonus": 1.5,
    "escape_revisit_weight": 1.4,
    "escape_trace": 0,
    "opening_rescue_until": 1,  # early rescue window for long, partially seen spawns
    "opening_rescue_min_len": 8,
    "opening_initial_id_limit": 6,
    "opening_rescue_value": 8.0,
    "opening_production_start": 1,
    "opening_production_until": 30,
    "opening_production_unit_cap": 32,
    "opening_production_value": 8.0,
    # --- targets (resource field) -----------------------------------------
    "v_pearl": 10.0,       # a visible pearl
    "v_mem": 6.0,          # a remembered pearl we cannot see now
    "mem_ttl": 40,         # forget remembered pearls after this many rounds
    "v_bed": 8.0,          # a bed predicted to hold a pearl when we arrive
    "bed_wait": 12.0,      # linear decay of bed value per round of waiting
    "bed_stale": 60,       # predicted pearls older than this lose value
    "v_unseen": 5.0,       # a never-seen tile (exploration)
    "v_stale": 1.5,        # per 100 rounds since a tile was seen
    "v_dive": 7.0,         # an unpaired portal (stepping in reveals where it goes)
    "dive_base": -0.5,     # score of an unplanned dive (unknown landing)
    "p_blind": 1.0,        # x V(me): chance an unseen portal exit holds a head
    "blind_mem": 1,        # use body sightings to estimate risk at unseen exits
    "blind_fresh": 12,     # recent body sighting window, in rounds
    "r_body": 1.0,         # risk when a body was recently near the exit
    "r_seen": 0.15,        # risk when the exit was recently surveyed and quiet
    "r_unseen": 0.5,       # risk when the exit area is unknown
    "p_dive": 0.1,         # x V(me): risk of stepping into an unpaired portal
    "gamma": 0.93,         # distance discount of target value
    "own_disc": 0.15,      # value factor when an ally head is clearly closer
    "enemy_disc": 0.6,     # value factor when an enemy head is clearly closer
    "big_cap": 72,        # node cap of the target search (far targets: far_target)
    "big_cap_saturated": 40,  # target-search cap when allied population is dense
    "born_cap": 48,        # ... on a dragon's first two turns (cold caches, CPU)
    "flood_cap": 22,       # flood-fill need never exceeds this (CPU)
    "flood_cap_long": 36,  # ... for dragons of length >= 10
    "hyst": 1.25,          # keep last target unless the new one is this much better
    # --- move evaluation --------------------------------------------------
    "w_goal": 1.2,         # per step of route distance to the target
    "w_sprint": 1.0,       # extra cost per sprint step (beyond the length lost)
    "slack": 3,            # flood-fill need = max(length + slack, min_area)
    "fcred": 2,            # flood credit per rim cell with unknown edges
    "fcred_portal": 6,     # flood credit for a rim cell with an unpaired portal
    "head_block": 0,       # cells next to other heads are blocked up to this depth
    "min_area": 5,         # smallest pocket we enter (1-wide dead ends kill)
    "child_area": 4,       # a newborn needs this much room
    "farm_factor": 0.15,   # trap penalty kept for a pocket we can eat and split out of
    "w_trap": 30.0,        # full penalty for a pocket with no room at all
    "v_ref": 8.0,          # trap penalty x max(1, V(me) / v_ref)
    "t_hidden": 6,         # other bodies running out of view: extra turns to vacate
    "w_threat": 1.0,        # scale of the head-trade risk penalty
    "p_long": 0.9,         # chance a SHORTER enemy head in reach trades with us
    "p_eq": 0.7,           # ... an equal-length enemy
    "p_short": 0.1,        # ... a longer enemy
    "p_sprint": 0.8,       # factor for reach that needs a sprint (2+ steps)
    "k_their": 0.5,        # weight of the enemy's loss in a trade we did not choose
    "cut_extra": 1,        # assumed hidden segments of an enemy running out of view
    "threat_base": 1.0,    # minimum cost of standing in enemy reach
    "w_crowd": 0.6,        # per ally head nearby (scaled by closeness)
    "devil_opening_until": 42,  # early center claim on the 32x16 Devil arena
    "devil_center_weight": 2.8, # reward each step toward the central columns
    "devil_lane_until": 60, # mild tie-break for distributed scouting
    "devil_lane_weight": 2.0, # never override a route away from the lane
    "devil_ally_body_weight": 2.5, # leave a small buffer around friendly trails
    "w_visit": 0.15,       # anti-dither, per recent visit
    "w_bed_block": 0.5,    # standing on a bed that is about to spawn
    # --- directional momentum from Yuna v03 -------------------------------
    "momentum_w": 0.6,
    "momentum_decay": 0.6,
    # --- combat ------------------------------------------------------------
    "attack": 1,           # consider striking enemy heads
    "atk_margin": 0.5,     # strike if V(enemy) - V(me) >= margin
    "atk_units": 3,        # need at least this many units to strike
    "w_support": 0.5,      # reduced trade gain for nearby allied heads
    "support_r": 3,        # allied head within this torus distance counts
    "support_cap": 2,      # count at most this many supporting heads
    # --- communication ------------------------------------------------------
    "gossip": 1,           # share pearls / soon-due beds in view by sonar
    "gossip_trust": 8,     # ignore reports on tiles we saw within this many rounds
    "gossip_horizon": 30,  # only share beds due within this many rounds
    "share_portals": 1,    # send a known portal pairing every other turn
    # --- hunting the enemy's long dragons ------------------------------------
    "prey_min": 8,         # an enemy this long (seen, or +2 if it runs out of view) is prey
    "prey_ttl": 15,        # prey reports older than this are ignored
    "hunt_from": 200,      # small foragers hunt from this round
    "hunt_max_len": 5,     # ... if at most this long
    "v_hunt": 1.0,         # target value per segment of the prey (capped at 40)
    # --- endgame: crown + feeding ----------------------------------------------
    "grow_from": 380,      # non-crowns: stop splitting, value length more
    "lv_end": 3.0,         # lv at round 500 (linear ramp from grow_from)
    "crown_from": 250,     # elect a crown (longest, lowest id) by sonar beacon
    "crown_ttl": 20,
    "crown_margin": 3,
    "claim_spread": 120,   # self-claims are staggered over this many rounds
    "claim_len": 3,        # ... and need at least this length     # a challenger must be this much longer to take over       # forget a crown report older than this
    "lv_crown": 4.0,       # the crown's value per segment
    "feed_base": 40,       # feeding starts at 500 - feed_base - (W + H) * feed_k
    "feed_k": 0.6,
    "feed_dist": 4,        # suicide within this manhattan distance of the crown head
    "crown_food": 5,       # endgame: others ignore pearls this close to the crown
    "crown_food_early": 3, # ... before feeding starts
    "w_flank": 3.0,        # feeder penalty for a tile next to the crown's body
    "feed_range": 16,      # only dragons this close (manhattan) to the crown feed
    "feed_min_crown": 4,   # only feed a crown at least this long
}

try:  # experiment variants drop an override.py next to this file
    from override import OVERRIDE
    P.update(OVERRIDE)
except ImportError:
    pass
