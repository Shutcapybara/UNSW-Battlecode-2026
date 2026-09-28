#!/usr/bin/env python3
"""Isolated, reproducible Leviathan experiments. No writes to other lineages."""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from replay import analyse
spec = importlib.util.spec_from_file_location('tournament', ROOT / 'tools/benchmarking/tournament.py')
tournament = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tournament)
MAPS = dict(quick=['arena', 'default_small', 'default', 'queen_of_spades'],
            holdout=['big_empty', 'small', 'schooltime', 'queen_of_spades_but_she_ages'],
            full=sorted(p.stem for p in (ROOT / 'maps').glob('*.map')))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(path):
    return {str(p.relative_to(path)): digest(p) for p in path.rglob('*')
            if p.is_file() and not any(s in ('.git', '.unswbc-build', '__pycache__')
                                      for s in p.relative_to(path).parts)}


def apply_overrides(folder, overrides):
    """Change a private snapshot only. C++ exposes numeric constexpr auto keys."""
    if (folder / 'main.cpp').exists() and (folder / 'params.h').exists():
        path = folder / 'params.h'
        text = path.read_text()
        for key, value in overrides.items():
            if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', key):
                raise ValueError('Invalid C++ parameter: ' + key)
            if not isinstance(value, (int, float, bool)) or str(value) in ('inf', '-inf', 'nan'):
                raise ValueError('C++ parameters must be finite numeric values or booleans')
            literal = str(value).lower() if isinstance(value, bool) else repr(value)
            text, count = re.subn(r'(constexpr auto ' + re.escape(key) + r'\s*=\s*)[^;]+;',
                                  lambda m: m[1] + literal + ';', text)
            if count != 1:
                raise ValueError('Unknown or duplicate C++ parameter: ' + key)
        path.write_text(text)
    else:
        target = folder / 'params.py'
        previous = target.read_text() if target.exists() else 'PARAMS = {}\n'
        target.write_text(previous + '\nPARAMS.update(' + repr(overrides) + ')\n')


def attach_metrics(detail, log):
    # This runner leaves replay instruction pointers null even with --sandbox.
    # Its final team summaries are the available metering evidence. Values
    # rounded to 0.1M remain labelled estimates; absent data remains None.
    for side, stats in detail['teams'].items():
        stats['max_points_estimate'] = None
        match = re.search(r'team ' + side + r' points per turn:.*?max ([0-9.]+)([MK]?)', log)
        if match:
            scale = {'M': 1_000_000, 'K': 1000, '': 1}[match[2]]
            stats['max_points_estimate'] = round(float(match[1]) * scale)
        for metric in ('p50', 'p99'):
            match = re.search(r'team ' + side + r' points per turn:.*?\b' + metric + r' ([0-9.]+)([MK]?)', log)
            stats[metric + '_points_estimate'] = (round(float(match[1]) *
                {'M': 1_000_000, 'K': 1000, '': 1}[match[2]]) if match else None)


def map_class(path):
    words = next(line.split() for line in path.read_text().splitlines()
                 if line.startswith('MAP '))
    return 'compact' if int(words[1]) * int(words[2]) <= 625 else 'open'


def ledger_row(row, focus, base, cycle, board):
    side = 'A' if row['team_a'] == focus else 'B'
    opponent = row['team_b'] if side == 'A' else row['team_a']
    detail = row.get('analysis', {})
    us = detail.get('teams', {}).get(side, {})
    them = detail.get('teams', {}).get('B' if side == 'A' else 'A', {})
    error = row['outcome'] == 'error' or row.get('analysis_error')
    return dict(bot=focus, base=base, opponent=opponent, map=row['map'],
                map_class=map_class(board), side=side,
                result='E' if error else 'D' if row['outcome'] == 'draw' else
                       'W' if row['winner'] == focus else 'L',
                win_type=detail.get('reason'), round=row['rounds'],
                our_longest=us.get('final', {}).get('longest'),
                their_longest=them.get('final', {}).get('longest'),
                cpu_p50=us.get('p50_points_estimate'), cpu_p99=us.get('p99_points_estimate'),
                cpu_max=us.get('max_points_estimate'), cycle=cycle,
                timeouts=us.get('timeouts'), replay=row.get('replay'))


