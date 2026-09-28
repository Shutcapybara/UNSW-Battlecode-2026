#!/usr/bin/env python3
"""P1 panel analysis: paired deltas, pace attainment, survival, and a
regularised logistic model of win ~ stage statistics (leave-one-map-out AUC).

Usage: python3 tools/pace/analyze.py BUILD/pace-panel [--targetcompact 23,17,30,58,86 ...]
Prints the report; writes nothing.
"""
import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

TILES = {"portals": 512, "trophy": 625, "dilemma": 512, "devil": 512,
         "schooltime": 2400, "slithery_fight": 1701, "queen_of_spades": 875,
         "default": 1024, "autarky": 972, "trauma": 1152}
COMPACT = {m for m, t in TILES.items() if t <= 625}
# corpus winner medians 2026-09-29 (units r25/r50/r100; total r25/r50/r100/r250)
TARGET = {"compact": {"u25": 7, "u50": 12, "u100": 23, "t25": 17, "t50": 30,
                      "t100": 58, "t250": 86},
          "open": {"u25": 6, "u50": 11, "u100": 20, "t25": 15, "t50": 27,
                   "t100": 50, "t250": 116}}


def sign_test(b, w):
    n = b + w
    if n == 0:
        return float("nan")
    k = min(b, w)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2.0 ** n * 2
    return min(1.0, p)


def score(row):
    return {"W": 1.0, "D": 0.5, "L": 0.0}[row["res"]]


def res_of(row):
    if row["winner"] == "error":
        return "E"
    if row["winner"] == "draw":
        return "D"
    return "W" if row["winner"] == row["side"] else "L"


