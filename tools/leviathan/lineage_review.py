"""Frozen four-lineage round robin; never builds in original bot directories."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

from lab import ROOT, source_hashes, tournament, attach_metrics
from replay import analyse

BOTS = ['leviathan-v07-local-cache', 'ouroboros-v05-spread',
        'kraken-v04-eval', 'hydra-v10-farmclean']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True)
    p.add_argument('--maps', default='arena,default_small,default,queen_of_spades,big_empty')
    p.add_argument('--sandbox', action='store_true')
    p.add_argument('--jobs', type=int, default=3)
    p.add_argument('--sources', help='Reuse an existing frozen sources directory')
    p.add_argument('--bots', nargs='+', default=BOTS)
    p.add_argument('--focus')
    args = p.parse_args()
    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=False)
    os.environ['PYTHONPYCACHEPREFIX'] = '/tmp/leviathan-review-pycache'
    boards = args.maps.split(',')
    sources = out / 'sources'
    sources.mkdir()
    origin = Path(args.sources) if args.sources else ROOT
    hashes = {}
    bots = {}
    for name in args.bots:
        src = origin / 'bots' / name
        before = source_hashes(src)
        target = sources / 'bots' / name
        shutil.copytree(src, target, ignore=shutil.ignore_patterns('.unswbc-build', '__pycache__', '.git'))
        if source_hashes(target) != before or source_hashes(src) != before:
            raise RuntimeError('Source changed while snapshotting: ' + name)
        hashes[name] = before
        bots[name] = target
    (sources / 'maps').mkdir()
    maps = {}
    for name in boards:
        target = sources / 'maps' / (name + '.map')
        shutil.copy2(origin / 'maps' / (name + '.map'), target)
        maps[name] = target
    for name in ['lineage_review.py', 'lab.py', 'replay.py']:
        shutil.copy2(Path(__file__).parent / name, sources / name)
    shutil.copy2(ROOT / 'tools/benchmarking/tournament.py', sources / 'tournament.py')
    manifest = dict(bots=args.bots, maps=boards, sandbox=args.sandbox, hashes=hashes,
                    runner=subprocess.run(['unswbc','--version'], capture_output=True,text=True).stdout.strip())
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    rows = []
    schedule = tournament.schedule(args.bots, boards, args.focus)
    with tempfile.TemporaryDirectory(prefix='lineage-review-') as tmp:
        workers = tournament.MatchWorkers(tmp)
        pool = ThreadPoolExecutor(max_workers=args.jobs)
        try:
            futures = {pool.submit(tournament.play, 'unswbc', maps[board], bots[a], bots[b], out,
                                  '%03d-%s-%s-vs-%s' % (i, board, a, b), 600, True, workers, args.sandbox): i
                       for i, (board,a,b) in enumerate(schedule)}
            for f in as_completed(futures):
                row = f.result()
                if row.get('replay'):
                    try:
                        detail = analyse(out / row['replay'])
                        assert detail['outcome'] == row['outcome'] and detail['rounds'] == row['rounds']
                        attach_metrics(detail, (out / row['log']).read_text())
                        row['analysis'] = detail
                        (out / Path(row['replay']).with_suffix('.analysis.json')).write_text(json.dumps(detail, indent=2))
                    except Exception as exc:
                        row['analysis_error'] = repr(exc)
                rows.append(row)
                tournament.save_results(out, rows, args.bots)
                print('%d/%d %s %s vs %s: %s' % (len(rows), len(schedule), row['map'],
                      row['team_a'], row['team_b'], row['winner'] or row['outcome']), flush=True)
        finally:
            workers.cancel()
            pool.shutdown(wait=True, cancel_futures=True)
    return int(any(r['outcome']=='error' or r.get('analysis_error') for r in rows))


if __name__ == '__main__':
    sys.exit(main())
