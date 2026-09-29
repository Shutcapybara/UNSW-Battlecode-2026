#!/usr/bin/env python3
"""cx benchmarks table — the C1-F §1 baseline table from bench.py JSONL runs.

For each arm (a bench jsonl) and each live map, per BENCHMARKS.md's three
yardsticks, each as absolute / ÷ field median / gap to top ten / field
percentile (medians over the arm's side-games on that map):

  economy curve  pearls eaten by r50/r100/r150/r250
  scale          dragons (units) and total length at r100
  hygiene        wall / self / ally-body / h2h deaths per 1k dragon-turns
                 (whole game), plus portal-step deaths per 100 portal steps

Field references are docs/analysis/benchmarks/{field_references,
field_distributions}.json (fixed, 954 side-games per map). Maps without a
reference (the generalisation panel) report absolute medians only.

    python3 tools/cx/benchmarks_table.py build/cx/f00-on-live.jsonl [--label NAME] \
        [MORE.jsonl ...] [--maps live|panel|all]
"""
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import statistics
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
BENCH = REPO / "docs/analysis/benchmarks"

NAME = {  # arena map stem -> field display name
    "portals": "Portals", "schooltime": "Schooltime", "default": "Default",
    "autarky": "Autarky", "trauma": "Trauma", "dilemma": "Prisoners Dilemma",
    "slithery_fight": "Slithery Fight", "queen_of_spades": "Queen Of Spades",
    "trophy": "Trophy", "devil": "Devil",
}
LIVE = list(NAME)

ECON = [("pearls@50", "eaten_r50"), ("pearls@100", "eaten_r100"),
        ("pearls@150", "eaten_r150"), ("pearls@250", "eaten_r250"),
        ("units@100", "units_r100"), ("total@100", "len_r100")]
HYG = [("death_wall_per1k", "wall"), ("death_self_per1k", "self"),
       ("death_ally_body_per1k", "body"), ("death_h2h_ally_per1k", "h2h")]


def load(path):
    return [json.loads(l) for l in pathlib.Path(path).read_text().splitlines() if l.strip()]


def deaths_per1k(u, cause):
    return 1000.0 * u.get("deaths", {}).get(cause, 0) / max(1, u.get("turns", 1))


def pct(dist, x):
    # share of the field you beat, ties counted half (BENCHMARKS convention)
    if not dist:
        return None
    lo = bisect.bisect_left(dist, x)
    hi = bisect.bisect_right(dist, x)
    return (lo + (hi - lo) / 2) / len(dist)


