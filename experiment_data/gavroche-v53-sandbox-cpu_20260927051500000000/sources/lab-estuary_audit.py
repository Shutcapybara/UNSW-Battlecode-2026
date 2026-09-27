#!/usr/bin/env python3
"""Audit Estuary experiments without treating deliberate donations as bugs.

Use --metrics for JSON files produced by tools/public_replay_review.py.
Corpse pickup attribution follows the last spawn at a cell; overwrites and
uncollected pearls prevent interpreting it as exact net economic efficiency.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re


def audit(folder, metrics=None):
    manifest = json.loads((folder / 'manifest.json').read_text())
    focus = manifest['focus']
    output = []
    for row in json.loads((folder / 'results.json').read_text()):
        side = 'A' if row['team_a'] == focus else 'B'
        stats = row.get('analysis', {}).get('teams', {}).get(side, {})
        donors, unexpected = {}, []
        for death in row.get('analysis', {}).get('death_events', []):
            if death['team'] != side or death['cause'] != 'invalid':
                continue
            match = re.fullmatch(r'estuary feed recipient=(\d+) len=(\d+)', death.get('indicator') or '')
            if match and death.get('decision_round') == death['round']:
                donors[death['id']] = int(match[1])
            else:
                unexpected.append(death)
        result = dict(map=row['map'], side=side,
                      opponent=row['team_b'] if side == 'A' else row['team_a'],
                      result='E' if row['outcome'] == 'error' else 'D' if row['outcome'] == 'draw'
                             else 'W' if row['winner'] == focus else 'L',
                      rounds=row['rounds'], final=stats.get('final'),
                      cpu_p99=stats.get('p99_points_estimate'), cpu_max=stats.get('max_points_estimate'),
                      timeouts=stats.get('timeouts'), donations=len(donors),
                      unexpected_invalid=unexpected, analysis_error=row.get('analysis_error'),
                      replay=str(folder / row['replay']) if row.get('replay') else None)
        metric = metrics / (Path(row['replay']).stem + '.json') if metrics and row.get('replay') else None
        if metric and metric.exists():
            detail = json.loads(metric.read_text())
            if Path(detail['file']).resolve() != (folder / row['replay']).resolve():
                result['metrics_note'] = 'Skipped same-named metrics from a different run.'
                output.append(result)
                continue
            curve = {r['round']: r[side] for r in detail['curve']}
            result['snapshots'] = {r: curve.get(r) for r in (30, 100, 280, 380, 400, 450)}
            result['large_self_wall_deaths'] = [d for d in detail['deaths'] if d['team'] == side
                                               and d['length'] >= 15 and d['cause'] in ('self', 'wall')]
            result['births'] = detail['stats'][side].get('splits', 0)
            result['newborn_deaths_10'] = detail['stats'][side].get('newborn_deaths_10', 0)
            result['turns'] = detail['stats'][side]['turns']
            result['donor_drops'] = sum((d['length'] + 1) // 2 for d in detail['deaths'] if d['id'] in donors)
            pickups = Counter()
            for transfer in detail['transfers']:
                donor = transfer['donor']
                if donor in donors:
                    kind = ('recipient' if transfer['collector'] == donors[donor] else
                            'other_ally' if transfer['team'] == side else 'enemy')
                    pickups[kind] += 1
                    if kind == 'recipient' and transfer['age'] <= 10:
                        pickups['recipient_within_10'] += 1
            result['donor_pickups'] = dict(pickups)
        output.append(result)
    return dict(run=str(folder), focus=focus, sandbox=manifest['sandbox'],
                overrides=manifest['overrides'], counts=dict(Counter(r['result'] for r in output)), fixtures=output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', nargs='+', type=Path)
    parser.add_argument('--metrics', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps([audit(p, args.metrics) for p in args.runs], indent=2) + '\n')
    print(args.out)
