#!/usr/bin/env python3
"""ASCII map view: kelp walls, portals, pearl beds, spawns.  Also used as a
library (load_map) by analysis tools.

    python3 tools/ouroboros/mapview.py maps/devil.map
"""
import sys


def load_map(text):
    W = H = 0
    tiles = {}
    kelp_h = set()   # (x, y): north side of (x, y)
    kelp_v = set()   # (x, y): west side of (x, y)
    portal_h = {}
    portal_v = {}
    dragons = []
    for line in text.splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == "MAP":
            W, H = int(p[1]), int(p[2])
        elif p[0] == "TILE":
            tiles[(int(p[1]), int(p[2]))] = (int(p[3]), int(p[4]))
        elif p[0] == "EDGE":
            idx, kind, pid = int(p[1]), int(p[2]), int(p[3])
            stride = W + 1
            col, row = idx % stride, idx // stride
            if row % 2 == 0:
                if col == W or row == 2 * H:
                    continue
                key, kset, pset = (col, row // 2), kelp_h, portal_h
            else:
                if col == W:
                    continue
                key, kset, pset = (col, (row - 1) // 2), kelp_v, portal_v
            if kind == 1:
                kset.add(key)
            elif kind == 2:
                pset[key] = pid
        elif p[0] == "DRAGON":
            n = int(p[2])
            dragons.append(("AB"[int(p[1])], [(int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n)]))
    return dict(W=W, H=H, tiles=tiles, kelp_h=kelp_h, kelp_v=kelp_v, portal_h=portal_h,
                portal_v=portal_v, dragons=dragons)


def render(m):
    W, H = m["W"], m["H"]
    heads = {}
    for team, cells in m["dragons"]:
        heads[cells[0]] = team
        for c in cells[1:]:
            heads.setdefault(c, team.lower())
    out = []
    for y in range(H):
        row = []
        for x in range(W):
            e = m["portal_h"].get((x, y))
            row.append("+" + ("~~" if (x, y) in m["kelp_h"] else ("%2d" % e if e is not None else "  ")))
        out.append("".join(row) + "+")
        row = []
        for x in range(W):
            e = m["portal_v"].get((x, y))
            wall = "|" if (x, y) in m["kelp_v"] else ("%d" % (e % 10) if e is not None else " ")
            t = m["tiles"].get((x, y), (0, 0))
            ch = heads.get((x, y))
            body = ch * 2 if ch else ("::" if t[1] > 0 and t[1] <= 30 else ".." if t[1] > 0 else "  ")
            row.append(wall + body)
        out.append("".join(row) + "|" if (0, y) in m["kelp_v"] else "".join(row) + " ")
    out.append("+--" * W + "+")
    return "\n".join(out)


if __name__ == "__main__":
    m = load_map(open(sys.argv[1]).read())
    print("%s: %dx%d  beds=%d  kelp=%d  portals=%d" % (
        sys.argv[1], m["W"], m["H"], sum(1 for t in m["tiles"].values() if t[1] > 0),
        len(m["kelp_h"]) + len(m["kelp_v"]), len(m["portal_h"]) + len(m["portal_v"])))
    print("legend: ~~ kelp (horizontal), | kelp (vertical), digits portal ids, "
          ":: fast bed (max gap <= 30), .. slow bed, AA/BB spawns")
    print(render(m))
