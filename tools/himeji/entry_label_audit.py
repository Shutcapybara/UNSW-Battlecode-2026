"""Freeze/replay a peer systematic sample; audit directed capacity and six-round labels.

No caches, simulator, API or shared-store writes. A move row is a surviving round-boundary
transition, not a claim about fatal actions or exact turn occupancy. Resume by game ID.
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--repo', type=Path, required=True)
ap.add_argument('--index', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--selection-in', type=Path, help='Published selection.json to replay exactly those IDs')
a = ap.parse_args()
sys.path.insert(0, str(a.repo))
from tools.analysis.features import frame as F

a.out.mkdir(parents=True, exist_ok=True)
metas = [m for m in map(json.loads, a.index.read_text().splitlines())
         if m.get('status') == 'completed' and (m.get('started_at') or '') >= '2026-10-02T03:49'
         and 7 in (m.get('team_a'), m.get('team_b'))
         and (a.repo / 'public_replays/corpus/replays' / f"{m['game_id']}.replay").exists()]
pick = metas[::max(1, len(metas) // 96)][:96]
if a.selection_in:
    ids = json.loads(a.selection_in.read_text())['game_ids']
    by_id = {m['game_id']: m for m in metas}
    pick = [by_id[i] for i in ids]
selection = {'eligible': len(metas), 'index_sha256': hashlib.sha256(a.index.read_bytes()).hexdigest(),
             'game_ids': [m['game_id'] for m in pick], 'selection': 'peer index order, stride floor(N/96), first96'}
(a.out / 'selection.json').write_text(json.dumps(selection, indent=2) + '\n')
target = a.out / 'games.jsonl'
done = {r['game_id'] for r in map(json.loads, target.read_text().splitlines())} if target.exists() else set()

def capacity(nbr, u, v, memo):
    """Number of reachable cells INCLUDING v, excluding u; values >=18 capped18."""
    if (u, v) in memo:
        return memo[u, v]
    seen, todo = {u, v}, [v]
    while todo and len(seen) - 1 < 18:
        for x in nbr.get(todo.pop(), ()):
            if x is not None and x not in seen:
                seen.add(x)
                todo.append(x)
    memo[u, v] = min(18, len(seen) - 1)
    return memo[u, v]

for meta in pick:
    gid = meta['game_id']
    if gid in done:
        continue
    p = a.repo / 'public_replays/corpus/replays' / f'{gid}.replay'
    assert hashlib.sha256(p.read_bytes()).hexdigest() == meta['sha256']
    g = F.decode(p)
    root = F._reader(p).object(0, 0)
    assert hashlib.sha256(root.text(0).encode()).hexdigest() == meta['map_hash']
    assert g['winner'].lower() == meta['winner']
    own = 'A' if meta['team_a'] == 7 else 'B'
    out = {k: meta[k] for k in ('game_id', 'series_id', 'ranked', 'map_name', 'map_hash', 'started_at', 'sha256')}
    out.update(own_side=own, own_submission=root.text(1 if own == 'A' else 2),
               last_round=g['last_round'], official_winner=g['winner'], sides=[])
    R, memo = g['rounds'], {}
    for side in ('A', 'B'):
        q = min(i for i, (team, body) in R[0].items() if team == side)
        death = next((d for d in g['events']['deaths'] if d['id'] == q), None)
        dr = death['round'] if death else 10**9
        cause = death['cause'] if death else None
        acts = {x['round']: x for x in g['events']['actions'] if x['id'] == q}
        eats = collections.Counter(x['round'] for x in g['events']['eats'] if x['id'] == q)
        counts, low = collections.Counter(), []
        # Deliberately reproduce peer surviving-transition window before auditing it.
        for t in range(1, len(R) - 1):
            if q not in R[t] or q not in R[t + 1]:
                break
            u, v = R[t][q][1][0], R[t + 1][q][1][0]
            if u == v or v not in g['nbr'].get(u, ()):
                continue
            cap = capacity(g['nbr'], u, v, memo)
            peer_e = cap - 1
            b = '0-4' if peer_e <= 4 else '5-8' if peer_e <= 8 else '9-16' if peer_e <= 16 else '17+'
            peer_wall = cause == 'wall' and 0 <= dr - (t + 1) <= 6
            counts[b + '_n'] += 1
            counts[b + '_wall'] += int(peer_wall)
            if cap > 5:
                continue
            landmark = t + 1
            if landmark <= dr < landmark + 6:
                label = 'wall' if cause == 'wall' else 'competing_' + cause
            elif g['last_round'] < landmark + 5:
                label = 'censored'
            else:
                label = 'alive_six'
            ac = acts.get(t, {})
            low.append(dict(round=t, landmark=landmark, u=u, v=v, capacity=cap, peer_e=peer_e,
                            length_before=len(R[t][q][1]), length_after=len(R[t+1][q][1]),
                            kind=ac.get('kind'), steps=ac.get('steps'), eats=eats[t],
                            peer_wall6=peer_wall, label_six=label))
        out['sides'].append(dict(side=side, who='us' if side == own else 'opp',
                                 team=meta['team_a' if side == 'A' else 'team_b'], queen=q,
                                 death_round=dr if death else None, death_cause=cause,
                                 counts=dict(counts), low_moves=low))
    with target.open('a') as f:
        f.write(json.dumps(out, separators=(',', ':')) + '\n')
    print(gid, len(out['sides'][0]['low_moves']), len(out['sides'][1]['low_moves']), flush=True)
