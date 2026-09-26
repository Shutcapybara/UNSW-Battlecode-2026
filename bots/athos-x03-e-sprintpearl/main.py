"""Athos: staged intention pipeline over the monte_christo-v01-core policy.

Six stages per turn (next-generation handoff contract):
  1 state       observation + decoded reports -> world/roles state (once)
  2 features    candidate-independent features (threat map, head reach)
  3 candidates  availability-gated candidate records from the executors
  4 decision    per-candidate previews + scoring; nomination of one action
  5 execution   the nominated executor serializes its concrete command
  6 commit      message construction/encoding and the protocol reply;
                only the selected execution's script changes (trail cells)

world owns perception memory; roles owns crown election; executors.MEM owns
target hysteresis (planner script state).  Previews never change the
simulated body or the protocol observation; only stage_commit mutates
persistent execution state.  This release is the behaviour-preserving
extraction of monte_christo-v01-core onto this contract: identical streams
by construction, verified by source-matched replay comparison (docs/athos.md).
"""
import sys
import protocol as io
import world as w
import tactics as tx
import executors as ex
import decision as dec
import roles
import radio
import comms
from params import P

work = {}


def initialize_state():
    w.init()
    w.T_HIDDEN[0] = P["t_hidden"]
    w.PREY_MIN[0] = P["prey_min"]
    w.PREY_TTL[0] = P["prey_ttl"]
    dec.DBG = None


def stage_state():
    # Consumes the observation and decoded reports exactly once.
    mine = w.sense()
    w.track_body(mine)
    w.prune()
    radio.hear(io.observation["messages"])
    roles.update()


def stage_features():
    work["threat"] = tx.threat_map()
    tx.set_head_near()


def stage_candidates():
    # Frozen, cheap availability checks.  plan_route also carries the
    # planner's script state (MEM); previews stay lazy in stage_decision.
    own_idx = {c: i for i, c in enumerate(w.body)}
    target, dist, mask, kind = ex.plan_route(own_idx)
    work["plan"] = {"target": target, "dist": dist, "mask": mask, "kind": kind}
    work["feed"] = ex.feeder_sacrifice(w.body)
    work["moves"] = ex.move_proposals(w.body)
    work["split"] = ex.split_proposal(w.body)


def stage_decision():
    if work["feed"] is not None:
        # FEED_ALLY: an explicit intentional donation outranks everything.
        work["actions"] = [(0.0, ("move", work["feed"]), dec.FEED_ALLY,
                            "sacrifice", None)]
    else:
        work["actions"] = dec.rank(work["threat"], work["plan"],
                                   work["moves"], work["split"])
    work["selected"] = dec.select(work["actions"])
    work["score"] = work["selected"][0]


def stage_execution():
    kind, arg = work["selected"][1]
    if kind == "split":
        cmd, a = ex.split_execute(arg)
        io.reply.update(command=cmd, argument=a)
    else:
        cmd, a, cells = ex.move_execute(arg)
        io.reply.update(command=cmd, argument=a)
        work["path_cells"] = cells


def stage_commit():
    # Message selection (radio) then encoding (comms via radio); the crown
    # handoff override rides the split's own body ray.
    work["messages"] = radio.outgoing()
    act = work["selected"][1]
    if act[0] == "split" and roles.ROLE[0] == "crown" and act[1] > w.LEN - act[1]:
        work["messages"][w.DIRS[(w.FACE + 2) % 4]] = comms.handoff_packet(act[1], w.RND)
    io.reply["sonar"] = work["messages"]


def record_diagnostics():
    work["intent"], work["intent_note"] = dec.classify(work["selected"], work["plan"])
    if P["training_trace"]:
        from diagnostics import trace_threats, trace_intent
        trace_threats(work)
        trace_intent(work)


def fallback():
    io.reply["sonar"] = {}
    d = ex.emergency_move()
    if d is not None:
        io.reply.update(command=io.Command.MOVE, argument=w.DIRS[d])


def main():
    if not io.read_init():
        return
    initialize_state()
    while io.read_turn():
        work.clear()
        io.reply.clear()
        io.reply.update(command=io.Command.MOVE, argument=io.observation["direction"], sonar={})
        try:
            stage_state()
            stage_features()
            stage_candidates()
            stage_decision()
            stage_execution()
            stage_commit()
            record_diagnostics()
        except Exception as exc:
            # A visible diagnostic, not a silently successful turn. One flush below.
            sys.stdout.write("LOG ATHOS_ERROR " + type(exc).__name__ + "\n")
            fallback()
        w.trail.extend(work.get("path_cells", ()))
        io.write_reply()


if __name__ == "__main__":
    main()
