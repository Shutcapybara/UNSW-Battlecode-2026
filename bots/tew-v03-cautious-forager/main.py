"""drake-v01-survive-forage: safety-first forager on the bahamut scaffold.

Hypothesis: exact death avoidance (body/kelp/tail timing, trap and tunnel
accounting) plus a pearl-gradient goal field and measured population growth
beats the mid pool and competes with the top pool without any hunting role.

Layer layout (bahamut scaffold hooks):

    absorb_turn_scalars  io.observation scalars -> module globals
    decode_messages      sonar uint64 -> validated reports (allies/enemies/...)
    update_state         perception: tiles/bodies/edges -> persistent model
    build_features       threat map, goal target, reverse distances
    build_actions        candidate step lists / split / dives with exact
                        engine simulation results
    choose_action        one evaluation function -> argmax
    execute_action       emit MOVE/SPLIT, maintain trail, script memory
    construct_messages   what to say (self report, relays, handoff)
    encode_messages      reports -> direction -> uint64 sonar payloads

Engine world-model pieces (edge array with portal pairing, exact move
simulation including tail-timing collisions, flood/doom trap tests, tunnel
walk, threat sprint reach) implement the published rules; the approach and
several heuristics are borrowed from bots/ouroboros-v05-spread (see README
credits).  Packet layout, salts, checksum, weights and structure are Drake's.
"""
import gc
import os
import sys

gc.disable()  # GC pauses cost judge points; no reference cycles here

import protocol as io

HERE = os.path.dirname(os.path.abspath(__file__))

# =====================================================================
# PARAMETERS (params.py beside this file: PARAMS = {...} overrides P/RP)
# =====================================================================
P = dict(
    # material
    unit_value=4.0,        # value of being alive as a unit, in length units
    len_value=1.0,         # value per segment
    len_value_end=3.0,     # ... ramps to this by the final round
    # threat model
    p_strike1=0.95,        # chance an enemy head 1 step away takes a trade
    p_strike2=0.65,        # ... 2 steps (costs it a segment)
    p_strike3=0.35,        # ... 3 steps
    p_split_child=0.10,    # chance a splittable enemy's newborn strikes
    trade_bias=1.5,        # extra loss felt for an even trade
    threat_reach=3,        # max enemy sprint we model
    # safety
    w_trap=20.0,           # per missing tile of escape space below need
    space_slack=4,         # need = my_len + slack reachable tiles
    w_space=0.08,          # per reachable tile (capped at need)
    w_doom=1.0,            # certain trap (enclosed dead end): x our value
    w_tunnel_head=8.0,     # a head faces us inside the tunnel we enter
    w_tunnel_body=4.0,
    w_tunnel_unknown=1.0,  # a tunnel that runs on into unseen tiles
    w_doomed=8.0,          # corridor an ally reported as a death trap
    doom_memory=200,
    w_exit0=10.0,           # new head has no uncontested free neighbour
    w_exit1=1.5,           # ... only one
    w_ally_head_adj=2.5,   # ending next to an ally head (traffic jam)
    w_ally_body_adj=0.3,   # per ally body tile touching our new head
    w_crowd=0.25,          # per ally segment within 2 tiles of our new head
    w_zone_crowd=0.4,      # waypoints: per recent ally report in the zone
    waypoint_every=2,      # rounds between waypoint zone re-scans
    # goal field
    bfs_cap=180,           # cells in the forward search
    doom_cap=40,           # cells in the permanent-trap search
    doom_skip=1,           # skip doom test where flood found room and 2+ exits
    rbfs_cap=260,          # cells in the reverse (to-target) search
    w_goal=1.2,            # per step closer to the chosen target
    w_goal_sprint=0.2,     # ... per extra step gained by sprinting
    goal_far_w=0.6,        # per manhattan step for off-search waypoints
    w_dist=1.0,            # target choice: cost per step
    pearl_stale=40,        # rounds before a remembered pearl is doubted
    own_disc=0.3,          # target value kept when another head is closer
    portal_explore=2.0,    # unpaired portal cells as frontier targets
    w_dive=1.5,            # stepping through an unpaired portal
    dive_risk=1.0,         # ... unknown landing
    w_dive_idle=2.0,       # ... bonus when no target is worth chasing
    w_blind_portal=0.0,    # portal step landing outside our window
    spawn_window=12,       # spawn predictions matter this many rounds ahead
    w_visit=0.25,          # per past visit of the destination (anti-dither)
    # sprint
    sprint_max=3,
    w_sprint=1.0,          # extra cost per extra sprint step
    # production
    split_min=4,           # parent length before a voluntary split
    child_size=2,
    team_target_small=12,  # desired units, maps <= 600 cells
    team_target_mid=40,    # desired units, maps <= 2000 cells
    team_target_big=60,    # desired units, bigger maps
    w_split=6.0,           # base value of a new unit when below target
    split_crowd_max=10,    # no voluntary split with more ally segments in view
    split_stop=380,        # no voluntary splits after this round
    split_danger_max=0.1,  # no voluntary split with head risk above this
    feed_start=480,        # from here non-crowns leave pearls for the crown
    # endgame
    end_start=440,         # from here: length value ramps, margins tighten
    crown_start=200,       # from here our longest dragon stops splitting
    crown_min_len=5,
    crown_memory=40,       # rounds an ally's crown report stays believed
    crown_kill_round=380,  # from here: strike any enemy at least as long
    # sonar
    relay_max=6,
    gossip_slots=2,
    enemy_ttl=2,
)

