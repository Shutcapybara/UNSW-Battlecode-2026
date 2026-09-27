"""ladder.py -- the production-first priority ladder (hunter-v20's policy).

Base: ouroboros; borrowed: the decision ladder of hunter-v20-portal-scouts
(user line), ported to our world model.  It is one point of the parameter
space (HANDOFF §4.2 convergence test): an option ordering with infinite
weight gaps instead of the evaluation function.

    1. attack   units >= ladder_attack_units: sprint into a visible enemy head
                that is LONGER than us, reachable within len-1 free steps
    2. split    length >= ladder_split_min: SPLIT child_size
    3. food     nearest visible pearl we own (route distance, ties by id)
    4. explore  friend spacing, view frontier, pearl hotspots, unscouted sectors

Everything is local to the 7x7 view, like the original.  Our additions:
exact simulation vetoes a move that is certain death (ladder_safety), and
roles the ladder does not cover (crown, feeding) stay with the evaluator.
Enabled by P["ladder"] (doctrine: compact maps).  Uses world.py state.
"""

LAD = {"sect": None, "sw": 0}


def ladder_active():
    return P["ladder"] and ROLE != CROWN and FEED[0] < 0 and RND < P["ladder_until"]


def _view():
    hx = HEAD % W
    hy = HEAD // W
    vis = set()
    for dy in range(-3, 4):
        base = ((hy + dy) % H) * W
        for dx in range(-3, 4):
            vis.add(base + (hx + dx) % W)
    return vis


def _adj(vis):
    """cell -> 4 destinations within the view: -1 wall/portal, -2 outside."""
    out = {}
    _ek = ek
    for c in vis:
        nb = nbr(c)
        x = c % W
        ks = (c, NC + (c + 1 if x + 1 < W else c + 1 - W), nb[2], NC + c)
        row = [-1, -1, -1, -1]
        for d in range(4):
            t = _ek[ks[d]]
            if t != 2 and t != 3:
                n = nb[d]
                row[d] = n if n in vis else -2
        out[c] = row
    return out


def _bfs(src, adj, blocked):
    dist = {src: 0}
    q = [src]
    qi = 0
    while qi < len(q):
        p = q[qi]
        qi += 1
        dn = dist[p] + 1
        for n in adj[p]:
            if n >= 0 and n not in dist and (blocked is None or n not in blocked):
                dist[n] = dn
                q.append(n)
    return dist


def _grid_field(sources, cap):
    """Multi-source BFS over plain grid adjacency (walls ignored), depth <= cap."""
    dist = {}
    q = []
    for c, d0 in sources:
        if d0 <= cap and dist.get(c, 99) > d0:
            dist[c] = d0
            q.append(c)
    q.sort(key=lambda c: dist[c])
    qi = 0
    while qi < len(q):
        p = q[qi]
        qi += 1
        dn = dist[p] + 1
        if dn > cap:
            continue
        for n in nbr(p):
            if dist.get(n, 99) > dn:
                dist[n] = dn
                q.append(n)
    return dist


