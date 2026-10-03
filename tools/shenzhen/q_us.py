"""Shenzhen: team 7 live (post-change) — by submission; RL losses, queen-decided anatomy, queen-length counterfactual."""
import duckdb, json
import numpy as np, pandas as pd
sub = {}
for l in open('public_replays/corpus/index.jsonl'):
    g = json.loads(l)
    for s in 'ab':
        if g['team_' + s] == 7:
            sub[str(g['game_id'])] = g.get('bot_' + s) or g.get('sub_' + s)
c = duckdb.connect()
d = c.sql("select distinct on (game, side) * from 'build/shenzhen/lean/*.parquet'").df()
T = pd.read_parquet('build/s1/corpus/teams.parquet')
cr = dict(zip(T.team, T.crank))
d['opp_rank'] = d.opp.map(cr)
d['opp_top10'] = d.opp_rank <= 10
us = d[d.team == '7'].copy()
us['sub'] = us.game.map(sub).map({'14265': 'hb1-14', '14585': 'carthage-05'})
us['rl'] = us.R >= 499
pocket = ['Slithery Fight', 'Autarky', 'Prisoners Dilemma', 'Prisoners Dilemma 10']
print('== by submission x ranked')
print(us.groupby(['sub', 'ranked']).agg(n=('win', 'size'), win=('win', 'mean'), opp_top10=('opp_top10', 'mean'),
      rl=('rl', 'mean')).round(3).to_string())
print('== by submission, vs top-10 opponents only')
v = us[us.opp_top10]
print(v.groupby('sub').agg(n=('win', 'size'), win=('win', 'mean'), rl=('rl', 'mean'),
      win_rl=('win', lambda s: s[us.loc[s.index, 'rl']].mean())).round(3).to_string())
import os
if os.environ.get('SZ_SUB'):
    us = us[us['sub'] == os.environ['SZ_SUB']]
rl = us[us.rl]
L = rl[rl.win == 0]
print(f'== RL games {len(rl)}, RL losses {len(L)}; by verdict reason:')
print(L.reason.value_counts().to_string())
qd = L[L.reason == 'queen']
print(f'queen-decided losses {len(qd)}: we led longest {int((qd.longest_end > qd.opp_longest_end).sum())}, led total {int((qd.total_end > qd.opp_total_end).sum())}; '
      f'opp queen length median {qd.opp_qlen_end.median()} p75 {qd.opp_qlen_end.quantile(.75)} p90 {qd.opp_qlen_end.quantile(.9)}')
print('== counterfactual: our queen alive at the end with length q (everything else equal) — RL losses flipped to wins')
for q in (1, 2, 3, 5, 8, 10, 15, 20, 30):
    flip = ((q > L.opp_qlen_end) | ((q == L.opp_qlen_end) & (L.longest_end > L.opp_longest_end))).sum()
    print(f'  q={q:>2}: {flip}/{len(L)} = {flip / len(L):.2f}   (RL win {rl.win.mean():.2f} -> {(rl.win.sum() + flip) / len(rl):.2f})')
print('== our queen: death round quantiles by map class; r<=10 deaths')
us['pocket'] = us['map'].isin(pocket)
print(us.groupby('pocket').q_death_round.describe(percentiles=[.1, .25, .5, .75]).round(0).to_string())
print(us.groupby('map').agg(n=('win', 'size'), q_dead_r10=('q_death_round', lambda s: (s <= 10).mean()),
      cause=('q_death_cause', lambda s: s.value_counts().head(2).to_dict())).to_string())
