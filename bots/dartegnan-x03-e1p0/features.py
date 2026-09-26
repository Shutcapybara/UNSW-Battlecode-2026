"""F0/F1: scoring facts only; never consumed by execution or enumeration.

distance: route steps (torus+2 when outside the tree); age: rounds;
gain: relative length segments; exposure: inherited expected material loss;
resource_value: inherited discounted utility. F1 discounts stale target evidence.
"""
import world as w
import mechanics as m
import topology
import field_reports
import roles


def build(c, ctx, threat):
    p = c['params']; target = c['target']
    distance = ctx['dist'].get(target, w.tdist(w.HEAD, target) + 2) if target >= 0 else 0
    facts = dict(distance=distance, age=w.RND - p.get('observed', w.RND),
                gain=p.get('length', w.LEN) - w.LEN,
                exposure=m.threat_cost(w.HEAD, w.LEN, threat),
                resource_value=p.get('value', 0),
                target_age=w.RND - w.pearls.get(target, w.RND),
                units=w.UNITS)
    terrain = ctx['topology']
    facts.update(topology.objective_facts(target, ctx))
    remote, confidence = field_reports.evidence(target, terrain)
    facts.update(round=w.RND, remaining=500-w.RND, phase=w.RND/500.0,
                 population_fraction=w.UNITS/max(1, w.LIMIT), length=w.LEN,
                 role=roles.ROLE[0], known_area=terrain['area'], free_cells=terrain['free'],
                 closed=terrain['closed'], area_censored=terrain['censored'],
                 free_exits=terrain['exits'],
                 congestion=(terrain['allied']+terrain['enemy'])/max(1, len(terrain['visible'])),
                 visible_area=len(terrain['visible']),
                 remote_balance=remote, remote_confidence=confidence,
                 information=p.get('information', 0),
                 portal_unknown=p.get('mode') == 'portal')
    return facts
