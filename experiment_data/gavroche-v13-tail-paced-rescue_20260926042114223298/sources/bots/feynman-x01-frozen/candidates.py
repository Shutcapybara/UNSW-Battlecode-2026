"""CANDIDATES: enumerate objective instances. No command is chosen here.

Record: {kind, target, subject, params, candidate_id}; cells y*W+x; ages in
rounds; lengths in segments. Kinds: GATHER, SCOUT, ATTACK, RETREAT, FEED_ALLY,
REPRODUCE (contract V1, inherited from Aramis I1).

C0 (Monte Christo parity): one ECONOMY objective from the inherited target
search (a pearl/bed -> GATHER; unseen tile, unpaired portal or far sector ->
SCOUT; feeder -> FEED_ALLY toward the crown; small-forager prey -> ATTACK
approach), one contact ATTACK per visible enemy head in sprint reach, one
REPRODUCE, and the emergency RETREAT.

C1 macro objectives (game-relative, from mass/topology features), each gated
by params so C1 with every gate off equals C0:
  ATTACK:pressure  toward the enemy mass vector (frontier pressure)
  RETREAT:support  toward allied mass, away from enemy mass
The search may populate world geometry caches only; script memory is read-only.
"""
import world as w
import valuation as val
import roles
import mass
import topology
import regions
from params import P

MEM = {"target": -1, "tval": 0.0, "dive": -1}


def candidate(kind, target=-1, subject=-1, **params):
    return dict(kind=kind, target=target, subject=subject, params=params,
                candidate_id=kind + ":" + str(subject if subject >= 0 else target))


def far_target():
    best = -1
    bv = 0.0
    gamma = P["gamma"]
    for c, r in w.pearls.items():
        if w.RND - r <= P["mem_ttl"] and c != w.HEAD:
            v = P["v_mem"] * gamma ** w.tdist(c, w.HEAD)
            if v > bv:
                bv = v
                best = c
    if best < 0:
        best = w.sector_target()
    return best


def search(own_idx):
    """Inherited Monte Christo target search (verbatim semantics).

    Returns (target, value, dive, source, dist, mask). mask[c] = bitmask of
    first moves that start a shortest route to c. `MEM` (target hysteresis) is
    read here and written only by commit()."""
    feeder = roles.ROLE[0] == "feeder"
    crown = roles.ROLE[0] == "crown"
    ally = w.ally_heads
    enemy = [c for c, _ in w.enemy_heads]
    gamma = P["gamma"]
    vmax = P["v_unseen"]
    if w.pearls:
        vmax = P["v_pearl"]
    elif w.spawn and P["v_bed"] > vmax:
        vmax = P["v_bed"]
    if w.pends and P["v_dive"] > vmax:
        vmax = P["v_dive"]
    prev = MEM["target"]
    prev_val = 0.0
    best = -1
    bval = 0.0
    dive = -1
    vac = w.vac
    OPT = w.OPT
    step_opt = w.step_opt
    pearls = w.pearls
    bed = w.bed
    seen = w.seen
    src = w.HEAD
    goal = w.crown[1] if feeder else -1
    dist = {src: 0}
    mask = {src: 0}
    q = [src]
    qi = 0
    cap = P["big_cap"] if w.RND - w.BORN >= 2 else P["born_cap"]
    disc = 1.0
    last_t = 0
    cell_value = val.cell_value
    while qi < len(q) and len(q) < cap:
        c = q[qi]
        qi += 1
        t = dist[c] + 1
        mc = mask[c]
        if t != last_t:
            last_t = t
            disc = gamma ** t
            if t > 3 and not feeder and vmax * disc <= bval:
                break
        g = OPT[c]
        if g is None:
            g = step_opt(c)
        for d in range(4):
            n = g[d]
            if n < 0:
                if n == -3 and not crown and not feeder:
                    v = P["v_dive"]
                    for hc, hid in ally:
                        if w.tdist(hc, c) < t - 1:
                            v *= P["own_disc"]
                            break
                    sc = v * disc
                    if sc > bval:
                        bval = sc
                        best = c
                        dive = d
                continue
            m = mc if c != src else (1 << d)
            tn = dist.get(n)
            if tn is not None:
                if tn == t:
                    mask[n] |= m
                continue
            i = own_idx.get(n)
            if i is not None and t < i + 2:
                continue
            v = vac.get(n)
            if v is not None and t < v:
                continue
            dist[n] = t
            mask[n] = m
            q.append(n)
            if feeder:
                continue
            if n not in pearls and bed[n] != 2 and seen[n]:
                continue
            v = cell_value(n, t, ally, enemy)
            if v > 0:
                sc = v * disc
                if n == prev:
                    prev_val = sc
                if sc > bval:
                    bval = sc
                    best = n
                    dive = -1
        if feeder and goal in dist:
            break
    if feeder:
        return goal, 0.0, -1, "feed", dist, mask, len(q)
    source = "search"
    if dive < 0 and prev >= 0 and prev_val > 0 and prev != best and prev_val * P["hyst"] >= bval:
        best = prev
        bval = prev_val
        source = "hysteresis"
    pr = w.prey
    if pr is not None and roles.ROLE[0] == "forager" and w.RND >= hunt_from() \
            and w.LEN <= P["hunt_max_len"] and w.RND - pr[3] <= P["prey_ttl"]:
        t = dist.get(pr[1])
        if t is None:
            t = w.tdist(w.HEAD, pr[1]) + 2
        sc = P["v_hunt"] * min(pr[2], 40) * gamma ** t
        if sc > bval:
            bval = sc
            best = pr[1]
            dive = -1
            source = "prey"
    if best < 0:
        best = far_target()
        source = "far"
    return best, bval, dive, source, dist, mask, len(q)


