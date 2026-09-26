"""F0/F1: scoring facts only; never consumed by execution or enumeration.

distance: route steps (torus+2 when outside the tree); age: rounds;
gain: relative length segments; exposure: inherited expected material loss;
resource_value: inherited discounted utility. F1 discounts stale target evidence.
"""
import world as w
import mechanics as m


def build(c, ctx, threat):
    p = c['params']; target = c['target']
    distance = ctx['dist'].get(target, w.tdist(w.HEAD, target) + 2) if target >= 0 else 0
    return dict(distance=distance, age=w.RND - p.get('observed', w.RND),
                gain=p.get('length', w.LEN) - w.LEN,
                exposure=m.threat_cost(w.HEAD, w.LEN, threat),
                resource_value=p.get('value', 0),
                target_age=w.RND - w.pearls.get(target, w.RND),
                units=w.UNITS)
