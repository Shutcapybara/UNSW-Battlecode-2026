"""Run every ordered pair of standalone bots on every bundled map."""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, CancelledError
from datetime import datetime
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import tempfile
import threading
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.stats_store import StatsStore

ROOT = Path(__file__).resolve().parents[1]
ANSI = re.compile(r'\x1b\[[0-9;]*m')
OUTCOME = re.compile(r'^(?:team ([AB]) wins|draw) after (\d+) rounds\b', re.MULTILINE)
MAX_MATCHES_WITHOUT_CONFIRMATION = 10_000


def schedule(bots, maps, focus_bot=None):
    return [(board, a, b) for board in sorted(maps)
            for a, b in itertools.permutations(sorted(bots), 2)
            if focus_bot is None or focus_bot in (a, b)]


def parse_result(log, returncode):
    matches = list(OUTCOME.finditer(ANSI.sub('', log)))
    if returncode != 0 or not matches:
        return 'error', None
    match = matches[-1]
    return match[1] or 'draw', int(match[2])


def map_name(board):
    """Return a stable map ID relative to the shared maps directory."""
    return board.relative_to(ROOT / 'maps').with_suffix('').as_posix()


def atomic_write(path, text):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(text, encoding='utf-8')
    temporary.replace(path)


def save_results(out, results, bots):
    atomic_write(out / 'results.json', json.dumps(results, indent=2) + '\n')
    standings = {name: dict(bot=name, played=0, wins=0, draws=0, losses=0, errors=0, points=0)
                 for name in bots}
    for result in results:
        a, b = result['team_a'], result['team_b']
        if result['outcome'] == 'error':
            standings[a]['errors'] += 1
            standings[b]['errors'] += 1
            continue
        for name in (a, b):
            standings[name]['played'] += 1
        if result['outcome'] == 'draw':
            for name in (a, b):
                standings[name]['draws'] += 1
                standings[name]['points'] += 1
        else:
            winner, loser = (a, b) if result['outcome'] == 'A' else (b, a)
            standings[winner]['wins'] += 1
            standings[winner]['points'] += 3
            standings[loser]['losses'] += 1
    ranked = sorted(standings.values(), key=lambda row: (-row['points'], -row['wins'], row['bot']))
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(ranked[0]))
    writer.writeheader()
    writer.writerows(ranked)
    atomic_write(out / 'standings.csv', output.getvalue())
    return ranked


def fingerprint(paths):
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    return digest.hexdigest()


def manifest_for(bots, maps, replays, executable, sandbox=False):
    sources = []
    for bot in bots.values():
        sources.extend(path for path in bot.rglob('*') if path.is_file() and
                       not any(part.startswith('.') or part in ('__pycache__', 'build')
                               for part in path.relative_to(bot).parts))
    return dict(version=1, bots=sorted(bots), maps=sorted(maps), replays=replays,
                sandbox=sandbox,
                executable=executable, input_hash=fingerprint(sources + list(maps.values())),
                script_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


def stop_process(process):
    if os.name == 'posix':
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()
    process.wait()


class MatchWorkers:
    """Own subprocesses and isolated per-thread build directories."""
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.lock = threading.Lock()
        self.processes = set()
        self.cancelled = False

    def bot_path(self, source):
        target = self.workspace / str(threading.get_ident()) / source.name
        if not target.exists():
            shutil.copytree(source, target, ignore=shutil.ignore_patterns(
                '.unswbc-build', '__pycache__', '.git', 'build'))
        built = target / '.unswbc-build'
        # unswbc recompiles project folders every time. Reuse each worker's
        # finished build directly; no other worker can overwrite its binary.
        if (target / '.build-ready').exists() and any(
                (built / name).is_file() for name in ('bot', 'bot.exe', 'main.py')):
            return built
        return target

    def mark_built(self, source):
        (self.workspace / str(threading.get_ident()) / source.name / '.build-ready').touch()

    def start(self, command, log):
        with self.lock:
            if self.cancelled:
                raise CancelledError()
            process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=(os.name == 'posix'))
            self.processes.add(process)
            return process

    def finished(self, process):
        with self.lock:
            self.processes.discard(process)

    def cancel(self):
        with self.lock:
            self.cancelled = True
            for process in self.processes:
                stop_process(process)


