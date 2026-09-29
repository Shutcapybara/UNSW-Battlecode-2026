#!/usr/bin/env python3
"""Compare bench runs (arms) in exact pairs (map, side, seed, opp).

    python3 tools/cx/ablate.py ARM_A.jsonl ARM_B.jsonl [ARM_C.jsonl ...] [--names a,b,c] [--filter live|panel]

For every metric: per-arm median, then for each ordered pair of arms (later - earlier)
the better/same/worse counts and a two-sided sign test. Metrics where lower is
better are flagged (L). Pools: live = the ten live maps; panel = var/, pub/, new/.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import pathlib

METRICS = [
    ("units_r25", 1), ("units_r50", 1), ("units_r100", 1), ("len_r100", 1), ("len_r250", 1),
    ("eaten_r100", 1), ("pearls_per_100dt", 1), ("moves_per_pearl", -1), ("first_pearl", -1),
    ("child_first_pearl_lag", -1), ("deaths_r100", -1), ("wall_r100", -1), ("self_r100", -1),
    ("body_r100", -1), ("h2h_r100", -1), ("portal_deaths_r100", -1), ("newborn_dead10_r100", -1),
    ("lenlost_r150", -1), ("win", 1),
]


def rows(path):
    out = {}
    for line in pathlib.Path(path).read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        u = dict(r["us"])
        c = u.get("deaths_cause_r100", {})
        for k in ("wall", "self", "body", "h2h"):
            u[f"{k}_r100"] = c.get(k, 0)
        u["win"] = 1 if r["result"] == "win" else 0 if r["result"] == "draw" else -1
        out[(r["map"], r["side"], r["seed"], r.get("opp"))] = u
    return out


def pool_of(m):
    return "panel" if "/" in m else "live"


def sign_p(b, w):
    n = b + w
    if n == 0:
        return 1.0
    k = min(b, w)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def med(v):
    v = sorted(x for x in v if x is not None)
    return v[len(v) // 2] if v else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arms", nargs="+")
    ap.add_argument("--names")
    ap.add_argument("--filter", choices=["live", "panel"])
    ap.add_argument("--metrics")
    a = ap.parse_args()
    names = a.names.split(",") if a.names else [pathlib.Path(p).stem for p in a.arms]
    data = [rows(p) for p in a.arms]
    keys = set(data[0])
    for d in data[1:]:
        keys &= set(d)
    if a.filter:
        keys = {k for k in keys if pool_of(k[0]) == a.filter}
    keys = sorted(keys)
    mets = [m for m in METRICS if not a.metrics or m[0] in a.metrics.split(",")]
    print(f"{len(keys)} common fixtures" + (f" ({a.filter})" if a.filter else ""))
    head = f"{'metric':>22} " + " ".join(f"{n[:10]:>10}" for n in names)
    pairs = list(itertools.combinations(range(len(names)), 2))
    head += "  " + "  ".join(f"{names[j][:6]}-{names[i][:6]} b/s/w p" for i, j in pairs)
    print(head)
    for m, sgn in mets:
        meds = [med([d[k].get(m) for k in keys]) for d in data]
        line = f"{m + (' (L)' if sgn < 0 else ''):>22} " + " ".join(f"{str(x):>10}" for x in meds)
        for i, j in pairs:
            b = s = w = 0
            for k in keys:
                x, y = data[j][k].get(m), data[i][k].get(m)
                if x is None or y is None:
                    continue
                dlt = (x - y) * sgn
                b += dlt > 0
                w += dlt < 0
                s += dlt == 0
            line += f"  {b:>3}/{s:>3}/{w:>3} p={sign_p(b, w):.3f}"
        print(line)


if __name__ == "__main__":
    main()