def save(out, rows, focus):
    rows.sort(key=lambda r: (r['map'], r['team_a'], r['team_b']))
    tournament.atomic_write(out / 'results.json', json.dumps(rows, indent=2) + '\n')
    grouped = defaultdict(Counter)
    for row in rows:
        opponent = row['team_b'] if row['team_a'] == focus else row['team_a']
        key = ('E' if row['outcome'] == 'error' else 'D' if row['outcome'] == 'draw'
               else 'W' if row['winner'] == focus else 'L')
        grouped[opponent][key] += 1
        grouped['TOTAL'][key] += 1
    lines = ['# ' + focus, '', '| Opponent | W | D | L | Errors |', '|---|---:|---:|---:|---:|']
    for opp, counts in grouped.items():
        lines.append('| %s | %d | %d | %d | %d |' % (opp, *(counts[k] for k in 'WDLE')))
    lines += ['', 'Both side assignments; deterministic maps, not independent random samples.', '',
              '| Map | Side | Opponent | Result | Rounds | Longest (us / them) | Splits | Deaths |',
              '|---|---|---|---|---:|---|---:|---|']
    for row in rows:
        side = 'A' if row['team_a'] == focus else 'B'
        opp = row['team_b'] if side == 'A' else row['team_a']
        detail = row.get('analysis', {}).get('teams', {})
        us, them = detail.get(side, {}), detail.get('B' if side == 'A' else 'A', {})
        lines.append('| %s | %s | %s | %s | %s | %s / %s | %s | %s |' % (
            row['map'], side, opp, row['outcome'], row['rounds'],
            us.get('final', {}).get('longest', '?'), them.get('final', {}).get('longest', '?'),
            us.get('splits', '?'), json.dumps(us.get('deaths', {}))))
    lines += ['', '## Health', '', '| Map | Side | Peak CPU points (rounded) | Invalid actions | Replay analysis error |',
              '|---|---|---:|---:|---|']
    for row in rows:
        side = 'A' if row['team_a'] == focus else 'B'
        us = row.get('analysis', {}).get('teams', {}).get(side, {})
        lines.append('| %s | %s | %s | %s | %s |' % (row['map'], side,
            us.get('max_points_estimate') or 'not recorded', us.get('deaths', {}).get('invalid', 0),
            row.get('analysis_error', '')))
    tournament.atomic_write(out / 'report.md', '\n'.join(lines) + '\n')


