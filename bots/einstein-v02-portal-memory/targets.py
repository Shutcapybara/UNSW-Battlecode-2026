"""targets.py -- the goal field: which cell this dragon heads for.

choose_target: forward BFS scoring cells with the role's selector weights
(pearls, predicted spawns, frontier, unpaired portals, zone danger, enemy
pull); waypoint: zone-level fallback; reverse_dist: distances to target.
"""

# ======================================================================
# GOAL FIELD
# ======================================================================
def unpaired_portal_cells():
    """Cells beside a portal edge whose far end we have not seen: stepping
    through is the only way to learn where it goes (and often the only way
    out of a walled base)."""
    out = set()
    for pid, ends in pends.items():
        if len(ends) == 1:
            k = ends[0]
            if k < NC:
                out.add(k)
                out.add(k - W if k >= W else k - W + NC)
            else:
                c = k - NC
                out.add(c)
                out.add(c - 1 if c % W else c - 1 + W)
    return out


def choose_target(tm):
    """Forward BFS from the head; score cells as targets with role weights.
    Returns (target cell, far waypoint flag)."""
    global bstamp
    rp = RP[ROLE]
    bstamp += 1
    st = bstamp
    cap = P["bfs_cap"]
    w_dist = P["w_dist"]
    w_pearl = rp["w_pearl"]
    w_spawn = rp["w_spawn"]
    w_front = rp["w_frontier"]
    w_zd = rp["w_zone_danger"]
    window = P["spawn_window"]
    stale = P["pearl_stale"]
    q = [HEAD]
    bmark[HEAD] = st
    bdist[HEAD] = 0
    qi = 0
    best = -1
    best_s = -1e9
    _pearls = pearls
    _spawn = spawn_at
    _unk = unk
    _occ = occ
    body = set(body_list())
    own_disc = P["own_disc"]
    upc = unpaired_portal_cells()
    w_portal = rp["w_frontier"] * P["portal_explore"]
    # pearls a clearly closer head will take: allies always; enemies only if
    # own_enemy (leaving pearls to the enemy just feeds its swarm)
    own_enemy = P["own_enemy"]
    others = [c for c, v in occ.items() if v[2] and (v[1] or own_enemy) and tdist(c, HEAD) <= 8]
    for c, ln, r, when in allies.values():
        if RND - when <= 1 and tdist(c, HEAD) <= 10:
            others.append(c)
    while qi < len(q) and len(q) < cap:
        c = q[qi]
        qi += 1
        dn = bdist[c] + 1
        for n in dest(c):
            if n < 0 or bmark[n] == st or n in _occ or n in body:
                continue
            bmark[n] = st
            bdist[n] = dn
            q.append(n)
            s = 0.0
            pr = _pearls.get(n)
            if pr is not None:
                s += w_pearl if RND - pr < stale else w_pearl * 0.4
            else:
                sp = _spawn.get(n)
                if sp is not None:
                    lag = sp - (RND + dn)
                    if -4 <= lag <= window:
                        s += w_spawn * (1.0 - (lag if lag > 0 else -lag) / (window + 4.0))
            if _unk[n]:
                s += w_front
            if n in upc:
                s += w_portal
            if s <= 0.0:
                continue
            if others:
                # someone else is clearly closer: leave it to them
                for oc in others:
                    if tdist(oc, n) + 1 < dn:
                        s *= own_disc
                        break
            if w_zd:
                s -= w_zd * zone_danger(n) * 0.25
            s -= w_dist * dn
            if n in tm:
                s -= 3.0
            if s > best_s:
                best_s = s
                best = n
    # role pulls that are not tile-local
    if rp["w_enemy"] > 0:
        for eid, (c, r, ln) in enemies.items():
            age = RND - r
            if age > 30:
                continue
            d = bdist[c] if bmark[c] == st else tdist(HEAD, c) * 1.3
            if d <= 0:
                continue
            s = rp["w_enemy"] * (1.0 - age / 30.0) * (1.0 + 0.1 * min(ln, 10)) - w_dist * d
            if s > best_s:
                best_s = s
                best = c
    far = -1
    if best_s < 1.0:
        far = cached_waypoint()
        if far >= 0:
            s = 1.0
            if bmark[far] == st:
                best = far
                best_s = s
    return best, far, best_s


WP = [-1, -99]


def cached_waypoint():
    """The zone scan is a few thousand interpreter lines: redo it every few
    rounds, or when we have arrived."""
    if WP[0] < 0 or RND - WP[1] >= P["waypoint_every"] or tdist(HEAD, WP[0]) <= 2:
        WP[0] = waypoint()
        WP[1] = RND
    return WP[0]


def waypoint():
    """Strategic target when nothing local is worth chasing: a zone center
    chosen by role (scouts: stalest, hunters: hottest, gatherers: richest-safe)."""
    rp = RP[ROLE]
    bestz = -1
    bs = -1e9
    hx = HEAD % W
    hy = HEAD // W
    salt = (MY_ID * 7919) & 0xFFFF
    zone_allies = {}
    for c, ln, r, when in allies.values():
        if RND - when <= 10:
            z = zone_of(c)
            zone_allies[z] = zone_allies.get(z, 0) + 1
    for zy in range(ZH):
        for zx in range(ZW):
            cx = min(W - 1, zx * ZS + ZS // 2)
            cy = min(H - 1, zy * ZS + ZS // 2)
            c = cy * W + cx
            if c == HEAD:
                continue
            dx = abs(cx - hx)
            dy = abs(cy - hy)
            if dx * 2 > W:
                dx = W - dx
            if dy * 2 > H:
                dy = H - dy
            d = dx + dy
            z = zy * ZW + zx
            last = seen[c]
            age = (RND + 1 - last) if last else 200
            s = rp["w_stale"] * min(age, 200) / 40.0
            s += rp["w_frontier"] * (0.5 if unk[c] else 0.0)
            zd = zone_danger(c)
            s -= rp["w_zone_danger"] * zd * 0.5
            if ROLE == HUNT:
                s += 2.0 * zd
            s -= P["w_zone_crowd"] * zone_allies.get(z, 0)
            s -= 0.08 * d
            s += ((salt + z * 131) % 97) / 97.0 * 1.5  # spread different dragons
            if s > bs:
                bs = s
                bestz = c
    return bestz


def reverse_dist(target, wanted):
    """BFS distances from target over known passable cells (edges reversed:
    moving n->c is legal iff c in dest(n); we approximate with symmetric edges,
    exact except for one-way portal geometry)."""
    need = set(wanted)
    out = {}
    if target in need:
        out[target] = 0
        need.discard(target)
    got = {target: 0}
    q = [target]
    qi = 0
    cap = P["rbfs_cap"]
    while qi < len(q) and need and len(got) < cap:
        c = q[qi]
        qi += 1
        dn = got[c] + 1
        for n in dest(c):
            if n < 0 or n in got:
                continue
            got[n] = dn
            if n in need:
                out[n] = dn
                need.discard(n)
            if n not in occ:
                q.append(n)
    return out
