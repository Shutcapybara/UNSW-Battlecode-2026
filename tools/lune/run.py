#!/usr/bin/env python3
"""Lune panel runner: one candidate vs a fixed opponent set, map x seat x seed, resumable,
budgeted (stops launching games before --budget seconds so a time-limited shell never
loses a half-played game), shardable across hosts. Rows are tools/cx/bench.py rows, so
tools/cx/benchmarks_table.py and tools/lune/score.py read them unchanged.

    python3 tools/lune/run.py bots/CAND --panel z1 --seeds 1 --out game_stats/runs/r1-CAND-z1-s1.jsonl \
        [--opps zoo|a,b] [--jobs 4] [--budget 150] [--shard k/n] [--sandbox] [--maps a,b] [--sides AB]

Panels: z1 = 10 live maps (BENCHMARKS z1 panel), gen = maps/new/* + maps/var/*_tr (generalisation, OOS rule),
probe = the dense CPU fixtures. Opponents default to tools.analysis.features.run_panel.ZOO (eight bots).
"""
from __future__ import annotations

import argparse, json, os, pathlib, sys, time
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "cx"))

ZOO = ['fenrir-v18-arrival-ready-beds', 'yuna-v05-core', 'chaewon-y04-probe', 'sinbad-v07-divecap',
       'gavroche-v32-supported-divecap', 'ouroboros-m01-vibing-mimic', 'kazuha-s01-swarm-dissolve',
       'hunter-v20-portal-scouts']  # == run_panel.ZOO (29 Sep)
LIVE = ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma',
        'autarky', 'devil', 'trauma']
GEN = sorted("new/" + p.stem for p in (REPO / "maps" / "new").glob("*.map")) + \
      sorted("var/" + p.stem for p in (REPO / "maps" / "var").glob("*_tr.map"))


def _one(job):
    """tools/cx/bench.py _one, on the lune arena copy (adds the r50/r150/r250 economy checkpoints)."""
    sys.path.insert(0, str(REPO / "tools" / "lune"))
    from arena_lune import run_game
    cand, opp, m, side, seed, sandbox = (job[k] for k in ("cand", "opp", "map", "side", "seed", "sandbox"))
    a, b = (cand, opp) if side == "A" else (opp, cand)
    r = run_game(str(REPO / "maps" / f"{m}.map"), a, b, seed, sandbox)
    r.pop("transcripts", None)
    us, them = ("A", "B") if side == "A" else ("B", "A")
    return {"map": m, "side": side, "seed": seed, "cand": cand, "opp": pathlib.Path(opp).name, "sandbox": sandbox,
            "result": "win" if r["winner"] == us else "loss" if r["winner"] == them else "draw",
            "rounds": r["rounds"], "us": r["stats"][us], "them": r["stats"][them],
            "errors": [e for e in r["errors"] if e[2] == us][:10], "secs": r["secs"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--panel", default="z1", choices=["z1", "gen", "custom"])
    ap.add_argument("--maps", default=None, help="comma list (overrides --panel)")
    ap.add_argument("--opps", default="zoo")
    ap.add_argument("--seeds", default="1")
    ap.add_argument("--sides", default="AB")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--budget", type=float, default=0, help="stop launching after this many seconds (0 = none)")
    ap.add_argument("--est", type=float, default=30, help="initial per-game seconds estimate for the budget")
    ap.add_argument("--shard", default=None, help="k/n")
    ap.add_argument("--reverse", action="store_true")
    ap.add_argument("--sandbox", action="store_true")
    ap.add_argument("--skip", nargs="*", default=[], help="other jsonl files whose fixtures count as done")
    a = ap.parse_args()
    t0 = time.time()
    maps = a.maps.split(",") if a.maps else (LIVE if a.panel == "z1" else GEN)
    opps = [f"bots/{o}" for o in ZOO] if a.opps == "zoo" else [o if "/" in o else f"bots/{o}" for o in a.opps.split(",")]
    seeds = [int(s) for s in a.seeds.split(",")]
    jobs = [(m, sd, s, o) for s in seeds for m in maps for o in opps for sd in a.sides]
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    for f in [out, *map(pathlib.Path, a.skip)]:
        if f.exists():
            for line in f.read_text().splitlines():
                if line.strip():
                    d = json.loads(line); done.add((d["map"], d["side"], d["seed"], d["opp"]))
    todo = [j for j in jobs if (j[0], j[1], j[2], pathlib.Path(j[3]).name) not in done]
    if a.shard:
        k, n = map(int, a.shard.split("/")); todo = [j for i, j in enumerate(todo) if i % n == k]
    if a.reverse:
        todo = todo[::-1]
    print(f"{len(jobs)} fixtures, {len(todo)} to run", flush=True)
    if not todo:
        return 0
    from unswbc.run import _resolve
    for b in {a.cand, *opps}:
        _resolve(b, a.sandbox)
    est, ran = a.est, 0
    with ProcessPoolExecutor(max_workers=a.jobs, max_tasks_per_child=1) as ex, out.open("a") as fh:
        running = {}
        it = iter(todo)
        def fill():
            while len(running) < a.jobs:
                if a.budget and time.time() - t0 + est * 1.15 > a.budget:
                    return
                j = next(it, None)
                if j is None:
                    return
                m, sd, s, o = j
                running[ex.submit(_one, {"cand": a.cand, "opp": o, "map": m, "side": sd, "seed": s,
                                         "sandbox": a.sandbox})] = j
        fill()
        while running:
            fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
            for f in fin:
                j = running.pop(f)
                try:
                    d = f.result()
                except Exception as e:
                    print("FAILED", j, repr(e)[:300], flush=True); continue
                est = max(est * 0.7, d["secs"]) if ran == 0 else max(0.8 * est + 0.2 * d["secs"], d["secs"] * 0.9)
                ran += 1
                fh.write(json.dumps(d) + "\n"); fh.flush()
            fill()
    print(f"ran {ran} in {time.time() - t0:.0f}s; {len(todo) - ran} left", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
