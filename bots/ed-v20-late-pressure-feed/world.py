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
fork_focus = -1
fork_until = -1
fork_received_round = -1

ek = None          # bytearray(2 * NC) edge kinds
epid = {}          # portal edge key -> portal id
pends = {}         # portal id -> [edge keys]
NB = None          # torus neighbours cache
OPT = None         # optimistic planning neighbours cache
DC = None          # destination cache (invalidated when edges are learned)
seen = None        # per cell: last round seen + 1 (0 = never)
bed = None         # per cell: 0 unknown, 1 not a bed, 2 bed
spawn = {}         # bed cell -> predicted round a pearl appears (last countdown seen)
bper = {}          # bed cell -> largest countdown seen (period estimate; 1 = regrows every round)
pearls = {}        # cell -> last round a pearl was seen there
visits = None      # per cell: recent head visits (decayed)
SEC = 8            # sector size for exploration bookkeeping
SW = SH = 0
sec_unseen = None  # per sector: tiles never seen
trail = []         # own head cells, oldest first
body = []          # own body, tail .. head
occ = {}           # other dragons: cell -> (id, ours, is_head)
vac = {}           # other dragons: cell -> our move number from which it is free
cut = set()        # other dragon ids whose body runs out of view (longer than seen)
enemy_heads = []   # (cell, id, visible length)
ally_heads = []    # (cell, id)
elen = {}          # enemy id -> visible segments
alen = {}          # ally id -> visible segments
echo = (0, 0, 0, 0, 0)
msgs = []
crown = None       # [id, head cell, length, round reported] of the elected crown
prey = None        # [id, head cell, length, round seen] of the longest enemy we know


def init():
    global W, H, NC, ME, TEAM, LIMIT, ek, NB, DC, OPT, seen, bed, visits, SW, SH, sec_unseen
    g = io.game
    ME = g["id"]
    TEAM = g["team"]
    W, H = g["size"]
    LIMIT = g["unit_limit"]
    NC = W * H
    ek = bytearray(2 * NC)
    NB = [None] * NC
    DC = [None] * NC
    OPT = [None] * NC
    seen = [0] * NC
    bed = bytearray(NC)
    visits = bytearray(NC)
    SW = (W + SEC - 1) // SEC
    SH = (H + SEC - 1) // SEC
    sec_unseen = [0] * (SW * SH)
    for sy in range(SH):
        hh = min(SEC, H - sy * SEC)
        for sx in range(SW):
            sec_unseen[sy * SW + sx] = hh * min(SEC, W - sx * SEC)


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
    """Planning neighbours: unknown edges optimistic (-2 -> the torus
    neighbour), kelp -1, unpaired portal -3.  Cached with dest()."""
    g = OPT[c]
    if g is None:
        d4 = dest(c)
        nb = nbr(c)
        g = OPT[c] = tuple(nb[d] if d4[d] == -2 else d4[d] for d in range(4))
    return g


def _touch(k):
    if k < NC:
        a = k
        b = nbr(k)[0]
    else:
        a = k - NC
        b = nbr(a)[3]
    DC[a] = None
    DC[b] = None
    OPT[a] = None
    OPT[b] = None


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


def learn_pair(k1, k2, pid):
    """A portal pairing heard by sonar (both edge keys and the id)."""
    if k1 >= 2 * NC or k2 >= 2 * NC or k1 == k2:
        return
    for k in (k1, k2):
        if ek[k] != 3:
            ek[k] = 3
            epid[k] = pid
            _touch(k)
    ends = pends.get(pid)
    if ends is None or len(ends) < 2:
        pends[pid] = [k1, k2]
        _touch(k1)
        _touch(k2)


