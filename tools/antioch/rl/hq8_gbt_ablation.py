"""Matched-size GBT ablation for the frozen Antioch H-Q8 local pilot.

Targets the executed Carthage05 F/R/L move from each reconstructed actor turn.
The fixed whole-game holdout is never used to fit bins, trees, or hyperparameters.
This measures imitation of Carthage05 actions; it is not an H-RL5 expert-search
target, full-game playing-strength result, or deployment model.

Example:
  nice -n 10 .venv/bin/python tools/antioch/rl/hq8_gbt_ablation.py \
    --dataset build/antioch/rl/hq8-pilot-v1/dataset.parquet \
    --manifest build/antioch/rl/hq8-pilot-v1/manifest.json \
    --out build/antioch/rl/hq8-gbt-ablation-v1
"""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

import numpy as np
import pandas as pd

if __package__:
    from . import gbt_local_curve, hq8_features
else:
    import gbt_local_curve
    import hq8_features

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TEACHER = ROOT / "bots/hb1-04-deployable/hb1_direction_compact.hpp"
DEFAULT_BASE_MANIFEST = ROOT / "build/antioch/rl/local-pilot-v1/manifest.json"
ROUNDS = 120
BOOTSTRAP_SAMPLES = 4000
BOOTSTRAP_SEED = 62003
LABEL_MAP = {"F": 0, "R": 1, "L": 2}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def validate_frozen_split(frame, manifest, base_manifest, baseline_names, hq8_names,
                          dataset_path, base_manifest_path):
    if manifest.get("complete") is not True:
        raise ValueError("H-Q8 dataset manifest must have complete:true")
    declared_hash = manifest.get("dataset_sha256")
    if declared_hash and declared_hash != sha256(dataset_path):
        raise ValueError("H-Q8 dataset SHA256 differs from its manifest")
    if manifest.get("source_manifest_sha256") not in (None, sha256(base_manifest_path)):
        raise ValueError("H-Q8 augmentation is not bound to the frozen local pilot manifest")
    if manifest.get("base_feature_names") not in (None, baseline_names):
        raise ValueError("Manifest HB1 feature order differs from the committed model")
    if manifest.get("augmented_feature_names") not in (None, baseline_names + hq8_names):
        raise ValueError("Manifest augmented feature order differs from the declared ablation")
    if manifest.get("augmented_feature_count") not in (None, len(baseline_names) + len(hq8_names)):
        raise ValueError("Manifest augmented feature count differs from the declared ablation")
    required_features = baseline_names + hq8_names
    missing = sorted(set(required_features) - set(frame.columns))
    if missing:
        raise ValueError(f"Augmented dataset is missing model inputs: {missing}")
    metadata = {"game", "pair", "partition", "side", "y_first", "y_family",
                "actor_turn", "sampling_weight", "round", "hq8_round", "hq8_is_queen"}
    missing = sorted(metadata - set(frame.columns))
    if missing:
        raise ValueError(f"Augmented dataset is missing target/split metadata: {missing}")
    if frame[["game", "pair", "partition", "side", "y_first", "y_family"]].isna().any().any():
        raise ValueError("Missing game, pair, partition, side or action target")
    if (frame.groupby("game").partition.nunique() != 1).any():
        raise ValueError("A whole game appears in more than one partition")
    if (frame.groupby("pair").partition.nunique() != 1).any():
        raise ValueError("A seat pair appears in more than one partition")
    if (frame.groupby("game").pair.nunique() != 1).any():
        raise ValueError("A game maps to more than one seat pair")
    if (frame.groupby("game").side.nunique() != 1).any():
        raise ValueError("A game maps to more than one Carthage05 seat")
    if frame.duplicated(["game", "actor_turn"]).any():
        raise ValueError("Duplicate actor turn within a game")

    expected_train = {str(v) for v in base_manifest.get("train_game_ids", [])}
    expected_holdout = {str(v) for v in base_manifest["holdout_game_ids"]}
    if not expected_train:
        expected_train = {str(f["game_id"]) for f in base_manifest["fixtures"]
                          if f["partition"] == "train"}
    expected_all = expected_train | expected_holdout
    actual_train = set(frame.loc[frame.partition == "train", "game"].astype(str))
    actual_holdout = set(frame.loc[frame.partition == "holdout", "game"].astype(str))
    if actual_train != expected_train or actual_holdout != expected_holdout:
        raise ValueError("Augmented data changed the original pilot train/holdout game IDs")
    if (actual_train & actual_holdout) or (actual_train | actual_holdout) != expected_all:
        raise ValueError("Frozen train/holdout fixture coverage is invalid")
    if len(actual_train) != 80 or len(actual_holdout) != 20:
        raise ValueError("Expected the frozen 80-train / 20-holdout whole-game split")
    if frame.groupby("pair").partition.nunique().ne(1).any():
        raise ValueError("Seat-pair split violated")
    holdout_pairs = frame.loc[frame.partition == "holdout", "pair"].nunique()
    if holdout_pairs != 10:
        raise ValueError(f"Expected 10 frozen holdout seat pairs, found {holdout_pairs}")
    if set(frame.partition.unique()) != {"train", "holdout"}:
        raise ValueError("Unexpected partition labels")
    if not set(frame.side.unique()) <= {"A", "B"}:
        raise ValueError("Expected Carthage05 sides A/B")
    if not frame.hq8_is_queen.isin([0, 1]).all():
        raise ValueError("H-Q8 is_queen must be a binary actor-role feature")
    if not np.array_equal(frame["round"].to_numpy(), frame["hq8_round"].to_numpy()):
        raise ValueError("Prefixed H-Q8 round must match the shared HB1 round input")
    if manifest.get("holdout_game_ids") is not None and {
            str(x) for x in manifest["holdout_game_ids"]} != expected_holdout:
        raise ValueError("Augmentation manifest changed the frozen holdout IDs")
    fixtures = manifest.get("fixtures", [])
    if fixtures:
        fixture_map = {str(f["game_id"]): f for f in fixtures}
        if set(fixture_map) != expected_all:
            raise ValueError("Augmentation manifest fixture IDs differ from the pilot")
        for game, group in frame.groupby("game"):
            f = fixture_map[str(game)]
            if set(group.partition.astype(str)) != {f["partition"]}:
                raise ValueError(f"Game {game} partition differs from augmentation manifest")
            if set(group.pair.astype(str)) != {str(f["pair"])}:
                raise ValueError(f"Game {game} pair differs from augmentation manifest")
            if set(group.side.astype(str)) != {f["seat"]}:
                raise ValueError(f"Game {game} side differs from augmentation manifest")
    return required_features


