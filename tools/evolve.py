#!/usr/bin/env python3
"""Evolve: the fast iteration harness for bot work.

Wraps tools/benchmarking/tournament.py focus runs and aggregates results across an
opponent pool, tagging every run into build/evolve/INDEX.md so versions
are comparable across sessions.

Usage:
    python3 tools/evolve.py arena hydra-v07-eval            # vs default pool
    python3 tools/evolve.py arena hydra-v07-eval --vs kraken-v03-judge-safe
    python3 tools/evolve.py arena hydra-v07-eval --maps quick --runs 2
    python3 tools/evolve.py log                            # history
    python3 tools/evolve.py copy hydra-v06-echo hydra-v07-eval

Map sets:
    quick  arena default devil queen_of_spades big_empty   (5 diverse maps)
    full   every map discovered recursively by tools/benchmarking/tournament.py

Both sides of every matchup are always played (schedule permutations),
exactly as tournament.py --focus-bot does.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'build' / 'evolve' / 'INDEX.md'

POOL = ['hunter-v03-team-growth', 'fry-v14-stateful-size-aware-3',
        'kraken-v03-judge-safe', 'hydra-v06-echo']
MAP_SETS = {
    'quick': ['arena', 'default', 'devil', 'queen_of_spades', 'big_empty'],
    'full': None,  # every map
}


def sh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), capture_output=True, text=True,
                          cwd=ROOT, timeout=7200)


def arena(bot: str, pool: list[str], maps: list[str] | None, jobs: int,
          runs: int, tag: str) -> None:
    from datetime import datetime
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    rows = []
    for opponent in pool:
        for run in range(runs):
            out = ROOT / 'build' / 'evolve' / f'{stamp}-{bot}-vs-{opponent}-{run}'
            cmd = ['python3', 'tools/benchmarking/tournament.py', '--focus-bot', bot,
                   '--bots', bot, opponent, '--jobs', str(jobs),
                   '--no-replays', '--output', str(out)]
            if maps:
                cmd += ['--maps'] + maps
            proc = sh(*cmd)
            results = out / 'results.json'
            if not results.exists():
                print(f"  !! {opponent} run {run} failed: "
                      f"{proc.stdout[-400:]} {proc.stderr[-400:]}")
                rows.append((opponent, run, 0, 0, 0))
                continue
            w = d = l = 0
            for m in json.loads(results.read_text()):
                me = 'A' if m['team_a'] == bot else 'B'
                o = m['outcome']
                if o == 'draw':
                    d += 1
                elif o == me:
                    w += 1
                else:
                    l += 1
            rows.append((opponent, run, w, d, l))
            print(f"  vs {opponent:35s} run {run}: {w}W {d}D {l}L")
    agg = {}
    for opp, _run, w, d, l in rows:
        a = agg.setdefault(opp, [0, 0, 0])
        a[0] += w
        a[1] += d
        a[2] += l
    tw = sum(a[0] for a in agg.values())
    td = sum(a[1] for a in agg.values())
    tl = sum(a[2] for a in agg.values())
    label = tag or f'{bot} {"quick" if maps else "full"}'
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    new_file = not INDEX.exists()
    with INDEX.open('a') as fh:
        if new_file:
            fh.write("| when | bot | mapset | opponent | W | D | L |\n"
                     "|---|---|---|---|---|---|---|\n")
        for opp, (w, d, l) in agg.items():
            fh.write(f"| {stamp} | {label} | {'quick' if maps else 'full'} "
                     f"| {opp} | {w} | {d} | {l} |\n")
        fh.write(f"| {stamp} | {label} | {'quick' if maps else 'full'} "
                 f"| **TOTAL** | **{tw}** | **{td}** | **{tl}** |\n")
    print(f"TOTAL: {tw}W {td}D {tl}L  (indexed at {INDEX.relative_to(ROOT)})")


def show_log() -> None:
    if not INDEX.exists():
        print("no runs indexed yet")
        return
    print(INDEX.read_text())


def copy(src: str, dst: str) -> None:
    s, d = ROOT / 'bots' / src, ROOT / 'bots' / dst
    if d.exists():
        sys.exit(f"{d} already exists")
    if not s.exists():
        sys.exit(f"{s} not found")
    import shutil
    shutil.copytree(s, d)
    for junk in ('__pycache__',):
        junkdir = d / junk
        if junkdir.exists():
            shutil.rmtree(junkdir)
    print(f"copied {src} -> {dst}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)

    a = sub.add_parser('arena')
    a.add_argument('bot')
    a.add_argument('--vs', nargs='+', default=None)
    a.add_argument('--maps', default='quick',
                   help='quick | full | comma-separated map names')
    a.add_argument('--jobs', type=int, default=6)
    a.add_argument('--runs', type=int, default=1)
    a.add_argument('--tag', default=None)

    sub.add_parser('log')
    c = sub.add_parser('copy')
    c.add_argument('src')
    c.add_argument('dst')

    args = ap.parse_args()
    if args.cmd == 'log':
        show_log()
    elif args.cmd == 'copy':
        copy(args.src, args.dst)
    else:
        pool = args.vs or [p for p in POOL if p != args.bot]
        maps = MAP_SETS.get(args.maps)
        if maps is None and args.maps not in MAP_SETS:
            maps = args.maps.split(',')
        t0 = time.time()
        arena(args.bot, pool, maps, args.jobs, args.runs, args.tag)
        print(f"({time.time() - t0:.0f}s)")


if __name__ == '__main__':
    main()
