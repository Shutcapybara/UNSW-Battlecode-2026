"""Porthos x02: the six-stage intention contract over Monte Christo v01.

Pipeline per turn (contract version 1):
  1. state update   -- observation + reports consumed once (world/radio/roles)
  2. candidates     -- intentions.propose: cheap frozen availability, stable
                       (kind, target, arg, id) records
  3. features       -- global features BEFORE candidates (allowed), then
                       target features and per-candidate mechanical previews
  4. decision       -- policy P0 scores and selects (decision.py)
  5. execution      -- the nominated intention's executor returns one
                       command + predicted outcome + status + diagnostics
  6. commit/output  -- only the selected execution's trail cells are
                       committed; messages constructed/encoded; reply sent

World owns perception memory; roles owns crown election; targets.MEM owns
target hysteresis.  Candidate evaluation never changes the simulated body or
protocol observation.
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
from params import P

work = {}


def initialize_state():
    w.init()
    w.T_HIDDEN[0] = P["t_hidden"]
    w.PREY_MIN[0] = P["prey_min"]
    w.PREY_TTL[0] = P["prey_ttl"]
    decision.DBG = None


def decode_messages():
    # radio owns semantic decode/validation after current coordinates are known.
    work["reports"] = io.observation["messages"]


def update_state():
    mine = w.sense()
    w.track_body(mine)
    w.prune()
    radio.hear(work["reports"])
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
        work["cands"], work["tf"], work["gf"]["threat"])


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
