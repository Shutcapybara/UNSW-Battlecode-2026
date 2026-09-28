#!/usr/bin/env python3
"""Sandbox CPU-point breakdown for a cx/anna C++ bot.

    python3 tools/cx/meter.py bots/<bot> [--opp bots/<opp>] [--fixtures schooltime:A,portals:B]

Builds copies of the bot under build/cx/meter/ with ANNA_MEASURE = 1 (helper
parse only), 2 (parse + World::sense) and 3 (full turn + 10 extra whole-map
BFS), plays each fixture under --sandbox, and prints p50/p99/max points per
turn and the boot (first) turn for each, plus the derived costs:
  parse = m1, sense = m2 - m1, policy = full - m2, BFS = (m3 - full) / 10.
Every figure includes the judge's fixed write cost (2.5 M + 4 k/byte).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
from arena import run_game  # noqa: E402

PROBE = "schooltime:A,portals:B,slithery_fight:A,trauma:B"


def variant(bot: pathlib.Path, k: int) -> pathlib.Path:
    dst = REPO / "build" / "cx" / "meter" / f"{bot.name}-m{k}"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(bot, dst, ignore=shutil.ignore_patterns(".unswbc-build", "__pycache__"))
    main = dst / "main.cpp"
    main.write_text(f"#define ANNA_MEASURE {k}\n" + main.read_text())
    return dst


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bot")
    ap.add_argument("--opp", default=None, help="opponent (default: the full bot itself)")
    ap.add_argument("--fixtures", default=PROBE)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--json")
    args = ap.parse_args()
    bot = pathlib.Path(args.bot).resolve()
    opp = args.opp or str(bot)
    variants = {"full": bot, "m1_parse": variant(bot, 1), "m2_sense": variant(bot, 2),
                "m3_bfs10": variant(bot, 3)}
    out = {}
    for fx in args.fixtures.split(","):
        m, side = fx.split(":")
        mp = str(REPO / "maps" / f"{m}.map")
        row = {}
        for name, path in variants.items():
            a, b = (str(path), opp) if side == "A" else (opp, str(path))
            r = run_game(mp, a, b, args.seed, sandbox=True)
            st = r["stats"][side]
            row[name] = {"points": st.get("points"), "boot": st.get("boot"),
                         "errors": len([e for e in r["errors"] if e[2] == side])}
        out[fx] = row
        f = row["full"]["points"]
        p1, p2, p3 = (row[k]["points"] for k in ("m1_parse", "m2_sense", "m3_bfs10"))
        print(f"{fx:>18}  full p50 {f['p50']/1e6:.2f}M p99 {f['p99']/1e6:.2f}M max {f['max']/1e6:.2f}M"
              f"  boot max {row['full']['boot']['max']/1e6:.2f}M  errors {row['full']['errors']}")
        print(f"{'':>18}  parse p50 {p1['p50']/1e6:.2f}M  sense +{(p2['p50']-p1['p50'])/1e6:.2f}M"
              f"  policy +{(f['p50']-p2['p50'])/1e6:.2f}M  BFS {(p3['p50']-f['p50'])/10/1e6:.3f}M each"
              f"  (boot parse-only {row['m1_parse']['boot']['max']/1e6:.2f}M)")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
