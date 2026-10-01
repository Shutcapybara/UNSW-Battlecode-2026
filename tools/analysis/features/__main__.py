"""python -m tools.analysis.features extract <replay|dir|glob ...> --out DIR [--index index.jsonl] [--cache DIR] [--jobs N]

Writes DIR/{features,series,samples,dragons,deaths,checks}.parquet. Input contract: replay path only; the
optional index adds run context (seed, toolkit) by game id. Units: features = side-game, series = side-round,
samples = side-round every 5 rounds, dragons = dragon, deaths = death, checks = identity x side-game.
"""
import argparse, glob, json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


def _one(args):
    # kept for compatibility; the CLI uses the importable extract.extract_one
    from tools.analysis.features.extract import extract_one
    return extract_one(args)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='tools.analysis.features')
    sub = ap.add_subparsers(dest='cmd', required=True)
    x = sub.add_parser('extract')
    x.add_argument('replays', nargs='+')
    x.add_argument('--out', required=True)
    x.add_argument('--index')
    x.add_argument('--cache')
    x.add_argument('--jobs', type=int, default=os.cpu_count())
    rg = sub.add_parser('registry', help='print the feature registry as a Markdown table (templates collapsed)')
    a = ap.parse_args(argv)
    if a.cmd == 'registry':
        from tools.analysis.features.registry import _T
        fams = {}
        for t in _T:
            fams.setdefault(t['family'], []).append(t)
        for fam in sorted(fams):
            print(f'\n### {fam}\n\n| feature | unit | definition | source | validation | proximal target |\n|---|---|---|---|---|---|')
            for t in fams[fam]:
                print(f"| `{t['name']}` | {t['unit']} | {t['definition']} | {t['source']} | {t['validation']} | {t['target'] or ''} |")
        return
    import pandas as pd
    paths = []
    for p in a.replays:
        if os.path.isdir(p):
            paths += sorted(glob.glob(os.path.join(p, '*.replay')))
        else:
            paths += sorted(glob.glob(p)) or [p]
    index = {}
    if a.index:
        for line in open(a.index):
            r = json.loads(line)
            index[Path(r.get('replay', r['game'])).stem] = r
    jobs = []
    for p in paths:
        r = index.get(Path(p).stem, {})
        meta = {k: r[k] for k in ('seed', 'toolkit', 'sandbox') if k in r}
        meta['panel_winner'] = r.get('winner')
        jobs.append((p, a.cache, meta))
    t0 = time.time()
    acc = {k: [] for k in ('side_rows', 'series', 'samples', 'dragons', 'deaths', 'checks', 'exposure')}
    errors = []
    with ProcessPoolExecutor(a.jobs) as ex:
        from tools.analysis.features.extract import extract_one
        for n, out in enumerate(ex.map(extract_one, jobs, chunksize=4), 1):
            if 'error' in out:
                errors.append(out['error'])
                continue
            for k in acc:
                acc[k].extend(out[k])
            if n % 50 == 0:
                print(f'{n}/{len(jobs)} {time.time() - t0:.0f}s', file=sys.stderr, flush=True)
    os.makedirs(a.out, exist_ok=True)
    names = dict(side_rows='features')
    for k, rows in acc.items():
        df = pd.DataFrame(rows)
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].map(lambda v: None if v is None else v if isinstance(v, str) else str(v))
        df.to_parquet(os.path.join(a.out, names.get(k, k) + '.parquet'), index=False)
    print(json.dumps(dict(replays=len(jobs), ok=len(jobs) - len(errors), errors=errors[:10], seconds=round(time.time() - t0))))


if __name__ == '__main__':
    main()
