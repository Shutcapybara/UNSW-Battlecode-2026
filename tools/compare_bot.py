#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=18,<24", "filelock>=3.16,<4"]
# ///
"""Compare one bot with an explicit TOML roster; save replays, summaries and graphs.

uv run tools/compare_bot.py bots/leviathan-v09-arrival [--config comparison.toml]
Requires unswbc on PATH; uv supplies Python and Parquet dependencies.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import csv
from datetime import datetime, timezone
import hashlib
from html import escape
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.benchmarking.tournament import MatchWorkers, play, atomic_write
from comparison_metrics import analyse, chart, NOTES
from game_stats import comparison_records, ensure_run_id, publish_games
from stats_store import StatsStore

DEFAULTS = dict(sides=["A", "B"], jobs=4, timeout_seconds=600, sandbox=False,
                control_every=10, seed_policy="random")
IGNORED = (".git", ".unswbc-build", "__pycache__", "build", ".DS_Store")
FAULT = re.compile(r'^round \d+: bot \d+ \(team [AB]\) (?!died:).*(?:exceeded CPU limit|exited|timed out|ran out of time|timeout|broken pipe|failed).*$', re.M)


def slug(name):
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip(".") or "bot"


def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob("*")) if p.is_file()
            and not any(part in IGNORED for part in p.relative_to(directory).parts)}


def read_config(path, candidate):
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            raise ValueError("Use Python 3.11+, or install tomli for Python 3.9/3.10.") from None
    config = tomllib.loads(path.read_text())
    if set(config) - {"bots", "maps", "run"}:
        raise ValueError("Unknown TOML keys: " + ", ".join(sorted(set(config) - {"bots", "maps", "run"})))
    for kind in ("bots", "maps"):
        if not isinstance(config.get(kind), list) or not config[kind] or any(
                not isinstance(p, str) or not p for p in config[kind]):
            raise ValueError(f"{kind} must be a nonempty array of paths")
    settings = config.get("run", {})
    if not isinstance(settings, dict) or set(settings) - set(DEFAULTS):
        raise ValueError("Unknown or malformed [run] settings")
    settings = dict(DEFAULTS, **settings)
    for key in ("jobs", "control_every"):
        if type(settings[key]) is not int or settings[key] < 1:
            raise ValueError(f"run.{key} must be a positive integer")
    timeout = settings["timeout_seconds"]
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("run.timeout_seconds must be finite and positive")
    if type(settings["sandbox"]) is not bool:
        raise ValueError("run.sandbox must be true or false")
    if settings["seed_policy"] not in ("random", "fixture_hash_v1"):
        raise ValueError('run.seed_policy must be "random" or "fixture_hash_v1"')
    sides = settings["sides"]
    if not isinstance(sides, list) or not sides or any(s not in ("A", "B") for s in sides) or len(set(sides)) != len(sides):
        raise ValueError('run.sides must contain "A", "B", or both, without duplicates')
    bots = {}
    for value in config["bots"]:
        source = (path.parent / value).resolve()
        if not (source / "bot.toml").is_file():
            raise ValueError(f"Bot has no bot.toml: {source}")
        if source == candidate:
            continue
        if source.name == candidate.name or (source.name in bots and bots[source.name] != source):
            raise ValueError(f"Bot directory names must be unique: {source.name}")
        bots[source.name] = source
    maps = {}
    for value in config["maps"]:
        source = (path.parent / value).resolve()
        files = sorted(source.glob("*.map")) if source.is_dir() else [source]
        if not files:
            raise ValueError(f"Map directory contains no .map files: {source}")
        for board in files:
            board = board.resolve()
            if not board.is_file() or board.suffix != ".map":
                raise ValueError(f"Not a .map file: {board}")
            if board.stem in maps and maps[board.stem] != board:
                raise ValueError(f"Map filenames must be unique: {board.stem}")
            maps[board.stem] = board
    if not bots:
        raise ValueError("No opponents remain after excluding the candidate itself")
    for names in ([candidate.name] + list(bots), list(maps)):
        if len({slug(n) for n in names}) != len(names):
            raise ValueError("Names collide when converted to output filenames")
    return bots, maps, settings


def schedule(manifest):
    return [(opponent, board, side) for opponent in manifest["opponents"]
            for board in manifest["maps"] for side in manifest["settings"]["sides"]]


def write_csv(path, rows, fields=None):
    fields = fields or list(dict.fromkeys(key for row in rows for key in row))
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    atomic_write(path, stream.getvalue())


def aggregate(results, fixtures, key):
    groups = {}
    for opponent, board, side in fixtures:
        label = {"opponent": opponent, "map": board}
        name = tuple(label[k] for k in key)
        row = groups.setdefault(name, dict(zip(key, name), scheduled=0, played=0, wins=0,
                                          draws=0, losses=0, errors=0, analysis_errors=0))
        row["scheduled"] += 1
    for game in results:
        row = groups[tuple(game[k] for k in key)]
        if game["outcome"] == "error":
            row["errors"] += 1
        else:
            row["played"] += 1
            metric = "draws" if game["outcome"] == "draw" else "wins" if game["outcome"] == game["side"] else "losses"
            row[metric] += 1
        row["analysis_errors"] += bool(game.get("analysis_error"))
    for row in groups.values():
        row["pending"] = row["scheduled"] - row["played"] - row["errors"]
        row["score"] = (row["wins"] + .5 * row["draws"]) / row["played"] if row["played"] else None
    return list(groups.values())


def save_report(out, manifest, results, status):
    fixtures = schedule(manifest)
    atomic_write(out / "results.json", json.dumps(results, indent=2) + "\n")
    write_csv(out / "games.csv", results, fields=list(dict.fromkeys(
        ["opponent", "map", "side", "outcome", "winner", "rounds", "seconds", "error", "analysis_error"] +
        [k for r in results for k in r])))
    summaries = {}
    for label, keys in (("bot", ["opponent"]), ("map", ["map"]), ("bot_and_map", ["opponent", "map"])):
        summaries[label] = aggregate(results, fixtures, keys)
        write_csv(out / f"summary_by_{label}.csv", summaries[label])
    wins = sum(r["outcome"] == r["side"] for r in results)
    draws = sum(r["outcome"] == "draw" for r in results)
    losses = sum(r["outcome"] not in (r["side"], "draw", "error") for r in results)
    progress = dict(status=status, scheduled=len(fixtures), recorded=len(results), wins=wins, draws=draws,
                    losses=losses, errors=sum(r["outcome"] == "error" for r in results),
                    analysis_errors=sum(bool(r.get("analysis_error")) for r in results),
                    runtime_faults=sum(r.get("runtime_faults", 0) for r in results),
                    updated=datetime.now(timezone.utc).isoformat())
    atomic_write(out / "progress.json", json.dumps(progress, indent=2) + "\n")
    text = [f'# Comparison: {manifest["candidate"]}\n',
            f'{status}: {len(results)}/{len(fixtures)} games recorded; {wins}W {draws}D {losses}L. '
            f'{progress["errors"]} game errors, {progress["analysis_errors"]} analysis errors, '
            f'{progress["runtime_faults"]} reported bot runtime faults.\n',
            'All W/D/L and scores are from the candidate\'s perspective. Score = (wins + 0.5 × draws) / played. '
            'Errors are not draws and are excluded from scores.\n',
            f'Mode: {"judge sandbox" if manifest["settings"]["sandbox"] else "native (not judge CPU validation)"}. '
            f'Seed policy: {manifest["settings"].get("seed_policy", "random")}.\n', NOTES,
            '\n| Opponent | W | D | L | Errors | Pending |\n|---|---:|---:|---:|---:|---:|']
    text += [f'| {r["opponent"]} | {r["wins"]} | {r["draws"]} | {r["losses"]} | {r["errors"]} | {r["pending"]} |' for r in summaries["bot"]]
    atomic_write(out / "summary.md", "\n".join(text) + "\n")
    page = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>Bot comparison</title><style>body{font:16px system-ui;max-width:1200px;margin:30px auto;padding:0 20px;color:#25313c;background:#fafaf8}table{border-collapse:collapse;width:100%;margin:15px 0}td,th{padding:8px;text-align:left;border-bottom:1px solid #d5dce1}a{color:#12699c}p{line-height:1.5}details{margin:20px 0}img{max-width:100%}</style>',
            f'<h1>{escape(manifest["candidate"])}</h1><p><b>{escape(text[1])}</b></p>',
            f'<p>{escape(text[2])} {escape(text[3])}</p>',
            '<p><a href="games.csv">Every game and final statistics</a> · <a href="summary_by_bot.csv">By opponent</a> · <a href="summary_by_map.csv">By map</a> · <a href="summary_by_bot_and_map.csv">Opponent × map</a> · <a href="manifest.json">Run manifest</a></p>',
            f'<details><summary>Metric definitions and limitations</summary><p>{escape(NOTES)}</p></details>']
    for label, keys in (("Opponent", "bot"), ("Map", "map")):
        page.append(f'<h2>By {label.lower()}</h2><table><tr><th>{label}</th><th>W</th><th>D</th><th>L</th><th>Errors</th><th>Pending</th></tr>')
        for r in summaries[keys]:
            page.append('<tr>' + ''.join(f'<td>{escape(str(v))}</td>' for v in
                         [r["opponent" if keys == "bot" else "map"], r["wins"], r["draws"], r["losses"], r["errors"], r["pending"]]) + '</tr>')
        page.append('</table>')
    for opponent in manifest["opponents"]:
        page.append(f'<h2>{escape(opponent)}</h2><table><tr><th>Map</th><th>Candidate side</th><th>Result</th><th>Artifacts</th></tr>')
        for r in results:
            if r["opponent"] != opponent:
                continue
            result = "error" if r["outcome"] == "error" else "draw" if r["outcome"] == "draw" else "win" if r["outcome"] == r["side"] else "loss"
            links = " · ".join(f'<a href="{quote(r[k])}">{k}</a>' for k in ("replay", "graph", "statistics", "series", "log")
                                if r.get(k) and (out / r[k]).is_file())
            error = r.get("error") or r.get("analysis_error")
            if error:
                links += '<br>' + escape(error)
            page.append(f'<tr><td>{escape(r["map"])}</td><td>{r["side"]}</td><td>{result}</td><td>{links}</td></tr>')
        page.append('</table>')
    atomic_write(out / "index.html", "\n".join(page) + '</html>\n')


def prepare(candidate, bots, maps, settings, config, executable):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    out = ROOT / "experiment_data" / f"{slug(candidate.name)}_{stamp}"
    out.mkdir(parents=True)
    manifest = dict(version=1, run_id=uuid.uuid4().hex, created=datetime.now(timezone.utc).isoformat(), timestamp=int(stamp),
                    candidate=candidate.name, opponents=list(bots), maps=list(maps), settings=settings,
                    original_config=str(config), original_bots={n: str(p) for n, p in {candidate.name: candidate, **bots}.items()},
                    original_maps={n: str(p) for n, p in maps.items()}, hashes={}, runner=executable,
                    analysis_sources={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in (Path(__file__), ROOT / "tools/game_stats.py", ROOT / "tools/comparison_metrics.py",
                                                ROOT / "tools/public_replay_review.py", ROOT / "tools/leviathan/replay.py",
                                                ROOT / "tools/ouroboros/mapview.py", ROOT / "tools/benchmarking/tournament.py")},
                    runner_version=subprocess.check_output([executable, "--version"], text=True).strip())
    for name, source in {candidate.name: candidate, **bots}.items():
        before = hashes(source)
        target = out / "sources/bots" / name
        shutil.copytree(source, target, ignore=shutil.ignore_patterns(*IGNORED))
        if before != hashes(target) or before != hashes(source):
            raise ValueError(f"Bot source changed during snapshot: {source}")
        manifest["hashes"][f"bots/{name}"] = before
    (out / "sources/maps").mkdir(parents=True)
    for name, source in maps.items():
        target = out / "sources/maps" / (name + ".map")
        shutil.copy2(source, target)
        manifest["hashes"][f"maps/{name}.map"] = hashlib.sha256(target.read_bytes()).hexdigest()
    shutil.copy2(config, out / "comparison.toml")
    atomic_write(out / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    return out, manifest


def match(out, manifest, fixture, workers):
    opponent, board, side = fixture
    name, settings = manifest["candidate"], manifest["settings"]
    candidate = out / "sources/bots" / name
    rival = out / "sources/bots" / opponent
    a, b = (candidate, rival) if side == "A" else (rival, candidate)
    folder = out / "opponents" / slug(opponent)
    for sub in ("replays", "graphs", "stats"):
        (folder / sub).mkdir(parents=True, exist_ok=True)
    label = slug(board) + "-candidate-" + side
    seed = None
    if settings.get("seed_policy", "random") == "fixture_hash_v1":
        material = f"gavroche-comparison-seed-v1\0{opponent}\0{board}".encode()
        seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    row = play(manifest["runner"], out / "sources/maps" / (board + ".map"), a, b,
               folder / "replays", label, settings["timeout_seconds"], True, workers,
               settings["sandbox"], seed=seed)
    row.update(opponent=opponent, side=side, analysis_error=None)
    if seed is not None:
        row["seed"] = str(seed)
    for key in ("log", "replay"):
        if row[key]:
            row[key] = str((folder / "replays" / row[key]).relative_to(out))
    row["runtime_faults"] = len(FAULT.findall((out / row["log"]).read_text(errors="replace")))
    if row["outcome"] == "error":
        return row
    try:
        if not row["replay"]:
            raise ValueError("Runner produced a result but no replay")
        stats = analyse(out / row["replay"], settings["control_every"])
        if stats["winner"] != row["outcome"] or stats["rounds"] != row["rounds"]:
            raise ValueError("Replay result disagrees with runner output")
        row["reason"] = stats["reason"]
        for key, suffix in (("statistics", "json"), ("series", "csv")):
            row[key] = str((folder / "stats" / (label + "." + suffix)).relative_to(out))
        atomic_write(out / row["statistics"], json.dumps(stats, separators=(",", ":")) + "\n")
        points = [dict(team=t, bot=name if t == side else opponent, **p) for t in "AB" for p in stats["series"][t]]
        write_csv(out / row["series"], points)
        row["graph"] = str((folder / "graphs" / (label + ".svg")).relative_to(out))
        chart(out / row["graph"], stats, name, opponent, side, board)
        for t in "AB":
            prefix = "candidate_" if t == side else "opponent_"
            row.update({prefix+k: v for k, v in stats["series"][t][-1].items() if k != "round"})
    except Exception as exc:
        row["analysis_error"] = f"{type(exc).__name__}: {exc}"
    return row


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bot", nargs="?", type=Path, help="Candidate directory containing bot.toml")
    parser.add_argument("--config", type=Path, help="Comparison TOML (default: repository comparison.toml)")
    parser.add_argument("--jobs", type=int, help="Override concurrency")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print fixtures without running or writing")
    parser.add_argument("--resume", type=Path, help="Resume an existing experiment using its frozen sources/configuration")
    args = parser.parse_args(argv)
    try:
        if args.jobs is not None and args.jobs < 1:
            raise ValueError("--jobs must be positive")
        if args.resume:
            if args.bot or args.config:
                raise ValueError("--resume uses the saved candidate/config; omit bot and --config")
            out = args.resume.resolve()
            manifest = json.loads((out / "manifest.json").read_text())
            if manifest.get("version") != 1:
                raise ValueError("Unsupported experiment manifest version")
            for relative, expected in manifest["hashes"].items():
                source = out / "sources" / relative
                actual = hashes(source) if source.is_dir() else hashlib.sha256(source.read_bytes()).hexdigest()
                if actual != expected:
                    raise ValueError(f"Frozen input changed: {relative}")
            results = json.loads((out / "results.json").read_text()) if (out / "results.json").exists() else []
        else:
            if not args.bot or not (args.bot.resolve() / "bot.toml").is_file():
                raise ValueError("Provide a candidate directory containing bot.toml")
            candidate = args.bot.resolve()
            config = (args.config or ROOT / "comparison.toml").resolve()
            bots, maps, settings = read_config(config, candidate)
            manifest = dict(candidate=candidate.name, opponents=list(bots), maps=list(maps), settings=settings)
            results = []
        jobs = args.jobs or manifest["settings"]["jobs"]
        fixtures = schedule(manifest)
        print(f'{manifest["candidate"]}: {len(manifest["opponents"])} opponents × {len(manifest["maps"])} maps × '
              f'{len(manifest["settings"]["sides"])} sides = {len(fixtures)} games', flush=True)
        if args.dry_run:
            for opponent, board, side in fixtures:
                print(f"  {board}: vs {opponent}, candidate side {side}")
            return 0
        executable = shutil.which("unswbc")
        if executable is None:
            raise ValueError("unswbc was not found on PATH")
        if args.resume:
            if subprocess.check_output([executable, "--version"], text=True).strip() != manifest["runner_version"]:
                raise ValueError("unswbc version changed; start a new experiment")
            manifest["runner"] = executable
        else:
            settings["jobs"] = jobs
            out, manifest = prepare(candidate, bots, maps, settings, config, executable)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Output: {out}", flush=True)
    ensure_run_id(out, manifest)
    local_stats = StatsStore(queue_only=True)
    local_run_id = local_stats.start_run(producer='compare_bot', manifest=manifest, run_id=manifest['run_id'])
    try:
        persisted = comparison_records(manifest, results)
        for record in persisted:
            local_stats.append_match(local_run_id, record['game_key'], record)
        ledger = publish_games(persisted, ROOT)
        print(f'Game ledger: {ledger["total"]} games ({ledger["added"]} added)', flush=True)
    except Exception as exc:
        print(f"Game ledger error: {exc}. Results preserved; resolve the ledger error and resume.", file=sys.stderr)
        return 1
    by_fixture = {(r["opponent"], r["map"], r["side"]): r for r in results}
    # A successful match stays complete even if its replay artifact was not
    # transferred. Replaying it would use a fresh random seed and replace the
    # recorded sample, because unswbc does not seed matches by default.
    pending = iter(f for f in fixtures if f not in by_fixture or by_fixture[f]["outcome"] == "error"
                   or by_fixture[f].get("analysis_error"))
    save_report(out, manifest, results, "running")
    with tempfile.TemporaryDirectory(prefix="comparison-builds-") as workspace:
        workers = MatchWorkers(workspace)
        pool = ThreadPoolExecutor(max_workers=jobs)
        active = {}

        def submit():
            fixture = next(pending, None)
            if fixture:
                active[pool.submit(match, out, manifest, fixture, workers)] = fixture

        try:
            for _ in range(jobs):
                submit()
            while active:
                finished, _ = wait(active, return_when=FIRST_COMPLETED)
                for future in finished:
                    fixture = active.pop(future)
                    try:
                        row = future.result()
                    except Exception as exc:
                        row = dict(opponent=fixture[0], map=fixture[1], side=fixture[2], outcome="error",
                                   winner=None, error=f"{type(exc).__name__}: {exc}", analysis_error=None)
                    by_fixture[fixture] = row
                    results = [by_fixture[f] for f in fixtures if f in by_fixture]
                    save_report(out, manifest, results, "running")
                    records = comparison_records(manifest, [row])
                    for record in records:
                        local_stats.append_match(local_run_id, record['game_key'], record)
                    if row["outcome"] != "error":
                        publish_games(records, ROOT)
                    print(f'[{len(results)}/{len(fixtures)}] {fixture}: {row["outcome"]}' +
                          (f' — {row.get("error") or row.get("analysis_error")}' if row.get("error") or row.get("analysis_error") else ''), flush=True)
                    submit()
        except KeyboardInterrupt:
            workers.cancel()
            save_report(out, manifest, results, "interrupted")
            print(f"Interrupted; completed results saved. Resume with --resume {out}", flush=True)
            return 130
        except Exception as exc:
            workers.cancel()
            save_report(out, manifest, results, "interrupted with error")
            print(f"Comparison stopped: {exc}. Completed results saved; resolve the error and resume with --resume {out}", file=sys.stderr)
            return 1
        finally:
            workers.cancel()
            pool.shutdown(wait=True, cancel_futures=True)
            local_stats.close()
    errors = sum(r["outcome"] == "error" or bool(r.get("analysis_error")) for r in results)
    save_report(out, manifest, results, "finished with errors" if errors else "complete")
    print(f"Report: {out / 'index.html'}", flush=True)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
