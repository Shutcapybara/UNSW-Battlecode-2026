"""S2 report: paired deltas vs a base arm plus economy medians per map class.

    python3 s2report.py --base BASEBOT --dirs RUN1 RUN2 ... [--arms BOT ...] [--maps m1,m2]

Fixture key = (map, seed, opp, side); opponent dirs named opp-<x> are treated as <x>.
"""
import argparse
import collections
import json
import math
from pathlib import Path

TILES = {"schooltime": 2400, "portals": 512, "slithery_fight": 1701, "queen_of_spades": 875,
         "default": 1024, "trophy": 625, "dilemma": 512, "dilemma_10": 512, "autarky": 972,
         "devil": 512, "trauma": 1152}


def cls(m):
    return "compact" if TILES.get(m, 9999) <= 625 else "open"


def score(r):
    return 1.0 if r["res"] == "W" else 0.5 if r["res"] == "D" else 0.0


def sign_p(b, w):
    n = b + w
    if n == 0:
        return 1.0
    k = min(b, w)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2.0 ** n)


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return float("nan")
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def load(dirs):
    rows = {}
    for d in dirs:
        p = Path(d) / "results.jsonl"
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if "error" in r or "me" not in r:
                continue
            opp = r["opp"][4:] if r["opp"].startswith("opp-") else r["opp"]
            rows[(r["cand"], r["map"], r["seed"], opp, r["side"])] = r
    return rows


def at(m, k, i):
    v = m["at"].get(k)
    return v[i] if v else None


def metrics(rs):
    me = [r["me"] for r in rs]
    turns = sum(m["turns"] for m in me)
    ws = sum(m["deaths"].get("wall", 0) + m["deaths"].get("self", 0) for m in me)
    return dict(
        n=len(rs), score=sum(map(score, rs)) / max(1, len(rs)),
        u25=med([at(m, "25", 0) for m in me]), u50=med([at(m, "50", 0) for m in me]),
        u100=med([at(m, "100", 0) for m in me]), t100=med([at(m, "100", 1) for m in me]),
        t250=med([at(m, "250", 1) for m in me]), l400=med([at(m, "400", 2) for m in me]),
        pd=med([m.get("portal_deaths") for m in me]), pearls=med([m.get("pearls") for m in me]),
        p100=med([m.get("pearls_r100") for m in me]), fp=med([m.get("team_first_pearl") for m in me]),
        cfp=med([m.get("first_pearl_median") for m in me]),
        ws1k=1000.0 * ws / max(1, turns), d100=med([m.get("deaths_r100") for m in me]),
        nb10=100.0 * sum(m["newborn_deaths10"] for m in me) / max(1, sum(m["births"] for m in me)),
        acts=dict(sum((collections.Counter(m["act"]) for m in me), collections.Counter())))


def fmt(k):
    return ("n=%(n)d score %(score).3f | u25/50/100 %(u25).0f/%(u50).0f/%(u100).0f | tot r100 %(t100).0f r250 %(t250).0f"
            " | long r400 %(l400).0f | pearls %(pearls).0f (r100 %(p100).0f) first %(fp).0f child %(cfp).0f"
            " | portal-deaths %(pd).0f | wall+self/1k %(ws1k).1f | deaths r100 %(d100).0f | nb10/100 %(nb10).1f") % k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--arms", nargs="*")
    ap.add_argument("--maps")
    ap.add_argument("--common", action="store_true", help="restrict every arm to fixtures all arms share")
    a = ap.parse_args()
    rows = load(a.dirs)
    if a.maps:
        keep = set(a.maps.split(","))
        rows = {k: v for k, v in rows.items() if k[1] in keep}
    arms = a.arms or sorted({k[0] for k in rows})
    if a.base not in arms:
        arms = [a.base] + arms
    fx = {c: {k[1:] for k in rows if k[0] == c} for c in arms}
    common = set.intersection(*[fx[c] for c in arms]) if a.common else None
    for c in arms:
        keys = [k for k in fx[c] if common is None or k in common]
        rs = [rows[(c,) + k] for k in keys]
        if not rs:
            continue
        print("\n== %s" % c)
        print("  all     " + fmt(metrics(rs)))
        for cl in ("compact", "open"):
            sub = [r for r in rs if cls(r["map"]) == cl]
            if sub:
                print("  %-7s " % cl + fmt(metrics(sub)))
        if c == a.base:
            continue
        better = worse = 0
        diffs = []
        pm = collections.defaultdict(list)
        po = collections.defaultdict(list)
        dt250 = []
        du100 = []
        for k in keys:
            b = rows.get((a.base,) + k)
            if b is None:
                continue
            r = rows[(c,) + k]
            d = score(r) - score(b)
            diffs.append(d)
            pm[k[0]].append(d)
            po[k[2]].append(d)
            better += d > 0
            worse += d < 0
            x, y = at(r["me"], "250", 1), at(b["me"], "250", 1)
            if x is not None and y is not None:
                dt250.append(x - y)
            x, y = at(r["me"], "100", 0), at(b["me"], "100", 0)
            if x is not None and y is not None:
                du100.append(x - y)
        if diffs:
            print("  PAIRED vs %s: n=%d delta %+.3f better/worse %d/%d sign p=%.3f | med d(total r250) %+.1f med d(units r100) %+.1f" % (
                a.base, len(diffs), sum(diffs) / len(diffs), better, worse, sign_p(better, worse),
                med(dt250), med(du100)))
            print("   maps: " + "  ".join("%s %+.2f(%d)" % (m[:10], sum(v) / len(v), len(v)) for m, v in sorted(pm.items())))
            print("   opps: " + "  ".join("%s %+.2f(%d)" % (o[:14], sum(v) / len(v), len(v)) for o, v in sorted(po.items())))


if __name__ == "__main__":
    main()
