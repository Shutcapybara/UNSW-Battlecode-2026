"""R2: anchored segment-density reports, not full dragon-length estimates.

Type 7 payload: x:6 y:6 round:9 source:11 ally:4 enemy:4 area:4 = 44 bits.
Mass and area describe the observed part of a known route-radius-two footprint
(<=13 tiles). IDs >=2048 or boards >64 disable transmission, never alias IDs.
Reports from a source replace earlier reports; age is never refreshed. No relay.
The anchor rotates between reachable regions, prioritising enemy evidence.
"""
import world as w
import comms
import topology

TYPE = 7
TTL = 12
REPORTS = {}
PACKET = None
LOCAL = None


def initialize():
    global PACKET, LOCAL
    REPORTS.clear(); PACKET = None; LOCAL = None


def encode(source, cell, rnd, ally, enemy, area):
    if not (0 <= source < 2048 and w.W <= 64 and w.H <= 64 and 0 <= rnd < 500
            and 0 <= cell < w.NC and 1 <= area <= 13 and 0 <= ally + enemy <= area
            and ally >= 0 and enemy >= 0): return None
    return comms.pack(TYPE, (cell % w.W) | ((cell // w.W) << 6) | (rnd << 12)
                      | (source << 21) | (ally << 32) | (enemy << 36) | (area << 40))


def decode(payload):
    x, y = payload & 63, (payload >> 6) & 63
    rnd, source = (payload >> 12) & 511, (payload >> 21) & 2047
    ally, enemy, area = (payload >> 32) & 15, (payload >> 36) & 15, (payload >> 40) & 15
    if x >= w.W or y >= w.H or not 0 <= w.RND-rnd <= TTL or rnd >= 500 \
            or not 1 <= area <= 13 or ally + enemy > area: return None
    return source, y*w.W+x, rnd, ally, enemy, area


def hear(payload):
    row = decode(payload)
    if row is None or row[0] == w.ME: return
    source = row[0]
    if source in REPORTS and REPORTS[source][2] >= row[2]: return
    REPORTS[source] = row
    if len(REPORTS) > 12:
        del REPORTS[min(REPORTS, key=lambda key: (REPORTS[key][2], key))]


def observe(topo):
    global PACKET, LOCAL
    for source in list(REPORTS):
        if w.RND - REPORTS[source][2] > TTL: del REPORTS[source]
    # At most four sampled anchors. This is a report-selection policy, separate
    # from encoding and from the action policy's experimental selector.
    anchors = [cell for cell, depth in topo['dist'].items()
               if depth in (2, 3) and w.seen[cell] == w.RND+1]
    if not anchors: anchors = [w.HEAD]
    off = (w.ME + w.RND//2) % len(anchors)
    own = set(w.body); rows = []
    for k in range(min(4, len(anchors))):
        cell = anchors[(off+k) % len(anchors)]
        cells = topology.footprint(cell, topo)
        ally = sum(c in own or (c in w.occ and w.occ[c][1]) for c in cells)
        enemy = sum(c in w.occ and not w.occ[c][1] for c in cells)
        rows.append((enemy, -w.visits[cell], cell, ally, len(cells)))
    enemy, _, cell, ally, area = max(rows, key=lambda row: row[:2])
    LOCAL = (w.ME, cell, w.RND, ally, enemy, area)
    PACKET = encode(*LOCAL)


def evidence(target, topo):
    """Average overlapping samples; accept only anchors in our known graph.

    Reports are route-relative regional context, not a target-tile occupancy
    claim. Same first-route branch establishes relevance; no isotropic field
    crosses a wall. Missing direction/evidence has zero confidence.
    """
    mask = topo['masks'].get(target, 0)
    if not mask: return 0.0, 0.0
    total = balance = confidence = 0.0
    for source, cell, rnd, ally, enemy, area in REPORTS.values():
        age = w.RND-rnd
        if not 0 <= age <= TTL or not topo['masks'].get(cell, 0) & mask: continue
        decay = 0.5 ** (age/4.0)
        total += 1.0
        balance += decay * (ally-enemy)/area
        confidence += decay
    return (balance/max(1.0, total), min(1.0, confidence/max(1.0, total)))


def schedule(legacy):
    if PACKET is None or (w.RND+w.ME) % 2: return legacy
    out = dict(legacy); off = (w.RND//2+w.ME) % 4
    protected = (comms.T_CROWN, comms.T_PREY, comms.T_PORTAL, comms.T_HANDOFF)
    dirs = [w.DIRS[(off+k)%4] for k in range(4)]
    direction = next((d for d in dirs if d not in out), None)
    if direction is None:
        direction = next((d for d in dirs if ((out[d] >> 8)&15) not in protected), None)
    if direction is not None: out[direction] = PACKET
    return out
