"""STATE layer: directional LENGTH density (per-quadrant swarm estimates).

Complements density.py (aggregate dragon COUNTS) with sender-relative
directional information: how much allied/enemy visible LENGTH lies in each
of the four quadrants around an observer.  Quadrants are defined relative to
the reporting dragon (game-relative evidence), encoded in the map frame via
the sender's reported position (comms.T_SWARM).

    quadrant(dx, dy) over wrapped view offsets, each tile in exactly one:
      q0: dx >= 0, dy > 0     q1: dx > 0, dy <= 0
      q2: dx <= 0, dy < 0     q3: dx < 0, dy >= 0   (incl. the centre tile)

Each source contributes ONE latest report PER QUADRANT, keyed by
(sender, quadrant); senders rotate quadrants each turn and jump to the
enemy-heaviest quadrant while in contact (scenario-tagged rotation).  The
field places each quadrant sample at sender position + QOFF[quadrant] and
applies the same separable triangular kernel and temporal decay as
density.py.  No evidence gives zero confidence, never proof of safety.
"""
import world as w
import comms
from params import P

LOCAL = None   # x, y, [ally len per quad], [enemy len per quad], round (EWMA)
CUR = None     # this turn's RAW (qa, qe) quadrant counts (for reporting)
LAST_HEAD = -1
REPORTS = {}   # (sender, quad) -> (x, y, ally_len, enemy_len, round, packet)
ACTIVE = []    # this turn's bounded (x, y, ally_len, enemy_len, decay)
AGES = []      # parallel to ACTIVE: report ages (x06 short-window fields)
CACHE = {}
DECAY = []
SHORT_DECAY = []   # x06: decay table for the short window (ewma_frozen.json)
CACHE2 = {}        # x06: cache for swarm.field_short
TTL = 0
COUNTERS = {"accepted": 0, "duplicate": 0, "old": 0, "sent": 0}

QOFF = ((2, 2), (2, -2), (-2, -2), (-2, 2))   # quadrant sample offsets


def init():
    global TTL, DECAY, SHORT_DECAY
    TTL = min(64, max(4, int(4 * P["swarm_half_life"])))
    DECAY = [0.5 ** (age / P["swarm_half_life"]) for age in range(TTL + 1)]
    SHORT_DECAY = [0.5 ** (age / P["swarm_h_short"]) for age in range(TTL + 1)]


def quadrant(dx, dy):
    if dx >= 0 and dy > 0:
        return 0
    if dx > 0 and dy <= 0:
        return 1
    if dx <= 0 and dy < 0:
        return 2
    return 3


def hear(report, packet):
    """report = (did, x, y, quad, ally_len, enemy_len, rnd)."""
    if not P["swarm_remote"]:
        return
    did, x, y, quad, aa, ee, rnd = report
    if did == w.ME:
        return
    age = w.RND - rnd
    if not 0 <= age <= TTL:
        COUNTERS["old"] += 1
        return
    key = (did, quad)
    prev = REPORTS.get(key)
    if prev is not None and rnd <= prev[4]:
        COUNTERS["duplicate"] += 1
        return
    REPORTS[key] = (x, y, aa, ee, rnd, packet)
    COUNTERS["accepted"] += 1
    cap = 4 * P["swarm_sources"]
    if len(REPORTS) > cap:
        # Prefer fresh reports; deterministic key tie-break.
        oldest = min(REPORTS, key=lambda k: (REPORTS[k][4], k))
        del REPORTS[oldest]


def _activate():
    del ACTIVE[:]
    del AGES[:]
    CACHE.clear()
    CACHE2.clear()
    for (did, quad), (x, y, aa, ee, rnd, packet) in REPORTS.items():
        age = w.RND - rnd
        if 0 <= age <= TTL:
            sx = (x + QOFF[quad][0]) % w.W
            sy = (y + QOFF[quad][1]) % w.H
            ACTIVE.append((sx, sy, aa, ee, DECAY[age]))
            AGES.append(age)
    if LOCAL is not None:
        x, y, qa, qe, rnd = LOCAL
        age = w.RND - rnd
        if 0 <= age <= TTL:
            for quad in range(4):
                sx = (int(x + 0.5) + QOFF[quad][0]) % w.W
                sy = (int(y + 0.5) + QOFF[quad][1]) % w.H
                ACTIVE.append((sx, sy, qa[quad], qe[quad], DECAY[age]))
                AGES.append(age)


