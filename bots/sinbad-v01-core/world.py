"""STATE layer: persistent map memory + this turn's view.

Cells are integers c = y * W + x.  Directions 0..3 = N E S W.
Edge keys: c = north edge of cell c; NC + c = west edge of cell c.
Edge kinds (ek): 0 unknown, 1 open, 2 kelp, 3 portal.

Geometry (dest with portal pairing) follows the engine rules; the formula for
portal exits is the same as tools/public_replay_review.py and ouroboros world.py.
"""
import protocol as io

DIRS = "NESW"
REV = (2, 3, 0, 1)

W = H = NC = 0
ME = -1
TEAM = "A"
LIMIT = 64
RND = 0
LEN = 2
UNITS = 1
FACE = 0
HEAD = -1
BORN = -1

ek = None          # bytearray(2 * NC) edge kinds
epid = {}          # portal edge key -> portal id
pends = {}         # portal id -> [edge keys]
NB = None          # torus neighbours cache
DC = None          # destination cache (invalidated when edges are learned)
seen = None        # per cell: last round seen + 1 (0 = never)
bed = None         # per cell: 0 unknown, 1 not a bed, 2 bed
spawn = {}         # bed cell -> predicted round a pearl appears (last countdown seen)
pearls = {}        # cell -> last round a pearl was seen there
visits = None      # per cell: recent head visits (decayed)
trail = []         # own head cells, oldest first
body = []          # own body, tail .. head
occ = {}           # other dragons: cell -> (id, ours, is_head)
enemy_heads = []   # (cell, id, visible length)
ally_heads = []    # (cell, id)
elen = {}          # enemy id -> visible segments
alen = {}          # ally id -> visible segments
echo = (0, 0, 0, 0, 0)
msgs = []


def init():
    global W, H, NC, ME, TEAM, LIMIT, ek, NB, DC, seen, bed, visits
    g = io.game
    ME = g["id"]
    TEAM = g["team"]
    W, H = g["size"]
    LIMIT = g["unit_limit"]
    NC = W * H
    ek = bytearray(2 * NC)
    NB = [None] * NC
    DC = [None] * NC
    seen = [0] * NC
    bed = bytearray(NC)
    visits = bytearray(NC)


# ----------------------------------------------------------------- geometry
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
        return nbr(c)[2]
    if d == 3:
        return NC + c
    return NC + nbr(c)[1]


def _dest_raw(c, d):
    """-1 blocked (kelp), -2 unknown edge, -3 unpaired portal, else the cell."""
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
        return -3
    pk = ends[0] if ends[1] == k else ends[1]
    if pk >= NC:
        pc = pk - NC
        return pc if d == 1 else nbr(pc)[3]
    return pk if d == 2 else nbr(pk)[0]


def dest(c):
    g = DC[c]
    if g is None:
        g = DC[c] = (_dest_raw(c, 0), _dest_raw(c, 1), _dest_raw(c, 2), _dest_raw(c, 3))
    return g


def step_opt(c):
    """Planning neighbours: unknown edges optimistic, kelp / unpaired portals blocked."""
    g = dest(c)
    nb = None
    out = []
    for d in range(4):
        n = g[d]
        if n == -2:
            if nb is None:
                nb = nbr(c)
            n = nb[d]
        out.append(n)
    return out


def _touch(k):
    if k < NC:
        a = k
        b = nbr(k)[0]
    else:
        a = k - NC
        b = nbr(a)[3]
    DC[a] = None
    DC[b] = None


