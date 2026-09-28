"""ouroboros-s02 replay analyser: pearl economy and death anatomy per team.

Pearl supply: bed spawns vs corpse drops, who ate them (A/B), how long they sat,
uneaten at end.  Deaths: cause x (terrain / own body / ally / enemy) x portal
first step x age bucket x round phase.

Usage: python3 econ2.py REPLAY [--team A]
Reuses the replay schema and map parser of tools/ouroboros (Claude lineage).
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

REASONS = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body",
           "hitHeadToHead": "h2h", "noValidAction": "noaction"}
DN = {"north": 0, "east": 1, "south": 2, "west": 3}


DLIST = []
LOGS = []


def analyse(path):
    rep = replaystats.load(path)
    mp = load_map(rep.map)
    W, H = mp["W"], mp["H"]
    NC = W * H
    ph, pv = mp["portal_h"], mp["portal_v"]
    ends = collections.defaultdict(list)
    for (x, y), pid in ph.items():
        ends[pid].append(y * W + x)
    for (x, y), pid in pv.items():
        ends[pid].append(NC + y * W + x)

    def nbr(c):
        x, y = c % W, c // W
        return ((y - 1) % H * W + x, y * W + (x + 1) % W, (y + 1) % H * W + x, y * W + (x - 1) % W)

    def ekey(c, d):
        if d == 0:
            return c
        if d == 2:
            return nbr(c)[2]
        if d == 3:
            return NC + c
        return NC + nbr(c)[1]

    def pid_of(k):
        if k < NC:
            return ph.get((k % W, k // W))
        k -= NC
        return pv.get((k % W, k // W))

    def step(c, d):
        k = ekey(c, d)
        p = pid_of(k)
        if p is None:
            return nbr(c)[d], False
        e = ends[p]
        if len(e) < 2:
            return nbr(c)[d], True
        pk = e[0] if e[1] == k else e[1]
        if pk >= NC:
            pc = pk - NC
            return (pc if d == 1 else nbr(pc)[3]), True
        return (pk if d == 2 else nbr(pk)[0]), True

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
    T = {t: dict(bed_eaten=0, corpse_eaten=0, bed_eaten_r100=0, deaths=collections.Counter(),
                 bed_latency=[], bed_latency_r100=[], units_peak=0) for t in "AB"}
    pearl = {}   # cell -> (round appeared, kind)
    del DLIST[:]
    del LOGS[:]
    spawned = collections.Counter()
    rnd = 0
    actor = -1
    last_move = {}
    in_death = False
    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rnd = ev.roundStart.round
            for t in "AB":
                n = sum(1 for i in alive if team_of[i] == t)
                if n > T[t]["units_peak"]:
                    T[t]["units_peak"] = n
        elif w == "turnStart":
            actor = ev.turnStart.id
            in_death = False
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
            if tc.hasPearl:
                kind = "corpse" if in_death else "bed"
                pearl[cell] = (rnd, kind)
                spawned[kind] += 1
                if rnd < 100:
                    spawned[kind + "_r100"] += 1
            else:
                pr = pearl.pop(cell, None)
                if actor in team_of and pr is not None:
                    tm = team_of[actor]
                    if pr[1] == "bed":
                        T[tm]["bed_eaten"] += 1
                        T[tm]["bed_latency"].append(rnd - pr[0])
                        if pr[0] < 100:
                            T[tm]["bed_latency_r100"].append(rnd - pr[0])
                        if rnd < 100:
                            T[tm]["bed_eaten_r100"] += 1
                    else:
                        T[tm]["corpse_eaten"] += 1
        elif w == "dragonSplit":
            s = ev.dragonSplit
            team = "A" if str(s.team) == "a" else "B"
            team_of[s.childId] = team
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
            alive.add(s.childId)
            born[s.childId] = rnd
        elif w == "dragonDeath":
            d = ev.dragonDeath
            i = d.id
            in_death = True
            team = team_of.get(i)
            reason = REASONS.get(str(d.reason), str(d.reason))
            if team:
                lm = last_move.get(i)
                via = "?"
                owner = "?"
                if lm and lm[0] == rnd:
                    hx, hy = lm[1]
                    tgt, portal = step(hy * W + hx, lm[2])
                    via = "portal" if portal else "plain"
                    tx, ty = tgt % W, tgt // W
                    if reason in ("body", "h2h", "self"):
                        owner = "none"
                        for j in alive:
                            if (tx, ty) in body[j]:
                                owner = "self" if j == i else ("ally" if team_of[j] == team else "enemy")
                                break
                elif reason == "noaction":
                    via = "-"
                age = rnd - born.get(i, 0)
                ab = "newborn" if born.get(i, 0) > 0 and age <= 10 else "grown"
                ph_ = "r0-100" if rnd < 100 else "r100-250" if rnd < 250 else "r250+"
                L = len(body.get(i, ()))
                key = "%s|%s|%s|%s|%s|L%s" % (reason, owner, via, ab, ph_, min(L, 5))
                T[team]["deaths"][key] += 1
                DLIST.append((team, i, rnd, key))
            alive.discard(i)
        elif w == "dragonLog":
            LOGS.append((ev.dragonLog.id, rnd, ev.dragonLog.text))
        elif w == "dragonAction":
            a = ev.dragonAction
            try:
                if a.action.which() == "move":
                    mv = list(a.action.move)
                    b = body.get(a.id)
                    if mv and b:
                        last_move[a.id] = (rnd, b[0], DN.get(str(mv[0]), 0))
            except Exception:
                pass
    out = dict(map=[l for l in rep.map.splitlines() if l.startswith("MAP_NAME")][:1],
               spawned=dict(spawned), uneaten_end=collections.Counter(k for _, k in pearl.values()),
               teams={})
    for t in "AB":
        d = T[t]
        lat = sorted(d["bed_latency"])
        out["teams"][t] = dict(bed_eaten=d["bed_eaten"], corpse_eaten=d["corpse_eaten"],
                               bed_eaten_r100=d["bed_eaten_r100"], units_peak=d["units_peak"],
                               bed_latency_med=lat[len(lat) // 2] if lat else None,
                               bed_latency_r100=sorted(d["bed_latency_r100"]),
                               deaths=dict(d["deaths"]))
    return out


if __name__ == "__main__":
    print(json.dumps(analyse(sys.argv[1]), indent=1))
