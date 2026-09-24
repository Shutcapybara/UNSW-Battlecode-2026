"""Parameter table for hydra-v11-macro.

Everything tunable lives here, keyed by name and documented next to its
value (docs/macro-spec.md section 6). Map-class doctrine is two dicts,
`compact` (<= 625 tiles) and `open`; `common` is shared. A variant
overrides values by dropping a `params.py` next to this file with
`OVERRIDES = {'key': value, ...}` applied on top of the merged table.
"""

COMMON = {
    # --- candidate search caps (CPU budget; the judge kills at 100M points) ---
    'compass_cap': 160,     # target BFS expansions per turn
    'threat_cap': 160,      # total threat BFS expansions per turn
    'sprint_max': 3,        # longest MOVE command emitted (steps; costs steps-1 segments)
    'sprint_enemy_dist': 3, # torus-manhattan that counts as "enemy near" for sprint gating
    'candidates_cap': 14,   # hard cap on simulated candidates per turn

    # --- evaluation weights, all in segment units ---
    'food': 9.0,            # value of one pearl eaten along the path (net of sprint payment)
    'risk': 6.0,            # scales p_strike * (len + unit_value) for ending in a threatened cell
    'trap': -70.0,          # flood-fill space below own length, or zero exits
    'mobility': 1.2,        # per cell of capped flood-fill freedom
    'exits': 1.5,           # per free neighbour of the end head
    'crowd': -6.0,          # per adjacent ally head at the end state
    'doom': -45.0,          # end head in the persistent trap memory
    'visit': -1.2,          # per prior visit of the end head (capped at 10)
    'momentum': 1.0,        # bonus for continuing to face the same way
    'jitter': 0.3,          # id-seeded anti-lockstep noise per (cell, round)
    'frontier': 2.0,        # end head itself unseen

    # --- compass (target BFS) cell gains ---
    'c_pearl': 30.0,        # remembered pearl, decays with age
    'c_live': 8.0,          # extra for a pearl visible this turn
    'c_bed': 22.0,          # bed predicted to spawn within walking time
    'camp': 3.0,            # arrive-this-many-rounds-early still counts as on time
    'c_frontier': 3.0,      # cell adjacent to unseen water
    'c_danger': 55.0,       # subtracted per unit of threat probability on the cell
    'pearl_age': 40,        # remembered pearls older than this stop pulling
    'bed_rearm_gap': 14,    # guessed respawn gap for beds whose prediction expired unseen

    # --- production schedule (section 5) ---
    't0': 4.0,              # team target at round 0
    'slope': 0.40,          # target units added per round
    'cap': 32,              # target ceiling (never above the engine unit limit)
    'split': 95.0,          # split value at full urgency
    'split_base': 0.60,     # splits score this fraction even at zero urgency:
                            # breeding must beat foraging while below target
    'split_min_len': 4,     # parent length needed to split a 2-segment child
    'split_stop': 380,      # voluntary splits stop here (crown/endgame hand-off later)
    'split_crowd': -5.0,    # per adjacent ally head when splitting
    'split_pocket': -25.0,  # packed-pocket split penalty (not a ban: churn wins compact)

    # --- unit value over time (a live dragon's strategic worth, in segments) ---
    'uv0': 6.0,
    'uv_end': 2.0,
    'uv_ramp': 300.0,

    # --- combat (section 8): trade only when V(enemy) - V(me) >= margin ---
    'trade_margin': 0,      # min enemy_len - my_len to initiate a head-to-head
    'trade_min_len': 4,     # newborns never volunteer
    'trade': 1.0,           # per segment of (enemy_len - my_len)
    'trade_unit': 1.5,      # unit-kill bonus, small: both sides lose a unit in a trade
    'trade_corpse': 2.5,    # per corpse pearl the exchange drops (both sides contest these)
    'trade_min_units': 2,   # never volunteer the last unit
    'trade_parity': 1,      # if 1, require allies_visible + 1 >= enemies_visible (v09 gate)

    # --- endgame shift (no crown yet in v11; survive and grow) ---
    'late_round': 380,      # round the endgame overlay applies from
    'late_bed_mult': 1.5,   # bed camping weighs more once production stops
    'late_food_mult': 1.3,  # growing the longest dragon is the only length lever left

    'indicator': 1,         # emit a short INDICATOR line (debugging; costs bytes)

    # --- crown / endgame (spec section 4; the round-500 tiebreak is game 2) ---
    # Neutral default: crown_start 501 disables the crown entirely.
    'crown_start': 260,     # from here the longest dragon stops splitting and farms
    'crown_kill_round': 380,  # from here units strike the enemy's big dragons
    'crown_bed_mult': 1.0,  # beds at normal weight: camping them starved the crown
    'crown_danger_mult': 1.6, # the crown avoids threatened corridors harder
    'crown_risk_mult': 3.0, # the crown doubles its death pricing
    'crown_food_mult': 1.5, # the crown is greedy: pearls outrank everything for growth
    'ck_within': 4,         # crown-kill arms when their longest is within this of ours
    'ck_margin': -3,        # crown-kill trades may go against a bigger enemy by this
    'ck_bonus': 40.0,       # extra score for a crown-kill strike
    'yield_gap': 4,         # yield pearls to allies this much longer than me
    'yield_radius': 6,      # right-of-way radius around a big ally
    'crown_spacing': 0,     # (off) the crown keeps this much distance from enemy heads
    'crown_space_pen': 0.0,    # (off) per turn inside enemy-head contact range
}

COMPACT = {
    # small maps: the numbers war is decided by round ~50; produce hard,
    # trade freely at parity (churn doctrine, fry-style)
    'slope': 0.50,
    'cap': 24,
    'trade_margin': 0,
    'trade_parity': 1,
    'split_stop': 360,
    'late_round': 360,
    'c_bed': 26.0,
    'camp': 4.0,
}

OPEN = {
    # big maps: space is plentiful, the numbers war runs to the unit limit,
    # and open games are length races: voluntary churn burns segments and
    # corpse-pearls feed the enemy (ouroboros's 59-1 open record is zero-trades)
    'slope': 0.50,
    'cap': 64,
    'trade_margin': 6,
    'trade_corpse': 0.5,
    'trade_unit': 0.5,
    'trade_parity': 1,
    'compass_cap': 220,
    'threat_cap': 200,
}

_COMPA = dict(COMMON); _COMPA.update(COMPACT)
_OPENO = dict(COMMON); _OPENO.update(OPEN)

try:
    from params import OVERRIDES
    _COMPA.update(OVERRIDES)
    _OPENO.update(OVERRIDES)
except ImportError:
    pass


def weights_for(cells):
    """Merged parameter table for a map of `cells` tiles."""
    return _COMPA if cells <= 625 else _OPENO
