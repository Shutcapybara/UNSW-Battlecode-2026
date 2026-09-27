"""Fermi support experiments. Uses only visible heads, bodies and known edges."""
import world as w
from params import P

COUNTS = {}


def reset():
    # A dragon can act more than once in a round; reset at each decision.
    COUNTS.clear()


def support_count(ec, el, mode):
    key = (ec, el, mode)
    if key in COUNTS:
        return COUNTS[key]
    n = 0
    for hc, hid in w.ally_heads:
        length = w.alen.get(hid, 1)
        if length < el:
            continue
        if mode == 1:
            reachable = w.tdist(hc, ec) <= P['support_rad']
        else:
            # A bounded current-board strike route, not geometric proximity.
            # Do not infer free unknown exits or assume bodies vacate in time.
            cap = min(P['support_rad'], max(0, length - 1))
            seen = {hc}
            queue = [(hc, 0)]
            reachable = False
            for c, depth in queue:
                if depth >= cap:
                    continue
                for dest in w.dest(c):
                    if dest < 0 or dest in seen:
                        continue
                    if dest == ec:
                        reachable = True
                        break
                    if dest in w.occ or dest in w.body:
                        continue
                    seen.add(dest)
                    queue.append((dest, depth + 1))
                if reachable:
                    break
        n += reachable
    COUNTS[key] = n
    return n


def threat_cost(h, newlen, threat, value):
    ts = threat.get(h)
    if not ts:
        return 0.0
    mine = value(newlen)
    cost = 0.0
    active = P['threat_ally'] > 0 and (P['threat_ally_all'] or
        (P['compact_nc'] > 0 and w.NC <= P['compact_nc'] and w.UNITS < P['unit_target']))
    for steps, eid, el, ec in ts:
        p = P['p_long'] if newlen > el else P['p_eq'] if newlen == el else P['p_short']
        if steps > 1:
            p *= P['p_sprint']
        c = p * max(P['threat_base'], mine - P['k_their'] * value(el))
        if active:
            n = support_count(ec, el, P['fermi_support'])
            c *= max(0.25, (1.0 - P['threat_ally']) ** n)
        cost = max(cost, c)
    return P['w_threat'] * cost
