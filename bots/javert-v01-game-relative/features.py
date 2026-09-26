"""F0/F1/F2: scoring facts only; never consumed by execution or enumeration.

distance: route steps (torus+2 when outside the tree); age: rounds;
gain: relative length segments; exposure: inherited expected material loss;
resource_value: inherited discounted utility. F1 discounts stale target evidence.

Javert F2 (settings.POLICY3) adds game-relative strategic facts, computed at
most once per turn and cached in ctx (never in retained state):
  openness      reachable room around the current head / room needed (0..1);
               a bounded state query using the same flood constants as movement
  phase_early   round < space_phase_end (game time changes the strategy)
  saturated     living units >= unit limit (population pressure)
  len_balance   (enemy - ally) visible length at the head over (sum + 1),
               from the D2 length field when available; 0.0 with no evidence
"""
import world as w
import tactics as tx
import mechanics as m
import settings
import density
from params import P


def _openness(ctx):
    """Bounded room ratio around the current body; flood scratch is restored."""
    o = ctx.get('openness')
    if o is None:
        need = max(w.LEN + P['slack'], P['min_area'])
        if w.LEN >= 10:
            need = min(need + w.LEN // 3, P['flood_cap_long'])
        else:
            need = min(need, P['flood_cap'])
        pocket, blind = tx.POCKET[0], tx.BLIND[0]
        try:
            area = tx.flood(w.body, need, 0)
        finally:
            tx.POCKET[0], tx.BLIND[0] = pocket, blind
        o = min(1.0, area / float(need))
        ctx['openness'] = o
    return o


def strategic(ctx):
    """F2 facts shared by every candidate this turn; never committed."""
    facts = dict(openness=_openness(ctx),
                 phase_early=float(w.RND < P['space_phase_end']),
                 saturated=float(w.UNITS >= w.LIMIT),
                 len_balance=0.0, len_confidence=0.0)
    if settings.LEN_DENSITY and density.ACTIVE_LEN:
        al, el, conf = density.field_len(w.HEAD)
        facts['len_balance'] = (el - al) / (al + el + 1.0)
        facts['len_confidence'] = conf
    return facts


def build(c, ctx, threat):
    p = c['params']; target = c['target']
    distance = ctx['dist'].get(target, w.tdist(w.HEAD, target) + 2) if target >= 0 else 0
    f = dict(distance=distance, age=w.RND - p.get('observed', w.RND),
             gain=p.get('length', w.LEN) - w.LEN,
             exposure=m.threat_cost(w.HEAD, w.LEN, threat),
             resource_value=p.get('value', 0),
             target_age=w.RND - w.pearls.get(target, w.RND),
             units=w.UNITS)
    if settings.POLICY3:
        s = ctx.get('strategic')
        if s is None:
            s = ctx['strategic'] = strategic(ctx)
        f.update(s)
    return f
