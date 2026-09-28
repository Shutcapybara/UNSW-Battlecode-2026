"""GAME I/O ADAPTER — normally leave unchanged.

Our implementation of the engine protocol, not strategy or sonar payload meaning.
Modify only to fix an adapter bug or change the supported game protocol.
"""
from enum import Enum
import sys
import frame


class Command(Enum):
    MOVE = "MOVE"    # argument: direction string, e.g. "N" or "NNE".
    SPLIT = "SPLIT"  # argument: number of segments to split off.


game, observation, reply = {}, {}, {}


def read_tokens():
    while True:
        line = sys.stdin.readline()
        if not line:
            return []
        tokens = line.split("#", 1)[0].split()
        if tokens:
            return tokens


def read_init():
    row = read_tokens()
    if not row:
        return False
    game.update(id=int(row[1]), team=read_tokens()[1],
                size=tuple(map(int, read_tokens()[1:])),
                unit_limit=int(read_tokens()[1]))
    frame.choose(game["size"][0], game["size"][1], game["team"])
    return True


def read_turn():
    row = read_tokens()
    if not row or row[0] == "ENDGAME":
        return False
    observation.clear()
    observation.update(round=int(row[1]), direction=frame.dirs(read_tokens()[1]),
                       length=int(read_tokens()[1]), units=int(read_tokens()[1]))
    observation["messages"] = [int(read_tokens()[0]) for _ in range(int(read_tokens()[1]))]
    row = read_tokens()
    observation["echoes"] = (0, 0, 0, 0, 0)
    if row[0] == "ECHOES":  # Absent before the first PROTOCOL 3 reply.
        observation["echoes"] = tuple(map(int, row[1:]))
        row = read_tokens()
    observation["tiles"] = frame.tiles([tuple(map(int, row))] + [tuple(map(int, read_tokens())) for _ in range(48)])
    observation["bodies"] = [frame.body(b) for b in [read_tokens() for _ in range(int(read_tokens()[1]))]]
    observation["horizontal_edges"] = frame.hedges([read_tokens() for _ in range(8)])
    observation["vertical_edges"] = frame.vedges([read_tokens() for _ in range(7)])
    return True


def write_reply():
    arg = reply["argument"]
    if reply["command"] == Command.MOVE:
        arg = frame.dirs(arg)
    lines = [f'{reply["command"].value} {arg}']
    if frame.MODE[0] != "id" and not frame.LOGGED[0]:  # activation marker, once per dragon
        lines.insert(0, "LOG ACT:frame:" + frame.MODE[0])
        frame.LOGGED[0] = True
    lines += [f"SONAR {frame.dirs(direction)} {payload}" for direction, payload in reply["sonar"].items()]
    sys.stdout.write("\n".join(lines + ["PROTOCOL 3", "ENDTURN"]) + "\n")
    sys.stdout.flush()
