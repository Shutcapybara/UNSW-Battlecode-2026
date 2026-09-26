"""Contract I1 / candidate dependency C0. Cells y*width+x; age in rounds.

At most one resource, one scout, four visible attacks, one remote attack,
one feed, one production and one retreat candidate. No commands chosen here.
Only world geometry caches may be populated. Script memory is read-only.
"""
import world as w
import tactics as tx
import roles
import resource_values as resource
import topology
from params import P

KINDS = ('GATHER', 'SCOUT', 'ATTACK', 'RETREAT', 'FEED_ALLY', 'REPRODUCE')


def candidate(kind, target=-1, subject=-1, **params):
    return dict(kind=kind, target=target, subject=subject, params=params,
                candidate_id=kind + ':' + str(subject if subject >= 0 else target))


def build(script, terrain=None):
    # One shared route tree, with a hard insertion cap (unlike legacy cap+3).
    cap = P['big_cap'] if w.RND - w.BORN >= 2 else P['born_cap']
    dist = {w.HEAD: 0}; mask = {w.HEAD: 0}; q = [w.HEAD]; qi = 0
    own = {c: i for i, c in enumerate(w.body)}
    while qi < len(q) and len(q) < cap:
        c = q[qi]; qi += 1; t = dist[c] + 1
        for d, n in enumerate(w.step_opt(c)):
            if n < 0: continue
            m = mask[c] if c != w.HEAD else 1 << d
            if n in dist:
                if dist[n] == t: mask[n] |= m
                continue
            if n in own and t < own[n] + 2: continue
            if t < w.vac.get(n, 0): continue
            dist[n] = t; mask[n] = m; q.append(n)
            if len(q) >= cap: break
    ctx = dict(dist=dist, mask=mask, route_nodes=len(q),
               topology=terrain if terrain is not None else topology.build())
    out = []
    enemy = [c for c, _ in w.enemy_heads]
    best = {}; values = {}
    prev = script.get('candidate_id') if script.get('stalled', 0) < 6 else None
    for c, t in dist.items():
        if not t: continue
        kind = 'GATHER' if c in w.pearls or w.bed[c] == 2 else 'SCOUT'
        if kind == 'SCOUT' and w.seen[c]: continue
        v = resource.cell_value(c, t, w.ally_heads, enemy) * P['gamma'] ** t
        ident = kind + ':' + str(c)
        if ident == prev: v *= P['hyst']
        if v > values.get(kind, 0):
            values[kind] = v; best[kind] = c
    if 'GATHER' not in best:
        for c, rnd in w.pearls.items():
            if c == w.HEAD or w.RND - rnd > P['mem_ttl']: continue
            v = resource.cell_value(c, w.tdist(c, w.HEAD), w.ally_heads, enemy)
            v *= P['gamma'] ** (w.tdist(c, w.HEAD) + 2)
            if v > values.get('GATHER', 0): values['GATHER'] = v; best['GATHER'] = c
    for kind in ('GATHER', 'SCOUT'):
        if kind in best: out.append(candidate(kind, best[kind], value=values[kind]))
    if 'SCOUT' not in best:
        c = w.sector_target()
        if c >= 0 and c != w.HEAD: out.append(candidate('SCOUT', c, value=0.25))
    out.extend(exploration(ctx, script))
    if P['attack'] and w.UNITS >= P['atk_units'] and roles.ROLE[0] == 'forager':
        heads = sorted(w.enemy_heads, key=lambda x: (w.tdist(w.HEAD, x[0]), x[1]))[:4]
        for c, eid in heads:
            out.append(candidate('ATTACK', c, eid, trade='favourable', length=w.elen[eid],
                                 observed=w.RND, visible=True))
        pr = w.prey
        if pr and w.RND >= P['hunt_from'] and w.LEN <= P['hunt_max_len'] \
                and w.RND - pr[3] <= P['prey_ttl'] and pr[0] not in [i for _, i in heads]:
            out.append(candidate('ATTACK', pr[1], pr[0], trade='favourable', length=pr[2],
                                 observed=pr[3], visible=False))
    if roles.ROLE[0] == 'feeder' and roles.fresh():
        out.append(candidate('FEED_ALLY', w.crown[1], w.crown[0], trade='donate',
                             observed=w.crown[3]))
    if roles.ROLE[0] == 'forager' and w.LEN >= P['split_min'] \
            and w.LEN - P['child'] >= 2 and w.UNITS < w.LIMIT \
            and w.RND < min(P['split_stop'], P['grow_from']) and len(w.body) == w.LEN:
        out.append(candidate('REPRODUCE', w.body[0], child=P['child']))
    # Always available: escape confined states even when there is no enemy.
    out.append(candidate('RETREAT', emergency_split=True))
    return out, ctx


def exploration(ctx, script):
    """At most one information waypoint and one nominated portal edge.

    The policy receives objective parameters, never a compass direction. Probe
    uncertainty is explicit; the executor alone resolves an edge to a move.
    Six coverage samples and at most 85*4 known-edge probes bound work.
    """
    if roles.ROLE[0] != 'forager': return []
    out = []; terrain = ctx['topology']; routes = ctx['dist']
    fringe = [c for c, t in routes.items() if 2 <= t <= 8 and not w.visits[c]]
    best = None
    if fringe:
        stride = max(1, len(fringe)//6)
        for cell in fringe[::stride][:6]:
            gain = topology.information(cell)
            value = gain * P['gamma'] ** routes[cell]
            if best is None or value > best[0]: best = (value, cell, gain)
    if best and best[2] >= 7:
        c = candidate('SCOUT', best[1], mode='information', information=best[2], value=best[0]/7)
        c['candidate_id'] = 'SCOUT:information:'+str(best[1]); out.append(c)
    best = None
    for cell, destinations in terrain['edges'].items():
        steps = routes.get(cell)
        if steps is None or steps > 8: continue
        for direction, nxt in enumerate(destinations):
            if nxt != -3: continue
            edge = w.ekey(cell, direction)
            ident = 'SCOUT:portal:'+str(edge)
            if script.get('candidate_id') == ident and script.get('stalled', 0) >= 6: continue
            value = steps - (1 if script.get('candidate_id') == ident else 0)
            if best is None or value < best[0]: best = (value, cell, edge)
    if best is not None:
        _, cell, edge = best
        c = candidate('SCOUT', cell, w.epid[edge], mode='portal', portal_edge=edge,
                      max_length=5, observed=w.RND, value=P['v_dive'])
        c['candidate_id'] = 'SCOUT:portal:'+str(edge); out.append(c)
    return out
