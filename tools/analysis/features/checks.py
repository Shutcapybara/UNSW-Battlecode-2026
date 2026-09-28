"""V0 bookkeeping identities per game (F1 feature lab). Each returns (name, residual); residual 0 = pass."""
import math


def v0_checks(g, out):
    rows = []
    R = len(g['rounds']) - 1
    ev = g['events']
    for t in 'AB':
        start = sum(len(b) for i, (tt, b) in g['rounds'][0].items() if tt == t)
        end = sum(len(b) for i, (tt, b) in g['rounds'][R].items() if tt == t)
        eats = sum(1 for e in ev['eats'] if e['team'] == t)
        died_moving = {(d['round'], d['id']) for d in ev['deaths'] if d['actor'] == d['id']}
        sprint = sum(a.get('paid', 0) for a in ev['actions'] if a['team'] == t and a['kind'] == 'move')
        lost = sum(d['length'] for d in ev['deaths'] if d['team'] == t)
        bad = sum(1 for a in ev['actions'] if a['team'] == t and a['kind'] == 'move' and not (0 <= a.get('paid', 0) <= max(a['steps'] - 1, 0)))
        rows.append(dict(check='sprint_paid_within_bounds', side=t, residual=bad))
        rows.append(dict(check='length_conservation', side=t, residual=end - (start + eats - sprint - lost)))
        fin = g['final'][t]
        rows.append(dict(check='final_matches_result', side=t,
                         residual=abs(end - fin['total']) + abs(sum(1 for i, (tt, b) in g['rounds'][R].items() if tt == t) - fin['units'])))
        # dropped pearls: a death of length L drops ceil(L/2) pearls (fewer if cells blocked) -> report shortfall
        drop = sum(math.ceil(d['length'] / 2) for d in ev['deaths'] if d['team'] == t)
        spawned = sum(1 for s in ev['spawns'] if s['origin'] == t)
        rows.append(dict(check='corpse_drop_shortfall', side=t, residual=drop - spawned))
    for s in out['samples']:
        pass
    by_round = {}
    for s in out['samples']:
        by_round.setdefault(s['round'], 0.0)
        by_round[s['round']] += s['territory']
    rows.append(dict(check='territory_sums_to_one', side='-', residual=round(max((abs(v - 1) for v in by_round.values() if v == v), default=0), 9)))
    return [dict(r, game=g['id']) for r in rows]
