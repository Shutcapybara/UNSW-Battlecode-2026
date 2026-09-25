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
    "bed_wait": 12.0,      # linear decay of bed value per round of waiting
    "bed_stale": 60,       # predicted pearls older than this lose value
    "v_unseen": 5.0,       # a never-seen tile (exploration)
    "v_stale": 1.5,        # per 100 rounds since a tile was seen
    "gamma": 0.93,         # distance discount of target value
    "own_disc": 0.15,      # value factor when an ally head is clearly closer
    "enemy_disc": 0.6,     # value factor when an enemy head is clearly closer
    "big_cap": 1500,       # node cap of the target search
    "hyst": 1.25,          # keep last target unless the new one is this much better
    # --- move evaluation --------------------------------------------------
    "w_goal": 1.2,         # per step of route distance to the target
    "w_sprint": 1.0,       # extra cost per sprint step (beyond the length lost)
    "slack": 3,            # flood-fill need = length + slack
    "w_trap": 30.0,        # full penalty for a pocket with no room at all
    "t_other": 4,          # other dragons' bodies block BFS up to this depth
    "w_threat": 1.0,       # scale of the head-trade risk penalty
    "p_adj": 0.6,          # chance an adjacent enemy head takes a trade
    "p_sprint": 0.25,      # chance an enemy sprints into us
    "threat_base": 1.5,    # minimum cost of standing in enemy reach
    "w_crowd": 0.6,        # per ally head nearby (scaled by closeness)
    "w_visit": 0.15,       # anti-dither, per recent visit
    "w_bed_block": 0.5,    # standing on a bed that is about to spawn
    # --- combat ------------------------------------------------------------
    "attack": 1,           # consider striking enemy heads
    "atk_margin": 0.0,     # strike if V(enemy) - V(me) >= margin
    "atk_units": 3,        # need at least this many units to strike
    # --- endgame -----------------------------------------------------------
    "grow_from": 380,      # stop splitting, value length more
    "lv_end": 3.0,         # lv at round 500 (linear ramp from grow_from)
}

try:  # experiment variants drop an override.py next to this file
    from override import OVERRIDE
    P.update(OVERRIDE)
except ImportError:
    pass
