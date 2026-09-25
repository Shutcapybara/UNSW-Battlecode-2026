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
    for k, d in enumerate(path):
        if k and len(b) <= 2:
            return "dead", b, eaten, None
        n = w.dest(b[-1])[d]
        if n == -2:           # unknown edge inside view should not happen
            n = w.nbr(b[-1])[d]
        if n < 0:
            return "dead", b, eaten, None
        if n in own:
            return "dead", b, eaten, None
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


def flood(body, need, t_other):
    """Cells reachable from body's head, respecting when our own segments
    vacate (segment i from the tail is free from our (i+2)-th move) and other
    bodies (blocked for t <= t_other).  Stops at `need` cells."""
    head = body[-1]
    idx = {}
    for i, c in enumerate(body):
        idx[c] = i
    occ = w.occ
    seen = {head: 0}
    q = [head]
    qi = 0
    n_ok = 0
    while qi < len(q):
        c = q[qi]
        qi += 1
        t = seen[c] + 1
        for n in w.step_opt(c):
            if n < 0 or n in seen:
                continue
            i = idx.get(n)
            if i is not None and t < i + 2:
                continue
            if t <= t_other and n in occ:
                continue
            seen[n] = t
            q.append(n)
            n_ok += 1
            if n_ok >= need:
                return n_ok
    return n_ok


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
    dicts; `first` is the first direction taken from src.  Bodies of other
    dragons block up to depth blocked_until; own segment i blocks while
    depth < i + 2."""
    occ = w.occ
    dist = {src: 0}
    first = {src: -1}
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
            if n < 0 or n in dist:
                continue
            i = own_idx.get(n)
            if i is not None and t < i + 2:
                continue
            if t <= blocked_until and n in occ:
                continue
            dist[n] = t
            first[n] = d if fc < 0 else fc
            q.append(n)
    return dist, first


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