def select_rows(frame):
    eligible = frame[(frame.y_family == "move") & frame.y_first.isin(LABEL_MAP)].copy()
    if eligible.empty:
        raise ValueError("No F/R/L move targets in the augmented dataset")
    if not eligible.sampling_weight.map(np.isfinite).all() or (eligible.sampling_weight <= 0).any():
        raise ValueError("Invalid inverse sampling weights")
    if not eligible.hq8_is_queen.isin([0, 1]).all():
        raise ValueError("Invalid queen actor-role slice values")
    return eligible.reset_index(drop=True)


def labels_from(rows):
    labels = rows.y_first.map(LABEL_MAP).to_numpy(dtype=np.uint8)
    if set(np.unique(labels)) != {0, 1, 2}:
        raise ValueError("Expected all three F/R/L action classes")
    return labels


def row_metrics(labels, probabilities, weights=None):
    if probabilities.shape != (len(labels), 3) or not np.isfinite(probabilities).all():
        raise ValueError("Invalid prediction matrix")
    if not np.allclose(probabilities.sum(axis=1), 1, atol=2e-12):
        raise ValueError("Predicted probabilities do not sum to one")
    if weights is None:
        weights = np.ones(len(labels), dtype=np.float64)
    else:
        weights = np.asarray(weights, dtype=np.float64)
        if weights.shape != (len(labels),) or not np.isfinite(weights).all() or np.any(weights <= 0):
            raise ValueError("Invalid metric weights")
    pred = probabilities.argmax(axis=1)
    accuracy = float(np.mean(pred == labels))
    logloss = float(-np.log(np.clip(probabilities[np.arange(len(labels)), labels], 1e-15, 1)).mean())
    weighted_accuracy = float(np.average(pred == labels, weights=weights))
    weighted_logloss = float(np.average(
        -np.log(np.clip(probabilities[np.arange(len(labels)), labels], 1e-15, 1)), weights=weights))
    f1 = []
    weighted_f1 = []
    recall = []
    weighted_recall = []
    for cls in range(3):
        tp_mask = (pred == cls) & (labels == cls)
        fp_mask = (pred == cls) & (labels != cls)
        fn_mask = (pred != cls) & (labels == cls)
        tp = int(np.sum(tp_mask))
        fp = int(np.sum(fp_mask))
        fn = int(np.sum(fn_mask))
        f1.append(2 * tp / max(1, 2 * tp + fp + fn))
        recall.append(tp / max(1, tp + fn))
        wtp, wfp, wfn = weights[tp_mask].sum(), weights[fp_mask].sum(), weights[fn_mask].sum()
        weighted_f1.append(2 * wtp / max(1e-300, 2 * wtp + wfp + wfn))
        weighted_recall.append(wtp / max(1e-300, wtp + wfn))
    return dict(rows=len(labels), accuracy=accuracy, logloss=logloss,
                macro_f1=float(np.mean(f1)), recall_F=float(recall[0]),
                recall_R=float(recall[1]), recall_L=float(recall[2]),
                sampling_weighted_accuracy=weighted_accuracy,
                sampling_weighted_logloss=weighted_logloss,
                sampling_weighted_macro_f1=float(np.mean(weighted_f1)),
                sampling_weighted_recall_F=float(weighted_recall[0]),
                sampling_weighted_recall_R=float(weighted_recall[1]),
                sampling_weighted_recall_L=float(weighted_recall[2]))