def table(path, label, refs, dists, only):
    rows = load(path)
    out = {"label": label, "games": len(rows), "maps": {}}
    for m in sorted({r["map"] for r in rows}):
        if only == "live" and m not in NAME:
            continue
        if only == "panel" and m in NAME:
            continue
        sub = [r for r in rows if r["map"] == m]
        cell = {"n": len(sub)}
        fname = NAME.get(m)
        for metric, key in ECON:
            vals = [r["us"].get(key) for r in sub if r["us"].get(key) is not None]
            cell[key] = {"abs": statistics.median(vals)} if vals else None
            if cell[key] and fname and fname in refs.get(metric, {}):
                ref = refs[metric][fname]
                cell[key]["ratio"] = cell[key]["abs"] / ref["median"] if ref["median"] else None
                cell[key]["top10_ratio"] = cell[key]["abs"] / ref["top10"] if ref["top10"] else None
                ps = [pct(dists[metric].get(fname, []), v) for v in vals]
                ps = [p for p in ps if p is not None]
                if ps:
                    cell[key]["pct"] = statistics.median(ps)
        for metric, cause in HYG:
            vals = [deaths_per1k(r["us"], cause) for r in sub]
            cell[cause] = {"abs": statistics.median(vals)}
            if fname and fname in refs.get(metric, {}):
                ref = refs[metric][fname]
                cell[cause]["excess_top10"] = cell[cause]["abs"] - ref["top10"]
                ps = [pct(dists[metric].get(fname, []), v) for v in vals]
                ps = [p for p in ps if p is not None]
                if ps:
                    cell[cause]["pct"] = statistics.median(ps)  # higher = fewer deaths
        # portal-step deaths per 100 steps (no field reference exists)
        steps = [r["us"].get("portal_steps") or 0 for r in sub]
        pd_ = [r["us"].get("portal_deaths") or 0 for r in sub]
        if sum(steps) > 0:
            cell["portal"] = {
                "steps_game": statistics.median(steps),
                "deaths_game": statistics.median(pd_),
                "per100": 100.0 * sum(pd_) / max(1, sum(steps)),
            }
        out["maps"][m] = cell
    # pooled
    pooled = {}
    for metric, key in ECON:
        vals = [r["us"].get(key) for r in rows if r["us"].get(key) is not None]
        pooled[key] = statistics.median(vals) if vals else None
    for _, cause in HYG:
        pooled[cause] = statistics.median([deaths_per1k(r["us"], cause) for r in rows])
    steps = [r["us"].get("portal_steps") or 0 for r in rows]
    pdd = [r["us"].get("portal_deaths") or 0 for r in rows]
    pooled["portal_per100"] = 100.0 * sum(pdd) / max(1, sum(steps))
    pooled["portal_steps_game"] = statistics.median(steps)
    pooled["portal_deaths_game"] = statistics.median(pdd)
    pooled["win_rate"] = sum(r["result"] == "win" for r in rows) / max(1, len(rows))
    out["pooled"] = pooled
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arms", nargs="+")
    ap.add_argument("--labels")
    ap.add_argument("--maps", default="live", choices=["live", "panel", "all"])
    ap.add_argument("--json-out")
    a = ap.parse_args()
    refs = json.load(open(BENCH / "field_references.json"))
    dists = json.load(open(BENCH / "field_distributions.json"))
    labels = a.labels.split(",") if a.labels else [pathlib.Path(p).stem for p in a.arms]
    tables = [table(p, l, refs, dists, a.maps) for p, l in zip(a.arms, labels)]
    if a.json_out:
        pathlib.Path(a.json_out).write_text(json.dumps(tables, indent=1))
    # print a compact text version
    for t in tables:
        print(f"\n== {t['label']} ({t['games']} games, {a.maps}) ==")
        hdr = f"{'map':>18} {'eat50':>14} {'eat100':>14} {'eat250':>14} {'u100':>14} {'len100':>14} {'wall/1k':>8} {'self/1k':>8} {'port/100':>8}"
        print(hdr)
        for m, c in t["maps"].items():
            def f(k, death=False):
                v = c.get(k)
                if not v:
                    return "-".rjust(14)
                if death:
                    s = f"{v['abs']:.1f}"
                    if "pct" in v:
                        s += f" p{v['pct']:.2f}"
                    return s.rjust(8)
                s = f"{v['abs']:.0f}"
                if v.get("ratio") is not None:
                    s += f" x{v['ratio']:.2f}"
                if v.get("pct") is not None:
                    s += f" p{v['pct']:.2f}"
                return s.rjust(14)
            pv = c.get("portal")
            print(f"{m:>18} {f('eaten_r50')} {f('eaten_r100')} {f('eaten_r250')} {f('units_r100')} "
                  f"{f('len_r100')} {f('wall', True)} {f('self', True)} "
                  f"{(f'{pv['per100']:.1f}' if pv else '-').rjust(8)}")
        p = t["pooled"]
        print("pooled: eat50/100/150/250 {} {} {} {} | u100 {} len100 {} | wall/self/body/h2h {:.1f}/{:.1f}/{:.1f}/{:.1f} | portal {:.1f}/100 ({:.0f} steps/g) | win {:.0%}".format(
            p["eaten_r50"], p["eaten_r100"], p["eaten_r150"], p["eaten_r250"], p["units_r100"],
            p["len_r100"], p["wall"], p["self"], p["body"], p["h2h"], p["portal_per100"],
            p["portal_steps_game"], p["win_rate"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
