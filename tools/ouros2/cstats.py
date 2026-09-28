"""Chaewon replay analyser: contract and outcome statistics per team.

Extends tools/ouroboros/replaystats.py (same body reconstruction) with the
S1 measurement protocol (build prompt S1 §7.3/§7.4):

  units/total/longest at r100, r250, r400, r499
  wall+self deaths per 1k dragon-turns, newborn deaths within 10 rounds
  (non-voluntary), child first-pearl latency, splits per decision r0-100
  ACT:<tag> markers from dragon LOG lines, by round
  conversion funnel: dissolves -> corpse pearls -> eaten by a crown within 2
  rounds -> crown alive at the end

Usage: python3 cstats.py REPLAY [--team A] [--json]
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "ouroboros"))
import replaystats  # noqa: E402
from mapview import load_map  # noqa: E402

CHECK_ROUNDS = (25, 50, 100, 250, 400, 499)
REASONS = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body",
           "hitHeadToHead": "h2h", "noValidAction": "noaction"}


def analyse(path):
    rep = replaystats.load(path)
    team_of, body, born = {}, {}, {}
    nid = 0
    for line in rep.map.splitlines():
        if line.startswith("DRAGON "):
            p = line.split()
            n = int(p[2])
            team_of[nid] = "AB"[int(p[1])]
            body[nid] = collections.deque((int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n))
            born[nid] = 0
            nid += 1
    alive = set(body)
    mp = load_map(rep.map)
    MW, MH = mp["W"], mp["H"]
    ph, pv = mp["portal_h"], mp["portal_v"]

    def crosses_portal(x, y, d):
        if d == 0:
            return (x, y) in ph
        if d == 2:
            return (x, (y + 1) % MH) in ph
        if d == 3:
            return (x, y) in pv
        return ((x + 1) % MW, y) in pv
    last_move = {}  # id -> (round, head, first dir)
    DN = {"north": 0, "east": 1, "south": 2, "west": 3}
    T = {t: dict(deaths=collections.Counter(), turns=0, turns_r100=0, splits_r100=0, splits=0,
                 births=0, newborn_deaths10=0, first_pearl=[], act=collections.defaultdict(list),
                 at={}, cpu=[], tle=0, crowns=set(), diss=0, diss_pearls=0, diss_eaten_crown=0,
                 diss_eaten_ally=0, pearls=0, noaction_unmarked=0, portal_deaths=0,
                 pearls_r100=0, team_first_pearl=None, deaths_r100=0, portal_deaths_r100=0,
                 portal_steps=0)
         for t in "AB"}
    first_pearl_done = set()
    rnd = 0
    actor = -1
    corpse = {}  # cell -> (team, round dropped, voluntary dissolve?)
    diss_pending = {}  # id -> round of ACT:diss
    last_act = {}      # id -> round of its last salv/diss marker
    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rnd = ev.roundStart.round
            if rnd in CHECK_ROUNDS:
                for t in "AB":
                    lens = [len(body[i]) for i in alive if team_of[i] == t]
                    T[t]["at"][rnd] = (len(lens), sum(lens), max(lens) if lens else 0)
        elif w == "turnStart":
            actor = ev.turnStart.id
        elif w == "dragonUpdate":
            u = ev.dragonUpdate
            b = body.get(u.id)
            if b is None:
                continue
            h = (u.head.x, u.head.y)
            t = (u.tail.x, u.tail.y)
            if not b or b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != t:
                b.pop()
        elif w == "tileChange":
            tc = ev.tileChange
            cell = (tc.tile.x, tc.tile.y)
            if not tc.hasPearl:
                if actor in alive and actor in team_of:
                    tm = team_of[actor]
                    T[tm]["pearls"] += 1
                    if rnd < 100:
                        T[tm]["pearls_r100"] += 1
                    if T[tm]["team_first_pearl"] is None:
                        T[tm]["team_first_pearl"] = rnd
                    if actor not in first_pearl_done:
                        first_pearl_done.add(actor)
                        if born.get(actor, 0) > 0:
                            T[tm]["first_pearl"].append(rnd - born[actor])
                    c = corpse.pop(cell, None)
                    if c is not None and c[2] and c[0] == tm and rnd - c[1] <= 2:
                        T[tm]["diss_eaten_ally"] += 1
                        if actor in T[tm]["crowns"]:
                            T[tm]["diss_eaten_crown"] += 1
        elif w == "dragonSplit":
            s = ev.dragonSplit
            team = "A" if str(s.team) == "a" else "B"
            team_of[s.childId] = team
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
            alive.add(s.childId)
            born[s.childId] = rnd
            T[team]["splits"] += 1
            T[team]["births"] += 1
            if rnd < 100:
                T[team]["splits_r100"] += 1
        elif w == "dragonDeath":
            d = ev.dragonDeath
            i = d.id
            team = team_of.get(i)
            reason = REASONS.get(str(d.reason), str(d.reason))
            if team:
                T[team]["deaths"][reason] += 1
                lm = last_move.get(i)
                if reason in ("body", "self", "h2h") and lm and lm[0] == rnd and lm[1] and \
                        crosses_portal(lm[1][0], lm[1][1], lm[2]):
                    T[team]["portal_deaths"] += 1
                    if rnd < 100:
                        T[team]["portal_deaths_r100"] += 1
                if rnd < 100:
                    T[team]["deaths_r100"] += 1
                if born.get(i, 0) > 0 and rnd - born[i] <= 10 and reason != "noaction" \
                        and i not in diss_pending:
                    T[team]["newborn_deaths10"] += 1
                if reason == "noaction" and last_act.get(i) != rnd:
                    T[team]["noaction_unmarked"] += 1
                vol = i in diss_pending
                if vol:
                    T[team]["diss"] += 1
                    cells = list(body.get(i, ()))[::2]
                    T[team]["diss_pearls"] += len(cells)
                    for c in cells:
                        corpse[c] = (team, rnd, True)
            alive.discard(i)
        elif w == "dragonAction":
            a = ev.dragonAction
            team = team_of.get(a.id)
            if team:
                T[team]["turns"] += 1
                try:
                    if a.action.which() == "move":
                        mv = list(a.action.move)
                        b = body.get(a.id)
                        if mv and b:
                            last_move[a.id] = (rnd, b[0], DN.get(str(mv[0]), 0))
                            if crosses_portal(b[0][0], b[0][1], DN.get(str(mv[0]), 0)):
                                T[team]["portal_steps"] += 1
                except Exception:
                    pass
                if rnd < 100:
                    T[team]["turns_r100"] += 1
                if a.tle:
                    T[team]["tle"] += 1
                try:
                    c = a.instructions.count
                    if c:
                        T[team]["cpu"].append(c)
                except Exception:
                    pass
        elif w == "dragonLog":
            lg = ev.dragonLog
            team = team_of.get(lg.id)
            if not team:
                continue
            for tok in lg.text.split():
                if tok.startswith("ACT:"):
                    tag = tok[4:]
                    T[team]["act"][tag].append(rnd)
                    if tag in ("salv", "diss"):
                        last_act[lg.id] = rnd
                    if tag == "crown":
                        T[team]["crowns"].add(lg.id)
                    elif tag == "diss":
                        diss_pending[lg.id] = rnd
    for t in "AB":
        lens = [len(body[i]) for i in alive if team_of[i] == t]
        T[t]["at"].setdefault(499, (len(lens), sum(lens), max(lens) if lens else 0))
    res = rep.result
    winner = "draw" if res.which() == "noWinner" else str(res.winner).upper()
    out = dict(botA=rep.botA, botB=rep.botB, rounds=rnd + 1, winner=winner, end=str(res.endReason),
               standing={"A": dict(units=res.teamA.dragonCount, longest=res.teamA.longestDragon,
                                   total=res.teamA.totalLength),
                         "B": dict(units=res.teamB.dragonCount, longest=res.teamB.longestDragon,
                                   total=res.teamB.totalLength)}, teams={})
    for t in "AB":
        d = T[t]
        cpu = sorted(d["cpu"])
        crown_alive = any(c in alive for c in d["crowns"])
        fp = sorted(d["first_pearl"])
        ws = d["deaths"]["wall"] + d["deaths"]["self"]
        out["teams"][t] = dict(
            deaths=dict(d["deaths"]), turns=d["turns"],
            wall_self_per_1k=1000.0 * ws / max(1, d["turns"]),
            splits=d["splits"], splits_per_decision_r0_r100=d["splits_r100"] / max(1, d["turns_r100"]),
            births=d["births"], newborn_deaths10=d["newborn_deaths10"],
            first_pearl_median=fp[len(fp) // 2] if fp else None,
            at={str(k): v for k, v in d["at"].items()},
            act={k: len(v) for k, v in d["act"].items()},
            act_rounds={k: v for k, v in d["act"].items()},
            crowns=len(d["crowns"]), crown_alive_end=crown_alive,
            diss=d["diss"], diss_pearls=d["diss_pearls"], diss_eaten_crown=d["diss_eaten_crown"],
            diss_eaten_ally=d["diss_eaten_ally"], pearls=d["pearls"],
            noaction_unmarked=d["noaction_unmarked"], portal_deaths=d["portal_deaths"],
            pearls_r100=d["pearls_r100"], team_first_pearl=d["team_first_pearl"],
            deaths_r100=d["deaths_r100"], portal_deaths_r100=d["portal_deaths_r100"],
            portal_steps=d["portal_steps"],
            tle=d["tle"], cpu_p99=cpu[int(len(cpu) * 0.99)] if cpu else 0,
            cpu_max=cpu[-1] if cpu else 0)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("--team")
    a = ap.parse_args()
    s = analyse(a.replay)
    if a.team:
        s["teams"] = {a.team: s["teams"][a.team]}
    for t in s["teams"].values():
        t.pop("act_rounds", None)
    print(json.dumps(s, indent=1))
