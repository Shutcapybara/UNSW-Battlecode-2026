"""Every tunable number of the Monte Christo policy.  Units: one segment of length = 1.

Experiment variants add override.py: OVERRIDE = {...}.
"""
P = {
    # --- Valjean features (all defaults = Monte Christo parity) -----------------
    "room_r": 4,           # topology radius (cells) for room / crowd features
    "sat_from": 1.0,       # unit saturation starts at this fraction of the limit
    "sat_disc": 0.0,       # own unit value x (1 - sat_disc * saturation) ...
    "sat_until": 380,      # ... before this round
    "sat_hunt": 0.0,       # saturation from which small foragers hunt early (0 = off)
    "sat_hunt_from": 60,   # ... from this round
    "w_crowd_split": 0.0,  # split penalty per segment/cell of crowd beyond crowd0
    "crowd0": 0.35,
    "w_confine_split": 0.0,  # split penalty per unit of open_frac below open0
    "open0": 0.6,
    "mass_half_life": 6.0, "mass_range": 30, "mass_scale": 8.0, "mass_sources": 16,
    "mass_rays": 0,        # rays per turn for T_MASS reports (0 = no mass comms)
    "mass_period": 1,
    "pressure": 0,         # C1: ATTACK toward the enemy mass vector
    "pressure_max_len": 5, "pressure_until": 380, "pressure_step": 8,
    "press_base": 0.0, "press_sat": 3.0, "press_econ": 0.3, "press_dist": 0.05,
    "support": 0,          # C1: RETREAT toward allied mass
    "support_step": 6, "support_exposure": 1.0,
    "sup_base": 1.0, "sup_balance": 4.0, "sup_econ": 0.3,
    "escape_eval": 0,      # E1: evaluated escape splits (0 = inherited -500 last resort)
    "escape_gate": -15.0,  # E1: consider escape splits when the best other option is below this
    "blind_child": 0.3,    # E1: expected loss fraction of a child whose cells are out of view
    "region": 0,           # C1: GATHER toward the best known bed region (sector)
    "region_until": 380, "reg_period": 5, "reg_min": 6, "reg_cap": 6.0,
    "reg_claim": 0.5, "reg_enemy": 0.1, "reg_gamma": 0.96,
    "reg_w": 0.3, "reg_margin": 1.0, "reg_persist": 1.0,
    "dead_end_disc": 1.0,  # value factor of pearls/beds inside 1-wide dead-end corridors
    "blind_mem": 0,        # portal-exit risk from remembered occupancy (0 = constant p_blind)
    "blind_recent": 12, "blind_floor": 0.15, "blind_unseen": 0.5,
    # --- Sinbad v06 ports (defaults = MC parity; S6 bundle sets them) ---------
    "w_trap_soft": 30.0,   # trap weight when the pocket still holds our body (v06: 5)
    "crown_cut_full": 0,   # crown assumes cut enemies reach reach_cap_crown (v06: 1)
    "reach_cap_crown": 3,
    "strike_reach": 3,     # contact paths up to this many steps (v06: 6)
    "trap_cap": 0.0,       # cap trap penalties at trap_cap x dragon value at stake (0 = off)
    "vac_eat": 0,          # other bodies whose head is next to a pearl vacate this much later
    "trace": 0,            # LOG VJ lines (native analysis only; never deploy enabled)
    "sprint3_limit": 12,   # bound expensive long-body 3-step searches
    "training_trace": 0,   # native data collection only; never deploy enabled
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

# Release settings of valjean-v01-portal-memory (frozen from e5@s6b).
RELEASE = {'blind_mem': 1, 'bed_wait': 0, 'hunt_max_len': 8, 'w_trap_soft': 5, 'crown_cut_full': 1, 'strike_reach': 6}
P.update(RELEASE)

try:  # experiment variants drop an override.py next to this file
    from override import OVERRIDE
    P.update(OVERRIDE)
except ImportError:
    pass
