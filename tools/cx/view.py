#!/usr/bin/env python3
"""Render one turn block (protocol 3 input) as ASCII: the 7x7 window with kelp
edges (| and -), portal edges (digits / P), pearls (o), bed countdowns, dragon
parts (own head @, own body *, ally head A / body a, enemy head E / body e).

    python3 tools/cx/view.py TRANSCRIPT.jsonl-or-arena.json DRAGON_ID [ROUND ...]
    (or import render(block, me) from other tools)
"""
from __future__ import annotations

import json
import sys


def parse(block: str) -> dict:
    lines = [l.split("#", 1)[0].split() for l in block.splitlines()]
    lines = [l for l in lines if l]
    i = 0
    out = {"round": int(lines[0][1]), "dir": lines[1][1], "len": int(lines[2][1]),
           "units": int(lines[3][1])}
    n = int(lines[4][1])
    i = 5 + n
    if lines[i][0] == "ECHOES":
        i += 1
    out["tiles"] = [tuple(map(int, lines[i + k])) for k in range(49)]
    i += 49
    nb = int(lines[i][1])
    out["bodies"] = lines[i + 1:i + 1 + nb]
    i += 1 + nb
    out["h"] = lines[i:i + 8]
    out["v"] = lines[i + 8:i + 15]
    return out


def render(block: str, me: int | None = None, team: str | None = None) -> str:
    o = parse(block)
    tiles = o["tiles"]
    pos = {}
    for b in o["bodies"]:
        t, did, x, y, f, hd = b[0], int(b[1]), int(b[2]), int(b[3]), b[4], b[5] == "1"
        if did == me:
            ch = "@" if hd else "*"
        elif team and t == team:
            ch = "A" if hd else "a"
        else:
            ch = "E" if hd else "e"
        pos[(x, y)] = ch
    rows = [f"round {o['round']} dir {o['dir']} len {o['len']} units {o['units']}  "
            f"x {tiles[0][0]}..{tiles[6][0]} y {tiles[0][1]}..{tiles[42][1]}"]
    for r in range(8):
        # horizontal edges row r
        line = "+"
        for c in range(7):
            e = o["h"][r][c]
            line += ("---" if e == "w" else "   " if e == "." else f"{e:^3}"[:3]) + "+"
        rows.append(line)
        if r == 7:
            break
        line = ""
        for c in range(8):
            e = o["v"][r][c]
            line += "|" if e == "w" else " " if e == "." else "P"
            if c < 7:
                x, y, p, cd = tiles[r * 7 + c]
                ch = pos.get((x, y))
                if ch:
                    cell = f" {ch} "
                elif p:
                    cell = " o "
                elif cd >= 0:
                    cell = f"{cd:>3}" if cd < 1000 else "  +"
                else:
                    cell = "   "
                line += cell
        rows.append(line)
    return "\n".join(rows)


def main() -> int:
    path, did = sys.argv[1], sys.argv[2]
    want = set(map(int, sys.argv[3:]))
    data = json.load(open(path))
    tr = data["transcripts"][did] if "transcripts" in data else data
    team = None
    for l in tr["init"].splitlines():
        if l.startswith("TEAM"):
            team = l.split()[1]
    for t in tr["turns"]:
        if not want or t["round"] in want:
            print(render(t["input"], int(did), team))
            print(">>", t["output"].replace("\n", " | "))
    return 0


if __name__ == "__main__":
    sys.exit(main())
