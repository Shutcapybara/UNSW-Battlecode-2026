"""Macro layer: crown election (longest dragon, lowest id) by relayed sonar
beacons, and the forager / crown / feeder role of this dragon."""
import world as w
import comms
from params import P

ROLE = ["forager"]
LAST = [0]   # last round we knew a fresh crown (claims are staggered after it)
INHERIT = [False]  # a crown handed its length (and role) to us by a split


def feed_from():
    # Keep Gavroche's map-size timing, with a 400-round floor for crown banking.
    return max(P.get("feed_min_round", 0),
               500 - P["feed_base"] - int((w.W + w.H) * P["feed_k"]))


def fresh():
    c = w.crown
    return c is not None and w.RND - c[3] <= P["crown_ttl"]


def _better(l1, i1, l2, i2):
    """Challenger (l1, i1) replaces crown (l2, i2): clearly longer, or an
    exact tie broken by id (settles simultaneous first claims)."""
    return l1 >= l2 + P["crown_margin"] or (l1 == l2 and i1 < i2)


def hear(did, cell, length, rnd):
    if w.RND - rnd > P["crown_ttl"]:
        return
    c = w.crown
    if c is None or w.RND - c[3] > P["crown_ttl"]:
        w.crown = [did, cell, length, rnd]
    elif did == c[0]:
        if rnd >= c[3]:
            w.crown = [did, cell, length, rnd]
    elif _better(length, did, c[2], c[0]):
        w.crown = [did, cell, length, rnd]


def decode(msgs):
    for m in msgs:
        u = comms.unpack(m)
        if u is None:
            continue
        typ, p = u
        if typ == comms.T_CROWN:
            d = comms.crown_decode(p)
            if d is not None:
                hear(*d)


def update():
    """After sense: refresh a visible crown, drop a vanished one, self-elect."""
    if w.RND < P["crown_from"]:
        ROLE[0] = "forager"
        return
    me = w.ME & 4095
    c = w.crown
    if c is not None and c[0] != me:
        vis = False
        for hc, hid in w.ally_heads:
            if (hid & 4095) == c[0]:
                c[1] = hc
                c[3] = w.RND
                vis = True
                break
        if not vis and w.cheb(c[1], w.HEAD) + (w.RND - c[3]) <= 2:
            w.crown = c = None  # it should be in view: it is dead
    if INHERIT[0]:
        INHERIT[0] = False
        w.crown = [me, w.HEAD, w.LEN, w.RND]
        ROLE[0] = "crown"
        return
    if c is None or not fresh():
        # staggered claims: whoever claims first is heard by its cluster
        base = max(P["crown_from"], LAST[0])
        claim = w.RND >= base + (w.ME * 7919) % P["claim_spread"] and w.LEN >= P["claim_len"]
    else:
        LAST[0] = w.RND
        claim = c[0] == me or _better(w.LEN, me, c[2], c[0])
    if claim:
        w.crown = [me, w.HEAD, w.LEN, w.RND]
        ROLE[0] = "crown"
        return
    if c is not None and fresh() and w.RND >= feed_from() and w.LEN <= P["feed_max_len"] \
            and c[2] >= P["feed_min_crown"] and c[2] > w.LEN \
            and w.tdist(w.HEAD, c[1]) <= P["feed_range"]:
        ROLE[0] = "feeder"
    else:
        ROLE[0] = "forager"


def crown_visible():
    """Head cell of the crown if it is in view, else -1."""
    c = w.crown
    if c is None:
        return -1
    for hc, hid in w.ally_heads:
        if (hid & 4095) == c[0]:
            return hc
    return -1


def outgoing():
    """direction -> payload.  Everyone relays the best crown it knows."""
    if w.RND < P["crown_from"] or not fresh():
        return {}
    c = w.crown
    v = comms.crown_packet(c[0], c[1], c[2], c[3])
    return {"N": v, "E": v, "S": v, "W": v}