def run(args):
    names = [args.bot] + args.vs
    if len(names) != len(set(names)):
        raise ValueError('Duplicate opponent / self match')
    boards = MAPS.get(args.maps, args.maps.split(','))
    # All sources, including reference opponents, are copied before execution.
    out = ROOT / (args.output or ('build/leviathan/' + datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + args.bot))
    out.mkdir(parents=True, exist_ok=False)
    sources = out / 'sources'
    sources.mkdir()
    hashes = {}
    snapshots = {}
    for name in names:
        source = ROOT / 'bots' / name
        if not (source / 'bot.toml').is_file():
            raise ValueError('Unknown bot: ' + name)
        target = sources / name
        before = source_hashes(source)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('.unswbc-build', '__pycache__', '.git'))
        snapshots[name] = target
        hashes[name] = source_hashes(target)
        if before != hashes[name] or before != source_hashes(source):
            raise RuntimeError('Bot changed while snapshotting; retry in a fresh output folder: ' + name)
    overrides = {}
    for item in args.set:
        key, value = item.split('=', 1)
        overrides[key] = ast.literal_eval(value)
    if overrides:
        apply_overrides(snapshots[args.bot], overrides)
        hashes[args.bot] = source_hashes(snapshots[args.bot])
    map_paths = {}
    for board in boards:
        target = sources / (board + '.map')
        shutil.copy2(Path(args.map_dir) / (board + '.map'), target)
        hashes[board + '.map'] = digest(target)
        map_paths[board] = target
    shutil.copy2(ROOT / 'tools/benchmarking/tournament.py', sources / 'tournament.py')
    for file in Path(__file__).parent.glob('*.py'):
        shutil.copy2(file, sources / ('lab-' + file.name))
    manifest = dict(focus=args.bot, opponents=args.vs, maps=boards, sandbox=args.sandbox,
                    hashes=hashes, harness={p.name: digest(p) for p in sources.glob('*.py')},
                    executable=shutil.which('unswbc'), python=sys.version, hypothesis=args.hypothesis,
                    base=args.base, cycle=args.cycle, overrides=overrides,
                    runner_version=subprocess.run(['unswbc', '--version'], capture_output=True,
                                                  text=True, timeout=10).stdout.strip())
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    rows = []
    # Keep Python's compiler cache inside a writable location, including children.
    os.environ['PYTHONPYCACHEPREFIX'] = str(out / 'pycache')
    with tempfile.TemporaryDirectory(prefix='leviathan-workers-') as workspace:
        workers = tournament.MatchWorkers(workspace)
        pool = ThreadPoolExecutor(max_workers=args.jobs)
        futures = {}
        try:
            for idx, (board, a, b) in enumerate(tournament.schedule(names, boards, args.bot)):
                label = '%03d-%s-%s-vs-%s' % (idx, board, a, b)
                future = pool.submit(tournament.play, 'unswbc', map_paths[board], snapshots[a], snapshots[b],
                                     out, label, args.timeout, True, workers, args.sandbox)
                futures[future] = label
            for future in as_completed(futures):
                row = future.result()
                if row['replay']:
                    try:
                        detail = analyse(out / row['replay'])
                        if detail['outcome'] != row['outcome'] or detail['rounds'] != row['rounds']:
                            raise ValueError('Replay result disagrees with runner')
                        log = (out / row['log']).read_text()
                        attach_metrics(detail, log)
                        for side in 'AB':
                            logged = len(re.findall(r'\(team ' + side + r'\) died:', log))
                            if sum(detail['teams'][side]['deaths'].values()) != logged:
                                raise ValueError('Replay deaths disagree with runner log')
                        row['analysis'] = detail
                        (out / (futures[future] + '.analysis.json')).write_text(json.dumps(detail, indent=2))
                    except Exception as exc:
                        row['analysis_error'] = str(exc)
                rows.append(row)
                save(out, rows, args.bot)
                tournament.atomic_write(out / 'ledger.jsonl', ''.join(json.dumps(
                    ledger_row(r, args.bot, args.base, args.cycle, map_paths[r['map']])) + '\n'
                    for r in rows))
                print('%d/%d %s: %s' % (len(rows), len(futures), futures[future], row['winner'] or row['outcome']), flush=True)
        finally:
            workers.cancel()
            pool.shutdown(wait=True, cancel_futures=True)
    print(out / 'report.md')
    unhealthy = any(r['outcome'] == 'error' or r.get('analysis_error') or any(
        t['timeouts'] for t in r.get('analysis', {}).get('teams', {}).values()) for r in rows)
    return int(unhealthy)


