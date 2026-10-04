#!/usr/bin/env python3
"""Run the D-043 post-M2 pool using the official zoo, fixture order and runner.

The shared run_panel.py still uses its pre-swap LIVE_MAPS for panel='z1'. This
Rome-owned wrapper swaps only the map list for LIVE_MAPS_M2 and delegates game
execution, outcome extraction and replay format to run_panel.run().
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features import run_panel as R


def fixtures(bot: str, seeds: list[int]) -> list[dict]:
    bot = bot.removeprefix("bots/")
    out = []
    for seed in seeds:
        for map_name in R.LIVE_MAPS_M2:
            for opponent in R.ZOO:
                for a, b in ((bot, opponent), (opponent, bot)):
                    out.append(dict(
                        map=map_name,
                        seed=seed,
                        botA=a,
                        botB=b,
                        game=f"s{seed}__{map_name.replace('/', '_')}__{Path(a).name}__{Path(b).name}",
                    ))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bot", required=True)
    ap.add_argument("--seeds", default="1,2,3")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--out")
    ap.add_argument("--unswbc", default=str(Path(sys.executable).parent / "unswbc"))
    ap.add_argument("--no-logs", action="store_true")
    a = ap.parse_args()
    bot = a.bot.removeprefix("bots/")
    seeds = [int(x) for x in a.seeds.split(",")]
    fx = fixtures(bot, seeds)
    expected = len(R.LIVE_MAPS_M2) * len(R.ZOO) * 2 * len(seeds)
    if len(fx) != expected:
        raise SystemExit(f"fixture count mismatch: {len(fx)} != {expected}")
    fp8 = R.runtime_fingerprint(f"bots/{bot}")[:8]
    root = Path(a.out) if a.out else Path("build/zoo") / f"m2-{bot}-{fp8}"
    (root / "replays").mkdir(parents=True, exist_ok=True)
    version = subprocess.run([a.unswbc, "--version"], capture_output=True, text=True).stdout.strip()
    todo = [f for f in fx if not (root / "replays" / (f["game"] + ".replay")).exists()]
    R.prebuild({f[k] for f in fx for k in ("botA", "botB")})
    print(f"{len(fx)} fixtures, {len(todo)} to run, {version}, maps={len(R.LIVE_MAPS_M2)}", flush=True)
    started = time.time()
    with open(root / "index.jsonl", "a") as idx, ThreadPoolExecutor(a.jobs) as pool:
        futures = [pool.submit(R.run, f, root, a.unswbc, version, a.no_logs) for f in todo]
        for n, future in enumerate(as_completed(futures), 1):
            try:
                row = future.result()
            except Exception as exc:
                print("ERR", exc, flush=True)
                continue
            if row:
                idx.write(json.dumps(row) + "\n")
                idx.flush()
                if n % 20 == 0 or row["rc"] != 0:
                    print(f"{n}/{len(todo)} {row['game']} rc={row['rc']}", flush=True)
    print(f"finished {len(todo)} fixtures in {time.time() - started:.0f}s -> {root}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
