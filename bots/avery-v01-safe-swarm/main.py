"""avery-v01-safe-swarm: safety-first foraging swarm (lineage avery, no parent).

One process per dragon.  Layered flow per turn (bahamut-scaffold architecture):

    protocol input -> decode reports -> update state -> build features
    -> build available intentions -> choose intention -> execute intention
    -> construct reports -> encode reports -> diagnostics -> commit -> output

Hypothesis: exact move simulation + flood-fill trap avoidance + a modest
split economy already beats careless swarm bots; conservative movement
(unknown edges are walls, unpaired portals are walls) trades map coverage
for near-zero self-inflicted deaths.

Design notes:
- Torus wrapping everywhere; portal-aware movement once both ends are known.
- Own body is tracked in `trail` (tail first); moving into ANY own segment,
  including the tail that is about to move, is fatal (engine rule).
- Sonar packets: check 8 | kind 4 | payload 52, salted per team.  Kinds:
  SELF, BED (pearl bed + spawn time), ENEMY, PORTAL.  One rotating gossip
  slot per turn, self reports on the remaining rays.
"""
import gc

gc.disable()  # interpreter GC pauses cost judge points; no cycles worth it

import protocol as io

# ======================================================================
# PARAMETERS
# ======================================================================
P = dict(
    unit_value=4.0,        # value of being a unit, in length units
    len_value=1.0,         # value per segment
    len_value_end=3.0,     # ... ramping to this by round 500 (length race)
    end_start=420,         # endgame ramp / trade tightening starts here
    # --- threat model -------------------------------------------------
    p_strike1=0.70,        # chance an enemy head 1 step away strikes
    p_strike2=0.30,
    p_strike3=0.12,
    trade_bias=1.5,        # extra loss felt for an even trade
    threat_reach=3,
    # --- safety ---------------------------------------------------------
    w_trap=12.0,           # per missing tile of escape space below need
    space_slack=4,         # need = my_len + slack reachable tiles
    space_need_cap=40,
    w_space=0.06,          # per reachable tile (up to need)
    w_doom=1.0,            # certain permanent trap: times our value
    w_exit0=5.0,           # new head has no uncontested free neighbour
    w_exit1=1.2,           # ... only one
    w_ally_head_adj=2.5,   # ending next to an ally head (traffic jam)
    w_ally_body_adj=0.3,   # per ally body tile touching our new head
    w_crowd=0.20,          # per ally segment within 2 tiles of our new head
    w_tunnel_head=10.0,    # a head faces us inside the tunnel we enter
    w_tunnel_body=8.0,     # a body blocks the tunnel ahead (following is fatal)
    w_tunnel_unknown=1.0,  # a tunnel that runs on into unseen tiles
    # --- goal field -----------------------------------------------------
    bfs_cap=160,           # cells in the forward target search
    rbfs_cap=240,          # cells in the reverse (to-target) search
    w_goal=1.2,            # per step closer to the chosen target
    w_goal_sprint=0.2,     # ... per extra step gained by sprinting
    goal_far_w=0.5,        # per manhattan step for off-search waypoints
    w_dist=1.0,            # target choice: cost per step
    w_pearl=10.0,
    w_spawn=5.0,
    w_frontier=1.2,        # per unknown side of a reached cell
    pearl_stale=40,        # rounds before a remembered pearl is doubted
    spawn_window=25,       # spawn predictions matter this many rounds ahead
    own_disc=0.3,          # target value kept when another head is clearly closer
    w_visit=0.2,           # per past visit of the destination (anti-dither)
    w_zone_crowd=0.3,      # waypoints: per recent ally report in the zone
    # --- sprint -----------------------------------------------------------
    sprint_max=3,
    w_sprint=1.0,          # extra cost per extra sprint step (beyond the segment)
    # --- production -------------------------------------------------------
    split_min=4,           # parent length before a voluntary split
    child_size=2,
    team_target_small=24,  # desired units, maps <= 600 cells
    team_target_mid=36,    # desired units, maps <= 2000 cells
    team_target_big=56,    # desired units, bigger maps
    w_split=6.0,           # base value of a new unit when below target
    split_crowd_max=10,    # no voluntary split with more ally segments in view
    split_stop=380,        # no voluntary splits after this round
    split_danger_max=0.3,  # no voluntary split with head risk above this
    w_emergency_split=5.0, # shedding the body when every move is fatal
    # --- portals ------------------------------------------------------------
    w_dive=0.5,            # stepping through an unpaired portal (unknown landing)
    # --- sonar -----------------------------------------------------------------
    relay_max=6,
    gossip_slots=1,
    enemy_ttl=2,
)

