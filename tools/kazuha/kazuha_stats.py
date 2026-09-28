#!/usr/bin/env python3
"""kazuha_stats: activation-contract stats from a replay.

Usage: kazuha_stats.py A|B FILE.replay
Curves/deaths come from replaystats.analyse (exact body reconstruction); the
light pass here adds ACT tag counts, certificate delivery (backward-ray pings
hitting a child on its first turn), newborn deaths within 10 rounds, splits
by r100, and the team's first-pearl round.
Prints one JSON line.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ouroboros"))
import replaystats  # noqa: E402


def main():
    team = sys.argv[1].upper()
    path = sys.argv[2]
    rep = replaystats.load(path)
    st = replaystats.analyse(path)
    W = H = 0
    for line in rep.map.splitlines():
        if line.startswith("MAP "):
            W, H = int(line.split()[1]), int(line.split()[2])

    born = {}
    dead = {}
    team_of = {}
    nid = 0
    for line in rep.map.splitlines():
        if line.startswith("DRAGON "):
            p = line.split()
            team_of[nid] = "AB"[int(p[1])]
            born[nid] = 0
            nid += 1
    heads = {}
    act_counts = {}
    act_rounds = {}
    cert_pings = 0
    first_pearl = None
    rnd = 0
    ours = lambda i: team_of.get(i) == team  # noqa: E731
    for e in rep.events:
        w = e.which()
        if w == "roundStart":
            rnd = e.roundStart.round
        elif w == "dragonSplit":
            s = e.dragonSplit
            born[s.childId] = rnd
            team_of[s.childId] = "A" if s.team == "a" else "B"
        elif w == "dragonDeath":
            d = e.dragonDeath
            dead[d.id] = (rnd, str(d.reason))
        elif w == "dragonUpdate":
            u = e.dragonUpdate
            heads[u.id] = u.head.y * W + u.head.x
        elif w == "sonarPing":
            p = e.sonarPing
            if p.which() == "hitId" and born.get(p.hitId) == rnd and ours(p.senderId):
                cert_pings += 1
        elif w == "dragonLog":
            t = e.dragonLog.text
            if t.startswith("ACT:") and ours(e.dragonLog.id):
                tag = t[4:]
                act_counts[tag] = act_counts.get(tag, 0) + 1
                act_rounds.setdefault(tag, []).append(rnd)
        elif w == "tileChange" and first_pearl is None:
            t = e.tileChange
            if not t.hasPearl:
                c = t.tile.y * W + t.tile.x
                for i, hc in heads.items():
                    if hc == c and ours(i):
                        first_pearl = rnd
                        break

    curve = st["teams"][team]["curve"]  # (round, units, total, longest) samples
    at = lambda r: next((row for row in curve if row[0] >= r), curve[-1])  # noqa: E731
    our_ids = [i for i in born if ours(i)]
    births = sum(1 for i in our_ids if born[i] > 0)
    nb = sum(1 for i in our_ids
             if born[i] > 0 and i in dead and dead[i][0] - born[i] <= 10)
    splits100 = sum(1 for i in our_ids if 0 < born[i] <= 100)
    d = st["teams"][team]["deaths"]
    turns = 0
    for row in curve:
        turns += row[1]  # total length proxy is wrong; use dragon-rounds below
    dragon_rounds = sum(1 for i in born
                        for r in range(0, (dead.get(i, (501,))[0]) if i in dead else 501)
                        if r >= born[i]) if born else 0
    out = dict(
        replay=str(path), team=team,
        winner=st["standing"]["A"] if team == "A" else st["standing"]["B"],
        units_r100=at(100)[1], units_r250=at(250)[1],
        longest_r400=at(400)[3], longest_r499=at(499)[3],
        final=curve[-1],
        splits_r0_r100=splits100,
        act_counts=act_counts,
        act_windows={k: [min(v), max(v)] for k, v in act_rounds.items()},
        cert_pings_child_first_turn=cert_pings,
        births=births, newborn_deaths_le_10=nb,
        newborn_death_pct=round(100.0 * nb / births, 1) if births else None,
        wall_self=d.get("wall", 0) + d.get("self", 0),
        deaths=d,
        first_pearl_round=first_pearl,
        pearls=st["teams"][team]["pearls"],
    )
    print(json.dumps(out))


if __name__ == "__main__":
    main()
