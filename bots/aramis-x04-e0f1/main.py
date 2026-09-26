"""Aramis: state -> intentions -> features -> decision -> execute -> commit/I/O."""
import protocol as io
import world as w
import tactics as tx
import roles
import radio
import comms
import intentions
import execution as ex
import features
import policy
import settings
from params import P


def initialize_state():
    w.init(); ex.initialize()
    w.T_HIDDEN[0] = P['t_hidden']; w.PREY_MIN[0] = P['prey_min']; w.PREY_TTL[0] = P['prey_ttl']


def turn():
    mine = w.sense(); w.track_body(mine); w.prune()
    radio.hear(io.observation['messages']); roles.update()
    threat = tx.threat_map(); tx.set_head_near()
    candidates, ctx = intentions.build(ex.SCRIPT)
    ctx['threat'] = threat
    facts = [features.build(c, ctx, threat) for c in candidates]
    audit = None
    if settings.TRACE and w.RND % 25 == 0:
        import diagnostics
        audit = diagnostics.invariance(candidates, ctx, facts)
    attempts = []; selected = None; r = None
    # Unavailable proposals commit nothing. Geometry previews are reused.
    for c, f in policy.rank(candidates, facts, settings.FEATURE_VERSION):
        proposal = ex.execute(c, ctx, settings.EXECUTOR_VERSION)
        attempts.append((c['candidate_id'], proposal['status'], proposal['reason']))
        if proposal['command'] is not None:
            selected = c; r = proposal; break
    if r is None: r = ex.fallback(ctx, 'all_intentions_unavailable')
    previous = dict(ex.SCRIPT) if settings.TRACE else None
    kind, arg = r['command']
    io.reply.update(command=io.Command.SPLIT if kind=='split' else io.Command.MOVE,
                    argument=str(arg) if kind=='split' else ''.join(w.DIRS[d] for d in arg))
    messages = radio.outgoing()
    for request, n in r['reports']:
        if request == 'crown_handoff': messages[w.DIRS[(w.FACE+2)%4]] = comms.handoff_packet(n, w.RND)
    io.reply['sonar'] = messages
    if settings.TRACE:
        import json
        import sys
        sys.stdout.write('LOG ARAMIS '+json.dumps(dict(id=w.ME, round=w.RND, length=w.LEN,
            role=roles.ROLE[0], head=w.HEAD, selected=selected, execution=r,
            previous=previous, attempts=attempts, invariance=audit), separators=(',', ':'))+'\n')
    ex.commit(r)


def main():
    if not io.read_init(): return
    initialize_state()
    while io.read_turn():
        io.reply.clear()
        io.reply.update(command=io.Command.MOVE, argument=io.observation['direction'], sonar={})
        try: turn()
        except Exception as exc:
            import sys
            sys.stdout.write('LOG MC_ERROR ARAMIS '+type(exc).__name__+'\n')
            for d in range(4):
                if tx.sim([d], w.body)[0]=='ok':
                    io.reply.update(command=io.Command.MOVE, argument=w.DIRS[d], sonar={}); break
        io.write_reply()


if __name__ == '__main__': main()
