"""Measure complete Carthage/Ares self-play rollouts with the deployed HB1 prior.

The benchmark runs the frozen Carthage05 executable on both sides in the
official CLI engine, serially, under the installed unswbc 1.2.5 runtime. It
records replay wall time and counts every actor turn from the resulting replay.
Replay capture is included in wall time, making the throughput conservative
for rollout collection. It measures this full policy, unlike the untrained
MLP callback throughput probe.

    nice -n 10 .venv/bin/python tools/antioch/rl/ares_rollout_bench.py \
      --out build/antioch/rl/ares-rollout-v1
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
BOT = ROOT / "bots/carthage-05-free-sprint"
DEFAULT_MAPS = ("arena", "big_empty", "Colosseum", "default_small", "stronghold")
DEFAULT_SEEDS = (101, 102)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify_policy(bot: Path) -> dict:
    model = bot / "hb1_direction_compact.hpp"
    policy = bot / "policy.hpp"
    source = model.read_text()
    match = re.search(r"dirc_n_trees\s*=\s*(\d+)\s*;", source)
    if not match:
        raise ValueError(f"Cannot find the compact direction tree count in {model}")
    trees = int(match.group(1))
    if trees != 1620 or trees % 3:
        raise ValueError(f"Expected the committed 540-round prior (1620 trees), found {trees}")
    policy_source = policy.read_text()
    if "hb1::dirc_proba" not in policy_source or "hb1::dirc_bind" not in policy_source:
        raise ValueError("Carthage05 policy no longer calls the HB1 compact direction prior")
    from tools.analysis.features.run_panel import runtime_fingerprint
    return {
        "bot": str(bot.relative_to(ROOT)),
        "source_fingerprint": runtime_fingerprint(str(bot)),
        "prior_rounds": trees // 3,
        "prior_trees": trees,
        "main_sha256": sha256(bot / "main.cpp"),
        "policy_sha256": sha256(policy),
        "prior_header_sha256": sha256(model),
        "params_sha256": sha256(bot / "params.hpp"),
    }


def count_turns(replay: Path) -> tuple[int, dict[str, int]]:
    sys.path.insert(0, str(ROOT / "tools/team_recon_claude"))
    import recon

    game = recon.Game(replay)
    count = 0

    def on_event(kind, **_event):
        nonlocal count
        if kind == "turn":
            count += 1

    game.run(on_event)
    bad = {str(k): int(v) for k, v in game.checks.items()
           if v and (str(k).endswith("bad") or "mismatch" in str(k))}
    return count, bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bot", type=Path, default=BOT)
    ap.add_argument("--maps", default=",".join(DEFAULT_MAPS))
    ap.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    ap.add_argument("--out", type=Path, default=ROOT / "build/antioch/rl/ares-rollout-v1")
    ap.add_argument("--timeout", type=int, default=900, help="Per-game timeout in seconds")
    args = ap.parse_args()
    bot = args.bot.resolve()
    out = args.out.resolve()
    maps = tuple(x.strip() for x in args.maps.split(",") if x.strip())
    seeds = tuple(int(x) for x in args.seeds.split(",") if x.strip())
    if not maps or not seeds or args.timeout < 1:
        ap.error("maps and seeds must be nonempty; timeout must be positive")
    version = importlib.metadata.version("unswbc")
    if version != "1.2.5":
        raise SystemExit(f"This frozen benchmark requires unswbc 1.2.5; found {version}")
    bot_info = verify_policy(bot)
    out.mkdir(parents=True, exist_ok=True)
    replay_dir = out / "replays"
    replay_dir.mkdir(exist_ok=True)
    warmup_map = maps[0]
    warmup_seed = min(seeds) - 1
    warmup_replay = replay_dir / "warmup.replay"
    warmup_command = [str(ROOT / ".venv/bin/unswbc"), "run",
                      str(ROOT / "maps" / f"{warmup_map}.map"),
                      str(bot), str(bot), "--seed", str(warmup_seed), "--no-logs",
                      "--no-indicator", "--no-draw", "--no-debug", "-o", str(warmup_replay)]
    warmup_start = time.perf_counter()
    warmup = subprocess.run(warmup_command, cwd=ROOT, text=True, capture_output=True,
                            timeout=args.timeout, check=False)
    warmup_seconds = time.perf_counter() - warmup_start
    if warmup.returncode != 0 or not warmup_replay.is_file():
        raise RuntimeError(
            f"warmup failed (rc={warmup.returncode})\n"
            f"stdout:\n{warmup.stdout[-2000:]}\nstderr:\n{warmup.stderr[-2000:]}"
        )
    print(json.dumps({"warmup": True, "map": warmup_map, "seed": warmup_seed,
                      "seconds_including_first_build": warmup_seconds,
                      "replay_sha256": sha256(warmup_replay)}), flush=True)
    rows = []
    for seed in seeds:
        for map_name in maps:
            board = ROOT / "maps" / f"{map_name}.map"
            if not board.is_file():
                raise FileNotFoundError(board)
            replay = replay_dir / f"s{seed}__{map_name}__carthage05-selfplay.replay"
            command = [str(ROOT / ".venv/bin/unswbc"), "run", str(board),
                       str(bot), str(bot), "--seed", str(seed), "--no-logs",
                       "--no-indicator", "--no-draw", "--no-debug", "-o", str(replay)]
            start = time.perf_counter()
            completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                                       timeout=args.timeout, check=False)
            seconds = time.perf_counter() - start
            if completed.returncode != 0 or not replay.is_file():
                raise RuntimeError(
                    f"{map_name} seed {seed} failed (rc={completed.returncode})\n"
                    f"stdout:\n{completed.stdout[-2000:]}\nstderr:\n{completed.stderr[-2000:]}"
                )
            actor_turns, bad_checks = count_turns(replay)
            if bad_checks:
                raise RuntimeError(f"{map_name} seed {seed}: reconstruction checks failed: {bad_checks}")
            row = {
                "map": map_name,
                "seed": seed,
                "seconds_including_engine_bots_and_replay_write": seconds,
                "actor_turns": actor_turns,
                "actor_turns_per_second": actor_turns / seconds,
                "full_games_per_hour_at_this_fixture_rate": 3600 / seconds,
                "replay_sha256": sha256(replay),
                "replay_bytes": replay.stat().st_size,
                "terminal_line": next((line for line in completed.stdout.splitlines()
                                        if line.startswith("winner:") or line.startswith("draw:")), ""),
            }
            rows.append(row)
            print(json.dumps(row), flush=True)

    total_seconds = sum(row["seconds_including_engine_bots_and_replay_write"] for row in rows)
    total_turns = sum(row["actor_turns"] for row in rows)
    report = {
        "schema": "antioch-ares-search-self-play-throughput-v1",
        "status": "PASS",
        "runtime": version,
        "engine_mode": "official unswbc CLI, no judge sandbox, serial complete games",
        "policy": bot_info,
        "seats": "same frozen bot on A and B in every game",
        "maps": list(maps),
        "seeds": list(seeds),
        "games": len(rows),
        "warmup_seconds_excluded_from_rate": warmup_seconds,
        "total_wall_seconds": total_seconds,
        "total_actor_turns": total_turns,
        "aggregate_actor_turns_per_second": total_turns / total_seconds,
        "aggregate_actor_decisions_per_hour": total_turns * 3600 / total_seconds,
        "aggregate_complete_games_per_hour": len(rows) * 3600 / total_seconds,
        "wall_time_includes": "engine, both Carthage05 C++ searches using the verified 540-round HB1 prior, game orchestration and compact replay writes",
        "limits": [
            "A small five-map/two-seed self-play throughput sample, not a training-loop or playing-strength result.",
            "Replay feature extraction, expert-target serialization and GBT refitting are not included.",
            "Throughput is specific to this host, installed 1.2.5 runtime and the frozen Carthage05 source fingerprint.",
        ],
        "fixtures": rows,
    }
    report_path = out / "report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in (
        "runtime", "games", "total_actor_turns", "total_wall_seconds",
        "aggregate_actor_turns_per_second", "aggregate_actor_decisions_per_hour",
        "aggregate_complete_games_per_hour")}, indent=2), flush=True)
    print(f"report: {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