def game_metrics(rows, labels, probabilities, weights, mask):
    positions = np.flatnonzero(mask)
    if not len(positions):
        return pd.DataFrame(columns=["game", "pair", "rows", "accuracy", "logloss", "macro_f1"])
    values = []
    sub = rows.iloc[positions]
    pred = probabilities[positions].argmax(axis=1)
    losses = -np.log(np.clip(probabilities[positions, labels[positions]], 1e-15, 1))
    for game, indexes in sub.groupby("game", sort=True).indices.items():
        local = np.asarray(indexes, dtype=np.int64)
        global_positions = positions[local]
        metrics = row_metrics(labels[global_positions], probabilities[global_positions])
        weighted = row_metrics(labels[global_positions], probabilities[global_positions], weights[global_positions])
        pair = str(rows.iloc[global_positions[0]].pair)
        values.append(dict(game=str(game), pair=pair, rows=int(len(local)),
                           accuracy=metrics["accuracy"], logloss=metrics["logloss"],
                           macro_f1=metrics["macro_f1"],
                           weighted_accuracy=weighted["sampling_weighted_accuracy"],
                           weighted_logloss=weighted["sampling_weighted_logloss"],
                           weighted_macro_f1=weighted["sampling_weighted_macro_f1"]))
    return pd.DataFrame(values)


def percentile_ci(values, samples, seed):
    values = np.asarray(values, dtype=np.float64)
    if not len(values):
        return [None, None]
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(values), size=(samples, len(values)))
    draws = values[indexes].mean(axis=1)
    return np.quantile(draws, [0.05, 0.95]).tolist()


def arm_summary(rows, labels, probabilities, weights, mask, samples, seed):
    positions = np.flatnonzero(mask)
    raw = row_metrics(labels[positions], probabilities[positions], weights[positions]) if len(positions) else None
    games = game_metrics(rows, labels, probabilities, weights, mask)
    result = dict(row_weighted=raw, rows=int(len(positions)), games=int(len(games)), game_macro={})
    for metric in ("accuracy", "logloss", "macro_f1", "weighted_accuracy", "weighted_logloss", "weighted_macro_f1"):
        if len(games):
            vals = games[metric].to_numpy()
            result["game_macro"][metric] = float(vals.mean())
            result["game_macro"][metric + "_bootstrap_ci90"] = percentile_ci(vals, samples, seed)
        else:
            result["game_macro"][metric] = None
            result["game_macro"][metric + "_bootstrap_ci90"] = [None, None]
    return result, games


