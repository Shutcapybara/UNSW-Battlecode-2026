#!/usr/bin/env python3
"""Descriptive, exactly paired opening tempo and portal exposure audit.
No gate verdicts. Validates campaign evidence and keeps raw numerators and
exposures instead of averaging per-game death percentages.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import campaign as c
import report
from tools.s1 import tempo_gate as tempo
from tools.s1.build import process


def analysis_id():
    paths = sorted((c.ROOT / 'tools/s1').glob('*.py')) + [Path(__file__)]
    return hashlib.sha256((report.analysis_id() + ''.join(c.sha(p) for p in paths)).encode()).hexdigest()


def extract(row, dest, aid):
    cache = c.STORE / 'phase-analysis' / aid
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (row['replay_sha256'] + '.json')
    if not path.exists():
        replay = dest / row['replay']
        result = process((str(replay), replay.stem, {'source': 'expedition'}))
        if 'error' in result:
            raise ValueError(result['error'])
        data = dict(sides=result['sides'], series=[s for s in result['series']
                    if s['round'] <= 150 and s['round'] % 5 == 0])
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(data) + '\n')
        tmp.replace(path)
    data = json.loads(path.read_text())
    side = next(s for s in data['sides'] if s['side'] == row['side'])
    if side['team'] != Path(row['cand']).name or side['opp'] != row['opp'] or side['result'] != row['result']:
        raise ValueError(f'Phase attribution mismatch: {path}')
    series = {s['round']: s for s in data['series'] if s['side'] == row['side']}
    if set(series) != set(range(0, 151, 5)):
        raise ValueError(f'Missing opening checkpoints: {path}')
    get = lambda r, k: float(series[r].get(k) or 0)
    return dict(map=side['map'], won=side['won'],
        income=[get(r, 'c_eats_bed') + get(r, 'c_eats_enemy_corpse') for r in range(0, 151, 5)],
        loss=[get(r, 'c_length_lost') - get(r, 'c_eats_ally_corpse') for r in range(0, 151, 5)],
        totals={k: get(150, k) for k in ('c_transits', 'c_transit_died3', 'c_death_h2h_ally',
                'c_own_goals', 'c_dragon_turns', 'c_splits', 'c_deaths_newborn', 'total')})


def summarize(rows):
    totals = {k: sum(r['totals'][k] for r in rows) for k in rows[0]['totals']}
    def ratio(n, d, scale=1):
        return scale * totals[n] / totals[d] if totals[d] else None
    return dict(games=len(rows), won=sum(r['won'] for r in rows), totals=totals,
        transit_died3=ratio('c_transit_died3', 'c_transits'),
        ally_headon_per1k_turns=ratio('c_death_h2h_ally', 'c_dragon_turns', 1000),
        own_goals_per1k_turns=ratio('c_own_goals', 'c_dragon_turns', 1000),
        newborn_death_per_split=ratio('c_deaths_newborn', 'c_splits'),
        total150_mean=totals['total'] / len(rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', choices=c.CANDIDATES, default=c.QUEUE[0])
    ap.add_argument('--panel', choices=('z1', 'gen'), default='z1')
    ap.add_argument('--map', help='Optional exact fixture map key, e.g. autarky')
    args = ap.parse_args()
    aid = analysis_id()
    canonical_aid = report.analysis_id()
    rows = {}
    for bot in (c.panel.PARENT, args.candidate):
        dest = c.run_dir(bot, args.panel)
        if json.loads((dest / 'contract.json').read_text()) != c.contract(bot, args.panel):
            raise ValueError(f'Frozen inputs changed: {dest}')
        rows[bot] = c.read_rows(bot, args.panel)
    keys = sorted(rows[c.panel.PARENT].keys() & rows[args.candidate].keys())
    if args.map:
        keys = [k for k in keys if k[0] == args.map]
    refs = json.loads(tempo.REF.read_text())['maps']
    output = dict(candidate=args.candidate, panel=args.panel, paired=len(keys), analysis_sha256=aid,
                  reference_sha256=c.sha(tempo.REF), status='DESCRIPTIVE ONLY; NO GATE VERDICT', maps={})
    for m in sorted({k[0] for k in keys}):
        matched = [k for k in keys if k[0] == m]
        data = {}
        for bot in rows:
            dest = c.run_dir(bot, args.panel)
            data[bot] = []
            for k in matched:
                report.canonical(rows[bot][k], dest, canonical_aid)
                data[bot].append(extract(rows[bot][k], dest, aid))
        parent, child = data[c.panel.PARENT], data[args.candidate]
        mapname = parent[0]['map']
        if mapname in refs:
            ref, kind = refs[mapname], 'frozen top10'
        else:
            ref = {k: np.median([r[k] for r in parent], axis=0).tolist() for k in ('income', 'loss')}
            kind = 'matched parent median; provisional until full coverage'
        deltas = [tempo.tempo(a, ref) - tempo.tempo(b, ref) for a, b in zip(child, parent)]
        output['maps'][m] = dict(paired=len(matched), seeds=sorted({k[2] for k in matched}),
            seats=sorted({k[1] for k in matched}), reference=kind,
            tempo_delta_rounds=float(np.mean(deltas)), parent=summarize(parent), candidate=summarize(child))
    output['limitations'] = ('Ordered partial panels cannot establish strength. All guard rates here use summed '
        'numerators/exposures through r150 on exactly paired games. Transit death within three rounds is '
        'associated with transit, not proof the portal caused death. Ally head-on counts are all locations; '
        'this is not ally head-on per transit. No independent-seed uncertainty claim or promotion.')
    suffix = (args.map or 'all').replace('/', '+')
    path = c.STORE / f'{args.candidate}-{args.panel}-{suffix}-phase.json'
    path.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