def compare(args):
    """Paired descriptive comparison; refuses mismatched budget modes/maps."""
    runs = [ROOT / args.baseline, ROOT / args.candidate]
    manifests = [json.loads((p / 'manifest.json').read_text()) for p in runs]
    if manifests[0]['sandbox'] != manifests[1]['sandbox']:
        raise ValueError('Cannot compare native and sandbox runs')
    for name in set(manifests[0]['maps']) & set(manifests[1]['maps']):
        if manifests[0]['hashes'][name + '.map'] != manifests[1]['hashes'][name + '.map']:
            raise ValueError('Map changed: ' + name)
    indexes = []
    for folder, manifest in zip(runs, manifests):
        focus = manifest['focus']
        index = {}
        for row in json.loads((folder / 'results.json').read_text()):
            if row['outcome'] == 'error' or row.get('analysis_error'):
                raise ValueError('Resolve failed matches before comparing')
            if any(t['timeouts'] for t in row.get('analysis', {}).get('teams', {}).values()):
                raise ValueError('Resolve judge timeouts before comparing')
            side = 'A' if row['team_a'] == focus else 'B'
            opponent = row['team_b'] if side == 'A' else row['team_a']
            index[(opponent, row['map'], side)] = .5 if row['outcome'] == 'draw' else float(row['winner'] == focus)
        indexes.append(index)
    common = sorted(set(indexes[0]) & set(indexes[1]))
    if not common:
        raise ValueError('No common opponent/map/side cases')
    for opponent in {key[0] for key in common}:
        if manifests[0]['hashes'][opponent] != manifests[1]['hashes'][opponent]:
            raise ValueError('Opponent source changed: ' + opponent)
    deltas = [indexes[1][key] - indexes[0][key] for key in common]
    print(json.dumps(dict(cases=len(common), baseline_score=sum(indexes[0][k] for k in common),
                          candidate_score=sum(indexes[1][k] for k in common),
                          improved=sum(d > 0 for d in deltas), regressed=sum(d < 0 for d in deltas),
                          tied=sum(d == 0 for d in deltas),
                          note='Descriptive paired results, not independent random trials.'), indent=2))


def clone(args):
    if not args.destination.startswith('leviathan-'):
        raise ValueError('Destination must be a new Leviathan version')
    destination = ROOT / 'bots' / args.destination
    shutil.copytree(ROOT / 'bots' / args.source, destination,
                    ignore=shutil.ignore_patterns('.unswbc-build', '__pycache__', '.git'))
    if args.set:
        import ast
        path = destination / 'weights.py'
        namespace = {}
        exec(path.read_text(), namespace)
        params = namespace['PARAMS']
        for change in args.set:
            key, value = change.split('=', 1)
            if key not in params:
                raise ValueError('Unknown weight: ' + key)
            params[key] = ast.literal_eval(value)
        path.write_text('"""' + args.hypothesis + '"""\nPARAMS = ' + repr(params) + '\n')
    (destination / 'EXPERIMENT.md').write_text('# ' + args.destination + '\n\nParent: ' + args.source + '\n\nHypothesis: ' + args.hypothesis + '\n')
    print(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('run')
    p.add_argument('bot')
    p.add_argument('--vs', nargs='+', default=['fry-v03-portal-hunters', 'kraken-v03-judge-safe', 'hydra-v06-echo'])
    p.add_argument('--maps', default='quick', help='quick, holdout, full, or comma separated names')
    p.add_argument('--jobs', type=int, default=2)
    p.add_argument('--timeout', type=float, default=1200)
    p.add_argument('--map-dir', default=str(ROOT / 'maps'))
    p.add_argument('--base', default=None)
    p.add_argument('--cycle', default='1')
    p.add_argument('--set', action='append', default=[], help='Snapshot-only params.py override: key=value')
    p.add_argument('--sandbox', action='store_true')
    p.add_argument('--output')
    p.add_argument('--hypothesis', default='Baseline measurement')
    p = sub.add_parser('clone')
    p.add_argument('source')
    p.add_argument('destination')
    p.add_argument('--set', nargs='*')
    p.add_argument('--hypothesis', required=True)
    p = sub.add_parser('compare')
    p.add_argument('baseline')
    p.add_argument('candidate')
    args = parser.parse_args()
    if args.command == 'run':
        if args.jobs < 1 or args.timeout <= 0:
            parser.error('jobs and timeout must be positive')
        return run(args)
    if args.command == 'compare':
        compare(args)
    else:
        clone(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
