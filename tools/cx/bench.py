#!/usr/bin/env python3
"""cx bench: seeded fixtures (map x side x seed) for one candidate against an
opponent, in parallel, one JSON line per game (resumable), plus a summary.

    python3 tools/cx/bench.py CANDIDATE OPPONENT --out build/cx/NAME.jsonl \
        [--maps live|compact|probe|a,b] [--seeds 1,2,3] [--sides AB] [--jobs 2] [--sandbox]
    python3 tools/cx/bench.py --summary build/cx/NAME.jsonl [--vs other.jsonl]

"Side A" means the candidate plays team A. The early-game columns are the C1
outcomes: units r25/r50/r100, total length r100/r250, first pearl, pearls eaten
by r100, deaths by cause per 1k dragon-turns. --vs pairs two runs on
(map, side, seed) and reports better/same/worse on total length r100 with a
two-sided sign test.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

LIVE = ["portals", "schooltime", "default", "autarky", "trauma", "dilemma", "slithery_fight",
        "queen_of_spades", "trophy", "devil"]
COMPACT = ["portals", "dilemma", "devil", "trophy"]
PROBE = [("schooltime", "A"), ("portals", "B"), ("slithery_fight", "A"), ("trauma", "B")]


def _one(job: dict) -> dict:
    from arena import run_game
    cand, opp, m, side, seed, sandbox = (job[k] for k in ("cand", "opp", "map", "side", "seed", "sandbox"))
    a, b = (cand, opp) if side == "A" else (opp, cand)
    r = run_game(str(REPO / "maps" / f"{m}.map"), a, b, seed, sandbox)
    r.pop("transcripts", None)
    us, them = ("A", "B") if side == "A" else ("B", "A")
    return {"map": m, "side": side, "seed": seed, "cand": cand, "opp": opp, "sandbox": sandbox,
            "result": "win" if r["winner"] == us else "loss" if r["winner"] == them else "draw",
            "rounds": r["rounds"], "us": r["stats"][us], "them": r["stats"][them],
            "errors": [e for e in r["errors"] if e[2] == us][:10], "secs": r["secs"]}


def run(args) -> None:
    maps = {"live": LIVE, "compact": COMPACT}.get(args.maps, None)
    jobs = []
    seeds = [int(s) for s in args.seeds.split(",")]
    if args.maps == "probe":
        for m, side in PROBE:
            for s in seeds:
                jobs.append((m, side, s))
    else:
        maps = maps or args.maps.split(",")
        for m in maps:
            for side in args.sides:
                for s in seeds:
                    jobs.append((m, side, s))
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            d = json.loads(line)
            done.add((d["map"], d["side"], d["seed"]))
    todo = [j for j in jobs if j not in done]
    print(f"{len(jobs)} fixtures, {len(todo)} to run", flush=True)
    with ProcessPoolExecutor(max_workers=args.jobs) as ex, out.open("a") as fh:
        futs = {ex.submit(_one, {"cand": args.cand, "opp": args.opp, "map": m, "side": sd,
                                 "seed": s, "sandbox": args.sandbox}): (m, sd, s)
                for m, sd, s in todo}
        for f in as_completed(futs):
            try:
                d = f.result()
            except Exception as e:  # keep going; report
                print("FAILED", futs[f], e, flush=True)
                continue
            fh.write(json.dumps(d) + "\n")
            fh.flush()
            u = d["us"]
            print(f'{d["map"]:>16} {d["side"]} s{d["seed"]} {d["result"]:>4} '
                  f'u25/50/100 {u["units_r25"]}/{u["units_r50"]}/{u["units_r100"]} '
                  f'len100 {u["len_r100"]} eat100 {u["eaten_r100"]} deaths {u["deaths"]} '
                  f'({d["secs"]}s)', flush=True)


def load(path: str) -> list[dict]:
    return [json.loads(l) for l in pathlib.Path(path).read_text().splitlines() if l.strip()]


def sign_p(better: int, worse: int) -> float:
    n = better + worse
    if n == 0:
        return 1.0
    k = min(better, worse)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def summary(path: str, vs: str | None = None, key: str = "len_r100") -> None:
    rows = load(path)
    cols = ["units_r25", "units_r50", "units_r100", "len_r100", "len_r250", "eaten_r100", "first_pearl"]
    print(f"{path}: {len(rows)} games, W/D/L "
          f"{sum(r['result'] == 'win' for r in rows)}/{sum(r['result'] == 'draw' for r in rows)}/"
          f"{sum(r['result'] == 'loss' for r in rows)}")
    print(f"{'map':>16} {'sd':>2} " + " ".join(f"{c:>10}" for c in cols) + "   opp len_r100  deaths")
    for r in sorted(rows, key=lambda r: (r["map"], r["side"], r["seed"])):
        u = r["us"]
        print(f'{r["map"]:>16} {r["side"]}{r["seed"]} ' + " ".join(f"{str(u.get(c)):>10}" for c in cols)
              + f'   {r["them"]["len_r100"]:>8}  {u["deaths"]}')
    n = len(rows)
    if n:
        med = {}
        for c in cols:
            vals = sorted(r["us"][c] if r["us"][c] is not None else 999 for r in rows)
            med[c] = vals[n // 2]
        print("median " + " ".join(f"{c}={v}" for c, v in med.items()))
        turns = sum(r["us"]["turns"] for r in rows)
        causes = {}
        for r in rows:
            for k, v in r["us"]["deaths"].items():
                causes[k] = causes.get(k, 0) + v
        print("deaths per 1k dragon-turns: " + ", ".join(
            f"{k} {1000 * v / max(1, turns):.2f}" for k, v in sorted(causes.items())) + f"  (turns {turns})")
        errs = sum(len(r["errors"]) for r in rows)
        print(f"bot errors (timeouts/crashes): {errs}")
        pts = [r["us"]["points"] for r in rows if "points" in r["us"]]
        if pts:
            print("sandbox points: p50 max-of-games {:.1f}M  p99 max {:.1f}M  max {:.1f}M".format(
                max(p["p50"] for p in pts) / 1e6, max(p["p99"] for p in pts) / 1e6,
                max(p["max"] for p in pts) / 1e6))
    if vs:
        other = {(r["map"], r["side"], r["seed"]): r for r in load(vs)}
        b = s = w = 0
        for r in rows:
            o = other.get((r["map"], r["side"], r["seed"]))
            if not o:
                continue
            x, y = r["us"][key], o["us"][key]
            if x > y:
                b += 1
            elif x < y:
                w += 1
            else:
                s += 1
        print(f"pairs on {key} vs {vs}: better {b} same {s} worse {w}  sign-test p={sign_p(b, w):.3f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cand", nargs="?")
    ap.add_argument("opp", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--maps", default="live")
    ap.add_argument("--seeds", default="1")
    ap.add_argument("--sides", default="AB")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2)))
    ap.add_argument("--sandbox", action="store_true")
    ap.add_argument("--summary")
    ap.add_argument("--vs")
    ap.add_argument("--key", default="len_r100")
    args = ap.parse_args()
    if args.summary:
        summary(args.summary, args.vs, args.key)
        return 0
    run(args)
    summary(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
