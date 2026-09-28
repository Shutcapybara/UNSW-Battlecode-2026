"""S2 paired analysis: per-arm paired win deltas AND paired economy-metric deltas.

    python3 tools/sakura/s02_analyze.py build/sakura-s02

Expects <dir>/base-s1 and <dir>/{econ,safety,explore,all}-s1 results.jsonl.
"""
import collections
import json
import sys
import statistics
from pathlib import Path

HERE = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
MAP_TILES = {"schooltime": 2400, "portals": 512, "slithery_fight": 1701, "queen_of_spades": 875,
             "default": 1024, "trophy": 625, "dilemma": 512, "autarky": 972, "devil": 512, "trauma": 1152}
METRICS = ["units_r25", "units_r50", "units_r100", "total_r250", "portal_deaths",
           "wall_self_per_1k", "all_deaths_per_1k", "pearls", "first_pearl"]


def load(d):
    rows = []
    for line in (HERE / d / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["winner"] != "error":
            rows.append(r)
    return rows


def pts(x):
    return 1.0 if x["res"] == "W" else 0.5 if x["res"] == "D" else 0.0


def main():
    arms = ["econ-s1", "safety-s1", "explore-s1", "all-s1"]
    base = {}
    for r in load("base-s1"):
        base[(r["map"], r["side"], r["opp"], r["seed"])] = r
    print("control base-s1: %d games, score %.1f/%d" % (
        len(base), sum(pts(r) for r in base.values()), len(base)))
    out = {"base_games": len(base)}
    for arm in arms:
        if not (HERE / arm / "results.jsonl").exists():
            continue
        rows = load(arm)
        pairs = []
        for r in rows:
            k = (r["map"], r["side"], r["opp"], r["seed"])
            if k in base:
                pairs.append((r, base[k]))
        n = len(pairs)
        bet = sum(1 for a, b in pairs if pts(a) > pts(b))
        wor = sum(1 for a, b in pairs if pts(a) < pts(b))
        net = sum(pts(a) - pts(b) for a, b in pairs)
        arm_score = sum(pts(a) for a, _ in pairs)
        print("\n== %s: %d pairs  better/worse %d/%d  net %+.1f  arm score %.1f" % (
            arm, n, bet, wor, net, arm_score))
        rep = dict(n=n, better=bet, worse=wor, net=net, arm_score=arm_score)
        # paired metric deltas, all maps + per class + hypothesis subsets
        def mdelta(sel, m):
            ds = []
            for a, b in sel:
                ca = a.get("contract", {}).get(a["side"], {})
                cb = b.get("contract", {}).get(b["side"], {})
                if m in ca and m in cb and ca[m] >= 0 and cb[m] >= 0:
                    ds.append(ca[m] - cb[m])
            return ds

        for label, sel in (("all", pairs),
                           ("compact", [p for p in pairs if MAP_TILES[p[0]["map"]] <= 625]),
                           ("open", [p for p in pairs if MAP_TILES[p[0]["map"]] > 625])):
            line = ["  %-8s" % label]
            for m in METRICS:
                ds = mdelta(sel, m)
                if not ds:
                    continue
                line.append("%s %+.1f" % (m.replace("_r", "r").replace("_per_1k", ""),
                                          statistics.median(ds)))
            print(" ".join(line))
            rep.setdefault("medians", {})[label] = {
                m: round(statistics.median(mdelta(sel, m)), 2) for m in METRICS if mdelta(sel, m)}
        # H-portal-safety subset
        sel = [p for p in pairs if p[0]["map"] in ("default", "schooltime", "portals")]
        ds = mdelta(sel, "portal_deaths")
        bb = statistics.median([b.get("contract", {}).get(b["side"], {}).get("portal_deaths", -1)
                                for b, _ in ((a, b) for a, b in sel)]) if sel else 0
        if ds:
            print("  portal-safety subset (n=%d): portal_deaths delta %+.1f (base median %.1f)"
                  % (len(sel), statistics.median(ds), bb))
            rep["portal_safety"] = dict(n=len(sel), delta=round(statistics.median(ds), 2),
                                        base_median=bb)
        # H-explore subset
        sel = [p for p in pairs if p[0]["map"] in ("portals", "slithery_fight", "trauma")]
        if sel:
            netx = sum(pts(a) - pts(b) for a, b in sel)
            print("  explore subset (n=%d): net pairs %+.1f" % (len(sel), netx))
            rep["explore_subset"] = dict(n=len(sel), net=netx)
        # per-map net
        pm = collections.defaultdict(float)
        for a, b in pairs:
            pm[a["map"]] += pts(a) - pts(b)
        rep["per_map_net"] = dict(pm)
        print("  per-map net: " + "  ".join("%s %+.0f" % kv for kv in sorted(pm.items())))
        out[arm] = rep
    (HERE / "analysis.json").write_text(json.dumps(out, indent=1))
    print("\nwrote analysis.json")


if __name__ == "__main__":
    main()
