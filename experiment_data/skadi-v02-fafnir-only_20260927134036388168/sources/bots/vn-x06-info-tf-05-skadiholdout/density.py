"""State/feature layer for bounded, deduplicated spatial sonar estimates.

Each source contributes ONE latest report, never one sample per received ray.
Counts are unique dragons with any visible segment, not body lengths or heads.
The observer is included in allies. These are overlapping 7x7 sensor counts,
not independent observations to add or a reconstructed global population.

Counts and sensor position use the same EWMA half-life. Position moves along
the shortest wrapped displacement. A portal-sized jump resets the local EWMA.
Reports preserve origin time through relay; their amplitudes decay by the same
half-life. Spatially overlapping estimates are averaged, with confidence kept
separate; no evidence gives zero confidence rather than proof of safety.
"""
import world as w
import comms
from params import P

LOCAL = None  # x, y, ally count, enemy count, observation round
LAST_HEAD = -1
REPORTS = {}  # original sender -> (x, y, ally, enemy, original round, packet)
ACTIVE = []   # this turn's bounded (x, y, ally, enemy, temporal decay)
AGES = []     # parallel to ACTIVE: report ages (x06 short-window fields)
CACHE = {}
DECAY = []
SHORT_DECAY = []  # x06: short-window decay (ewma_frozen.json)
CACHE2 = {}       # x06: cache for density.field_short
TTL = 0
COUNTERS = {"accepted": 0, "duplicate": 0, "old": 0, "sent": 0}
PRED = (0., 0., 0.)


def init():
    global TTL, DECAY, SHORT_DECAY
    TTL = min(64, max(4, int(4 * P["density_half_life"])))
    DECAY = [0.5 ** (age / P["density_half_life"]) for age in range(TTL + 1)]
    SHORT_DECAY = [0.5 ** (age / P["density_h_short"]) for age in range(TTL + 1)]


def delta(a, b, size):
    return (b - a + size * 0.5) % size - size * 0.5


def hear(report, packet):
    if not P["density_remote"]:
        return
    did, x, y, allies, enemies, rnd = report
    if did == w.ME:
        return
    age = w.RND - rnd
    if not 0 <= age <= TTL:
        COUNTERS["old"] += 1
        return
    prev = REPORTS.get(did)
    if prev is not None and rnd <= prev[4]:
        COUNTERS["duplicate"] += 1
        return
    REPORTS[did] = (x, y, allies, enemies, rnd, packet)
    COUNTERS["accepted"] += 1
    if len(REPORTS) > P["density_sources"]:
        # Prefer fresh reports; deterministic ID tie-break, no identity folding.
        oldest = min(REPORTS, key=lambda key: (REPORTS[key][4], key))
        del REPORTS[oldest]


def _activate(include_local=True):
    del ACTIVE[:]
    del AGES[:]
    CACHE.clear()
    CACHE2.clear()
    for x, y, aa, ee, rnd, packet in REPORTS.values():
        age = w.RND - rnd
        if 0 <= age <= TTL:
            ACTIVE.append((x, y, aa, ee, DECAY[age]))
            AGES.append(age)
    if include_local and LOCAL is not None:
        x, y, aa, ee, rnd = LOCAL
        age = w.RND - rnd
        if 0 <= age <= TTL:
            ACTIVE.append((x, y, aa, ee, DECAY[age]))
            AGES.append(age)


def observe():
    global LOCAL, LAST_HEAD
    aa = 1.0 + len(w.alen)
    ee = float(len(w.elen))
    x, y = w.HEAD % w.W, w.HEAD // w.W
    if LOCAL is None or LAST_HEAD < 0 or w.tdist(LAST_HEAD, w.HEAD) > 3:
        LOCAL = (float(x), float(y), aa, ee, w.RND)
    else:
        px, py, pa, pe, rnd = LOCAL
        age = max(0, w.RND - rnd)
        retain = 0.5 ** (age / P["density_half_life"])
        gain = 1.0 - retain
        LOCAL = ((px + gain * delta(px, x, w.W)) % w.W,
                 (py + gain * delta(py, y, w.H)) % w.H,
                 retain * pa + gain * aa, retain * pe + gain * ee, w.RND)
    LAST_HEAD = w.HEAD
    for did in [did for did, row in REPORTS.items() if w.RND - row[4] > TTL]:
        del REPORTS[did]
    _activate()


def field(cell):
    """Return decayed ally count, enemy count and evidence coverage (0..1).

    A separable triangular kernel is an inexpensive soft footprint. Amplitudes
    shrink with age even if this is the only source: temporal weights must NOT
    cancel in the denominator. Denominator uses spatial weights only.
    """
    cached = CACHE.get(cell)
    if cached is not None:
        return cached
    x, y = cell % w.W, cell // w.W
    radius = P["density_radius"]
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


# ------------------------------------------------- x06 short-window field
def field_short(cell):
    """Same kernel and coverage semantics as field(), decayed with the SHORT
    window (density_h_short).  Parallel implementation so field() stays
    byte-identical to x01."""
    cached = CACHE2.get(cell)
    if cached is not None:
        return cached
    x, y = cell % w.W, cell // w.W
    radius = P["density_radius"]
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


def resource_factor(cell):
    # Direct vision and existing ownership/threat rules take precedence.
    if w.seen[cell] == w.RND + 1:
        return 1.0
    allies, enemies, confidence = field(cell)
    return 1.0 / (1.0 + P["density_ally"] * max(0.0, allies - 1.0)
                  + P["density_enemy"] * enemies)


# Porthos x03 note: v07's schedule() and trace() are deliberately NOT carried
# over.  Message selection lives in radio.py (the contract keeps selection
# distinct from state), and relay was shown not load-bearing by the
# monte_christo x08 experiment.  gradient_score (x06, rejected) is dropped.
