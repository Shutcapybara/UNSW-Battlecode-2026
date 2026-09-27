"""world.py -- IO, persistent world model, geometry, SENSE.

State: terrain edges (ek/epid/pends), pearls, spawn_at, enemies, allies,
zone heat, our trail; per-turn view: occ, enemy_heads, ally_heads, enemy_len.
Uses (other modules): P, relay_q, bed_packet, portal_packet (comms).
"""

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
body_seen = {}     # cell -> last round a non-self dragon segment was observed
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
    apply_doctrine(NC)


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


FEED = [-1]
CROWN_INFO = [-1, 0, -99]   # cell, length, round heard (relayed crown beacon)
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
        body_seen[c] = RND
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


def in_view(c):
    dx = abs(c % W - HEAD % W)
    dy = abs(c // W - HEAD // W)
    if dx * 2 > W:
        dx = W - dx
    if dy * 2 > H:
        dy = H - dy
    return dx <= 3 and dy <= 3


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
