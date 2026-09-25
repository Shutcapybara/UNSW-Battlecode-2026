"""Message selection (what to say, in which direction) and hearing.

Crown beacons: from crown_from, on two opposite rays (N/S on even rounds,
E/W on odd).  Food gossip on the remaining rays: pearls in view and the beds
in view that spawn soonest (two per packet).  Receivers adopt reports about
tiles they have not seen recently.
"""
import world as w
import comms
import roles
from params import P

ORDER = ("N", "E", "S", "W")


def hear(msgs):
    fresh_after = w.RND - P["gossip_trust"]
    for m in msgs:
        u = comms.unpack(m)
        if u is None:
            continue
        typ, p = u
        if typ == comms.T_CROWN:
            d = comms.crown_decode(p)
            if d is not None:
                roles.hear(*d)
        elif typ == comms.T_FOOD and P["gossip"]:
            for c, r in comms.food_decode(p):
                if w.seen[c] - 1 >= fresh_after:
                    continue  # we have our own recent look
                if r <= w.RND:
                    if w.RND - r <= P["mem_ttl"]:
                        if w.pearls.get(c, -1) < r:
                            w.pearls[c] = r
                else:
                    w.bed[c] = 2
                    w.spawn[c] = r


def _food_entries():
    """Pearls in view first, then view beds by soonest spawn."""
    rnd = w.RND
    pearls = []
    beds = []
    horizon = rnd + P["gossip_horizon"]
    for x, y, p, cd in w.io_tiles():
        c = y * w.W + x
        if p:
            pearls.append((c, rnd))
        elif 0 < cd and rnd + cd <= horizon:
            beds.append((rnd + cd, c))
    beds.sort()
    return pearls + [(c, s) for s, c in beds]


def outgoing():
    out = {}
    dirs = list(ORDER)
    if w.RND >= P["crown_from"] and roles.fresh():
        c = w.crown
        v = comms.crown_packet(c[0], c[1], c[2], c[3])
        pair = ("N", "S") if w.RND % 2 == 0 else ("E", "W")
        for d in pair:
            out[d] = v
            dirs.remove(d)
    if P["gossip"] and w.W <= 64 and w.H <= 64:
        ents = _food_entries()
        if ents:
            k = 0
            n = len(ents)
            off = (w.RND * 2) % n
            for d in dirs:
                if k >= n:
                    break
                pair = [ents[(off + k) % n]]
                if k + 1 < n:
                    pair.append(ents[(off + k + 1) % n])
                k += 2
                out[d] = comms.food_packet(pair)
    return out
