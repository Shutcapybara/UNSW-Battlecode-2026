"""Replay -> Yeji contract statistics (own actions + outcome curve), per team.

Needs pycapnp.  Reuses the capnp schema of tools/ouroboros.  Body
reconstruction follows tools/ouroboros/replaystats.py.

Per team:
  units/total/longest at r100, r250, r400, r499 (start of round)
  deaths by reason, wall_self per 1k dragon-turns, dragon-turns
  births, newborn deaths within 10 rounds, child first-pearl latency (median)
  ACT:<tag> counts by round (from LOG lines)            -> activation contract
  dissolve funnel: diss deaths, corpse pearls, eaten by ally / by crown in 2 rounds,
                   crown ids (ACT:crown), crown alive at end
  cpu p50/p99/max (metered replays only)

Usage: python3 ystats.py REPLAY [--json]
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / "ouroboros" / "replay.capnp"
_schema = None
CHECK = (100, 250, 400, 499)


def schema():
    global _schema
    if _schema is None:
        import capnp
        capnp.remove_import_hook()
        _schema = capnp.load(str(SCHEMA))
    return _schema


def load(path):
    return schema().Replay.from_bytes_packed(Path(path).read_bytes(),
                                             traversal_limit_in_words=2 ** 62)


def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def analyse(path):
    rep = load(path)
    team_of, body = {}, {}
    nid = 0
    for line in rep.map.splitlines():
        if line.startswith("DRAGON "):
            p = line.split()
            n = int(p[2])
            team_of[nid] = "AB"[int(p[1])]
            body[nid] = collections.deque((int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n))
            nid += 1
    born = {i: 0 for i in body}
    first_pearl = {}
    alive = set(body)
    T = {t: dict(deaths=collections.Counter(), turns=0, births=0, nb_dead10=0,
                 act=collections.Counter(), act_rounds=collections.defaultdict(list),
                 cpu=[], tle=0, pearls=0, curve={}, crowns=set(),
                 diss_ids=set(), diss_deaths=0, corpse=0, corpse_ally=0, corpse_crown=0,
                 child_lat=[], first_pearl=None, sw=0, sw_turns=0)
         for t in "AB"}
    rnd = 0
    actor = -1
    diss_pending = {}       # dragon id -> round of ACT:diss
    corpse_cells = {}       # (x,y) -> (team, round dropped)
    dying_actor_turn = None

    def sample(r):
        for t in "AB":
            lens = [len(body[i]) for i in alive if team_of.get(i) == t]
            T[t]["curve"][r] = (len(lens), sum(lens), max(lens) if lens else 0)

    reason_names = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body",
                    "hitHeadToHead": "h2h", "noValidAction": "noaction"}
    died_this_turn = None
    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rnd = ev.roundStart.round
            if rnd in CHECK:
                sample(rnd)
            # expire corpse pearls
            for c in [c for c, v in corpse_cells.items() if rnd - v[1] > 2]:
                del corpse_cells[c]
        elif w == "turnStart":
            actor = ev.turnStart.id
            died_this_turn = None
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
                if died_this_turn is not None and died_this_turn in T[team_of.get(died_this_turn, "A")]["diss_ids"]:
                    tm = team_of[died_this_turn]
                    corpse_cells[cell] = (tm, rnd)
                    T[tm]["corpse"] += 1
            else:
                if actor in alive and actor in team_of:
                    tm = team_of[actor]
                    T[tm]["pearls"] += 1
                    if T[tm]["first_pearl"] is None:
                        T[tm]["first_pearl"] = rnd
                    if actor not in first_pearl:
                        first_pearl[actor] = rnd
                        if born.get(actor, 0) > 0:
                            T[tm]["child_lat"].append(rnd - born[actor])
                    cc = corpse_cells.pop(cell, None)
                    if cc is not None and cc[0] == tm:
                        T[tm]["corpse_ally"] += 1
                        if actor in T[tm]["crowns"]:
                            T[tm]["corpse_crown"] += 1
        elif w == "dragonSplit":
            s = ev.dragonSplit
            tm = "A" if str(s.team) == "a" else "B"
            team_of[s.childId] = tm
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
            alive.add(s.childId)
            born[s.childId] = rnd
            T[tm]["births"] += 1
        elif w == "dragonDeath":
            d = ev.dragonDeath
            i = d.id
            tm = team_of.get(i)
            if tm:
                T[tm]["deaths"][reason_names.get(str(d.reason), str(d.reason))] += 1
                if born.get(i, 0) > 0 and rnd - born[i] <= 10:
                    T[tm]["nb_dead10"] += 1
                if i in T[tm]["diss_ids"] and i == actor:
                    T[tm]["diss_deaths"] += 1
            if i == actor:
                died_this_turn = i
            alive.discard(i)
        elif w == "dragonAction":
            a = ev.dragonAction
            tm = team_of.get(a.id)
            if tm:
                T[tm]["turns"] += 1
                if a.tle:
                    T[tm]["tle"] += 1
                try:
                    c = a.instructions.count
                    if c:
                        T[tm]["cpu"].append(c)
                except Exception:
                    pass
        elif w == "dragonLog":
            lg = ev.dragonLog
            tm = team_of.get(lg.id)
            if not tm:
                continue
            for tok in lg.text.split():
                if tok.startswith("ACT:"):
                    tag = tok[4:]
                    if tag.startswith("sw"):
                        a, _, b = tag[2:].partition("_")
                        T[tm]["sw"] += int(a)
                        T[tm]["sw_turns"] += int(b or 0)
                        continue
                    T[tm]["act"][tag] += 1
                    T[tm]["act_rounds"][tag].append(rnd)
                    if tag == "crown":
                        T[tm]["crowns"].add(lg.id)
                    elif tag == "diss":
                        T[tm]["diss_ids"].add(lg.id)
    sample(500)
    res = rep.result
    winner = "draw" if res.which() == "noWinner" else str(res.winner).upper()
    out = dict(botA=rep.botA, botB=rep.botB, rounds=rnd + 1, winner=winner, end=str(res.endReason),
               standing={"A": dict(units=res.teamA.dragonCount, longest=res.teamA.longestDragon,
                                   total=res.teamA.totalLength),
                         "B": dict(units=res.teamB.dragonCount, longest=res.teamB.longestDragon,
                                   total=res.teamB.totalLength)},
               teams={})
    for t in "AB":
        d = T[t]
        cpu = sorted(d["cpu"])
        ws = d["deaths"]["wall"] + d["deaths"]["self"]
        cur = d["curve"]
        o = dict(deaths=dict(d["deaths"]), turns=d["turns"],
                 wall_self_per_1k=round(1000.0 * ws / max(1, d["turns"]), 2),
                 births=d["births"], nb_dead10=d["nb_dead10"],
                 child_first_pearl_med=median(d["child_lat"]), first_pearl=d["first_pearl"],
                 pearls=d["pearls"], act=dict(d["act"]),
                 act_windows={k: [min(v), max(v)] for k, v in d["act_rounds"].items()},
                 diss_deaths=d["diss_deaths"], corpse=d["corpse"], corpse_ally=d["corpse_ally"],
                 corpse_crown=d["corpse_crown"],
                 crown_alive_end=any(c in alive for c in d["crowns"]),
                 sw_per_100=round(100.0 * d["sw"] / d["sw_turns"], 2) if d["sw_turns"] else None,
                 tle=d["tle"], cpu_n=len(cpu),
                 cpu_p50=cpu[len(cpu) // 2] if cpu else 0,
                 cpu_p99=cpu[int(len(cpu) * 0.99)] if cpu else 0,
                 cpu_max=cpu[-1] if cpu else 0)
        for r in CHECK:
            if r in cur:
                o["units_r%d" % r], o["total_r%d" % r], o["longest_r%d" % r] = cur[r]
        out["teams"][t] = o
    return out


if __name__ == "__main__":
    st = analyse(sys.argv[1])
    print(json.dumps(st, indent=1 if "--json" not in sys.argv else None, default=str))
