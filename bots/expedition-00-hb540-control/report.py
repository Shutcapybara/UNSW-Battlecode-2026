#!/usr/bin/env python3
"""Audit saved Expedition replays and paired coverage; never run games or promote.
Writes an analysis cache keyed by replay and analysis source hashes, leaving the
original arena rows intact. Partial panels produce descriptive evidence only.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import campaign as c
from tools.analysis.features.extract import extract_one


def analysis_id():
    paths = list((c.ROOT / 'tools/analysis/features').glob('*.py'))
    paths += list((c.ROOT / 'tools/hub/vendor/leviathan').glob('*.py'))
    paths += list((c.ROOT / 'tools/hub/vendor/ouroboros').glob('*.py'))
    return hashlib.sha256(''.join(str(p.relative_to(c.ROOT)) + c.sha(p)
                                  for p in sorted(paths)).encode()).hexdigest()


def canonical(row, dest, aid):
    cache = c.STORE / 'analysis' / aid
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (row['replay_sha256'] + '.json')
    if not path.exists():
        out = extract_one((str(dest / row['replay']), str(cache / 'frames'),
                           {'seed': row['seed'], 'sandbox': False}))
        if 'error' in out:
            raise ValueError(out['error'])
        small = {k: out[k] for k in ('side_rows', 'checks')}
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(small, indent=2) + '\n')
        tmp.replace(path)
    out = json.loads(path.read_text())
    failures = [x for x in out['checks'] if x['check'] != 'corpse_drop_shortfall'
                and (not math.isfinite(x['residual']) or abs(x['residual']) > 1e-6)]
    if failures:
        raise ValueError(f'Replay bookkeeping failed: {path}: {failures}')
    sides = {x['side']: x for x in out['side_rows']}
    feature = sides[row['side']]
    if (feature['bot'] != Path(row['cand']).name or feature['opponent'] != row['opp']
            or feature['result'] != row['result'] or feature['rounds'] != row['rounds']):
        raise ValueError(f'Replay/index attribution mismatch: {path}')
    # Round-level snapshots and inferred intake are different estimands. Record
    # the discrepancy without silently replacing the historical gate's inputs.
    pairs = [(f'eaten_r{r}', f'pearls@{r}') for r in (50, 100, 150, 250)]
    pairs += [('units_r100', 'units@100'), ('len_r100', 'total@100')]
    discrepancies = {a: {'arena': row['us'][a], 'replay': feature[b]}
                     for a, b in pairs if row['us'][a] != feature[b]}
    return feature, discrepancies, out['checks']


def build_report(candidate):
    aid = analysis_id()
    report = dict(candidate=candidate, parent=c.panel.PARENT, analysis_sha256=aid,
                  promotion='NOT AUTHORIZED', panels={}, measurement_discrepancies=[])
    all_rows = {}
    for pn in ('z1', 'gen'):
        rows, feats = {}, {}
        for bot in (c.panel.PARENT, candidate):
            dest = c.run_dir(bot, pn)
            if dest.exists():
                if json.loads((dest / 'contract.json').read_text()) != c.contract(bot, pn):
                    raise ValueError(f'Frozen inputs changed: {dest}')
            rows[bot] = c.read_rows(bot, pn)
            feats[bot] = {}
            for key, row in rows[bot].items():
                feature, differences, checks = canonical(row, dest, aid)
                feats[bot][key] = feature
                if differences:
                    report['measurement_discrepancies'].append(
                        dict(bot=bot, panel=pn, fixture=key, differences=differences))
        parent, child = rows[c.panel.PARENT], rows[candidate]
        paired = sorted(parent.keys() & child.keys())
        wanted = c.panel.expected(pn, [1, 2, 3])
        complete = set(parent) == set(child) == wanted
        report['panels'][pn] = dict(parent_games=len(parent), candidate_games=len(child),
            paired=len(paired), required_pairs=len(wanted), complete=complete,
            maps=sorted({k[0] for k in paired}), seats=sorted({k[1] for k in paired}),
            seeds=sorted({k[2] for k in paired}))
        if paired:
            report['panels'][pn]['descriptive_only'] = {
                field: sum(feats[candidate][k][field] - feats[c.panel.PARENT][k][field]
                           for k in paired) / len(paired)
                for field in ('won', 'pearls@50', 'pearls@100', 'units@100', 'total@100')}
        all_rows[pn] = rows
    complete = all(p['complete'] for p in report['panels'].values())
    report['status'] = 'COMPLETE COVERAGE; GATE AUDIT STILL REQUIRED' if complete else 'INCOMPLETE; NO GATE VERDICT'
    if complete:
        stats = {pn: c.panel.gate.panel_stats(rows[candidate], rows[c.panel.PARENT], pn)
                 for pn, rows in all_rows.items()}
        verdict, reasons = c.panel.gate.gate(stats)
        report['historical_arena_mean_gate_diagnostic'] = dict(verdict=verdict, reasons=reasons, panels=stats)
    report['limitations'] = ('Descriptive partial coverage is not a strength estimate. Arena inferred intake and '
        'turn-time material differ from replay event counts and round-start material. The historical gate '
        'diagnostic is only emitted at complete three-seed coverage. Median form, tempo, opening percentiles, '
        'per-map guards and sandbox CPU validation remain separate requirements.')
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', choices=c.QUEUE, default=c.QUEUE[0])
    a = ap.parse_args()
    report = build_report(a.candidate)
    dest = c.STORE / f'{a.candidate}-report.json'
    dest.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'measurement_discrepancies'}, indent=2))
    print(f'{len(report["measurement_discrepancies"])} discrepant game records; full details: {dest}')


if __name__ == '__main__':
    main()
