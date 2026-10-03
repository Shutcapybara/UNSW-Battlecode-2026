#!/usr/bin/env python3
"""Run a small, fixed-seed serial comparison for Sparta family changes."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
RESULT = re.compile(r'^(?:team ([AB]) wins|draw) after (\d+) rounds(?: \(([^)]*)\))?', re.MULTILINE)


def sha256(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    return digest.hexdigest()


def source_files(bot: Path) -> list[Path]:
    return [p for p in bot.rglob('*') if p.is_file() and not any(
        part.startswith('.') or part in ('__pycache__', 'build')
        for part in p.relative_to(bot).parts)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, help='bot directory name')
    parser.add_argument('--opponents', nargs='+', required=True, help='bot directory names')
    parser.add_argument('--maps', nargs='+', required=True, help='map paths relative to maps/, with or without .map')
    parser.add_argument('--seeds', default='1,2,3')
    parser.add_argument('--output', type=Path, required=True, help='empty output directory under build/')
    parser.add_argument('--timeout', type=float, default=900)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    candidate = ROOT / 'bots' / args.candidate
    opponents = [ROOT / 'bots' / name for name in args.opponents]
    maps = [(ROOT / 'maps' / (name.removesuffix('.map') + '.map')) for name in args.maps]
    if not (candidate / 'bot.toml').is_file():
        parser.error(f'unknown candidate: {args.candidate}')
    for name, bot in zip(args.opponents, opponents):
        if not (bot / 'bot.toml').is_file():
            parser.error(f'unknown opponent: {name}')
    if any(not p.is_file() for p in maps):
        parser.error('one or more maps do not exist')
    seeds = [int(s) for s in args.seeds.split(',')]
    if not seeds or any(s < 0 for s in seeds):
        parser.error('--seeds must be comma-separated nonnegative integers')
    executable = os.environ.get('UNSWBC') or shutil.which('unswbc')
    if executable is None:
        fallback = ROOT / '.venv' / 'bin' / 'unswbc'
        if fallback.is_file():
            executable = str(fallback)
    if executable is None:
        parser.error('unswbc was not found on PATH, in UNSWBC, or in .venv/bin')
    count = len(seeds) * len(maps) * len(opponents) * 2
    print(f'{count} serial matches ({len(seeds)} seeds x {len(maps)} maps x '
          f'{len(opponents)} opponents x both seats).')
    if args.dry_run:
        return 0

    output = (ROOT / args.output).resolve() if not args.output.is_absolute() else args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error(f'output directory is not empty: {output}')
    output.mkdir(parents=True, exist_ok=True)
    source = source_files(candidate) + [p for bot in opponents for p in source_files(bot)] + maps
    manifest = dict(candidate=args.candidate, opponents=args.opponents,
                    maps=[p.relative_to(ROOT / 'maps').with_suffix('').as_posix() for p in maps],
                    seeds=seeds, timeout=args.timeout, executable=str(Path(executable).resolve()),
                    input_hash=sha256(source), runner_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    started=datetime.now().astimezone().isoformat(timespec='seconds'))
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    rows = []
    for seed in seeds:
        for map_name, board in zip(manifest['maps'], maps):
            for opponent_name, opponent in zip(args.opponents, opponents):
                for side in ('A', 'B'):
                    team_a, team_b = ((candidate, opponent) if side == 'A' else (opponent, candidate))
                    label = f's{seed}__{map_name.replace("/", "+")}__{args.candidate}__vs__{opponent_name}__{side}'
                    replay = output / f'{label}.replay'
                    log = output / f'{label}.log'
                    command = [executable, 'run', '--seed', str(seed), '--no-logs', '--no-indicator',
                               '--no-draw', str(board), str(team_a), str(team_b), '-o', str(replay)]
                    start = time.monotonic()
                    try:
                        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                              timeout=args.timeout)
                        text = proc.stdout + proc.stderr
                        rc = proc.returncode
                    except subprocess.TimeoutExpired as error:
                        text = (error.stdout or b'').decode(errors='replace') if isinstance(error.stdout, bytes) else (error.stdout or '')
                        text += f'\ntimeout after {args.timeout:g} seconds'
                        rc = -1
                    log.write_text(text, encoding='utf-8')
                    matches = list(RESULT.finditer(text))
                    winner = None
                    rounds = None
                    reason = None
                    outcome = 'error'
                    if rc == 0 and matches:
                        match = matches[-1]
                        rounds = int(match.group(2))
                        reason = match.group(3)
                        if match.group(1) is None:
                            winner, outcome = 'draw', 'draw'
                        else:
                            winner = team_a.name if match.group(1) == 'A' else team_b.name
                            outcome = 'win' if winner == args.candidate else 'loss'
                    row = dict(seed=seed, map=map_name, opponent=opponent_name, candidate_side=side,
                               outcome=outcome, winner=winner, rounds=rounds, reason=reason, rc=rc,
                               seconds=round(time.monotonic() - start, 2), replay=replay.name, log=log.name)
                    rows.append(row)
                    (output / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')
                    print(f"[{len(rows)}] s{seed} {map_name} vs {opponent_name} side={side}: "
                          f"{outcome} rounds={rounds} rc={rc}", flush=True)

    summary = defaultdict(lambda: dict(wins=0, draws=0, losses=0, errors=0, games=0))
    for row in rows:
        record = summary[row['opponent']]
        record['games'] += 1
        record['wins' if row['outcome'] == 'win' else
               'draws' if row['outcome'] == 'draw' else
               'errors' if row['outcome'] == 'error' else 'losses'] += 1
    (output / 'summary.json').write_text(json.dumps(dict(summary), indent=2) + '\n')
    for opponent, record in sorted(summary.items()):
        print(f"{args.candidate} vs {opponent}: {record['wins']}W-"
              f"{record['draws']}D-{record['losses']}L, {record['errors']} errors")
    return 1 if any(row['outcome'] == 'error' for row in rows) else 0


if __name__ == '__main__':
    raise SystemExit(main())
