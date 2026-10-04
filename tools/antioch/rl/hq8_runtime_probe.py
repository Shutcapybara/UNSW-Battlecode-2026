"""Capture H-Q8 rows from real unswbc 1.2.5 controller observations.

This tool copies carthage-05-free-sprint into build/, adds a LOG-only probe,
replays selected frozen local-pilot-v1 fixture specs, and compares every
logged C++ row with features reconstructed from that probe game's replay.
The measured bot snapshot and the shared H-Q8 encoder are never modified.

    .venv/bin/python tools/antioch/rl/hq8_runtime_probe.py --games 1,22,41,62,81
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "build/antioch/rl/local-pilot-v1"
OUT = ROOT / "build/antioch/rl/hq8-runtime-probe-v1"
BASE_BOT = "carthage-05-free-sprint"
BASE_DIR = ROOT / "bots" / BASE_BOT
PROBE_DIR = OUT / "bot"
RUNTIME = ROOT / ".venv/bin/unswbc"
LOG_RE = re.compile(r"^LOG HQ8V1 (\d+) (\d+) (-?\d+(?:,-?\d+)*)$", re.MULTILINE)
RESULT_RE = re.compile(r"winner: ([AB]) .*?round (\d+) .*?\((.*?)\)")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(path)


def source_fingerprint(path: Path) -> str:
    """Mirror run_panel.runtime_fingerprint for the existing bot snapshot."""
    sys.path.insert(0, str(ROOT))
    from tools.analysis.features.run_panel import runtime_fingerprint
    return runtime_fingerprint(path)


def make_probe_copy(probe_dir: Path) -> dict:
    header = ROOT / "tools/antioch/rl/hq8_features.hpp"
    shutil.copytree(BASE_DIR, probe_dir, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".unswbc-build", "bot", "*.o"))
    shutil.copy2(header, probe_dir / "hq8_features.hpp")
    main_path = probe_dir / "main.cpp"
    main = main_path.read_text()
    include = '#include "world.hpp"\n'
    if main.count(include) != 1:
        raise RuntimeError("Unexpected base main.cpp include layout")
    main = main.replace(include, include + '#include "hq8_features.hpp"\n', 1)
    ctor = "    hb1::Proc hproc(ct.get_id(), ct.get_team().value, game.width, game.height, game.unit_limit);\n"
    if main.count(ctor) != 1:
        raise RuntimeError("Unexpected base H-B1 processor constructor")
    main = main.replace(ctor, ctor +
        "    hq8::Encoder hqproc(ct.get_id(), ct.get_team().value, game.width, game.height, game.unit_limit);\n", 1)
    feature_call = """            hb_row = hproc.features(hb1::block_from(ct, game));
            pol.hb_row = &hb_row;"""
    feature_code = """            hb1::Block const observation = hb1::block_from(ct, game);
            hb_row = hproc.features(observation);
            pol.hb_row = &hb_row;
            hq8::Block hqblock;
            hqblock.round = observation.round;
            hqblock.length = observation.length;
            for (size_t k = 0; k < hqblock.tiles.size(); ++k) {
                auto const& src = observation.tiles[k];
                hqblock.tiles[k] = {src.x, src.y, src.p, src.cd};
            }
            for (auto const& src : observation.bodies)
                hqblock.bodies.push_back({src.team, src.id, src.x, src.y, src.facing, src.head});
            hqblock.H = observation.Hm;
            hqblock.V = observation.Vm;
            auto const values = hqproc.features(hqblock);
            std::cout << "LOG HQ8V1 " << ct.get_id() << " " << game.get_round_num() << " ";
            for (size_t k = 0; k < values.size(); ++k)
                std::cout << (k ? "," : "") << values[k];
            std::cout << "\\n";"""
    if main.count(feature_call) != 1:
        raise RuntimeError("Unexpected base feature-call layout")
    main = main.replace(feature_call, feature_code, 1)
    split_call = "            hproc.record_split(dec.split);\n"
    if main.count(split_call) != 1:
        raise RuntimeError("Unexpected base split-memory update")
    main = main.replace(split_call, split_call + "            hqproc.record_split();\n", 1)
    main_path.write_text(main)
    return {
        "base_bot": BASE_BOT,
        "base_runtime_fingerprint": source_fingerprint(BASE_DIR),
        "pilot_expected_base_fingerprint": json.loads((PILOT / "manifest.json").read_text())[
            "source_fingerprints"][BASE_BOT],
        "probe_main_sha256": sha256(main_path),
        "probe_hq8_header_sha256": sha256(probe_dir / "hq8_features.hpp"),
        "probe_scope": "Only LOG HQ8V1 records and a separate H-Q8 encoder were added; Ares decisions, HB1 inputs and responses are preserved.",
    }


def parse_probe_logs(text: str) -> list[tuple[int, int, list[int]]]:
    records = []
    for match in LOG_RE.finditer(text):
        values = [int(value) for value in match.group(3).split(",")]
        records.append((int(match.group(1)), int(match.group(2)), values))
    return records


def replay_rows(replay: Path, side: str):
    dump_cmd = [sys.executable, str(ROOT / "tools/hb1/cpp/dump_blocks.py"), str(replay), side]
    dumped = subprocess.run(dump_cmd, cwd=ROOT, capture_output=True, text=True)
    if dumped.returncode:
        raise RuntimeError(f"Replay block reconstruction failed: {dumped.stderr[-2000:]}")
    sys.path.insert(0, str(ROOT / "tools/team_recon_claude"))
    from hq8_features import Encoder, NAMES
    import features_view
    actors = {}
    records = []
    lines = dumped.stdout.splitlines()
    i = 0
    while i < len(lines):
        parts = lines[i].split()
        i += 1
        if not parts:
            continue
        if parts[0] == "TURN":
            dragon = int(parts[1])
            if dragon not in actors:
                actors[dragon] = Encoder(dragon, parts[2], *map(int, parts[3:]))
            block_lines = []
            while i < len(lines) and lines[i] != "END":
                block_lines.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError("Truncated TURN block in replay dump")
            i += 1
            block, consumed = features_view.parse_block(block_lines)
            if consumed != len(block_lines):
                raise ValueError("Trailing data in replay TURN block")
            values = actors[dragon].features(block)
            records.append((dragon, block["round"], values))
        elif parts[:2] == ["ACT", "split"]:
            actors[dragon].record_split()
    return records, NAMES


def compare(runtime_rows, replay, names):
    counts = {}
    examples = []
    if len(runtime_rows) != len(replay):
        counts["row_count"] = abs(len(runtime_rows) - len(replay))
    for i in range(min(len(runtime_rows), len(replay))):
        did, rnd, actual = runtime_rows[i]
        expected_did, expected_rnd, expected = replay[i]
        if (did, rnd) != (expected_did, expected_rnd):
            counts["actor_or_round"] = counts.get("actor_or_round", 0) + 1
            if len(examples) < 50:
                examples.append({"index": i, "runtime": [did, rnd], "replay": [expected_did, expected_rnd]})
        if len(actual) != len(expected):
            counts["feature_count"] = counts.get("feature_count", 0) + 1
            continue
        for name, got, want in zip(names, actual, expected):
            if got != want:
                counts[name] = counts.get(name, 0) + 1
                if len(examples) < 50:
                    examples.append({"index": i, "dragon": did, "round": rnd,
                                     "feature": name, "runtime": got, "replay": want})
    return {"runtime_rows": len(runtime_rows), "replay_rows": len(replay),
            "mismatch_counts": counts, "exact": not counts, "mismatch_examples": examples}


def run_fixture(fixture: dict, out: Path, probe_dir: Path):
    game_id = fixture["game_id"]
    replay = out / "replays" / f"pilot-{game_id:04d}.replay"
    log = out / "logs" / f"pilot-{game_id:04d}.txt"
    replay.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    base_replay = PILOT / "replays" / f"{fixture['game']}.replay"
    if not base_replay.is_file():
        raise FileNotFoundError(base_replay)
    if replay.exists() or log.exists():
        raise FileExistsError(f"Refusing to overwrite diagnostic artifact for game {game_id}")
    map_path = ROOT / "maps" / f"{fixture['map']}.map"
    bots = []
    for key in ("botA", "botB"):
        if fixture[key] == BASE_BOT:
            bots.append(str(probe_dir))
        else:
            bots.append(str(ROOT / "bots" / fixture[key]))
    command = [str(RUNTIME), "run", "-v", "--no-logs", "--no-indicator", "--no-draw",
               "--seed", str(fixture["seed"]), "-o", str(replay), str(map_path), *bots]
    started = time.monotonic()
    with log.open("w") as output:
        result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                timeout=1800, check=False)
    elapsed = round(time.monotonic() - started, 3)
    text = log.read_text(errors="replace")
    runtime_rows = parse_probe_logs(text)
    if result.returncode or not replay.is_file():
        raise RuntimeError(f"Probe match {game_id} failed rc={result.returncode}; see {log}")
    replayed_rows, names = replay_rows(replay, fixture["seat"])
    result_report = compare(runtime_rows, replayed_rows, names)
    result_line = next((line for line in reversed(text.splitlines()) if line.startswith("winner:")), "")
    return {
        "game_id": game_id,
        "pilot_fixture": {key: fixture[key] for key in ("game", "map", "seed", "botA", "botB", "seat", "opp", "pair", "partition")},
        "pilot_replay_sha256": sha256(base_replay),
        "probe_replay_sha256": sha256(replay),
        "probe_log_sha256": sha256(log),
        "probe_replay": str(replay.relative_to(ROOT)),
        "probe_log": str(log.relative_to(ROOT)),
        "seconds": elapsed,
        "returncode": result.returncode,
        "result_line": result_line,
        "runtime_actor_rows": len(runtime_rows),
        "replay_actor_rows": len(replayed_rows),
        "coverage": {
            "queen_rows": sum(row[2][names.index("is_queen")] == 1 for row in replayed_rows),
            "nonqueen_rows": sum(row[2][names.index("is_queen")] == 0 for row in replayed_rows),
            "late_rows_round_ge_350": sum(row[1] >= 350 for row in replayed_rows),
            "stale_enemy_rows": sum(row[2][names.index("enemy_seen_age")] > 0 for row in replayed_rows),
            "split_age_rows": sum(row[2][names.index("own_split_age")] >= 0 for row in replayed_rows),
        },
        **result_report,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", default="1,22,41,62,81",
                        help="Frozen pilot game IDs; selected defaults cover all five maps and both seats")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if importlib.metadata.version("unswbc") != "1.2.5":
        raise SystemExit("Runtime parity probe requires unswbc==1.2.5")
    manifest_path = PILOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("runtime") != "1.2.5":
        raise SystemExit("Frozen local pilot was not produced by unswbc 1.2.5")
    expected = manifest["source_fingerprints"][BASE_BOT]
    actual = source_fingerprint(BASE_DIR)
    if actual != expected:
        raise SystemExit(f"Measured bot fingerprint changed: manifest={expected} current={actual}")
    game_ids = [int(value) for value in args.games.split(",") if value]
    fixtures_by_id = {fixture["game_id"]: fixture for fixture in manifest["fixtures"]}
    if not game_ids or len(game_ids) != len(set(game_ids)) or any(game_id not in fixtures_by_id for game_id in game_ids):
        parser.error("--games must be unique IDs in the frozen local pilot")
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"Output already contains artifacts: {out}; use a new --out path")
    out.mkdir(parents=True, exist_ok=True)
    probe_dir = out / "bot"
    probe = make_probe_copy(probe_dir)
    from unswbc.project import Project
    compile_started = time.monotonic()
    Project.from_dir(str(probe_dir)).compile()
    compile_seconds = round(time.monotonic() - compile_started, 3)
    reports = []
    for game_id in game_ids:
        report = run_fixture(fixtures_by_id[game_id], out, probe_dir)
        reports.append(report)
        print(json.dumps({"game_id": game_id, "exact": report["exact"],
                          "runtime_rows": report["runtime_actor_rows"],
                          "seconds": report["seconds"]}), flush=True)
    summary = {
        "schema": "antioch-hq8-runtime-observation-parity-v1",
        "runtime": importlib.metadata.version("unswbc"),
        "pilot_manifest_sha256": sha256(manifest_path),
        "pilot_source_fingerprint": expected,
        "probe": probe,
        "probe_compile_seconds": compile_seconds,
        "probe_code_sha256": sha256(Path(__file__)),
        "feature_schema_sha256": sha256(ROOT / "tools/antioch/rl/hq8_features.hpp"),
        "games": reports,
        "total_runtime_rows": sum(report["runtime_actor_rows"] for report in reports),
        "all_exact": all(report["exact"] for report in reports),
        "limitations": [
            "Each selected frozen pilot fixture was rerun with the probe in the same seat, map, seed and opponent roster; the comparison is between the C++ controller observation and reconstruction from that same probe rerun replay.",
            "Verbose LOG output and the added encoder consume extra CPU and are diagnostic only; these runs do not measure candidate performance.",
            "unswbc 1.2.5 seed fixes engine randomness but its CLI notes that non-sandbox bot-local randomness may differ between reruns.",
        ],
    }
    write_json(out / "report.json", summary)
    print(json.dumps({"report": str(out / "report.json"), "all_exact": summary["all_exact"],
                      "total_runtime_rows": summary["total_runtime_rows"],
                      "probe_compile_seconds": compile_seconds}, indent=2))
    if not summary["all_exact"]:
        raise SystemExit("Runtime observation parity failed; see report.json")


if __name__ == "__main__":
    main()
