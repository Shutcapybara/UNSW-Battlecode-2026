#!/usr/bin/env python3
"""Death forensics: for every death of one team, was it forced?

For each death we rebuild the board at the start of the dying dragon's turn
and count the neighbours of its head that were legal (not kelp, not any
body).  'forced' = no legal neighbour existed.  Output groups deaths by
reason x forced, and whose body / which kind of tile killed us.

    python3 tools/ouroboros/deaths.py REPLAY [--team A] [-v]
    python3 tools/ouroboros/deaths.py RUN_DIR [--cand NAME]   (all kept replays)
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import replaystats as R  # noqa: E402
from mapview import load_map  # noqa: E402

REASON = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body",
          "hitHeadToHead": "h2h", "noValidAction": "noaction"}
DV = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}
DIRN = ("north", "east", "south", "west")


def analyse(path, team_want, verbose=False):
    rep = R.load(path)
    m = load_map(rep.map)
    W, H = m["W"], m["H"]

    def kelp(x, y, d):
        if d == "north":
            return (x, y) in m["kelp_h"]
        if d == "south":
            return (x, (y + 1) % H) in m["kelp_h"]
        if d == "west":
            return (x, y) in m["kelp_v"]
        return ((x + 1) % W, y) in m["kelp_v"]

    def portal(x, y, d):
        if d == "north":
            return (x, y) in m["portal_h"]
        if d == "south":
            return (x, (y + 1) % H) in m["portal_h"]
        if d == "west":
            return (x, y) in m["portal_v"]
        return ((x + 1) % W, y) in m["portal_v"]

    team_of, body = {}, {}
    for i, (t, cells) in enumerate(m["dragons"]):
        team_of[i] = t
        body[i] = collections.deque(cells)
    alive = set(body)
    rnd = 0
    actor = None
    snap = {}
    start = None
    act = None
    out = collections.Counter()
    rows = []
    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rnd = ev.roundStart.round
        elif w == "turnStart":
            actor = ev.turnStart.id
            snap = {c: i for i in alive for c in body[i]}
            start = body[actor][0] if actor in body else None
            ln0 = len(body.get(actor, ()))
        elif w == "dragonAction":
            a = ev.dragonAction.action
            k = a.which()
            act = [str(d) for d in a.move] if k == "move" else ("split %d" % a.split if k == "split" else k)
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
            d = ev.dragonDeath
            i = d.id
            reason = REASON.get(str(d.reason), str(d.reason))
            if team_of.get(i) == team_want and i == actor and reason != "h2h" and start:
                hx, hy = start
                legal = 0
                what = []
                for dn in DIRN:
                    if kelp(hx, hy, dn):
                        what.append(dn[0] + ":kelp")
                        continue
                    if portal(hx, hy, dn):
                        legal += 1
                        what.append(dn[0] + ":portal")
                        continue
                    dx, dy = DV[dn]
                    c = ((hx + dx) % W, (hy + dy) % H)
                    o = snap.get(c)
                    if o is None:
                        legal += 1
                        what.append(dn[0] + ":free")
                    elif o == i:
                        what.append(dn[0] + ":self")
                    else:
                        what.append(dn[0] + (":ally" if team_of[o] == team_want else ":enemy")
                                    + ("H" if body[o][0] == c else ""))
                forced = "forced" if legal == 0 else "chosen"
                out[(reason, forced)] += 1
                rows.append(dict(round=rnd, id=i, len=ln0, reason=reason, forced=forced, at=start,
                                 act=act, around=what))
                if verbose:
                    print("r%-3d id%-4d len%-3d at%-9s %-5s %-6s act=%s  %s" % (
                        rnd, i, ln0, "%d,%d" % start, reason, forced, act, " ".join(what)))
            alive.discard(i)
    return out, rows


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--team", default="A")
    ap.add_argument("--cand", default="ouroboros")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    t = Path(a.target)
    total = collections.Counter()
    if t.is_dir():
        for line in (t / "results.jsonl").read_text().splitlines():
            r = json.loads(line)
            if not r.get("replay") or a.cand not in r["cand"]:
                continue
            c, _ = analyse(t / r["replay"], r["side"], a.v)
            total.update(c)
    else:
        total, _ = analyse(t, a.team, a.v)
    for k, v in sorted(total.items(), key=lambda kv: -kv[1]):
        print("%-6s %-7s %d" % (k[0], k[1], v))


if __name__ == "__main__":
    main()