def med_q(vals, q=0.25):
    if not vals:
        return "-"
    v = sorted(vals)

    def pct(p):
        return v[min(len(v) - 1, max(0, int(round(p * (len(v) - 1)))))]

    return "%.1f [%.1f-%.1f]" % (statistics.median(v), pct(q), pct(1 - q))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("panel")
    ap.add_argument("--minseed", type=int, default=0)
    args = ap.parse_args()
    rows = []
    for line in Path(args.panel, "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        r["res"] = res_of(r)
        if r["res"] != "E" and r["seed"] >= args.minseed:
            rows.append(r)
    by_key = {}
    for r in rows:
        by_key[(r["map"], r["side"], r["seed"], r["opp"], r["arm"])] = r
    arms = sorted({r["arm"] for r in rows})
    print("games per arm:", {a: sum(1 for r in rows if r["arm"] == a) for a in arms})

    # ---- paired deltas vs host --------------------------------------------
    for arm in arms:
        if arm == "host":
            continue
        pairs = []
        for k, rh in by_key.items():
            if rh["arm"] != "host":
                continue
            ra = by_key.get(k[:4] + (arm,))
            if ra is None:
                continue
            pairs.append((rh, ra, score(ra) - score(rh)))
        b = sum(1 for _, _, d in pairs if d > 0)
        w = sum(1 for _, _, d in pairs if d < 0)
        t = len(pairs) - b - w
        print("\n== %s vs host (paired, n=%d): better %d / worse %d / tie %d, "
              "delta %+.3f, sign p %.4f" % (arm, len(pairs), b, w, t,
              sum(d for _, _, d in pairs) / max(1, len(pairs)), sign_test(b, w)))
        for cls in ("compact", "open"):
            sel = [(rh, ra, d) for rh, ra, d in pairs
                   if (rh["map"] in COMPACT) == (cls == "compact")]
            if sel:
                bb = sum(1 for _, _, d in sel if d > 0)
                ww = sum(1 for _, _, d in sel if d < 0)
                print("   %-8s n=%-4d %+.3f (b%d/w%d, p %.3f)  |  du100 %+.1f  dt250 %+.1f" %
                      (cls, len(sel), sum(d for _, _, d in sel) / len(sel), bb, ww,
                       sign_test(bb, ww),
                       statistics.median(ra["mine"]["u100"] - rh["mine"]["u100"]
                                        for rh, ra, _ in sel),
                       statistics.median(ra["mine"]["t250"] - rh["mine"]["t250"]
                                        for rh, ra, _ in sel)))
        per_map = defaultdict(list)
        for rh, ra, d in pairs:
            per_map[rh["map"]].append(d)
        print("   per-map: " + "  ".join("%s %+.2f(%d)" % (m, sum(v) / len(v), len(v))
                                        for m, v in sorted(per_map.items())))

    # ---- win share + attainment + survival --------------------------------
    print("\n== pace attainment (median [q25-q75]) and win share, per arm and class")
    for cls in ("compact", "open"):
        print("-- %s (targets u25 %d u50 %d u100 %d t250 %d)" %
              (cls, TARGET[cls]["u25"], TARGET[cls]["u50"], TARGET[cls]["u100"],
               TARGET[cls]["t250"]))
        for arm in arms:
            sel = [r for r in rows if r["arm"] == arm and
                   (r["map"] in COMPACT) == (cls == "compact")]
            if not sel:
                continue
            ws = statistics.mean(score(r) for r in sel)
            onpace = statistics.mean(1.0 if r["mine"]["u100"] >=
                                     0.9 * TARGET[cls]["u100"] else 0.0 for r in sel)
            surv = [statistics.mean(1.0 if r["mine"]["u%d" % st] > 0 else 0.0
                                    for r in sel) for st in (100, 250, 400)]
            print("  %-8s n=%-3d ws %.3f onpace@r100 %.2f | u25 %-8s u50 %-8s u100 %-8s "
                  "t250 %-8s | surv r100/250/400 %.2f/%.2f/%.2f | d_wall+self/1k %s "
                  "newborn10 %s" % (
                arm, len(sel), ws, onpace,
                med_q([r["mine"]["u25"] for r in sel]),
                med_q([r["mine"]["u50"] for r in sel]),
                med_q([r["mine"]["u100"] for r in sel]),
                med_q([r["mine"]["t250"] for r in sel]),
                surv[0], surv[1], surv[2],
                med_q([r["mine"]["d_wall"] + r["mine"]["d_self"] for r in sel]),
                med_q([r["mine"]["newborn10"] for r in sel])))

    # ---- logistic model: win ~ stage statistics (all games) ----------------
    feats = ["du25", "du50", "du100", "dt250", "dl400", "dwall", "dself", "dbody",
             "dh2h", "splits", "newborn", "portal", "sonar"]
    X, Y, M = [], [], []
    for r in rows:
        m, o = r["mine"], r["theirs"]
        x = [m["u25"] - o["u25"], m["u50"] - o["u50"], m["u100"] - o["u100"],
             m["t250"] - o["t250"], m["l400"] - o["l400"],
             m["d_wall"], m["d_self"], m["d_body"], m["d_h2h"],
             m["splits"] / 100.0, m["newborn10"] / 10.0,
             m["portal_steps"] / 100.0, m["sonar"] / max(1, m["turns"]) / 10.0]
        X.append(x)
        Y.append(1.0 if r["res"] == "W" else 0.0 if r["res"] == "L" else 0.5)
        M.append(r["map"])
    n, d = len(X), len(feats)
    mu = [statistics.mean(c) for c in zip(*X)]
    sd = [max(1e-9, statistics.pstdev(c)) for c in zip(*X)]
    Z = [[(X[i][j] - mu[j]) / sd[j] for j in range(d)] for i in range(n)]
    Yb = [max(0.0, min(1.0, y)) for y in Y]

    def fit(rows_idx, lam=1.0, iters=400, lr=0.3):
        beta = [0.0] * d
        b0 = 0.0
        for _ in range(iters):
            gb0, gb = 0.0, [0.0] * d
            for i in rows_idx:
                z = b0 + sum(beta[j] * Z[i][j] for j in range(d))
                p = 1.0 / (1.0 + math.exp(-max(-30, min(30, z))))
                e = p - Yb[i]
                gb0 += e / len(rows_idx)
                for j in range(d):
                    gb[j] += e * Z[i][j] / len(rows_idx)
            b0 -= lr * gb0
            for j in range(d):
                beta[j] -= lr * (gb[j] + lam * beta[j] / len(rows_idx))
        return b0, beta

    def auc(pairs):
        pos = sorted(p for p, y in pairs if y == 1)
        neg = sorted(p for p, y in pairs if y == 0)
        if not pos or not neg:
            return float("nan")
        import bisect
        wins = ties = 0
        for p in neg:
            lo = bisect.bisect_left(pos, p)
            hi = bisect.bisect_right(pos, p)
            ties += hi - lo
            wins += len(pos) - hi
        return (wins + 0.5 * ties) / (len(pos) * len(neg))

    b0, beta = fit(range(n))
    print("\n== logistic win ~ stage stats (standardised coefficients, L2=1, n=%d)" % n)
    for j in sorted(range(d), key=lambda j: -abs(beta[j])):
        print("   %-9s %+.3f" % (feats[j], beta[j]))
    maps = sorted(set(M))
    aucs = []
    for hm in maps:
        tr = [i for i in range(n) if M[i] != hm]
        te = [i for i in range(n) if M[i] == hm]
        if len(set(Yb[i] for i in te)) < 2:
            continue
        tb0, tbeta = fit(tr)
        pred = [(tb0 + sum(tbeta[j] * Z[i][j] for j in range(d)), Yb[i]) for i in te]
        aucs.append((hm, auc(pred)))
    print("   leave-one-map-out AUC: mean %.3f | %s" %
          (statistics.mean(a for _, a in aucs),
           "  ".join("%s %.2f" % (m, a) for m, a in aucs)))


if __name__ == "__main__":
    main()
