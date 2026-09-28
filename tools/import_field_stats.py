#!/usr/bin/env python3
"""Read a consistent snapshot of the running full-field tournament into the ledger.

.venv/bin/python tools/import_field_stats.py build/all-functional-bots-2026-09-25
Does not modify the tournament database, manifest, sources or running harness.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import uuid

from game_stats import ROOT, digest, make_record, publish_games


def field_records(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    if not manifest.get("prepared") or manifest["mode"] != "native":
        raise ValueError("Expected a prepared native full-field tournament")
    identity = {k: manifest[k] for k in ("created", "bots", "maps", "hashes", "mode", "runner_version")}
    run_id = uuid.uuid5(uuid.NAMESPACE_URL, "unswbc-field:" + digest(identity)).hex
    bot_hashes = {name: digest(manifest["hashes"][name]) for name in manifest["bots"]}
    map_hashes = {}
    for name in manifest["maps"]:
        expected = manifest["hashes"][name + ".map"]
        actual = hashlib.sha256((directory / "sources/maps" / (name + ".map")).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Frozen map changed: {name}")
        map_hashes[name] = expected
    # A single SELECT is a consistent SQLite read snapshot. Release its read lock
    # before hashing/conversion/publication, so the ongoing runner can keep writing.
    with sqlite3.connect((directory / "games.sqlite3").as_uri() + "?mode=ro", uri=True, timeout=30) as db:
        raw = db.execute("SELECT map,a,b,outcome,data FROM games ORDER BY map,a,b").fetchall()
    records, errors = [], 0
    for board, a, b, outcome, data in raw:
        game = json.loads(data)
        if (board, a, b, outcome) != tuple(game[k] for k in ("map", "team_a", "team_b", "outcome")):
            raise ValueError("Database key disagrees with result payload")
        if outcome == "error":
            errors += 1
            continue
        if a == b or a not in bot_hashes or b not in bot_hashes or board not in map_hashes:
            raise ValueError("Game outside the full-field roster")
        winner = a if outcome == "A" else b if outcome == "B" else None
        if game.get("winner") != winner:
            raise ValueError("Winner disagrees with outcome")
        records.append(make_record(
            run_id=run_id, game_key=json.dumps([board, a, b], separators=(",", ":")),
            source="bot_field_tournament", run_started_at=manifest["created"],
            bot_a=a, bot_b=b, bot_a_sha256=bot_hashes[a], bot_b_sha256=bot_hashes[b],
            map_name=board, map_sha256=map_hashes[board], mode="native",
            runner_version=manifest["runner_version"], outcome=outcome,
            rounds=game.get("rounds"), runtime_faults=len(game.get("runtime_faults", []))))
        # manifest.seed shuffles the schedule; it is NOT an engine game seed.
    return records, dict(run_id=run_id, completed=len(records), errors=errors,
                         scheduled=manifest["games"], manifest=manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    records, info = field_records(args.directory)
    result = publish_games(records, ROOT)
    print(f'{info["completed"]}/{info["scheduled"]} completed field games; '
          f'{result["added"]} newly published; {result["total"]} ledger games.')


if __name__ == "__main__":
    main()
