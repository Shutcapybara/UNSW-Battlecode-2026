"""sakura funnel: the conversion funnel (7.4) from kept replays.

For each game, after the dissolve onset:
  eligible feeders  - dragon-rounds alive at L <= 3 (the pool that could feed)
  feeders that acted - ACT:diss events
  mass delivered     - corpse pearls from a dissolve eaten by a teammate <= 2 rounds later
  crown survived     - the team's longest dragon at the end is alive
  final margin       - our longest - their longest at the final sample

    python3 tools/sakura/funnel.py DIR1 [DIR2 ...]   # dirs of kept replays
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "ouroboros"))
import replaystats  # noqa: E402

ONSET = {"portals": 300, "slithery_fight": 300}
FEED_MAX_LEN = 3


def funnel(path, mapname):
    rep = replaystats.load(str(path))
    team_of = {}
    body = {}
    nid = 0
    n_init = 0
    for line in rep.map.splitlines():
        if line.startswith("DRAGON "):
            parts = line.split()
            team = "AB"[int(parts[1])]
            n = int(parts[2])
            cells = [(int(parts[3 + 2 * i]), int(parts[4 + 2 * i])) for i in range(n)]
            team_of[nid] = team
            body[nid] = collections.deque(cells)
            nid += 1
            n_init += 1
    onset = ONSET.get(mapname, 400)
    alive = set(body)
    born = {}
    rnd = 0
    actor = -1
    diss_round = {}         # id -> round of its ACT:diss
    per_diss = []           # (team, round, set(cells), eater counts)
    eligible = collections.Counter()   # team -> dragon-rounds
    acted = collections.Counter()      # team -> ACT:diss count
    for ev in rep.events:
        w = ev.which()
        if w == "roundStart":
            rnd = ev.roundStart.round
            if rnd >= onset:
                for i in alive:
                    if len(body[i]) <= FEED_MAX_LEN:
                        eligible[team_of[i]] += 1
        elif w == "turnStart":
            actor = ev.turnStart.id
        elif w == "dragonLog":
            if str(ev.dragonLog.text) == "ACT:diss":
                acted[team_of.get(ev.dragonLog.id, "?")] += 1
                diss_round[ev.dragonLog.id] = rnd
        elif w == "dragonSplit":
            s = ev.dragonSplit
            team_of[s.childId] = "AB"[0 if str(s.team) == "a" else 1]
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
            alive.add(s.childId)
            born[s.childId] = rnd
        elif w == "dragonDeath":
            d = ev.dragonDeath
            # only deliberate dissolutions count toward delivered mass
            if diss_round.get(d.id) == rnd:
                per_diss.append([team_of.get(d.id, "?"), rnd, set(body.get(d.id, ())),
                                 collections.Counter(), False])
            alive.discard(d.id)
        elif w == "tileChange":
            tc = ev.tileChange
            cell = (tc.tile.x, tc.tile.y)
            if tc.hasPearl:
                for rec in per_diss:
                    if cell in rec[2] and abs(rnd - rec[1]) <= 1:
                        rec[4] = True
            else:
                t = team_of.get(actor)
                if t and actor in alive:
                    for rec in per_diss:
                        if cell in rec[2] and 0 <= rnd - rec[1] <= 2 and \
                                team_of.get(actor) == rec[0]:
                            rec[3][actor] += 1
    # final standings
    st = replaystats.analyse(str(path))
    out = {}
    for t in "AB":
        delivered = sum(min(sum(rec[3].values()), 2) for rec in per_diss if rec[0] == t)
        crown_alive = 1 if st["standing"][t]["units"] > 0 else 0
        margin = st["standing"][t]["longest"] - st["standing"]["B" if t == "A" else "A"]["longest"]
        out[t] = dict(eligible=eligible[t], acted=acted[t], delivered=delivered,
                      diss_events=acted[t], crown_alive=crown_alive, margin=margin,
                      longest=st["standing"][t]["longest"])
    out["rounds"] = st["rounds"]
    return out


def main():
    for d in sys.argv[1:]:
        d = Path(d)
        rows = []
        for rp in sorted(d.glob("replays/*.replay")):
            mapname = rp.name.split("__")[0]
            try:
                rows.append((mapname, funnel(rp, mapname)))
            except Exception as exc:
                print("skip %s: %r" % (rp.name, exc))
        by_class = collections.defaultdict(list)
        for m, f in rows:
            cls = "compact" if int(f["rounds"]) and m in (
                "devil", "dilemma", "portals", "trophy", "queen_of_spades") else "open"
            # compact = <= 625 tiles per the brief
            by_class[(cls,)].append((m, f))
        print("\n== %s (%d games) ==" % (d.name, len(rows)))
        for cls in ("compact", "open"):
            games = by_class.get((cls,), [])
            if not games:
                continue
            print("[%s]" % cls)
            for t in "AB":
                vals = [f[t] for _, f in games]
                n = len(vals)
                med = lambda k: sorted(v[k] for v in vals)[n // 2]
                print("  team %s: eligible med %.0f  acted med %.0f  delivered med %.0f  "
                      "crown alive %.2f  margin med %+.0f  longest med %.0f" % (
                          t, med("eligible"), med("acted"), med("delivered"),
                          sum(v["crown_alive"] for v in vals) / float(n),
                          med("margin"), med("longest")))
        for m, f in rows[:0]:
            pass
        for m, f in rows:
            print("  %-16s rounds %-4d A elig %-5d acted %-3d deliv %-3d crown %d margin %+d | "
                  "B elig %-5d acted %-3d deliv %-3d crown %d margin %+d" % (
                      m, f["rounds"], f["A"]["eligible"], f["A"]["acted"], f["A"]["delivered"],
                      f["A"]["crown_alive"], f["A"]["margin"],
                      f["B"]["eligible"], f["B"]["acted"], f["B"]["delivered"],
                      f["B"]["crown_alive"], f["B"]["margin"]))


if __name__ == "__main__":
    main()
