"""Behavioural fidelity: target (8264 public games) vs clone and local bots in closed loop, same metric code."""
import json, glob, collections
import numpy as np, pandas as pd
W = ['0-50', '50-100', '100-250', '250-400', '400-500']


def profile(d, s):
    T = d['teams'][s]
    acts = d['actions'][s]
    turns = sum(T['turns'].values()) or 1
    splits = sum(T['split'].values())
    deaths = collections.Counter()
    for k, v in T['death'].items():
        deaths[k.split('|')[1]] += v
    eat_bed = sum(v for k, v in T['eat'].items() if k.endswith('bed') or k.endswith('init'))
    eat_c = sum(v for k, v in T['eat'].items() if k.endswith('corpse'))
    tr = {r['round']: r[s] for r in d['traj']}
    g = lambda r, k: tr[r][k] if r in tr else np.nan
    return dict(split_rate=splits / turns, split1_rate=deaths['noValidAction'] / turns,
                sprint_rate=sum(T['sprint'].values()) / turns, sonar_per_turn=sum(T['sonar'].values()) / turns,
                corpse_share=eat_c / max(eat_bed + eat_c, 1), h2h_deaths_per_1k=1000 * deaths['hitHeadToHead'] / turns,
                wall_self_body_per_1k=1000 * (deaths['hitWall'] + deaths['hitSelf'] + deaths['hitOtherBody']) / turns,
                units_r100=g(100, 'units'), units_r250=g(250, 'units'), longest_r400=g(400, 'longest'),
                longest_end=d['result'][s]['longest'], units_end=d['result'][s]['units'],
                ended_by_elim=d['result']['reason'] == 'teamEliminated', rounds=d['result']['rounds'])


rows = []
m = pd.read_csv('out/corpus/manifest.csv', dtype={'game_id': str})
m = m[(m.status == 'ok') & (m.target_submission == 8264)]
for _, r in m.iterrows():
    d = json.load(open(f'out/descriptive/{r.game_id}.json'))
    rows.append(dict(who='Vibing++ 8264 (public)', map=d['map'], result=r.result, **profile(d, r.side)))
res = pd.read_csv('out/closed_loop/results.csv')
for _, r in res.iterrows():
    stem = f"{r.arm}__{r.opp}__{r['map'][:-4]}__{r.side}"
    f = f'out/closed_loop/descriptive/{stem}.json'
    d = json.load(open(f))
    o = 'B' if r.side == 'A' else 'A'
    rows.append(dict(who=r.arm, map=d['map'], result=r.result, **profile(d, r.side)))
    rows.append(dict(who=r.opp + ' (vs ' + ('mimic' if 'mimic' in r.arm else 'v10') + ')', map=d['map'],
                     result={'W': 'L', 'L': 'W'}.get(r.result, r.result), **profile(d, o)))
P = pd.DataFrame(rows)
P.to_csv('out/agg/fidelity_profiles.csv', index=False)
keep = ['Vibing++ 8264 (public)', 'ouroboros-m01-vibing-mimic', 'ouroboros-v10-beacon', 'gavroche-v32-supported-divecap (vs mimic)',
        'serre-v01-foundation (vs mimic)', 'sinbad-v07-divecap (vs mimic)', 'fry-v14-stateful-size-aware-3 (vs mimic)']
cols = ['split_rate', 'split1_rate', 'sprint_rate', 'sonar_per_turn', 'corpse_share', 'h2h_deaths_per_1k', 'wall_self_body_per_1k',
        'units_r100', 'units_r250', 'longest_r400', 'longest_end', 'ended_by_elim']
S = P[P.who.isin(keep)].groupby('who')[cols].median().loc[keep]
S['n'] = P[P.who.isin(keep)].groupby('who').size().loc[keep]
pd.set_option('display.width', 250)
print(S.round(3).to_string())
S.round(4).to_csv('out/agg/fidelity_table.csv')
