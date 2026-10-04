"""Shenzhen: H-SZ14 (enemy queen visibility / home range) and H-SZ8 mechanism (donors of crown meals). Reads build/shenzhen/qsight."""
import duckdb
import pandas as pd, numpy as np
h = duckdb.sql("select * from 'build/shenzhen/qsight/part-*.parquet'").df()
T = pd.read_parquet('build/s1/corpus/teams.parquet'); cr = dict(zip(T.team, T.crank)); nm = dict(zip(T.team, T.name))
coh = lambda t: 'us' if t == '7' else 'top10' if (cr.get(t) or 999) <= 10 else 'r11_50' if (cr.get(t) or 999) <= 50 else 'other'
print('games', h.game.nunique())
v = h[(h.kind == 'vis') & (h.alive_rounds > 0)].copy(); v['coh'] = v.team.map(coh); v['name'] = v.team.map(nm)
v['seen_share'] = v.seen_rounds / v.alive_rounds
print('== H-SZ14 queen seen by the enemy (any segment in a 7x7 vision of an enemy head), queens alive >= r5')
print(v.groupby('coh').agg(n=('game', 'size'), alive_rounds_med=('alive_rounds', 'median'), seen_share=('seen_share', 'mean'),
      ever_seen=('first_seen', lambda s: s.notna().mean()), first_seen_med=('first_seen', 'median')).round(3).to_string())
long = v[v.alive_rounds >= 400]
print('-- queens alive >= 400 rounds (keepers): by team (top 10)')
print(long[long.coh == 'top10'].groupby('name').agg(n=('game', 'size'), seen_share=('seen_share', 'mean'), ever=('first_seen', lambda s: s.notna().mean()),
      first_med=('first_seen', 'median'), home150=('home150', 'median'), home300=('home300', 'median'), home490=('home490', 'median')).round(2).to_string())
print('-- home range (Chebyshev distance of queen head from its spawn), alive queens, all cohorts')
for c in (50, 150, 300, 490):
    x = v[v[f'home{c}'] >= 0]
    print(c, x.groupby('coh')[f'home{c}'].describe(percentiles=[.25, .5, .75])[['count', '25%', '50%', '75%']].round(1).to_dict('index'))
f = h[h.kind == 'feed'].copy(); f['coh'] = f.team.map(coh); f['name'] = f.team.map(nm)
f['phase'] = pd.cut(f.meal_round, [-1, 149, 399, 600], labels=['r0-149', 'r150-399', 'r400+'])
print('== H-SZ8 mechanism: donors of queen meals on ally corpses (top 10), death cause share by phase')
x = f[f.coh == 'top10']
print(pd.crosstab([x.phase], x.donor_cause, normalize='index').round(3).to_string())
print(pd.crosstab([x.name], x.donor_cause).to_string())
print('donor length median', x.groupby('phase', observed=True).donor_len.median().to_dict(), 'donor age median', x.groupby('phase', observed=True).donor_age.median().to_dict(), 'lag median', x.lag.median())
print('meals per donor death (pearls eaten per corpse) top10:', round(len(x) / max(1, x.groupby(['game', 'side']).apply(lambda s: s.donor_len.count(), include_groups=False).sum()), 2))
