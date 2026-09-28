"""Message selection (what to say, in which direction) and hearing.

Crown beacons: from crown_from, on two opposite rays (N/S on even rounds,
E/W on odd).  Food gossip on the remaining rays: pearls in view and the beds
in view that spawn soonest (two per packet).  Receivers adopt reports about
tiles they have not seen recently.

x03 state/radio change (communication version 2): after the legacy content,
reserve up to two rays for the density layers -- one aggregate COUNT report
(comms.T_DENSITY, from the monte_christo-v07 study) and one directional
LENGTH report (comms.T_SWARM, rotating quadrants).  Idle rays are used first;
only FOOD rays may be displaced.  CROWN, PREY and PORTAL traffic is never
displaced: portal pairings are load-bearing for the topology feature line.
The split handoff stays a final explicit override in main.py.
"""
import world as w
import comms
import roles
import density
import swarm
from params import P

ORDER = ("N", "E", "S", "W")


def hear(msgs):
    fresh_after = w.RND - P["gossip_trust"]
    for m in msgs:
        u = comms.unpack(m)
        if u is None:
            continue
        typ, p = u
        if typ == comms.T_DENSITY:
            d = comms.density_decode(p)
            if d is not None:
                density.hear(d, m)
        elif typ == comms.T_SWARM:
            d = comms.swarm_decode(p)
            if d is not None:
                swarm.hear(d, m)
        elif typ == comms.T_CROWN:
            d = comms.crown_decode(p)
            if d is not None:
                roles.hear(*d)
        elif typ == comms.T_PORTAL:
            if 2 * w.NC <= 8192:
                k1, k2, pid = comms.portal_decode(p)
                w.learn_pair(k1, k2, pid)
        elif typ == comms.T_PREY:
            d = comms.crown_decode(p)
            if d is not None and w.RND - d[3] <= P["prey_ttl"]:
                w.see_prey(*d)
        elif typ == comms.T_HANDOFF:
            ln, r = comms.handoff_decode(p)
            if 0 <= w.RND - r <= 1:
                roles.INHERIT[0] = True
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


def _reserve(out):
    """Add the density layers to the legacy message dict.

    Ray choice rotates by (round + id).  With two free rays the aggregate
    count and the directional length report go out together; with one free
    ray they alternate by round parity; with none, nothing is sent.  Only
    FOOD rays are ever taken over (v07 evidence: displaced crowns were not
    the problem, but portal pairings feed the topology line and stay)."""
    dpkt = None
    if P["density_remote"] and P["density_rays"] > 0 and density.LOCAL is not None \
            and (w.RND + w.ME) % P["density_period"] == 0:
        x, y, aa, ee, rnd = density.LOCAL
        dpkt = comms.density_packet(w.ME, x, y, aa, ee, rnd)
    spkt = swarm.packet_now() if P["swarm_rays"] > 0 else None
    if dpkt is None and spkt is None:
        return out
    off = (w.RND + w.ME) % 4
    dirs = [ORDER[(off + k) % 4] for k in range(4)]
    slots = [d for d in dirs if d not in out]
    for d in dirs:
        if len(slots) >= 2:
            break
        if d not in slots and ((out.get(d, 0) >> 8) & 15) == comms.T_FOOD:
            slots.append(d)
    if not slots:
        return out
    out = dict(out)
    if len(slots) >= 2:
        if dpkt is not None:
            out[slots[0]] = dpkt
            density.COUNTERS["sent"] += 1
        if spkt is not None:
            out[slots[1]] = spkt
            swarm.COUNTERS["sent"] += 1
    else:
        pkt = dpkt if w.RND % 2 == 0 else spkt
        if pkt is None:
            pkt = spkt if dpkt is None else dpkt
        if pkt is not None:
            out[slots[0]] = pkt
    return out


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
    pr = w.prey
    if pr is not None and w.RND - pr[3] <= P["prey_ttl"] and dirs:
        d = dirs.pop(0 if w.RND % 2 else -1)
        out[d] = comms.crown_packet(pr[0], pr[1], pr[2], pr[3], comms.T_PREY)
    if P["share_portals"] and dirs and 2 * w.NC <= 8192 and w.RND % 2 == 0:
        prs = w.paired()
        if prs:
            pid, e = prs[(w.RND // 2 + w.ME) % len(prs)]
            out[dirs.pop()] = comms.portal_packet(pid, e[0], e[1])
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
    return _reserve(out)