import os
TRACE = os.path.exists("/tmp/avery-trace-on")


def trace(msg):
    if TRACE:
        with open("/tmp/avery-trace-%s-%d.log" % (TEAM, MY_ID), "a") as fh:
            fh.write(msg + "\n")


DIRS = "NESW"

# ======================================================================
# STATE  (module-level; one process per dragon)
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
BORN = 0
MOVED_DIR = 0

ek = None          # edge kinds, 2*NC: 0 unknown 1 open 2 kelp 3 portal
epid = {}          # portal edge key -> portal id
pends = {}         # portal id -> [edge keys]
unk = None         # per cell: count of unknown sides
seen = None        # per cell: last round seen (0 = never; stored +1)
fertile = None     # per cell: spawns pearls
visits = None      # per cell: head visits
NB = None          # torus neighbour cache
DC = None          # destination cache (invalidated on edge learning)

pearls = {}        # cell -> round seen
spawn_at = {}      # cell -> predicted spawn round
enemies = {}       # enemy id -> (cell, round, len)
allies = {}        # ally id -> (cell, len, round)
trail = []         # our head cells, oldest first (body = last LEN)
relay_q = []       # outgoing gossip packets
relayed = {}       # (kind, payload) -> round relayed (dedupe)
told = {}          # enemy id -> round last broadcast
bed_told = {}      # bed cell -> round last broadcast
portal_told = set()

# per-turn view
occ = {}           # cell -> (dragon id, is_ours, is_head)
enemy_heads = []   # (cell, id)
ally_heads = set()
enemy_len = {}     # enemy id -> visible segment count
echo = (0, 0, 0, 0, 0)
ZS = 8             # zone size for waypoints / heat
ZW = ZH = 1
zone_heat = {}     # zone -> [enemy heat, round]


def setup():
    global ek, unk, seen, fertile, visits, NB, DC, NC, ZW, ZH
    NC = W * H
    ek = bytearray(2 * NC)
    unk = bytearray(b"\x04") * NC
    seen = [0] * NC
    fertile = bytearray(NC)
    visits = bytearray(NC)
    NB = [None] * NC
    DC = [None] * NC
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
    """Edge key of cell c's side d (0 N, 1 E, 2 S, 3 W).
    Horizontal edge k = y*W + x is the NORTH edge of cell (x, y).
    Vertical edge NC + y*W + x is the WEST edge of cell (x, y)."""
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
    if pk >= NC:                     # far end is a vertical edge (west of pc)
        pc = pk - NC
        px = pc % W
        py = pc // W
        if d == 1:
            return pc
        return py * W + (px - 1 if px else W - 1)
    px = pk % W                      # far end is a horizontal edge (north of pk)
    py = pk // W
    if d == 2:
        return pk
    return (py - 1 if py else H - 1) * W + px


def dest(c):
    g = DC[c]
    if g is not None:
        return g
    g = DC[c] = (dest_raw(c, 0), dest_raw(c, 1), dest_raw(c, 2), dest_raw(c, 3))
    return g


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
K_SELF, K_BED, K_ENEMY, K_PORTAL = 1, 2, 3, 4
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
    if v >> 56 != chk(body):
        return None
    return body >> 52, body & ((1 << 52) - 1)


def self_packet():
    return pack(K_SELF, (MY_ID & 0xFFF) << 38 | (HEAD & 0xFFF) << 26
                | (min(LEN, 255) << 18) | (min(UNITS, 127) << 11)
                | (MOVED_DIR & 3) << 9 | (RND & 0x1FF))


def bed_packet(cell, when, ttl):
    return pack(K_BED, (ttl & 3) << 50 | (cell & 0xFFF) << 20 | (when & 0x3FF))