def paired_summary(base_games, hq8_games, samples, seed):
    merged = base_games.merge(hq8_games, on=["game", "pair"], suffixes=("_base", "_hq8"),
                              validate="one_to_one")
    if merged.empty:
        return dict(pairs=0, metrics={}), merged
    pair_rows = []
    for pair, group in merged.groupby("pair", sort=True):
        record = {"pair": str(pair), "games": int(len(group))}
        for metric in ("accuracy", "logloss", "macro_f1", "weighted_accuracy", "weighted_logloss", "weighted_macro_f1"):
            base_value = float(group[metric + "_base"].mean())
            hq8_value = float(group[metric + "_hq8"].mean())
            record[metric + "_baseline"] = base_value
            record[metric + "_with_hq8"] = hq8_value
            record[metric + "_delta"] = hq8_value - base_value
        pair_rows.append(record)
    pair_frame = pd.DataFrame(pair_rows)
    summary = dict(pairs=len(pair_frame), metrics={})
    for metric in ("accuracy", "logloss", "macro_f1", "weighted_accuracy", "weighted_logloss", "weighted_macro_f1"):
        values = pair_frame[metric + "_delta"].to_numpy()
        summary["metrics"][metric] = dict(
            paired_delta_mean=float(values.mean()),
            paired_delta_bootstrap_ci90=percentile_ci(values, samples, seed))
    game_metrics_delta = {}
    for metric in ("accuracy", "logloss", "macro_f1", "weighted_accuracy", "weighted_logloss", "weighted_macro_f1"):
        values = merged[metric + "_hq8"].to_numpy() - merged[metric + "_base"].to_numpy()
        game_metrics_delta[metric] = dict(
            paired_delta_mean=float(values.mean()),
            paired_delta_bootstrap_ci90=percentile_ci(values, samples, seed + 1))
    summary["paired_game_deltas"] = dict(games=len(merged), metrics=game_metrics_delta)
    return summary, pair_frame