def play(executable, board, a, b, out, label, timeout, replays, workers=None, sandbox=False, seed=None):
    log_path = out / f'{label}.log'
    replay_path = out / f'{label}.replay'
    run_a, run_b = (workers.bot_path(a), workers.bot_path(b)) if workers else (a, b)
    command = [executable, 'run']
    if sandbox:
        command += ['--sandbox', '-v']
    if seed is not None:
        command += ['--seed', str(seed)]
    command += [str(board), str(run_a), str(run_b)]
    command += ['-o', str(replay_path)] if replays else ['--no-replay']
    start = time.monotonic()
    error = None
    with log_path.open('w', encoding='utf-8') as log:
        process = workers.start(command, log) if workers else subprocess.Popen(
            command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=(os.name == 'posix'))
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            stop_process(process)
            returncode = -1
            error = f'timed out after {timeout:g} seconds'
            log.write('\n' + error + '\n')
        except KeyboardInterrupt:
            stop_process(process)
            raise
        finally:
            if workers:
                workers.finished(process)
    outcome, rounds = parse_result(log_path.read_text(encoding='utf-8', errors='replace'), returncode)
    if workers and outcome != 'error':
        workers.mark_built(a)
        workers.mark_built(b)
    if outcome == 'error' and error is None:
        error = f'runner exited with {returncode}' if returncode else 'no final match result in log'
    return dict(map=map_name(board), team_a=a.name, team_b=b.name, outcome=outcome,
                winner=a.name if outcome == 'A' else b.name if outcome == 'B' else None,
                rounds=rounds, seconds=round(time.monotonic()-start, 3), error=error,
                log=log_path.name, replay=replay_path.name if replays and replay_path.exists() else None)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bots', nargs='+', help='Bot folder names (default: all bots/*/bot.toml)')
    parser.add_argument('--focus-bot', help='Run only matches involving this bot, against every other selected bot')
    parser.add_argument('--maps', nargs='+',
                        help='Map paths relative to maps/, with or without .map (default: all maps/**/*.map)')
    parser.add_argument('--output', type=Path, help='Results directory (default: a new build/tournament-TIMESTAMP directory)')
    parser.add_argument('--resume', action='store_true', help='Skip completed matches in --output; retry errors')
    parser.add_argument('--jobs', '-j', type=int, default=min(4, os.cpu_count() or 1),
                        help='Concurrent matches (default: up to 4 CPU cores; use 1 for sequential)')
    parser.add_argument('--timeout', type=float, default=180, help='Maximum seconds per match (default: 180)')
    parser.add_argument('--no-replays', action='store_true', help='Save logs/results without replay files')
    parser.add_argument('--sandbox', action='store_true',
                        help='Run bots under judge CPU limits and retain verbose diagnostics')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print schedule size without running or writing anything')
    parser.add_argument('--show-schedule', action='store_true',
                        help='Print every scheduled match (large schedules also require --allow-large)')
    parser.add_argument('--allow-large', action='store_true',
                        help='Explicitly allow schedules larger than 10,000 matches')
    args = parser.parse_args(argv)
    if args.show_schedule and not args.dry_run:
        parser.error('--show-schedule requires --dry-run')
    if args.jobs < 1:
        parser.error('--jobs must be at least 1')
    if not 0 < args.timeout < float('inf'):
        parser.error('--timeout must be a finite positive number')
    if args.resume and not args.output:
        parser.error('--resume requires --output')
    bots = {p.parent.name: p.parent for p in (ROOT / 'bots').glob('*/bot.toml')}
    map_root = ROOT / 'maps'
    maps = {p.relative_to(map_root).with_suffix('').as_posix(): p
            for p in map_root.rglob('*.map')}
    for selected, available, kind in ((args.bots, bots, 'bot'), (args.maps, maps, 'map')):
        if selected:
            names = {name.removesuffix('.map') if kind == 'map' else name for name in selected}
            unknown = names - available.keys()
            if unknown:
                parser.error(f'unknown {kind}(s): {", ".join(sorted(unknown))}')
            for name in list(available):
                if name not in names:
                    del available[name]
    if len(bots) < 2 or not maps:
        parser.error('select at least two bots and one map')
    if args.focus_bot is not None and args.focus_bot not in bots:
        parser.error('--focus-bot must name an existing bot included in the --bots selection')
    match_count = (2 * (len(bots) - 1) * len(maps) if args.focus_bot is not None
                   else len(bots) * (len(bots) - 1) * len(maps))
    print(f'{len(bots)} bots, {len(maps)} maps, {match_count} matches '
          '(both sides, no self-matches).', flush=True)
    if match_count > MAX_MATCHES_WITHOUT_CONFIRMATION and not args.allow_large:
        if args.dry_run and not args.show_schedule:
            return 0
        parser.error(f'schedule exceeds {MAX_MATCHES_WITHOUT_CONFIRMATION:,} matches; '
                     'select fewer bots/maps or pass --allow-large explicitly')
    if args.dry_run and not args.show_schedule:
        return 0
    matches = schedule(bots, maps, args.focus_bot)
    if args.dry_run:
        for board, a, b in matches:
            print(f'{board}: A={a}, B={b}')
        return 0
    executable = shutil.which('unswbc')
    if executable is None:
        parser.error('unswbc was not found on PATH')
    out = (args.output or ROOT / 'build' / f'tournament-{datetime.now():%Y%m%d-%H%M%S-%f}').resolve()
    manifest = manifest_for(bots, maps, not args.no_replays, executable, args.sandbox)
    manifest['run_id'] = uuid.uuid4().hex
    manifest['focus_bot'] = args.focus_bot
    if args.resume:
        if not (out / 'manifest.json').is_file():
            parser.error('--output does not contain a tournament manifest')
        saved_manifest = json.loads((out / 'manifest.json').read_text())
        if saved_manifest.get('run_id'):
            manifest['run_id'] = saved_manifest['run_id']
        if saved_manifest != manifest:
            parser.error('bots, focus bot, maps, script or replay settings changed; start a new output directory')
        results = json.loads((out / 'results.json').read_text()) if (out / 'results.json').exists() else []
    else:
        if out.exists() and any(out.iterdir()):
            parser.error('--output is not empty; use --resume or a new directory')
        out.mkdir(parents=True, exist_ok=True)
        atomic_write(out / 'manifest.json', json.dumps(manifest, indent=2) + '\n')
        results = []
    print(f'Results: {out}', flush=True)
    local_stats = StatsStore(queue_only=True)
    local_run_id = local_stats.start_run(producer='tournament', manifest=manifest, run_id=manifest['run_id'])
    by_match = {(r['map'], r['team_a'], r['team_b']): r for r in results}
    save_results(out, results, bots)
    pending = iter((index, key) for index, key in enumerate(matches, 1)
                   if key not in by_match or by_match[key]['outcome'] == 'error')
    print(f'Running up to {args.jobs} matches concurrently.', flush=True)
    with tempfile.TemporaryDirectory(prefix='tournament-workers-') as workspace:
        workers = MatchWorkers(workspace)
        executor = ThreadPoolExecutor(max_workers=args.jobs)
        active = {}

        def submit_next():
            item = next(pending, None)
            if item is None:
                return
            index, key = item
            board, a, b = key
            label = f'{index:04d}-{board.replace("/", "_")}-{a}-vs-{b}'
            print(f'[{index}/{len(matches)}] Starting {board}: {a} vs {b}', flush=True)
            future = executor.submit(play, executable, maps[board], bots[a], bots[b], out,
                                     label, args.timeout, not args.no_replays, workers,
                                     sandbox=args.sandbox)
            active[future] = (index, key)

        try:
            for _ in range(min(args.jobs, len(matches))):
                submit_next()
            while active:
                finished, _ = wait(active, return_when=FIRST_COMPLETED)
                for future in finished:
                    index, key = active.pop(future)
                    result = future.result()
                    by_match[key] = result
                    results = [by_match[item] for item in matches if item in by_match]
                    # Only this coordinating thread writes shared result files.
                    save_results(out, results, bots)
                    local_stats.append_match(local_run_id, json.dumps([result['map'], result['team_a'], result['team_b']], separators=(',', ':')), result)
                    print(f"[{index}/{len(matches)}] Finished {key[0]}: {key[1]} vs {key[2]}: "
                          f"{result['winner'] or result['outcome']}", flush=True)
                    submit_next()
        except KeyboardInterrupt:
            workers.cancel()
            print(f'\nStopped. Completed results are saved; resume with --output {out} --resume and the same selections.')
            return 130
        finally:
            workers.cancel()
            executor.shutdown(wait=True, cancel_futures=True)
            local_stats.close()
    ranked = save_results(out, results, bots)
    print('\nStandings (win 3 points, draw 1):')
    for row in ranked:
        print(f"{row['bot']:<24} {row['points']:>4} pts  {row['wins']}W {row['draws']}D {row['losses']}L  {row['errors']} errors")
    errors = sum(r['outcome'] == 'error' for r in results)
    print(f'\n{len(results)} matches saved; {errors} errors. See standings.csv and results.json.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
