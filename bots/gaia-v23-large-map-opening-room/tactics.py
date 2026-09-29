"""FEATURES layer (local tactics): exact move simulation, time-aware flood
fill, enemy reach (threat) and route search.  Pure functions of world state."""
import world as w
from params import P


def sim(path, body):
    """Exact engine simulation of MOVE path for our dragon.

    Returns (status, body_after, eaten, hit) where status is
    'ok', 'dead' or 'h2h' (hit = id of the head we collide with).
    """
    b = list(body)
    own = set(b)
    occ = w.occ
    pearls = w.pearls
    rnd = w.RND
    eaten = 0
    ate = set()
    BLIND[0] = 0
    BLINDCELL[0] = -1
    for k, d in enumerate(path):
        if k and len(b) <= 2:
            return "dead", b, eaten, None
        n = w.dest(b[-1])[d]
        if n == -2:           # unknown edge inside view should not happen
            n = w.nbr(b[-1])[d]
        if n == -3:           # unpaired portal: the landing tile is unknown
            return ("dive" if k == 0 else "dead"), b, eaten, None
        if n < 0:
            return "dead", b, eaten, None
        if n in own:
            return "dead", b, eaten, None
        if w.cheb(n, w.HEAD) > 3:
            BLIND[0] += 1   # through a portal to a tile we cannot see
            if BLINDCELL[0] < 0:
                BLINDCELL[0] = n
        o = occ.get(n)
        if o is not None:
            if o[2]:
                return "h2h", b, eaten, o[0]
            return "dead", b, eaten, None
        b.append(n)
        own.add(n)
        if pearls.get(n) == rnd and n not in ate:
            ate.add(n)
            eaten += 1
        else:
            own.discard(b.pop(0))
        if k:
            own.discard(b.pop(0))
    return "ok", b, eaten, None


BLIND = [0]   # set by sim: steps that landed outside the view (portal exits)
BLINDCELL = [-1]  # first such landing cell, for portal-exit risk memory
POCKET = [0]  # set by flood: visible pearls inside the region it counted


def flood(body, need, t_other):
    """Room reachable from body's head, respecting when our own segments
    vacate (segment i from the tail is free from our (i+2)-th move) and other
    bodies (blocked for t <= t_other).  Cells next to another dragon's head
    are blocked for t <= head_block (it may step there first).  Known terrain
    only: a rim cell with an unknown edge credits fcred cells of probable room,
    an unpaired portal credits fcred_portal (an exit to somewhere new).
    Stops at `need`."""
    head = body[-1]
    idx = {}
    for i, c in enumerate(body):
        idx[c] = i
    vac = w.vac
    # Larger boards have enough alternate corridors for the opening split
    # check to use the roomier policy. Compact boards keep the strict block so
    # reproduction does not trade away the only local escape route.
    opening_room = (w.RND < P.get("opening_until", 100)
                    and w.W * w.H >= P.get("opening_room_area", 1000))
    hb = P.get("opening_head_block", 0) if opening_room else P["head_block"]
    near = HEADNEAR[0]
    seen = {head: 0}
    q = [head]
    qi = 0
    n_ok = 0
    fc = P["fcred"]
    fp = P["fcred_portal"]
    pearls = w.pearls
    rnd = w.RND
    pk = 0
    POCKET[0] = 0
    while qi < len(q):
        c = q[qi]
        qi += 1
        t = seen[c] + 1
        rim = 0
        for n in w.dest(c):
            if n < 0:
                if n == -2 and rim < fc:
                    n_ok += fc - rim
                    rim = fc
                elif n == -3 and rim < fp:
                    n_ok += fp - rim
                    rim = fp
                if n_ok >= need:
                    return n_ok
                continue
            if n in seen:
                continue
            i = idx.get(n)
            if i is not None and t < i + 2:
                continue
            v = vac.get(n)
            if v is not None and t < v:
                continue
            if t <= hb and n in near:
                continue
            seen[n] = t
            q.append(n)
            n_ok += 1
            if pearls.get(n) == rnd:
                pk += 1
            if n_ok >= need:
                POCKET[0] = pk
                return n_ok
    POCKET[0] = pk
    return n_ok


HEADNEAR = [set()]


def set_head_near():
    """Cells an other dragon's head can step into next (for flood)."""
    s = set()
    for c, o in w.occ.items():
        if o[2]:
            for n in w.dest(c):
                if n >= 0:
                    s.add(n)
    HEADNEAR[0] = s


def exits(body):
    """Free neighbours of the head right now (for next turn), tail excluded."""
    head = body[-1]
    own = set(body[1:]) if len(body) > 1 else set()
    n_ok = 0
    for n in w.dest(head):
        if n == -2:
            continue
        if n >= 0 and n not in own and n not in w.occ:
            n_ok += 1
    return n_ok


def threat_map():
    """cell -> list of (steps, enemy id, enemy visible length) for every cell an
    enemy head can reach in its next action (sprints up to len-1, max 3)."""
    out = {}
    occ = w.occ
    for ec, eid in w.enemy_heads:
        if w.cheb(ec, w.HEAD) > 7:
            continue
        el = w.elen.get(eid, 1)
        if eid in w.cut:
            el += P["cut_extra"]   # its body continues out of view
        reach = el - 1
        if reach < 1:
            reach = 1
        if reach > 3:
            reach = 3
        dist = {ec: 0}
        q = [ec]
        qi = 0
        while qi < len(q):
            c = q[qi]
            qi += 1
            dc = dist[c]
            if dc >= reach:
                continue
            for n in w.dest(c):
                if n < 0 or n in dist:
                    continue
                if n in occ:
                    continue
                dist[n] = dc + 1
                q.append(n)
        for c, dc in dist.items():
            if dc:
                out.setdefault(c, []).append((dc, eid, el))
    return out


def bfs_from(src, cap, blocked_until, own_idx):
    """Route search from src over optimistic terrain.  Returns (dist, first)
    dicts; `first` is the first direction taken from src.  Other bodies
    block until they vacate (world.vac); own segment i blocks while
    depth < i + 2."""
    vac = w.vac
    dist = {src: 0}
    first = {src: -1}
    dives = []   # (cell, dir, depth, first dir): unpaired portals to explore
    q = [src]
    qi = 0
    while qi < len(q) and len(q) < cap:
        c = q[qi]
        qi += 1
        t = dist[c] + 1
        fc = first[c]
        g = w.step_opt(c)
        for d in range(4):
            n = g[d]
            if n < 0:
                if n == -3:
                    dives.append((c, d, t, d if fc < 0 else fc))
                continue
            if n in dist:
                continue
            i = own_idx.get(n)
            if i is not None and t < i + 2:
                continue
            v = vac.get(n)
            if v is not None and t < v:
                continue
            dist[n] = t
            first[n] = d if fc < 0 else fc
            q.append(n)
    return dist, first, dives


def rev_dist(target, cap, stop_cells):
    """Terrain distance to target (portals are two-way, kelp symmetric)."""
    dist = {target: 0}
    q = [target]
    qi = 0
    left = set(stop_cells)
    left.discard(target)
    while qi < len(q) and left and len(q) < cap:
        c = q[qi]
        qi += 1
        t = dist[c] + 1
        for n in w.step_opt(c):
            if n < 0 or n in dist:
                continue
            dist[n] = t
            q.append(n)
            left.discard(n)
    return dist
