"""Shenzhen: H-SZ5 (does anyone hunt queens?), H-SZ7 (queen exposure/escort), H-SZ8b (late-feed meals). Reads build/shenzhen/hazard."""
import duckdb
import pandas as pd, numpy as np
h = duckdb.sql("select * from 'build/shenzhen/hazard/part-*.parquet'").df()
T = pd.read_parquet('build/s1/corpus/teams.parquet'); cr = dict(zip(T.team, T.crank)); nm = dict(zip(T.team, T.name))
coh = lambda t: 'us' if t == '7' else 'top10' if (cr.get(t) or 999) <= 10 else 'r11_50' if (cr.get(t) or 999) <= 50 else 'other'
e = h[h.kind == 'exp'].copy(); e['killer'] = e.opp; e['kcoh'] = e.killer.map(coh); e['kname'] = e.killer.map(nm)
print('games', h.game.nunique())
def mh(x):
    # Mantel-Haenszel rate ratio queen vs non-queen, strata = length bin
    num = den = 0.0
    for lb, s in x.groupby('lbin'):
        q, n = s[s.queen], s[~s.queen]
        a, t1 = q.enemy_deaths.sum(), q.dragon_rounds.sum(); b, t0 = n.enemy_deaths.sum(), n.dragon_rounds.sum()
        T_ = t1 + t0
        if T_ == 0: continue
        num += a * t0 / T_; den += b * t1 / T_
    qd = x[x.queen].enemy_deaths.sum()
    return pd.Series(dict(queen_kills=qd, queen_rate_1k=1000 * qd / max(1, x[x.queen].dragon_rounds.sum()),
                          other_rate_1k=1000 * x[~x.queen].enemy_deaths.sum() / max(1, x[~x.queen].dragon_rounds.sum()),
                          RR_mh=num / den if den else np.nan))
print('== H-SZ5 queen vs non-queen enemy-kill hazard, by killer cohort (length-stratified rate ratio)')
print(e.groupby('kcoh').apply(mh, include_groups=False).round(3).to_string())
print('-- by killer team (top ten + us)')
x = e[e.killer.map(lambda t: (cr.get(t) or 999) <= 10 or t == '7')]
print(x.groupby('kname').apply(mh, include_groups=False).round(3).sort_values('RR_mh').to_string())
print('-- victim length bins, all killers: dragon-rounds and rate per 1k')
print(e.groupby(['lbin', 'queen']).agg(dr=('dragon_rounds', 'sum'), kills=('enemy_deaths', 'sum')).assign(rate=lambda s: (1000 * s.kills / s.dr).round(2)).to_string())
q = h[h.kind == 'qexp'].copy(); q['coh'] = q.team.map(coh); q['name'] = q.team.map(nm)
q = q[q.rounds > 0]
print('== H-SZ7 queen exposure while alive (r>=10): share of queen-rounds with enemy head within 3 / 6, ally head within 3')
agg = q.groupby('coh').apply(lambda s: pd.Series(dict(n=len(s), qrounds=s.rounds.sum(), e3=s.e3.sum() / s.rounds.sum(), e6=s.e6.sum() / s.rounds.sum(), a3=s.a3.sum() / s.rounds.sum(), dmean=(s.dmin_mean * s.rounds).sum() / s.rounds.sum())), include_groups=False)
print(agg.round(3).to_string())
t = q[q.team.map(lambda t: (cr.get(t) or 999) <= 10)]
print(t.groupby('name').apply(lambda s: pd.Series(dict(n=len(s), e3=s.e3.sum() / s.rounds.sum(), a3=s.a3.sum() / s.rounds.sum(), dmean=(s.dmin_mean * s.rounds).sum() / s.rounds.sum())), include_groups=False).round(3).to_string())
m = h[h.kind == 'meal'].copy(); m['coh'] = m.team.map(coh); m['name'] = m.team.map(nm)
print('== H-SZ8b queen meals by phase and origin (sum over games), top-10 teams')
mm = m[m.team.map(lambda t: (cr.get(t) or 999) <= 10)]
print(mm.pivot_table(index=['name', 'phase'], columns='origin', values='n', aggfunc='sum', fill_value=0).to_string())
