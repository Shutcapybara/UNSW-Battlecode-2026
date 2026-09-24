#!/usr/bin/env python3
"""Autopsy: play one verbose match and report what actually happened.

Usage:
    python3 tools/autopsy.py botA botB [--map maps/default.map]
                                   [--rounds 40,120,240,400]
                                   [--raw LOGFILE]

Parses `unswbc run -v` output (ANSI-stripped) into:
  - outcome and round count
  - deaths by cause, per team
  - unit-count curve (from the runner's `dragons: X vs Y` progress lines)
  - split counts per team
  - per-dragon last indicator (role/length) at death

The point: turn "we lost" into "we starved after round 300" or "we died
12 times to head-to-head in the first 60 rounds".
"""
from __future__ import annotations

import argparse
import collections
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANSI = re.compile(r'\x1b\[[0-9;]*m')
ROUND_LINE = re.compile(r'^round (\d+): bot (\S+) \(team ([AB])\) died: (.+)$')
PROGRESS = re.compile(r'running round (\d+)/\d+.*dragons: (\d+) vs (\d+)')
OUTCOME = re.compile(r'^(team ([AB]) wins|draw) after (\d+) rounds', re.MULTILINE)


def resolve(bot: str) -> str:
    """Accept either a path or a bots/ folder name."""
    candidate = Path(bot)
    if not candidate.exists():
        candidate = ROOT / 'bots' / bot
    if not candidate.exists():
        sys.exit(f'bot not found: {bot}')
    return str(candidate)


def run_match(bot_a: str, bot_b: str, board: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            ['unswbc', 'run', board, '-v', '-o', tmp + '/replay.json',
             resolve(bot_a), resolve(bot_b)],
            capture_output=True, text=True, timeout=600, cwd=ROOT)
        return ANSI.sub('', proc.stdout + proc.stderr)


def autopsy(log: str, rounds: list[int]) -> dict:
    deaths = collections.defaultdict(collections.Counter)
    splits = collections.Counter()
    units: dict[int, tuple[int, int]] = {}
    outcome, final_round = None, 0
    for line in log.splitlines():
        m = ROUND_LINE.match(line)
        if m:
            r, _bot, team, cause = m.groups()
            final_round = max(final_round, int(r))
            deaths[team][cause] += 1
            continue
        m = PROGRESS.search(line)
        if m:
            units[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
        if line.startswith('SPLIT '):
            pass  # attributed below via stdout blocks
    # attribute splits to teams via stdout blocks
    team = None
    for line in log.splitlines():
        m = re.match(r'^round \d+: bot \S+ \(team ([AB])\) stdout:', line)
        if m:
            team = m.group(1)
        elif line.startswith('SPLIT ') and team:
            splits[team] += 1
    m = OUTCOME.search(log)
    if m:
        outcome = (m.group(1), int(m.group(3)))
        final_round = int(m.group(3))
    return dict(outcome=outcome, deaths=deaths, splits=splits,
                units=units, final_round=final_round)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('bot_a')
    ap.add_argument('bot_b')
    ap.add_argument('--map', default='maps/default.map')
    ap.add_argument('--rounds', default='60,150,300,450')
    ap.add_argument('--raw', help='reuse a saved -v log instead of playing')
    args = ap.parse_args()

    log = Path(args.raw).read_text() if args.raw else run_match(
        args.bot_a, args.bot_b, args.map)
    rep = autopsy(log, [int(x) for x in args.rounds.split(',')])

    board = args.map
    if rep['outcome']:
        print(f"{board}: {rep['outcome'][0]} after {rep['outcome'][1]} rounds")
    for team, name in (('A', args.bot_a), ('B', args.bot_b)):
        causes = rep['deaths'].get(team, collections.Counter())
        total = sum(causes.values())
        detail = ', '.join(f'{c}={n}' for c, n in causes.most_common())
        print(f"  team {team} ({name}): {total} deaths, {rep['splits'][team]} splits"
              f"{'; ' + detail if detail else ''}")
    marks = [int(x) for x in args.rounds.split(',')]
    print("  units (A vs B):", end='')
    for r in marks:
        near = min(rep['units'], key=lambda k: abs(k - r)) if rep['units'] else 0
        if rep['units'] and abs(near - r) <= 40:
            a, b = rep['units'][near]
            print(f"  r{near}:{a}v{b}", end='')
    print()
    if args.raw is None:
        print("  (rerun with --raw to re-analyse the same game)")


if __name__ == '__main__':
    sys.exit(main())
