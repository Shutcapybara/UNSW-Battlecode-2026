#!/usr/bin/env python3
"""econ: production economics per team in a round window.

Why does one team out-produce the other?  For every kept replay of a run
(or single replays), per team, over rounds [lo, hi):

  eat/turn     pearls eaten per dragon-turn (head efficiency)
  near         mean torus distance from a head to the nearest pearl on board
  hoard        share of dragon-turns spent at length >= 4 without splitting
  split_len    mean parent length when it splits
  child_age    mean rounds from birth to a dragon's first split (born in window)
  len>=4 wait  mean rounds a dragon stays at length >= 4 before splitting
  sprint       sprint steps per dragon-turn
  units_end    units alive at hi

    python3 tools/ouroboros/econ.py RUN_DIR [--from 0 --to 40] [--opp NAME] [--map M]
    python3 tools/ouroboros/econ.py a.replay b.replay --team A
"""
import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import replaystats as R  # noqa: E402
from mapview import load_map  # noqa: E402


def stats(path, lo, hi):
    rep = R.load(path)
    m = load_map(rep.map)
    W, H = m["W"], m["H"]
    team, length, head, born, first_split, ready = {}, {}, {}, {}, {}, {}
    for i, (t, c) in enumerate(m["dragons"]):
        team[i] = t
        length[i] = 3
        born[i] = 0
    pearls = set()
    st = {t: collections.Counter() for t in "AB"}
    rnd = 0
    actor = None
    alive = set(team)

    def tdist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rnd = ev.roundStart.round
            if rnd >= hi:
                break
            continue
        if w == "turnStart":
            actor = ev.turnStart.id
            continue
        if w == "tileChange":
            p = (ev.tileChange.tile.x, ev.tileChange.tile.y)
            if ev.tileChange.hasPearl:
                pearls.add(p)
            else:
                pearls.discard(p)
                if actor in length and actor in alive:
                    length[actor] += 1
                    if lo <= rnd:
                        st[team[actor]]["pearls"] += 1
            continue
        if w == "dragonUpdate":
            u = ev.dragonUpdate
            head[u.id] = (u.head.x, u.head.y)
            continue
        if w == "dragonSplit":
            s = ev.dragonSplit
            t = team[s.parentId]
            team[s.childId] = t
            alive.add(s.childId)
            if rnd >= lo:
                st[t]["splits"] += 1
                st[t]["split_len"] += length.get(s.parentId, 0)
                if s.parentId in ready:
                    st[t]["wait"] += rnd - ready.pop(s.parentId)
                    st[t]["wait_n"] += 1
                if s.parentId not in first_split:
                    first_split[s.parentId] = rnd
                    if born.get(s.parentId, -1) >= lo:
                        st[t]["child_age"] += rnd - born[s.parentId]
                        st[t]["child_age_n"] += 1
            ready.pop(s.parentId, None)
            length[s.parentId] = len(s.parentBody)
            length[s.childId] = len(s.childBody)
            born[s.childId] = rnd
            if s.childBody:
                head[s.childId] = (s.childBody[0].x, s.childBody[0].y)
            continue
        if w == "dragonDeath":
            d = ev.dragonDeath
            t = team.get(d.id)
            if t and rnd >= lo:
                r = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body",
                     "hitHeadToHead": "h2h", "noValidAction": "idle"}.get(str(d.reason), "?")
                if r == "h2h":
                    r = "h2h_struck" if d.id == actor else "h2h_took"
                st[t]["die_" + r] += 1
                st[t]["die_len"] += length.get(d.id, 0)
            alive.discard(ev.dragonDeath.id)
            ready.pop(ev.dragonDeath.id, None)
            continue
        if w == "dragonAction":
            a = ev.dragonAction
            i = a.id
            t = team.get(i)
            if t is None:
                continue
            if a.action.which() == "move" and len(a.action.move) > 1:
                length[i] -= len(a.action.move) - 1
                if rnd >= lo:
                    st[t]["sprint"] += len(a.action.move) - 1
            if rnd < lo:
                continue
            st[t]["turns"] += 1
            if length.get(i, 0) >= 4 and a.action.which() != "split":
                st[t]["hoard"] += 1
                ready.setdefault(i, rnd)
            if pearls and i in head:
                st[t]["near"] += min(tdist(head[i], p) for p in pearls)
                st[t]["near_n"] += 1
    for t in "AB":
        st[t]["units_end"] = sum(1 for i in alive if team.get(i) == t)
    return st


ROWS = (("eat/turn", lambda s: s["pearls"] / max(1, s["turns"])),
        ("near", lambda s: s["near"] / max(1, s["near_n"])),
        ("hoard", lambda s: s["hoard"] / max(1, s["turns"])),
        ("split_len", lambda s: s["split_len"] / max(1, s["splits"])),
        ("child_age", lambda s: s["child_age"] / max(1, s["child_age_n"])),
        ("len>=4 wait", lambda s: s["wait"] / max(1, s["wait_n"])),
        ("sprint/turn", lambda s: s["sprint"] / max(1, s["turns"])),
        ("pearls", lambda s: s["pearls"]),
        ("splits", lambda s: s["splits"]),
        ("turns", lambda s: s["turns"]),
        ("units_end", lambda s: s["units_end"]),
        ("die_h2h_struck", lambda s: s["die_h2h_struck"]),
        ("die_h2h_took", lambda s: s["die_h2h_took"]),
        ("die_body", lambda s: s["die_body"]),
        ("die_self+wall", lambda s: s["die_self"] + s["die_wall"]),
        ("die_len", lambda s: s["die_len"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--from", dest="lo", type=int, default=0)
    ap.add_argument("--to", dest="hi", type=int, default=40)
    ap.add_argument("--opp", default=None)
    ap.add_argument("--map", default=None)
    ap.add_argument("--team", default="A")
    a = ap.parse_args()
    games = []  # (path, our team, result)
    for p in map(Path, a.paths):
        if p.is_dir():
            for line in (p / "results.jsonl").read_text().splitlines():
                r = json.loads(line)
                if not r.get("replay") or r["res"] not in "WLD":
                    continue
                opp = r["B"] if r["side"] == "A" else r["A"]
                if a.opp and a.opp not in opp:
                    continue
                if a.map and r["map"] != a.map:
                    continue
                games.append((p / r["replay"], r["side"], r["res"]))
        else:
            games.append((p, a.team, "?"))
    agg = collections.defaultdict(lambda: {"us": collections.Counter(), "them": collections.Counter()})
    n = collections.Counter()
    for path, me, res in games:
        st = stats(path, a.lo, a.hi)
        op = "B" if me == "A" else "A"
        key = "all"
        for k in (key, res):
            agg[k]["us"].update(st[me])
            agg[k]["them"].update(st[op])
            n[k] += 1
    print("rounds %d-%d, %d games (sums over games; ratios pooled)" % (a.lo, a.hi, n["all"]))
    cols = [k for k in ("all", "W", "L") if n[k]]
    print("%-12s" % "" + "".join("%9s %6s" % (c + ":us", "them") for c in cols))
    for name, f in ROWS:
        line = "%-12s" % name
        for c in cols:
            u, t = f(agg[c]["us"]), f(agg[c]["them"])
            if name in ("pearls", "splits", "turns", "units_end") or name.startswith("die"):
                u, t = u / n[c], t / n[c]
            line += "%9.2f %6.2f" % (u, t)
        print(line)


if __name__ == "__main__":
    main()
