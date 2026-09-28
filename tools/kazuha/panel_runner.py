#!/usr/bin/env python3
"""kazuha panel runner: both-sides seeded fixtures for a candidate and control.

Replicates compare_bot's fixture list (opponents x maps x sides from a
comparison TOML) and runs each fixture under several deterministic seed
variants (v1 == compare_bot's fixture_hash_v1), for two bots, reusing
bots/tournament.play so semantics match the shared harness exactly.

Usage (from the worktree root, PATH prefixed with the unswbc 1.2.2 venv):
  python3 tools/kazuha/panel_runner.py --candidate bots/kazuha-s01-swarm-dissolve \
      --control bots/ouroboros-v10-beacon --config comparison-kazuha.toml \
      --out build/kz-panel --seeds 3 --jobs 4 [--only-seed 1]
Writes OUT/results.jsonl (one row per game) and OUT/replays/*.replay.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from bots.tournament import MatchWorkers, play  # noqa: E402


def fixture_seed(opponent, board, variant):
    material = "gavroche-comparison-seed-v1\0%s\0%s\0kazuha-v%d" % (opponent, board, variant)
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


def read_config(path):
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    cfg = tomllib.loads(Path(path).read_text())
    return cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--only-seed", type=int, default=None)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()

    executable = shutil.which("unswbc")
    if not executable:
        sys.exit("unswbc not on PATH")
    version = os.popen("%s --version" % executable).read().strip().splitlines()[0]

    cfg = read_config(args.config)
    root = Path(args.config).parent
    opponents = {Path(p).name: (root / p) for p in cfg["bots"]}
    maps = {Path(p).stem: (root / p) for p in cfg["maps"]}
    sides = cfg.get("run", {}).get("sides", ["A", "B"])

    out = Path(args.out).resolve()
    (out / "replays").mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(exist_ok=True)
    workers = MatchWorkers()

    jobs = []
    variants = [args.only_seed] if args.only_seed else range(1, args.seeds + 1)
    bots = {"cand": Path(args.candidate).resolve(), "ctl": Path(args.control).resolve()}
    for v in variants:
        for oname, opath in opponents.items():
            for mname, mpath in maps.items():
                for side in sides:
                    for tag, bdir in bots.items():
                        if oname == bdir.name:
                            continue
                        jobs.append((tag, bdir, oname, opath, mname, mpath, side, v))
    # resume support
    done = set()
    res_path = out / "results.jsonl"
    if res_path.exists():
        for line in res_path.read_text().splitlines():
            r = json.loads(line)
            if r.get("outcome") not in (None, "error"):
                done.add((r["tag"], r["opponent"], r["map"], r["side"], r["variant"]))
        jobs = [j for j in jobs if (j[0], j[2], j[4], j[6], j[7]) not in done]
    meta = dict(candidate=str(bots["cand"]), control=str(bots["ctl"]),
                config=str(args.config), runner=version,
                fixtures=len(opponents) * len(maps) * len(sides))
    (out / "meta.json").write_text(json.dumps(meta, indent=1))

    def run_one(job):
        tag, bdir, oname, opath, mname, mpath, side, v = job
        seed = fixture_seed(oname, mname, v)
        label = "%s__v%d__%s__vs__%s__%s" % (tag, v, mname, oname, side)
        a = bdir if side == "A" else opath
        b = opath if side == "A" else bdir
        row = play(executable, str(mpath), a, b, out / "logs", label,
                   args.timeout, True, workers, sandbox=False, seed=seed)
        row.update(tag=tag, bot=bdir.name, opponent=oname, map=mname, side=side,
                   variant=v, seed=str(seed))
        return row

    print("%d games -> %s" % (len(jobs), out), flush=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_one, j): j for j in jobs}
        n = 0
        for f in as_completed(futs):
            row = f.result()
            n += 1
            with open(res_path, "a") as fh:
                fh.write(json.dumps(row) + "\n")
            print("[%d/%d] %s v%d %s vs %s (%s) -> %s" % (
                n, len(jobs), row["tag"], row["variant"], row["map"], row["opponent"],
                row["side"], row.get("outcome")), flush=True)


if __name__ == "__main__":
    main()
