"""Replay -> match metrics.  Needs `pip install pycapnp`.

Reconstructs every dragon's body from the event stream (map spawns, per-step
DragonUpdate head/tail, split bodies, deaths) so we can report what actually
happened, per team:

  units / total length / longest dragon every SAMPLE rounds
  deaths by cause and by game phase, length lost in deaths
  splits (count and child sizes), pearls eaten
  head-to-head trades (and whether they were up- or down-trades)
  CPU points per turn (p50 / p99 / max) when the replay was metered (--sandbox)

Usage as a script:  python3 replaystats.py some.replay [--team A] [--json]
"""
from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLE = 25
PHASES = ((0, 100, "early"), (100, 250, "mid"), (250, 400, "late"), (400, 501, "end"))
REASONS = ("wall", "self", "body", "h2h", "noaction")

_schema = None


def schema():
    global _schema
    if _schema is None:
        import capnp  # noqa: WPS433
        capnp.remove_import_hook()
        _schema = capnp.load(str(HERE / "replay.capnp"))
    return _schema


def phase_of(rnd):
    for lo, hi, name in PHASES:
        if lo <= rnd < hi:
            return name
    return "end"


def load(path):
    data = Path(path).read_bytes()
    return schema().Replay.from_bytes_packed(data, traversal_limit_in_words=2 ** 62)