FORAGE, CROWN = 0, 1
ROLE_NAMES = ("forage", "crown")
RP = {
    FORAGE: dict(risk=2.5, trade_margin=3, w_pearl=10.0, w_spawn=6.0,
                 w_frontier=1.5, w_zone_danger=6.0, w_spread=0.25,
                 strike_bonus=0.0),
    CROWN: dict(risk=2.8, trade_margin=3, w_pearl=12.0, w_spawn=6.0,
                w_frontier=0.5, w_zone_danger=3.0, w_spread=0.1,
                strike_bonus=0.0),
}


def load_params():
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

TRACE = os.path.exists("/tmp/drake-trace-on")


def trace(msg):
    if TRACE:
        with open("/tmp/drake-trace-%s-%d.log" % (TEAM, MY_ID), "a") as fh:
            fh.write(msg + "\n")


# =====================================================================
# STATE - persistent per dragon instance (one process per dragon)
# =====================================================================
W = H = NC = 0
MY_ID = -1
TEAM = "A"
UNIT_LIMIT = 64
SALT = 0
RND = 0
LEN = 3
UNITS = 1
FACING = 0
HEAD = 0
ROLE = FORAGE
MOVED_DIR = 0          # facing after our action this turn (self packet)
DIRS = "NESW"

ek = None              # edge kinds, 2*NC: 0 unknown 1 open 2 kelp 3 portal
epid = {}              # portal edge -> portal id
pends = {}             # portal id -> [edge keys]
unk = None             # per cell: count of unknown sides
seen = None            # per cell: last round seen (0 = never; stored +1)
fertile = None         # per cell: spawns pearls
visits = None          # per cell: head visits (anti-dither)
NB = None              # torus neighbour cache
DC = None              # per-cell cached dest() tuple
bmark = None           # forward BFS stamps (choose_target scratch)
bdist = None
bstamp = 0

pearls = {}            # cell -> round seen
spawn_at = {}          # cell -> predicted spawn round
enemies = {}           # id -> (cell, round, len)
allies = {}            # id -> (cell, len, role, round)
ally_face = {}         # id -> facing reported with the last self packet
zone_heat = {}         # zone -> [enemy heat, round]
trail = []             # our head cells, oldest first (body = last LEN)
relay_q = []
relayed = {}
portal_told = set()
bed_told = {}
told = {}
handoff = None         # target cell received at birth, or -1
doomed = {}            # cell -> round an ally reported it as a dead end
doom_told = False

# per-turn view (rebuilt by update_state)
occ = {}               # cell -> (dragon id, ours, is head, facing)
enemy_heads = []       # (cell, id)
ally_heads = set()
enemy_len = {}
echo = (0, 0, 0, 0, 0)
ZS = 8                 # zone size for waypoint scan
ZW = ZH = 1

state = {}             # scaffold script memory (waypoint cache); commit late
work = {}              # per-turn scratch