def observe(mine):
    """Fold this turn's view into the local quadrant EWMA.  `mine` is the
    visible own non-head segments from world.sense; the head adds one."""
    global LOCAL, LAST_HEAD, CUR
    qa = [0.0, 0.0, 0.0, 0.0]
    qe = [0.0, 0.0, 0.0, 0.0]
    hx, hy = w.HEAD % w.W, w.HEAD // w.W
    for c, _d in mine:
        qa[quadrant(_wob(c % w.W - hx, w.W), _wob(c // w.W - hy, w.H))] += 1.0
    qa[quadrant(0, 0)] += 1.0            # own head (centre tile -> q3)
    for c, (did, ours, head) in w.occ.items():
        dx = _wob(c % w.W - hx, w.W)
        dy = _wob(c // w.W - hy, w.H)
        if ours:
            qa[quadrant(dx, dy)] += 1.0
        else:
            qe[quadrant(dx, dy)] += 1.0
    CUR = (qa, qe)
    x, y = float(hx), float(hy)
    if LOCAL is None or LAST_HEAD < 0 or w.tdist(LAST_HEAD, w.HEAD) > 3:
        LOCAL = (x, y, qa, qe, w.RND)    # a portal jump resets the EWMA
    else:
        px, py, pa, pe, rnd = LOCAL
        age = max(0, w.RND - rnd)
        retain = 0.5 ** (age / P["swarm_half_life"])
        gain = 1.0 - retain
        LOCAL = ((px + gain * _delta(px, x, w.W)) % w.W,
                 (py + gain * _delta(py, y, w.H)) % w.H,
                 [retain * pa[q] + gain * qa[q] for q in range(4)],
                 [retain * pe[q] + gain * qe[q] for q in range(4)], w.RND)
    LAST_HEAD = w.HEAD
    for key in [k for k, row in REPORTS.items() if w.RND - row[4] > TTL]:
        del REPORTS[key]
    _activate()


def _wob(d, size):
    """Wrapped offset into (-size/2, size/2]."""
    if d * 2 > size:
        d -= size
    elif d * 2 < -size:
        d += size
    return d


def _delta(a, b, size):
    return (b - a + size * 0.5) % size - size * 0.5


def field(cell):
    """Decayed ally length, enemy length and evidence coverage (0..1) near
    a cell.  Same kernel semantics as density.field: spatial-only
    denominator, so a lone stale source shrinks instead of normalising."""
    cached = CACHE.get(cell)
    if cached is not None:
        return cached
    x, y = cell % w.W, cell // w.W
    radius = P["swarm_radius"]
    total = aa = ee = confidence = 0.0
    for px, py, allies, enemies, decay in ACTIVE:
        dx, dy = abs(x - px), abs(y - py)
        dx = min(dx, w.W - dx)
        dy = min(dy, w.H - dy)
        if dx >= radius or dy >= radius:
            continue
        spatial = (1.0 - dx / radius) * (1.0 - dy / radius)
        weight = spatial * decay
        total += spatial
        confidence += weight
        aa += weight * allies
        ee += weight * enemies
    denom = max(1.0, total)
    answer = aa / denom, ee / denom, min(1.0, confidence)
    CACHE[cell] = answer
    return answer


def balance(allies, enemies):
    """Enemy-minus-ally control from LENGTH evidence, damped for scale."""
    return (enemies - allies) / (allies + enemies + P["swarm_damp"])


# ------------------------------------------------- x06 short-window fields
def field_short(cell):
    """Same kernel and coverage semantics as field(), decayed with the SHORT
    window (swarm_h_short; validated vs replay ground truth).  Parallel
    implementation so field() stays byte-identical to x01."""
    cached = CACHE2.get(cell)
    if cached is not None:
        return cached
    x, y = cell % w.W, cell // w.W
    radius = P["swarm_radius"]
    total = aa = ee = confidence = 0.0
    for k, (px, py, allies, enemies, _decay) in enumerate(ACTIVE):
        dx, dy = abs(x - px), abs(y - py)
        dx = min(dx, w.W - dx)
        dy = min(dy, w.H - dy)
        if dx >= radius or dy >= radius:
            continue
        spatial = (1.0 - dx / radius) * (1.0 - dy / radius)
        weight = spatial * SHORT_DECAY[AGES[k]]
        total += spatial
        confidence += weight
        aa += weight * allies
        ee += weight * enemies
    denom = max(1.0, total)
    answer = aa / denom, ee / denom, min(1.0, confidence)
    CACHE2[cell] = answer
    return answer


def gain_short(cell):
    """Balance gradient of the SHORT window: positive = toward enemy control
    that only fresh evidence supports (rising contact), not old occupancy."""
    aa, ee, _ = field_short(cell)
    ha, he, _ = field_short(w.HEAD)
    return balance(aa, ee) - balance(ha, he)


def gain(cell):
    """Balance(cell) - balance(HEAD): positive means toward enemy control.
    The game-relative directional feature -- no compass constant involved."""
    aa, ee, _ = field(cell)
    ba, be, _ = field(w.HEAD)
    return balance(aa, ee) - balance(ba, be)


def packet_now():
    """This turn's quadrant report: the enemy-heaviest quadrant while any
    enemy is in evidence (contact: the most valuable direction first), else
    rotating coverage so every quadrant refreshes within four turns.  Raw
    current counts are sent -- receivers apply their own temporal decay."""
    if LOCAL is None or CUR is None:
        return None
    x, y = LOCAL[0], LOCAL[1]
    qa, qe = CUR
    if max(qe) >= P["swarm_contact"]:
        quad = max(range(4), key=lambda q: (qe[q], -q))
    else:
        quad = (w.RND + w.ME) % 4
    return comms.swarm_packet(w.ME, x, y, quad, qa[quad], qe[quad], w.RND)