def enemy_packet(cell, ln, eid, ttl):
    return pack(K_ENEMY, (ttl & 3) << 50 | (eid & 0xFFF) << 36 | (cell & 0xFFF) << 24
                | (min(ln, 255) << 16) | (RND & 0x1FF))


def portal_packet(pid):
    a, b = pends[pid][0], pends[pid][1]
    return pack(K_PORTAL, (2 << 50) | (pid & 0xFF) << 32 | (a & 0xFFFF) << 16 | (b & 0xFFFF))


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


# ======================================================================
# ENCODING LAYER: decode reports
# ======================================================================
def decode_messages():
    for v in io.observation["messages"]:
        got = unpack(v)
        if got is None:
            continue
        kind, pl = got
        if kind == K_SELF:
            aid = (pl >> 38) & 0xFFF
            if aid != (MY_ID & 0xFFF):
                cell = (pl >> 26) & 0xFFF
                if cell < NC:
                    allies[aid] = (cell, (pl >> 18) & 0xFF, RND)
        elif kind == K_BED:
            cell = (pl >> 20) & 0xFFF
            if cell < NC and not fertile[cell]:
                fertile[cell] = 1
                when = pl & 0x3FF
                if when > RND:
                    spawn_at[cell] = when
            relay(kind, pl, (pl >> 50) & 3)
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
            if a < 2 * NC and b < 2 * NC:
                for k in (a, b):
                    if ek[k] == 0:
                        ek[k] = 3
                        epid[k] = pid
                        edge_known(k)
                ends = pends.setdefault(pid, [])
                for k in (a, b):
                    if k not in ends and len(ends) < 2:
                        ends.append(k)
                if len(ends) == 2:
                    portal_paired(ends[0])
                    portal_paired(ends[1])
            relay(kind, pl, (pl >> 50) & 3)


# ======================================================================
# STATE LAYER: perception
# ======================================================================
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
            portal_paired(k)   # invalidate destination cache
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


def update_state():
    """Visible information + decoded reports -> persistent state."""
    global HEAD
    tiles = io.observation["tiles"]
    r1 = RND + 1
    for i in range(49):
        t = tiles[i]
        c = t[1] * W + t[0]
        if i == 24:
            HEAD = c
        seen[c] = r1
        if t[2]:
            pearls[c] = RND
        elif c in pearls:
            del pearls[c]
        pt = t[3]
        if pt >= 0:
            if not fertile[c]:
                fertile[c] = 1
                if len(relay_q) < P["relay_max"] and bed_told.get(c, -99) < RND - 80:
                    bed_told[c] = RND
                    relay_q.append(bed_packet(c, RND + pt, 2))
            if not t[2]:
                spawn_at[c] = RND + (pt if pt > 0 else 1)
    occ.clear()
    del enemy_heads[:]
    ally_heads.clear()
    enemy_len.clear()
    mine = []
    for b in io.observation["bodies"]:
        did = int(b[1])
        c = int(b[3]) * W + int(b[2])
        is_head = b[5] == "1"
        if did == MY_ID:
            if not is_head:
                mine.append((c, DIRS.index(b[4][0])))
            continue
        ours = b[0] == TEAM
        occ[c] = (did, ours, is_head)
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
    rows_h = io.observation["horizontal_edges"]
    for r in range(8):
        base = ((hy - 3 + r) % H) * W
        row = rows_h[r]
        for col in range(7):
            learn(base + (hx - 3 + col) % W, row[col])
    rows_v = io.observation["vertical_edges"]
    for r in range(7):
        base = NC + ((hy - 3 + r) % H) * W
        row = rows_v[r]
        for col in range(8):
            learn(base + (hx - 3 + col) % W, row[col])
    return mine


def seed_trail(mine):
    """First turn: rebuild the body from visible own segments (tail first).
    A body segment faces towards its head: its forward neighbour is the
    next segment towards the head."""
    if trail:
        return
    chain = [HEAD]
    left = dict(mine)
    while len(chain) < LEN and left:
        cur = chain[-1]
        nxt = -1
        for c, d in left.items():
            if dest(c)[d] == cur or nbr(c)[d] == cur:
                nxt = c
                break
        if nxt < 0:
            break
        del left[nxt]
        chain.append(nxt)
    trail.extend(reversed(chain))


