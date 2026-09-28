"""ouroboros-s02 (Claude, Ouroboros lineage) on the fenrir-v18 host (live control 9508).

Host docstring follows.  s02 adds: atlas + portal probe + HOLD (portal safety),
atlas beds / pre-positioning / contested sprints (economy), portal-landing
exploration, the newborn neck fix, and ACT markers; every mechanism is a
params.py switch.

Monte Christo: Bahamut hooks with explicit state, features, policy and I/O.

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
import separation
from params import P

work = {}


def initialize_state():
    w.init()
    w.T_HIDDEN[0] = P["t_hidden"]
    w.PREY_MIN[0] = P["prey_min"]
    w.PREY_TTL[0] = P["prey_ttl"]
    pol.DBG = None
    density.init()
    separation.init()


def decode_messages():
    # radio owns semantic decode/validation after current coordinates are known.
    work["reports"] = io.observation["messages"]


def update_state():
    mine = w.sense()
    w.track_body(mine)
    w.prune()
    radio.hear(work["reports"])
    separation.observe_birth()
    roles.update()
    density.observe()


def build_features():
    work["threat"] = tx.threat_map()
    tx.set_head_near()


def build_actions():
    work["actions"] = pol.rank_actions(work["threat"])


def choose_action():
    work["score"], work["selected"] = max(work["actions"], key=lambda pair: pair[0])
    if P.get("diag", 0) and work["score"] < -900:
        work["act"].append("DG:forced")
    elif P.get("diag", 0) and work["selected"][0] == "move":
        st = tx.sim(work["selected"][1], w.body)[0]
        if st != "ok":
            work["act"].append("DG:" + st)
        elif len(w.body) < w.LEN:
            work["act"].append("DG:partial")


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
    if act[0] == "split":
        inherit = roles.ROLE[0] == "crown" and act[1] > w.LEN - act[1]
        escape = (not inherit and roles.ROLE[0] == "forager" and
                  len(w.body) >= w.LEN and separation.should_escape_spawn(w.body[0]))
        if escape or inherit:
            packet = comms.split_packet(w.ME, w.body[0], w.RND, escape, inherit)
            work["messages"][w.DIRS[(w.FACE + 2) % 4]] = packet
            separation.queue_handoff(packet, w.RND)
    else:
        separation.retry_handoff(work["messages"], w.RND, w.FACE)


def probe_ray():
    """s02 (after chaewon y04/y05): when the chosen move leaves our head next to
    a portal whose landing we cannot see, cast that one ray alone through it
    carrying a HOLD packet; next turn's echo is attributable to it."""
    if not P["probe_on"] or roles.ROLE[0] == "crown":
        return
    if separation.PENDING_HANDOFF is not None:
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
    work["messages"] = {w.DIRS[best[1]]: comms.hold_packet(nh, w.RND)}
    w.PROBE[0] = w.RND
    w.PROBE[1] = nh
    w.PROBE[2] = best[2]
    work["act"].append("ACT:probe")


def mark_actions():
    """s02 activation contract markers (LOG ACT:<tag>)."""
    kind, arg = work["selected"]
    if kind != "move":
        return
    acts = work["act"]
    tgt = pol.MEM.get("target", -1)
    if len(arg) > 1 and pol.MEM.get("sprint_ok") and w.pearls.get(
            tx.sim(arg, w.body)[1][-1]) == w.RND:
        acts.append("ACT:sprint")
    if tgt >= 0 and w.bed[tgt] == 2 and w.pearls.get(tgt) != w.RND:
        # economy markers: an atlas bed never seen (bed) or a fast bed not yet
        # due at arrival (pre-positioning); the far-target fallback (far)
        s = w.spawn.get(tgt)
        if s is None:
            if w.ABED is not None and not w.seen[tgt]:
                acts.append("ACT:far" if tgt == pol.MEM.get("far") else "ACT:bed")
        elif s > w.RND + w.tdist(w.HEAD, tgt):
            acts.append("ACT:bed")
    if pol.MEM.get("explore") and (w.portal_steps().get(w.HEAD, 0) >> arg[0]) & 1:
        acts.append("ACT:dive")


def encode_messages():
    io.reply["sonar"] = work["messages"]


def record_diagnostics():
    if P["density_trace"]:
        density.trace(work)
    if P["training_trace"]:
        from diagnostics import trace_threats
        trace_threats(work)
    indicator = separation.indicator()
    if indicator is not None:
        io.reply["indicator"] = indicator


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
        work["act"] = []
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
            mark_actions()
            encode_messages()
            record_diagnostics()
        except Exception as exc:
            # A visible diagnostic, not a silently successful turn. One flush below.
            import sys
            sys.stdout.write("LOG MC_ERROR " + type(exc).__name__ + "\n")
            fallback()
        if w.DIAG:
            work.setdefault("act", []).extend(w.DIAG)
            del w.DIAG[:]
        if work.get("act"):
            io.reply["log"] = work["act"]
        w.trail.extend(work.get("path_cells", ()))
        io.write_reply()


if __name__ == "__main__":
    main()
