"""STATE/FEATURES: shared estimates of allied and enemy dragon MASS (segments).

Adapted from Aramis's density.py (counts of dragons) to body length, because
a region holding one 30-long enemy is not the same as one holding a 2-long one.

Each dragon keeps an EWMA of what it sees: allied segments (its own length
included) and enemy segments in its 7x7 view, at an EWMA sensor position.
It broadcasts that as a T_MASS packet; receivers keep ONE latest report per
original sender (relays never refresh age). Evidence decays with half-life
`mass_half_life` rounds and is forgotten after 4 half-lives.

Game-relative directional features for this dragon (never compass constants):
  e_mass, a_mass   distance-weighted enemy / allied segments around us (others only)
  e_vec, a_vec     unit vectors from our head toward that mass (dx, dy) or None
  e_dist           mass-weighted mean toroidal distance to enemy evidence
  balance          (E - A) / (A + E + 1) at our head from the smoothed field
Kernel: weight = decay(age) / (1 + d / mass_scale), sources with d > mass_range ignored.
"""
import math
import world as w
import comms
from params import P

LOCAL = None
LAST_HEAD = -1
REPORTS = {}   # sender -> (x, y, aseg, eseg, round, packet)
ACTIVE = []    # (x, y, aseg, eseg, decay)
DECAY = []
TTL = 0
F = {}


def init():
    global TTL, DECAY
    hl = P["mass_half_life"]
    TTL = min(64, max(4, int(4 * hl)))
    DECAY = [0.5 ** (age / hl) for age in range(TTL + 1)]


def delta(a, b, size):
    return (b - a + size * 0.5) % size - size * 0.5


def hear(report, packet):
    did, x, y, aa, ee, rnd = report
    if did == (w.ME & 511):
        return
    age = w.RND - rnd
    if not 0 <= age <= TTL:
        return
    prev = REPORTS.get(did)
    if prev is not None and rnd <= prev[4]:
        return
    REPORTS[did] = (x, y, aa, ee, rnd, packet)
    if len(REPORTS) > P["mass_sources"]:
        oldest = min(REPORTS, key=lambda k: (REPORTS[k][4], k))
        del REPORTS[oldest]


def observe():
    """After world.sense(): update the local EWMA, expire reports, build features."""
    global LOCAL, LAST_HEAD
    aa = float(w.LEN + sum(w.alen.values()))
    ee = float(sum(w.elen.values()))
    x, y = w.HEAD % w.W, w.HEAD // w.W
    hl = P["mass_half_life"]
    if LOCAL is None or LAST_HEAD < 0 or w.tdist(LAST_HEAD, w.HEAD) > 3:
        LOCAL = (float(x), float(y), aa, ee, w.RND)
    else:
        px, py, pa, pe, rnd = LOCAL
        retain = 0.5 ** (max(0, w.RND - rnd) / hl)
        g = 1.0 - retain
        LOCAL = ((px + g * delta(px, x, w.W)) % w.W, (py + g * delta(py, y, w.H)) % w.H,
                 retain * pa + g * aa, retain * pe + g * ee, w.RND)
    LAST_HEAD = w.HEAD
    for did in [d for d, r in REPORTS.items() if w.RND - r[4] > TTL]:
        del REPORTS[did]
    del ACTIVE[:]
    for x0, y0, a0, e0, rnd, _ in REPORTS.values():
        ACTIVE.append((x0, y0, a0, e0, DECAY[w.RND - rnd]))
    _features(x, y, ee)


def _features(hx, hy, e_view):
    rng = P["mass_range"]
    sc = P["mass_scale"]
    ea = aa = 0.0
    ex = ey = ax = ay = 0.0
    edsum = 0.0
    for x0, y0, a0, e0, dec in ACTIVE:
        dx = delta(hx, x0, w.W)
        dy = delta(hy, y0, w.H)
        d = abs(dx) + abs(dy)
        if d > rng:
            continue
        k = dec / (1.0 + d / sc)
        nd = max(1.0, d)
        if e0 > 0:
            m = k * e0
            ea += m
            ex += m * dx / nd
            ey += m * dy / nd
            edsum += m * d
        if a0 > 0:
            m = k * a0
            aa += m
            ax += m * dx / nd
            ay += m * dy / nd
    # enemies in our own view count at distance ~2 with full weight
    for c, eid in w.enemy_heads:
        dx = delta(hx, c % w.W, w.W)
        dy = delta(hy, c // w.W, w.H)
        d = abs(dx) + abs(dy)
        m = float(w.elen.get(eid, 1))
        ea += m
        ex += m * dx / max(1.0, d)
        ey += m * dy / max(1.0, d)
        edsum += m * d
    F["e_mass"] = ea
    F["a_mass"] = aa
    F["e_vec"] = _unit(ex, ey)
    F["a_vec"] = _unit(ax, ay)
    F["e_dist"] = edsum / ea if ea > 0 else None
    F["sources"] = len(ACTIVE)
    loc = LOCAL
    A = loc[2] + aa * 0.5
    E = loc[3] + ea * 0.5
    F["balance"] = (E - A) / (A + E + 1.0)


def _unit(x, y):
    n = math.sqrt(x * x + y * y)
    if n < 1e-6:
        return None
    return (x / n, y / n, n)


def waypoint(vec, dist):
    """Cell `dist` steps from the head along a unit vector (None if no vector)."""
    if vec is None:
        return -1
    dx = int(round(vec[0] * dist))
    dy = int(round(vec[1] * dist))
    return ((w.HEAD // w.W + dy) % w.H) * w.W + (w.HEAD % w.W + dx) % w.W


def schedule(legacy):
    """Put our mass report on idle rays; optionally displace food gossip.

    Crown, prey, portal and handoff packets are never displaced. Every other
    turn one ray relays a peer's latest report unchanged (age preserved).
    """
    if LOCAL is None or P["mass_rays"] <= 0 or (w.RND + w.ME) % P["mass_period"]:
        return legacy
    x, y, aa, ee, rnd = LOCAL
    pkt = comms.mass_packet(w.ME, x, y, aa, ee, rnd)
    if pkt is None:
        return legacy
    out = dict(legacy)
    off = (w.RND + w.ME) % 4
    dirs = [w.DIRS[(off + k) % 4] for k in range(4)]
    sel = [d for d in dirs if d not in out]
    for d in dirs:
        if len(sel) >= P["mass_rays"]:
            break
        if d not in sel and ((out.get(d, 0) >> 8) & 15) == comms.T_FOOD:
            sel.append(d)
    relay = None
    if REPORTS and w.RND % 2:
        peers = sorted(REPORTS)
        relay = REPORTS[peers[(w.RND // 2 + w.ME) % len(peers)]][5]
    for k, d in enumerate(sel):
        out[d] = relay if (k == 1 and relay is not None) else pkt
    return out