def body_list():
    n = LEN if LEN < len(trail) else len(trail)
    return trail[-n:]


def prune():
    for c in [c for c, r in pearls.items() if RND - r > 80]:
        del pearls[c]
    for c in [c for c, w in spawn_at.items() if w < RND - 30]:
        del spawn_at[c]
    for k in [k for k, v in enemies.items() if RND - v[1] > 40]:
        del enemies[k]
    for k in [k for k, v in allies.items() if RND - v[2] > 40]:
        del allies[k]
    for k in [k for k, r in relayed.items() if RND - r > 40]:
        del relayed[k]


# ======================================================================
# FEATURE LAYER
# ======================================================================
def threat_map():
    """cell -> list of (steps, enemy id) within every visible enemy head's
    sprint reach.  Paths go through free tiles only; the strike destination
    itself may be occupied (it lands wherever our head ends up)."""
    tm = {}
    reach_cap = P["threat_reach"]
    for ec, eid in enemy_heads:
        ln = enemy_len.get(eid, 2)
        reach = min(reach_cap, max(1, ln - 1))   # visible count is a lower bound
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


def lv():
    """Value of one segment: ramps up towards the round-500 length race."""
    a = P["len_value"]
    b = P["len_value_end"]
    s = P["end_start"] - 100
    if RND <= s:
        return a
    f = (RND - s) / (500.0 - s)
    return a + (b - a) * (f if f < 1 else 1)


def dragon_value(ln):
    return P["unit_value"] + lv() * ln


def head_risk(cell, my_len_after, tm):
    """Expected material loss from enemy strikes on this head tile."""
    lst = tm.get(cell)
    if not lst:
        return 0.0
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
    return (1.0 - survive) * worst


def simulate(path, body):
    """Apply a step list to our body (tail-first list).  Returns
    (alive, head, len, eaten, struck_enemy_id, new_body) with exact engine
    rules: each sprint step beyond the first costs one segment; entering our
    own tail kills us even though that tail would have moved; entering an
    enemy head kills both; entering anything else occupied kills only us."""
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
                return (False, n, ln, eaten, o[0], b)   # strike: both die
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


def flood(start, body, cap):
    """Tiles reachable from start avoiding occupied cells; our own body frees
    up from the tail as we move (segment i frees after i+1 steps)."""
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
            if n < 0 or n in got or n in occ:
                continue
            j = bset.get(n)
            if j is not None and j >= dep - 1:
                continue
            got[n] = dep
            q.append(n)
    return len(got)


def doom(start, body):
    """Permanent-trap test ignoring other dragons (they move) but not our own
    body.  Returns -1 when the region is open or unknown, else the number of
    known pearls inside: the region is enclosed by kelp/our body and cannot
    hold us (too small, or acyclic: a dead end we can never turn around in)."""
    bset = {}
    for i, c in enumerate(body):
        bset[c] = i
    cap = 3 * len(body) + 12
    if cap > 40:
        cap = 40
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
                    return -1   # unknown edge / unpaired portal: maybe an exit
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
    cyclic = edges // 2 >= size   # every internal edge counted from both ends
    if size < len(body) + 2 or not cyclic:
        n = 0
        for c in got:
            if c in pearls:
                n += 1
        return n
    return -1


def tunnel_ahead(cell, came):
    """Walk forward through a 1-wide tunnel from cell (entered from `came`).
    Unknown side edges do not end the walk (tunnels run beyond our window);
    a known junction does.  Returns 2 if a head (visible, or an ally's recent
    self report) sits in the tunnel ahead, 1 if a body blocks it, 3 if the
    tunnel runs on into the unknown, else 0."""
    prev = came
    cur = cell
    heading = -1
    for d in range(4):
        if dest(came)[d] == cell or nbr(came)[d] == cell:
            heading = d
    recent = [ac for ac, ln, when in allies.values() if RND - when <= 2]
    steps = 0
    for _ in range(14):
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
bmark = None
bdist = None
bstamp = 0


