"""Win-score gates and carried queen/material diagnostics from seeded finals screens."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features.frame import decode


def cluster_interval(rows, key, seed=61006):
    clusters = defaultdict(list)
    for row in rows:
        clusters[row['map']].append(row[key])
    if not clusters:
        return None
    rng = random.Random(seed)
    keys = list(clusters)
    values = []
    for _ in range(5000):
        sample = [v for _ in keys for v in clusters[rng.choice(keys)]]
        values.append(sum(sample) / len(sample))
    values.sort()
    point = sum(sum(v) for v in clusters.values()) / sum(len(v) for v in clusters.values())
    return dict(point=point, interval90=[values[250], values[4749]], maps=len(keys), fixtures=len(rows))


def read_run(path):
    manifest = json.loads((path / 'manifest.json').read_text())
    candidate = manifest['candidate']
    results = json.loads((path / 'results.json').read_text())
    valid, faults = [], []
    for result in results:
        r = dict(result)
        if r['outcome'] == 'error':
            faults.append(dict(fixture=r['fixture'], error=r['error']))
            continue
        try:
            frame = decode(path / r['replay'])
            if frame['winner'] != r['outcome']:
                raise ValueError('Replay winner differs from runner')
            tles = sum(e['tle'] for e in frame['events']['actions'])
            invalid = sum(e['cause'] == 'invalid' for e in frame['events']['deaths'])
            if tles or invalid:
                raise ValueError(f'Unresolved runtime faults: {tles} TLEs, {invalid} invalid deaths')
            r['score'] = .5 if r['outcome'] == 'draw' else float(r['winner'] == candidate)
            team = r['candidate_seat']
            queen = min(i for i, (t, b) in frame['rounds'][0].items() if t == team)
            r['diagnostics'] = {}
            for rnd in (100, 300):
                reached = rnd <= frame['last_round']
                state = frame['rounds'][rnd] if reached else frame['rounds'][-1]
                r['diagnostics'][str(rnd)] = dict(reached=reached,
                    total=sum(len(b) for t, b in state.values() if t == team),
                    queen_alive=queen in state, queen_length=len(state[queen][1]) if queen in state else 0)
            r['queen_death'] = next((e for e in frame['events']['deaths'] if e['id'] == queen), None)
            valid.append(r)
        except Exception as e:
            faults.append(dict(fixture=r['fixture'], error=str(e)))
    return manifest, valid, faults


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--reference-run', type=Path, help='Matching retained-baseline fixtures against the same keepers')
    ap.add_argument('--baseline', default='bokuto-18-queenfeed')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    manifest, results, faults = read_run(args.run)
    summary = dict(candidate=manifest['candidate'], faults=faults, opponents={},
                   scope='Development screen unless a separate untouched confirmation split is explicitly pinned')
    for opponent in manifest['opponents']:
        rr = [r for r in results if r['opponent'] == opponent]
        stats = dict(wins=sum(r['score'] == 1 for r in rr), draws=sum(r['score'] == .5 for r in rr),
                     losses=sum(r['score'] == 0 for r in rr), score=cluster_interval(rr, 'score'))
        for rnd in ('100', '300'):
            stats['r' + rnd] = {key: sum(r['diagnostics'][rnd][key] for r in rr) / len(rr)
                               for key in ('total', 'queen_alive')} if rr else {}
            stats['r' + rnd]['reached'] = sum(r['diagnostics'][rnd]['reached'] for r in rr)
        stats['queen_death_causes'] = dict(Counter(r['queen_death']['cause'] for r in rr if r['queen_death']))
        if opponent == args.baseline and rr:
            direct = [dict(r, advantage=r['score'] - .5) for r in rr]
            stats['advantage'] = cluster_interval(direct, 'advantage')
            stats['positive_screen'] = not faults and stats['advantage']['interval90'][0] > 0
        summary['opponents'][opponent] = stats
    if args.reference_run:
        ref_manifest, reference, ref_faults = read_run(args.reference_run)
        if ref_manifest['candidate'] != args.baseline:
            ap.error('Reference run must use the retained baseline as candidate')
        def maps(m):
            return {Path(row['path']).stem: row['sha256'] for row in m['maps']}
        if maps(manifest) != maps(ref_manifest) or manifest['seeds'] != ref_manifest['seeds']:
            ap.error('Matched comparison requires identical map bytes and seeds')
        lookup = {(r['map'], r['opponent'], r['candidate_seat'], r['seed']): r for r in reference}
        paired = []
        missing = []
        for r in results:
            if r['opponent'] == args.baseline:
                continue
            key = (r['map'], r['opponent'], r['candidate_seat'], r['seed'])
            if key not in lookup:
                missing.append(key)
            else:
                paired.append(dict(r, delta=r['score'] - lookup[key]['score']))
        summary['matched_keeper_delta'] = cluster_interval(paired, 'delta')
        summary['reference_faults'] = ref_faults
        summary['missing_pairs'] = missing
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'diagnostics.json').write_text(json.dumps(results, indent=2) + '\n')
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return int(bool(faults or summary.get('reference_faults') or summary.get('missing_pairs')))


if __name__ == '__main__':
    raise SystemExit(main())
