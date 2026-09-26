"""defaults.py -- every tunable: P (global), RP (per role slice), role ids.

params.py beside main.py (PARAMS = {...}) overrides these; keys "k" or
"role.k" (e.g. "hunt.w_enemy").  Loaded first; shares one namespace with
the other modules (see main.py).
"""

# ======================================================================
# PARAMETERS
# ======================================================================
P = dict(
    # --- material ---------------------------------------------------
    unit_value=4.0,        # value of being a unit, in length units
    len_value=1.0,         # value per segment
    len_value_end=3.0,     # ... ramps to this by the final round (length race)
    # --- threat model -------------------------------------------------
    p_strike1=0.75,        # chance an enemy head 1 step away takes a trade
    p_strike2=0.35,        # ... 2 steps (costs it a segment)
    p_strike3=0.15,        # ... 3 steps
    p_split_child=0.10,    # chance a splittable enemy's newborn strikes
    trade_bias=1.5,        # extra loss felt for an even trade (we'd rather not)
    threat_reach=3,        # max enemy sprint we model
    # --- safety ---------------------------------------------------------
    w_trap=12.0,           # per missing tile of escape space below need
    space_slack=4,         # need = my_len + slack reachable tiles
    w_space=0.08,          # per reachable tile (capped at need)
    w_doom=1.0,            # certain trap (enclosed dead end): times our value
    w_tunnel_head=8.0,     # a head faces us inside the tunnel we enter
    w_tunnel_body=4.0,
    w_tunnel_unknown=1.0,  # a tunnel that runs on into unseen tiles (costs devil, wins qos/help)
    w_doomed=8.0,          # corridor an ally reported as a death trap
    doom_memory=200,     # something occupies it
    w_exit0=6.0,           # new head has no uncontested free neighbour
    w_exit1=1.5,           # ... only one
    w_ally_head_adj=2.5,   # ending next to an ally head (traffic jam)
    w_ally_body_adj=0.3,   # per ally body tile touching our new head
    w_crowd=0.25,          # per ally segment within 2 tiles of our new head
    w_zone_crowd=0.4,      # waypoints: per recent ally report in the zone
    waypoint_every=1,      # rounds between waypoint re-scans (4 lost qos 10-0 -> 3-7: re-aim every turn)
    # --- goal field -----------------------------------------------------
    bfs_cap=180,           # cells in the forward search
    doom_cap=40,           # cells in the permanent-trap search
    doom_skip=1,           # skip it where the flood found room and there are 2+ ways on
    farm_len=4,            # a dead end is a farm if length + its pearls reach this (split out)
    farm_max_len=5,        # ... for small dragons only: a long one (or a crown) loses its length
    w_doom_farm=1.0,       # ... and then costs only this
    w_emergency_split=5.0, # value of shedding the body when every move is fatal
    rbfs_cap=260,          # cells in the reverse (to-target) search
    w_goal=1.2,            # per step closer to the chosen target
    w_goal_sprint=0.2,     # ... per extra step gained by sprinting
    goal_far_w=0.6,        # per manhattan step for off-search waypoints
    w_dist=1.0,            # target choice: cost per step
    pearl_stale=40,        # rounds before a remembered pearl is doubted
    own_disc=0.3,          # target value kept when another head is clearly closer
    own_enemy=0,           # ... counting enemy heads too (1 = v05-v07 behaviour)
    portal_explore=2.0,    # unpaired portal cells as targets, x the role's frontier weight
    w_dive=1.5,            # stepping through an unpaired portal
    dive_risk=1.0,         # ... unknown landing
    w_dive_idle=2.0,       # ... bonus when no target is worth chasing
    w_blind_portal=0.0,    # any portal step landing outside our window (2-8 lost portal maps)
    spawn_window=25,       # spawn predictions matter this many rounds ahead (12 -> 25: small maps 48-24 -> 53-19)
    w_visit=0.25,          # per past visit of the destination (anti-dither)
    # --- sprint -----------------------------------------------------------
    sprint_max=3,
    w_sprint=1.0,          # extra cost per extra sprint step (beyond the segment)
    # --- production -------------------------------------------------------
    split_min=4,           # parent length before a voluntary split
    child_size=2,
    team_target_small=26,  # desired units, maps <= 600 cells
    team_target_mid=40,    # desired units, maps <= 2000 cells
    team_target_big=60,    # desired units, bigger maps
    w_split=6.0,           # base value of a new unit when below target
    split_crowd_max=10,    # no voluntary split with more ally segments than this in view
    split_stop=380,        # no voluntary splits after this round
    split_danger_max=0.3,  # no voluntary split with head risk above this
    w_eat_prod=0.0,        # extra value per pearl eaten before split_stop (non-crown): the
                           # lambda_unit share of a pearl (child_size pearls make a unit).  0 = v10
    # --- ladder policy (ladder.py; hunter-v20's priority ladder) -------------
    ladder=0,              # 1 = non-crown dragons decide by the ladder (0 = evaluator only, v10)
    ladder_until=500,      # ... before this round
    ladder_attack_units=3, # trade up into a longer enemy head only with this many units
    ladder_split_min=4,    # split whenever at least this long
    ladder_safety=1,       # veto a ladder move: 1 certain death (exact simulation); 2 also a
                           # pocket smaller than len + space_slack (flood)
    ladder_risk_max=99,    # veto a ladder step whose head_risk exceeds this (99 = off)
    # --- roles (child role mix by phase) -----------------------------------
    early_end=120,
    mid_end=360,
    mix_early=(0.45, 0.25, 0.30),   # gather, hunt, scout
    mix_mid=(0.45, 0.45, 0.10),
    mix_late=(0.70, 0.30, 0.00),
    orphan_role=0,         # newborn without a hand-off: 0 = hunter if len<=2 (v10); 1 = draw from the mix
    scout_min_cells=600,   # maps this small: no scouts, and the *_small mixes
    mix_early_small=(1.0, 0.0, 0.0),
    mix_mid_small=(0.7, 0.3, 0.0),
    # --- endgame -------------------------------------------------------------
    end_start=440,         # from here: length value ramps, trade margins tighten
    crown_start=200,       # from here the longest dragon we know of stops splitting
    crown_min_len=4,       # ... if it is at least this long
    crown_memory=40,       # rounds an ally's crown report stays believed
    crown_kill_round=380,  # from here: strike any enemy at least as long as our longest
    feed_start=400,        # from here small dragons near a known crown die beside it
    feed_max_len=20,       # ... if at most this long
    feed_range=30,         # ... heading for the crown from this far
    feed_dist=2,           # ... dying once this close
    crown_demote=3,        # a crown steps down when a known crown is this much longer
    beacon_ttl=3,          # ... hops it may be relayed
    beacon_memory=6,       # rounds a relayed beacon stays believed
    # --- sonar -----------------------------------------------------------------
    relay_max=6,
    gossip_slots=2,
    hot_slots=0,           # ladder dragons: rays per turn carrying a K_HOT pearl hotspot (0 = v10)
    enemy_ttl=2,
)

