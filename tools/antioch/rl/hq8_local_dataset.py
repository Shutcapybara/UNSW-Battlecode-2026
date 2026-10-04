"""Augment the frozen local pilot with the replay-derived H-Q8-v1 observation block.

    .venv/bin/python tools/antioch/rl/hq8_local_dataset.py \
      --source build/antioch/rl/local-pilot-v1 \
      --out build/antioch/rl/hq8-pilot-v1 --jobs 2

The H-Q8 encoder receives exactly the reconstructed protocol block each actor
would receive, with per-dragon state carried between turns. All36 H-Q8 values
are retained (prefixed in output); `hq8_round` duplicates the baseline `round`
and is excluded from the augmented model's input list. Source labels, outcome,
map, seed, and partition remain metadata, not model inputs.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import importlib.metadata
import json
import multiprocessing
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.antioch.rl import hq8_features as H
from tools.antioch.rl import local_dataset as base

SOURCE = ROOT / "build/antioch/rl/local-pilot-v1"


def digest(path):
    return base.sha256(path)


def receipt_inputs(source, manifest):
    return dict(source_manifest_sha256=digest(source / "manifest.json"),
                source_receipt_sha256=digest(source / "extraction-receipt.json"),
                source_dataset_sha256=digest(source / "dataset.parquet"),
                encoder_py_sha256=digest(Path(H.__file__)),
                encoder_cpp_sha256=digest(Path(__file__).with_name("hq8_features.hpp")),
                roundblock_sha256=digest(ROOT / "tools/team_recon_claude/roundblock.py"),
                recon_sha256=digest(ROOT / "tools/team_recon_claude/recon.py"),
                runtime=manifest["runtime"], feature_names=list(H.NAMES))


def bind_build_source(out, inputs):
    path = out / "build-receipt.json"
    if path.exists():
        if json.loads(path.read_text())["inputs"] != inputs:
            raise ValueError("Augmentation code/inputs changed during resume; use a fresh output directory")
    else:
        if (out / "rows").exists() and any((out / "rows").iterdir()):
            raise ValueError("Partial augmentation has no build receipt; audit or use a fresh output directory")
        out.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dict(inputs=inputs, status="building"), indent=2) + "\n")


def observations_for_replay(replay, side, game_id, expected):
    sys.path.insert(0, str(ROOT / "tools/team_recon_claude"))
    import recon
    import roundblock
    import features_view as FV

    g = recon.Game(replay)
    encoders, turn_counts, rows = {}, {}, []

    def cb(kind, **event):
        if kind == "turn":
            dragon = event["dragon"]
            if dragon.team != side:
                return
            n = turn_counts.get(dragon.id, 0)
            turn_counts[dragon.id] = n + 1
            proto3 = n > 0 or dragon.parent is not None
            block_lines = roundblock.build_block(g, dragon, proto3=proto3)
            block, consumed = FV.parse_block(block_lines)
            if consumed != len(block_lines):
                raise ValueError(f"Game {game_id}: trailing observation input")
            encoder = encoders.get(dragon.id)
            if encoder is None:
                encoder = encoders[dragon.id] = H.Encoder(
                    dragon.id, side, g.board.W, g.board.H, g.board.unit_limit)
            values = encoder.features(block)
            row = dict(game=game_id, dragon=dragon.id, round=block["round"], actor_turn=len(rows))
            row.update({"hq8_" + name: int(value) for name, value in zip(H.NAMES, values)})
            rows.append(row)
        elif kind == "action" and event["dragon"].team == side:
            action = event["action"]
            if action[0] == "split":
                encoders[event["dragon"].id].record_split()

    g.run(cb)
    keys = [(int(row["dragon"]), int(row["round"])) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError(f"Game {game_id}: duplicate dragon/round keys")
    expected_keys = list(zip(expected.dragon.astype(int), expected["round"].astype(int)))
    if keys != expected_keys:
        mismatch = next((i for i, (a, b) in enumerate(zip(keys, expected_keys)) if a != b), None)
        raise ValueError(f"Game {game_id}: encoder rows misalign at {mismatch}; {len(keys)} vs {len(expected_keys)}")
    bad = {k: v for k, v in g.checks.items() if v and (k.endswith("bad") or k.endswith("mismatch"))}
    if bad:
        raise ValueError(f"Game {game_id}: replay reconstruction checks failed: {bad}")
    return pd.DataFrame(rows), dict(rows=len(rows), checks=dict(g.checks), map=g.board.name, rounds=g.round,
                            queens=int(sum(x["hq8_is_queen"] for x in rows)),
                            late=int(sum(x["hq8_round"] >= 350 for x in rows)))


def augment_one(args):
    source, out, fixture, result = args
    game_id = fixture["game_id"]
    source_rows = source / "rows" / f"{game_id:04d}.parquet"
    original = pd.read_parquet(source_rows)
    replay = source / result["replay"]
    if digest(replay) != result["replay_sha256"]:
        raise ValueError(f"Game {game_id}: changed pilot replay")
    features, report = observations_for_replay(replay, fixture["seat"], game_id,
                                               original[["dragon", "round"]])
    merged = pd.concat([original.reset_index(drop=True),
                        features[[column for column in features if column.startswith("hq8_")]].reset_index(drop=True)], axis=1)
    if merged.columns.duplicated().any() or len(merged) != len(original):
        raise ValueError(f"Game {game_id}: augmented rows/columns do not align")
    destination = out / "rows" / f"{game_id:04d}.parquet"
    temporary = Path(str(destination) + ".tmp")
    merged.to_parquet(temporary, index=False)
    temporary.replace(destination)
    report.update(game_id=game_id, partition=fixture["partition"], side=fixture["seat"],
                  source_rows_sha256=digest(source_rows), replay_sha256=digest(replay),
                  augmented_sha256=digest(destination))
    (out / "rows" / f"{game_id:04d}.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def run(source, out, jobs, limit=0):
    manifest = json.loads((source / "manifest.json").read_text())
    base.audit(source)
    inputs = receipt_inputs(source, manifest)
    receipt_path = out / "receipt.json"
    out.mkdir(parents=True, exist_ok=True)
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt["inputs"] != inputs:
            raise ValueError("Augmentation inputs changed; use a fresh output directory")
        dataset_path = out / "dataset.parquet"
        if digest(dataset_path) != receipt["dataset_sha256"]:
            raise ValueError("Frozen augmented dataset changed")
        print(json.dumps({"status": "PASS", "message": "Verified existing frozen H-Q8 dataset",
                          "dataset": str(dataset_path), "sha256": receipt["dataset_sha256"]}, indent=2))
        return
    bind_build_source(out, inputs)
    (out / "rows").mkdir(exist_ok=True)
    base_index = base.index_rows(source)
    chosen_fixtures = manifest["fixtures"][:limit] if limit else manifest["fixtures"]
    fixture_by_id = {fixture["game_id"]: fixture for fixture in chosen_fixtures}
    tasks = [(source, out, fixture_by_id[gid], base_index[gid])
             for gid in sorted(fixture_by_id)]
    reports = []
    with ProcessPoolExecutor(max_workers=jobs, mp_context=multiprocessing.get_context("fork")) as pool:
        futures = {pool.submit(augment_one, task): task[2]["game_id"] for task in tasks}
        for number, future in enumerate(as_completed(futures), 1):
            report = future.result()
            reports.append(report)
            print(f"H-Q8 {number}/{len(tasks)}: id={report['game_id']} rows={report['rows']} "
                  f"queen={report['queens']} late={report['late']}", flush=True)
    reports.sort(key=lambda row: row["game_id"])
    sampled = pd.read_parquet(source / "dataset.parquet")
    sampled = sampled[sampled.game.isin(fixture_by_id)].reset_index(drop=True)
    pieces = []
    augmented_names = ["hq8_" + name for name in H.NAMES]
    if len(augmented_names) != 36 or len(set(augmented_names)) != 36:
        raise ValueError("Unexpected H-Q8-v1 feature schema")
    for game_id, rows in sampled.groupby("game", sort=True):
        frame = pd.read_parquet(out / "rows" / f"{int(game_id):04d}.parquet")
        if not np.array_equal(frame.actor_turn.to_numpy()[rows.actor_turn.to_numpy()], rows.actor_turn.to_numpy()):
            raise ValueError(f"Game {game_id}: actor turn alignment failed")
        selected = frame.loc[rows.actor_turn, augmented_names].reset_index(drop=True)
        if not selected.hq8_round.equals(rows["round"].reset_index(drop=True)):
            raise ValueError(f"Game {game_id}: H-Q8 round does not match baseline round")
        pieces.append(selected)
    added = pd.concat(pieces, ignore_index=True)
    augmented = pd.concat([sampled.reset_index(drop=True), added], axis=1)
    if len(augmented) != len(sampled) or augmented.columns.duplicated().any():
        raise ValueError("Bad combined dataset dimensions")
    dataset_path = out / "dataset.parquet"
    temporary = Path(str(dataset_path) + ".tmp")
    augmented.to_parquet(temporary, index=False)
    temporary.replace(dataset_path)
    current_base_names = list(manifest["feature_names"])
    augmented_model_names = current_base_names + [name for name in augmented_names if name != "hq8_round"]
    complete = not limit
    output_manifest = dict(schema="antioch-local-hq8-pilot-v1", complete=complete, runtime=manifest["runtime"],
                           source_manifest_sha256=inputs["source_manifest_sha256"],
                           source_dataset_sha256=inputs["source_dataset_sha256"],
                           source_receipt_sha256=inputs["source_receipt_sha256"],
                           game_ids=sorted(fixture_by_id),
                           train_game_ids=[f["game_id"] for f in chosen_fixtures if f["partition"] == "train"],
                           holdout_game_ids=[f["game_id"] for f in chosen_fixtures if f["partition"] == "holdout"],
                           split="Inherited unchanged from frozen local-pilot-v1: whole games and both seats of each matchup stay together",
                           base_feature_names=current_base_names, hq8_feature_names=augmented_names,
                           augmented_feature_names=augmented_model_names,
                           augmented_feature_count=len(augmented_model_names),
                           feature_semantics="36 current conservative H-Q8-v1 fields; unknown is -1, not inferred dead; `hq8_round` is retained for audit but excluded from augmented model list",
                           labels="Existing Carthage05 observed actions/search choices and game outcomes; not H-RL5 search targets",
                           model_inputs_exclude=["game", "dragon", "side", "partition", "pair", "map", "seed", "game_score",
                                                 "actor_turn", "all y_* labels", "post_* outcomes"],
                           sampling=manifest["sampling"], dataset_rows=len(augmented),
                           dataset_sha256=digest(dataset_path), producer_inputs=inputs,
                           game_reports=reports)
    (out / "manifest.json").write_text(json.dumps(output_manifest, indent=2) + "\n")
    receipt = dict(status="PASS" if complete else "SMOKE_ONLY", inputs=inputs,
                   output_manifest_sha256=digest(out / "manifest.json"),
                   dataset_sha256=digest(dataset_path), rows=len(augmented), games=len(reports),
                   python_encoder_parity="Pending C++ and live-observation parity gates",
                   hq8_unknown_semantics="-1 means unavailable under the v1 observation contract")
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    build_receipt = json.loads((out / "build-receipt.json").read_text())
    build_receipt["status"] = "PASS" if complete else "SMOKE_ONLY"
    (out / "build-receipt.json").write_text(json.dumps(build_receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "inputs"}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--out", type=Path, default=ROOT / "build/antioch/rl/hq8-pilot-v1")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--limit", type=int, default=0, help="Create a partial smoke artifact; never a training dataset")
    args = parser.parse_args()
    if args.jobs < 1 or args.limit < 0:
        parser.error("jobs must be positive and limit nonnegative")
    source, out = args.source.resolve(), args.out.resolve()
    if source == out or source in out.parents or out in source.parents:
        parser.error("--out must be separate from and outside the frozen source dataset")
    run(source, out, args.jobs, args.limit)


if __name__ == "__main__":
    main()
