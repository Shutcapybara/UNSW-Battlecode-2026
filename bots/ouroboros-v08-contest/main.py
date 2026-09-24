"""ouroboros-v08-contest: evaluation-function dragon (see docs/ouroboros-design.md).

One process per dragon.  Each turn:

    SENSE    parse the wire -> persistent world model
    LISTEN   fold sonar gossip into the model
    ASSESS   phase, threat map, goal target (role-weighted target field)
    SEARCH   enumerate candidate actions (moves, sprints, strikes, splits)
    EVALUATE score every candidate with one evaluation function
    ACT      emit the argmax, then sonar (gossip / child hand-off)

Every number that shapes a decision lives in P (global) or RP (per role) and
can be overridden by params.py next to this file:
    PARAMS = {"w_goal": 3.0, "hunt.trade_margin": -1}
"""
import gc
import os
import sys

gc.disable()  # no reference cycles worth collecting; GC pauses cost judge points

HERE = os.path.dirname(os.path.abspath(__file__))

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
    sys.path.insert(0, HERE)
    try:
        from params import PARAMS as over
    except ImportError:
        return
    for k, v in over.items():
        if "." in k:
            rname, key = k.split(".", 1)
            RP[ROLE_NAMES.index(rname)][key] = v
        else:
            P[k] = tuple(v) if isinstance(v, list) else v


load_params()

TRACE = os.path.exists("/tmp/ouro-trace-on")

# ======================================================================
# IO
# ======================================================================
READ = sys.stdin.readline
OUT = []


def emit(s):
    OUT.append(s)


def flush():
    OUT.append("PROTOCOL 3")
    OUT.append("ENDTURN")
    sys.stdout.write("\n".join(OUT) + "\n")
    sys.stdout.flush()
    del OUT[:]


def parts():
    while True:
        line = READ()
        if not line:
            return []
        h = line.find("#")
        if h >= 0:
            line = line[:h]
        p = line.split()
        if p:
            return p


def trace(msg):
    if TRACE:
        with open("/tmp/ouro-trace-%s-%d.log" % (TEAM, MY_ID), "a") as fh:
            fh.write(msg + "\n")


# ======================================================================
# STATE
# ======================================================================
W = H = NC = 0
MY_ID = -1
TEAM = "A"
UNIT_LIMIT = 64
RND = 0
LEN = 3
UNITS = 1
FACING = 0
HEAD = 0
ROLE = GATHER
BORN = 0
DIRS = "NESW"

ek = None          # edge kinds, 2*NC: 0 unknown 1 open 2 kelp 3 portal
epid = {}          # portal edge -> portal id
pends = {}         # portal id -> [edge keys]
unk = None         # per cell: count of unknown sides
seen = None        # per cell: last round seen (0 = never; stored +1)
fertile = None     # per cell: spawns pearls
visits = None      # per cell: head visits
NB = None          # neighbour cache (torus only)
DC = None          # destination cache (edges fully known)
bmark = bdist = bfirst = None
bstamp = 0

pearls = {}        # cell -> round seen
spawn_at = {}      # cell -> predicted spawn round
enemies = {}       # key -> (cell, round, len)
allies = {}        # id -> (cell, len, role, round)
ally_face = {}     # id -> facing reported with the last self packet
MOVED_DIR = 0      # facing after our action this turn (for the self packet)
zone_heat = {}     # zone -> [enemy heat, round]
trail = []         # our head cells, oldest first (body = last LEN)
relay_q = []
relayed = {}
portal_told = set()
bed_told = {}
told = {}
handoff = None     # (role, target) received at birth
doomed = {}        # cell -> round an ally reported it as a dead-end entrance
doom_told = False
target_hint = -1

# per-turn view
occ = {}           # cell -> (dragon id, team is ours, is head)
enemy_heads = []   # (cell, id, visible len)
ally_heads = set()
enemy_len = {}
echo = (0, 0, 0, 0, 0)
ZS = 8             # zone size
ZW = ZH = 1


def setup():
    global ek, unk, seen, fertile, visits, NB, DC, NC, bmark, bdist, bfirst, ZW, ZH
    NC = W * H
    ek = bytearray(2 * NC)
    unk = bytearray(b"\x04") * NC
    seen = [0] * NC
    fertile = bytearray(NC)
    visits = bytearray(NC)
    NB = [None] * NC
    DC = [None] * NC
    bmark = [0] * NC
    bdist = [0] * NC
    bfirst = bytearray(NC)
    ZW = (W + ZS - 1) // ZS
    ZH = (H + ZS - 1) // ZS


# ======================================================================
# GEOMETRY
# ======================================================================
def nbr(c):
    g = NB[c]
    if g is None:
        x = c % W
        g = NB[c] = (c - W if c >= W else c - W + NC,
                     c + 1 if x + 1 < W else c + 1 - W,
                     c + W if c < NC - W else c + W - NC,
                     c - 1 if x else c - 1 + W)
    return g


def ekey(c, d):
    if d == 0:
        return c
    if d == 2:
        return c + W if c < NC - W else c + W - NC
    if d == 3:
        return NC + c
    x = c % W
    return NC + (c + 1 if x + 1 < W else c + 1 - W)


def dest_raw(c, d):
    """Cell reached leaving c towards d: -1 blocked (kelp / unpaired portal), -2 unknown."""
    k = ekey(c, d)
    t = ek[k]
    if t == 1:
        return nbr(c)[d]
    if t == 0:
        return -2
    if t == 2:
        return -1
    ends = pends.get(epid.get(k))
    if not ends or len(ends) < 2:
        return -1
    pk = ends[0] if ends[1] == k else ends[1]
    if pk >= NC:
        pc = pk - NC
        px = pc % W
        py = pc // W
        if d == 1:
            return pc
        return py * W + (px - 1 if px else W - 1)
    px = pk % W
    py = pk // W
    if d == 2:
        return pk
    return (py - 1 if py else H - 1) * W + px


def dest(c):
    g = DC[c]
    if g is not None:
        return g
    g = DC[c] = (dest_raw(c, 0), dest_raw(c, 1), dest_raw(c, 2), dest_raw(c, 3))
    return g  # every edge / portal change invalidates the cells it touches


def edge_known(k):
    if k < NC:
        cells = (k, k - W if k >= W else k - W + NC)
    else:
        c = k - NC
        cells = (c, c - 1 if c % W else c - 1 + W)
    for cell in cells:
        if unk[cell]:
            unk[cell] -= 1
        DC[cell] = None