def initialize_state():
    global W, H, NC, MY_ID, TEAM, UNIT_LIMIT, SALT
    global ek, unk, seen, fertile, visits, NB, DC, bmark, bdist, ZW, ZH
    g = io.game
    MY_ID = g["id"]
    TEAM = g["team"]
    W, H = g["size"]
    UNIT_LIMIT = g["unit_limit"]
    SALT = 0x6D if TEAM == "A" else 0xB7   # team salt for packet checksums
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
    ZW = (W + ZS - 1) // ZS
    ZH = (H + ZS - 1) // ZS


# =====================================================================
# GEOMETRY (torus + learned edges, portals paired by id)
# =====================================================================
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
    """Cell reached leaving c towards d: -1 blocked (kelp / unpaired portal),
    -2 unknown edge."""
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


# =====================================================================
# SONAR PACKETS  [check 8 | kind 4 | payload 52], checksum salted by team
# =====================================================================
K_SELF, K_ENEMY, K_PORTAL, K_BED, K_HANDOFF, K_DOOM = 1, 2, 3, 4, 5, 6


def chk(body):
    h = SALT
    b = body
    for _ in range(4):
        h = ((h << 5) + (h >> 2) + (b & 0x3FFF)) & 0xFFFF
        b >>= 14
    return (h ^ (h >> 8)) & 0xFF


def pack(kind, payload):
    body = (kind << 52) | (payload & ((1 << 52) - 1))
    return (chk(body) << 56) | body


def unpack(v):
    body = v & ((1 << 56) - 1)
    if (v >> 56) != chk(body):
        return None
    kind = body >> 52
    if kind > K_DOOM or kind < K_SELF:
        return None
    return kind, body & ((1 << 52) - 1)


def self_packet():
    return pack(K_SELF, (MY_ID & 0xFFF) << 40 | (HEAD & 0xFFF) << 28
                | (min(LEN, 255) << 20) | (ROLE & 3) << 18
                | (min(UNITS, 127) << 11) | (MOVED_DIR & 3) << 9)


def enemy_packet(cell, ln, eid, ttl):
    return pack(K_ENEMY, (ttl & 3) << 50 | (eid & 0xFFF) << 38 | (cell & 0xFFF) << 26
                | (min(ln, 255) << 18) | (RND & 0x1FF))


def portal_packet(pid):
    a, b = pends[pid][0], pends[pid][1]
    return pack(K_PORTAL, (2 << 50) | (pid & 0xFF) << 32 | (a & 0xFFFF) << 16 | (b & 0xFFFF))


def bed_packet(cell, when, ttl):
    return pack(K_BED, (ttl & 3) << 50 | (cell & 0xFFF) << 38 | (when & 0x3FF))


def handoff_packet(target):
    return pack(K_HANDOFF, ((target + 1) & 0x1FFF) << 24 | (RND & 0x1FF))


def doom_packet(cell, ttl):
    return pack(K_DOOM, (ttl & 3) << 50 | (cell & 0xFFF) << 38 | (RND & 0x1FF))


def relay(kind, payload, ttl):
    if ttl <= 1 or len(relay_q) >= P["relay_max"]:
        return
    key = (kind, payload & ~(3 << 50))
    if relayed.get(key, -99) > RND - 20:
        return
    relayed[key] = RND
    relay_q.append(pack(kind, (payload & ~(3 << 50)) | ((ttl - 1) << 50)))


def heat_zone(cell, amount):
    z = zone_of(cell)
    h = zone_heat.get(z)
    if h is None:
        zone_heat[z] = [amount, RND]
    else:
        age = RND - h[1]
        h[0] = h[0] * (0.977 ** age) + amount   # half-life ~30 rounds
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


# =====================================================================
# DECODE / PERCEPTION
# =====================================================================
def absorb_turn_scalars():
    global RND, LEN, UNITS, FACING, echo
    ob = io.observation
    RND = ob["round"]
    FACING = DIRS.index(ob["direction"][0])
    LEN = ob["length"]
    UNITS = ob["units"]
    echo = ob["echoes"]


