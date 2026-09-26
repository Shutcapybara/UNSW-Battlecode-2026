"""Valjean: observation -> state -> features -> candidates -> previews ->
decision -> execution -> commit/messages -> output.

Layer ownership (docs/valjean.md):
  world/roles/radio/mass/topology  state (once per turn, before candidates)
  candidates                       objective instances (no commands)
  executors                        commands + predictions; pure w.r.t. memory
  policy                           Q = objective value + executor value
  main.commit                      the ONLY writer of script/trail/target memory
"""
import protocol as io
import world as w
import tactics as tx
import roles
import radio
import comms
import mass
import topology
import candidates as cand
import executors as ex
import policy
from params import P

SCRIPT = {}


def initialize_state():
    w.init()
    w.T_HIDDEN[0] = P["t_hidden"]
    w.PREY_MIN[0] = P["prey_min"]
    w.PREY_TTL[0] = P["prey_ttl"]
    w.VAC_EAT[0] = P["vac_eat"]
    mass.init()
    SCRIPT.clear()  # a child starts with empty script memory (fresh process)


def crown_flank():
    out = set()
    if roles.ROLE[0] == "feeder" and w.crown is not None:
        cid = w.crown[0]
        for c, o in w.occ.items():
            if o[1] and (o[0] & 4095) == cid:
                for n in w.dest(c):
                    if n >= 0:
                        out.add(n)
    return out


def turn():
    msgs = io.observation["messages"]
    mine = w.sense()
    w.track_body(mine)
    w.prune()
    radio.hear(msgs)
    roles.update()
    topology.update()
    mass.observe()
    if roles.ROLE[0] == "crown" and P["crown_cut_full"]:
        threat = tx.threat_map(P["reach_cap_crown"], True)  # Sinbad v06 crown reach
    else:
        threat = tx.threat_map()
    tx.set_head_near()
    cands, ctx = cand.build(SCRIPT)
    ctx["threat"] = threat
    ctx["crown_flank"] = crown_flank()
    results = [None if policy.is_escape(c) else ex.execute(c, ctx) for c in cands]
    if policy.best_other(cands, results, ctx) < policy.escape_gate():
        results = [ex.execute(c, ctx) if r is None else r for c, r in zip(cands, results)]
    chosen, r = policy.choose(cands, results, ctx)
    if r is None:
        chosen, r = None, ex.fallback(ctx, "no_executable_objective")
    kind, arg = r["command"]
    if kind == "split":
        io.reply.update(command=io.Command.SPLIT, argument=str(arg))
    else:
        io.reply.update(command=io.Command.MOVE, argument="".join(w.DIRS[d] for d in arg))
    messages = radio.outgoing()
    if kind == "split" and roles.ROLE[0] == "crown" and arg > w.LEN - arg:
        messages[w.DIRS[(w.FACE + 2) % 4]] = comms.handoff_packet(arg, w.RND)
    io.reply["sonar"] = messages
    if P["trace"]:
        trace(cands, results, chosen, r, ctx)
    commit(chosen, r, cands[0])


def commit(chosen, r, econ):
    # the economy search's hysteresis memory follows its own nominee every turn
    cand.MEM["target"] = econ["target"]
    w.trail.extend(r["path_cells"])
    SCRIPT.clear()
    if chosen is not None:
        SCRIPT.update(candidate_id=chosen["candidate_id"], kind=chosen["kind"],
                      target=chosen["target"], round=w.RND, outcome=r["outcome"])


def trace(cands, results, chosen, r, ctx):
    import json
    import sys
    rec = dict(id=w.ME, rnd=w.RND, len=w.LEN, units=w.UNITS, role=roles.ROLE[0],
               sel=chosen["candidate_id"] if chosen else None, out=r["outcome"],
               q=round(r.get("q", 0) or 0, 2),
               opts=[(c["candidate_id"], round(x["q"], 2)) for c, x in zip(cands, results)
                     if x is not None and x.get("q") is not None],
               room=topology.F.get("room"), crowd=round(topology.F.get("crowd", 0), 2),
               em=round(mass.F.get("e_mass", 0), 1), am=round(mass.F.get("a_mass", 0), 1),
               src=mass.F.get("sources"))
    sys.stdout.write("LOG VJ " + json.dumps(rec, separators=(",", ":")) + "\n")


def main():
    if not io.read_init():
        return
    initialize_state()
    while io.read_turn():
        io.reply.clear()
        io.reply.update(command=io.Command.MOVE, argument=io.observation["direction"], sonar={})
        try:
            turn()
        except Exception as exc:
            import sys
            sys.stdout.write("LOG VJ_ERROR " + type(exc).__name__ + " " + str(exc)[:80] + "\n")
            io.reply["sonar"] = {}
            for d in range(4):
                if tx.sim([d], w.body)[0] == "ok":
                    io.reply.update(command=io.Command.MOVE, argument=w.DIRS[d])
                    break
        io.write_reply()


if __name__ == "__main__":
    main()
