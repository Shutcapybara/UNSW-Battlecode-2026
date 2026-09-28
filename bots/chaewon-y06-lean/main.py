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
import yuna
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
    yuna.apply_phase_overrides()
    w.track_body(mine)
    w.prune()
    radio.hear(work["reports"])
    roles.update()
    density.observe()
    if P["nb_mode"]:
        yuna.note_birth()


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


def probe_ray():
    """y04 portal probe: when our head ends next to a portal whose landing we
    cannot see, cast that one ray alone (next turn's echo is then its own)."""
    if not P["probe_on"] or roles.ROLE[0] == "crown" or not w.ATLAS[0]:
        return
    kind, arg = work["selected"]
    nh = w.HEAD
    if kind == "move":
        st, nb, _, _ = tx.sim(arg, w.body)
        if st != "ok":
            return
        nh = nb[-1]
    tgt = pol.MEM.get("target", -1)
    best = None
    for d in range(4):
        if w.ek[w.ekey(nh, d)] != 3:
            continue
        L = w.dest(nh)[d]
        if L < 0 or w.cheb(L, nh) <= 3:
            continue
        pr = w.PRES.get(L)
        if pr is not None and w.RND + 1 - pr[0] <= 1:
            continue
        key = w.tdist(L, tgt) if tgt >= 0 else d
        if best is None or key < best[0]:
            best = (key, d, L)
    if best is None:
        return
    work["messages"] = {w.DIRS[best[1]]: 0}
    w.PROBE[0] = w.RND
    w.PROBE[1] = nh
    w.PROBE[2] = best[2]


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
            if work["selected"][0] != "split":
                probe_ray()
            encode_messages()
            record_diagnostics()
        except Exception as exc:
            # A visible diagnostic, not a silently successful turn. One flush below.
            import sys
            sys.stdout.write("LOG MC_ERROR " + type(exc).__name__ + "\n")
            fallback()
        sel = work.get("selected")
        if P["mom_w"] and sel and sel[0] == "move":
            yuna.mom_update(sel[1][0])
        if yuna.EVENTS:
            import sys
            sys.stdout.write("".join("LOG Y " + e + "\n" for e in yuna.EVENTS))
            del yuna.EVENTS[:]
        w.trail.extend(work.get("path_cells", ()))
        io.write_reply()


if __name__ == "__main__":
    main()
