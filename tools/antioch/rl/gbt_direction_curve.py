"""Measure the archived HB1 direction prior's exact size versus boosting rounds.

    .venv/bin/python tools/antioch/rl/gbt_direction_curve.py
    .venv/bin/python tools/antioch/rl/gbt_direction_curve.py \
        --heldout-parquet build/hb1/q1/direction.parquet --games build/hb1/games.parquet

The default needs only the committed compact model. It reports current byte sizes
and explicitly labels the rounded, historical accuracy anchors as unverified.
With the original HB1 inputs, it evaluates the seed-62 20% game holdout on CPU.
This measures truncation of one fitted model, not a depth ablation or a refit.
Zip bytes include all C/C++ files of the deployment bot, replacing its direction
header with the selected prefix. They are source upload bytes, not wasm bytes.
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
MODEL = ROOT / "bots/hb1-04-deployable/hb1_direction_compact.hpp"
BOT = ROOT / "bots/hb1-14-prior-r540"
OUTPUT = ROOT / "build/antioch/rl/gbt-direction-curve"
ARCHIVED = {100: 0.827, 400: 0.842, 1000: 0.847, 1900: 0.849, 2345: 0.850}


def array(text, name):
    match = re.search(rf"\b{name}\[\] = \{{(.*?)\}};", text, re.S)
    if match is None:
        raise ValueError(f"Missing compact-model array {name}")
    return match.group(1)


def zipped_header(header, bot):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("hb1_direction_compact.hpp", header.encode())
    header_bytes = len(buffer.getvalue())
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bot.iterdir()):
            if path.suffix in {".cpp", ".hpp", ".cc", ".hh", ".c", ".h"}:
                if path.name == "hb1_direction_compact.hpp":
                    archive.writestr(path.name, header.encode())
                else:
                    archive.write(path, path.name)
    return header_bytes, len(buffer.getvalue())


def evaluate(args, names, starts, node_body, base, classes, points):
    """Use the original game split; compile a one-core compact-tree evaluator."""
    import numpy as np
    import pandas as pd

    games = pd.read_parquet(args.games)
    corpus = sorted(games.loc[games["set"] == "corpus", "game"].astype(int))
    test_games = set(np.random.default_rng(62).choice(corpus, len(corpus) // 5, replace=False).tolist())
    rows = pd.read_parquet(args.heldout_parquet)
    rows = rows[rows.game.astype(int).isin(test_games)]
    rows = rows[(rows.y_family == "move") & rows.y_first.isin(["F", "R", "L"])]
    if rows.empty:
        raise ValueError("No original held-out move rows found")
    matrix = rows[names].to_numpy(dtype="<f4")
    labels = rows.y_first.map({"F": 0, "R": 1, "L": 2}).to_numpy(dtype="<i4")
    matrix.tofile(args.out / "features.f32")
    labels.tofile(args.out / "labels.i32")
    np.asarray(starts, dtype="<i4").tofile(args.out / "starts.i32")
    np.fromiter((int(word, 16) for word in re.findall(r"0x[0-9a-f]+", node_body)), dtype="<u8").tofile(
        args.out / "nodes.u64")
    binary = args.out / "gbt_direction_curve"
    subprocess.run(["g++", "-O2", "-std=c++17", str(Path(__file__).with_suffix(".cpp")), "-o", str(binary)],
                   check=True)
    command = [str(binary), str(args.out), str(len(rows)), str(len(names)), str(len(classes)),
               ",".join(map(str, points)), ",".join(map(str, base)), ",".join(map(str, classes))]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    scores = {int(line.split(",")[0]): float(line.split(",")[1]) for line in result.stdout.splitlines()}
    return scores, {"seed": 62, "split": "20% of corpus games; no fitting in this command",
                    "corpus_games": len(corpus), "heldout_games": len(test_games),
                    "heldout_games_with_rows": int(rows.game.nunique()), "heldout_rows": len(rows),
                    "heldout_parquet": str(args.heldout_parquet), "games_parquet": str(args.games)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-header", type=Path, default=MODEL)
    parser.add_argument("--deployment-bot", type=Path, default=BOT)
    parser.add_argument("--rounds", default="25,50,100,200,400,540,1000,1900,2345")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    parser.add_argument("--heldout-parquet", type=Path)
    parser.add_argument("--games", type=Path)
    args = parser.parse_args()
    if bool(args.heldout_parquet) != bool(args.games):
        parser.error("--heldout-parquet and --games must be supplied together")
    args.out.mkdir(parents=True, exist_ok=True)
    source = args.model_header.read_text()
    n_classes = int(re.search(r"dirc_K = (\d+)", source).group(1))
    starts = [int(value) for value in array(source, "dirc_tree_start").split(",") if value.strip()]
    names = re.findall(r'"([^"]+)"', array(source, "dirc_feats"))
    base = [float(value.strip().removesuffix("f")) for value in array(source, "dirc_base").split(",")]
    classes = [int(value) for value in array(source, "dirc_classes").split(",")]
    prelude, tail = source.split("inline constexpr unsigned long long dirc_nodes[] = {\n", 1)
    body, ending = tail.split("\n};", 1)
    lines = body.splitlines()
    if any(line.count(",") != 12 for line in lines[:-1]):
        raise ValueError("Expected the generator's 12-node-per-line format")
    n_nodes = sum(line.count(",") for line in lines)
    points = sorted(set(int(point) for point in args.rounds.split(",")))
    if min(points) < 1 or max(points) > len(starts) // n_classes:
        parser.error("rounds must lie within the archived fitted model")
    scores, evaluation = ({}, None)
    if args.heldout_parquet:
        scores, evaluation = evaluate(args, names, starts, body, base, classes, points)
    records = []
    for rounds in points:
        trees = rounds * n_classes
        nodes = starts[trees] if trees < len(starts) else n_nodes
        whole, remainder = divmod(nodes, 12)
        prefix_lines = lines[:whole]
        if remainder:
            prefix_lines.append(",".join(lines[whole].split(",")[:remainder]) + ",")
        head = re.sub(r"dirc_n_trees = \d+", f"dirc_n_trees = {trees}", prelude)
        head = re.sub(r"dirc_tree_start\[\] = \{.*?\};",
                      "dirc_tree_start[] = {" + ",".join(map(str, starts[:trees])) + "};", head, flags=re.S)
        header = head + "inline constexpr unsigned long long dirc_nodes[] = {\n" + "\n".join(prefix_lines) + "\n};" + ending
        zipped, bot_zip = zipped_header(header, args.deployment_bot)
        record = {"rounds": rounds, "trees": trees, "nodes": nodes,
                  "compact_node_and_start_bytes": nodes * 8 + trees * 4,
                  "header_source_bytes": len(header.encode()), "header_zip_bytes": zipped,
                  "deployment_bot_zip_bytes": bot_zip, "upload_fits_4_mib": bot_zip <= 4 * 2**20,
                  "heldout_accuracy_current": scores.get(rounds),
                  "archived_accuracy_30k_rows_rounded_unverified": ARCHIVED.get(rounds)}
        records.append(record)
        print(f"{rounds:4d} rounds: header zip {zipped / 1024:8.1f} KiB; "
              f"bot zip {bot_zip / 2**20:6.2f} MiB; current accuracy {scores.get(rounds)}", flush=True)
    display = lambda path: str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    result = {"model": display(args.model_header),
              "model_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "deployment_bot": display(args.deployment_bot),
              "method": "Prefix truncation of the original HB1 cap3000/leaves255 fitted model; no depth refit",
              "size_method": "Original 8-byte compact-node source layout; Python ZIP_DEFLATED at default compression",
              "evaluation": evaluation,
              "accuracy_status": "measured on original held-out rows" if evaluation else "blocked: original HB1 held-out inputs absent",
              "archived_accuracy_source": "claude/hb1-status.md:242-243; 30,000 held-out rows; rounded to 3 decimals; not rerun",
              "archived_accuracy_warning": "Only valid for the default original HB1 model; historical samples differ from the full 179,436-row holdout",
              "original_corpus_warning": "Restore the original 817-game games.parquet; rebuilding against an enlarged corpus changes the seed-62 holdout and can include training games",
              "resume_command": ".venv/bin/python tools/antioch/rl/gbt_direction_curve.py --heldout-parquet build/hb1/q1/direction.parquet --games build/hb1/games.parquet",
              "required_inputs": ["build/hb1/q1/direction.parquet", "build/hb1/games.parquet"],
              "depth_refit_required_inputs": "Also restore build/hb1/v5/corpus/*.parquet (original training games); use CPU XGBoost for a predeclared depth/round grid",
              "points": records}
    if args.model_header.resolve() != MODEL.resolve():
        result["archived_accuracy_source"] = None
        for record in records:
            record["archived_accuracy_30k_rows_rounded_unverified"] = None
    (args.out / "curve.json").write_text(json.dumps(result, indent=2) + "\n")
    with (args.out / "curve.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(args.out / "curve.json")


if __name__ == "__main__":
    main()
