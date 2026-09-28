"""Every tunable number of the Sinbad policy.  Units: one segment of length = 1.

Experiment variants (tools/sinbad/arena.py) add override.py: OVERRIDE = {...}.
"""
P = {
    # --- material ---------------------------------------------------------
    "lv": 1.0,             # value of one segment of our length
    "unit": 3.0,           # value of one dragon (unit) beyond its length
    # --- production ---------------------------------------------------------
    "split_min": 4,        # split when length >= this
    "child": 2,            # child size
    "split_val": 4.0,      # score of a (safe) split during the production phase
    "split_stop": 380,     # no production splits from this round
    # --- targets (resource field) -----------------------------------------
    "v_pearl": 10.0,       # a visible pearl
    "v_mem": 6.0,          # a remembered pearl we cannot see now
    "mem_ttl": 40,         # forget remembered pearls after this many rounds
    "v_bed": 8.0,          # a bed predicted to hold a pearl when we arrive
    "bed_wait": 0.0,       # 0: a bed counts only if due by our arrival (12 = linear wait decay)
    "fast_per": 0,         # beds whose countdown never exceeded this keep full value out of view (0 = off)
    "fast_mult": 1.0,      # ... times v_bed
    "bed_stale": 60,       # predicted pearls older than this lose value
    "v_unseen": 5.0,       # a never-seen tile (exploration)
    "v_stale": 1.5,        # per 100 rounds since a tile was seen
    "v_dive": 3.0,         # an unpaired portal (stepping in reveals where it goes; 7: dives killed pairs of our own)
    "dive_units": 999,     # unpaired portals are targets only while we have fewer units
    "dive_base": -0.5,     # score of an unplanned dive (unknown landing)
    "p_blind": 1.0,        # x V(me): chance an unseen portal exit holds a head
    "p_dive": 0.1,         # x V(me): risk of stepping into an unpaired portal
    "gamma": 0.93,         # distance discount of target value
    "own_disc": 0.15,      # value factor when an ally head is clearly closer
    "enemy_disc": 0.6,     # value factor when an enemy head is clearly closer
    "big_cap": 160,        # node cap of the target search (far targets: far_target)
    "born_cap": 60,        # ... on a dragon's first two turns (cold caches, CPU)
    "fork_intent": 0,
    "fork_age": 8,
    "fork_radius": 3,
    "fork_value_scale": 0.35,
    "flood_cap": 24,       # flood-fill need never exceeds this (CPU)
    "flood_cap_long": 40,  # ... for dragons of length >= 10
    "long_len": 12,        # from this length: no 3-step sprints (CPU)
    "hyst": 1.25,          # keep last target unless the new one is this much better
    # --- move evaluation --------------------------------------------------
    "w_goal": 1.2,         # per step of route distance to the target
    "w_sprint": 1.0,       # extra cost per sprint step (beyond the length lost)
    "slack": 3,            # flood-fill need = max(length + slack, min_area)
    "fcred": 2,            # flood credit per rim cell with unknown edges
    "fcred_portal": 6,     # flood credit for a rim cell with an unpaired portal
    "head_block": 0,       # cells next to other heads are blocked up to this depth
    "crowd_need": 0,       # extra flood room per ally head within crowd_rad (0 = off)
    "crowd_rad": 3,
    "min_area": 5,         # smallest pocket we enter (1-wide dead ends kill)
    "child_area": 4,       # a newborn needs this much room
    "farm_factor": 0.15,   # trap penalty kept for a pocket we can eat and split out of
    "w_trap": 30.0,        # full penalty for a pocket with no room at all
    "w_trap_soft": 5.0,    # ... when the pocket still holds our whole body
    "v_ref": 8.0,          # trap penalty x max(1, V(me) / v_ref)
    "t_hidden": 6,         # other bodies running out of view: extra turns to vacate
    "w_threat": 1.0,       # scale of the head-trade risk penalty
    "p_long": 0.9,         # chance a SHORTER enemy head in reach trades with us
    "p_eq": 0.7,           # ... an equal-length enemy
    "p_short": 0.1,        # ... a longer enemy
    "p_sprint": 0.8,       # factor for reach that needs a sprint (2+ steps)
    "k_their": 0.5,        # weight of the enemy's loss in a trade we did not choose
    "reach_cap_crown": 3,  # the crown assumes enemy sprints up to this long (6: worse off big maps)
    "cut_extra": 1,        # assumed hidden segments of an enemy running out of view
    "threat_base": 1.0,    # minimum cost of standing in enemy reach
    "w_crowd": 0.6,        # per ally head nearby (scaled by closeness)
    "w_visit": 0.15,       # anti-dither, per recent visit
    "w_bed_block": 0.5,    # standing on a bed that is about to spawn
    # --- priority ladder (compact maps) ------------------------------------
    "ladder_nc": 0,        # maps with at most this many tiles use the ladder (0 = never)
    "ladder_floor": -3.0,  # ladder choices must score above this in the evaluator
    # --- combat ------------------------------------------------------------
    "attack": 1,           # consider striking enemy heads
    "atk_margin": 0.5,     # strike if V(enemy) - V(me) >= margin
    "atk_units": 3,        # need at least this many units to strike
    "strike_reach": 6,     # longest sprint we search for a strike
    "strike_bonus": 2.0,   # score of a strike on top of V(enemy) - V(me)
    # --- communication ------------------------------------------------------
    "gossip": 1,           # share pearls / soon-due beds in view by sonar
    "gossip_trust": 8,     # ignore reports on tiles we saw within this many rounds
    "gossip_horizon": 30,  # only share beds due within this many rounds
    "share_portals": 1,    # send a known portal pairing every other turn
    # --- hunting the enemy's long dragons ------------------------------------
    "prey_min": 8,         # an enemy this long (seen, or +2 if it runs out of view) is prey
    "prey_ttl": 15,        # prey reports older than this are ignored
    "hunt_from": 200,      # small foragers hunt from this round
    "hunt_max_len": 8,     # ... if at most this long (5: big+bigT 13-3, 8: 15-1)
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
    "feed_pressure_gate": 0, # require fresh observed rival pressure before feeding
    "feed_pressure_state_only": 0, # bypass feed clock when pressure is observed
    "feed_pressure_slack": 2, # rival may trail crown by this many segments
}

try:  # experiment variants drop an override.py next to this file
    from override import OVERRIDE
    P.update(OVERRIDE)
except ImportError:
    pass
