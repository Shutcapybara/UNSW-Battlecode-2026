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
import sys
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


def build_features():
    work["threat"] = tx.threat_map()
    tx.set_head_near()


def build_actions():
    work["actions"] = pol.rank_actions(work["threat"])


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
    act = work["selected"]
    if act[0] == "split" and roles.ROLE[0] == "crown" and act[1] > w.LEN - act[1]:
        work["messages"][w.DIRS[(w.FACE + 2) % 4]] = comms.handoff_packet(act[1], w.RND)


def encode_messages():
    io.reply["sonar"] = work["messages"]


def record_diagnostics():
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
        w.PROFILE[:] = [0] * len(w.PROFILE)
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
            sys.stdout.write("LOG MC_ERROR " + type(exc).__name__ + "\n")
            fallback()
        if P.get("cpu_profile", 0) and w.RND >= 350:
            p = w.PROFILE
            sys.stdout.write(
                "LOG PROFILE r=%d id=%d len=%d units=%d occ=%d allies=%d enemies=%d "
                "sim=%d threat_heads=%d threat_nodes=%d floods=%d flood_nodes=%d "
                "search_nodes=%d candidates=%d visible_segments=%d vacancy_links=%d vacancy_walk=%d\n"
                % (w.RND, w.ME, w.LEN, w.UNITS, len(w.occ), len(w.ally_heads),
                   len(w.enemy_heads), p[0], p[1], p[2], p[3], p[4], p[5],
                   p[6], p[7], p[8], p[9]))
        w.trail.extend(work.get("path_cells", ()))
        io.write_reply()


if __name__ == "__main__":
    main()
