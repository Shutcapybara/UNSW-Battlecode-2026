"""Native-only paired proposal audit, run on identical observed inputs.

Instrumentation lives outside the deployed dependency closure. It exercises both
feature versions without committing any proposal and checks retained-state purity.
"""
def invariance(candidates, ctx, facts):
    import copy
    import hashlib
    import json
    import protocol as io
    import world as w
    import roles
    import execution as ex
    import policy
    import settings
    import field_reports
    def retained():
        return (ex.SCRIPT,w.body,w.trail,w.pearls,w.occ,w.vac,w.crown,w.prey,
                roles.ROLE,roles.LAST,roles.INHERIT,io.observation,field_reports.REPORTS,
                field_reports.LOCAL,field_reports.PACKET)
    before=copy.deepcopy(retained())
    proposals0=[ex.execute(c,ctx,settings.EXECUTOR_VERSION) for c in candidates]
    policy.rank_previews(candidates,facts,proposals0,1,w.RND,0)
    policy.rank_previews(candidates,facts,proposals0,1,w.RND,1)
    proposals1=[ex.execute(c,ctx,settings.EXECUTOR_VERSION) for c in candidates]
    if before != retained() or proposals0 != proposals1:
        raise AssertionError('Unchosen execution mutated state or features changed proposal')
    encoded=json.dumps(io.observation,sort_keys=True,separators=(',',':')).encode()
    return dict(proposals=len(proposals0), input_sha256=hashlib.sha256(encoded).hexdigest(),
                unchanged=True, retained_state_unchanged=True)
