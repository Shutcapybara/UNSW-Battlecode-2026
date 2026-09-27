"""safety.py -- threat model, exact simulation, space / trap tests.

threat_map: enemy head reach; head_risk: p_strike(k) x value exchanged;
simulate: exact engine rules for a step list; flood/doom/tunnel_heads:
escape space, enclosed dead ends, 1-wide tunnels with heads in them.
"""

# ======================================================================
# THREAT
# ======================================================================
def threat_map():
    """cell -> list of (steps, enemy id) for every visible enemy head's sprint reach.

    Paths go through free tiles only; the destination may be anything (the
    strike lands on our head wherever it ends up)."""
    tm = {}
    reach_cap = P["threat_reach"]
    for ec, eid in enemy_heads:
        ln = enemy_len.get(eid, 2)
        # the visible count is a lower bound; assume one more if it touches the window edge
        reach = min(reach_cap, max(1, ln - 1))
        frontier = [ec]
        seen_ = {ec: 0}
        for s in range(1, reach + 1):
            nxt = []
            for c in frontier:
                for n in dest(c):
                    if n < 0 or n in seen_:
                        continue
                    seen_[n] = s
                    lst = tm.get(n)
                    if lst is None:
                        tm[n] = [(s, eid)]
                    else:
                        lst.append((s, eid))
                    if n not in occ:
                        nxt.append(n)
            frontier = nxt
    return tm


def split_threat_cells():
    """Tiles next to the visible tail of long enemies (a newborn can strike once)."""
    out = set()
    for eid, n in enemy_len.items():
        if n < 4:
            continue
        # find its tail-most visible segment: a segment no other segment points to
        segs = [c for c, v in occ.items() if v[0] == eid and not v[2]]
        if not segs:
            continue
        # cheap: every neighbour of every non-head segment end
        for c in segs[-1:]:
            for m in dest(c):
                if m >= 0:
                    out.add(m)
    return out


def dragon_value(ln, role=None):
    return P["unit_value"] + lv() * ln


def lv():
    """Value of one segment: ramps up towards the end of the game."""
    a = P["len_value"]
    b = P["len_value_end"]
    s = P["end_start"] - 100
    if RND <= s:
        return a
    f = (RND - s) / (500.0 - s)
    return a + (b - a) * (f if f < 1 else 1)


def head_risk(cell, my_len_after, tm, split_cells):
    """Expected material loss from enemy strikes on this head tile before our next turn."""
    lst = tm.get(cell)
    rp = RP[ROLE]
    risk = 0.0
    if lst:
        my_v = dragon_value(my_len_after)
        survive = 1.0
        worst = 0.0
        for s, eid in lst:
            p = P["p_strike1"] if s == 1 else P["p_strike2"] if s == 2 else P["p_strike3"]
            survive *= 1.0 - p
            their_v = dragon_value(enemy_len.get(eid, 2))
            loss = my_v - their_v + P["trade_bias"]
            if loss > worst:
                worst = loss
        if worst < 0.5:
            worst = 0.5
        risk = (1.0 - survive) * worst
    if cell in split_cells:
        risk += P["p_split_child"] * dragon_value(my_len_after)
    return risk * rp["risk"]


# ======================================================================
# SEARCH SUPPORT
# ======================================================================
def body_list():
    n = LEN if LEN < len(trail) else len(trail)
    return trail[-n:]


def simulate(path, body):
    """Apply a step list to our body (tail first list).  Returns
    (alive, head, len, eaten, struck_enemy_id, new_body) with exact engine rules."""
    b = list(body)
    ln = len(b)
    eaten = 0
    cell = b[-1]
    for i, d in enumerate(path):
        if i > 0 and ln <= 2:
            return (False, cell, ln, eaten, None, b)
        n = dest(cell)[d]
        if n < 0:
            return (False, cell, ln, eaten, None, b)
        if n in b:
            # own segment (the tail too: collision precedes tail movement)
            return (False, n, ln, eaten, None, b)
        o = occ.get(n)
        if o is not None:
            if o[2] and not o[1]:
                return (False, n, ln, eaten, o[0], b)  # strike
            return (False, n, ln, eaten, None, b)
        b.append(n)
        cell = n
        if n in pearls:
            eaten += 1
        else:
            del b[0]
        if i > 0:
            del b[0]
        ln = len(b)
    return (True, cell, ln, eaten, None, b)


NOSET = frozenset()


def flood(start, body, cap, blocked2):
    """Tiles reachable from start avoiding bodies and contested tiles (next to
    another head: it may step there first); our own body frees up from the
    tail as we move."""
    bset = {}
    nb = len(body)
    for i, c in enumerate(body):
        bset[c] = i  # 0 = tail
    got = {start: 0}
    q = [start]
    qi = 0
    while qi < len(q) and len(got) < cap:
        c = q[qi]
        qi += 1
        dep = got[c] + 1
        for n in dest(c):
            if n < 0 or n in got or n in occ or n in blocked2:
                continue
            j = bset.get(n)
            if j is not None and j >= dep - 1:
                continue
            got[n] = dep
            q.append(n)
    return len(got)