def paired():
    return [(pid, e) for pid, e in pends.items() if len(e) == 2]


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
        if not seen[c]:
            sec_unseen[(y // SEC) * SW + x // SEC] -= 1
        seen[c] = r1
        if p:
            pearls[c] = RND
        elif c in pearls:
            del pearls[c]
        if cd >= 0:
            bed[c] = 2
            spawn[c] = RND + cd
            if cd > bper.get(c, 0):
                bper[c] = cd
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
    segdir = {}
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
        segdir[c] = DIRS.index(b[4][0])
        if ours:
            alen[did] = alen.get(did, 0) + 1
            if head:
                ally_heads.append((c, did))
        else:
            elen[did] = elen.get(did, 0) + 1
            if head:
                enemy_heads.append((c, did))
    _vacancy(segdir)
    for c, eid in enemy_heads:
        ln = elen.get(eid, 1) + (2 if eid in cut else 0)
        see_prey(eid & 4095, c, ln, RND)
    return mine


def see_prey(did, cell, ln, rnd):
    global prey
    if ln < PREY_MIN[0]:
        return
    p = prey
    if p is None or RND - p[3] > PREY_TTL[0] or did == p[0] and rnd >= p[3] or ln > p[2]:
        prey = [did, cell, ln, rnd]


PREY_MIN = [8]
PREY_TTL = [15]


def _links(cur):
    """Cells a body can continue into from cur (open edge, portal, unknown edge)."""
    out = []
    g = dest(cur)
    for d in range(4):
        n = g[d]
        if n == -2:
            n = nbr(cur)[d]
        if n >= 0:
            out.append(n)
    return out


def _next_seg(cur, cands, dirs):
    """Pick the segment behind cur: its direction points at cur (normal), or
    straight away from cur (a newborn keeps its parent's directions), else any."""
    if len(cands) == 1:
        return cands[0]
    for n in cands:
        d = dirs.get(n)
        if d is not None and (dest(n)[d] == cur or nbr(n)[d] == cur):
            return n
    for n in cands:
        d = dirs.get(n)
        if d is not None and (dest(n)[d ^ 2] == cur or nbr(n)[d ^ 2] == cur):
            return n
    return cands[0]


def _vacancy(segdir):
    """Other bodies: segment i from the (visible) tail is free from our move
    i + 2 (the owner moves at least once per round, may not have moved yet).
    A chain whose rear end sits on the view border may continue: add T_HIDDEN.
    Chains are walked from visible heads by adjacency (newborns keep their
    parent's segment directions, which point the wrong way)."""
    vac.clear()
    cut.clear()
    hx = HEAD % W
    hy = HEAD // W

    def border(c):
        dx = abs(c % W - hx)
        dy = abs(c // W - hy)
        if dx * 2 > W:
            dx = W - dx
        if dy * 2 > H:
            dy = H - dy
        return dx >= 3 or dy >= 3

    for h, o in list(occ.items()):
        if not o[2]:
            continue
        did = o[0]
        chain = [h]
        seen = {h}
        while len(chain) < 400:
            cur = chain[-1]
            cands = [n for n in _links(cur) if n not in seen and n in segdir
                     and occ[n][0] == did and not occ[n][2]]
            if not cands:
                break
            n = _next_seg(cur, cands, segdir)
            chain.append(n)
            seen.add(n)
        i = 0
        if border(chain[-1]):
            i = T_HIDDEN[0]
            cut.add(did)
        for c in reversed(chain):
            vac[c] = i + 2
            i += 1
    # bodies whose head is out of view: follow segment directions
    nxt = {}
    pointed = set()
    for c, d in segdir.items():
        if c in vac or occ[c][2]:
            continue
        n = dest(c)[d]
        if n < 0:
            n = nbr(c)[d]
        o = occ.get(n)
        if o is not None and o[0] == occ[c][0] and n not in vac:
            nxt[c] = n
            pointed.add(n)
    for c in segdir:
        if c in pointed or c in vac:
            continue
        i = 0
        if border(c):
            i = T_HIDDEN[0]
            cut.add(occ[c][0])
        cur = c
        guard = 0
        while cur is not None and guard < 400:
            vac[cur] = i + 2
            i += 1
            cur = nxt.get(cur)
            guard += 1
    for c in segdir:
        if c not in vac:
            vac[c] = 99


T_HIDDEN = [6]  # set from params.P["t_hidden"] by main


def io_tiles():
    return io.observation["tiles"]


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
                # a newborn's segments keep the parent's directions (they point
                # away from our head): link by adjacency instead
                lk = _links(cur)
                for c in left:
                    if c in lk:
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


def sector_target():
    """Centre of the nearest sector with never-seen tiles (ties rotate by id)."""
    best = -1
    bd = 1 << 30
    hx = HEAD % W
    hy = HEAD // W
    n = SW * SH
    off = (ME * 7) % n if n else 0
    for k in range(n):
        s = (k + off) % n
        if sec_unseen[s] <= 0:
            continue
        cx = min(W - 1, (s % SW) * SEC + SEC // 2)
        cy = min(H - 1, (s // SW) * SEC + SEC // 2)
        dx = abs(cx - hx)
        dy = abs(cy - hy)
        if dx * 2 > W:
            dx = W - dx
        if dy * 2 > H:
            dy = H - dy
        if dx + dy < bd:
            bd = dx + dy
            best = cy * W + cx
    return best
