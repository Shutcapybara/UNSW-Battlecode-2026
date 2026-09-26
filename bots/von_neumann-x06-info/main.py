"""Porthos x04: policy P1 over the x03 swarm state/radio layer.

Pipeline per turn (contract version 1, as x03):
  1. state update   -- observation + reports consumed once (world/radio/roles);
                       density.observe / swarm.observe fold the sonar evidence
  2. candidates     -- intentions.propose (frozen v1)
  3. features       -- global features BEFORE candidates, then target features
                       and per-candidate mechanical previews (FEATURES v2)
  4. decision       -- policy P1 (decision.py v2): P0's field conditioned on
                       phase, saturation, confinement and density evidence
  5. execution      -- executor set E0 (frozen v1)
  6. commit/output  -- only the selected execution's trail cells commit

x04 = x03 with ONLY the decision layer replaced (policy P0 -> P1); candidate
construction, target search, previews, weights defaults and executors are
frozen, so x03 vs x04 isolates the feature consumers:
  early-saturation aggression, confinement-gated production,
  density-discounted target progress.
"""
import protocol as io
import world as w
import tactics as tx
import roles
import radio
import comms
import targets
import intentions
import features
import decision
import executors
import density
import swarm
from params import P

work = {}


def initialize_state():
    w.init()
    w.T_HIDDEN[0] = P["t_hidden"]
    w.PREY_MIN[0] = P["prey_min"]
    w.PREY_TTL[0] = P["prey_ttl"]
    decision.DBG = None
    density.init()
    swarm.init()


def decode_messages():
    # radio owns semantic decode/validation after current coordinates are known.
    work["reports"] = io.observation["messages"]


def update_state():
    mine = w.sense()
    w.track_body(mine)
    w.prune()
    radio.hear(work["reports"])
    density.observe()
    swarm.observe(mine)
    roles.update()


def build_global_features():
    work["gf"] = features.global_features()


def build_candidates():
    work["cands"], work["ctx"] = intentions.propose()


def build_features():
    work["tf"] = features.target_features(work["ctx"])
    for c in work["cands"]:
        features.preview(c, work["gf"], work["tf"])


def choose_action():
    work["selected"], work["ranked"] = decision.choose(
        work["cands"], work["tf"], work["gf"])


def execute_action():
    work["exec"] = executors.execute(work["selected"])
    kind, arg = work["exec"]["command"]
    if kind == "split":
        io.reply.update(command=io.Command.SPLIT, argument=str(arg))
    else:
        io.reply.update(command=io.Command.MOVE,
                        argument="".join(w.DIRS[d] for d in arg))


def construct_messages():
    # Scheduling chooses packet content and rays. comms.py owns bit encoding.
    work["messages"] = radio.outgoing()
    kind, arg = work["exec"]["command"]
    if kind == "split" and roles.ROLE[0] == "crown" and arg > w.LEN - arg:
        work["messages"][w.DIRS[(w.FACE + 2) % 4]] = comms.handoff_packet(arg, w.RND)


def encode_messages():
    io.reply["sonar"] = work["messages"]


def record_diagnostics():
    if P["training_trace"]:
        from diagnostics import trace_threats
        kind, arg = work["exec"]["command"]
        trace_threats({"selected": (kind, arg), "threat": work["gf"]["threat"]})
    if P["intent_trace"]:
        import json
        import sys
        rec = work["exec"]
        sys.stdout.write("LOG MC_INTENT " + json.dumps({
            "kind": work["selected"]["kind"], "reason": rec["reason"],
            "status": rec["status"], "predicted": rec["predicted"],
            "trade": rec["trade"], **rec["diag"]},
            separators=(",", ":")) + "\n")


def fallback():
    io.reply["sonar"] = {}
    for d in range(4):
        if tx.sim([d], w.body)[0] == "ok":
            io.reply.update(command=io.Command.MOVE, argument=w.DIRS[d])
            return


def main():
    if not io.read_init():
        return
    initialize_state()
    while io.read_turn():
        work.clear()
        io.reply.clear()
        io.reply.update(command=io.Command.MOVE, argument=io.observation["direction"], sonar={})
        try:
            decode_messages()
            update_state()
            build_global_features()
            build_candidates()
            build_features()
            choose_action()
            execute_action()
            construct_messages()
            encode_messages()
            record_diagnostics()
        except Exception as exc:
            # A visible diagnostic, not a silently successful turn. One flush below.
            import sys
            sys.stdout.write("LOG MC_ERROR " + type(exc).__name__ + "\n")
            fallback()
        # Only the selected execution's script state is committed (and, on an
        # error turn after execution, exactly what the legacy bot committed).
        w.trail.extend(work.get("exec", {}).get("path_cells", ()))
        io.write_reply()


if __name__ == "__main__":
    main()