def decode_messages():
    global handoff
    work["reports"] = []
    for v in io.observation["messages"]:
        got = unpack(v)
        if got is None:
            continue
        kind, pl = got
        work["reports"].append((kind, pl))
        if kind == K_SELF:
            aid = (pl >> 40) & 0xFFF
            if aid != (MY_ID & 0xFFF):
                cell = (pl >> 28) & 0xFFF
                if cell < NC:
                    allies[aid] = (cell, (pl >> 20) & 0xFF, (pl >> 18) & 3, RND)
                    ally_face[aid] = (pl >> 9) & 3
        elif kind == K_ENEMY:
            cell = (pl >> 26) & 0xFFF
            if cell < NC:
                eid = (pl >> 38) & 0xFFF
                ln = (pl >> 18) & 0xFF
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
            cell = (pl >> 38) & 0xFFF
            if cell < NC and not fertile[cell]:
                fertile[cell] = 1
                when = pl & 0x3FF
                if when > RND:
                    spawn_at[cell] = when
                relay(kind, pl, (pl >> 50) & 3)
        elif kind == K_DOOM:
            cell = (pl >> 38) & 0xFFF
            if cell < NC and cell not in doomed:
                doomed[cell] = RND
                relay(kind, pl, (pl >> 50) & 3)
        elif kind == K_HANDOFF:
            if handoff is None and RND - (pl & 0x1FF) <= 1:
                handoff = ((pl >> 24) & 0x1FFF) - 1


def update_state():
    """Perception: fold this turn's observation into the persistent model.
    Returns own visible non-head segments (first-turn trail seeding)."""
    global HEAD, ROLE
    ob = io.observation
    mine = sense(ob["tiles"], ob["bodies"], ob["horizontal_edges"], ob["vertical_edges"])
    if trail and trail[-1] != HEAD:
        trail.append(HEAD)
    if len(trail) > 400:
        del trail[:-300]
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
    # crown volunteer: the length race wants one dragon that stops splitting
    if ROLE != CROWN and RND >= P["crown_start"] and LEN >= P["crown_min_len"]:
        best_crown = -1
        for aid, (c, ln, r, when) in allies.items():
            if r == CROWN and RND - when < P["crown_memory"] and ln > best_crown:
                best_crown = ln
        if best_crown < 0 or LEN >= best_crown + 3:
            ROLE = CROWN
    return mine


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
        if t[2] == 1:
            pearls[c] = RND
        elif c in pearls:
            del pearls[c]
        if pt >= 0:
            if not fertile[c]:
                fertile[c] = 1
                if len(relay_q) < P["relay_max"] and bed_told.get(c, -99) < RND - 80:
                    bed_told[c] = RND
                    relay_q.append(bed_packet(c, RND + pt, 2))
            if t[2] != 1:
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
            portal_paired(k)   # also just invalidates DC for both cells
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


# =====================================================================
# FEATURES: threat map and goal field
# =====================================================================
def threat_map():
    """cell -> list of (steps, enemy id) for visible enemy heads' sprint reach."""
    tm = {}
    for ec, eid in enemy_heads:
        ln = enemy_len.get(eid, 2)
        reach = min(P["threat_reach"], max(1, ln - 1))
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
    """Tiles next to the visible tail of long enemies (a newborn can strike)."""
    out = set()
    for eid, n in enemy_len.items():
        if n < 4:
            continue
        segs = [c for c, v in occ.items() if v[0] == eid and not v[2]]
        for c in segs[-1:]:
            for m in dest(c):
                if m >= 0:
                    out.add(m)
    return out


def choose_target(tm):
    """Forward BFS from the head; score cells as targets.  Returns
    (target cell, far waypoint or -1, best score).  A cached goal stays
    chosen while its evidence persists, so the dragon commits to a
    direction instead of thrashing between adjacent spawn predictions."""
    global bstamp
    rp = RP[ROLE]
    goal = state.get("goal")
    if goal is not None:
        cell, gr = goal
        keep = False
        if cell != HEAD and cell >= 0:
            if RND - gr < 6:
                keep = True
            elif cell in pearls and RND - pearls[cell] < P["pearl_stale"]:
                keep = True
            elif spawn_at.get(cell, -1) >= RND - 2:
                keep = True
        if keep and tdist(HEAD, cell) > 1:
            work["state_updates"]["goal"] = goal
            return cell, -1, 2.0
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
    others = [c for c, v in occ.items() if v[2] and tdist(c, HEAD) <= 8]
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
            # late game: non-crown dragons leave pearls for the crown
            pearls_mine = ROLE == CROWN or RND < P["feed_start"]
            pr = _pearls.get(n)
            if pr is not None:
                s += w_pearl if RND - pr < stale else w_pearl * 0.4
                if not pearls_mine:
                    s -= w_pearl * 0.75 if RND - pr < stale else w_pearl * 0.3
            else:
                sp = _spawn.get(n)
                if sp is not None:
                    lag = sp - (RND + dn)
                    if -4 <= lag <= window:
                        s += w_spawn * (1.0 - (lag if lag > 0 else -lag) / (window + 4.0))
                        if not pearls_mine:
                            s -= w_spawn * 0.75
            if _unk[n]:
                s += w_front
            if n in upc:
                s += w_portal
            if s <= 0.0:
                continue
            if others:
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
    far = -1
    if best_s < 1.0:
        far = cached_waypoint()
        if far >= 0 and bmark[far] == st:
            best = far
            best_s = 1.0
    else:
        work["state_updates"]["goal"] = [best, RND]
    return best, far, best_s


