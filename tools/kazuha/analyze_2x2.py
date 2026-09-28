#!/usr/bin/env python3
"""Aggregate the kazuha 2x2: paired results + falsifier stats from replays.

Usage: analyze_2x2.py CONTROL_DIR BOTH_DIR PROD_DIR DISSOLVE_DIR [--nodecode]
Prints the paired table (each arm vs control on shared fixtures) and the
falsifier medians per arm (decoded from each dir's replays).
"""
import json
import statistics
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

COMPACT = {"portals", "trophy", "dilemma", "devil"}


def load(d):
    rows = json.loads((Path(d) / "results.json").read_text())
    return {(r["opponent"], r["map"], r["side"]): r for r in rows
            if r.get("outcome") != "error"}


def pts(r):
    won = (r["side"] == "A" and r["outcome"] == "A") or (r["side"] == "B" and r["outcome"] == "B")
    draw = r["outcome"] not in ("A", "B")
    return 1.0 if won else (0.5 if draw else 0.0)


def decode(path_team):
    import subprocess
    path, team = path_team
    out = subprocess.run(
        [str(Path(__file__).parent / "kazuha_stats.py"), team, str(path)],
        capture_output=True, text=True)
    try:
        return json.loads(out.stdout.strip().splitlines()[-1])
    except Exception:
        return None


def main():
    dirs = dict(ctl=sys.argv[1], both=sys.argv[2], prod=sys.argv[3], diss=sys.argv[4])
    decode_flag = "--nodecode" not in sys.argv
    data = {k: load(v) for k, v in dirs.items()}
    ctl = data["ctl"]
    print("arm      n    score%%   better/worse/tie (vs control, paired)   compact +/-%s  open +/-%s")
    for k in ("both", "prod", "diss"):
        arm = data[k]
        keys = sorted(set(arm) & set(ctl))
        b = w = t = 0
        cb = cw = 0
        ob = ow = 0
        sc = sum(pts(arm[key]) for key in keys)
        for key in keys:
            a, c = pts(arm[key]), pts(ctl[key])
            if a > c:
                b += 1
                if key[1] in COMPACT:
                    cb += 1
                else:
                    ob += 1
            elif a < c:
                w += 1
                if key[1] in COMPACT:
                    cw += 1
                else:
                    ow += 1
            else:
                t += 1
        print("%-6s %4d   %5.1f    %d/%d/%d                         %+d / %+d" % (
            k, len(keys), 100 * sc / max(len(keys), 1), b, w, t, cb - cw, ob - ow))
    # per-map deltas for the full arm
    for k in ("both", "prod", "diss"):
        arm = data[k]
        keys = sorted(set(arm) & set(ctl))
        pm = defaultdict(int)
        for key in keys:
            d = pts(arm[key]) - pts(ctl[key])
            pm[key[1]] += d
        print("%s per-map paired delta: %s" % (
            k, dict(sorted(pm.items(), key=lambda kv: kv[1]))))
    if not decode_flag:
        return
    # falsifier stats from replays
    print("\nfalsifier medians (decoded from replays):")
    for k, d in dirs.items():
        rows = []
        replays = []
        for r in json.loads((Path(d) / "results.json").read_text()):
            if r.get("replay") and r.get("outcome") != "error":
                replays.append((Path(d) / r["replay"], r["side"]))
        with ProcessPoolExecutor(max_workers=4) as ex:
            for st in ex.map(decode, replays, chunksize=8):
                if st:
                    rows.append(st)
        def med(f):
            vals = [f(r) for r in rows if f(r) is not None]
            return statistics.median(vals) if vals else None
        fp = [r["first_pearl_round"] for r in rows if r.get("first_pearl_round") is not None]
        nb = [r["newborn_death_pct"] for r in rows if r.get("newborn_death_pct") is not None]
        print("%-6s games=%d units_r100=%.0f longest_r400=%.0f longest_r499=%.0f "
              "newborn_death_pct=%.1f first_pearl=%.0f pearls=%.0f diss=%d esc=%d cert=%d prod=%d" % (
                  k, len(rows),
                  med(lambda r: r["units_r100"]) or -1,
                  med(lambda r: r["longest_r400"]) or -1,
                  med(lambda r: r["longest_r499"]) or -1,
                  statistics.median(nb) if nb else -1,
                  statistics.median(fp) if fp else -1,
                  med(lambda r: r["pearls"]) or -1,
                  statistics.median([sum(r["act_counts"].get("diss", 0) for _ in (0,)) for r in rows]) if rows else 0,
                  med(lambda r: r["act_counts"].get("esc", 0)) or 0,
                  med(lambda r: r["act_counts"].get("cert", 0)) or 0,
                  med(lambda r: r["act_counts"].get("prod", 0)) or 0,
                  ))


if __name__ == "__main__":
    main()
