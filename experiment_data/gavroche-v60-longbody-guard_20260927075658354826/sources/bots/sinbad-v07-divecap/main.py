"""Sinbad v01 -- evaluation-function dragon (see README.md).

Flow: protocol input -> decode reports -> update state -> build features
      -> candidates -> choose -> execute -> construct/encode reports -> output.
"""
from enum import Enum, auto
import os
import protocol as io
import world as w
import tactics as tx
import policy as pol
import roles
import radio
import comms
from params import P


class Intent(Enum):
    MOVE = auto()     # a path of 1-3 steps (sprint)
    SPLIT = auto()
    STRIKE = auto()   # a path ending on an enemy head


state = {}
work = {}
TRACE = os.path.exists("/tmp/sinbad-trace-on")


def trace(msg):
    if TRACE:
        with open("/tmp/sinbad-%d-%s-%d.log" % (os.getppid(), w.TEAM, w.ME), "a") as fh:
            fh.write(msg + "\n")


def initialize_state():
    w.init()
    w.T_HIDDEN[0] = P["t_hidden"]
    w.PREY_MIN[0] = P["prey_min"]
    w.PREY_TTL[0] = P["prey_ttl"]
    pol.LADDER[0] = w.NC <= P["ladder_nc"]
    if not TRACE:
        pol.DBG = None


def decode_messages():
    work["reports"] = io.observation["messages"]


def update_state():
    mine = w.sense()
    w.track_body(mine)
    w.prune()
    radio.hear(work["reports"])
    roles.update()


def build_features():
    if roles.ROLE[0] == "crown":  # long sprints kill crowns: look further
        work["threat"] = tx.threat_map(P["reach_cap_crown"], True)
    else:
        work["threat"] = tx.threat_map()
    tx.set_head_near()


def choose_action():
    score, act = pol.evaluate(work["threat"])
    work["selected"] = act
    work["score"] = score


def execute_action():
    act = work["selected"]
    if act is None:
        return
    kind, arg = act
    if kind == "split":
        io.reply["command"] = io.Command.SPLIT
        io.reply["argument"] = str(arg)
        return
    io.reply["command"] = io.Command.MOVE
    io.reply["argument"] = "".join(w.DIRS[d] for d in arg)
    if len(arg) > 1:  # remember intermediate head cells for body tracking
        st, nb, eaten, hit = tx.sim(arg, w.body)
        if st == "ok":
            work["path_cells"] = nb[-len(arg):-1]


def construct_messages():
    pass


def encode_messages():
    io.reply["sonar"] = radio.outgoing()
    act = work.get("selected")
    if act and act[0] == "split" and roles.ROLE[0] == "crown" and act[1] > w.LEN - act[1]:
        # the child keeps most of the crown: tell it, through our own body
        io.reply["sonar"][w.DIRS[(w.FACE + 2) % 4]] = comms.handoff_packet(act[1], w.RND)


def record_diagnostics():
    if TRACE:
        trace("   eh=%s ah=%s" % (w.enemy_heads, w.ally_heads[:6]))
        trace("   " + " ".join("%s:%s:%s" % ("".join(w.DIRS[d] for d in pa), sc, ar) for pa, sc, ar in pol.DBG if len(pa) == 1))
        del pol.DBG[:]
        trace("r%d len%d head%d %s act=%s score=%.2f tgt=%d crown=%s" % (
            w.RND, w.LEN, w.HEAD, roles.ROLE[0], work.get("selected"), work.get("score", 0),
            pol.MEM["target"], w.crown))


def fallback():
    """First single step that the exact simulation survives."""
    io.reply["sonar"] = {}
    for d in range(4):
        try:
            if tx.sim([d], w.body)[0] == "ok":
                io.reply["command"] = io.Command.MOVE
                io.reply["argument"] = w.DIRS[d]
                return
        except Exception:
            break


def main():
    if not io.read_init():
        return
    initialize_state()
    while io.read_turn():
        work.clear()
        work.update(reports=[], actions=[], selected=None, messages=[], state_updates={})
        io.reply.clear()
        io.reply.update(command=io.Command.MOVE, argument=io.observation["direction"], sonar={})
        try:
            decode_messages()
            update_state()
            build_features()
            choose_action()
            execute_action()
            construct_messages()
            encode_messages()
            record_diagnostics()
        except Exception as exc:  # never forfeit a turn to a bug
            fallback()
            if TRACE:
                import traceback
                trace("EXC r%d %s" % (w.RND, traceback.format_exc()))
        pc = work.get("path_cells")
        if pc:
            w.trail.extend(pc)
        io.write_reply()


if __name__ == "__main__":
    main()