def doom(start, body):
    """Permanent-trap test, ignoring other dragons (they move) but not our own
    body (it frees from the tail).  Returns -1 when the region reachable from
    start is open, else the number of known pearls inside it: the region is
    enclosed by kelp/our body and cannot hold us (too small, or acyclic: a
    1-wide dead end where we can never turn around)."""
    bset = {}
    for i, c in enumerate(body):
        bset[c] = i
    cap = 3 * len(body) + 12
    if cap > P["doom_cap"]:
        cap = P["doom_cap"]
    got = {start: 0}
    q = [start]
    qi = 0
    edges = 0
    while qi < len(q):
        c = q[qi]
        qi += 1
        dep = got[c] + 1
        ds = dest(c)
        for d in range(4):
            n = ds[d]
            if n < 0:
                if n == -2 or ek[ekey(c, d)] == 3:
                    return -1  # unknown edge / unpaired portal: maybe an exit
                continue
            if n in got:
                edges += 1
                continue
            j = bset.get(n)
            if j is not None and j >= dep - 1:
                continue
            got[n] = dep
            q.append(n)
            edges += 1
            if len(got) >= cap:
                return -1
    size = len(got)
    # every internal edge was counted from both ends (tree edges once each way)
    cyclic = edges // 2 >= size
    if size < len(body) + 2 or not cyclic:
        n = 0
        for c in got:
            if c in pearls:
                n += 1
        return n
    return -1


def tunnel_heads(cell, came):
    """Walk forward through a 1-wide tunnel from cell (entered from `came`).
    Unknown side edges do not end the walk (tunnels run beyond our window);
    a known junction does.  Returns 2 if a head (visible, or an ally's
    recent self report) sits in the tunnel ahead, 1 if a body blocks it."""
    prev = came
    cur = cell
    heading = -1
    for d in range(4):
        if dest(came)[d] == cell or nbr(came)[d] == cell:
            heading = d
    recent = [ac for ac, ln, r, when in allies.values() if RND - when <= 2]
    steps = 0
    for _ in range(18):
        ds = dest(cur)
        known = [n for n in ds if n >= 0 and n != prev]
        unknown = sum(1 for n in ds if n == -2)
        if len(known) > 1 or (len(known) == 1 and unknown):
            return 0          # a junction: not a tunnel from here on
        if known:
            nxt = known[0]
        elif unknown and heading >= 0:
            if steps >= 1:
                return 3      # a known tunnel running on into the unknown
            nxt = nbr(cur)[heading]   # assume the tunnel runs straight on
        else:
            return 0          # dead end: doom() handles it
        steps += 1
        o = occ.get(nxt)
        if o is not None:
            return 2 if o[2] else 1
        if nxt in recent:
            return 2
        for d in range(4):
            if ds[d] == nxt or nbr(cur)[d] == nxt:
                heading = d
        prev = cur
        cur = nxt
    return 0


def blind_portal(path):
    """Does this path go through a portal onto a tile we cannot see?  The
    landing may be occupied: that is a body death we never saw coming."""
    cell = HEAD
    for d in path:
        n = dest(cell)[d]
        if n < 0:
            return True
        if ek[ekey(cell, d)] == 3 and not in_view(n):
            return True
        cell = n
    return False


def blind_exit_cells(path):
    """Known paired portal exits crossed outside vision, or None if a landing
    is unknown (an unpaired portal)."""
    cells = []
    cell = HEAD
    for d in path:
        n = dest(cell)[d]
        if n < 0:
            return None
        if ek[ekey(cell, d)] == 3 and not in_view(n):
            cells.append(n)
        cell = n
    return cells


def blind_memory_risk(path):
    """Estimated occupancy risk for known blind exits. Recent remembered
    bodies raise risk only if that cell has not since been seen clear."""
    if not P["portal_memory"]:
        return None
    cells = blind_exit_cells(path)
    if cells is None or not cells:
        return None
    recent = P["portal_mem_recent"]
    risk = P["portal_mem_floor"]
    for c in cells:
        if RND + 1 - seen[c] > recent:
            risk = max(risk, P["portal_mem_unseen"])
        around = (c,) + tuple(nbr(c))
        for x in around:
            age = body_seen.get(x)
            if age is None or RND - age > recent:
                continue
            if seen[x] > age + 1 and x not in occ:
                continue
            risk = 1.0
            break
    return risk


def fallback_move():
    """Least-bad single step when nothing scored (all options fatal)."""
    body = body_list()
    best = FACING
    bv = -1e9
    for d in range(4):
        n = dest(HEAD)[d]
        v = 0.0
        if n < 0:
            v = -100.0
        elif n in body:
            v = -90.0
        else:
            o = occ.get(n)
            if o is not None:
                if o[1] and o[2]:
                    v = -200.0  # ally head: kills two of ours
                elif o[1]:
                    v = -80.0
                elif o[2]:
                    v = -10.0   # enemy head: at least a trade
                else:
                    v = -60.0
        if v > bv:
            bv = v
            best = d
    return best
