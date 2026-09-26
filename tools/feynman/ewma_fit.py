#!/usr/bin/env python3
"""Offline EWMA half-life validation from mass_trace (LOG FM) streams.

For each dragon's raw observation series (one row per own turn), replay the
mass.py local estimator at candidate half-lives: EWMA with the same
portal-jump reset (toroidal head displacement > 3 resets), then score the
one-round-ahead prediction of the next observation. Consumption was off in
the trace runs, so the observation stream is policy-independent.

Usage: .venv/bin/python tools/feynman/ewma_fit.py build/feynman/traces/fm_*.log
"""
import json
import math
import sys
from collections import defaultdict

HALFLIVES = [1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 32]


def series(paths):
    """-> {map: {(id): [(rnd, x, y, aa, ee), ...]}} sorted by round."""
    out = defaultdict(lambda: defaultdict(list))
    for p in paths:
        name = p.rsplit("/", 1)[-1].replace("fm_", "").replace(".log", "")
        for line in open(p):
            row = json.loads(line[line.index("LOG FM ") + 7:])
            out[name][row["id"]].append(
                (row["rnd"], row["x"], row["y"], row["aa"], row["ee"]))
    for m in out:
        for did in out[m]:
            out[m][did].sort()
    return out


def predict_errors(obs, hl, signal):
    """MSE of the one-round-ahead EWMA prediction for signal index (3=aa, 4=ee)."""
    err = []
    px = py = None
    est = 0.0
    last_rnd = None
    W = H = 60  # toroidal jump test only needs an upper bound; maps are <= 60
    for rnd, x, y, aa, ee in obs:
        v = aa if signal == 3 else ee
        if last_rnd is None or abs(x - px) + abs(y - py) > 3:
            est = v  # reset: fresh observation (also first turn)
        else:
            gap = max(1, rnd - last_rnd)
            retain = 0.5 ** (gap / hl)
            est = retain * est + (1.0 - retain) * v
        pred_next = 0.5 ** (1.0 / hl) * est
        err.append((pred_next, v, rnd))
        px, py, last_rnd = x, y, rnd
    # score prediction at t against the observation at t+1
    sse, n = 0.0, 0
    sse_c, n_c = 0.0, 0  # conditional: enemy actually visible at t or t+1
    for (pred, v, r1), (_, actual, r2) in zip(err, err[1:]):
        if r2 == r1 + 1:
            sse += (pred - actual) ** 2
            n += 1
            if v > 0 or actual > 0:
                sse_c += (pred - actual) ** 2
                n_c += 1
    return sse, n, sse_c, n_c


def main(paths):
    data = series(paths)
    for signal, label in ((3, "ally"), (4, "enemy")):
        print(f"\n== {label} half-life sweep (MSE per predicted turn) ==")
        print(f"{'hl':>4} " + " ".join(f"{m[:12]:>12}" for m in data) + f" {'ALL':>12}")
        for hl in HALFLIVES:
            cells = []
            tot_sse = tot_n = 0
            tot_c = tot_cn = 0
            for m in data:
                sse = n = sc = nc = 0
                for did, obs in data[m].items():
                    s, k, s2, k2 = predict_errors(obs, hl, signal)
                    sse += s
                    n += k
                    sc += s2
                    nc += k2
                cells.append((sse, n))
                tot_sse += sse
                tot_n += n
                tot_c += sc
                tot_cn += nc
            row = " ".join(f"{(s / n if n else float('nan')):12.3f}" for s, n in cells)
            cond = f"  cond-MSE {tot_c / max(1, tot_cn):8.3f} (n={tot_cn})" if label == "enemy" else ""
            print(f"{hl:>4} {row} {tot_sse / max(1, tot_n):12.3f}   (n={tot_n}){cond}")


if __name__ == "__main__":
    main(sys.argv[1:])
