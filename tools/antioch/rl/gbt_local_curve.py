"""Measure compression fidelity to the committed full GBT on frozen local games.

    .venv/bin/python tools/antioch/rl/gbt_local_curve.py \
        --dataset build/antioch/rl/local-pilot-v1/dataset.parquet \
        --manifest build/antioch/rl/local-pilot-v1/manifest.json \
        --out build/antioch/rl/local-pilot-v1/curve --header-parity-rows 32

Evaluate only partition='holdout', with both games of a seat pair kept together.
The teacher is the original 2,345-round model. Agreement is compression fidelity
on these local states; it does not measure expert imitation, improved play or
the original HB1 held-out accuracy. No fitting or threshold selection occurs.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

import numpy as np
import pandas as pd

if __package__:
    from . import gbt_direction_curve as sizes
else:
    import gbt_direction_curve as sizes

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL = ROOT / "bots/hb1-04-deployable/hb1_direction_compact.hpp"
DEFAULT_BOT = ROOT / "bots/carthage-05-free-sprint"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_model(path):
    source = path.read_text()
    classes = [int(value) for value in sizes.array(source, "dirc_classes").split(",")]
    k = int(re.search(r"dirc_K = (\d+)", source).group(1))
    starts = np.array([int(value) for value in sizes.array(source, "dirc_tree_start").split(",") if value.strip()], "<i4")
    names = re.findall(r'"([^"]+)"', sizes.array(source, "dirc_feats"))
    base = np.array([float(value.strip().removesuffix("f")) for value in sizes.array(source, "dirc_base").split(",")], "<f4")
    prelude, tail = source.split("inline constexpr unsigned long long dirc_nodes[] = {\n", 1)
    body, ending = tail.split("\n};", 1)
    nodes = np.fromiter((int(word, 16) for word in re.findall(r"0x[0-9a-f]+", body)), dtype="<u8")
    if k != len(classes) or len(base) != k or len(starts) % k:
        raise ValueError("Compact model class/tree shape mismatch")
    if starts[0] != 0 or np.any(np.diff(starts) <= 0) or starts[-1] >= len(nodes):
        raise ValueError("Compact model tree offsets invalid")
    return dict(source=source, k=k, classes=classes, starts=starts, names=names, base=base,
                nodes=nodes, prelude=prelude, body=body, ending=ending, full_rounds=len(starts) // k)


def prefix_size(model, rounds, bot):
    trees = rounds * model["k"]
    nodes = int(model["starts"][trees]) if trees < len(model["starts"]) else len(model["nodes"])
    lines = model["body"].splitlines()
    if any(line.count(",") != 12 for line in lines[:-1]):
        raise ValueError("Expected the committed compact generator's 12-node line layout")
    whole, remainder = divmod(nodes, 12)
    prefix = lines[:whole]
    if remainder:
        prefix.append(",".join(lines[whole].split(",")[:remainder]) + ",")
    head = re.sub(r"dirc_n_trees = \d+", f"dirc_n_trees = {trees}", model["prelude"])
    head = re.sub(r"dirc_tree_start\[\] = \{.*?\};",
                  "dirc_tree_start[] = {" + ",".join(map(str, model["starts"][:trees])) + "};", head, flags=re.S)
    header = head + "inline constexpr unsigned long long dirc_nodes[] = {\n" + "\n".join(prefix) + "\n};" + model["ending"]
    compressed, bot_zip = sizes.zipped_header(header, bot)
    return dict(trees=trees, nodes=nodes, compact_node_and_start_bytes=nodes * 8 + trees * 4,
                header_source_bytes=len(header.encode()), header_zip_bytes=compressed,
                deployment_bot_zip_bytes=bot_zip, upload_fits_4_mib=bot_zip <= 4 * 2**20)


def select_holdout(frame, manifest, names):
    required = set(names) | {"game", "pair", "partition", "side"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")
    if frame[["game", "pair", "partition", "side"]].isna().any().any():
        raise ValueError("Missing game/partition/side values")
    if (frame.groupby("game").partition.nunique() > 1).any():
        raise ValueError("Whole-game split violated: a game appears in multiple partitions")
    if (frame.groupby("pair").partition.nunique() > 1).any():
        raise ValueError("Seat-pair split violated: a pair appears in multiple partitions")
    if (frame.groupby("game").pair.nunique() != 1).any():
        raise ValueError("A game maps to multiple seat pairs")
    if not set(frame.side.unique()) <= {"A", "B"}:
        raise ValueError("Expected side A/B")
    if not set(frame.partition.unique()) <= {"train", "holdout"}:
        raise ValueError("Expected frozen train/holdout partitions")
    fixtures = manifest.get("fixtures")
    if fixtures:
        declared_games = {str(fixture["game_id"]): fixture for fixture in fixtures}
        for game, group in frame.groupby("game"):
            fixture = declared_games.get(str(game))
            if fixture is None:
                raise ValueError(f"Dataset game {game} is absent from manifest")
            if set(group.partition) != {fixture["partition"]} or set(group.pair) != {fixture["pair"]}:
                raise ValueError(f"Dataset game {game} partition/pair differs from manifest")
            if set(group.side) != {fixture["seat"]}:
                raise ValueError(f"Dataset game {game} side differs from manifest")
    if "y_family" in frame and "y_first" in frame:
        frame = frame[(frame.y_family == "move") & frame.y_first.isin(["F", "R", "L"])]
    rows = frame[frame.partition == "holdout"].copy().reset_index(drop=True)
    if rows.empty:
        raise ValueError("Frozen partition='holdout' has no direction rows")
    declared = manifest.get("holdout_game_ids")
    if declared is not None and not set(rows.game.astype(str)) <= {str(game) for game in declared}:
        raise ValueError("Dataset holdout disagrees with manifest holdout_game_ids")
    if declared is not None and set(rows.game.astype(str)) != {str(game) for game in declared}:
        raise ValueError("Manifest holdout has games with no eligible dataset rows")
    if declared is not None and set(frame.loc[frame.partition != "holdout", "game"].astype(str)) & {str(game) for game in declared}:
        raise ValueError("Manifest holdout includes a training game")
    matrix = rows[names].to_numpy(dtype="<f4")
    if np.isinf(matrix).any():
        raise ValueError("Infinite model features")
    if fixtures and (rows.groupby("pair").game.nunique() != 2).any():
        raise ValueError("A holdout seat pair is missing one of its games")
    return rows, matrix


def paired_delta_summary(rows, agreement, reference, samples, seed):
    """Compare prefixes on identical states; resample both seat games as a pair."""
    data = pd.DataFrame(dict(game=rows.game.astype(str), pair=rows.pair.astype(str),
                             agreement=agreement.astype(float),
                             delta=agreement.astype(float) - reference.astype(float)))
    per_game = data.groupby(["pair", "game"], sort=True)[["delta", "agreement"]].mean()
    pair_means = per_game.groupby(level="pair").mean()
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(pair_means), size=(samples, len(pair_means)))
    delta_boot = pair_means.delta.to_numpy()[draws].mean(axis=1)
    agreement_boot = pair_means.agreement.to_numpy()[draws].mean(axis=1)
    return dict(agreement_pair_mean=float(pair_means.agreement.mean()),
                agreement_pair_bootstrap_ci90=np.quantile(agreement_boot, [0.05, 0.95]).tolist(),
                agreement_delta_vs_reference_pair_mean=float(pair_means.delta.mean()),
                agreement_delta_vs_reference_pair_bootstrap_ci90=np.quantile(delta_boot, [0.05, 0.95]).tolist(),
                agreement_delta_vs_reference_pairs=len(pair_means)), [
                    {"pair": pair, "games": int(len(per_game.loc[pair])), "agreement": float(values.agreement),
                     "agreement_delta": float(values.delta)} for pair, values in pair_means.iterrows()]


def compile_evaluator(out, parity=False, model_path=None):
    binary = out / ("gbt-local-curve-parity" if parity else "gbt-local-curve")
    command = ["g++", "-O0" if parity else "-O3", "-std=c++17"]
    if parity:
        command += ["-DGBT_HEADER_PARITY", "-I", str(model_path.parent)]
    command += [str(Path(__file__).with_suffix(".cpp")), "-o", str(binary)]
    subprocess.run(command, check=True)
    return binary, command


def write_model(model, out):
    for name, values in [("starts.i32", model["starts"]), ("nodes.u64", model["nodes"]), ("base.f32", model["base"])]:
        values.tofile(out / name)


def run_evaluator(binary, out, matrix, model, checkpoints):
    matrix.tofile(out / "features.f32")
    command = [str(binary), str(out), str(len(matrix)), str(matrix.shape[1]), str(model["k"]),
               ",".join(map(str, checkpoints))]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True)
    return json.loads(result.stdout)


def group_summary(game_ids, agreement, tv, kl, js, bootstrap_samples, seed):
    values = pd.DataFrame(dict(game=game_ids.astype(str), agreement=agreement, total_variation=tv,
                               kl_teacher_to_prefix_nats=kl, js_divergence_nats=js))
    groups = values.groupby("game", sort=True)
    sums = groups.sum(numeric_only=True)
    counts = groups.size().to_numpy()
    means = sums.to_numpy() / counts[:, None]
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(counts), size=(bootstrap_samples, len(counts)))
    macro_samples = means[draws].mean(axis=1)
    row_samples = sums.to_numpy()[draws].sum(axis=1) / counts[draws].sum(axis=1)[:, None]
    result = dict(rows=len(values), games=len(counts))
    for column, name in enumerate(sums.columns):
        result[name + "_row_mean"] = float(values[name].mean())
        result[name + "_game_mean"] = float(means[:, column].mean())
        result[name + "_game_bootstrap_ci90"] = np.quantile(macro_samples[:, column], [0.05, 0.95]).tolist()
        result[name + "_row_bootstrap_ci90"] = np.quantile(row_samples[:, column], [0.05, 0.95]).tolist()
    per_game = []
    for game, count, mean in zip(sums.index, counts, means):
        per_game.append({"game": str(game), "rows": int(count), **{name: float(value) for name, value in zip(sums.columns, mean)}})
    return result, per_game


def slices(rows, teacher_prediction, classes):
    masks = {"all": np.ones(len(rows), dtype=bool)}
    for label, name in [(0, "F"), (1, "R"), (2, "L")]:
        masks["teacher_class_" + name] = np.array(classes)[teacher_prediction] == label
    if "is_queen" in rows:
        masks["queen"] = rows.is_queen.astype(bool).to_numpy()
    elif "dragon" in rows:
        masks["queen"] = rows.dragon.to_numpy() == rows.side.map({"A": 0, "B": 1}).to_numpy()
    if "round" in rows:
        masks["late_round_ge_350"] = rows["round"].to_numpy() >= 350
        masks["opening_round_lt_100"] = rows["round"].to_numpy() < 100
    for side in ["A", "B"]:
        masks["side_" + side] = rows.side.to_numpy() == side
    return masks


def divergence(teacher, prefix):
    minimum = 1e-300
    mixture = (teacher + prefix) / 2
    teacher_log = np.log(np.maximum(teacher, minimum))
    prefix_log = np.log(np.maximum(prefix, minimum))
    mixture_log = np.log(np.maximum(mixture, minimum))
    tv = np.abs(teacher - prefix).sum(axis=1) / 2
    kl = np.maximum(0, (teacher * (teacher_log - prefix_log)).sum(axis=1))
    js = np.maximum(0, (teacher * (teacher_log - mixture_log) + prefix * (prefix_log - mixture_log)).sum(axis=1) / 2)
    return tv, kl, js


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model-header", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--deployment-bot", type=Path, default=DEFAULT_BOT)
    parser.add_argument("--rounds", default="25,50,100,200,400,540,1000,1900,2345")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=62)
    parser.add_argument("--header-parity-rows", type=int, default=0)
    args = parser.parse_args()
    if args.bootstrap_samples < 1 or args.header_parity_rows < 0:
        parser.error("bootstrap samples must be positive; parity rows must be nonnegative")
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    model = load_model(args.model_header)
    manifest = json.loads(args.manifest.read_text())
    if manifest.get("teacher_model_sha256") not in (None, sha256(args.model_header)):
        raise ValueError("Teacher model SHA256 differs from manifest")
    if manifest.get("feature_names", model["names"]) != model["names"]:
        raise ValueError("Manifest feature order differs from model")
    dataset_hash = sha256(args.dataset)
    if manifest.get("dataset_sha256") not in (None, dataset_hash):
        raise ValueError("Dataset SHA256 differs from manifest")
    frame = pd.read_parquet(args.dataset)
    rows, matrix = select_holdout(frame, manifest, model["names"])
    criterion = manifest.get("candidate_screen")
    reference_rounds = int(criterion["reference_rounds"]) if criterion else min(540, model["full_rounds"])
    checkpoints = sorted(set(int(point) for point in args.rounds.split(",")) | {model["full_rounds"], reference_rounds})
    if checkpoints[0] < 1 or checkpoints[-1] != model["full_rounds"]:
        parser.error("Requested rounds exceed fitted teacher")
    write_model(model, args.out)
    binary, compile_command = compile_evaluator(args.out)
    print(f"Evaluating {len(rows)} rows from {rows.game.nunique()} frozen holdout games", flush=True)
    evaluation = run_evaluator(binary, args.out, matrix, model, checkpoints)
    teacher = np.fromfile(args.out / f'probabilities-{model["full_rounds"]}.f64', "<f8").reshape(len(rows), model["k"])
    if not np.isfinite(teacher).all() or not np.allclose(teacher.sum(axis=1), 1, atol=1e-14):
        raise ValueError("Invalid teacher probabilities")
    teacher_prediction = teacher.argmax(axis=1)
    reference_probabilities = np.fromfile(args.out / f"probabilities-{reference_rounds}.f64", "<f8").reshape(teacher.shape)
    reference_agreement = reference_probabilities.argmax(axis=1) == teacher_prediction
    reference_bytes = prefix_size(model, reference_rounds, args.deployment_bot)["deployment_bot_zip_bytes"]
    masks = slices(rows, teacher_prediction, model["classes"])
    points, per_game, flat_slices, per_pair = [], [], [], []
    for rounds in checkpoints:
        prefix = np.fromfile(args.out / f"probabilities-{rounds}.f64", "<f8").reshape(len(rows), model["k"])
        if not np.isfinite(prefix).all() or not np.allclose(prefix.sum(axis=1), 1, atol=1e-14):
            raise ValueError(f"Invalid prefix probabilities at {rounds} rounds")
        agreement = prefix.argmax(axis=1) == teacher_prediction
        tv, kl, js = divergence(teacher, prefix)
        point = {"rounds": rounds, **prefix_size(model, rounds, args.deployment_bot), "slices": {}}
        paired, pairs = paired_delta_summary(rows, agreement, reference_agreement, args.bootstrap_samples, args.seed)
        point.update(paired)
        point["reference_rounds"] = reference_rounds
        point["upload_saving_fraction_vs_reference"] = 1 - point["deployment_bot_zip_bytes"] / reference_bytes
        if criterion:
            point["passes_predeclared_compression_screen"] = bool(
                point["upload_saving_fraction_vs_reference"] >= criterion["minimum_upload_saving_fraction"] and
                paired["agreement_delta_vs_reference_pair_bootstrap_ci90"][0] >= criterion["paired_agreement_delta_90pct_ci_lower_bound"])
        per_pair += [{"rounds": rounds, **pair} for pair in pairs]
        for name, mask in masks.items():
            if not mask.any():
                point["slices"][name] = {"rows": 0, "games": 0, "status": "no rows in holdout"}
                continue
            result, games = group_summary(rows.game.to_numpy()[mask], agreement[mask], tv[mask], kl[mask], js[mask],
                                           args.bootstrap_samples, args.seed)
            point["slices"][name] = result
            flat_slices.append({"rounds": rounds, "slice": name, **result})
            if name == "all":
                point.update(result)
                per_game += [{"rounds": rounds, **game} for game in games]
        points.append(point)
        print(f'{rounds:4d} rounds: game agreement {point["agreement_game_mean"]:.6f}; '
              f'CI90 {point["agreement_game_bootstrap_ci90"]}; bot zip {point["deployment_bot_zip_bytes"]} bytes', flush=True)
    parity = None
    if args.header_parity_rows:
        if args.model_header.resolve() != DEFAULT_MODEL.resolve():
            raise ValueError("Header parity requires the committed original model")
        parity_dir = args.out / "header-parity"
        parity_dir.mkdir(exist_ok=True)
        for name in ["starts.i32", "nodes.u64", "base.f32"]:
            shutil.copyfile(args.out / name, parity_dir / name)
        sample_indices = np.random.default_rng(args.seed).choice(len(rows), min(args.header_parity_rows, len(rows)), replace=False)
        parity_binary, parity_command = compile_evaluator(parity_dir, parity=True, model_path=args.model_header)
        parity = run_evaluator(parity_binary, parity_dir, matrix[sample_indices], model, [model["full_rounds"]])
        parity["compile_command"] = parity_command
        expected = teacher[sample_indices]
        actual = np.fromfile(parity_dir / f'probabilities-{model["full_rounds"]}.f64', "<f8").reshape(expected.shape)
        if not np.array_equal(actual, expected):
            raise ValueError("Parity sample differs from primary evaluator")
        parity["primary_evaluator_probabilities_bit_equal"] = True
        parity["sample_seed"] = args.seed
    final = points[-1]
    if final["agreement_game_mean"] != 1 or final["total_variation_row_mean"] != 0:
        raise ValueError("Full teacher does not agree with itself exactly")
    bot_sources = {path.name: sha256(path) for path in sorted(args.deployment_bot.iterdir())
                   if path.suffix in {".cpp", ".hpp", ".cc", ".hh", ".c", ".h"}}
    result = dict(kind="local GBT prefix compression fidelity", teacher_full_rounds=model["full_rounds"],
                  interpretation="Agreement with a fixed full GBT teacher on fresh local holdout states; not expert accuracy, learned improvement or a promotion result",
                  dataset=str(args.dataset), dataset_sha256=dataset_hash, manifest=str(args.manifest), manifest_sha256=sha256(args.manifest),
                  model=str(args.model_header), model_sha256=sha256(args.model_header),
                  evaluator_source_sha256=sha256(Path(__file__).with_suffix(".cpp")),
                  deployment_bot=str(args.deployment_bot), deployment_source_sha256=bot_sources,
                  all_dataset_rows=len(frame), all_dataset_games=int(frame.game.nunique()),
                  evaluated_holdout_rows=len(rows), evaluated_holdout_games=int(rows.game.nunique()),
                  holdout_game_ids=sorted(rows.game.astype(str).unique().tolist()),
                  holdout_partition="holdout", bootstrap=dict(samples=args.bootstrap_samples, seed=args.seed,
                      grouping="Game/row intervals resample whole games; pair agreement and prefix-minus-reference intervals resample whole seat pairs",
                      primary="Absolute fidelity: equal weight per game; paired differences: equal weight per pair, then equal weight per game inside pair",
                      interval="central 90% percentile interval [5th,95th]; row-weighted clustered intervals also reported"),
                  divergence="total variation, KL(teacher||prefix) and Jensen-Shannon; natural-log units",
                  upload_size="ZIP_DEFLATED C/C++ source upload for deployment bot after replacing only its direction header; not compiled size",
                  header_parity=parity, compile_command=compile_command, evaluator=evaluation,
                  queen_slice_available="queen" in masks, elapsed_seconds=time.monotonic() - started, points=points)
    result["runtime"] = manifest.get("runtime")
    result["sampling"] = manifest.get("sampling")
    result["candidate_screen"] = criterion
    if criterion:
        passed = [point for point in points if point.get("passes_predeclared_compression_screen")]
        result["screen_recommendation"] = dict(
            qualifying_rounds=[point["rounds"] for point in passed],
            smallest_upload_rounds=min(passed, key=lambda point: point["deployment_bot_zip_bytes"])["rounds"] if passed else None,
            scope=criterion.get("scope", "Compression screen only; actual reserved evaluation required before adoption"))
    (args.out / "curve.json").write_text(json.dumps(result, indent=2) + "\n")
    tables = {"curve.csv": [{key: value for key, value in point.items() if key != "slices"} for point in points],
              "per-game.csv": per_game, "per-pair-deltas.csv": per_pair, "slices.csv": flat_slices}
    for filename, records in tables.items():
        with (args.out / filename).open("w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    print(args.out / "curve.json", flush=True)


if __name__ == "__main__":
    main()
