#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=18,<24", "filelock>=3.16,<4"]
# ///
"""Shared game-outcome ledger: publish, rebuild, import and merge Parquets.

Versioned contributions live in game_stats/runs/<run UUID>.parquet. The central
game_stats.parquet is their deduplicated union and is generated, not Git-merged.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid

import pyarrow as pa
import pyarrow.parquet as pq
from filelock import FileLock

ROOT = Path(__file__).resolve().parents[1]
STRINGS = ["game_id", "run_id", "game_key", "fixture_id", "source", "run_started_at",
           "bot_a", "bot_b", "bot_a_sha256", "bot_b_sha256", "map", "map_sha256",
           "mode", "runner_version", "seed", "outcome"]
COUNTS = ["a_wins", "a_losses", "b_wins", "b_losses", "draws"]
SCHEMA = pa.schema([(k, pa.string()) for k in STRINGS] +
                   [(k, pa.int32()) for k in ["rounds", "runtime_faults"] + COUNTS],
                   metadata={b"game_stats_schema_version": b"1"})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def identities(row):
    game_id = digest([row["run_id"], row["game_key"]])
    fixture_id = digest([row[k] for k in ("bot_a_sha256", "bot_b_sha256", "map_sha256",
                                         "mode", "runner_version", "seed")])
    return game_id, fixture_id


def make_record(*, run_id, game_key, source, run_started_at, bot_a, bot_b,
                bot_a_sha256, bot_b_sha256, map_name, map_sha256, mode,
                runner_version, outcome, rounds=None, runtime_faults=None, seed=None):
    """Common entry point for other runners; game_key is unique within a run.

    Reuse run_id/game_key when re-importing a game. Use another run_id or game_key
    for an intentional new game, even when the same bots/map/seed are repeated.
    """
    started = datetime.fromisoformat(run_started_at)
    if started.tzinfo is None:
        raise ValueError("run_started_at must include its timezone")
    row = dict(run_id=uuid.UUID(run_id).hex, game_key=game_key, source=source,
               run_started_at=started.astimezone(timezone.utc).isoformat(), bot_a=bot_a, bot_b=bot_b,
               bot_a_sha256=bot_a_sha256, bot_b_sha256=bot_b_sha256,
               map=map_name, map_sha256=map_sha256, mode=mode, runner_version=runner_version,
               seed=None if seed is None else str(seed), outcome=outcome, rounds=rounds,
               runtime_faults=runtime_faults, a_wins=int(outcome == "A"), a_losses=int(outcome == "B"),
               b_wins=int(outcome == "B"), b_losses=int(outcome == "A"), draws=int(outcome == "draw"))
    row["game_id"], row["fixture_id"] = identities(row)
    validate(row)
    return row


def validate(row):
    if set(row) != set(SCHEMA.names):
        raise ValueError("Game record columns do not match schema version 1")
    for key in STRINGS:
        if key == "seed" and row[key] is None:
            continue
        if not isinstance(row[key], str) or not row[key]:
            raise ValueError(f"{key} must be a nonempty string")
    if uuid.UUID(row["run_id"]).hex != row["run_id"]:
        raise ValueError("run_id must be a canonical UUID hex string")
    started = datetime.fromisoformat(row["run_started_at"])
    if started.tzinfo is None or started.astimezone(timezone.utc).isoformat() != row["run_started_at"]:
        raise ValueError("run_started_at must be canonical UTC")
    for key in ("bot_a_sha256", "bot_b_sha256", "map_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", row[key]):
            raise ValueError(f"{key} must be a SHA-256 fingerprint")
    if row["mode"] not in ("native", "sandbox") or row["outcome"] not in ("A", "B", "draw"):
        raise ValueError("Only completed native/sandbox game outcomes belong in the ledger")
    for key in ["rounds", "runtime_faults"] + COUNTS:
        if row[key] is None and key not in COUNTS:
            continue
        if type(row[key]) is not int or not 0 <= row[key] < 2**31:
            raise ValueError(f"Invalid {key}")
    expected = [int(row["outcome"] == value) for value in ("A", "B", "B", "A", "draw")]
    if [row[k] for k in COUNTS] != expected:
        raise ValueError("Win/loss/draw flags disagree with outcome")
    if (row["game_id"], row["fixture_id"]) != identities(row):
        raise ValueError("Game/fixture IDs disagree with the record's identity")


def union(records):
    """Idempotent union; contradictory copies are errors, never last-write-wins."""
    games = {}
    for row in records:
        validate(row)
        old = games.get(row["game_id"])
        if old is not None and old != row:
            changed = ", ".join(k for k in SCHEMA.names if old[k] != row[k])
            raise ValueError(f'Conflicting copies of game {row["game_id"]}: {changed}')
        games[row["game_id"]] = row
    return [games[k] for k in sorted(games)]


def read_parquet(path):
    with pq.ParquetFile(path) as file:
        table = file.read()
    if not table.schema.equals(SCHEMA, check_metadata=False) or (
            table.schema.metadata or {}).get(b"game_stats_schema_version") != b"1":
        raise ValueError(f"Unsupported game statistics schema: {path}")
    return union(table.to_pylist())


def write_parquet(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix="." + path.name, suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        pq.write_table(pa.Table.from_pylist(records, schema=SCHEMA), temporary, compression="zstd")
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def publish_games(records, root=ROOT):
    """Update per-run contributions and the central union under a process lock.

    Call with [] to rebuild after git pull/merge. Publish a batch rather than one
    game at a time when importing large historical tournaments.
    """
    root = Path(root).resolve()
    incoming = union(records)
    folder = root / "game_stats"
    runs = folder / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    with FileLock(str(folder / ".write.lock"), timeout=120):
        existing = []
        for path in sorted(runs.glob("*.parquet")):
            rows = read_parquet(path)
            if any(row["run_id"] != path.stem for row in rows):
                raise ValueError(f"Contribution filename must match its run_id: {path}")
            existing.extend(rows)
        merged = union(existing + incoming)  # Validate everything before changing any file.
        changed_runs = {row["run_id"] for row in incoming}
        for run_id in sorted(changed_runs):
            before = union(r for r in existing if r["run_id"] == run_id)
            after = [r for r in merged if r["run_id"] == run_id]
            if before != after:
                write_parquet(runs / (run_id + ".parquet"), after)
        # Contributions are authoritative. A crash before this write is repaired
        # by the next publish/rebuild; no successfully written game is lost.
        write_parquet(root / "game_stats.parquet", merged)
    return dict(total=len(merged), added=len(merged) - len(union(existing)))


def ensure_run_id(out, manifest):
    if "run_id" not in manifest:
        # Stable migration for old experiment copies, independent of local paths.
        identity = {k: manifest[k] for k in ("created", "candidate", "opponents", "maps", "hashes")}
        manifest["run_id"] = uuid.uuid5(uuid.NAMESPACE_URL, "unswbc-comparison:" + digest(identity)).hex
        temporary = out / "manifest.json.tmp"
        temporary.write_text(json.dumps(manifest, indent=2) + "\n")
        temporary.replace(out / "manifest.json")
    return manifest["run_id"]


def comparison_records(manifest, results):
    if manifest.get("version") != 1:
        raise ValueError("Unsupported comparison manifest version")
    records = []
    for game in results:
        if game["outcome"] == "error":
            continue
        if game["side"] not in ("A", "B"):
            raise ValueError("Invalid candidate side")
        candidate, opponent = manifest["candidate"], game["opponent"]
        if opponent not in manifest["opponents"] or game["map"] not in manifest["maps"]:
            raise ValueError("Result is outside the manifest's bot/map roster")
        a, b = (candidate, opponent) if game["side"] == "A" else (opponent, candidate)
        if game.get("team_a", a) != a or game.get("team_b", b) != b:
            raise ValueError("Result teams disagree with candidate side")
        winner = a if game["outcome"] == "A" else b if game["outcome"] == "B" else None
        if "winner" in game and game["winner"] != winner:
            raise ValueError("Result winner disagrees with outcome")
        key = json.dumps([opponent, game["map"], game["side"]], separators=(",", ":"))
        records.append(make_record(
            run_id=manifest["run_id"], game_key=key, source="compare_bot", run_started_at=manifest["created"],
            bot_a=a, bot_b=b, bot_a_sha256=digest(manifest["hashes"][f"bots/{a}"]),
            bot_b_sha256=digest(manifest["hashes"][f"bots/{b}"]), map_name=game["map"],
            map_sha256=manifest["hashes"][f'maps/{game["map"]}.map'],
            mode="sandbox" if manifest["settings"]["sandbox"] else "native",
            runner_version=manifest["runner_version"], outcome=game["outcome"],
            rounds=game.get("rounds"), runtime_faults=game.get("runtime_faults")))
    return records


def pair_summary(records):
    totals = {}
    for row in records:
        for side, other in (("a", "b"), ("b", "a")):
            key = (row[f"bot_{side}"], row[f"bot_{side}_sha256"], row[f"bot_{other}"],
                   row[f"bot_{other}_sha256"], row["mode"], row["runner_version"])
            value = totals.setdefault(key, dict(wins=0, losses=0, draws=0))
            value["wins"] += row[f"{side}_wins"]
            value["losses"] += row[f"{side}_losses"]
            value["draws"] += row["draws"]
    columns = ("bot", "bot_sha256", "opponent", "opponent_sha256", "mode", "runner_version")
    return [dict(zip(columns, key), **totals[key]) for key in sorted(totals)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Ledger repository root (default: this repository)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("rebuild", help="Rebuild central Parquet from tracked run contributions")
    merge = commands.add_parser("merge", help="Union external Parquets into the contribution store and central ledger")
    merge.add_argument("files", nargs="+", type=Path)
    ingest = commands.add_parser("import", help="Import existing compare_bot experiment directories")
    ingest.add_argument("experiments", nargs="+", type=Path)
    summary = commands.add_parser("summary", help="Print pairwise W/L/D as CSV, grouped by source version and runtime")
    summary.add_argument("--output", type=Path, help="Write CSV here instead of stdout")
    args = parser.parse_args(argv)
    try:
        if args.command == "summary":
            rows = pair_summary(read_parquet(args.root / "game_stats.parquet"))
            handle = args.output.open("w", newline="") if args.output else sys.stdout
            try:
                fields = ["bot", "bot_sha256", "opponent", "opponent_sha256", "mode", "runner_version", "wins", "losses", "draws"]
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            finally:
                if args.output:
                    handle.close()
            return 0
        records = []
        if args.command == "merge":
            for path in args.files:
                records.extend(read_parquet(path))
        elif args.command == "import":
            for out in args.experiments:
                manifest = json.loads((out / "manifest.json").read_text())
                ensure_run_id(out, manifest)
                records.extend(comparison_records(manifest, json.loads((out / "results.json").read_text())))
        result = publish_games(records, args.root)
        print(f'{result["added"]} games added; {result["total"]} total. Central ledger: {args.root.resolve() / "game_stats.parquet"}')
        return 0
    except Exception as exc:
        print(f"Game statistics error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