def portal_paired(k):
    if k < NC:
        cells = (k, k - W if k >= W else k - W + NC)
    else:
        c = k - NC
        cells = (c, c - 1 if c % W else c - 1 + W)
    for cell in cells:
        DC[cell] = None


def tdist(a, b):
    ax = a % W
    ay = a // W
    bx = b % W
    by = b // W
    dx = abs(ax - bx)
    dy = abs(ay - by)
    if dx * 2 > W:
        dx = W - dx
    if dy * 2 > H:
        dy = H - dy
    return dx + dy


def zone_of(c):
    return (c // W // ZS) * ZW + (c % W) // ZS


# ======================================================================
# SONAR PACKETS  (check 8 | kind 4 | payload 52)
# ======================================================================
K_SELF, K_ENEMY, K_PORTAL, K_BED, K_HANDOFF, K_DOOM = 1, 2, 3, 4, 5, 6
SALT = 0


def chk(body):
    h = SALT
    b = body
    for _ in range(4):
        h = (h * 167 + (b & 0x3FFF)) & 0xFFFF
        b >>= 14
    return (h ^ (h >> 8)) & 0xFF


def pack(kind, payload):
    body = (kind << 52) | (payload & ((1 << 52) - 1))
    return (chk(body) << 56) | body


def unpack(v):
    body = v & ((1 << 56) - 1)
    if (v >> 56) != chk(body):
        return None
    return body >> 52, body & ((1 << 52) - 1)


def self_packet():
    return pack(K_SELF, (MY_ID & 0xFFF) << 40 | (HEAD & 0xFFF) << 28 | (min(LEN, 255) << 20)
                | (ROLE & 3) << 18 | (min(UNITS, 127) << 11) | (MOVED_DIR & 3) << 9)


def enemy_packet(cell, ln, eid, ttl):
    return pack(K_ENEMY, (ttl & 3) << 50 | (eid & 0xFFF) << 36 | (cell & 0xFFF) << 24
                | (min(ln, 255) << 16) | (RND & 0x1FF))


def portal_packet(pid):
    a, b = pends[pid][0], pends[pid][1]
    return pack(K_PORTAL, (2 << 50) | (pid & 0xFF) << 32 | (a & 0xFFFF) << 16 | (b & 0xFFFF))


def bed_packet(cell, when, ttl):
    return pack(K_BED, (ttl & 3) << 50 | (cell & 0xFFF) << 20 | (when & 0x3FF))


def handoff_packet(role, target):
    return pack(K_HANDOFF, (role & 3) << 40 | ((target + 1) & 0x1FFF) << 24 | (RND & 0x1FF))


def doom_packet(cell, ttl):
    return pack(K_DOOM, (ttl & 3) << 50 | (cell & 0xFFF) << 20 | (RND & 0x1FF))


def report_doom():
    """Every way forward is a dead end: tell the team where the trap starts
    (the first corridor cell after the last junction on our trail)."""
    global doom_told
    if doom_told:
        return
    cells = trail[-40:]
    entrance = cells[-1]
    for i in range(len(cells) - 2, -1, -1):
        c = cells[i]
        exits = 0
        for n in dest(c):
            if n >= 0:
                exits += 1
        if exits >= 3:
            entrance = cells[i + 1]
            break
        entrance = c
    doom_told = True
    doomed[entrance] = RND
    relay_q.insert(0, doom_packet(entrance, 2))
    relay_q.insert(0, doom_packet(entrance, 2))


def relay(kind, payload, ttl):
    if ttl <= 1 or len(relay_q) >= P["relay_max"]:
        return
    key = (kind, payload & ~(3 << 50))
    if relayed.get(key, -99) > RND - 20:
        return
    relayed[key] = RND
    relay_q.append(pack(kind, (payload & ~(3 << 50)) | ((ttl - 1) << 50)))


def hear(v):
    global handoff
    got = unpack(v)
    if got is None:
        return
    kind, pl = got
    if kind == K_SELF:
        aid = (pl >> 40) & 0xFFF
        if aid != (MY_ID & 0xFFF):
            cell = (pl >> 28) & 0xFFF
            if cell < NC:
                allies[aid] = (cell, (pl >> 20) & 0xFF, (pl >> 18) & 3, RND)
                ally_face[aid] = (pl >> 9) & 3
    elif kind == K_ENEMY:
        cell = (pl >> 24) & 0xFFF
        if cell < NC:
            eid = (pl >> 36) & 0xFFF
            ln = (pl >> 16) & 0xFF
            cur = enemies.get(eid)
            if cur is None or cur[1] < RND - 1:
                enemies[eid] = (cell, RND - 1, ln)
                heat_zone(cell, 1.0)
            relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_PORTAL:
        a = (pl >> 16) & 0xFFFF
        b = pl & 0xFFFF
        pid = (pl >> 32) & 0xFF
        for k in (a, b):
            if k < 2 * NC and ek[k] == 0:
                ek[k] = 3
                epid[k] = pid
                edge_known(k)
        if a < 2 * NC and b < 2 * NC:
            ends = pends.setdefault(pid, [])
            for k in (a, b):
                if k not in ends and len(ends) < 2:
                    ends.append(k)
            if len(ends) == 2:
                portal_paired(ends[0])
                portal_paired(ends[1])
        relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_BED:
        cell = (pl >> 20) & 0xFFF
        if cell < NC and not fertile[cell]:
            fertile[cell] = 1
            when = pl & 0x3FF
            if when > RND:
                spawn_at[cell] = when
            relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_DOOM:
        cell = (pl >> 20) & 0xFFF
        if cell < NC:
            if cell not in doomed:
                doomed[cell] = RND
                relay(kind, pl, (pl >> 50) & 3)
    elif kind == K_HANDOFF:
        if handoff is None and RND - (pl & 0x1FF) <= 1:
            handoff = ((pl >> 40) & 3, ((pl >> 24) & 0x1FFF) - 1)


def heat_zone(cell, amount):
    z = zone_of(cell)
    h = zone_heat.get(z)
    if h is None:
        zone_heat[z] = [amount, RND]
    else:
        # exponential decay, half-life ~30 rounds
        age = RND - h[1]
        h[0] = h[0] * (0.977 ** age) + amount
        h[1] = RND


ZD_MEMO = {}
ZD_RND = [-1]


def zone_danger(cell):
    if ZD_RND[0] != RND:
        ZD_MEMO.clear()
        ZD_RND[0] = RND
    z = zone_of(cell)
    v = ZD_MEMO.get(z)
    if v is not None:
        return v
    h = zone_heat.get(z)
    if h is None:
        v = 0.0
    else:
        v = h[0] * (0.977 ** (RND - h[1]))
        if v > 4.0:
            v = 4.0
    ZD_MEMO[z] = v
    return v


# ======================================================================
# SENSE
# ======================================================================
def sense(tiles, bodies, rows_h, rows_v):
    global HEAD
    r1 = RND + 1
    for i in range(49):
        t = tiles[i]
        c = int(t[1]) * W + int(t[0])
        if i == 24:
            HEAD = c
        seen[c] = r1
        pt = int(t[3])
        if t[2] == "1":
            pearls[c] = RND
        elif c in pearls:
            del pearls[c]
        if pt >= 0:
            if not fertile[c]:
                fertile[c] = 1
                if len(relay_q) < P["relay_max"] and bed_told.get(c, -99) < RND - 80:
                    bed_told[c] = RND
                    relay_q.append(bed_packet(c, RND + pt, 2))
            if t[2] != "1":
                spawn_at[c] = RND + (pt if pt > 0 else 1)
    occ.clear()
    del enemy_heads[:]
    ally_heads.clear()
    enemy_len.clear()
    mine = []
    for b in bodies:
        did = int(b[1])
        c = int(b[3]) * W + int(b[2])
        is_head = b[5] == "1"
        if did == MY_ID:
            if not is_head:
                mine.append((c, DIRS.index(b[4][0])))
            continue
        ours = b[0] == TEAM
        occ[c] = (did, ours, is_head, DIRS.index(b[4][0]))
        pearls.pop(c, None)
        if ours:
            if is_head:
                ally_heads.add(c)
        else:
            enemy_len[did] = enemy_len.get(did, 0) + 1
            if is_head:
                enemy_heads.append((c, did))
    # edges
    hx = HEAD % W
    hy = HEAD // W
    for r in range(8):
        y = (hy - 3 + r) % H
        base = y * W
        row = rows_h[r]
        for col in range(7):
            learn(base + (hx - 3 + col) % W, row[col])
    for r in range(7):
        y = (hy - 3 + r) % H
        base = NC + y * W
        row = rows_v[r]
        for col in range(8):
            learn(base + (hx - 3 + col) % W, row[col])
    return mine


def learn(k, tok):
    cur = ek[k]
    if tok == ".":
        if cur == 0:
            ek[k] = 1
            edge_known(k)
        return
    if tok == "w":
        if cur != 2:
            if cur == 0:
                edge_known(k)
            ek[k] = 2
            DC_reset(k)
        return
    if cur == 3:
        return
    pid = int(tok)
    if cur == 0:
        edge_known(k)
    ek[k] = 3
    epid[k] = pid
    ends = pends.setdefault(pid, [])
    if k not in ends and len(ends) < 2:
        ends.append(k)
        if len(ends) == 2:
            portal_paired(ends[0])
            portal_paired(ends[1])
            if pid not in portal_told:
                portal_told.add(pid)
                relay_q.insert(0, portal_packet(pid))


def DC_reset(k):
    portal_paired(k)


def seed_trail(mine):
    """First turn: rebuild the body from visible own segments (tail first)."""
    if trail:
        return
    chain = [HEAD]
    left = dict(mine)
    while len(chain) < LEN and left:
        cur = chain[-1]
        nxt = -1
        for c, d in left.items():
            # a body segment faces towards the head: its forward neighbour is cur
            if dest(c)[d] == cur or nbr(c)[d] == cur:
                nxt = c
                break
        if nxt < 0:
            break
        del left[nxt]
        chain.append(nxt)
    trail.extend(reversed(chain))


# ======================================================================
# THREAT
# ======================================================================
def threat_map():
    """cell -> list of (steps, enemy id) for every visible enemy head's sprint reach.

    Paths go through free tiles only; the destination may be anything (the
    strike lands on our head wherever it ends up)."""
    tm = {}
    reach_cap = P["threat_reach"]
    for ec, eid in enemy_heads:
        ln = enemy_len.get(eid, 2)
        # the visible count is a lower bound; assume one more if it touches the window edge
        reach = min(reach_cap, max(1, ln - 1))
        frontier = [ec]
        seen_ = {ec: 0}
        for s in range(1, reach + 1):
            nxt = []
            for c in frontier:
                for n in dest(c):
                    if n < 0 or n in seen_:
                        continue
                    seen_[n] = s
                    lst = tm.get(n)
                    if lst is None:
                        tm[n] = [(s, eid)]
                    else:
                        lst.append((s, eid))
                    if n not in occ:
                        nxt.append(n)
            frontier = nxt
    return tm


def split_threat_cells():
    """Tiles next to the visible tail of long enemies (a newborn can strike once)."""
    out = set()
    for eid, n in enemy_len.items():
        if n < 4:
            continue
        # find its tail-most visible segment: a segment no other segment points to
        segs = [c for c, v in occ.items() if v[0] == eid and not v[2]]
        if not segs:
            continue
        # cheap: every neighbour of every non-head segment end
        for c in segs[-1:]:
            for m in dest(c):
                if m >= 0:
                    out.add(m)
    return out


def dragon_value(ln, role=None):
    return P["unit_value"] + lv() * ln


def lv():
    """Value of one segment: ramps up towards the end of the game."""
    a = P["len_value"]
    b = P["len_value_end"]
    s = P["end_start"] - 100
    if RND <= s:
        return a
    f = (RND - s) / (500.0 - s)
    return a + (b - a) * (f if f < 1 else 1)


def head_risk(cell, my_len_after, tm, split_cells):
    """Expected material loss from enemy strikes on this head tile before our next turn."""
    lst = tm.get(cell)
    rp = RP[ROLE]
    risk = 0.0
    if lst:
        my_v = dragon_value(my_len_after)
        survive = 1.0
        worst = 0.0
        for s, eid in lst:
            p = P["p_strike1"] if s == 1 else P["p_strike2"] if s == 2 else P["p_strike3"]
            survive *= 1.0 - p
            their_v = dragon_value(enemy_len.get(eid, 2))
            loss = my_v - their_v + P["trade_bias"]
            if loss > worst:
                worst = loss
        if worst < 0.5:
            worst = 0.5
        risk = (1.0 - survive) * worst
    if cell in split_cells:
        risk += P["p_split_child"] * dragon_value(my_len_after)
    return risk * rp["risk"]


# ======================================================================
# SEARCH SUPPORT
# ======================================================================
def body_list():
    n = LEN if LEN < len(trail) else len(trail)
    return trail[-n:]


def simulate(path, body):
    """Apply a step list to our body (tail first list).  Returns
    (alive, head, len, eaten, struck_enemy_id, new_body) with exact engine rules."""
    b = list(body)
    ln = len(b)
    eaten = 0
    cell = b[-1]
    for i, d in enumerate(path):
        if i > 0 and ln <= 2:
            return (False, cell, ln, eaten, None, b)
        n = dest(cell)[d]
        if n < 0:
            return (False, cell, ln, eaten, None, b)
        if n in b:
            # own segment (the tail too: collision precedes tail movement)
            return (False, n, ln, eaten, None, b)
        o = occ.get(n)
        if o is not None:
            if o[2] and not o[1]:
                return (False, n, ln, eaten, o[0], b)  # strike
            return (False, n, ln, eaten, None, b)
        b.append(n)
        cell = n
        if n in pearls:
            eaten += 1
        else:
            del b[0]
        if i > 0:
            del b[0]
        ln = len(b)
    return (True, cell, ln, eaten, None, b)


NOSET = frozenset()


def flood(start, body, cap, blocked2):
    """Tiles reachable from start avoiding bodies and contested tiles (next to
    another head: it may step there first); our own body frees up from the
    tail as we move."""
    bset = {}
    nb = len(body)
    for i, c in enumerate(body):
        bset[c] = i  # 0 = tail
    got = {start: 0}
    q = [start]
    qi = 0
    while qi < len(q) and len(got) < cap:
        c = q[qi]
        qi += 1
        dep = got[c] + 1
        for n in dest(c):
            if n < 0 or n in got or n in occ or n in blocked2:
                continue
            j = bset.get(n)
            if j is not None and j >= dep - 1:
                continue
            got[n] = dep
            q.append(n)
    return len(got)


def doom(start, body):
    """Permanent-trap test, ignoring other dragons (they move) but not our own
    body (it frees from the tail).  Returns -1 when the region reachable from
    start is open, else the number of known pearls inside it: the region is
    enclosed by kelp/our body and cannot hold us (too small, or acyclic: a
    1-wide dead end where we can never turn around)."""
    bset = {}
    for i, c in enumerate(body):
        bset[c] = i
    cap = 3 * len(body) + 12
    if cap > P["doom_cap"]:
        cap = P["doom_cap"]
    got = {start: 0}
    q = [start]
    qi = 0
    edges = 0
    while qi < len(q):
        c = q[qi]
        qi += 1
        dep = got[c] + 1
        ds = dest(c)
        for d in range(4):
            n = ds[d]
            if n < 0:
                if n == -2 or ek[ekey(c, d)] == 3:
                    return -1  # unknown edge / unpaired portal: maybe an exit
                continue
            if n in got:
                edges += 1
                continue
            j = bset.get(n)
            if j is not None and j >= dep - 1:
                continue
            got[n] = dep
            q.append(n)
            edges += 1
            if len(got) >= cap:
                return -1
    size = len(got)
    # every internal edge was counted from both ends (tree edges once each way)
    cyclic = edges // 2 >= size
    if size < len(body) + 2 or not cyclic:
        n = 0
        for c in got:
            if c in pearls:
                n += 1
        return n
    return -1


def tunnel_heads(cell, came):
    """Walk forward through a 1-wide tunnel from cell (entered from `came`).
    Unknown side edges do not end the walk (tunnels run beyond our window);
    a known junction does.  Returns 2 if a head (visible, or an ally's
    recent self report) sits in the tunnel ahead, 1 if a body blocks it."""
    prev = came
    cur = cell
    heading = -1
    for d in range(4):
        if dest(came)[d] == cell or nbr(came)[d] == cell:
            heading = d
    recent = [ac for ac, ln, r, when in allies.values() if RND - when <= 2]
    steps = 0
    for _ in range(18):
        ds = dest(cur)
        known = [n for n in ds if n >= 0 and n != prev]
        unknown = sum(1 for n in ds if n == -2)
        if len(known) > 1 or (len(known) == 1 and unknown):
            return 0          # a junction: not a tunnel from here on
        if known:
            nxt = known[0]
        elif unknown and heading >= 0:
            if steps >= 1:
                return 3      # a known tunnel running on into the unknown
            nxt = nbr(cur)[heading]   # assume the tunnel runs straight on
        else:
            return 0          # dead end: doom() handles it
        steps += 1
        o = occ.get(nxt)
        if o is not None:
            return 2 if o[2] else 1
        if nxt in recent:
            return 2
        for d in range(4):
            if ds[d] == nxt or nbr(cur)[d] == nxt:
                heading = d
        prev = cur
        cur = nxt
    return 0


# ======================================================================
# GOAL FIELD
# ======================================================================
def unpaired_portal_cells():
    """Cells beside a portal edge whose far end we have not seen: stepping
    through is the only way to learn where it goes (and often the only way
    out of a walled base)."""
    out = set()
    for pid, ends in pends.items():
        if len(ends) == 1:
            k = ends[0]
            if k < NC:
                out.add(k)
                out.add(k - W if k >= W else k - W + NC)
            else:
                c = k - NC
                out.add(c)
                out.add(c - 1 if c % W else c - 1 + W)
    return out


def choose_target(tm):
    """Forward BFS from the head; score cells as targets with role weights.
    Returns (target cell, far waypoint flag)."""
    global bstamp
    rp = RP[ROLE]
    bstamp += 1
    st = bstamp
    cap = P["bfs_cap"]
    w_dist = P["w_dist"]
    w_pearl = rp["w_pearl"]
    w_spawn = rp["w_spawn"]
    w_front = rp["w_frontier"]
    w_zd = rp["w_zone_danger"]
    window = P["spawn_window"]
    stale = P["pearl_stale"]
    q = [HEAD]
    bmark[HEAD] = st
    bdist[HEAD] = 0
    qi = 0
    best = -1
    best_s = -1e9
    _pearls = pearls
    _spawn = spawn_at
    _unk = unk
    _occ = occ
    body = set(body_list())
    own_disc = P["own_disc"]
    upc = unpaired_portal_cells()
    w_portal = rp["w_frontier"] * P["portal_explore"]
    # pearls a clearly closer head will take: allies always; enemies only if
    # own_enemy (leaving pearls to the enemy just feeds its swarm)
    own_enemy = P["own_enemy"]
    others = [c for c, v in occ.items() if v[2] and (v[1] or own_enemy) and tdist(c, HEAD) <= 8]
    for c, ln, r, when in allies.values():
        if RND - when <= 1 and tdist(c, HEAD) <= 10:
            others.append(c)
    while qi < len(q) and len(q) < cap:
        c = q[qi]
        qi += 1
        dn = bdist[c] + 1
        for n in dest(c):
            if n < 0 or bmark[n] == st or n in _occ or n in body:
                continue
            bmark[n] = st
            bdist[n] = dn
            q.append(n)
            s = 0.0
            pr = _pearls.get(n)
            if pr is not None:
                s += w_pearl if RND - pr < stale else w_pearl * 0.4
            else:
                sp = _spawn.get(n)
                if sp is not None:
                    lag = sp - (RND + dn)
                    if -4 <= lag <= window:
                        s += w_spawn * (1.0 - (lag if lag > 0 else -lag) / (window + 4.0))
            if _unk[n]:
                s += w_front
            if n in upc:
                s += w_portal
            if s <= 0.0:
                continue
            if others:
                # someone else is clearly closer: leave it to them
                for oc in others:
                    if tdist(oc, n) + 1 < dn:
                        s *= own_disc
                        break
            if w_zd:
                s -= w_zd * zone_danger(n) * 0.25
            s -= w_dist * dn
            if n in tm:
                s -= 3.0
            if s > best_s:
                best_s = s
                best = n
    # role pulls that are not tile-local
    if rp["w_enemy"] > 0:
        for eid, (c, r, ln) in enemies.items():
            age = RND - r
            if age > 30:
                continue
            d = bdist[c] if bmark[c] == st else tdist(HEAD, c) * 1.3
            if d <= 0:
                continue
            s = rp["w_enemy"] * (1.0 - age / 30.0) * (1.0 + 0.1 * min(ln, 10)) - w_dist * d
            if s > best_s:
                best_s = s
                best = c
    far = -1
    if best_s < 1.0:
        far = cached_waypoint()
        if far >= 0:
            s = 1.0
            if bmark[far] == st:
                best = far
                best_s = s
    return best, far, best_s


WP = [-1, -99]


def cached_waypoint():
    """The zone scan is a few thousand interpreter lines: redo it every few
    rounds, or when we have arrived."""
    if WP[0] < 0 or RND - WP[1] >= P["waypoint_every"] or tdist(HEAD, WP[0]) <= 2:
        WP[0] = waypoint()
        WP[1] = RND
    return WP[0]


def waypoint():
    """Strategic target when nothing local is worth chasing: a zone center
    chosen by role (scouts: stalest, hunters: hottest, gatherers: richest-safe)."""
    rp = RP[ROLE]
    bestz = -1
    bs = -1e9
    hx = HEAD % W
    hy = HEAD // W
    salt = (MY_ID * 7919) & 0xFFFF
    zone_allies = {}
    for c, ln, r, when in allies.values():
        if RND - when <= 10:
            z = zone_of(c)
            zone_allies[z] = zone_allies.get(z, 0) + 1
    for zy in range(ZH):
        for zx in range(ZW):
            cx = min(W - 1, zx * ZS + ZS // 2)
            cy = min(H - 1, zy * ZS + ZS // 2)
            c = cy * W + cx
            if c == HEAD:
                continue
            dx = abs(cx - hx)
            dy = abs(cy - hy)
            if dx * 2 > W:
                dx = W - dx
            if dy * 2 > H:
                dy = H - dy
            d = dx + dy
            z = zy * ZW + zx
            last = seen[c]
            age = (RND + 1 - last) if last else 200
            s = rp["w_stale"] * min(age, 200) / 40.0
            s += rp["w_frontier"] * (0.5 if unk[c] else 0.0)
            zd = zone_danger(c)
            s -= rp["w_zone_danger"] * zd * 0.5
            if ROLE == HUNT:
                s += 2.0 * zd
            s -= P["w_zone_crowd"] * zone_allies.get(z, 0)
            s -= 0.08 * d
            s += ((salt + z * 131) % 97) / 97.0 * 1.5  # spread different dragons
            if s > bs:
                bs = s
                bestz = c
    return bestz


def reverse_dist(target, wanted):
    """BFS distances from target over known passable cells (edges reversed:
    moving n->c is legal iff c in dest(n); we approximate with symmetric edges,
    exact except for one-way portal geometry)."""
    need = set(wanted)
    out = {}
    if target in need:
        out[target] = 0
        need.discard(target)
    got = {target: 0}
    q = [target]
    qi = 0
    cap = P["rbfs_cap"]
    while qi < len(q) and need and len(got) < cap:
        c = q[qi]
        qi += 1
        dn = got[c] + 1
        for n in dest(c):
            if n < 0 or n in got:
                continue
            got[n] = dn
            if n in need:
                out[n] = dn
                need.discard(n)
            if n not in occ:
                q.append(n)
    return out


# ======================================================================
# PRODUCTION
# ======================================================================
def team_target():
    if NC <= 600:
        t = P["team_target_small"]
    elif NC <= 2000:
        t = P["team_target_mid"]
    else:
        t = P["team_target_big"]
    return min(t, UNIT_LIMIT)


def child_role():
    if RND < P["early_end"]:
        mix = P["mix_early"]
    elif RND < P["mid_end"]:
        mix = P["mix_mid"]
    else:
        mix = P["mix_late"]
    if NC <= P["scout_min_cells"]:
        if RND < P["early_end"]:
            mix = P["mix_early_small"]
        elif RND < P["mid_end"]:
            mix = P["mix_mid_small"]
        else:
            mix = (mix[0] + mix[2] * 0.5, mix[1] + mix[2] * 0.5, 0.0)
    counts = [0.0, 0.0, 0.0]
    n = 0
    for aid, (c, ln, r, when) in allies.items():
        if RND - when < 25 and r < 3:
            counts[r] += 1
            n += 1
    # deterministic: the most under-represented role
    best = 0
    bd = -1e9
    for r in range(3):
        deficit = mix[r] * (n + 1) - counts[r]
        if mix[r] <= 0:
            continue
        if deficit > bd:
            bd = deficit
            best = r
    return best


def emergency_split():
    """Every way forward is death: shed the body so the tail end lives on.
    The newborn (head on our tail, facing away) takes all but 2 segments."""
    if LEN < 4 or UNITS >= UNIT_LIMIT:
        return 0
    body = body_list()
    if len(body) < LEN:
        return 0
    n = LEN - 2
    ch = body[0]
    ch2 = body[1]
    parent = set(body[n:])
    for m in dest(ch):
        if m >= 0 and m != ch2 and m not in parent and m not in occ:
            return n
    return 0


def split_value(head_risk_now):
    if ROLE == CROWN:
        return None
    if RND >= P["split_stop"] or LEN < P["split_min"] or UNITS >= UNIT_LIMIT:
        return None
    n = P["child_size"]
    if LEN - n < 2:
        return None
    target = team_target()
    if UNITS >= target:
        return None
    if head_risk_now > P["split_danger_max"] * P["unit_value"]:
        return None
    # a newborn in a packed window is a future traffic death, not a unit
    crowd = 0
    for o in occ.values():
        if o[1]:
            crowd += 1
    if crowd > P["split_crowd_max"]:
        return None
    # the newborn: head on our tail, facing away from our body.  It must
    # have somewhere to go, and not straight into a tunnel with a head in it.
    body = body_list()
    if len(body) < LEN:
        return None
    ch = body[0]
    ch2 = body[1]
    parent = set(body[n:])
    ok = 0
    for m in dest(ch):
        if m < 0 or m == ch2 or m in parent or m in occ:
            continue
        if tunnel_heads(m, ch):
            continue
        if doom(m, [ch2, ch, m][-2:] if n == 2 else [ch, m]) >= 0:
            continue
        ok += 1
    if ok == 0:
        return None
    # value of a unit falls as we approach target
    frac = UNITS / float(target)
    return P["w_split"] * (1.2 - frac) - (1.0 if ok == 1 else 0.0), n


# ======================================================================
# DECIDE
# ======================================================================
def candidates(body):
    """Single steps always; sprints (2..sprint_max) only when they can matter:
    a visible enemy head is close (strike / escape), every single step looks
    dangerous, or step one eats a pearl (a free second step)."""
    out = []
    for d in range(4):
        out.append(([d], simulate([d], body)))
    maxk = min(P["sprint_max"], LEN - 1)
    if maxk < 2:
        return out
    near = False
    for c, eid in enemy_heads:
        if tdist(HEAD, c) <= maxk + 1:
            near = True
            break
    grow = []
    if near:
        grow = [p for p, r in out if r[0]]
    else:
        for p, r in out:
            if r[0] and r[1] in pearls:
                grow.append(p)
    # depth 2: full candidates.  depth 3: strikes only (cheap to score, and
    # the only reason to pay two segments in one turn)
    for path in grow:
        for d in range(4):
            p2 = path + [d]
            res = simulate(p2, body)
            if res[0] or res[4] is not None:
                out.append((p2, res))
            if res[0] and maxk >= 3 and near:
                for d3 in range(4):
                    p3 = p2 + [d3]
                    r3 = simulate(p3, body)
                    if r3[4] is not None:
                        out.append((p3, r3))
    return out


def decide():
    global ROLE
    body = body_list()
    if TRACE:
        import time
        _t = [time.perf_counter()]
    tm = threat_map()
    sc = split_threat_cells()
    rp = RP[ROLE]
    lvv = lv()

    if TRACE:
        _t.append(time.perf_counter())
    target, far, tscore = choose_target(tm)
    if TRACE:
        _t.append(time.perf_counter())
    cands = candidates(body)
    ends = [res[1] for p, res in cands if res[0]]
    if TRACE:
        _t.append(time.perf_counter())
    rdist = reverse_dist(target, ends + [HEAD]) if target >= 0 else {}
    if TRACE:
        _t.append(time.perf_counter())
    base_d = rdist.get(HEAD)

    # ally head positions (visible) for traffic avoidance
    best = None
    best_v = -1e18
    my_v = dragon_value(LEN)
    need = LEN + P["space_slack"]
    if need > 40:
        need = 40
    scored = []
    n_ok = 0
    ally_segs = [(c % W, c // W) for c, o in occ.items() if o[1]]
    near_allies = [c for c, ln, r, when in allies.values()
                   if RND - when <= 3 and tdist(c, HEAD) <= 12]
    contested = set()
    for c, v in occ.items():
        if v[2]:
            for m in dest(c):
                if m >= 0 and m not in occ:
                    contested.add(m)
    for path, res in cands:
        alive, cell, ln, eaten, struck, nb = res
        k = len(path)
        if not alive:
            if struck is not None:
                # trade: both die; they lose their value, we lose ours
                their = enemy_len.get(struck, 2)
                their_v = dragon_value(their)
                margin = rp["trade_margin"]
                if RND >= P["end_start"]:
                    margin = max(margin, 1)
                v = their_v - my_v + rp["strike_bonus"] - 0.3 * (k - 1)
                if RND >= P["crown_kill_round"] and ROLE != CROWN and \
                        their >= max(LEN + 1, longest_known_ally()):
                    margin = 0  # their crown outgrows ours: take it off the board
                    v += 10.0
                if their < LEN + margin and UNITS > 2:
                    v -= 50.0  # below this role's trade threshold
                v -= 20.0      # losing the unit's future is never free
                v += 20.0 * (1 if their >= LEN + margin else 0)
                scored.append((v, path, "strike"))
            continue
        v = lvv * (ln - LEN)                      # sprint cost, pearls eaten
        v -= head_risk(cell, ln, tm, sc)
        sp = flood(cell, nb, need + 1, NOSET)
        if sp < need:
            v -= P["w_trap"] * (need - sp) / float(need) * (1.0 + ln * 0.1)
        v += P["w_space"] * sp
        ex = 0.0
        nfree = 0
        nbs = set(nb)
        for m in dest(cell):
            if m >= 0 and m not in occ and m not in nbs:
                nfree += 1
                ex += 0.5 if m in contested else 1.0
        # the permanent-trap test is the expensive one: skip it where the
        # flood found room and the head has two ways on (not a corridor)
        dm = -1
        if not P["doom_skip"] or sp < need or nfree < 2:
            dm = doom(cell, nb)
        if dm < 0:
            n_ok += 1
        elif ln + dm >= P["farm_len"] and UNITS < UNIT_LIMIT and LEN <= P["farm_max_len"] \
                and ROLE != CROWN:
            # a dead end with pearls enough to grow and split our way out:
            # the child walks out of the corridor, the stub stays.  A farm.
            v -= P["w_doom_farm"]
            n_ok += 1
        else:
            v -= P["w_doom"] * (dragon_value(ln) + 2.0)
        th = tunnel_heads(cell, nb[-2] if len(nb) > 1 else HEAD)
        if th:
            v -= P["w_tunnel_head"] if th == 2 else (P["w_tunnel_body"] if th == 1 else
                                                     P["w_tunnel_unknown"])
        if cell in doomed and RND - doomed[cell] < P["doom_memory"]:
            v -= P["w_doomed"]
        if ex < 0.5:
            v -= P["w_exit0"]
        elif ex < 1.5:
            v -= P["w_exit1"] * (1.5 - ex)
        # goal potential
        if target >= 0:
            d = rdist.get(cell)
            if d is not None and base_d is not None:
                prog = base_d - d
                if prog > 1:
                    v += P["w_goal"] + P["w_goal_sprint"] * (prog - 1)
                else:
                    v += P["w_goal"] * prog
            elif far >= 0:
                v += P["goal_far_w"] * (tdist(HEAD, far) - tdist(cell, far))
        # traffic
        for m in dest(cell):
            if m in ally_heads:
                v -= P["w_ally_head_adj"]
            else:
                o = occ.get(m)
                if o is not None and o[1]:
                    v -= P["w_ally_body_adj"]
        if ally_segs:
            cx = cell % W
            cy = cell // W
            crowd = 0
            for ax, ay in ally_segs:
                dx = ax - cx
                if dx < 0:
                    dx = -dx
                if dx * 2 > W:
                    dx = W - dx
                if dx > 2:
                    continue
                dy = ay - cy
                if dy < 0:
                    dy = -dy
                if dy * 2 > H:
                    dy = H - dy
                if dy <= 2:
                    crowd += 1
            v -= P["w_crowd"] * crowd
        if blind_portal(path):
            v -= P["w_blind_portal"]
        v -= P["w_visit"] * visits[cell]
        # spread from nearby allies (gossip positions)
        v += spread_term(cell, near_allies) * rp["w_spread"]
        # sprinting burns production: extra cost per extra step
        v -= P["w_sprint"] * (k - 1)
        v += ((MY_ID * 31 + RND * 7 + path[0] * 13) % 10) * 0.001
        scored.append((v, path, "move"))
    if TRACE:
        _t.append(time.perf_counter())
        trace("PH r%d threat=%.2f target=%.2f cands=%.2f(n%d) rdist=%.2f(n%d) eval=%.2f" % (
            RND, (_t[1] - _t[0]) * 1e3, (_t[2] - _t[1]) * 1e3, (_t[3] - _t[2]) * 1e3, len(cands),
            (_t[4] - _t[3]) * 1e3, len(rdist), (_t[5] - _t[4]) * 1e3))
    if n_ok == 0 and len(trail) > 2:
        report_doom()
        es = emergency_split()
        if es:
            scored.append((P["w_emergency_split"], es, "split"))
    ds0 = dest(HEAD)
    for d in range(4):
        if ds0[d] == -1 and ek[ekey(HEAD, d)] == 3:
            # unpaired portal: an unknown destination, worth a look when
            # nothing better is on offer (scouts like it more)
            v = P["w_dive"] * (1.5 if ROLE == SCOUT else 1.0) - P["dive_risk"]
            if tscore < 1.0:
                v += P["w_dive_idle"]
            scored.append((v, [d], "dive"))
    risk_here = head_risk(HEAD, LEN, tm, sc)
    sv = split_value(risk_here)
    if sv is not None:
        v, n = sv
        v -= risk_here * 0.5
        scored.append((v, n, "split"))
    if not scored:
        return None
    scored.sort(key=lambda t: t[0], reverse=True)
    if TRACE:
        trace("r%d id%d role%d len%d head%d tgt%d far%d top=%s" % (
            RND, MY_ID, ROLE, LEN, HEAD, target, far,
            [(round(s[0], 2), s[1], s[2]) for s in scored[:4]]))
    return scored[0], target


def in_view(c):
    dx = abs(c % W - HEAD % W)
    dy = abs(c // W - HEAD // W)
    if dx * 2 > W:
        dx = W - dx
    if dy * 2 > H:
        dy = H - dy
    return dx <= 3 and dy <= 3


def blind_portal(path):
    """Does this path go through a portal onto a tile we cannot see?  The
    landing may be occupied: that is a body death we never saw coming."""
    cell = HEAD
    for d in path:
        n = dest(cell)[d]
        if n < 0:
            return True
        if ek[ekey(cell, d)] == 3 and not in_view(n):
            return True
        cell = n
    return False


def spread_term(cell, near):
    best = 99
    for c in near:
        d = tdist(cell, c)
        if d < best:
            best = d
    if best >= 99:
        return 0.0
    return best if best < 8 else 8


def fallback_move():
    """Least-bad single step when nothing scored (all options fatal)."""
    body = body_list()
    best = FACING
    bv = -1e9
    for d in range(4):
        n = dest(HEAD)[d]
        v = 0.0
        if n < 0:
            v = -100.0
        elif n in body:
            v = -90.0
        else:
            o = occ.get(n)
            if o is not None:
                if o[1] and o[2]:
                    v = -200.0  # ally head: kills two of ours
                elif o[1]:
                    v = -80.0
                elif o[2]:
                    v = -10.0   # enemy head: at least a trade
                else:
                    v = -60.0
        if v > bv:
            bv = v
            best = d
    return best


# ======================================================================
# ACT
# ======================================================================
def commit_path(path):
    global MOVED_DIR
    MOVED_DIR = path[-1]
    cell = HEAD
    for d in path:
        n = dest(cell)[d]
        if n < 0:
            break
        cell = n
        trail.append(cell)
    emit("MOVE " + "".join(DIRS[d] for d in path))


def send_sonars(split_dir=None, handoff_msg=None):
    """Four rays.  Gossip (relay queue) takes up to `gossip_slots` of them,
    rotating; every other ray carries our self report (position + heading),
    which is what lets allies keep out of the tunnel we are in."""
    sp = self_packet()
    start = RND & 3
    ng = P["gossip_slots"]
    for j in range(4):
        d = (start + j) & 3
        if d == split_dir and handoff_msg is not None:
            emit("SONAR %s %d" % (DIRS[d], handoff_msg))
        elif ng > 0 and relay_q:
            emit("SONAR %s %d" % (DIRS[d], relay_q.pop(0)))
            ng -= 1
        else:
            emit("SONAR %s %d" % (DIRS[d], sp))


def boot_turn(mine):
    """First turn of a new process: interpreter boot ate most of the budget.
    Take the safest single step."""
    body = body_list()
    best = -1
    bv = -1e9
    for d in range(4):
        res = simulate([d], body)
        if not res[0]:
            continue
        c = res[1]
        v = 0.0
        for m in dest(c):
            o = occ.get(m)
            if o is not None:
                if o[2] and not o[1]:
                    v -= 5.0
                elif o[2]:
                    v -= 2.0
                else:
                    v -= 0.5
            elif m < 0:
                v -= 0.3
        if c in pearls:
            v += 1.0
        if handoff is not None and handoff[1] >= 0:
            v -= 0.05 * tdist(c, handoff[1])
        if v > bv:
            bv = v
            best = d
    if best < 0:
        best = fallback_move()
        trail.append(dest(HEAD)[best] if dest(HEAD)[best] >= 0 else HEAD)
        emit("MOVE " + DIRS[best])
    else:
        commit_path([best])
    send_sonars()


def take_turn():
    global ROLE
    visits[HEAD] = min(255, visits[HEAD] + 1)
    for c, eid in enemy_heads:
        ln = enemy_len.get(eid, 2)
        enemies[eid] = (c, RND, ln)
        heat_zone(c, 0.5)
        if len(relay_q) < P["relay_max"] and told.get(eid, -99) < RND - 3:
            told[eid] = RND
            relay_q.append(enemy_packet(c, ln, eid, P["enemy_ttl"]))
    if RND % 16 == 0:
        prune()
    if ROLE != CROWN and RND >= P["crown_start"] and LEN >= P["crown_min_len"]:
        # the length race: one dragon stops splitting and banks length.  We
        # volunteer when no ally crown is known, or the known ones are clearly
        # shorter than us (they may be dying).
        best_crown = -1
        for aid, (c, ln, r, when) in allies.items():
            if r == CROWN and RND - when < P["crown_memory"] and ln > best_crown:
                best_crown = ln
        if best_crown < 0 or LEN >= best_crown + 3:
            ROLE = CROWN
    got = decide()
    if got is None:
        d = fallback_move()
        if TRACE:
            trace("r%d FALLBACK d%d head%d body%s dest%s occ%s" % (RND, d, HEAD, body_list(), dest(HEAD), [occ.get(n) for n in dest(HEAD)]))
        n = dest(HEAD)[d]
        trail.append(n if n >= 0 else HEAD)
        emit("MOVE " + DIRS[d])
        send_sonars()
        return
    (v, act, kind), target = got
    if kind == "split":
        n = act
        role = child_role()
        emit("SPLIT %d" % n)
        # the child's head is our old tail; a ray fired back into our own
        # body exits at the (new) tail and lands on the child's head
        back = neck_dir()
        msg = handoff_packet(role, target)
        # body after split
        del trail[:-(LEN - n)]
        send_sonars(back, msg)
        return
    commit_path(act)
    send_sonars()


def neck_dir():
    """Direction from the head into our own neck segment (-1 if unknown)."""
    body = body_list()
    if len(body) < 2:
        return None
    neck = body[-2]
    ds = dest(HEAD)
    for d in range(4):
        if ds[d] == neck or nbr(HEAD)[d] == neck:
            return d
    return None


def longest_known_ally():
    best = 0
    for aid, (c, ln, r, when) in allies.items():
        if RND - when < 30 and ln > best:
            best = ln
    return best


def prune():
    for c in [c for c, r in pearls.items() if RND - r > 80]:
        del pearls[c]
    for c in [c for c, w in spawn_at.items() if w < RND - 30]:
        del spawn_at[c]
    for k in [k for k, v in enemies.items() if RND - v[1] > 40]:
        del enemies[k]
    for k in [k for k, v in allies.items() if RND - v[3] > 40]:
        del allies[k]
    for k in [k for k, r in relayed.items() if RND - r > 40]:
        del relayed[k]


# ======================================================================
# MAIN
# ======================================================================
def main():
    global W, H, MY_ID, TEAM, UNIT_LIMIT, RND, LEN, UNITS, FACING, echo, ROLE, BORN, SALT
    p = parts()
    if not p:
        return
    MY_ID = int(p[1])
    TEAM = parts()[1]
    p = parts()
    W = int(p[1])
    H = int(p[2])
    UNIT_LIMIT = int(parts()[1])
    SALT = 0x5A if TEAM == "A" else 0xC3
    setup()
    first = True
    while True:
        p = parts()
        if not p or p[0] == "ENDGAME":
            return
        RND = int(p[1])
        FACING = DIRS.index(parts()[1][0])
        LEN = int(parts()[1])
        UNITS = int(parts()[1])
        nmsg = int(parts()[1])
        msgs = [int(parts()[0]) for _ in range(nmsg)]
        f = parts()
        echo = (0, 0, 0, 0, 0)
        if f[0] == "ECHOES":
            echo = tuple(int(v) for v in f[1:6])
            f = parts()
        tiles = [f] + [parts() for _ in range(48)]
        nb = int(parts()[1])
        bodies = [parts() for _ in range(nb)]
        rows_h = [parts() for _ in range(8)]
        rows_v = [parts() for _ in range(7)]
        if TRACE:
            import time
            t0 = time.perf_counter()
        if first:
            BORN = RND
        for m in msgs:
            hear(m)
        mine = sense(tiles, bodies, rows_h, rows_v)
        if first:
            seed_trail(mine)
            if RND == 0:
                ROLE = GATHER
            elif handoff is not None:
                ROLE = handoff[0]
            else:
                ROLE = HUNT if LEN <= 2 else GATHER
        if trail and trail[-1] != HEAD:
            trail.append(HEAD)
        if len(trail) > 400:
            del trail[:-300]
        if first and RND > 0:
            boot_turn(mine)
        else:
            take_turn()
        if TRACE:
            trace("T r%d len%d dt=%.2fms n_enemy=%d occ=%d" % (RND, LEN, (time.perf_counter() - t0) * 1000, len(enemy_heads), len(occ)))
        first = False
        flush()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        if TRACE:
            import traceback
            trace("CRASH\n" + traceback.format_exc())
        raise
