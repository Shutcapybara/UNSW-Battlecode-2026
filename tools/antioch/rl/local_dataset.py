"""Generate a fresh, frozen HB1-feature pilot without the historical parquet files.

    .venv/bin/python tools/antioch/rl/local_dataset.py plan
    .venv/bin/python tools/antioch/rl/local_dataset.py run --dry-run
    .venv/bin/python tools/antioch/rl/local_dataset.py run --jobs 8
    .venv/bin/python tools/antioch/rl/local_dataset.py extract --jobs 8
    .venv/bin/python tools/antioch/rl/local_dataset.py audit

The 100-game pilot uses five training maps, five opponents, both seats, and
seeds 101/102. Twenty games are held out before running; both seats of each
matchup belong to the same partition. Pool/gen fixtures are excluded. Replay
and outcome metadata are never model features. This is a dataset for measuring
compression fidelity, not a reproduction of historical expert accuracy.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.metadata
import json
import multiprocessing
from pathlib import Path
import random
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.analysis.features.run_panel import runtime_fingerprint
from tools.antioch.rl.gbt_direction_curve import MODEL, array
from tools.carthage import lane

DEFAULT_OUT = ROOT / "build/antioch/rl/local-pilot-v1"
BOT = "carthage-05-free-sprint"
OPPONENTS = lane.ZOO[:5]
SEEDS = (101, 102)
SPLIT_SEED = 62
SAMPLE_SEED = 20261003


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    partial = Path(str(path) + ".tmp")
    partial.write_text(json.dumps(value, indent=2) + "\n")
    partial.replace(path)


def make_manifest():
    maps = list(lane.TRAIN_MAPS)
    if set(maps) & (set(lane.LIVE_MAPS) | set(lane.GEN_MAPS)):
        raise ValueError("Training maps overlap a reserved evaluation panel")
    fixtures = []
    rng = random.Random(SPLIT_SEED)
    for map_name in maps:
        groups = [(seed, opponent) for seed in SEEDS for opponent in OPPONENTS]
        holdout = set(rng.sample(groups, len(groups) // 5))
        for seed, opponent in groups:
            pair = f"s{seed}__{map_name}__{opponent}"
            for seat in ("A", "B"):
                game = len(fixtures) + 1
                bot_a, bot_b = (BOT, opponent) if seat == "A" else (opponent, BOT)
                fixtures.append(dict(game_id=game, game=f"{game:04d}__{pair}__{seat}",
                                     pair=pair, panel="train", map=map_name, seed=seed,
                                     botA=bot_a, botB=bot_b, opp=opponent, seat=seat,
                                     partition="holdout" if (seed, opponent) in holdout else "train"))
    names = re.findall(r'"([^"]+)"', array(MODEL.read_text(), "dirc_feats"))
    return dict(schema="antioch-local-hb1-pilot-v1", runtime=importlib.metadata.version("unswbc"),
                bot=BOT, source_fingerprints={bot: runtime_fingerprint(ROOT / "bots" / bot)
                                             for bot in [BOT, *OPPONENTS]},
                map_sha256={m: sha256(ROOT / "maps" / f"{m}.map") for m in maps},
                feature_source_sha256={str(p.relative_to(ROOT)): sha256(p) for p in [
                    ROOT / "tools/team_recon_claude/features_v5.py",
                    ROOT / "tools/team_recon_claude/features_view.py",
                    ROOT / "tools/team_recon_claude/roundblock.py",
                    ROOT / "tools/team_recon_claude/recon.py"]},
                teacher_model=str(MODEL.relative_to(ROOT)), teacher_model_sha256=sha256(MODEL),
                feature_names=names, split_seed=SPLIT_SEED, sample_seed=SAMPLE_SEED,
                sampling="Uniform without replacement, at most 2000 eligible move states per game; full actor rows retained separately",
                sample_cap=2000, holdout_game_ids=[f["game_id"] for f in fixtures if f["partition"] == "holdout"],
                split="Whole games; both seats of each map/opponent/seed pair share a partition; two holdout pairs per map",
                purpose="Fresh full-model teacher fidelity; no historical expert-accuracy claim or policy fitting",
                candidate_screen={"reference_rounds": 540, "minimum_upload_saving_fraction": 0.10,
                                  "paired_agreement_delta_90pct_ci_lower_bound": -0.005,
                                  "scope": "Screen only; actual reserved pool/gen evaluation is required before adoption"},
                fixtures=fixtures)


def load_manifest(out):
    path = out / "manifest.json"
    if not path.exists():
        raise SystemExit("Run the plan stage first")
    manifest = json.loads(path.read_text())
    current = make_manifest()
    if manifest != current:
        raise SystemExit("Frozen manifest no longer matches runtime, inputs or roster; use a new output directory")
    if manifest["runtime"] != "1.2.5":
        raise SystemExit("This pilot requires unswbc==1.2.5")
    return manifest


def plan(out):
    manifest = make_manifest()
    if manifest["runtime"] != "1.2.5":
        raise SystemExit("This pilot requires unswbc==1.2.5")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "manifest.json").exists():
        load_manifest(out)
    else:
        write_json(out / "manifest.json", manifest)
    bind_producer(out, manifest)
    print(json.dumps(dict(manifest=str(out / "manifest.json"), games=len(manifest["fixtures"]),
                          train_games=80, holdout_games=20, maps=lane.TRAIN_MAPS,
                          opponents=OPPONENTS, seeds=SEEDS), indent=2), flush=True)


def index_rows(out):
    path = out / "index.jsonl"
    if not path.exists():
        return {}
    rows = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["game_id"] in rows:
            raise ValueError(f"Duplicate index entry for game {row['game_id']}")
        rows[row["game_id"]] = row
    return rows


def producer_inputs(out, manifest):
    return dict(manifest_sha256=sha256(out / "manifest.json"),
                builder_sha256=sha256(Path(__file__)), runner_sha256=sha256(Path(lane.__file__)),
                reconstruction_sources=manifest["feature_source_sha256"], runtime=manifest["runtime"])


def bind_producer(out, manifest, adopt=False):
    path = out / "producer.json"
    expected = producer_inputs(out, manifest)
    if path.exists():
        if json.loads(path.read_text())["inputs"] != expected:
            raise ValueError("Producer inputs changed; keep this dataset frozen and use a new output directory")
    else:
        if not adopt and ((out / "index.jsonl").exists() or list((out / "rows").glob("*.json"))):
            raise ValueError("Existing artifacts have no producer receipt; run the explicit audit stage first")
        write_json(path, dict(inputs=expected,
                              recorded="after completion and adoption audit" if adopt else "before generation",
                              source_hash_scope="code at receipt; initial pilot had validation-only edits during generation" if adopt else "code before generation"))
        (out / "producer-source.py").write_bytes(Path(__file__).read_bytes())


def run(out, jobs, limit, dry_run):
    manifest = load_manifest(out)
    existing = index_rows(out)
    fixtures = manifest["fixtures"][:limit] if limit else manifest["fixtures"]
    pending = [f for f in fixtures if f["game_id"] not in existing]
    if dry_run:
        print(json.dumps(dict(games=len(fixtures), pending=len(pending), jobs=jobs,
                              partitions={p: sum(f["partition"] == p for f in fixtures)
                                          for p in ("train", "holdout")},
                              first_fixture=fixtures[0]), indent=2))
        return
    bind_producer(out, manifest)
    for fixture in fixtures:
        replay = out / "replays" / (fixture["game"] + ".replay")
        row = existing.get(fixture["game_id"])
        if row and (row["rc"] or row["winner"] not in ("A", "B", "draw") or not replay.exists()
                    or sha256(replay) != row["replay_sha256"]):
            raise SystemExit(f"Existing fixture {fixture['game_id']} is failed, missing or changed")
        if not row and replay.exists():
            raise SystemExit(f"Unindexed replay {replay}; inspect before resuming")
    if not pending:
        print(f"All {len(fixtures)} requested fixtures are already complete; timing report retained", flush=True)
        return
    (out / "replays").mkdir(exist_ok=True)
    for bot in sorted({f[key] for f in pending for key in ("botA", "botB")}):
        lane.prebuild(bot)
    started = time.monotonic()
    spec = dict(bot=BOT, params="", policy="")
    failures = []
    with (out / "index.jsonl").open("a") as index, ThreadPoolExecutor(jobs) as executor:
        futures = {executor.submit(lane.run_one, f, out, spec): f for f in pending}
        for number, future in enumerate(as_completed(futures), 1):
            row = future.result()
            if row is None:
                raise RuntimeError("Runner skipped an unindexed replay")
            replay = out / row["replay"]
            row["replay_sha256"] = sha256(replay) if replay.exists() else None
            index.write(json.dumps(row) + "\n")
            index.flush()
            if row["rc"] or row["winner"] not in ("A", "B", "draw") or not replay.exists():
                failures.append(row["game_id"])
            print(f"games {number}/{len(pending)}: id={row['game_id']} {row['map']} "
                  f"{row['seat']} {row['winner']} {row['seconds']}s rc={row['rc']}", flush=True)
    rows = list(index_rows(out).values())
    report = dict(runtime=manifest["runtime"], completed_games=len(rows), failures=failures,
                  this_run_wall_seconds=round(time.monotonic() - started, 3), jobs=jobs,
                  cumulative_game_seconds=sum(r["seconds"] for r in rows),
                  replay_bytes=sum((out / r["replay"]).stat().st_size for r in rows if (out / r["replay"]).exists()),
                  manifest_sha256=sha256(out / "manifest.json"))
    write_json(out / "run-report.json", report)
    print(json.dumps(report, indent=2), flush=True)
    if failures:
        raise SystemExit("Failed pilot fixtures: " + str(failures))


def extract_one(work):
    import numpy as np
    import pandas as pd
    from tools.team_recon_claude.features_v5 import extract as features

    out, fixture, result, manifest = work
    game_id = fixture["game_id"]
    prefix = out / "rows" / f"{game_id:04d}"
    report_path = Path(str(prefix) + ".json")
    raw_path = Path(str(prefix) + ".parquet")
    sample_path = Path(str(prefix) + ".sample.parquet")
    replay = out / result["replay"]
    if sha256(replay) != result["replay_sha256"]:
        raise ValueError(f"Changed replay for game {game_id}")
    if report_path.exists():
        report = json.loads(report_path.read_text())
        if (report.get("replay_sha256") != result["replay_sha256"] or report.get("side") != fixture["seat"]
                or report.get("partition") != fixture["partition"]):
            raise ValueError(f"Cached extraction provenance differs for game {game_id}")
        if report.get("raw_sha256") != sha256(raw_path) or report.get("sample_sha256") != sha256(sample_path):
            raise ValueError(f"Changed extracted files for game {game_id}")
        expected_score = 0.5 if result["winner"] == "draw" else float(result["winner"] == fixture["seat"])
        for path in (raw_path, sample_path):
            scores = pd.read_parquet(path, columns=["game_score"])["game_score"]
            if not scores.eq(expected_score).all():
                raise ValueError(f"Cached outcome metadata differs for game {game_id}")
        return report
    started = time.monotonic()
    rows, game, description = features(str(replay), fixture["seat"], game_id)
    invalid = {k: v for k, v in description["checks"].items() if v and (k.endswith("bad") or k.endswith("mismatch"))}
    if invalid:
        raise ValueError(f"Replay reconstruction failed for game {game_id}: {invalid}")
    frame = pd.DataFrame(rows)
    missing = set(manifest["feature_names"]) - set(frame.columns)
    if frame.empty or missing:
        raise ValueError(f"Game {game_id}: empty rows or missing model features {sorted(missing)}")
    frame["side"] = fixture["seat"]
    frame["partition"] = fixture["partition"]
    frame["pair"] = fixture["pair"]
    frame["map"] = fixture["map"]
    frame["seed"] = fixture["seed"]
    frame["is_queen"] = frame["dragon"].isin([0, 1]).astype("int8")
    frame["game_score"] = 0.5 if result["winner"] == "draw" else float(result["winner"] == fixture["seat"])
    frame["actor_turn"] = np.arange(len(frame))
    metadata = ["game", "dragon", "side", "partition", "pair", "map", "seed", "is_queen", "game_score", "actor_turn",
                "y_family", "y_first", "y_nsteps", "y_seq", "y_split", "post_died", "post_reason"]
    frame = frame[list(dict.fromkeys(manifest["feature_names"] + metadata))]
    partial = Path(str(raw_path) + ".tmp")
    frame.to_parquet(partial, index=False)
    partial.replace(raw_path)
    eligible = frame[(frame.y_family == "move") & frame.y_first.isin(["F", "R", "L"])]
    chosen = np.random.default_rng(manifest["sample_seed"] + game_id).choice(
        len(eligible), min(len(eligible), manifest["sample_cap"]), replace=False)
    sample = eligible.iloc[np.sort(chosen)].copy()
    sample["eligible_game_rows"] = len(eligible)
    sample["sampling_weight"] = len(eligible) / len(sample) if len(sample) else 0
    partial = Path(str(sample_path) + ".tmp")
    sample.to_parquet(partial, index=False)
    partial.replace(sample_path)
    report = dict(game_id=game_id, side=fixture["seat"], partition=fixture["partition"],
                  raw_rows=len(frame), eligible_rows=len(eligible), sample_rows=len(sample),
                  queen_sample_rows=int(sample.is_queen.sum()), late_sample_rows=int((sample["round"] >= 350).sum()),
                  seconds=round(time.monotonic() - started, 3), checks=description["checks"],
                  replay_sha256=result["replay_sha256"], raw_sha256=sha256(raw_path), sample_sha256=sha256(sample_path))
    write_json(report_path, report)
    return report


def extract(out, jobs, limit):
    import pandas as pd

    manifest = load_manifest(out)
    bind_producer(out, manifest)
    if (out / "extraction-receipt.json").exists():
        audit(out)
        print("Completed dataset verified; existing data and timing reports retained", flush=True)
        return
    indexed = index_rows(out)
    fixtures = manifest["fixtures"][:limit] if limit else manifest["fixtures"]
    missing = [f["game_id"] for f in fixtures if f["game_id"] not in indexed]
    if missing:
        raise SystemExit(f"Games not run yet: {missing}")
    for fixture in fixtures:
        result = indexed[fixture["game_id"]]
        if result["rc"] or result["winner"] not in ("A", "B", "draw"):
            raise SystemExit(f"Game {fixture['game_id']} failed")
    (out / "rows").mkdir(exist_ok=True)
    work = [(out, f, indexed[f["game_id"]], manifest) for f in fixtures]
    started = time.monotonic()
    reports = []
    # fork avoids Python 3.14's default forkserver socket in restricted hosts.
    with multiprocessing.get_context("fork").Pool(jobs) as pool:
        for number, report in enumerate(pool.imap_unordered(extract_one, work), 1):
            reports.append(report)
            print(f"extract {number}/{len(work)}: id={report['game_id']} "
                  f"{report['raw_rows']} rows / {report['sample_rows']} sampled / {report['seconds']}s", flush=True)
    reports.sort(key=lambda r: r["game_id"])
    dataset = pd.concat([pd.read_parquet(out / "rows" / f"{r['game_id']:04d}.sample.parquet")
                         for r in reports], ignore_index=True)
    dataset_path = out / ("dataset.parquet" if not limit else f"dataset-first-{limit}.parquet")
    partial = Path(str(dataset_path) + ".tmp")
    dataset.to_parquet(partial, index=False)
    partial.replace(dataset_path)
    report = dict(runtime=manifest["runtime"], games=len(reports), raw_rows=sum(r["raw_rows"] for r in reports),
                  eligible_rows=sum(r["eligible_rows"] for r in reports), sample_rows=len(dataset),
                  feature_count=len(manifest["feature_names"]), partition_games=dataset.groupby("partition").game.nunique().to_dict(),
                  partition_rows=dataset.partition.value_counts().to_dict(), queen_sample_rows=int(dataset.is_queen.sum()),
                  late_sample_rows=int((dataset["round"] >= 350).sum()),
                  wall_seconds=round(time.monotonic() - started, 3), jobs=jobs,
                  manifest_sha256=sha256(out / "manifest.json"), dataset_sha256=sha256(dataset_path),
                  dataset=str(dataset_path.relative_to(ROOT)) if dataset_path.is_relative_to(ROOT) else str(dataset_path),
                  checks={key: sum(r["checks"].get(key, 0) for r in reports) for key in {k for r in reports for k in r["checks"]}},
                  games_report=reports)
    write_json(out / ("dataset-report.json" if not limit else f"dataset-first-{limit}-report.json"), report)
    print(json.dumps({k: v for k, v in report.items() if k != "games_report"}, indent=2), flush=True)
    if not limit:
        audit(out)


def audit(out):
    """Adopt legacy pilot output only after checking every file and sample."""
    import numpy as np
    import pandas as pd

    manifest = load_manifest(out)
    indexed = index_rows(out)
    fixtures = manifest["fixtures"]
    if set(indexed) != {f["game_id"] for f in fixtures}:
        raise ValueError("Index does not contain exactly the frozen fixture roster")
    previous = out / "extraction-receipt.json"
    if previous.exists():
        bind_producer(out, manifest)
    records, samples = [], []
    for fixture in fixtures:
        game_id = fixture["game_id"]
        result = indexed[game_id]
        if any(result.get(key) != value for key, value in fixture.items()):
            raise ValueError(f"Index fixture changed for game {game_id}")
        replay = out / "replays" / (fixture["game"] + ".replay")
        if result["replay"] != str(replay.relative_to(out)) or result["rc"] or result["winner"] not in ("A", "B", "draw"):
            raise ValueError(f"Invalid result for game {game_id}")
        replay_hash = sha256(replay)
        prefix = out / "rows" / f"{game_id:04d}"
        raw_path, sample_path = Path(str(prefix) + ".parquet"), Path(str(prefix) + ".sample.parquet")
        report = json.loads(Path(str(prefix) + ".json").read_text())
        raw_hash, sample_hash = sha256(raw_path), sha256(sample_path)
        if (replay_hash != result["replay_sha256"] or replay_hash != report["replay_sha256"]
                or raw_hash != report["raw_sha256"] or sample_hash != report["sample_sha256"]):
            raise ValueError(f"Artifact hash mismatch for game {game_id}")
        raw, sample = pd.read_parquet(raw_path), pd.read_parquet(sample_path)
        score = 0.5 if result["winner"] == "draw" else float(result["winner"] == fixture["seat"])
        for frame in (raw, sample):
            expected = dict(game=game_id, side=fixture["seat"], partition=fixture["partition"],
                            pair=fixture["pair"], map=fixture["map"], seed=fixture["seed"], game_score=score)
            if frame.empty or any(not frame[key].eq(value).all() for key, value in expected.items()):
                raise ValueError(f"Cached metadata mismatch for game {game_id}")
            if not frame["is_queen"].eq(frame.dragon.isin([0, 1]).astype("int8")).all():
                raise ValueError(f"Queen metadata mismatch for game {game_id}")
        if not np.array_equal(raw.actor_turn, np.arange(len(raw))):
            raise ValueError(f"Actor-turn keys changed for game {game_id}")
        eligible = raw[(raw.y_family == "move") & raw.y_first.isin(["F", "R", "L"])]
        chosen = np.random.default_rng(manifest["sample_seed"] + game_id).choice(
            len(eligible), min(len(eligible), manifest["sample_cap"]), replace=False)
        expected_sample = eligible.iloc[np.sort(chosen)].reset_index(drop=True)
        common = list(raw.columns)
        if not expected_sample.equals(sample[common].reset_index(drop=True)):
            raise ValueError(f"Sample does not match frozen sampling recipe for game {game_id}")
        if not sample.eligible_game_rows.eq(len(eligible)).all() or not sample.sampling_weight.eq(len(eligible) / len(sample)).all():
            raise ValueError(f"Sampling weight mismatch for game {game_id}")
        if (report["raw_rows"], report["eligible_rows"], report["sample_rows"]) != (len(raw), len(eligible), len(sample)):
            raise ValueError(f"Report counts changed for game {game_id}")
        if any(v and (k.endswith("bad") or k.endswith("mismatch")) for k, v in report["checks"].items()):
            raise ValueError(f"Bad reconstruction checks for game {game_id}")
        samples.append(sample)
        records.append(dict(game_id=game_id, side=fixture["seat"], partition=fixture["partition"], winner=result["winner"],
                            replay_sha256=replay_hash, raw_sha256=raw_hash, sample_sha256=sample_hash,
                            report_sha256=sha256(Path(str(prefix) + ".json"))))
    dataset = pd.read_parquet(out / "dataset.parquet")
    if not dataset.equals(pd.concat(samples, ignore_index=True)):
        raise ValueError("Combined dataset differs from the per-game samples")
    dataset_hash = sha256(out / "dataset.parquet")
    if json.loads((out / "dataset-report.json").read_text())["dataset_sha256"] != dataset_hash:
        raise ValueError("Dataset report hash changed")
    receipt = dict(status="PASS", inputs=producer_inputs(out, manifest), index_sha256=sha256(out / "index.jsonl"),
                   dataset_sha256=dataset_hash, dataset_rows=len(dataset), game_count=len(records), games=records,
                   audited="Fixture/index correspondence, replay/raw/sample hashes, metadata, deterministic sample, weights, combined dataset",
                   producer_source_scope="Source recorded after initial completed pilot; only validation/resume logic changed during its run; no feature/filter/sampling changes")
    if previous.exists() and json.loads(previous.read_text()) != receipt:
        raise ValueError("Completed extraction receipt changed; keep this dataset frozen")
    bind_producer(out, manifest, adopt=True)
    write_json(previous, receipt)
    print(json.dumps({k: v for k, v in receipt.items() if k not in ("games", "inputs")}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("plan", "run", "extract", "audit"))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="Smoke stage only; never changes the frozen roster")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1 or args.limit < 0:
        parser.error("jobs must be positive and limit nonnegative")
    out = args.out.resolve()
    if args.stage == "plan":
        plan(out)
    elif args.stage == "run":
        run(out, args.jobs, args.limit, args.dry_run)
    elif args.stage == "extract":
        if args.dry_run:
            parser.error("--dry-run applies to the run stage")
        extract(out, args.jobs, args.limit)
    else:
        if args.dry_run or args.limit:
            parser.error("audit checks the complete frozen pilot")
        audit(out)


if __name__ == "__main__":
    main()
