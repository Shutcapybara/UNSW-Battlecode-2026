"""SCOUT/portal implementation; objective identity is an edge, not a heading.

E0 offers the probe to the inherited local movement ranker. E1 performs the
requested one-step probe once at its entry, under explicit length/time/role
limits. Both return unknown outcome, never a predicted safe landing. Approach
and terminal execution remain distinguishable in the result record.
"""
import world as w
import roles


def direction(c):
    edge = c['params']['portal_edge']
    if c['target'] != w.HEAD: return None
    return next((d for d in range(4) if w.ekey(w.HEAD, d) == edge), None)


def permitted(c):
    return roles.ROLE[0] == 'forager' and w.LEN <= c['params']['max_length'] \
        and w.UNITS >= 3 and w.RND < 440


def execute(c, ctx, version, executor):
    edge = c['params']['portal_edge']
    if not 0 <= edge < 2*w.NC or w.ek[edge] != 3 or w.epid.get(edge) != c['subject']:
        return executor.result(c, ctx, reason='portal_evidence_expired')
    if len(w.pends.get(c['subject'], ())) == 2:
        return executor.result(c, ctx, reason='portal_already_mapped')
    if not permitted(c): return executor.result(c, ctx, reason='probe_permission')
    d = direction(c)
    if d is not None and version == 1:
        row = next((r for r in executor.movement(ctx) if r['path'] == [d] and r['state'] == 'dive'), None)
        if row is None: return executor.result(c, ctx, reason='portal_revalidation_failed')
        return executor.result(c, ctx, ('move', [d]), 'unknown_portal', 'active', 'probe_connection', row)
    result = executor.route(c, ctx)
    if result['command'] is not None and result['outcome'] != 'unknown_portal':
        result['status'] = result['updates']['status'] = 'active'
        result['reason'] = 'approach_portal'
    return result
