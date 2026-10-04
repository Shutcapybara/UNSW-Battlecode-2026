"""Small reproducible cohort/label summaries from entry_label_audit's local rows."""
import argparse
import collections
import csv
import json
import random
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--rows', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
games = list(map(json.loads, a.rows.read_text().splitlines()))
assert len(games) == 96 and len({g['game_id'] for g in games}) == 96
side_rows, totals, strata = [], collections.defaultdict(collections.Counter), collections.defaultdict(list)
for g in games:
    for s in g['sides']:
        who = s['who']
        totals[who].update(s['counts'])
        row = {k: g[k] for k in ('game_id', 'series_id', 'ranked', 'map_name', 'map_hash', 'own_submission', 'last_round')}
        row.update(side=s['side'], team=s['team'], who=who, death_round=s['death_round'], death_cause=s['death_cause'])
        low = s['low_moves']
        row.update(peer_low_moves=len(low), peer_low_wall=sum(m['peer_wall6'] for m in low),
                   corrected_low_moves=sum(m['capacity'] <= 4 for m in low),
                   corrected_low_wall=sum(m['capacity'] <= 4 and m['peer_wall6'] for m in low),
                   window_only_seventh=sum(m['peer_wall6'] and m['label_six'] != 'wall' for m in low),
                   low_censored=sum(m['label_six'] == 'censored' for m in low),
                   low_competing=sum(m['label_six'].startswith('competing_') for m in low),
                   low_non_single=sum(m['kind'] != 'move' or m['steps'] != 1 for m in low),
                   peer_low_death=int(any(m['peer_wall6'] for m in low)))
        for cap in (4, 5):
            eligible = [m for m in low if m['capacity'] <= cap and m['kind'] == 'move' and m['steps'] == 1]
            first = eligible[0] if eligible else None
            row[f'first_cap{cap}_landmark'] = first['landmark'] if first else None
            row[f'first_cap{cap}_label'] = first['label_six'] if first else 'unexposed'
            row[f'first_cap{cap}_ate'] = first['eats'] if first else None
        side_rows.append(row)
        strata[(who, g['own_submission'], g['ranked'])].append(row)

def summarize(rows):
    out = {'games': len(rows), 'series': len({r['series_id'] for r in rows}),
           'wall_deaths': sum(r['death_cause'] == 'wall' for r in rows)}
    for cap in (4, 5):
        key = f'first_cap{cap}_label'
        labels = collections.Counter(r[key] for r in rows)
        out[key] = dict(labels)
        at_risk = [r for r in rows if r[key] not in ('unexposed', 'censored')]
        out[f'first_cap{cap}_complete_series'] = len({r['series_id'] for r in at_risk})
        walls = sum(r[key] == 'wall' for r in at_risk)
        # Boundary bootstrap intervals have false precision; report none there.
        ci = None
        if 0 < walls < len(at_risk) and out[f'first_cap{cap}_complete_series'] >= 8:
            clusters = collections.defaultdict(list)
            for r in at_risk:
                clusters[r['series_id']].append(r[key] == 'wall')
            ids, rng, vals = list(clusters), random.Random(2424), []
            for _ in range(2000):
                draw = [v for _ in ids for v in clusters[rng.choice(ids)]]
                vals.append(sum(draw) / len(draw))
            vals.sort()
            ci = [vals[49], vals[1949]]
        out[f'first_cap{cap}_wall_known_fraction'] = walls / len(at_risk) if at_risk else None
        out[f'first_cap{cap}_series_boot95'] = ci
    return out

out = {'games': len(games), 'series': len({g['series_id'] for g in games}),
       'peer_totals': {k: dict(v) for k, v in totals.items()},
       'by_parent_mode_side': {'|'.join(map(str, k)): summarize(v) for k, v in strata.items()},
       'scope': 'First surviving single-step entry per queen, six subsequent rounds. Parent/mode separated. No causal or stable target claim.'}
out['low_move_audit'] = {}
for who in ('us', 'opp'):
    rows = [r for r in side_rows if r['who'] == who]
    keys = ['peer_low_moves', 'peer_low_wall', 'corrected_low_moves', 'corrected_low_wall',
            'window_only_seventh', 'low_censored', 'low_competing', 'low_non_single', 'peer_low_death']
    out['low_move_audit'][who] = {k: sum(r[k] for r in rows) for k in keys}
    out['low_move_audit'][who]['schooltime_moves'] = sum(r['peer_low_moves'] for r in rows if r['map_name'] == 'Schooltime')
    out['low_move_audit'][who]['schooltime_exposed_queens'] = sum(r['peer_low_moves'] > 0 for r in rows if r['map_name'] == 'Schooltime')

hash_groups = collections.defaultdict(list)
for r in side_rows:
    hash_groups[(r['map_name'], r['map_hash'], r['ranked'], r['own_submission'], r['who'])].append(r)
out['exact_hash_strata'] = [dict(map_name=k[0], map_hash=k[1], ranked=k[2], own_submission=k[3], who=k[4],
                               **summarize(v)) for k, v in sorted(hash_groups.items())]
out['selection_window'] = [min(g['started_at'] for g in games), max(g['started_at'] for g in games)]
out['map_hashes'] = len({g['map_hash'] for g in games})

a.out.mkdir(parents=True, exist_ok=True)
(a.out / 'summary.json').write_text(json.dumps(out, indent=2) + '\n')
with (a.out / 'queen-cohorts.csv').open('w') as f:
    w = csv.DictWriter(f, fieldnames=list(side_rows[0]))
    w.writeheader()
    w.writerows(side_rows)
print(json.dumps(out, indent=2))
