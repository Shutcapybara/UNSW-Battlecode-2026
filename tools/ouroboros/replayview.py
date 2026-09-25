#!/usr/bin/env python3
"""Print ASCII frames of a replay: dragons, pearls, kelp.

    python3 tools/ouroboros/replayview.py REPLAY --rounds 20,30,40 [--window x,y,r]

Legend: A/B heads (uppercase), a/b bodies, o pearl, # cell with kelp on its
west side is shown as '|' between cells and '---' above cells.
"""
import argparse
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import replaystats as R  # noqa: E402
from mapview import load_map  # noqa: E402


def frames(path, rounds):
    rep = R.load(path)
    m = load_map(rep.map)
    W, H = m["W"], m["H"]
    team_of, body = {}, {}
    for i, (t, cells) in enumerate(m["dragons"]):
        team_of[i] = t
        body[i] = collections.deque(cells)
    alive = set(body)
    pearls = set()
    want = sorted(rounds)
    out = {}
    rnd = -1
    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            r = ev.roundStart.round
            if want and r >= want[0]:
                out[want.pop(0)] = draw(m, W, H, alive, body, team_of, pearls)
            rnd = r
        elif w == "tileChange":
            t = ev.tileChange
            p = (t.tile.x, t.tile.y)
            if t.hasPearl:
                pearls.add(p)
            else:
                pearls.discard(p)
        elif w == "dragonUpdate":
            u = ev.dragonUpdate
            b = body.get(u.id)
            if b is None:
                continue
            h = (u.head.x, u.head.y)
            t = (u.tail.x, u.tail.y)
            if b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != t:
                b.pop()
        elif w == "dragonSplit":
            s = ev.dragonSplit
            team_of[s.childId] = "A" if str(s.team) == "a" else "B"
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
            alive.add(s.childId)
        elif w == "dragonDeath":
            alive.discard(ev.dragonDeath.id)
    return out


def draw(m, W, H, alive, body, team_of, pearls):
    grid = {}
    for i in alive:
        t = team_of[i]
        for j, c in enumerate(body[i]):
            grid[c] = t if j == 0 else t.lower()
    lines = []
    na = sum(1 for i in alive if team_of[i] == "A")
    nb = len(alive) - na
    la = sum(len(body[i]) for i in alive if team_of[i] == "A")
    lb = sum(len(body[i]) for i in alive if team_of[i] == "B")
    lines.append("A: %d units, %d length   B: %d units, %d length   pearls on board: %d" % (
        na, la, nb, lb, len(pearls)))
    for y in range(H):
        top = []
        row = []
        for x in range(W):
            top.append("+" + ("--" if (x, y) in m["kelp_h"] else "  "))
            wall = "|" if (x, y) in m["kelp_v"] else " "
            ch = grid.get((x, y))
            if ch is None:
                ch = "o" if (x, y) in pearls else "."
            row.append(wall + ch + " ")
        lines.append("".join(top))
        lines.append("".join(row))
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("--rounds", default="50")
    a = ap.parse_args()
    fr = frames(a.replay, [int(r) for r in a.rounds.split(",")])
    for r, text in sorted(fr.items()):
        print("=== round %d ===" % r)
        print(text)