def _near_field(sources, cap, cells):
    """Torus-manhattan distance from each view cell to the nearest source
    (plus the source's start value), kept when <= cap.  Sources outside the
    7x7 window are projected onto its border (exact for manhattan distance),
    then one two-pass distance transform over the window: O(sources + 49)."""
    hx = HEAD % W
    hy = HEAD // W
    hw = W // 2
    hh = H // 2
    g = [99] * 49
    lim = cap + 6
    for c, d0 in sources:
        if d0 > cap:
            continue
        dx = (c % W - hx + hw) % W - hw
        dy = (c // W - hy + hh) % H - hh
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        if ax + ay + d0 > lim:
            continue
        v = d0
        if dx > 3:
            v += dx - 3
            dx = 3
        elif dx < -3:
            v += -3 - dx
            dx = -3
        if dy > 3:
            v += dy - 3
            dy = 3
        elif dy < -3:
            v += -3 - dy
            dy = -3
        i = (dy + 3) * 7 + dx + 3
        if v < g[i]:
            g[i] = v
    for i in range(49):
        v = g[i]
        if i % 7 and g[i - 1] + 1 < v:
            v = g[i - 1] + 1
        if i >= 7 and g[i - 7] + 1 < v:
            v = g[i - 7] + 1
        g[i] = v
    for i in range(48, -1, -1):
        v = g[i]
        if i % 7 != 6 and g[i + 1] + 1 < v:
            v = g[i + 1] + 1
        if i < 42 and g[i + 7] + 1 < v:
            v = g[i + 7] + 1
        g[i] = v
    out = {}
    for c in cells:
        dx = (c % W - hx + hw) % W - hw
        dy = (c // W - hy + hh) % H - hh
        if -3 <= dx <= 3 and -3 <= dy <= 3:
            v = g[(dy + 3) * 7 + dx + 3]
            if v <= cap:
                out[c] = v
    return out


def _sectors(vis):
    if LAD["sect"] is None:
        LAD["sw"] = (W + 3) // 4
        LAD["sect"] = bytearray(LAD["sw"] * ((H + 3) // 4))
    sw = LAD["sw"]
    sect = LAD["sect"]
    for c in vis:
        sect[(c // W // 4) * sw + (c % W) // 4] = 1
    return sect


def ladder_decide():
    body = body_list()
    bset = set(body)
    vis = _view()
    adj = _adj(vis)
    blocked = set(occ)
    blocked.update(bset)
    blocked.discard(HEAD)
    order = [(o + MY_ID + RND // 8) & 3 for o in range(4)]

    # 1. attack: trade up into a longer enemy head
    if UNITS >= P["ladder_attack_units"] and LEN >= 2:
        reach = LEN - 1
        path = {HEAD: []}
        q = [HEAD]
        qi = 0
        hit = None
        while qi < len(q) and hit is None:
            p = q[qi]
            qi += 1
            if len(path[p]) >= reach:
                continue
            row = adj[p]
            for d in order:
                n = row[d]
                if n < 0 or n in path:
                    continue
                path[n] = path[p] + [d]
                o = occ.get(n)
                if o is not None:
                    if o[2] and not o[1] and enemy_len.get(o[0], 0) > LEN:
                        hit = path[n]
                        break
                    continue
                if n in bset:
                    continue
                q.append(n)
        if hit:
            res = simulate(hit, body)
            if res[4] is not None:
                return (0.0, hit, "strike"), -1

    # 2. split
    if LEN >= P["ladder_split_min"] and UNITS < UNIT_LIMIT and RND < P["split_stop"]:
        return (0.0, P["child_size"], "split"), -1

    # 3/4. food, else explore
    dist = {HEAD: 0}
    first = {}
    q = [HEAD]
    qi = 0
    while qi < len(q):
        p = q[qi]
        qi += 1
        dn = dist[p] + 1
        row = adj[p]
        for d in order:
            n = row[d]
            if n < 0 or n in dist or n in blocked:
                continue
            dist[n] = dn
            first[n] = d if p == HEAD else first[p]
            q.append(n)
    friends = sorted((v[0], c) for c, v in occ.items() if v[1] and v[2])
    # one multi-source BFS per layer instead of two per friend (CPU): live
    # routes give ownership (distance, then lower id) and friend distance;
    # terrain routes (through bodies), then torus distance, are the fallbacks
    own = {}
    q = []
    for fid, fc in friends:
        if fc in adj and fc not in own:
            own[fc] = (0, fid)
            q.append(fc)
    qi = 0
    while qi < len(q):
        p = q[qi]
        qi += 1
        dd, fid = own[p]
        dd += 1
        for n in adj[p]:
            if n >= 0 and n not in own and n not in blocked:
                own[n] = (dd, fid)
                q.append(n)
    terr = None
    nf_memo = {}

    def nearest_friend(c):
        nonlocal terr
        v = nf_memo.get(c)
        if v is not None:
            return v
        o = own.get(c)
        if o is not None:
            best = o[0]
        elif not friends:
            best = 99
        else:
            if terr is None:
                terr = {}
                tq = []
                for fid, fc in friends:
                    if fc in adj and fc not in terr:
                        terr[fc] = 0
                        tq.append(fc)
                ti = 0
                while ti < len(tq):
                    p = tq[ti]
                    ti += 1
                    dn = terr[p] + 1
                    for n in adj[p]:
                        if n >= 0 and n not in terr:
                            terr[n] = dn
                            tq.append(n)
            best = terr.get(c)
            if best is None:
                best = min(tdist(c, fc) for fid, fc in friends)
        nf_memo[c] = best
        return best

    pearl = -1
    ps = -10 ** 9
    for c, dd in dist.items():
        if dd == 0 or pearls.get(c) != RND:
            continue
        o = own.get(c)
        if o is not None and o < (dd, MY_ID):
            continue
        fd = nearest_friend(c)
        s = -dd * 100 + (fd if fd < 10 else 10) - visits[c]
        if s > ps:
            ps = s
            pearl = c
    target = pearl
    if target < 0:
        # hotspots: pearls seen in the last 8 rounds, beds due within 8,
        # and (hot_slots) hotspots allies told us about
        hot = []
        for c, r in pearls.items():
            if RND - r <= 8:
                hot.append((c, 0))
        for c, w in spawn_at.items():
            cd = w - RND
            if 0 <= cd <= 8:
                st = 6 - cd // 2
                hot.append((c, (12 - (st if st > 1 else 1)) // 2))
        if P["hot_slots"]:
            for c, (obs, st) in hotspots().items():
                hot.append((c, (12 - st) // 2))
        hfield = _near_field(hot, 10, dist) if hot else {}
        sect = _sectors(vis)
        sw = LAD["sw"]
        unsc = []
        for i in range(len(sect)):
            if not sect[i]:
                x = min(W - 1, (i % sw) * 4 + 2)
                y = min(H - 1, (i // sw) * 4 + 2)
                unsc.append((y * W + x, 0))
        ufield = _near_field(unsc, 12, dist) if unsc else {}
        es = -10 ** 9
        for c, dd in dist.items():
            if dd == 0:
                continue
            fr = 0
            for d in range(4):
                if nbr(c)[d] not in vis and ek[ekey(c, d)] != 2:
                    fr += 1
            s = nearest_friend(c) * 60 + fr * 80 - dd * 8 - visits[c] * 3
            hd = hfield.get(c, 99)
            if hd < 10:
                s += (10 - hd) * 35
            ud = ufield.get(c, 99)
            if ud < 12:
                s += (12 - ud) * 25
            if s > es:
                es = s
                target = c
    if target >= 0:
        d = first[target]
    else:
        d = -1
        for dd in range(4):
            if adj[HEAD][dd] == -2:
                d = dd
                break
        if d < 0:
            return None
    if P["ladder_safety"]:
        res = simulate([d], body)
        if not res[0] and res[4] is None:
            return None  # certain death: let the evaluator find a way out
        if P["ladder_safety"] >= 2 and res[0]:
            need = LEN + P["space_slack"]
            if flood(res[1], res[5], need + 1, NOSET) < need:
                return None  # a pocket too small for us: the evaluator scores the escape
        if res[0] and P["ladder_risk_max"] < 90:
            if head_risk(res[1], res[2], threat_map(), NOSET) > P["ladder_risk_max"]:
                return None  # an enemy head can take this tile: the evaluator prices it
    # The production ladder's local grid excludes every portal edge, so its
    # chosen step can never be a portal dive. When portal access is enabled,
    # hand control to the evaluator if a paired portal is directly available;
    # it can compare that move with ordinary steps and, when separately enabled,
    # price blind exits from remembered occupancy. Unpaired portals remain
    # under the old policy.
    if P["portal_access"]:
        for pd in range(4):
            if ek[ekey(HEAD, pd)] != 3:
                continue
            exit_cell = dest(HEAD)[pd]
            if exit_cell < 0 or not simulate([pd], body)[0]:
                continue
            portal_risk = blind_memory_risk([pd])
            if TRACE:
                trace("PM_LADDER_DEFER r%d id%d d%d exit%d risk%s" %
                      (RND, MY_ID, pd, exit_cell,
                       "none" if portal_risk is None else "%.2f" % portal_risk))
            return None
    return (0.0, [d], "move"), target
