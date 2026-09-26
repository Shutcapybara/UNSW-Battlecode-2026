"""Parameter and role table borrowed unchanged from ouroboros-v10-beacon."""
P = dict(
    # Pearl component; neutral defaults reproduce v08. These keys are also
    # documented with consumers and ranges in README.md.
    **{"pearl.prepos": 0,          # 0 legacy; 1 arrival-time bed valuation
       "pearl.compact_only": 1,    # 0 all maps; 1 <=625 cells only
       "pearl.prediction_ttl": 4,  # 0..30: overdue timer memory, rounds
       "pearl.confirmed_only": 0}, # 0 legacy; 1 only observed pearls grow body
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
    # --- roles (child role mix by phase) -----------------------------------
    early_end=120,
    mid_end=360,
    mix_early=(0.45, 0.25, 0.30),   # gather, hunt, scout
    mix_mid=(0.45, 0.45, 0.10),
    mix_late=(0.70, 0.30, 0.00),
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


def load_params():
    """params.py (PARAMS = {...}) beside main.py overrides P / RP.
    A python file, not json: the submission bundle only ships *.py."""
    try:
        from params import PARAMS as over
    except ImportError:
        return
    for k, v in over.items():
        if "." in k and k.split(".", 1)[0] in ROLE_NAMES:
            rname, key = k.split(".", 1)
            RP[ROLE_NAMES.index(rname)][key] = v
        else:
            if k not in P:
                raise ValueError("Unknown parameter: " + k)
            P[k] = tuple(v) if isinstance(v, list) else v


load_params()

