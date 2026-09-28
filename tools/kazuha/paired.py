#!/usr/bin/env python3
"""Paired comparison of two compare_bot experiment dirs on shared fixtures.

Usage: paired.py EXPDIR_ARM EXPDIR_CONTROL
Both dirs must contain results.json rows keyed by (opponent, map, side).
Prints: per-arm score, paired better/worse/tie, per-map deltas, sign test.
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def load(d):
    rows = json.loads((Path(d) / "results.json").read_text())
    return {(r["opponent"], r["map"], r["side"]): r for r in rows}


def pts(r):
    o = r["outcome"]
    won = (r["side"] == "A" and o == "A") or (r["side"] == "B" and o == "B")
    draw = o in ("draw", "Draw")
    return 1.0 if won else (0.5 if draw else 0.0)


def sign_test(b, w):
    n = b + w
    if n == 0:
        return 1.0
    k = min(b, w)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main(arm_d, ctl_d):
    arm = load(arm_d)
    ctl = load(ctl_d)
    keys = sorted(set(arm) & set(ctl))
    only_arm = set(arm) - set(ctl)
    only_ctl = set(ctl) - set(arm)
    abetter = aworse = tie = 0
    per_map = defaultdict(lambda: [0, 0, 0])     # map -> [better, worse, tie]
    per_opp = defaultdict(lambda: [0, 0, 0])
    arm_score = ctl_score = 0.0
    for k in keys:
        a = pts(arm[k])
        c = pts(ctl[k])
        arm_score += a
        ctl_score += c
        if a > c:
            abetter += 1
            per_map[k[1]][0] += 1
            per_opp[k[0]][0] += 1
        elif a < c:
            aworse += 1
            per_map[k[1]][1] += 1
            per_opp[k[0]][1] += 1
        else:
            tie += 1
            per_map[k[1]][2] += 1
            per_opp[k[0]][2] += 1
    n = len(keys)
    print("paired fixtures: %d (arm-only %d, control-only %d)" % (n, len(only_arm), len(only_ctl)))
    print("arm score: %.1f/%d (%.1f%%)  control score: %.1f/%d (%.1f%%)" % (
        arm_score, n, 100 * arm_score / max(n, 1), ctl_score, n, 100 * ctl_score / max(n, 1)))
    print("pairs better/worse/tie: %d/%d/%d  sign-test p=%.4f" % (
        abetter, aworse, tie, sign_test(abetter, aworse)))
    print("\nper map (better/worse/tie):")
    for m in sorted(per_map):
        b, w, t = per_map[m]
        print("  %-18s %2d/%2d/%2d  %+d" % (m, b, w, t, b - w))
    print("\nper opponent (better/worse/tie):")
    for o in sorted(per_opp):
        b, w, t = per_opp[o]
        print("  %-34s %2d/%2d/%2d  %+d" % (o, b, w, t, b - w))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
