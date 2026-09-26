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

Javert D2 (settings.LEN_DENSITY): the same estimator additionally carries
length sums -- visible ally segments (own length included) and visible enemy
segments -- in a type-7 packet sent beside the type-6 counts in the same turn.
Remote rows merge by (sender mod 512, round) with matching rounded position;
sources without a length packet keep count-only estimates. field_len() exposes
the decayed length field; nothing consumes it unless a policy switch says so.
"""
import world as w
import comms
import settings
from params import P

LOCAL = None  # x, y, ally count, enemy count, observation round
LOCAL_LEN = None  # x, y, ally length, enemy length, observation round (D2)
LAST_HEAD = -1
REPORTS = {}  # original sender -> (x, y, ally, enemy, original round, packet)
LEN_ROWS = {}  # (sender mod 512, round) -> (x, y, ally length, enemy length) (D2)
ACTIVE = []   # this turn's bounded (x, y, ally, enemy, temporal decay)
ACTIVE_LEN = []  # this turn's (x, y, ally length, enemy length, decay) rows
CACHE = {}
CACHE_LEN = {}
DECAY = []
TTL = 0
COUNTERS = {"accepted": 0, "duplicate": 0, "old": 0, "sent": 0, "len_rows": 0}


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


def hear_len(decoded):
    """D2: store a type-7 row; merge happens at activation, never on arrival."""
    did, x, y, a_len, e_len, rnd = decoded
    if did == (w.ME & 511) and rnd == w.RND:
        return  # our own ray echoed back; LOCAL_LEN already holds it
    if not 0 <= w.RND - rnd <= TTL:
        return
    LEN_ROWS[(did, rnd)] = (x, y, a_len, e_len)
    COUNTERS["len_rows"] += 1
    if len(LEN_ROWS) > P["density_sources"]:
        oldest = min(LEN_ROWS, key=lambda key: (key[1], key[0]))
        del LEN_ROWS[oldest]


def _activate(include_local=True):
    del ACTIVE[:]
    del ACTIVE_LEN[:]
    CACHE.clear()
    CACHE_LEN.clear()
    use_len = settings.LEN_DENSITY
    for did, (x, y, aa, ee, rnd, packet) in REPORTS.items():
        age = w.RND - rnd
        if not 0 <= age <= TTL:
            continue
        decay = DECAY[age]
        ACTIVE.append((x, y, aa, ee, decay))
        if use_len:
            row = LEN_ROWS.get((did & 511, rnd))
            # merge only when the length packet names the same rounded place
            if row is not None and row[0] == x and row[1] == y:
                ACTIVE_LEN.append((row[0], row[1], row[2], row[3], decay))
    if include_local and LOCAL is not None:
        x, y, aa, ee, rnd = LOCAL
        age = w.RND - rnd
        if 0 <= age <= TTL:
            ACTIVE.append((x, y, aa, ee, DECAY[age]))
            if use_len and LOCAL_LEN is not None:
                lx, ly, al, el, lrnd = LOCAL_LEN
                if w.RND - lrnd <= TTL:
                    ACTIVE_LEN.append((lx, ly, al, el, DECAY[w.RND - lrnd]))


def _ewma(old_xy, new_xy, old_ae, new_ae):
    px, py, rnd = old_xy
    x, y = new_xy
    age = max(0, w.RND - rnd)
    retain = 0.5 ** (age / P["density_half_life"])
    gain = 1.0 - retain
    return ((px + gain * delta(px, x, w.W)) % w.W,
            (py + gain * delta(py, y, w.H)) % w.H,
            retain * old_ae[0] + gain * new_ae[0],
            retain * old_ae[1] + gain * new_ae[1], w.RND)


def observe():
    global LOCAL, LOCAL_LEN, LAST_HEAD, PRED
    if P["density_trace"]:
        _activate()
        PRED = field(w.HEAD)  # strictly before consuming this turn's counts
    aa = 1.0 + len(w.alen)
    ee = float(len(w.elen))
    x, y = w.HEAD % w.W, w.HEAD // w.W
    al = float(w.LEN + sum(w.alen.values()))
    el = float(sum(w.elen.values()))
    if LOCAL is None or LAST_HEAD < 0 or w.tdist(LAST_HEAD, w.HEAD) > 3:
        LOCAL = (float(x), float(y), aa, ee, w.RND)
        if settings.LEN_DENSITY:
            LOCAL_LEN = (float(x), float(y), al, el, w.RND)
    else:
        px, py, aa0, ee0, rnd0 = LOCAL
        LOCAL = _ewma((px, py, rnd0), (x, y), (aa0, ee0), (aa, ee))
        if settings.LEN_DENSITY and LOCAL_LEN is not None:
            lx, ly, al0, el0, lrnd = LOCAL_LEN
            LOCAL_LEN = _ewma((lx, ly, lrnd), (x, y), (al0, el0), (al, el))
    LAST_HEAD = w.HEAD
    for did in [did for did, row in REPORTS.items() if w.RND - row[4] > TTL]:
        del REPORTS[did]
    for key in [key for key in LEN_ROWS if w.RND - key[1] > TTL]:
        del LEN_ROWS[key]
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


def field_len(cell):
    """D2: decayed ally/enemy visible-length sums and coverage at a cell.

    Same kernel, decay and denominators as field(); sources without merged
    length evidence simply do not contribute. Bounded callers only: every
    query is cached but the row set is at most density_sources + local.
    """
    cached = CACHE_LEN.get(cell)
    if cached is not None:
        return cached
    x, y = cell % w.W, cell // w.W
    radius = P["density_radius"]
    total = al = el = confidence = 0.0
    for px, py, a_len, e_len, decay in ACTIVE_LEN:
        dx, dy = abs(x - px), abs(y - py)
        dx = min(dx, w.W - dx)
        dy = min(dy, w.H - dy)
        if dx >= radius or dy >= radius:
            continue
        spatial = (1.0 - dx / radius) * (1.0 - dy / radius)
        weight = spatial * decay
        total += spatial
        confidence += weight
        al += weight * a_len
        el += weight * e_len
    denom = max(1.0, total)
    answer = al / denom, el / denom, min(1.0, confidence)
    CACHE_LEN[cell] = answer
    return answer


def resource_factor(cell):
    # Direct vision and existing ownership/threat rules take precedence.
    if w.seen[cell] == w.RND + 1:
        return 1.0
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

    Javert R2 (settings.LEN_DENSITY): on a density turn the second reserved ray
    carries the type-7 length packet describing the same sensor centre and
    round; if no second ray is available the counts go out alone.
    """
    if LOCAL is None or P["density_rays"] <= 0:
        return legacy
    if (w.RND + w.ME) % P["density_period"]:
        return legacy
    x, y, aa, ee, rnd = LOCAL
    packet = comms.density_packet(w.ME, x, y, aa, ee, rnd)
    if packet is None:
        return legacy
    len_packet = None
    if settings.LEN_DENSITY and LOCAL_LEN is not None and w.ME < 512:
        lx, ly, al, el, lrnd = LOCAL_LEN
        len_packet = comms.density_len_packet(w.ME, lx, ly, al, el, lrnd)
    out = dict(legacy)
    off = (w.RND + w.ME) % 4
    dirs = [w.DIRS[(off + k) % 4] for k in range(4)]
    # Fill idle rays first; reserve the remainder in a rotating order.
    selected = [d for d in dirs if d not in out]
    for d in dirs:
        if len(selected) >= P["density_rays"] + (1 if len_packet else 0):
            break
        if d not in selected and ((out.get(d, 0) >> 8) & 15) not in (comms.T_CROWN, comms.T_PREY):
            selected.append(d)
    relay = None
    if P["density_relay"] and REPORTS and w.RND % 2:
        peers = sorted(REPORTS)
        row = REPORTS[peers[(w.RND // 2 + w.ME) % len(peers)]]
        if w.RND - row[4] <= TTL:
            relay = row[5]
    for k, d in enumerate(selected):
        out[d] = relay if k == 1 and relay is not None else packet
    if len_packet and len(selected) > P["density_rays"]:
        out[selected[P["density_rays"]]] = len_packet
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