def choose_target(tm):
    """Forward BFS from the head; score cells as targets.
    Returns (target cell, far waypoint cell or -1, best score)."""
    global bstamp
    bstamp += 1
    st = bstamp
    cap = P["bfs_cap"]
    w_dist = P["w_dist"]
    window = P["spawn_window"]
    stale = P["pearl_stale"]
    q = [HEAD]
    bmark[HEAD] = st
    bdist[HEAD] = 0
    qi = 0
    best = -1
    best_s = -1e9
    body = set(body_list())
    # pearls a clearly closer ally head will take: leave them
    others = [c for c, v in occ.items() if v[2] and v[1] and tdist(c, HEAD) <= 8]
    for c, ln, when in allies.values():
        if RND - when <= 1 and tdist(c, HEAD) <= 10:
            others.append(c)
    while qi < len(q) and len(q) < cap:
        c = q[qi]
        qi += 1
        dn = bdist[c] + 1
        for n in dest(c):
            if n < 0 or bmark[n] == st or n in occ or n in body:
                continue
            bmark[n] = st
            bdist[n] = dn
            q.append(n)
            s = 0.0
            pr = pearls.get(n)
            if pr is not None:
                s += P["w_pearl"] if RND - pr < stale else P["w_pearl"] * 0.4
            else:
                sp = spawn_at.get(n)
                if sp is not None:
                    lag = sp - (RND + dn)
                    if -4 <= lag <= window:
                        s += P["w_spawn"] * (1.0 - (lag if lag > 0 else -lag) / (window + 4.0))
            if unk[n]:
                s += P["w_frontier"] * 0.25 * unk[n]
            if s <= 0.0:
                continue
            if others:
                for oc in others:
                    if tdist(oc, n) + 1 < dn:
                        s *= P["own_disc"]
                        break
            s -= w_dist * dn
            if n in tm:
                s -= 3.0
            if s > best_s:
                best_s = s
                best = n
    far = -1
    if best_s < 1.0:
        far = waypoint()
        if far >= 0 and bmark[far] == st:
            best = far
            best_s = 1.0
    return best, far, best_s


def waypoint():
    """Strategic target when nothing local is worth chasing: a stale,
    uncrowded zone centre, salted per dragon to spread the swarm."""
    best_c = -1
    bs = -1e9
    hx = HEAD % W
    hy = HEAD // W
    salt = (MY_ID * 7919) & 0xFFFF
    zone_allies = {}
    for c, ln, when in allies.values():
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
            s = 1.5 * min(age, 200) / 40.0
            s -= P["w_zone_crowd"] * zone_allies.get(z, 0)
            s -= 0.08 * d
            hz = zone_heat.get(z)
            if hz is not None:
                s -= 2.0 * min(hz[0] * (0.977 ** (RND - hz[1])), 4.0)
            s += ((salt + z * 131) % 97) / 97.0 * 1.5
            if s > bs:
                bs = s
                best_c = c
    return best_c


def reverse_dist(target, wanted):
    """BFS distances from target over known passable cells (approximate:
    symmetric edges, exact except one-way portal geometry)."""
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
# DECISION LAYER
# ======================================================================
def team_target():
    if NC <= 600:
        t = P["team_target_small"]
    elif NC <= 2000:
        t = P["team_target_mid"]
    else:
        t = P["team_target_big"]
    return min(t, UNIT_LIMIT)


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


def split_value(risk_here):
    """Voluntary production: value of splitting off child_size segments now,
    or None when illegal/unwise.  Illegal splits are fatal, so check hard."""
    if RND >= P["split_stop"] or LEN < P["split_min"] or UNITS >= UNIT_LIMIT:
        return None
    n = P["child_size"]
    if LEN - n < 2:
        return None
    target = team_target()
    if UNITS >= target:
        return None
    if risk_here > P["split_danger_max"] * P["unit_value"]:
        return None
    crowd = 0
    for o in occ.values():
        if o[1]:
            crowd += 1
    if crowd > P["split_crowd_max"]:
        return None
    # the newborn's head is our tail cell, facing away from our body:
    # it must have somewhere to go
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
        # a newborn entering an occupied/doomed corridor dies within a turn
        if tunnel_ahead(m, ch):
            continue
        if doom(m, [ch, m]) >= 0:
            continue
        ok += 1
    if ok == 0:
        return None
    frac = UNITS / float(target)
    return P["w_split"] * (1.2 - frac) - (1.0 if ok == 1 else 0.0), n


