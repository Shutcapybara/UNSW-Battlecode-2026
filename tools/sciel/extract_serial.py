#!/usr/bin/env python3
"""Serial (single-process) feature extraction for the sciel lane.

The stock `python -m tools.analysis.features extract` uses a ProcessPoolExecutor;
on this 24 GB host with swap full the spawned workers get SIGKILLed by the OS
(BrokenProcessPool). This runs the same per-replay function in ONE process with
a small thread pool (the decode is mostly GIL-bound; threads only halve the
wall time but never die) and writes the same parquet layout, so lane.py's
`features*/features.parquet` glob picks the output up unchanged.

    ~/.venvs/bc122/bin/python tools/sciel/extract_serial.py BOT --panel pool|gen [--jobs 3]
"""
from __future__ import annotations

import argparse, glob, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/sciel'))

RUNS = ROOT / 'build/sciel/runs'


def extracted(root):
    import pandas as pd
    got = set()
    for f in glob.glob(str(root / 'features*/features.parquet')):
        got |= set(pd.read_parquet(f, columns=['game'])['game'])
    return got


def _one(job):
    path, meta = job
    from tools.analysis.features.frame import load
    from tools.analysis.features.extract import extract
    from tools.analysis.features.checks import v0_checks
    try:
        g = load(path, None)
        out = extract(g, meta)
        out['checks'] = v0_checks(g, out)
        return out
    except Exception as e:
        return dict(error=f'{path}: {type(e).__name__}: {e}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--panel', default='both')
    ap.add_argument('--jobs', type=int, default=3)
    a = ap.parse_args()
    import pandas as pd
    for panel in (['pool', 'gen'] if a.panel == 'both' else [a.panel]):
        root = RUNS / a.bot / panel
        have = extracted(root)
        reps = [p for p in sorted(glob.glob(str(root / 'replays/*.replay')))
                if Path(p).stem not in have]
        if not reps:
            print(f'[{panel}] nothing new to extract')
            continue
        index = {}
        for f in glob.glob(str(root / 'index-*.jsonl')):
            if f.endswith('.tmp.jsonl'):
                continue
            for line in open(f):
                r = json.loads(line)
                index[Path(r.get('replay', r['game'])).stem] = r
        jobs = []
        for p in reps:
            r = index.get(Path(p).stem, {})
            meta = {k: r[k] for k in ('seed', 'toolkit', 'sandbox') if k in r}
            meta['panel_winner'] = r.get('winner')
            jobs.append((p, meta))
        t0 = time.time()
        acc = {k: [] for k in ('side_rows', 'series', 'samples', 'dragons', 'deaths', 'checks', 'exposure')}
        errors = []
        with ThreadPoolExecutor(a.jobs) as ex:
            for n, out in enumerate(ex.map(_one, jobs), 1):
                if 'error' in out:
                    errors.append(out['error'])
                    continue
                for k in acc:
                    acc[k].extend(out[k])
                if n % 40 == 0:
                    print(f'[{panel}] {n}/{len(jobs)} {time.time() - t0:.0f}s', flush=True)
        outdir = root / f'features-serial-{int(time.time())}'
        outdir.mkdir(parents=True, exist_ok=True)
        names = dict(side_rows='features')
        for k, rows in acc.items():
            df = pd.DataFrame(rows)
            for c in df.columns:
                if df[c].dtype == object:
                    df[c] = df[c].map(lambda v: None if v is None else v if isinstance(v, str) else str(v))
            df.to_parquet(outdir / (names.get(k, k) + '.parquet'), index=False)
        print(f'[{panel}] extracted {len(jobs)} -> {outdir.name} '
              f'({len(errors)} errors) {time.time() - t0:.0f}s', flush=True)
        if errors:
            print(json.dumps(errors[:5]), flush=True)


if __name__ == '__main__':
    main()
