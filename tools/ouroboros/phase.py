#!/usr/bin/env python3
"""What separates our wins from our losses in one phase of the game?

For every kept replay of a run, count events inside a round window for us
and for them (pearls eaten, splits, deaths by cause, head-to-heads we struck
or took, sprint steps, units at the window's end), then average separately
over won and lost games.  Needs the run to have kept replays (--keep all).

    python3 tools/ouroboros/phase.py RUN_DIR [--from 0 --to 50] [--cand NAME]
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

REASON = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body",
          "hitHeadToHead": "h2h", "noValidAction": "noaction"}


def window_stats(path, lo, hi):
    rep = R.load(path)
    m = load_map(rep.map)
    team = {i: t for i, (t, c) in enumerate(m["dragons"])}
    alive = set(team)
    st = {t: collections.Counter() for t in "AB"}
    rnd = 0
    actor = None
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
        if w == "dragonSplit":
            s = ev.dragonSplit
            team[s.childId] = team[s.parentId]
            alive.add(s.childId)
            if rnd >= lo:
                st[team[s.parentId]]["splits"] += 1
            continue
        if w == "dragonDeath":
            d = ev.dragonDeath
            t = team.get(d.id)
            alive.discard(d.id)
            if t and rnd >= lo:
                r = REASON.get(str(d.reason), "?")
                st[t]["die_" + r] += 1
                if r == "h2h":
                    st[t]["h2h_took" if d.id != actor else "h2h_struck"] += 1
            continue
        if rnd < lo:
            continue
        if w == "tileChange" and not ev.tileChange.hasPearl and actor in team:
            st[team[actor]]["pearls"] += 1
        elif w == "dragonAction":
            a = ev.dragonAction
            t = team.get(a.id)
            if t:
                st[t]["turns"] += 1
                if a.action.which() == "move":
                    st[t]["sprint_steps"] += len(a.action.move) - 1
    for t in "AB":
        st[t]["units_end"] = sum(1 for i in alive if team.get(i) == t)
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--from", dest="lo", type=int, default=0)
    ap.add_argument("--to", dest="hi", type=int, default=50)
    ap.add_argument("--cand", default=None)
    a = ap.parse_args()
    run = Path(a.run)
    agg = {"W": collections.Counter(), "L": collections.Counter()}
    n = collections.Counter()
    for line in (run / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["res"] not in "WL" or not r.get("replay"):
            continue
        if a.cand and r["cand"] != a.cand:
            continue
        st = window_stats(run / r["replay"], a.lo, a.hi)
        me = r["side"]
        op = "B" if me == "A" else "A"
        for k, v in st[me].items():
            agg[r["res"]]["us_" + k] += v
        for k, v in st[op].items():
            agg[r["res"]]["them_" + k] += v
        n[r["res"]] += 1
    keys = sorted(set(k[3:] for k in agg["W"]) | set(k[3:] for k in agg["L"]) |
                  set(k[5:] for k in agg["W"] if k.startswith("them_")))
    keys = sorted(set(k.split("_", 1)[1] for res in agg for k in agg[res]))
    print("rounds %d-%d   wins n=%d   losses n=%d   (per game averages)" % (a.lo, a.hi, n["W"], n["L"]))
    print("%-14s %8s %8s   %8s %8s" % ("", "W: us", "W: them", "L: us", "L: them"))
    for k in keys:
        row = []
        for res in "WL":
            d = max(1, n[res])
            row += [agg[res]["us_" + k] / d, agg[res]["them_" + k] / d]
        print("%-14s %8.1f %8.1f   %8.1f %8.1f" % (k, *row))


if __name__ == "__main__":
    main()
