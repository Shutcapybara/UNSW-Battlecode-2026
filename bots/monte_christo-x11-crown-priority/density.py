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
CACHE = {}
DECAY = []
TTL = 0
COUNTERS = {"accepted": 0, "duplicate": 0, "old": 0, "sent": 0}
PRED = (0., 0., 0.)


def init():
    global TTL, DECAY
    TTL = min(64, max(4, int(4 * P["density_half_life"])))
    DECAY = [0.5 ** (age / P["density_half_life"]) for age in range(TTL + 1)]


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
    CACHE.clear()
    for x, y, aa, ee, rnd, packet in REPORTS.values():
        age = w.RND - rnd
        if 0 <= age <= TTL:
            ACTIVE.append((x, y, aa, ee, DECAY[age]))
    if include_local and LOCAL is not None:
        x, y, aa, ee, rnd = LOCAL
        age = w.RND - rnd
        if 0 <= age <= TTL:
            ACTIVE.append((x, y, aa, ee, DECAY[age]))


def observe():
    global LOCAL, LAST_HEAD, PRED
    if P["density_trace"]:
        _activate()
        PRED = field(w.HEAD)  # strictly before consuming this turn's counts
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


def resource_factor(cell):
    allies, enemies, confidence = field(cell)
    return 1.0 / (1.0 + P["density_ally"] * max(0.0, allies - 1.0)
                  + P["density_enemy"] * enemies)


def gradient_score(cell):
    aa, ee, _ = field(cell)
    ba, be, _ = field(w.HEAD)
    # Move toward positive allied-minus-enemy control, as a bounded tie-break.
    change = (aa - ee) - (ba - be)
    return max(-0.75, min(0.75, P["density_gradient"] * change))


def schedule(legacy):
    """Reserve 0/1/2/4 rays for density; use spare rays, rotating by ID/time.

    Reserved rays may replace ANY legacy report, including crowns. This is a
    tunable allocation rather than assuming the old semantics are optimal.
    On a relay ray forward one original latest report without refreshing it.
    Split handoff is a final explicit override in main.py.
    """
    if LOCAL is None or P["density_rays"] <= 0:
        return legacy
    if (w.RND + w.ME) % P["density_period"]:
        return legacy
    x, y, aa, ee, rnd = LOCAL
    packet = comms.density_packet(w.ME, x, y, aa, ee, rnd)
    if packet is None:
        return legacy
    out = dict(legacy)
    off = (w.RND + w.ME) % 4
    dirs = [w.DIRS[(off + k) % 4] for k in range(4)]
    # Fill idle rays first; reserve the remainder in a rotating order.
    selected = [d for d in dirs if d not in out]
    for d in dirs:
        if len(selected) >= P["density_rays"]:
            break
        # Keep the two crown rays: density competes for remaining capacity.
        if d not in selected and ((out.get(d, 0) >> 8) & 15) != comms.T_CROWN:
            selected.append(d)
    relay = None
    if P["density_relay"] and REPORTS and w.RND % 2:
        peers = sorted(REPORTS)
        row = REPORTS[peers[(w.RND // 2 + w.ME) % len(peers)]]
        if w.RND - row[4] <= TTL:
            relay = row[5]
    for k, d in enumerate(selected):
        out[d] = relay if k == 1 and relay is not None else packet
    COUNTERS["sent"] += len(selected)
    return out


def trace(work):
    if (w.RND + w.ME) % 8:
        return
    import sys
    import json
    sys.stdout.write("LOG MC_DENSITY " + json.dumps([
        w.ME, w.RND, w.HEAD, 1 + len(w.alen), len(w.elen),
        list(LOCAL), list(PRED), len(REPORTS), dict(COUNTERS),
        work.get("selected"), work.get("messages", {})], separators=(",", ":")) + "\n")
