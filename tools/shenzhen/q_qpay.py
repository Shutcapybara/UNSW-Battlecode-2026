"""Shenzhen H-SZ21: sprint tax by cohort, queen vs all (RL games, post-m2)."""
import duckdb, pandas as pd, numpy as np
d = duckdb.sql("select distinct on (game, side) * from 'build/shenzhen/qpay/part-*.parquet'").df()
T = pd.read_parquet('build/s1/corpus/teams.parquet'); cr = dict(zip(T.team, T.crank)); nm = dict(zip(T.team, T.name))
d['coh'] = d.team.map(lambda t: 'us' if t == '7' else 'top10' if (cr.get(t) or 999) <= 10 else 'r11_50' if (cr.get(t) or 999) <= 50 else 'other')
print('games', d.game.nunique())
g = d.groupby('coh').agg(n=('game', 'size'), all_paid=('all_paid', 'mean'), all_multi_share=('all_multi', 'sum'), all_moves=('all_moves', 'sum'),
     q_paid=('q_paid', 'mean'), q_paid250=('q_paid250', 'mean'), q_multi=('q_multi', 'sum'), q_moves=('q_moves', 'sum'), q_alive=('q_alive_end', 'mean'))
g['all_multi_share'] = g.all_multi_share / g.all_moves; g['q_multi_share'] = g.q_multi / g.q_moves
print(g.drop(columns=['all_moves', 'q_multi', 'q_moves']).round(3).to_string())
k = d[d.q_alive_end]
print('-- queens alive at end: paid segments per game, by cohort'); print(k.groupby('coh').agg(n=('game', 'size'), q_paid=('q_paid', 'mean'), q_paid_any=('q_paid', lambda s: (s > 0).mean()), qlen=('qlen_end', 'median')).round(3).to_string())
t = d[d.coh == 'top10']; t = t.assign(name=t.team.map(nm))
print(t.groupby('name').agg(n=('game', 'size'), all_paid=('all_paid', 'mean'), q_paid=('q_paid', 'mean'), q_multi=('q_multi', 'mean')).round(2).to_string())
