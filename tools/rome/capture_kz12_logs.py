#!/usr/bin/env python3
"""Capture KZ12 queen-turn logs from deterministic replays of an existing panel.

The official replay file stores observations/actions but not bot stdout. This
tool reruns each existing fixture through the same installed unswbc Python
engine, records only the original queen's KZ12 diagnostic rows, and verifies
the replayed winner/length against the official run index before writing logs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.cx.arena import run_game

LOG_RE = re.compile(r"LOG KZ12 r=(-?\d+) k=(\d+) veto=(\d+) fallback=(\d+) cap=(-?\d+)")


def capture(row: dict, expected_bot: str) -> dict:
    bot_a = Path(row["botA"]).name
    bot_b = Path(row["botB"]).name
    if expected_bot not in (bot_a, bot_b):
        raise ValueError(f"{row['game']}: expected bot {expected_bot}, found {bot_a}/{bot_b}")
    side = "A" if bot_a == expected_bot else "B"
    game = run_game(
        f"maps/{row['map']}.map",
        f"bots/{row['botA']}",
        f"bots/{row['botB']}",
        seed=int(row["seed"]),
        record=side,
    )
    transcripts = game.get("transcripts") or {}
    if not transcripts:
        raise RuntimeError(f"{row['game']}: no {side} transcript captured")
    queen_key = min(transcripts, key=lambda i: int(i))
    queen_id = int(queen_key)
    queen_turns = transcripts[queen_key]["turns"]
    decisions = []
    for turn in queen_turns:
        for match in LOG_RE.finditer(turn.get("output", "")):
            r, k, veto, fallback, cap = map(int, match.groups())
            decisions.append({"round": r, "dose": k, "vetoed_directions": veto,
                              "fallback": fallback, "max_selected_Cb": cap})
    winner = game["winner"]
    rounds = int(game["rounds"])
    matched = winner == row.get("winner") and rounds == row.get("rounds")
    return {"game": row["game"], "map": row["map"], "bot": expected_bot, "side": side,
            "winner": winner, "rounds": rounds, "index_winner": row.get("winner"),
            "index_rounds": row.get("rounds"), "official_match": matched,
            "queen_id": queen_id, "decisions": decisions,
            "errors": game.get("errors", [])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument("--bot", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--resume", action="store_true", help="reuse already captured, verified game IDs in --out")
    a = ap.parse_args()
    rows = [json.loads(s) for s in a.index.read_text().splitlines() if s.strip()]
    rows = [r for r in rows if a.bot in (Path(r["botA"]).name, Path(r["botB"]).name)]
    if not rows:
        raise SystemExit("no fixtures for requested bot")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    results = []
    existing = []
    if a.resume and a.out.is_file():
        existing = [json.loads(s) for s in a.out.read_text().splitlines() if s.strip()]
        if any(not r.get("official_match") or r.get("errors") for r in existing):
            raise SystemExit("--resume input contains an unverified/mismatched record")
    seen = {r["game"] for r in existing}
    todo = [r for r in rows if r["game"] not in seen]
    results.extend(existing)
    mode = "a" if a.resume else "w"
    with a.out.open(mode) as out, ThreadPoolExecutor(a.jobs) as pool:
        futures = {pool.submit(capture, row, a.bot): row for row in todo}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            out.write(json.dumps(result) + "\n")
            out.flush()
            if i % 20 == 0:
                print(f"{len(existing) + i}/{len(rows)} fixtures", flush=True)
    mismatch = [r for r in results if not r["official_match"] or r["errors"]]
    no_log = sum(not r["decisions"] for r in results)
    no_log_maps = Counter(r["map"] for r in results if not r["decisions"])
    print(json.dumps({"fixtures": len(results), "official_mismatches": len(mismatch),
                      "engine_errors": sum(bool(r["errors"]) for r in results),
                      "without_queen_log": no_log, "without_queen_log_by_map": dict(no_log_maps),
                      "log_rows": sum(len(r["decisions"]) for r in results),
                      "out": str(a.out)}, indent=2))
    return 1 if mismatch else 0


if __name__ == "__main__":
    raise SystemExit(main())