def analyse(path):
    rep = load(path)
    team_of = {}
    body = {}
    # initial dragons from the map text: DRAGON team len x1 y1 x2 y2 ...
    nid = 0
    for line in rep.map.splitlines():
        if line.startswith("DRAGON "):
            parts = line.split()
            team = "AB"[int(parts[1])]
            n = int(parts[2])
            cells = [(int(parts[3 + 2 * i]), int(parts[4 + 2 * i])) for i in range(n)]
            team_of[nid] = team
            body[nid] = collections.deque(cells)
            nid += 1

    T = {t: dict(deaths=collections.Counter(), deaths_phase=collections.Counter(),
                 len_lost=0, splits=0, child_sizes=collections.Counter(), pearls=0,
                 h2h_up=0, h2h_even=0, h2h_down=0, curve=[], cpu=[], tle=0,
                 peak_units=0, suicides=0, h2h_struck=0, h2h_hit=0)
         for t in "AB"}
    rnd = 0
    alive = set(body)
    pending_h2h = []  # deaths this turn by head-to-head: (id, team, len)
    last_sample = -1
    actor = -1

    def sample(r):
        row = {}
        for t in "AB":
            lens = [len(body[i]) for i in alive if team_of[i] == t]
            row[t] = (len(lens), sum(lens), max(lens) if lens else 0)
            T[t]["peak_units"] = max(T[t]["peak_units"], len(lens))
        for t in "AB":
            T[t]["curve"].append((r,) + row[t])

    def flush_h2h():
        # pair head-to-head deaths: they arrive as (victim, mover) back to back
        i = 0
        while i + 1 < len(pending_h2h):
            a, b = pending_h2h[i], pending_h2h[i + 1]
            if a[1] != b[1]:
                for me, other in ((a, b), (b, a)):
                    if me[2] < other[2]:
                        T[me[1]]["h2h_up"] += 1
                    elif me[2] == other[2]:
                        T[me[1]]["h2h_even"] += 1
                    else:
                        T[me[1]]["h2h_down"] += 1
            i += 2
        del pending_h2h[:]

    reason_names = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body",
                    "hitHeadToHead": "h2h", "noValidAction": "noaction"}
    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rnd = ev.roundStart.round
            if rnd // SAMPLE != last_sample:
                last_sample = rnd // SAMPLE
                sample(rnd)
        elif w == "turnStart":
            flush_h2h()
            actor = ev.turnStart.id
        elif w == "dragonUpdate":
            u = ev.dragonUpdate
            i = u.id
            if i not in body:
                continue
            b = body[i]
            h = (u.head.x, u.head.y)
            t = (u.tail.x, u.tail.y)
            if not b or b[0] != h:
                b.appendleft(h)
            before = len(b)
            while len(b) > 1 and b[-1] != t:
                b.pop()
            # a step that did not move the tail ate a pearl
            if before == len(b) and len(b) > 1:
                pass
        elif w == "tileChange":
            tc = ev.tileChange
            if not tc.hasPearl:
                # pearl removed: eaten by the head standing there
                if actor in alive and actor in team_of:
                    T[team_of[actor]]["pearls"] += 1
        elif w == "dragonSplit":
            s = ev.dragonSplit
            team = "AB"[0 if str(s.team) == "a" else 1]
            team_of[s.childId] = team
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
            alive.add(s.childId)
            T[team]["splits"] += 1
            T[team]["child_sizes"][len(s.childBody)] += 1
        elif w == "dragonDeath":
            d = ev.dragonDeath
            i = d.id
            team = team_of.get(i, "?")
            reason = reason_names.get(str(d.reason), str(d.reason))
            ln = len(body.get(i, ()))
            if team in T:
                T[team]["deaths"][reason] += 1
                T[team]["deaths_phase"][phase_of(rnd)] += 1
                T[team]["len_lost"] += ln
                if reason == "h2h":
                    pending_h2h.append((i, team, ln))
                    if i == actor:
                        T[team]["h2h_struck"] += 1   # we moved onto their head
                    else:
                        T[team]["h2h_hit"] += 1      # they moved onto ours
            alive.discard(i)
        elif w == "dragonAction":
            a = ev.dragonAction
            team = team_of.get(a.id)
            if team:
                if a.tle:
                    T[team]["tle"] += 1
                if a.has("instructions") if hasattr(a, "has") else True:
                    try:
                        c = a.instructions.count
                        if c:
                            T[team]["cpu"].append(c)
                    except Exception:
                        pass
                try:
                    if a.action.which() == "suicide":
                        T[team]["suicides"] += 1
                except Exception:
                    pass
    flush_h2h()
    sample(rnd + 1)

    res = rep.result
    try:
        winner = str(res.winner).upper()
    except Exception:
        winner = "draw"
    if res.which() == "noWinner":
        winner = "draw"
    out = dict(botA=rep.botA, botB=rep.botB, rounds=rnd + 1, winner=winner,
               end=str(res.endReason),
               standing={"A": dict(units=res.teamA.dragonCount, longest=res.teamA.longestDragon,
                                   total=res.teamA.totalLength),
                         "B": dict(units=res.teamB.dragonCount, longest=res.teamB.longestDragon,
                                   total=res.teamB.totalLength)},
               teams={})
    for t in "AB":
        d = T[t]
        cpu = sorted(d["cpu"])
        out["teams"][t] = dict(
            deaths=dict(d["deaths"]), deaths_phase=dict(d["deaths_phase"]),
            len_lost=d["len_lost"], splits=d["splits"], child_sizes=dict(d["child_sizes"]),
            pearls=d["pearls"], h2h_up=d["h2h_up"], h2h_even=d["h2h_even"],
            h2h_down=d["h2h_down"], h2h_struck=d["h2h_struck"], h2h_hit=d["h2h_hit"], peak_units=d["peak_units"], tle=d["tle"],
            suicides=d["suicides"], curve=d["curve"],
            cpu_p50=cpu[len(cpu) // 2] if cpu else 0,
            cpu_p99=cpu[int(len(cpu) * 0.99)] if cpu else 0,
            cpu_max=cpu[-1] if cpu else 0)
    return out


def describe(stats, team="A"):
    other = "B" if team == "A" else "A"
    me, op = stats["teams"][team], stats["teams"][other]
    lines = []
    lines.append("%s (team %s) vs %s: winner=%s end=%s rounds=%d" % (
        stats["bot" + team], team, stats["bot" + other], stats["winner"], stats["end"],
        stats["rounds"]))
    lines.append("final: us %s | them %s" % (stats["standing"][team], stats["standing"][other]))
    lines.append("round  us(units,total,longest)   them(units,total,longest)")
    for a, b in zip(me["curve"], op["curve"]):
        lines.append("%4d   %3d %4d %3d            %3d %4d %3d" % (a[0], a[1], a[2], a[3], b[1], b[2], b[3]))
    for name, d in (("us", me), ("them", op)):
        lines.append("%-4s deaths=%s phase=%s len_lost=%d splits=%d sizes=%s pearls=%d "
                     "h2h up/even/down=%d/%d/%d struck/hit=%d/%d cpu p99=%.1fM max=%.1fM tle=%d" % (
                         name, d["deaths"], d["deaths_phase"], d["len_lost"], d["splits"],
                         d["child_sizes"], d["pearls"], d["h2h_up"], d["h2h_even"],
                         d["h2h_down"], d["h2h_struck"], d["h2h_hit"], d["cpu_p99"] / 1e6, d["cpu_max"] / 1e6, d["tle"]))
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("--team", default="A")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    s = analyse(a.replay)
    if a.json:
        print(json.dumps(s, indent=1))
    else:
        print(describe(s, a.team))
