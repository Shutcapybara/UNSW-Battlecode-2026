"""Every tunable number of the Monte Christo policy.  Units: one segment of length = 1.

Experiment variants add override.py: OVERRIDE = {...}.
"""
P = {
    "sprint3_limit": 12,   # bound expensive long-body 3-step searches
    "training_trace": 0,   # native data collection only; never deploy enabled
    "intent_trace": 0,     # LOG MC_INTENT per turn (selection/status/outcome); never deploy enabled
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
    "bed_wait": 12.0,      # linear decay of bed value per round of waiting
    "bed_stale": 60,       # predicted pearls older than this lose value
    "v_unseen": 5.0,       # a never-seen tile (exploration)
    "v_stale": 1.5,        # per 100 rounds since a tile was seen
    "v_dive": 7.0,         # an unpaired portal (stepping in reveals where it goes)
    "dive_base": -0.5,     # score of an unplanned dive (unknown landing)
    "p_blind": 1.0,        # x V(me): chance an unseen portal exit holds a head
    "p_dive": 0.1,         # x V(me): risk of stepping into an unpaired portal
    "gamma": 0.93,         # distance discount of target value
    "own_disc": 0.15,      # value factor when an ally head is clearly closer
    "enemy_disc": 0.6,     # value factor when an enemy head is clearly closer
    "big_cap": 160,        # node cap of the target search (far targets: far_target)
    "born_cap": 60,        # ... on a dragon's first two turns (cold caches, CPU)
    "flood_cap": 24,       # flood-fill need never exceeds this (CPU)
    "flood_cap_long": 40,  # ... for dragons of length >= 10
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
    "w_threat": 1.0,       # scale of the head-trade risk penalty
    "p_long": 0.9,         # chance a SHORTER enemy head in reach trades with us
    "p_eq": 0.7,           # ... an equal-length enemy
    "p_short": 0.1,        # ... a longer enemy
    "p_sprint": 0.8,       # factor for reach that needs a sprint (2+ steps)
    "k_their": 0.5,        # weight of the enemy's loss in a trade we did not choose
    "cut_extra": 1,        # assumed hidden segments of an enemy running out of view
    "threat_base": 1.0,    # minimum cost of standing in enemy reach
    "w_crowd": 0.6,        # per ally head nearby (scaled by closeness)
    "w_visit": 0.15,       # anti-dither, per recent visit
    "w_bed_block": 0.5,    # standing on a bed that is about to spawn
    # --- combat ------------------------------------------------------------
    "attack": 1,           # consider striking enemy heads
    "atk_margin": 0.5,     # strike if V(enemy) - V(me) >= margin
    "atk_units": 3,        # need at least this many units to strike
    # --- communication ------------------------------------------------------
    "gossip": 1,           # share pearls / soon-due beds in view by sonar
    "gossip_trust": 8,     # ignore reports on tiles we saw within this many rounds
    "gossip_horizon": 30,  # only share beds due within this many rounds
    "share_portals": 1,    # send a known portal pairing every other turn
    # --- state: aggregate count density (from the v07 radio study) ------------
    "density_half_life": 4.0,
    "density_radius": 7.0,   # separable triangular kernel, toroidal tiles
    "density_sources": 32,   # hard bound on retained unique reporters
    "density_remote": 1,
    "density_ally": 0.25,
    "density_enemy": 0.40,
    "density_period": 1,
    "density_rays": 1,       # reserved rays (idle rays first, FOOD displaceable)
    # --- state: directional length density (x03) -------------------------------
    "swarm_half_life": 4.0,
    "swarm_radius": 7.0,
    "swarm_sources": 32,     # retained unique reporters (x4 quadrant rows)
    "swarm_remote": 1,
    "swarm_rays": 1,
    "swarm_damp": 4.0,       # balance damping: lengths are bigger than counts
    "swarm_contact": 0.5,    # an enemy quadrant this heavy = contact: report it
    # --- features v2 (computed in x03; consumed by policy versions >= 2) -------
    "aggro_until": 200,      # "early": the opening, where trades buy space
    "child_room_cap": 12,    # graded confinement: flood cap at the child head
    # --- portal reconnaissance (candidates C2 / executors E2, x05) -------------
    "portal_recon": 1,       # master gate for recon objectives
    "recon_min_area": 300,   # compact maps reveal themselves; skip recon
    "recon_until": 400,      # late-game information has no time to pay off
    "recon_min_len": 3,      # expendable scouts: not shorter (fragile) ...
    "recon_max_len": 6,      # ... and not longer (too valuable to dive)
    "recon_units": 4,        # the team must be able to spare a scout
    "recon_tval": 4.0,       # recon when nothing better than a near unseen tile;
                             # the search's own in-range dive nominations score
                             # ~5+ and keep recon off: no duplicate dive objectives
    "recon_reach": 8,        # max optimistic route distance to the portal
    "recon_cap": 96,         # BFS node cap for the recon probe/preview
    "recon_max": 2,          # at most this many recon objectives per turn
    "recon_val": 7.0,        # base value of pairing a portal (cf. v_dive)
    "recon_info_w": 3.0,     # weight of the portal sector's unseen fraction
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