def unpaired_portal_cells():
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


def cached_waypoint():
    wp = state.get("wp") or [-1, -99]
    if wp[0] < 0 or RND - wp[1] >= P["waypoint_every"] or tdist(HEAD, wp[0]) <= 2:
        wp = [waypoint(), RND]
        work["state_updates"]["wp"] = wp
    return wp[0]


def waypoint():
    """Strategic target when nothing local is worth chasing: the stalest
    low-danger zone centre, de-congested by recent ally reports."""
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
            s = 1.5 * min(age, 200) / 40.0            # staleness pull
            s += rp["w_frontier"] * (0.5 if unk[c] else 0.0)
            s -= rp["w_zone_danger"] * zone_danger(c) * 0.5
            s -= P["w_zone_crowd"] * zone_allies.get(z, 0)
            s -= 0.08 * d
            s += ((salt + z * 131) % 97) / 97.0 * 1.5  # spread different dragons
            if s > bs:
                bs = s
                bestz = c
    return bestz


def reverse_dist(target, wanted):
    """BFS distances from target over known passable cells (approximated
    with symmetric edges; exact except for one-way portal geometry)."""
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


# =====================================================================
# SEARCH SUPPORT: exact move simulation and trap tests
# =====================================================================
def body_list():
    n = LEN if LEN < len(trail) else len(trail)
    return trail[-n:]


def simulate(path, body):
    """Apply a step list to our body (tail-first list).  Returns
    (alive, head, len, eaten, struck_enemy_id, new_body) with exact engine
    rules: kelp/unknown/unpaired-portal fatal, any occupied tile fatal
    (own tail included - collision precedes tail movement), enemy head
    kills both, sprint steps burn a segment each and need length > 2."""
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
            return (False, n, ln, eaten, None, b)
        o = occ.get(n)
        if o is not None:
            if o[2] and not o[1]:
                return (False, n, ln, eaten, o[0], b)  # strike: both die
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
    """Tiles reachable from start avoiding bodies and contested tiles; our
    own body frees up from the tail as we move."""
    bset = {}
    for i, c in enumerate(body):
        bset[c] = i   # 0 = tail
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
    """Permanent-trap test, ignoring other dragons (they move) but not our
    own body (it frees from the tail): region too small, or acyclic (a
    1-wide dead end we can never turn around in)."""
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
                    return False   # unknown edge / unpaired portal: maybe an exit
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
                return False
    size = len(got)
    cyclic = edges // 2 >= size
    return size < len(body) + 2 or not cyclic


def tunnel_heads(cell, came):
    """Walk forward through a 1-wide tunnel from cell (entered from `came`).
    2 = a head sits in the tunnel ahead, 1 = a body blocks it,
    3 = a known tunnel running on into the unknown, 0 = nothing special."""
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
            return 0           # a junction: not a tunnel from here on
        if known:
            nxt = known[0]
        elif unknown and heading >= 0:
            if steps >= 1:
                return 3
            nxt = nbr(cur)[heading]   # assume the tunnel runs straight on
        else:
            return 0           # dead end: doom() handles it
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


# =====================================================================
# PRODUCTION
# =====================================================================
def team_target():
    if NC <= 600:
        t = P["team_target_small"]
    elif NC <= 2000:
        t = P["team_target_mid"]
    else:
        t = P["team_target_big"]
    return min(t, UNIT_LIMIT)


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
    crowd = 0
    for o in occ.values():
        if o[1]:
            crowd += 1
    if crowd > P["split_crowd_max"]:
        return None
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
        if doom(m, [ch2, ch]):
            continue
        ok += 1
    if ok == 0:
        return None
    frac = UNITS / float(target)
    return P["w_split"] * (1.2 - frac) - (1.0 if ok == 1 else 0.0), n


