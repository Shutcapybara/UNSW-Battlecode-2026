"""Ranked Slithery mass-flow pilot; frozen geometry/seat/time matched selection.

Reads existing replays only. Flow window is [round250 start, round400 start).
Matching does not control opponents and is not a causal policy comparison.
"""
import argparse
import collections
import datetime
import hashlib
import json
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--repo', type=Path, required=True)
ap.add_argument('--snapshot', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--start', type=int, default=250)
ap.add_argument('--end', type=int, default=400)
a = ap.parse_args()
assert 0 <= a.start < a.end <= 500
a.out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(a.repo))
from tools.analysis.features import frame as F

idx = list(map(json.loads, (a.snapshot / 'index.jsonl').read_text().splitlines()))
tops = {r['id'] for r in json.loads((a.snapshot / 'ladder.json').read_text())
        if r.get('rank') and r['rank'] <= 10 and not r.get('dev')}
pool = [m for m in idx if m.get('status') == 'completed' and m.get('ranked')
        and m.get('map_name') == 'Slithery Fight' and (m.get('started_at') or '') >= '2026-10-02T04:22']
own = [m for m in pool if 7 in (m['team_a'], m['team_b'])]
stamp = lambda m: datetime.datetime.fromisoformat(m['started_at'].replace('Z', '+00:00')).timestamp()
blocks, tasks = [], {}
for m in own:
    side = 'A' if m['team_a'] == 7 else 'B'
    matches = sorted([x for x in pool if 7 not in (x['team_a'], x['team_b'])
                      and x['team_a' if side == 'A' else 'team_b'] in tops
                      and x['map_hash'] == m['map_hash'] and abs(stamp(x) - stamp(m)) <= 21600],
                     key=lambda x: (abs(stamp(x) - stamp(m)), x['game_id']))[:3]
    blocks.append(dict(own_game=m['game_id'], side=side, series=m['series_id'], map_hash=m['map_hash'],
                       matches=[dict(game=x['game_id'], dt_seconds=stamp(x)-stamp(m)) for x in matches]))
    for x in [m] + matches:
        tasks[x['game_id']] = x
manifest = dict(blocks=blocks, top10=sorted(tops), games=list(tasks),
                window_start=a.start, window_end_exclusive=a.end,
                index_sha256=hashlib.sha256((a.snapshot/'index.jsonl').read_bytes()).hexdigest(),
                cohort='ranked post-m2 Slithery; own14585 verified in payload; field currenttop10, same exacthash and seat, within6h, nearest3; opponents unmatched')
if (a.out / 'selection.json').exists():
    previous = json.loads((a.out / 'selection.json').read_text())
    assert previous.get('window_start', 250) == a.start and previous.get('window_end_exclusive', 400) == a.end
    assert previous['index_sha256'] == manifest['index_sha256'] and previous['games'] == manifest['games']
(a.out / 'selection.json').write_text(json.dumps(manifest, indent=2)+'\n')
path = a.out / 'flows.jsonl'
done = {r['game_id'] for r in map(json.loads, path.read_text().splitlines())} if path.exists() else set()
for gid, m in tasks.items():
    if gid in done:
        continue
    p = a.repo / 'public_replays/corpus/replays' / f'{gid}.replay'
    assert hashlib.sha256(p.read_bytes()).hexdigest() == m['sha256']
    g = F.decode(p)
    assert g['map_hash'] == m['map_hash'][:12]
    assert g['winner'].lower() == m['winner']
    rec = {k: m[k] for k in ('game_id', 'series_id', 'started_at', 'map_hash', 'team_a', 'team_b', 'sha256')}
    rec.update(last_round=g['last_round'], winner=g['winner'], reason=g['reason'], sides=[])
    for side in ('A', 'B'):
        if m['team_a' if side == 'A' else 'team_b'] == 7:
            assert g['bot'+side] == '14585'
        if g['last_round'] < a.end - 1:
            rec['sides'].append(dict(side=side, reached_window=False, submission=g['bot'+side]))
            continue
        snapshots = g['rounds']
        def totals(r):
            bodies = [b for t,b in snapshots[r].values() if t == side]
            return dict(units=len(bodies), total=sum(map(len,bodies)))
        events = {k:[e for e in es if e.get('team') == side and a.start <= e['round'] < a.end]
                  for k,es in g['events'].items()}
        eats = collections.Counter(e['origin'] for e in events['eats'])
        paid = sum(e.get('paid', 0) for e in events['actions'] if e['kind'] == 'move')
        deaths = sum(e['length'] for e in events['deaths'])
        split_delta = sum(e['parent_len']+e['child_len']-e['before'] for e in events['splits'])
        start, end = totals(a.start), totals(a.end)
        delta = end['total']-start['total']
        predicted = sum(eats.values())-paid-deaths+split_delta
        counts = collections.Counter(e['cause'] for e in events['deaths'])
        row = dict(side=side, submission=g['bot'+side], reached_window=True, start=start, end=end,
                   eats=dict(eats), eats_total=sum(eats.values()), sprint_paid=paid, death_segments=deaths,
                   split_delta=split_delta, splits=len(events['splits']), deaths=dict(counts),
                   at_cap_rounds=sum(totals(r)['units'] >= 62 for r in range(a.start,a.end)),
                   observed_delta=delta, predicted_delta=predicted, residual=delta-predicted)
        rec['sides'].append(row)
    with path.open('a') as f:
        f.write(json.dumps(rec, separators=(',', ':'))+'\n')
    print(gid, [(r['side'], r.get('residual')) for r in rec['sides']], flush=True)
