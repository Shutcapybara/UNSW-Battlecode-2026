"""Turn-local terrain evidence. Unknown edges are boundaries, never free room.

Known portals participate in this directed graph; unpaired portals are recorded
as opportunities. The radius-four area is a lower bound when the search hits
unknown terrain. Bodies count as occupancy, not permanent walls. No hidden map
or team/spawn heading enters the graph. Work: <=85 nodes, <=4 edges per node.
"""
import world as w

RADIUS = 6
CAP = 85


def build():
    dist = {w.HEAD: 0}; masks = {w.HEAD: 0}; queue = [w.HEAD]
    edges = {}; unknown = set(); portals = set(); clipped = False
    for cell in queue:
        depth = dist[cell]
        destinations = w.dest(cell)
        edges[cell] = destinations
        for direction, nxt in enumerate(destinations):
            if nxt == -2: unknown.add(cell)
            if nxt == -3: portals.add(w.ekey(cell, direction))
            if nxt < 0 or depth >= RADIUS: continue
            mask = masks[cell] if cell != w.HEAD else 1 << direction
            if nxt in dist:
                if dist[nxt] == depth + 1: masks[nxt] |= mask
                continue
            if len(queue) >= CAP:
                clipped = True
                continue
            dist[nxt] = depth + 1; masks[nxt] = mask; queue.append(nxt)
    local = {cell for cell in queue if dist[cell] <= 4}
    visible = {cell for cell in local if w.seen[cell] == w.RND + 1}
    own = set(w.body)
    # Aggregate exact integer masses once by shortest first-route mask. Each
    # objective then sums at most sixteen groups instead of rescanning every
    # visible cell and rebuilding the potentially long own-body set.
    groups = {}
    for cell in visible:
        key = -1 if cell == w.HEAD else masks[cell]
        row = groups.setdefault(key, [0, 0, 0])
        row[0] += 1
        if cell in own or (cell in w.occ and w.occ[cell][1]): row[1] += 1
        elif cell in w.occ: row[2] += 1
    allied = sum(cell in own or (cell in w.occ and w.occ[cell][1]) for cell in visible)
    enemy = sum(cell in w.occ and not w.occ[cell][1] for cell in visible)
    free = sum(cell not in own and cell not in w.occ for cell in local)
    exits = sum(n >= 0 and n not in own and n not in w.occ for n in w.dest(w.HEAD))
    # A complete component requires neither a depth/cap boundary nor unknown edges.
    closed = not clipped and not unknown and not portals and max(dist.values()) < RADIUS
    return dict(dist=dist, masks=masks, edges=edges, unknown=unknown, portals=portals,
                local=local, visible=visible, area=len(local), free=free,
                allied=allied, enemy=enemy, exits=exits, closed=closed,
                censored=clipped or bool(unknown or portals), nodes=len(queue),
                mass_groups=groups, mass_cache={})


def footprint(origin, topo, radius=2):
    """Known directed route neighbourhood, at most 13 cells for radius two.

    Only currently observed cells contribute mass and denominator. A portal can
    change the footprint's shape without making its unseen exit observed.
    """
    dist = {origin: 0}; queue = [origin]
    for cell in queue:
        if dist[cell] >= radius: continue
        for nxt in topo['edges'].get(cell, ()):
            if nxt >= 0 and nxt not in dist and len(queue) < 13:
                dist[nxt] = dist[cell] + 1; queue.append(nxt)
    return [cell for cell in queue if w.seen[cell] == w.RND + 1]


def information(cell):
    """New observation cells at a nominated destination (0..49), not reward."""
    x, y = cell % w.W, cell // w.W
    if w.W < 7 or w.H < 7:
        cells = {((y+dy)%w.H)*w.W+(x+dx)%w.W for dy in range(-3,4) for dx in range(-3,4)}
        return sum(not w.seen[c] for c in cells)
    return sum(not w.seen[((y + dy) % w.H) * w.W + (x + dx) % w.W]
               for dy in range(-3, 4) for dx in range(-3, 4))


def objective_facts(target, ctx):
    topo = ctx['topology']; mask = topo['masks'].get(target, 0)
    cached = topo['mass_cache'].get(mask)
    if cached is not None: return cached
    ally = enemy = 0.0; area = 0
    for branch, (cells, aa, ee) in topo['mass_groups'].items():
        if mask and not branch & mask: continue
        area += cells; ally += aa; enemy += ee
    result = dict(toward_ally_segments=ally, toward_enemy_segments=enemy,
                  toward_area=area, direction_known=bool(mask))
    topo['mass_cache'][mask] = result
    return result
