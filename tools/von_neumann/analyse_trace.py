#!/usr/bin/env python3
"""Summarise MC_INTENT traces from a traced Von Neumann run directory.

The runner swallows bot stdout, but LOG lines are embedded in the replay event
stream (kind 6), so decode the replays (tools/leviathan/replay.py Reader).
Counts, per game and in total: selections by intention kind, h2h strike
selections by trade class, prey chases, plus rounds and deaths for context.

Usage: .venv/bin/python -m tools.von_neumann.analyse_trace <run-dir>
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "leviathan"))
from replay import Reader  # noqa: E402


def scan(replay_path):
    counts = Counter()
    root = Reader(replay_path).object(0, 0)
    if root.num(0, "I") != 2:
        raise ValueError("Expected replay format 2")
    for ev in root.items(3):
        kind = ev.num(0, "H")
        if kind != 6:
            continue
        obj = ev.child(0)
        msg = obj.text(0)
        if not msg.startswith("MC_INTENT "):
            continue
        rec = json.loads(msg[10:])
        counts[rec.get("kind", "?")] += 1
        if rec.get("predicted") == "h2h":
            trade = rec.get("trade") or ("path-trade" if rec.get("reason") != "strike" else "favourable")
            counts["h2h:" + trade] += 1
        if rec.get("reason") == "chase":
            counts["chase"] += 1
        if rec.get("status") == "fallback":
            counts["fallback"] += 1
    return counts


def analyse(run_dir):
    rows = []
    total = Counter()
    for rp in sorted(Path(run_dir).glob("opponents/*/replays/*-candidate-*.replay")):
        c = scan(rp)
        rows.append({"replay": str(rp.relative_to(run_dir)), "counts": dict(c)})
        total.update(c)
    return rows, total


def main():
    rows, total = analyse(sys.argv[1])
    print(json.dumps({"total": dict(total), "per_game": rows}, indent=2))


if __name__ == "__main__":
    main()