def tdist(a, b):
    dx = abs(a % W - b % W)
    dy = abs(a // W - b // W)
    if dx * 2 > W:
        dx = W - dx
    if dy * 2 > H:
        dy = H - dy
    return dx + dy


def cheb(a, b):
    dx = abs(a % W - b % W)
    dy = abs(a // W - b // W)
    if dx * 2 > W:
        dx = W - dx
    if dy * 2 > H:
        dy = H - dy
    return dx if dx > dy else dy


# ------------------------------------------------------------------- sense
def _learn(k, tok):
    cur = ek[k]
    if tok == ".":
        if cur != 1:
            ek[k] = 1
            _touch(k)
        return
    if tok == "w":
        if cur != 2:
            ek[k] = 2
            _touch(k)
        return
    pid = int(tok)
    if cur != 3:
        ek[k] = 3
        epid[k] = pid
        _touch(k)
    ends = pends.setdefault(pid, [])
    if k not in ends and len(ends) < 2:
        ends.append(k)
        if len(ends) == 2:
            _touch(ends[0])
            _touch(ends[1])


def sense():
    """Observation -> state.  Returns this turn's visible own segments."""
    global RND, LEN, UNITS, FACE, HEAD, echo, msgs, BORN
    ob = io.observation
    RND = ob["round"]
    LEN = ob["length"]
    UNITS = ob["units"]
    FACE = DIRS.index(ob["direction"])
    echo = ob["echoes"]
    msgs = ob["messages"]
    if BORN < 0:
        BORN = RND
    r1 = RND + 1
    tiles = ob["tiles"]
    t = tiles[24]
    HEAD = t[1] * W + t[0]
    for x, y, p, cd in tiles:
        c = y * W + x
        seen[c] = r1
        if p:
            pearls[c] = RND
        elif c in pearls:
            del pearls[c]
        if cd >= 0:
            bed[c] = 2
            spawn[c] = RND + cd
        else:
            bed[c] = 1
    # edges
    hx = HEAD % W
    hy = HEAD // W
    rows = ob["horizontal_edges"]
    for r in range(8):
        base = ((hy - 3 + r) % H) * W
        row = rows[r]
        for col in range(7):
            _learn(base + (hx - 3 + col) % W, row[col])
    rows = ob["vertical_edges"]
    for r in range(7):
        base = NC + ((hy - 3 + r) % H) * W
        row = rows[r]
        for col in range(8):
            _learn(base + (hx - 3 + col) % W, row[col])
    # dragons
    occ.clear()
    del enemy_heads[:]
    del ally_heads[:]
    elen.clear()
    alen.clear()
    mine = []
    for b in ob["bodies"]:
        did = int(b[1])
        c = int(b[3]) * W + int(b[2])
        head = b[5] == "1"
        if did == ME:
            if not head:
                mine.append((c, DIRS.index(b[4][0])))
            continue
        ours = b[0] == TEAM
        occ[c] = (did, ours, head)
        if ours:
            alen[did] = alen.get(did, 0) + 1
            if head:
                ally_heads.append((c, did))
        else:
            elen[did] = elen.get(did, 0) + 1
            if head:
                enemy_heads.append((c, did))
    return mine


def track_body(mine):
    """Maintain trail/body (tail..head).  Reseed from the visible chain if the
    remembered trail disagrees with what we see."""
    global body
    if not trail or trail[-1] != HEAD:
        trail.append(HEAD)
    if len(trail) > 700:
        del trail[:-600]
    ok = len(trail) >= LEN
    if ok:
        bset = set(trail[-LEN:])
        if len(bset) != LEN:
            ok = False
        else:
            for c, d in mine:
                if c not in bset:
                    ok = False
                    break
    if not ok:
        chain = [HEAD]
        left = dict(mine)
        while left:
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
        chain.reverse()
        del trail[:]
        trail.extend(chain)
    body = trail[-LEN:]
    v = visits[HEAD]
    if v < 250:
        visits[HEAD] = v + 1
    if RND % 16 == 0:  # slow decay
        for c in set(trail[-64:]):
            if visits[c]:
                visits[c] -= 1


def prune():
    if RND % 8:
        return
    ttl = 400
    for c in [c for c, r in pearls.items() if RND - r > ttl]:
        del pearls[c]