# =====================================================================
# DECISION
# =====================================================================
def dragon_value(ln):
    return P["unit_value"] + lv() * ln


def lv():
    a = P["len_value"]
    b = P["len_value_end"]
    s = P["end_start"] - 100
    if RND <= s:
        return a
    f = (RND - s) / (500.0 - s)
    return a + (b - a) * (f if f < 1 else 1)


def head_risk(cell, my_len_after, tm, split_cells):
    rp = RP[ROLE]
    lst = tm.get(cell)
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


def candidates(body):
    """Single steps always; sprints (2..sprint_max) only when they can
    matter: a visible enemy head is close, every single step is unsafe, or
    step one eats a pearl (a free second step)."""
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
    if near:
        grow = [p for p, r in out if r[0]]
    elif not [1 for p, r in out if r[0]]:
        grow = []
    else:
        grow = [p for p, r in out if r[0] and r[1] in pearls]
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


def blind_portal(path):
    """Does this path go through a portal onto a tile we cannot see?"""
    cell = HEAD
    for d in path:
        n = dest(cell)[d]
        if n < 0:
            return True
        if ek[ekey(cell, d)] == 3 and not in_view(n):
            return True
        cell = n
    return False


def in_view(c):
    dx = abs(c % W - HEAD % W)
    dy = abs(c // W - HEAD // W)
    if dx * 2 > W:
        dx = W - dx
    if dy * 2 > H:
        dy = H - dy
    return dx <= 3 and dy <= 3


def spread_term(cell, near):
    best = 99
    for c in near:
        d = tdist(cell, c)
        if d < best:
            best = d
    if best >= 99:
        return 0.0
    return best if best < 8 else 8


def longest_known_ally():
    best = 0
    for aid, (c, ln, r, when) in allies.items():
        if RND - when < 30 and ln > best:
            best = ln
    return best


def build_features():
    tm = threat_map()
    work["threat"] = tm
    work["split_cells"] = split_threat_cells()
    target, far, tscore = choose_target(tm)
    work["target"] = target
    work["far"] = far
    work["tscore"] = tscore


def build_actions():
    body = body_list()
    work["body"] = body
    work["actions"] = candidates(body)


def choose_action():
    tm = work["threat"]
    sc = work["split_cells"]
    target = work["target"]
    far = work["far"]
    tscore = work["tscore"]
    body = work["body"]
    rp = RP[ROLE]
    lvv = lv()
    ends = [res[1] for p, res in work["actions"] if res[0]]
    rdist = reverse_dist(target, ends + [HEAD]) if target >= 0 else {}
    work["rdist"] = rdist
    base_d = rdist.get(HEAD)

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
    for path, res in work["actions"]:
        alive, cell, ln, eaten, struck, nb = res
        k = len(path)
        if not alive:
            if struck is not None:
                their = enemy_len.get(struck, 2)
                their_v = dragon_value(their)
                margin = rp["trade_margin"]
                if RND >= P["end_start"]:
                    margin = max(margin, 1)
                v = their_v - my_v + rp["strike_bonus"] - 0.3 * (k - 1)
                if RND >= P["crown_kill_round"] and ROLE != CROWN and \
                        their >= max(LEN + 1, longest_known_ally()):
                    margin = 0   # their crown outgrows ours: take it off the board
                    v += 10.0
                if their < LEN + margin and UNITS > 2:
                    v -= 50.0    # below this role's trade threshold
                v -= 20.0        # losing the unit's future is never free
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
        if (not P["doom_skip"] or sp < need or nfree < 2) and doom(cell, nb):
            v -= P["w_doom"] * (dragon_value(ln) + 2.0)
        else:
            n_ok += 1
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
        v += spread_term(cell, near_allies) * rp["w_spread"]
        v -= P["w_sprint"] * (k - 1)
        v += ((MY_ID * 31 + path[0] * 13) % 10) * 0.001
        scored.append((v, path, "move"))
    work["n_ok"] = n_ok
    # unpaired portal dives: the only way out of some walled regions
    ds0 = dest(HEAD)
    for d in range(4):
        if ds0[d] == -1 and ek[ekey(HEAD, d)] == 3:
            v = P["w_dive"] - P["dive_risk"]
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
        work["selected"] = None
        return
    scored.sort(key=lambda t: t[0], reverse=True)
    work["selected"] = scored[0]
    if TRACE:
        vis = [c for c in pearls if in_view(c)]
        trace("r%d id%d role%d len%d head%d tgt%d far%d np%d vis%d top=%s" % (
            RND, MY_ID, ROLE, LEN, HEAD, target, far, len(pearls), len(vis),
            [(round(s[0], 2), s[1], s[2]) for s in scored[:4]]))


# =====================================================================
# EXECUTION
# =====================================================================
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
    io.reply["command"] = io.Command.MOVE
    io.reply["argument"] = "".join(DIRS[d] for d in path)


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
                    v = -200.0    # ally head: kills two of ours
                elif o[1]:
                    v = -80.0
                elif o[2]:
                    v = -10.0     # enemy head: at least a trade
                else:
                    v = -60.0
        if v > bv:
            bv = v
            best = d
    return best


def report_doom():
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


def execute_action():
    sel = work["selected"]
    if sel is None:
        d = fallback_move()
        n = dest(HEAD)[d]
        trail.append(n if n >= 0 else HEAD)
        io.reply["command"] = io.Command.MOVE
        io.reply["argument"] = DIRS[d]
        return
    v, act, kind = sel
    if kind == "split":
        n = act
        io.reply["command"] = io.Command.SPLIT
        io.reply["argument"] = str(n)
        # the child's head is our old tail; a ray fired back into our own
        # body exits at the (new) tail and lands on the child's head
        work["split_back"] = neck_dir()
        work["handoff_target"] = work["target"]
        del trail[:-(LEN - n)]
        return
    if kind == "dive":
        # commit_path breaks on the unknown landing without appending a
        # guess; the next turn's trail-mismatch check heals the trail.
        commit_path(act)
        return
    commit_path(act)
    if work["n_ok"] == 0 and len(trail) > 2:
        report_doom()


# =====================================================================
# MESSAGES: what to say, and how to encode it
# =====================================================================
def construct_messages():
    work["messages"] = []


def encode_messages():
    sp = self_packet()
    start = RND & 3
    ng = P["gossip_slots"]
    back = work.get("split_back")
    ho = handoff_packet(work["handoff_target"]) if "handoff_target" in work else None
    sonar = {}
    for j in range(4):
        d = (start + j) & 3
        if back is not None and d == back and ho is not None:
            sonar[DIRS[d]] = ho
        elif ng > 0 and relay_q:
            sonar[DIRS[d]] = relay_q.pop(0)
            ng -= 1
        else:
            sonar[DIRS[d]] = sp
    io.reply["sonar"] = sonar


def record_diagnostics():
    pass


# =====================================================================
# MAIN
# =====================================================================
def boot_turn():
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
        if handoff is not None and handoff >= 0:
            v -= 0.05 * tdist(c, handoff)
        if v > bv:
            bv = v
            best = d
    if best < 0:
        best = fallback_move()
        n = dest(HEAD)[best]
        trail.append(n if n >= 0 else HEAD)
        io.reply["command"] = io.Command.MOVE
        io.reply["argument"] = DIRS[best]
        return
    commit_path([best])


def main():
    first = True
    if not io.read_init():
        return
    initialize_state()
    while io.read_turn():
        work.clear()
        work.update(reports=[], actions=[], selected=None, messages=[],
                    state_updates={})
        # Transport-only fallback: go straight (replaced by execute_action).
        io.reply.clear()
        io.reply.update(command=io.Command.MOVE, argument=io.observation["direction"], sonar={})
        absorb_turn_scalars()
        decode_messages()
        mine = update_state()
        if first:
            seed_trail(mine)
        if first and RND > 0:
            boot_turn()          # newborn child: cheap safe step
        else:
            build_features()
            build_actions()
            choose_action()
            execute_action()
        construct_messages()
        encode_messages()
        record_diagnostics()
        state.update(work["state_updates"])
        io.write_reply()
        first = False


if __name__ == "__main__":
    try:
        main()
    except Exception:
        if TRACE:
            import traceback
            trace("CRASH\n" + traceback.format_exc())
        raise