def candidates(body):
    """Single steps always; sprints only when they can matter: a visible
    enemy head is close (strike / escape), or step one eats a pearl (the
    growth pays for the sprint segment)."""
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
    body = body_list()
    tm = threat_map()
    target, far, tscore = choose_target(tm)
    cands = candidates(body)
    ends = [res[1] for p, res in cands if res[0]]
    rdist = reverse_dist(target, ends + [HEAD]) if target >= 0 else {}
    base_d = rdist.get(HEAD)

    best = None
    my_v = dragon_value(LEN)
    need = LEN + P["space_slack"]
    if need > P["space_need_cap"]:
        need = P["space_need_cap"]
    scored = []
    n_ok = 0
    lvv = lv()
    ally_segs = [(c % W, c // W) for c, o in occ.items() if o[1]]
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
                # trade: both die; worth it only when they are clearly longer
                their = enemy_len.get(struck, 2)
                their_v = dragon_value(their)
                margin = 2 if RND < P["end_start"] else 0
                v = their_v - my_v - 0.3 * (k - 1)
                if their < LEN + margin or UNITS <= 2:
                    v -= 50.0
                scored.append((v, path, "strike"))
            continue
        v = lvv * (ln - LEN)                    # sprint cost, pearls eaten
        v -= head_risk(cell, ln, tm)
        sp = flood(cell, nb, need + 1)
        if sp < need:
            v -= P["w_trap"] * (need - sp) / float(need) * (1.0 + ln * 0.1)
        v += P["w_space"] * min(sp, need)
        nfree = 0
        ex = 0.0
        nbs = set(nb)
        for m in dest(cell):
            if m >= 0 and m not in occ and m not in nbs:
                nfree += 1
                ex += 0.5 if m in contested else 1.0
        # the permanent-trap test is the expensive one: skip it where the
        # flood found room and the head has two ways on
        dm = -1
        if sp < need or nfree < 2:
            dm = doom(cell, nb)
        if dm < 0:
            n_ok += 1
        else:
            v -= P["w_doom"] * (dragon_value(ln) + 2.0)
        th = tunnel_ahead(cell, nb[-2] if len(nb) > 1 else HEAD)
        if th == 2:
            v -= P["w_tunnel_head"]
        elif th == 1:
            v -= P["w_tunnel_body"]
        elif th == 3:
            v -= P["w_tunnel_unknown"]
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
        v -= P["w_visit"] * visits[cell]
        v -= P["w_sprint"] * (k - 1)
        v += ((MY_ID * 31 + RND * 7 + path[0] * 13) % 10) * 0.001
        scored.append((v, path, "move"))
    if n_ok == 0 and len(trail) > 2:
        es = emergency_split()
        if es:
            scored.append((P["w_emergency_split"], es, "split"))
    # unpaired portal beside us: an unknown landing, only when desperate/bored
    ds0 = dest(HEAD)
    for d in range(4):
        if ds0[d] == -1 and ek[ekey(HEAD, d)] == 3:
            v = P["w_dive"] - 1.0
            if tscore < 1.0:
                v += 1.5
            scored.append((v, [d], "dive"))
    risk_here = head_risk(HEAD, LEN, tm)
    sv = split_value(risk_here)
    if sv is not None:
        v, n = sv
        v -= risk_here * 0.5
        scored.append((v, n, "split"))
    if not scored:
        if TRACE:
            trace("r%d id%d NOSCORE head%d body%s dest%s" % (RND, MY_ID, HEAD, body, dest(HEAD)))
        return None
    scored.sort(key=lambda t: t[0], reverse=True)
    if TRACE:
        trace("r%d id%d DECIDE head%d body%s top=%s" % (
            RND, MY_ID, HEAD, body, [(round(s[0], 2), s[1], s[2]) for s in scored[:4]]))
    return scored[0]


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
                    v = -200.0   # ally head: kills two of ours
                elif o[1]:
                    v = -80.0
                elif o[2]:
                    v = -10.0    # enemy head: at least a trade
                else:
                    v = -60.0
        if v > bv:
            bv = v
            best = d
    return best


# ======================================================================
# EXECUTION LAYER
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
    io.reply.update(command=io.Command.MOVE, argument="".join(DIRS[d] for d in path))


def execute_action(selected):
    if selected is None:
        d = fallback_move()
        n = dest(HEAD)[d]
        trail.append(n if n >= 0 else HEAD)
        io.reply.update(command=io.Command.MOVE, argument=DIRS[d])
        return
    v, act, kind = selected
    if kind == "split":
        n = act
        io.reply.update(command=io.Command.SPLIT, argument=str(n))
        # our body after the split: we keep the head end
        del trail[:-(LEN - n)]
        work["state_updates"]["split_this_turn"] = True
        return
    # "move" and "dive" both translate to a movement command
    if kind == "dive":
        # destination unknown: step through, trail catches up next turn
        io.reply.update(command=io.Command.MOVE, argument=DIRS[act[0]])
        return
    commit_path(act)


def send_sonars():
    """Gossip (relay queue) takes up to gossip_slots rays, rotating; every
    other ray carries our self report (position + heading + length)."""
    sp = self_packet()
    start = RND & 3
    ng = P["gossip_slots"]
    sonar = {}
    for j in range(4):
        d = (start + j) & 3
        if ng > 0 and relay_q:
            sonar[DIRS[d]] = relay_q.pop(0)
            ng -= 1
        else:
            sonar[DIRS[d]] = sp
    io.reply["sonar"] = sonar


def construct_messages():
    send_sonars()


# ======================================================================
# MAIN LOOP
# ======================================================================
def boot_turn(mine):
    """First turn of a new (split-child) process: interpreter boot ate most
    of the budget.  Take the safest single step."""
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
        if v > bv:
            bv = v
            best = d
    if best < 0:
        d = fallback_move()
        n = dest(HEAD)[d]
        trail.append(n if n >= 0 else HEAD)
        io.reply.update(command=io.Command.MOVE, argument=DIRS[d])
    else:
        commit_path([best])
    send_sonars()


def take_turn():
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
    selected = decide()
    execute_action(selected)
    send_sonars()


work = {"state_updates": {}}


def main():
    global W, H, MY_ID, TEAM, UNIT_LIMIT, RND, LEN, UNITS, FACING, echo, BORN, SALT
    if not io.read_init():
        return
    MY_ID = io.game["id"]
    TEAM = io.game["team"]
    W, H = io.game["size"]
    UNIT_LIMIT = io.game["unit_limit"]
    SALT = 0x5A if TEAM == "A" else 0xC3
    setup()
    global bmark, bdist
    bmark = [0] * NC
    bdist = [0] * NC
    first = True
    while io.read_turn():
        RND = io.observation["round"]
        FACING = DIRS.index(io.observation["direction"][0])
        LEN = io.observation["length"]
        UNITS = io.observation["units"]
        echo = io.observation["echoes"]
        work["state_updates"] = {}
        io.reply.clear()
        io.reply.update(command=io.Command.MOVE, argument=io.observation["direction"], sonar={})
        if first:
            BORN = RND
        decode_messages()
        mine = update_state()
        if first:
            seed_trail(mine)
        elif trail and trail[-1] != HEAD:
            # a dive through an unpaired portal teleports the head somewhere
            # dest() cannot know: the stored trail is no longer contiguous.
            prev = trail[-1]
            if HEAD not in dest(prev) and HEAD not in nbr(prev):
                del trail[:]
                seed_trail(mine)   # rebuild from the segments we can see
        if trail and trail[-1] != HEAD:
            trail.append(HEAD)
        if len(trail) > 400:
            del trail[:-300]
        if first and RND > 0:
            boot_turn(mine)
        else:
            take_turn()
        if TRACE:
            trace("r%d id%d len%d head%d trail%s reply=%s %s" % (
                RND, MY_ID, LEN, HEAD, body_list(),
                io.reply["command"].value, io.reply["argument"]))
        state_updates = work["state_updates"]
        if state_updates:
            pass   # v01 keeps all state in module globals; nothing to commit
        io.write_reply()
        first = False


if __name__ == "__main__":
    main()
