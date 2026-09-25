#!/usr/bin/env python3
"""Frozen, resumable all-version tournament. One SQLite row per map/side game."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'bahamut-scaffold': 'Unimplemented strategy scaffold.',
            'kraken-prof': 'Profiling wrapper around kraken-v02-bigmap; not a distinct competitor.'}
RESULT = re.compile(r'^(?:team ([AB]) wins|draw) after (\d+) rounds \(([^)]+)\)', re.M)
FAULT = re.compile(r'^round (\d+): bot (\d+) \(team ([AB])\) (?!died:)(.*(?:exited|timed out|ran out of time|timeout|broken pipe|failed).*)$', re.M)
LIVE, LOCK = set(), threading.Lock()


def save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def hashes(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file() and not any(
                x.startswith('.') or x in ('__pycache__', 'build') for x in p.relative_to(folder).parts)}


def invoke(command, log, timeout):
    log.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with log.open('w') as handle:
        process = subprocess.Popen(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        with LOCK:
            LIVE.add(process)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = -9
            handle.write('\nHARNESS TIMEOUT\n')
        finally:
            with LOCK:
                LIVE.discard(process)
    return code, time.monotonic() - start


def game(out, manifest, board, a, b, label, timeout):
    log = out / 'logs' / label[:3] / (label + '.log')
    command = [manifest['runner'], 'run', str(out / 'sources/maps' / (board + '.map')),
               str(out / 'sources/bots' / a / '.unswbc-build'),
               str(out / 'sources/bots' / b / '.unswbc-build'), '--no-replay', '--no-debug']
    code, seconds = invoke(command, log, timeout)
    content = log.read_text(errors='replace')
    match = RESULT.search(content)
    faults = [dict(round=int(r), id=int(i), side=s, message=m) for r, i, s, m in FAULT.findall(content)]
    outcome = (match[1] or 'draw') if code == 0 and match else 'error'
    return dict(map=board, team_a=a, team_b=b, outcome=outcome,
                winner=a if outcome == 'A' else b if outcome == 'B' else None,
                rounds=int(match[2]) if match else None, reason=match[3] if match else None,
                seconds=round(seconds, 3), returncode=code, runtime_faults=faults,
                log=str(log.relative_to(out)), error=None if outcome != 'error' else content[-2000:])


def prepare(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    bots = sorted(p.parent.name for p in (ROOT / 'bots').glob('*/bot.toml') if p.parent.name not in EXCLUDED)
    manifest = dict(created=datetime.now(timezone.utc).isoformat(), mode='native',
                    runner=shutil.which('unswbc'), python=shutil.which('python3'),
                    exclusions=dict(EXCLUDED), bots=bots, maps=[], hashes={},
                    seed=250925, replays=False, toolkit_python=args.toolkit_python)
    for name in bots:
        source, target = ROOT / 'bots' / name, out / 'sources/bots' / name
        before = hashes(source)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('.unswbc-build', '__pycache__', '.git', 'build'))
        if before != hashes(target) or before != hashes(source):
            raise RuntimeError('Source changed during snapshot: ' + name)
        manifest['hashes'][name] = before
    (out / 'sources/maps').mkdir(parents=True)
    for source in sorted((ROOT / 'maps').glob('*.map')):
        target = out / 'sources/maps' / source.name
        shutil.copy2(source, target)
        manifest['maps'].append(source.stem)
        manifest['hashes'][source.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest['runner_version'] = subprocess.check_output([manifest['runner'], '--version'], text=True).strip()
    engine = subprocess.check_output([args.toolkit_python, '-c',
        'from unswbc.engine import WASM_PATH; print(WASM_PATH)'], text=True).strip()
    manifest['engine_sha256'] = hashlib.sha256(Path(engine).read_bytes()).hexdigest()
    shutil.copy2(__file__, out / 'tournament.py')
    save(out / 'manifest.json', manifest)
    print('Frozen', len(bots), 'bots and', len(manifest['maps']), 'maps.', flush=True)

    def compile_bot(name):
        source = out / 'sources/bots' / name
        code, seconds = invoke([args.toolkit_python, '-c',
            'from unswbc.project import Project; import sys; print(Project.from_dir(sys.argv[1]).compile())',
            str(source)], out / 'preflight' / (name + '.build.log'), 240)
        return dict(bot=name, returncode=code, seconds=seconds)

    builds = []
    with ThreadPoolExecutor(max_workers=min(args.jobs, 8)) as pool:
        for future in as_completed([pool.submit(compile_bot, n) for n in bots]):
            row = future.result(); builds.append(row)
            print('Build', len(builds), '/', len(bots), row['bot'], row['returncode'], flush=True)
    save(out / 'builds.json', builds)
    failed = {r['bot']: 'Compilation failed; see preflight build log.' for r in builds if r['returncode']}
    preflight = []
    eligible = [n for n in bots if n not in failed]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(game, out, manifest, 'arena', n, n, 'preflight-' + n, args.timeout): n for n in eligible}
        for future in as_completed(futures):
            row = future.result(); preflight.append(row)
            name = futures[future]
            if row['outcome'] == 'error' or any(f['round'] == 0 for f in row['runtime_faults']):
                failed[name] = 'Failed arena startup preflight; see preflight.json and its log.'
            print('Preflight', len(preflight), '/', len(eligible), name, row['outcome'], len(row['runtime_faults']), flush=True)
            save(out / 'preflight.json', preflight)
    manifest['exclusions'].update(failed)
    manifest['bots'] = [n for n in bots if n not in failed]
    manifest['games'] = len(manifest['bots']) * (len(manifest['bots']) - 1) * len(manifest['maps'])
    manifest['prepared'] = True
    save(out / 'manifest.json', manifest)
    print('Prepared', len(manifest['bots']), 'entrants;', manifest['games'], 'games.', flush=True)


def run(args):
    out = args.output.resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    if not manifest.get('prepared'):
        raise RuntimeError('Preparation has not completed.')
    current_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if manifest.get('run_script_sha256', current_hash) != current_hash:
        raise RuntimeError('Run harness changed; review before resuming.')
    manifest['run_script_sha256'] = current_hash
    save(out / 'manifest.json', manifest)
    shutil.copy2(__file__, out / 'tournament.py')
    for name in manifest['bots']:
        if hashes(out / 'sources/bots' / name) != manifest['hashes'][name]:
            raise RuntimeError('Frozen source changed: ' + name)
    db = sqlite3.connect(out / 'games.sqlite3')
    db.execute('CREATE TABLE IF NOT EXISTS games (map TEXT, a TEXT, b TEXT, outcome TEXT, data TEXT, PRIMARY KEY(map,a,b))')
    done = {(m, a, b) for m, a, b, result in db.execute('SELECT map,a,b,outcome FROM games') if result != 'error'}
    fixtures = list(itertools.product(manifest['maps'], itertools.permutations(manifest['bots'], 2)))
    random.Random(manifest['seed']).shuffle(fixtures)
    schedule = [(i, board, a, b) for i, (board, (a, b)) in enumerate(fixtures) if (board, a, b) not in done]
    pending = iter(schedule)
    active, recent = {}, []
    start = time.monotonic(); completed = len(done); errors = 0

    def status():
        elapsed = time.monotonic() - start
        newly = completed - len(done)
        rate = newly / elapsed * 60 if elapsed else 0
        save(out / 'status.json', dict(total=manifest['games'], complete=completed, remaining=manifest['games']-completed,
            errors_this_run=errors, workers=args.jobs, games_per_minute=round(rate, 2),
            elapsed_seconds=round(elapsed), eta_hours=round((manifest['games']-completed)/rate/60, 2) if rate else None,
            updated=datetime.now(timezone.utc).isoformat(), running=bool(active), recent=recent[-5:]))

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        def submit():
            item = next(pending, None)
            if item:
                i, board, a, b = item
                active[pool.submit(game, out, manifest, board, a, b, '%06d' % i, args.timeout)] = item
        for _ in range(args.jobs): submit()
        status()
        try:
            with (out / 'games.jsonl').open('a') as ledger:
                while active:
                    finished, _ = wait(active, timeout=30, return_when=FIRST_COMPLETED)
                    for future in finished:
                        item = active.pop(future)
                        try:
                            row = future.result()
                        except Exception as exc:
                            row = dict(map=item[1], team_a=item[2], team_b=item[3], outcome='error', error=repr(exc))
                        data = json.dumps(row, separators=(',', ':'))
                        db.execute('INSERT OR REPLACE INTO games VALUES (?,?,?,?,?)',
                                   (row['map'], row['team_a'], row['team_b'], row['outcome'], data))
                        db.commit(); ledger.write(data + '\n'); ledger.flush()
                        completed += row['outcome'] != 'error'; errors += row['outcome'] == 'error'
                        recent.append({k: row.get(k) for k in ('map', 'team_a', 'team_b', 'outcome', 'seconds')})
                        if len(recent) > 10: recent.pop(0)
                        submit()
                        if (completed + errors) % 100 == 0:
                            print(completed, '/', manifest['games'], 'completed;', errors, 'errors', flush=True)
                    status()
        finally:
            with LOCK:
                for process in list(LIVE):
                    try: os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
    db.close()
    status()
    print('Run finished:', completed, '/', manifest['games'], 'errors:', errors, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('prepare', 'run'))
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=12)
    p.add_argument('--timeout', type=float, default=900)
    p.add_argument('--toolkit-python', default='/Users/alik/.local/share/uv/tools/unswbc/bin/python3')
    a = p.parse_args()
    if a.jobs < 1: p.error('--jobs must be positive')
    os.environ['PYTHONPYCACHEPREFIX'] = str(a.output.resolve().parent / 'all-bot-tournament-pycache')
    (prepare if a.command == 'prepare' else run)(a)
