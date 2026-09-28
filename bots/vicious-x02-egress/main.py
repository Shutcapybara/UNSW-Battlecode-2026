"""Monte Christo: Bahamut hooks with explicit state, features, policy and I/O.

World owns perception memory; roles owns crown election; policy.MEM owns target
hysteresis. Candidate evaluation never changes the simulated body or protocol
observation. Only the selected execution commits intermediate trail positions.
"""
import protocol as io
import world as w
import tactics as tx
import policy as pol
import roles
import radio
import comms
import density
import temporal
from params import P

work = {}


def initialize_state():
    w.init()
    w.T_HIDDEN[0] = P["t_hidden"]
    w.PREY_MIN[0] = P["prey_min"]
    w.PREY_TTL[0] = P["prey_ttl"]
    pol.DBG = None
    density.init()


def decode_messages():
    # radio owns semantic decode/validation after current coordinates are known.
    work["reports"] = io.observation["messages"]


def update_state():
    mine = w.sense()
    w.track_body(mine)
    w.prune()
    radio.hear(work["reports"])
    roles.update()
    density.observe()
    temporal.observe()


def build_features():
    work["threat"] = tx.threat_map()
    tx.set_head_near()


def build_actions():
    work["actions"] = temporal.adjust(pol.rank_actions(work["threat"]), work["threat"])


def choose_action():
    work["score"], work["selected"] = max(work["actions"], key=lambda pair: pair[0])


def execute_action():
    kind, arg = work["selected"]
    if kind == "split":
        io.reply.update(command=io.Command.SPLIT, argument=str(arg))
    else:
        io.reply.update(command=io.Command.MOVE, argument="".join(w.DIRS[d] for d in arg))
        if len(arg) > 1:
            st, nb, _, _ = tx.sim(arg, w.body)
            if st == "ok":
                work["path_cells"] = nb[-len(arg):-1]


def construct_messages():
    # Scheduling chooses packet content and rays. comms.py owns bit encoding.
    work["messages"] = radio.outgoing()
    temporal.send(work)
    act = work["selected"]
    if act[0] == "split" and roles.ROLE[0] == "crown" and act[1] > w.LEN - act[1]:
        work["messages"][w.DIRS[(w.FACE + 2) % 4]] = comms.handoff_packet(act[1], w.RND)


def encode_messages():
    io.reply["sonar"] = work["messages"]


def record_diagnostics():
    temporal.trace(work)
    if P["density_trace"]:
        density.trace(work)
    if P["training_trace"]:
        from diagnostics import trace_threats
        trace_threats(work)


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
            build_features()
            build_actions()
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
        w.trail.extend(work.get("path_cells", ()))
        io.write_reply()


if __name__ == "__main__":
    main()