def hunt_from():
    """C1 (sat_hunt): a saturated team may hunt before hunt_from."""
    h = P["hunt_from"]
    if P["sat_hunt"] and val.saturation() >= P["sat_hunt"]:
        h = min(h, P["sat_hunt_from"])
    return h


def build(script=None):
    body = w.body
    own_idx = {c: i for i, c in enumerate(body)}
    target, bval, dive, source, dist, mask, nodes = search(own_idx)
    ctx = dict(dist=dist, mask=mask, route_nodes=nodes, econ_value=bval, econ_source=source)
    out = []
    role = roles.ROLE[0]
    if role == "feeder":
        econ = candidate("FEED_ALLY", target, w.crown[0], trade="donate", observed=w.crown[3],
                         econ=True)
    elif source == "prey":
        econ = candidate("ATTACK", target, w.prey[0], trade="favourable", approach=True,
                         observed=w.prey[3], value=bval, econ=True)
    else:
        kind = "GATHER" if (target in w.pearls or w.bed[target] == 2) and dive < 0 else "SCOUT"
        econ = candidate(kind, target, value=bval, dive=dive, source=source, econ=True)
    out.append(econ)
    # contact objectives: every visible enemy head (the executor checks reach)
    if P["attack"] and w.UNITS >= P["atk_units"]:
        for c, eid in w.enemy_heads:
            if w.cheb(c, w.HEAD) <= 4:
                out.append(candidate("ATTACK", c, eid, trade="favourable", contact=True,
                                     observed=w.RND, length=w.elen.get(eid, 1)))
    if role == "forager" and w.LEN >= P["split_min"] and w.LEN - P["child"] >= 2 \
            and w.UNITS < w.LIMIT and w.RND < min(P["split_stop"], P["grow_from"]) \
            and len(body) == w.LEN:
        out.append(candidate("REPRODUCE", body[0], child=P["child"]))
    out.append(candidate("RETREAT", emergency_split=True))
    out.extend(macro(ctx, script or {}))
    return out, ctx


def macro(ctx, script):
    """C1 objectives. Values are policy business; here only availability."""
    out = []
    if P["region"] and roles.ROLE[0] == "forager" and w.RND < P["region_until"]:
        top = regions.best()
        if top is not None:
            v, cell, s, d, avail = top
            prev = script.get("candidate_id", "")
            c = candidate("GATHER", cell, region=True, value=v, dist=d, sector=s, avail=avail,
                          persist=prev == "GATHER:region:%d" % s)
            c["candidate_id"] = "GATHER:region:%d" % s
            out.append(c)
    F = mass.F
    role = roles.ROLE[0]
    if P["pressure"] and role == "forager" and w.LEN <= P["pressure_max_len"] \
            and F.get("e_vec") is not None and w.RND < P["pressure_until"]:
        wp = mass.waypoint(F["e_vec"], P["pressure_step"])
        if wp >= 0 and wp != w.HEAD:
            c = candidate("ATTACK", wp, trade="favourable", approach=True, press=True,
                          e_mass=F["e_mass"], e_dist=F["e_dist"])
            c["candidate_id"] = "ATTACK:pressure"
            out.append(c)
    if P["support"] and F.get("a_vec") is not None and F.get("e_mass", 0) > 0:
        wp = mass.waypoint(F["a_vec"], P["support_step"])
        if wp >= 0 and wp != w.HEAD:
            c = candidate("RETREAT", wp, support=True, a_mass=F["a_mass"], e_mass=F["e_mass"])
            c["candidate_id"] = "RETREAT:support"
            out.append(c)
    return out
