"""E0/E1 intention executors. Never reads policy features or policy settings.

One shared mechanical movement preview per turn; at most 52 simulated paths,
each flood bounded by 40 credited cells. Only commit() changes SCRIPT/trail.
Results separate status, fallback and predicted outcome. Survival is conditional
on known occupancy, not a guarantee against future enemy actions/hidden exits.
"""
import world as w
import tactics as tx
import mechanics as m
import roles
from params import P

SCRIPT = {}


def initialize():
    SCRIPT.clear()  # also the explicit fresh-child initialization contract


def need_area():
    need = max(w.LEN + P['slack'], P['min_area'])
    return min(need + w.LEN // 3, P['flood_cap_long']) if w.LEN >= 10 else min(need, P['flood_cap'])


def movement(ctx):
    if 'moves' in ctx: return ctx['moves']
    threat = ctx['threat']; need = need_area(); rows = []
    for path in m.candidates(w.body):
        st, nb, eaten, hit = tx.sim(path, w.body)
        blind = tx.BLIND[0]; area = 0; risk = 0.0
        score = -1000.0 - len(path)
        if st == 'ok':
            h = nb[-1]
            score = m.lv_now() * (len(nb) - w.LEN) - P['w_sprint'] * (len(path) - 1)
            score += 0.5 * eaten
            if blind: score -= P['p_blind'] * m.dragon_value(len(nb))
            area = tx.flood(nb, need, 0)
            if area < need:
                pen = P['w_trap'] * (need - area) / need
                if area < len(nb): pen += P['w_trap']
                k = tx.POCKET[0]
                if len(nb) + k >= P['split_min'] and len(nb) + k > area + 1 and w.UNITS < w.LIMIT:
                    pen *= P['farm_factor']
                pen *= max(1.0, m.dragon_value(len(nb)) / P['v_ref'])
                score -= pen
            risk = m.threat_cost(h, len(nb), threat)
            score -= risk
            for hc, hid in w.ally_heads:
                dd = w.tdist(hc, h)
                if dd <= 2: score -= P['w_crowd'] * (3 - dd)
            score -= P['w_visit'] * w.visits[h]
            if w.bed[h] == 2 and w.spawn.get(h, -9) == w.RND + 1: score -= P['w_bed_block']
        rows.append(dict(path=path, state=st, body=nb, eaten=eaten, hit=hit,
                         score=score, area=area, exposure=risk, blind=blind))
    ctx['moves'] = rows
    return rows


def progress(target, ctx):
    if target < 0 or target == w.HEAD: return [0] * 4
    mask = ctx['mask'].get(target)
    if mask is None:
        cells = [(3 * w.tdist(c, target) + t, c) for c, t in ctx['dist'].items() if t]
        if not cells: return [0] * 4
        # Stable route-discovery tie breaking, inherited from Monte Christo.
        waypoint = min(cells, key=lambda pair: pair[0])[1]
        mask = ctx['mask'][waypoint]
    return [1 if (mask >> d) & 1 else -1 for d in range(4)]


def result(c, ctx, command=None, outcome='none', status='unavailable', reason='', row=None):
    target = c['target']; end = row['body'][-1] if row and row['state'] == 'ok' else w.HEAD
    delta = w.tdist(w.HEAD, target) - w.tdist(end, target) if target >= 0 else 0
    same = SCRIPT.get('candidate_id') == c['candidate_id']
    updates = dict(candidate_id=c['candidate_id'], kind=c['kind'], target=target,
                   started=SCRIPT.get('started', w.RND) if same else w.RND,
                   stalled=(SCRIPT.get('stalled', 0) + 1 if same else 1) if delta <= 0 else 0,
                   round=w.RND, status=status, outcome=outcome,
                   expected_length=len(row['body']) if row and row['state'] == 'ok' else None)
    reports = []
    if command and command[0] == 'split' and roles.ROLE[0] == 'crown' and command[1] > w.LEN-command[1]:
        reports.append(('crown_handoff', command[1]))
    return dict(command=command, outcome=outcome, status=status, reason=reason,
                fallback=False, progress=delta, cost=dict(route_nodes=ctx.get('route_nodes', 0),
                move_previews=len(ctx.get('moves', ()))), updates=updates, reports=reports,
                interrupted=SCRIPT.get('candidate_id') if SCRIPT and not same else None,
                path_cells=row['body'][-len(row['path']):-1] if row and row['state']=='ok' and len(row['path'])>1 else [],
                area=row['area'] if row else None, exposure=row['exposure'] if row else None)


def route(c, ctx):
    kind = c['kind']; prog = progress(c['target'], ctx); options = []
    flank = set()
    if kind == 'FEED_ALLY':
        for cell, occ in w.occ.items():
            if occ[1] and (occ[0] & 4095) == c['subject']:
                flank.update(n for n in w.dest(cell) if n >= 0)
    for row in movement(ctx):
        st = row['state']; path = row['path']; value = row['score']
        if st == 'ok':
            if kind != 'RETREAT': value += P['w_goal'] * prog[path[0]] * (1 if len(path)==1 else 0.7)
            if kind == 'RETREAT': value -= row['exposure']  # escape explicitly values reduced exposure
            if row['body'][-1] in flank: value -= P['w_flank']
            options.append((value, row, 'predicted_survive'))
        elif st == 'h2h' and kind == 'ATTACK' and row['hit'] == c['subject'] \
                and c['params'].get('trade') == 'favourable':
            value = m.strike_value(row['hit'], len(path))
            if value is not None: options.append((value, row, 'intentional_head_trade'))
        elif st == 'dive' and kind == 'SCOUT' and c['params'].get('dive') == path[0]:
            options.append((P['dive_base']-P['p_dive']*m.dragon_value(w.LEN)+P['v_dive']*.5,
                            row, 'unknown_portal'))
    if not options: return result(c, ctx, reason='no_permitted_movement')
    _, row, outcome = max(options, key=lambda x:x[0])
    done = outcome == 'intentional_head_trade' or (row['state']=='ok' and row['body'][-1]==c['target'])
    return result(c, ctx, ('move', row['path']), outcome, 'completed' if done else 'active',
                  'contact' if outcome=='intentional_head_trade' else 'route', row)


def reproduce(c, ctx, version):
    n = c['params']['child']
    if n != P['child']: return result(c, ctx, reason='unsupported_split_point')
    proposal = m.split_option(w.body, ctx['threat'], need_area())
    if proposal is None: return result(c, ctx, reason='split_geometry_or_room')
    all_body = set(w.body)
    child_exits = [x for x in w.dest(w.body[0]) if x >= 0 and x not in all_body and x not in w.occ]
    parent_exits = [x for x in w.dest(w.HEAD) if x >= 0 and x not in all_body and x not in w.occ]
    if not child_exits or not parent_exits: return result(c, ctx, reason='blocked_split_continuation')
    # E1 changes REPRODUCE only: a child needs an exit outside known enemy reach.
    if version == 1 and not any(x not in ctx['threat'] for x in child_exits):
        return result(c, ctx, reason='child_exits_exposed')
    return result(c, ctx, proposal[1], 'predicted_split_survive', 'completed', 'viable_child')


def feed(c, ctx):
    if c['params'].get('trade') != 'donate' or not roles.fresh() or w.crown[0] != c['subject']:
        return result(c, ctx, reason='ally_expired')
    ch = roles.crown_visible()
    if ch >= 0 and w.tdist(ch, w.HEAD) <= P['feed_dist']:
        for d in [(w.FACE+2)%4, 0, 1, 2, 3]:
            if tx.sim([d], w.body)[0] == 'dead':
                # Every other segment, starting at head, becomes a pearl.
                r = result(c, ctx, ('move', [d]), 'intentional_donation', 'completed', 'crown_nearby')
                r['donation_cells'] = w.body[::-2]
                return r
    return route(c, ctx)


def execute(c, ctx, version=0):
    """Pure proposal wrt observation/world facts/script. ctx is a turn-local cache."""
    blind, pocket = tx.BLIND[0], tx.POCKET[0]
    try:
        kind = c['kind']
        if kind in ('GATHER', 'SCOUT', 'ATTACK', 'FEED_ALLY') and \
                SCRIPT.get('candidate_id') == c['candidate_id'] and SCRIPT.get('stalled', 0) >= 6:
            return result(c, ctx, reason='stalled_six_turns')
        if kind == 'REPRODUCE': return reproduce(c, ctx, version)
        if kind == 'FEED_ALLY': return feed(c, ctx)
        if kind == 'ATTACK':
            if w.RND - c['params']['observed'] > P['prey_ttl']:
                return result(c, ctx, reason='enemy_expired')
            if c['params']['visible'] and not any(eid==c['subject'] for _, eid in w.enemy_heads):
                return result(c, ctx, reason='enemy_gone')
        if kind == 'GATHER' and c['target'] not in w.pearls and w.bed[c['target']] != 2:
            return result(c, ctx, reason='resource_gone')
        if kind == 'RETREAT':
            rows = movement(ctx)
            if not any(r['state']=='ok' for r in rows) and c['params'].get('emergency_split'):
                command = m.escape_split(w.body)
                if command: return result(c, ctx, command, 'child_escape_parent_at_risk', 'active', 'emergency_split')
        return route(c, ctx)
    finally:
        tx.BLIND[0], tx.POCKET[0] = blind, pocket


def fallback(ctx, reason):
    from intentions import candidate
    c = candidate('RETREAT', emergency_split=True)
    r = execute(c, ctx)
    r['fallback'] = True
    r['status'] = 'interrupted'
    r['updates']['status'] = 'interrupted'
    r['reason'] = reason + ':' + r['reason']
    if r['command'] is None:
        # No WAIT exists. This is syntactically valid, explicitly not called safe.
        r = result(c, ctx, ('move', [w.FACE]), 'predicted_death', 'interrupted', 'no_predicted_surviving_move')
        r['fallback'] = True
    return r


def commit(r):
    if r['command'] is None: raise ValueError('Cannot commit unavailable execution')
    SCRIPT.clear(); SCRIPT.update(r['updates'])
    w.trail.extend(r['path_cells'])
