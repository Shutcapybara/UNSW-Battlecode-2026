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
import separation
import gaia
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
    gaia.init()


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
    gaia.observe()


def build_features():
    work["threat"] = tx.threat_map()
    tx.set_head_near()


def build_actions():
    work["actions"] = pol.rank_actions(work["threat"])


def choose_action():
    work["score"], work["selected"] = max(work["actions"], key=lambda pair: pair[0])
    if not action_is_safe(work["selected"]):
        fallback()


def action_is_safe(action):
    """Validate the planner result before it reaches the engine.

    This is the final guard against a stale route, an unsafe pearl, or a
    malformed split.  It is intentionally independent of action scoring.
    """
    kind, arg = action
    if kind == "split":
        return gaia.split_legal(arg)
    status, body_after, eaten, hit = tx.sim(arg, w.body)
    if status == "dead":
        return False
    if status == "h2h" and not gaia.combat_allowed(hit):
        return False
    return gaia.safe_move(arg, body_after, eaten, work.get("threat"))


def execute_action():
    kind, arg = work["selected"]
    if kind == "split":
        io.reply.update(command=io.Command.SPLIT, argument=str(arg))
    else:
        io.reply.update(command=io.Command.MOVE, argument="".join(w.DIRS[d] for d in arg))
        status, body_after, eaten, _ = tx.sim(arg, w.body)
        gaia.record_portal(arg, status)
        if len(arg) > 1:
            if status == "ok":
                work["path_cells"] = body_after[-len(arg):-1]


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
    """Recover in safety order while always checking engine legality.

    Normal safe choices are preferred. If every move is rejected by Gaia's
    safety policy, choose an ordinary simulator-legal move before considering
    a head trade or blind portal. This prevents exception recovery from
    emitting a blocked direction without making risky movement the first
    response to a pearl/pathfinding veto.
    """
    options = []
    ordinary_legal = []
    risky_legal = []
    for d in range(4):
        status, body_after, eaten, hit = tx.sim([d], w.body)
        if status == "dead":
            continue
        n = body_after[-1] if body_after else w.HEAD
        score = gaia.action_bonus(n, d) - P.get("w_visit", 0.0) * w.visits[n]
        # Prefer ordinary moves to blind dives or head trades in a fallback.
        score += 2.0 if status == "ok" else -2.0
        (ordinary_legal if status == "ok" else risky_legal).append((score, d))
        if not gaia.safe_move([d], body_after, eaten, work.get("threat")):
            continue
        if status == "h2h" and not gaia.combat_allowed(hit):
            continue
        options.append((score, d))
    if options:
        _, d = max(options)
        work["selected"] = ("move", [d])
        io.reply.update(command=io.Command.MOVE, argument=w.DIRS[d], sonar={})
        return
    if ordinary_legal:
        _, d = max(ordinary_legal)
        work["selected"] = ("move", [d])
        io.reply.update(command=io.Command.MOVE, argument=w.DIRS[d], sonar={})
        return
    if gaia.split_legal(P.get("child", 2)):
        work["selected"] = ("split", P.get("child", 2))
        io.reply.update(command=io.Command.SPLIT, argument=str(P.get("child", 2)), sonar={})
        return
    if risky_legal:
        _, d = max(risky_legal)
        work["selected"] = ("move", [d])
        io.reply.update(command=io.Command.MOVE, argument=w.DIRS[d], sonar={})
        return
    # Every direction can be occupied in a terminal position.  The first
    # command is still syntactically legal; the engine will report the death
    # rather than receiving an invalid/empty action from this process.
    work["selected"] = ("move", [0])
    io.reply.update(command=io.Command.MOVE, argument=w.DIRS[0], sonar={})


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
