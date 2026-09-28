"""Aggregate descriptive JSONs into target-vs-opponent tables.

    python3 aggregate_desc.py MANIFEST.csv DESC_DIR OUT_PREFIX [--sub 8264]
"""
import argparse, collections, json
from pathlib import Path
import numpy as np
import pandas as pd

WIN = ['0-50', '50-100', '100-250', '250-400', '400-500']
ap = argparse.ArgumentParser()
ap.add_argument('manifest'); ap.add_argument('desc'); ap.add_argument('out'); ap.add_argument('--sub', type=int)
a = ap.parse_args()
m = pd.read_csv(a.manifest, dtype={'game_id': str})
m = m[m.status == 'ok']
if a.sub:
    m = m[m.target_submission == a.sub]
games, trajrows, splitrows, deathrows = [], [], [], []
for _, r in m.iterrows():
    f = Path(a.desc) / f"{r.game_id}.json"
    if not f.exists():
        continue
    d = json.loads(f.read_text())
    if 'error' in d:
        continue
    t, o = r.side, ('B' if r.side == 'A' else 'A')
    g = dict(game=r.game_id, map=d['map'], W=d['W'], H=d['H'], opp=r.opponent_name, result=r.result,
             sub=r.target_submission, side=t, rounds=d['result']['rounds'], end=d['result']['reason'])
    for who, s in (('t', t), ('o', o)):
        T = d['teams'][s]
        for w in WIN:
            g[f'{who}_turns_{w}'] = T['turns'].get(w, 0)
            g[f'{who}_split_{w}'] = T['split'].get(w, 0)
            g[f'{who}_sprint_{w}'] = T['sprint'].get(w, 0)
            g[f'{who}_xsteps_{w}'] = T['extra_steps'].get(w, 0)
            g[f'{who}_portal_{w}'] = T['portal'].get(w, 0)
            g[f'{who}_sonar_{w}'] = T['sonar'].get(w, 0)
            g[f'{who}_deathlen_{w}'] = T['deathlen'].get(w, 0)
            g[f'{who}_eatbed_{w}'] = T['eat'].get(f'{w}|bed', 0) + T['eat'].get(f'{w}|init', 0)
            g[f'{who}_eatcorpse_{w}'] = T['eat'].get(f'{w}|corpse', 0)
            g[f'{who}_deaths_{w}'] = sum(v for k, v in T['death'].items() if k.startswith(w + '|'))
        for k, v in T['death'].items():
            reason = k.split('|')[1]
            g[f'{who}_death_{reason}'] = g.get(f'{who}_death_{reason}', 0) + v
        for k, v in T['sonar_hit'].items():
            g[f'{who}_sonarhit_{k}'] = v
        g[f'{who}_sonar_distinct'] = d['sonar_distinct'][s]
        g[f'{who}_tle'] = sum(T['tle'].values())
        g[f'{who}_final_units'] = d['result'][s]['units']
        g[f'{who}_final_total'] = d['result'][s]['total']
        g[f'{who}_final_longest'] = d['result'][s]['longest']
        g[f'{who}_first_split'] = d['first'][s].get('split', -1)
        acts = d['actions'][s]
        g[f'{who}_moves'] = sum(v for k, v in acts.items() if k.startswith('move'))
        g[f'{who}_sonar_rel_B'] = d['sonar_dirrel'][s].get('B', 0)
        g[f'{who}_sonar_rel_S'] = d['sonar_dirrel'][s].get('S', 0)
        g[f'{who}_sonar_rel_F'] = d['sonar_dirrel'][s].get('F', 0)
    games.append(g)
    for row in d['traj']:
        for who, s in (('t', t), ('o', o)):
            trajrows.append(dict(game=r.game_id, map=d['map'], result=r.result, who=who, round=row['round'], **row[s]))
    for s in d['splits']:
        splitrows.append(dict(game=r.game_id, map=d['map'], who='t' if s['team'] == t else 'o', **{k: v for k, v in s.items() if k != 'team'}))
    for s in d['deaths']:
        deathrows.append(dict(game=r.game_id, map=d['map'], who='t' if s['team'] == t else 'o', **{k: v for k, v in s.items() if k != 'team'}))
G = pd.DataFrame(games)
TJ = pd.DataFrame(trajrows)
SP = pd.DataFrame(splitrows)
DE = pd.DataFrame(deathrows)
for name, df in (('games', G), ('traj', TJ), ('splits', SP), ('deaths', DE)):
    df.to_csv(f'{a.out}_{name}.csv', index=False)
print('games', len(G), 'W/L', G.result.value_counts().to_dict())
