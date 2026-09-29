#!/usr/bin/env python3
"""Assemble the C1-F shared summary: exact-pair ablations + portal statistics
for every measured arm, into game_stats/runs/cx-f-benchmarks-20260930.json
(small, commit-able; the raw jsonl stay under build/)."""
from __future__ import annotations

import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parents[2]
B = HERE / "build/cx"


def load(name):
    p = B / f"{name}.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def signp(b, w):
    n = b + w
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, w) + 1)) / 2 ** n)


def pairs(base_rows, arm_rows, key):
    bi = {(r["map"], r["side"], r["seed"], r["opp"]): r for r in base_rows}
    b = w = s = 0
    for r in arm_rows:
        o = bi.get((r["map"], r["side"], r["seed"], r["opp"]))
        if not o:
            continue
        x, y = r["us"].get(key), o["us"].get(key)
        if x is None or y is None:
            continue
        b += x > y
        w += x < y
        s += x == y
    return {"b": b, "s": s, "w": w, "p": round(signp(b, w), 4)}


def portal_stats(base_rows, arm_rows):
    bi = {(r["map"], r["side"], r["seed"], r["opp"]): r for r in base_rows}
    out = {"steps": [0, 0], "deaths": [0, 0], "eaten_r100": [0, 0], "sprint": 0}
    per_map = {}
    for r in arm_rows:
        o = bi.get((r["map"], r["side"], r["seed"], r["opp"]))
        if not o:
            continue
        m = r["map"]
        pm = per_map.setdefault(m, {"steps": [0, 0], "deaths": [0, 0], "eaten": [0, 0]})
        for i, (rr, tag) in enumerate(((o, "base"), (r, "arm"))):
            out["steps"][i] += rr["us"].get("portal_steps", 0)
            out["deaths"][i] += rr["us"].get("portal_deaths", 0)
            out["eaten_r100"][i] += rr["us"].get("eaten_r100", 0)
            pm["steps"][i] += rr["us"].get("portal_steps", 0)
            pm["deaths"][i] += rr["us"].get("portal_deaths", 0)
            pm["eaten"][i] += rr["us"].get("eaten_r100", 0)
        out["sprint"] += r["us"].get("sprint_segs", 0)
        pm.setdefault("sprint", 0)
        pm["sprint"] += r["us"].get("sprint_segs", 0)
    for v in per_map.values():
        for k in ("steps", "deaths", "eaten"):
            if v[k][1]:
                v[k] = v[k]
        v["per100"] = [round(100 * v["deaths"][i] / max(1, v["steps"][i]), 1) for i in (0, 1)]
    res = {
        "steps": out["steps"], "deaths": out["deaths"],
        "per100": [round(100 * out["deaths"][i] / max(1, out["steps"][i]), 1) for i in (0, 1)],
        "eaten_r100": out["eaten_r100"],
        "sprint_per_pearl": round(out["sprint"] / max(1, out["eaten_r100"][1]), 4),
        "per_map": per_map,
    }
    return res


def main():
    base_live = load("f00-on-live")
    base_panel = load("f00-off-panel")
    arms = sys.argv[1:] or ["f01", "f02", "f02b", "f02c", "f03", "f03b", "f04",
                            "f05-on", "f05-off"]
    summary = {"generated": "2026-09-30", "task": "C1-F",
               "base": "bots/cx-f00-base (= anna-a02-chassis + ATLAS_ENABLED)",
               "arms": {}}
    base_off = load("f00-off-live")
    for a in arms:
        rows = load(f"{a}-live")
        if not rows:
            continue
        base = base_off if a.endswith("-off") else base_live  # match the atlas cell
        entry = {"n_live": len(rows),
                 "pairs": {k: pairs(base, rows, k) for k in
                           ("len_r100", "eaten_r100", "units_r100", "len_r250", "win")},
                 "portal": portal_stats(base, rows)}
        prows = load(f"{a}-panel") if "-noatlas" in a or a in ("f05-off",) else load(f"{a}-panel")
        # panel arm files: fXX-noatlas panel runs are named fXXb-panel etc; keep simple:
        summary["arms"][a] = entry
    # baseline panels: atlas inertness
    on_p, off_p = load("f00-on-panel"), load("f00-off-panel")
    if on_p and off_p:
        summary["baseline_panel_atlas"] = {
            "n": len(off_p),
            "pairs_len_r100": pairs(on_p, off_p, "len_r100"),
            "pairs_eaten_r100": pairs(on_p, off_p, "eaten_r100"),
            "note": "on-panel vs off-panel: the atlas matches nothing off-pool "
                    "(mirrored/transposed/new); differences are engine-path noise "
                    "from the ~4% of games where a view coincidentally matched",
        }
    outp = HERE / "game_stats/runs/cx-f-benchmarks-20260930.json"
    outp.write_text(json.dumps(summary, indent=1))
    print(f"wrote {outp} ({outp.stat().st_size} bytes)")
    for a, e in summary["arms"].items():
        lp = e["portal"]
        print(f"{a}: n={e['n_live']} len {e['pairs']['len_r100']} | "
              f"portal steps {lp['steps'][0]}->{lp['steps'][1]} per100 {lp['per100'][0]}->{lp['per100'][1]} "
              f"| eat100 {lp['eaten_r100'][0]}->{lp['eaten_r100'][1]} | sprint/pearl {lp['sprint_per_pearl']}")


if __name__ == "__main__":
    main()
