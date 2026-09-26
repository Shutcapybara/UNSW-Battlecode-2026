"""STATE/FEATURES: instance-specific map topology around a cell.

room(c): cells reachable from c within ROOM_R steps over static terrain
(known-open edges, unknown edges optimistic, kelp blocked, paired portals
followed, unpaired portals end the walk). Bodies are ignored: this is the
shape of the space, not its current occupancy. Units: cells. The open-torus
maximum for radius r is 2r^2 + 2r + 1 (41 at r = 4).

Cached per cell; the cache is dropped whenever world learns a new edge
(world.EPOCH changes), so a known area costs nothing after the first query.

Derived per-turn features (units in brackets):
  open_frac   room(head) / diamond size                      [0..1]
  local_mass  own length + visible ally + enemy segments       [segments]
  crowd       local_mass / room(head)                          [segments/cell]
  local_units ally + enemy dragons in view (+ self)            [dragons]
"""
import world as w
from params import P

CACHE = {}
EPOCH = [-1]
F = {}


def diamond(r):
    return 2 * r * r + 2 * r + 1


def room(c, r=None):
    if r is None:
        r = P["room_r"]
    if EPOCH[0] != w.EPOCH[0]:
        CACHE.clear()
        EPOCH[0] = w.EPOCH[0]
    key = c * 16 + r
    v = CACHE.get(key)
    if v is not None:
        return v
    dist = {c: 0}
    q = [c]
    qi = 0
    while qi < len(q):
        x = q[qi]
        qi += 1
        t = dist[x]
        if t >= r:
            continue
        for n in w.step_opt(x):
            if n >= 0 and n not in dist:
                dist[n] = t + 1
                q.append(n)
    v = len(q)
    CACHE[key] = v
    return v


def update():
    """Once per turn, after world.sense()."""
    r = P["room_r"]
    rm = room(w.HEAD, r)
    mass = w.LEN + sum(w.alen.values()) + sum(w.elen.values())
    F["room"] = rm
    F["open_frac"] = rm / float(diamond(r))
    F["local_mass"] = mass
    F["crowd"] = mass / float(max(1, rm))
    F["local_units"] = 1 + len(w.alen) + len(w.elen)
    F["ally_units"] = len(w.alen)
    F["enemy_units"] = len(w.elen)
    return F


DE_CACHE = {}
DE_EPOCH = [-1]


def degree(c):
    """Exits of c over static terrain: open or unknown edges and portals."""
    k = 0
    for n in w.dest(c):
        if n >= 0 or n == -2 or n == -3:
            k += 1
    return k


def dead_end(c, depth=4):
    """True if c lies in a 1-wide corridor that is closed within `depth` cells
    on at least one side (a dragon entering it cannot turn around)."""
    if DE_EPOCH[0] != w.EPOCH[0]:
        DE_CACHE.clear()
        DE_EPOCH[0] = w.EPOCH[0]
    v = DE_CACHE.get(c)
    if v is not None:
        return v
    d = degree(c)
    if d >= 3:
        v = False
    elif d <= 1:
        v = True
    else:
        v = False
        for n0 in w.dest(c):
            if n0 < 0:
                continue
            prev, cur = c, n0
            for _ in range(depth):
                dc = degree(cur)
                if dc <= 1:
                    v = True
                    break
                if dc >= 3:
                    break
                nxt = -1
                for n in w.dest(cur):
                    if n >= 0 and n != prev:
                        nxt = n
                        break
                if nxt < 0:
                    break
                prev, cur = cur, nxt
            if v:
                break
    DE_CACHE[c] = v
    return v