# role ids
GATHER, HUNT, SCOUT, CROWN = 0, 1, 2, 3
ROLE_NAMES = ("gather", "hunt", "scout", "crown")
RP = {
    # per-role slices of the same evaluation
    GATHER: dict(risk=1.3, trade_margin=3, w_pearl=10.0, w_spawn=6.0, w_frontier=1.5,
                 w_enemy=0.0, w_stale=0.0, w_zone_danger=6.0, w_spread=0.25, strike_bonus=0.0),
    HUNT: dict(risk=0.8, trade_margin=0, w_pearl=6.0, w_spawn=3.0, w_frontier=2.0,
               w_enemy=9.0, w_stale=1.0, w_zone_danger=-2.0, w_spread=0.35, strike_bonus=1.0),
    SCOUT: dict(risk=1.0, trade_margin=1, w_pearl=4.0, w_spawn=1.0, w_frontier=8.0,
                w_enemy=1.0, w_stale=4.0, w_zone_danger=1.0, w_spread=0.6, strike_bonus=0.5),
    CROWN: dict(risk=1.6, trade_margin=3, w_pearl=10.0, w_spawn=6.0, w_frontier=0.5,
                w_enemy=0.0, w_stale=0.0, w_zone_danger=3.0, w_spread=0.1, strike_bonus=0.0),
}


# ----------------------------------------------------------------------
# DOCTRINE: per map-class overrides of P / RP, applied once the map size is
# known (apply_doctrine, called from setup()).  The class is "compact" when
# the map has at most compact_max_cells tiles (arena, Colosseum,
# default_small, devil, trophy), else "open".  Keys as in params.py:
# "k" or "role.k".  Empty = v10 behaviour on every map.
# params.py sets them with a class prefix: "compact:split_min", "open:hunt.risk".
# ----------------------------------------------------------------------
P["compact_max_cells"] = 625
DOCTRINE = {
    # v13: compact maps play hunter-v20's production ladder (ladder.py) with
    # our safety vetoes and shared pearl hotspots; crowns and feeding stay
    # with the evaluator.  Open maps: v10 unchanged.
    "compact": {"ladder": 1, "ladder_attack_units": 2, "ladder_safety": 2, "ladder_risk_max": 1.0, "hot_slots": 1},
    "open": {},
}
MAP_CLASS = "open"


def set_param(k, v):
    if "." in k:
        rname, key = k.split(".", 1)
        RP[ROLE_NAMES.index(rname)][key] = v
    else:
        P[k] = tuple(v) if isinstance(v, list) else v


def load_params():
    """params.py (PARAMS = {...}) beside main.py overrides P / RP / DOCTRINE.
    A python file, not json: the submission bundle only ships *.py."""
    sys.path.insert(0, HERE)
    try:
        from params import PARAMS as over
    except ImportError:
        return
    for k, v in over.items():
        if ":" in k:
            cls, key = k.split(":", 1)
            DOCTRINE[cls][key] = v
        else:
            set_param(k, v)


def apply_doctrine(ncells):
    global MAP_CLASS
    MAP_CLASS = "compact" if ncells <= P["compact_max_cells"] else "open"
    for k, v in DOCTRINE[MAP_CLASS].items():
        set_param(k, v)


load_params()