def check_train_holdout_probability_files(path, count):
    values = np.fromfile(path, dtype="<f8")
    if values.size != count * 3:
        raise ValueError(f"Prediction file length mismatch: {path}")
    return values.reshape(count, 3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--base-manifest", type=Path, default=DEFAULT_BASE_MANIFEST)
    parser.add_argument("--teacher-header", type=Path, default=DEFAULT_TEACHER)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=ROUNDS)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    parser.add_argument("--seed", type=int, default=BOOTSTRAP_SEED)
    args = parser.parse_args()
    if args.rounds < 1 or args.bootstrap_samples < 1:
        parser.error("rounds and bootstrap samples must be positive")
    started = time.monotonic()
    args.out.mkdir(parents=True, exist_ok=True)
    model = gbt_local_curve.load_model(args.teacher_header)
    baseline_names = model["names"]
    if len(baseline_names) != 270 or len(set(baseline_names)) != len(baseline_names):
        raise ValueError(f"Expected 270 unique committed HB1 model features, found {len(baseline_names)}")
    hq8_prefixed = ["hq8_" + name for name in hq8_features.NAMES]
    if "hq8_round" not in hq8_prefixed or len(hq8_prefixed) != 36:
        raise ValueError("Unexpected H-Q8 schema")
    hq8_names = [name for name in hq8_prefixed if name != "hq8_round"]
    manifest = json.loads(args.manifest.read_text())
    base_manifest = json.loads(args.base_manifest.read_text())
    if manifest.get("source_dataset_sha256"):
        base_dataset = args.base_manifest.parent / "dataset.parquet"
        if sha256(base_dataset) != manifest["source_dataset_sha256"]:
            raise ValueError("Augmented dataset references a changed base pilot dataset")
    if manifest.get("runtime") not in (None, "1.2.5") and manifest.get("unswbc") not in (None, "1.2.5"):
        raise ValueError("Expected the 1.2.5 replay reconstruction runtime")
    frame = pd.read_parquet(args.dataset)
    feature_names = validate_frozen_split(frame, manifest, base_manifest, baseline_names, hq8_names,
                                          args.dataset, args.base_manifest)
    rows = select_rows(frame)
    del frame
    train = rows[rows.partition == "train"].reset_index(drop=True)
    holdout = rows[rows.partition == "holdout"].reset_index(drop=True)
    if len(train) < 1000 or len(holdout) < 100:
        raise ValueError("Unexpectedly small direction dataset")
    if set(np.unique(labels_from(train))) != {0, 1, 2} or set(np.unique(labels_from(holdout))) != {0, 1, 2}:
        raise ValueError("A split lacks one or more direction classes")
    all_values = rows[feature_names].to_numpy(dtype="<f4", copy=True)
    if np.isinf(all_values).any():
        raise ValueError("Infinite feature values")
    if not np.isfinite(all_values[:, :len(baseline_names)]).any(axis=0).all():
        raise ValueError("At least one baseline input is fully missing")
    x_train = train[feature_names].to_numpy(dtype="<f4", copy=True)
    x_holdout = holdout[feature_names].to_numpy(dtype="<f4", copy=True)
    y_train = labels_from(train)
    y_holdout = labels_from(holdout)
    weights_train = train.sampling_weight.to_numpy(dtype="<f4", copy=True)
    if not np.isfinite(weights_train).all() or np.any(weights_train <= 0):
        raise ValueError("Training weights must be finite and positive")

    matrix_train = args.out / "train-305.f32"
    matrix_holdout = args.out / "holdout-305.f32"
    labels_path = args.out / "train-labels.u8"
    weights_path = args.out / "train-weights.f32"
    x_train.tofile(matrix_train)
    x_holdout.tofile(matrix_holdout)
    y_train.tofile(labels_path)
    weights_train.tofile(weights_path)
    write_json(args.out / "dataset-audit.json", dict(
        schema="antioch-hq8-gbt-ablation-input-v1", dataset=str(args.dataset),
        dataset_sha256=sha256(args.dataset), manifest=str(args.manifest),
        manifest_sha256=sha256(args.manifest), base_manifest=str(args.base_manifest),
        base_manifest_sha256=sha256(args.base_manifest), base_dataset_sha256=sha256(args.base_manifest.parent / "dataset.parquet"),
        teacher_header=str(args.teacher_header), teacher_sha256=sha256(args.teacher_header),
        runtime=manifest.get("runtime", manifest.get("unswbc")), total_sample_rows=len(rows),
        train_rows=len(train), holdout_rows=len(holdout), train_games=int(train.game.nunique()),
        holdout_games=int(holdout.game.nunique()), train_pairs=int(train.pair.nunique()),
        holdout_pairs=int(holdout.pair.nunique()), train_game_ids=sorted(train.game.astype(str).unique()),
        holdout_game_ids=sorted(holdout.game.astype(str).unique()), label_target="Carthage05 reconstructed executed move y_first in F/R/L",
        feature_sets={"baseline_count": len(baseline_names), "baseline_names": baseline_names,
                      "added_hq8_count": len(hq8_names), "added_hq8_names": hq8_names,
                      "augmented_count": len(feature_names)},
        hq8_round_duplicate="hq8_round validated against baseline round and excluded from augmented model",
        split="Frozen inherited whole-game 80/20; both seat games of each pair stay in one partition",
        no_holdout_fit="Histogram thresholds are computed inside each C++ fit from train rows only; holdout used once for final metrics",
        feature_nan_semantics="NaN has a learned per-split default branch; H-Q8 unknown sentinel -1 remains numeric",
        data_sampling_weight="Rows weighted by recorded inverse per-game sample inclusion weight"))
    binary = args.out / "hq8-gbt-ablation"
    compile_command = ["g++", "-O3", "-std=c++17", "-fopenmp",
                       str(Path(__file__).with_suffix(".cpp")), "-o", str(binary)]
    subprocess.run(compile_command, check=True)
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = env.get("OMP_NUM_THREADS", str(min(8, os.cpu_count() or 1)))
    fit_reports = {}
    for arm, feature_count in (("baseline270", 270), ("with_hq8_305", 305)):
        prefix = args.out / arm
        command = [str(binary), str(matrix_train), str(len(train)), str(len(feature_names)), str(feature_count),
                   str(labels_path), str(weights_path), str(matrix_holdout), str(len(holdout)),
                   str(args.rounds), str(prefix)]
        subprocess.run(command, check=True, env=env)
        fit_reports[arm] = json.loads(Path(str(prefix) + ".trainer.json").read_text())

    base_holdout = check_train_holdout_probability_files(
        args.out / "baseline270.holdout-prob.f64", len(holdout))
    hq8_holdout = check_train_holdout_probability_files(
        args.out / "with_hq8_305.holdout-prob.f64", len(holdout))
    base_train = check_train_holdout_probability_files(args.out / "baseline270.train-prob.f64", len(train))
    hq8_train = check_train_holdout_probability_files(args.out / "with_hq8_305.train-prob.f64", len(train))
    target_train, target_holdout = labels_from(train), labels_from(holdout)

    masks = {
        "all": np.ones(len(holdout), dtype=bool),
        "actor_is_queen": holdout.hq8_is_queen.to_numpy(dtype=bool),
        "late_round_ge_350": holdout["round"].to_numpy() >= 350,
        "queen_late_round_ge_350": holdout.hq8_is_queen.to_numpy(dtype=bool) & (holdout["round"].to_numpy() >= 350),
    }
    base_train_summary, _ = arm_summary(train, target_train, base_train,
                                        train.sampling_weight.to_numpy(dtype=np.float64),
                                        np.ones(len(train), dtype=bool),
                                        args.bootstrap_samples, args.seed)
    result = dict(kind="matched-size H-Q8 GBT feature ablation",
                  interpretation="Held-out imitation of Carthage05 executed/search-selected F/R/L moves. This is not full game strength, new H-RL5 search supervision, teacher fidelity, or deployment evidence.",
                  train={},
                  holdout={}, paired_holdout_deltas={}, configuration={
                      "rounds": args.rounds, "max_depth": 3, "max_bins": 32, "learning_rate": 0.08,
                      "l2": 3.0, "min_gain": 1.0, "min_leaf_rows": 64,
                      "class_count": 3, "classes": ["F", "R", "L"],
                      "histogram_cutpoints_fit_on": "train partition only",
                      "sample_weight": "inverse per-game sampling weight", "randomness": "deterministic greedy splits",
                      "feature_budget": "identical complete depth-3 trees and rounds; every node slot stored"},
                  models={}, slices={}, elapsed_seconds=None)
    # Both arms share labels/split and equal leaf/tree parameter budget.
    train_hq8_summary, _ = arm_summary(train, target_train, hq8_train, train.sampling_weight.to_numpy(dtype=np.float64),
                                       np.ones(len(train), dtype=bool), args.bootstrap_samples, args.seed)
    result["train"] = {"baseline270": base_train_summary, "with_hq8_305": train_hq8_summary}
    per_game_all = []
    per_pair_all = []
    for name, mask in masks.items():
        if int(mask.sum()) == 0:
            result["slices"][name] = {"rows": 0, "games": 0, "status": "no eligible holdout rows"}
            continue
        holdout_weights = holdout.sampling_weight.to_numpy(dtype=np.float64)
        base_summary, base_games = arm_summary(holdout, target_holdout, base_holdout, holdout_weights, mask,
                                               args.bootstrap_samples, args.seed)
        hq8_summary, hq8_games = arm_summary(holdout, target_holdout, hq8_holdout, holdout_weights, mask,
                                              args.bootstrap_samples, args.seed)
        paired, pair_frame = paired_summary(base_games, hq8_games,
                                            args.bootstrap_samples, args.seed)
        result["slices"][name] = {"baseline270": base_summary, "with_hq8_305": hq8_summary,
                                  "paired_delta_with_hq8_minus_baseline": paired}
        if name == "all":
            result["holdout"] = result["slices"][name]
        for _, row in base_games.iterrows():
            other = hq8_games[hq8_games.game == row.game].iloc[0]
            per_game_all.append(dict(slice=name, game=row.game, pair=row.pair, rows=int(row.rows),
                                     baseline_accuracy=row.accuracy, hq8_accuracy=other.accuracy,
                                     delta_accuracy=other.accuracy - row.accuracy,
                                     baseline_logloss=row.logloss, hq8_logloss=other.logloss,
                                     delta_logloss=other.logloss - row.logloss,
                                     baseline_macro_f1=row.macro_f1, hq8_macro_f1=other.macro_f1,
                                     delta_macro_f1=other.macro_f1 - row.macro_f1,
                                     baseline_weighted_accuracy=row.weighted_accuracy,
                                     hq8_weighted_accuracy=other.weighted_accuracy,
                                     delta_weighted_accuracy=other.weighted_accuracy - row.weighted_accuracy,
                                     baseline_weighted_logloss=row.weighted_logloss,
                                     hq8_weighted_logloss=other.weighted_logloss,
                                     delta_weighted_logloss=other.weighted_logloss - row.weighted_logloss))
        for _, row in pair_frame.iterrows():
            per_pair_all.append(dict(slice=name, **row.to_dict()))
    for arm, probabilities, target, sample_rows in (
            ("baseline270", base_holdout, target_holdout, holdout),
            ("with_hq8_305", hq8_holdout, target_holdout, holdout)):
        result["models"][arm] = {
            "training_report": fit_reports[arm],
            "numeric_model_bytes": fit_reports[arm]["size_bytes"],
            "node_file_bytes": (args.out / f"{arm}.nodes.bin").stat().st_size,
            "probability_argmax_accuracy_holdout": row_metrics(target, probabilities)["accuracy"],
            "split_uses": {feature_names[int(index) if arm == "with_hq8_305" else int(index)]: count
                           for index, count in fit_reports[arm]["split_uses_by_feature"].items()},
        }
    baseline_node_bytes = result["models"]["baseline270"]["node_file_bytes"]
    augmented_node_bytes = result["models"]["with_hq8_305"]["node_file_bytes"]
    if baseline_node_bytes != augmented_node_bytes:
        raise ValueError("Matched model node budget did not produce equal serialized sizes")
    added_use_count = sum(count for name, count in result["models"]["with_hq8_305"]["split_uses"].items()
                          if name.startswith("hq8_"))
    result["models"]["with_hq8_305"]["added_hq8_split_uses"] = added_use_count
    result["comparison"] = dict(node_file_bytes_equal=baseline_node_bytes,
                                model_node_budget_equal=True,
                                baseline_feature_count=270, augmented_feature_count=305,
                                added_hq8_features=35, augmented_hq8_split_uses=added_use_count,
                                train_and_holdout_game_ids_identical=True)
    result["inputs"] = dict(dataset=str(args.dataset), dataset_sha256=sha256(args.dataset),
                            manifest=str(args.manifest), manifest_sha256=sha256(args.manifest),
                            base_manifest=str(args.base_manifest), base_manifest_sha256=sha256(args.base_manifest),
                            teacher_header=str(args.teacher_header), teacher_sha256=sha256(args.teacher_header),
                            cpp_trainer=str(Path(__file__).with_suffix(".cpp")),
                            cpp_trainer_sha256=sha256(Path(__file__).with_suffix(".cpp")),
                            python_source=str(Path(__file__)), python_source_sha256=sha256(Path(__file__)),
                            runtime=manifest.get("runtime", manifest.get("unswbc")))
    result["bootstrap"] = dict(samples=args.bootstrap_samples, seed=args.seed,
                               interval="central percentile 90% [5th,95th]",
                               per_arm="resample games; paired game delta resamples the same games across arms; primary pair delta resamples seat pairs, preserving both games",
                               queen_slice="hq8_is_queen == 1; the acting dragon is its team queen")
    result["elapsed_seconds"] = time.monotonic() - started
    write_json(args.out / "ablation.json", result)
    for filename, records in (("per-game.csv", per_game_all), ("per-pair.csv", per_pair_all)):
        with (args.out / filename).open("w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    print(json.dumps({"result": str(args.out / "ablation.json"),
                      "comparison": result["comparison"],
                      "holdout": result["holdout"],
                      "slices": result["slices"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
