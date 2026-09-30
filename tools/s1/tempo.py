"""S1-T: early-game tempo metrics, validated on the corpus. Run from the repo root.

  python3 tools/s1/tempo.py build     # sample + references + per-side-game metrics -> build/s1/out/tempo/
  python3 tools/s1/tempo.py validate  # win prediction, team-level validity, noise, cohort values
  python3 tools/s1/tempo.py score --db local --where "run like '%renoir-00-base/pool'"   # score any set of side-games
  python3 tools/s1/tempo.py compare --cand <bot> --inc <bot> [--where "run like '%/pool'"]   # decision with a verdict

Curves (per side-game, rounds 0..150 every 5):
  income  I(t) = bed pearls + enemy-corpse pearls eaten by t    (new mass; eating our own corpses is not income)
  loss    D(t) = length lost to our deaths by t, minus our own corpse pearls we re-ate (unrecovered loss)
  material M(t) = total length at t
The reference is the top-10 median curve on the same map (the cohort 'top10', all their games), made non-decreasing.

Candidate metrics (per side-game; averaged over t = 10, 20, ..., 150; units in brackets):
  zgap      mean over t of the field z-score of M(t)                                  [field SD]
  lag_M     horizontal lag on material: t - R_M^-1(M(t))                              [rounds]
  lag_I     horizontal lag on income:   t - R_I^-1(I(t))                              [rounds]
  tempo     lag on income-net-of-loss:  t - R_N^-1(I(t) - D(t) + D_ref(t)) with N = I, i.e. deaths beyond the reference's
            are charged as income not earned                                          [rounds]
Horizontal lag = how many rounds ago the top ten were where we are now. A constant lag means we match their rate and are
merely late; a growing lag (drift = lag(150) - lag(50)) means we are falling behind.
"""
import json, sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import numpy as np
import pandas as pd

S1 = ROOT / 'build' / 's1'
OUT = S1 / 'out' / 'tempo'
T = np.arange(0, 151, 5)
TS = np.arange(10, 151, 10)
PER_MAP = 900            # sampled games per map for the field (all team-7 games are always included)
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)


def pull(c, view='series', where='', sample=True):
    cols = """game, side, map, team, cohort, name, won, round, total, units,
              coalesce(c_eats_bed, 0) + coalesce(c_eats_enemy_corpse, 0) as income,
              coalesce(c_length_lost, 0) - coalesce(c_eats_ally_corpse, 0) as loss"""
    samp = ''
    if sample:
        samp = f"""and (cohort = 'us' or game in (select game from (select game, map, row_number() over (partition by map order by hash(game)) k
                   from (select distinct game, map from sides)) where k <= {PER_MAP}))"""
    w = f'and ({where})' if where else ''
    return c.execute(f"select {cols} from {view} where round % 5 = 0 and round <= 150 {samp} {w}").df()


def curves(df):
    """side-game x round matrices"""
    df = df.sort_values(['game', 'side', 'round'])
    key = df[['game', 'side']].drop_duplicates()
    out = {}
    for k in ('total', 'income', 'loss'):
        m = df.pivot_table(index=['game', 'side'], columns='round', values=k).reindex(columns=T).ffill(axis=1)
        out[k] = m
    meta = df.groupby(['game', 'side']).agg(map=('map', 'first'), team=('team', 'first'), cohort=('cohort', 'first'),
                                            name=('name', 'first'), won=('won', 'first'))
    return out, meta.reindex(out['total'].index)


EXCLUDE_FROM_REFERENCE = {'91', '306'}   # SSS, Cutlery: their unranked games are not their rated bot (S1-Q2 addendum 2)


def reference(C, meta):
    ref = {}
    top = (meta.cohort == 'top10') & ~meta.team.astype(str).isin(EXCLUDE_FROM_REFERENCE)
    for m in meta['map'].unique():
        sel = top & (meta['map'] == m)
        r = {}
        for k in ('total', 'income', 'loss'):
            v = C[k][sel.values].median(axis=0).values
            r[k] = v
        r['total_mono'] = np.maximum.accumulate(r['total'])
        r['income_mono'] = np.maximum.accumulate(r['income'])
        ref[m] = r
    return ref


LAG_MIN = -60             # a side can be at most 60 rounds ahead of the reference (bounds the extrapolation tail)


def inv_lag(v, R, t):
    return float(np.clip(_inv_lag(v, R, t), LAG_MIN, t))


def _inv_lag(v, R, t):
    """horizontal lag: t - (round at which the non-decreasing reference R first reaches v); extrapolate past the end with
    the last 30-round slope; values below R(0) give lag = t"""
    R = R + np.arange(len(R)) * 1e-6          # strictly increasing for interp
    if v <= R[0]:
        return float(t)
    if v >= R[-1]:
        slope = max((R[-1] - R[-7]) / 30.0, 1e-3)
        return float(t - (T[-1] + (v - R[-1]) / slope))
    return float(t - np.interp(v, R, T))


def metrics(C, meta, ref, zstats=None):
    rows = []
    idx = {r: i for i, r in enumerate(T)}
    for j, (key, mrow) in enumerate(meta.iterrows()):
        r = ref.get(mrow['map'])
        if r is None:
            continue
        M, I, D = C['total'].values[j], C['income'].values[j], C['loss'].values[j]
        lm, li, lt = [], [], []
        for t in TS:
            k = idx[t]
            lm.append(inv_lag(M[k], r['total_mono'], t))
            li.append(inv_lag(I[k], r['income_mono'], t))
            # unrecovered loss beyond the reference's is charged as income not earned (and less loss is credited)
            lt.append(inv_lag(I[k] - (D[k] - r['loss'][k]), r['income_mono'], t))
        lm, li, lt = np.array(lm), np.array(li), np.array(lt)
        z = np.nan
        if zstats is not None:
            mu, sd = zstats[mrow['map']]
            z = float(np.nanmean((M[[idx[t] for t in TS]] - mu) / np.where(sd > 0, sd, np.nan)))
        rows.append(dict(game=key[0], side=key[1], map=mrow['map'], team=mrow['team'], cohort=mrow['cohort'], name=mrow['name'],
                         won=mrow['won'], zgap=z, lag_M=lm.mean(), lag_I=li.mean(), tempo=lt.mean(),
                         tempo_r50=lt[TS.tolist().index(50)], tempo_r100=lt[TS.tolist().index(100)], tempo_r150=lt[-1],
                         drift=lt[-1] - lt[TS.tolist().index(50)], lag_I_r150=li[-1], lag_M_r150=lm[-1]))
    return pd.DataFrame(rows)


def zstats_of(C, meta):
    zs = {}
    idx = [list(T).index(t) for t in TS]
    for m in meta['map'].unique():
        v = C['total'][(meta['map'] == m).values].values[:, idx]
        zs[m] = (np.nanmean(v, axis=0), np.nanstd(v, axis=0))
    return zs


def cmd_build():
    from tools.s1.q import connect
    c = connect('corpus')
    df = pull(c)
    C, meta = curves(df)
    ref = reference(C, meta)
    zs = zstats_of(C, meta)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(dict(ref=ref, zs=zs), OUT / 'reference.pkl')
    # sides extras for validation
    s = c.execute("select game, side, gap, opp_elo, elo, started_at from sides").df()
    X = metrics(C, meta, ref, zs).merge(s, on=['game', 'side'], how='left')
    X.to_parquet(OUT / 'field_metrics.parquet', index=False)
    print(f'built: {len(X)} side-games over {X["map"].nunique()} maps')


def auc(score, y):
    y = np.asarray(y); s = pd.Series(np.asarray(score)).rank().values
    pos = y == 1
    n1, n0 = pos.sum(), (~pos).sum()
    return (s[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def cmd_validate():
    import statsmodels.api as sm
    X = pd.read_parquet(OUT / 'field_metrics.parquet')
    X = X[X.won != 0.5]
    mets = ['zgap', 'lag_M', 'lag_I', 'tempo', 'tempo_r50', 'drift']
    sign = {'zgap': 1, 'lag_M': -1, 'lag_I': -1, 'tempo': -1, 'tempo_r50': -1, 'drift': -1}
    print('1) predicting the win (within map; higher-is-better orientation). AUC raw, and logit per within-map SD with Elo gap held')
    rows = []
    for mt in mets:
        a = np.mean([auc(sign[mt] * x[mt], x.won) for _, x in X.groupby('map') if x.won.nunique() == 2])
        x = X.dropna(subset=[mt, 'gap']).copy()
        x['z'] = x.groupby('map')[mt].transform(lambda v: (v - v.mean()) / v.std()) * sign[mt]
        x['g'] = x.gap.clip(-800, 800) / 100
        f = sm.Logit(x.won, sm.add_constant(x[['z', 'g']])).fit(disp=0)
        rows.append(dict(metric=mt, within_map_auc=a, logit_per_sd_elo_held=f.params['z']))
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    print('\n2) team-level validity: team mean (maps weighted equally) vs current Elo; split-half reliability of team means')
    t = pd.read_parquet(S1 / 'corpus' / 'teams.parquet')[['team', 'elo_now', 'crank', 'name']]
    X['half'] = X.game.astype(str).str[-1].astype(int) % 2
    rows = []
    for mt in mets:
        tm = X.groupby(['team', 'map'])[mt].mean().groupby('team').mean()
        n = X.groupby('team').size()
        tm = tm[n[n >= 60].index]
        j = pd.concat([tm.rename('m'), t.set_index('team').elo_now], axis=1).dropna()
        h = X.groupby(['team', 'half'])[mt].mean().unstack().loc[tm.index].dropna()
        rows.append(dict(metric=mt, teams=len(j), spearman_vs_elo=j.m.corr(j.elo_now, method='spearman') * sign[mt],
                         split_half_r=h[0].corr(h[1])))
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    print('\n3) noise: SD of the per-side-game metric within team x map (the unit a panel measures); side-games for SE = 1 round')
    rows = []
    for mt in mets:
        r = X.groupby(['team', 'map'])[mt].transform(lambda v: v - v.mean())
        sd = r.std()
        rows.append(dict(metric=mt, within_team_map_sd=sd, side_games_for_se_1=sd ** 2))
    print(pd.DataFrame(rows).round(2).to_string(index=False))
    print('\n4) cohort values (median over side-games of the per-map medians)')
    X['grp'] = X.cohort.where(X.cohort.isin(['top10', 'r11_30', 'r31_50', 'us']))
    X.loc[(X.cohort == 'us') & (X.started_at >= pd.Timestamp('2026-09-29 06:00', tz='UTC')), 'grp'] = 'us_now'
    print(X.dropna(subset=['grp']).groupby(['grp', 'map'])[mets].median().groupby('grp').mean().round(2).to_string())
    print('\nper map, tempo (rounds behind the top-10 median income curve, net of excess loss):')
    print(X.dropna(subset=['grp']).pivot_table(index='map', columns='grp', values='tempo', aggfunc='median').round(1).to_string())


def cmd_score(db, where):
    from tools.s1.q import connect
    c = connect(db)
    R = pd.read_pickle(OUT / 'reference.pkl')
    view = 'series' if db == 'corpus' else 'l_series'
    df = pull(c, view, where, sample=False)
    C, meta = curves(df)
    X = metrics(C, meta, R['ref'], R['zs'])
    print(X.groupby(['name', 'map'])[['tempo', 'tempo_r50', 'drift', 'lag_I', 'lag_M']].median().round(1).to_string())
    per_map = X.groupby(['name', 'map']).tempo.agg(['median', 'size'])
    print(per_map.groupby('name')['median'].mean().round(2).rename('tempo (maps equal)').to_string())
    return X


def cmd_compare(cand, inc, db='local', where='', boots=2000, seed=1):
    """decision: candidate vs incumbent on the same panel. Maps with a top-10 reference use it; other maps (e.g. maps/new)
    use the incumbent's own median curves as the reference, so tempo there is 'rounds ahead of / behind the incumbent'."""
    from tools.s1.q import connect
    c = connect(db)
    R = pd.read_pickle(OUT / 'reference.pkl')
    view = 'series' if db == 'corpus' else 'l_series'
    w = f"name in ('{cand}', '{inc}')" + (f' and ({where})' if where else '')
    df = pull(c, view, w, sample=False)
    C, meta = curves(df)
    ref = dict(R['ref'])
    for m in meta['map'].unique():
        if m not in ref:        # unseen map: the incumbent is the reference
            sel = ((meta['map'] == m) & (meta['name'] == inc)).values
            r = {k: C[k][sel].median(axis=0).values for k in ('total', 'income', 'loss')}
            r['total_mono'], r['income_mono'] = np.maximum.accumulate(r['total']), np.maximum.accumulate(r['income'])
            ref[m] = r
    X = metrics(C, meta, ref)
    rng = np.random.default_rng(seed)
    rows, bs = [], []
    for m, x in X.groupby('map'):
        a, b = x[x.name == cand].tempo.values, x[x.name == inc].tempo.values
        if len(a) < 5 or len(b) < 5:
            continue
        d = np.median(a) - np.median(b)
        boot = [np.median(rng.choice(a, len(a))) - np.median(rng.choice(b, len(b))) for _ in range(boots)]
        rows.append(dict(map=m, n_cand=len(a), n_inc=len(b), cand=np.median(a), inc=np.median(b), delta=d,
                         lo=np.percentile(boot, 2.5), hi=np.percentile(boot, 97.5), reference='top10' if m in R['ref'] else 'incumbent'))
        bs.append(boot)
    T = pd.DataFrame(rows)
    if T.empty:
        print('no map has >= 5 side-games for both bots: run both on the same panel first')
        return T
    tot = np.mean(np.array(bs), axis=0)
    D, lo, hi = T.delta.mean(), np.percentile(tot, 2.5), np.percentile(tot, 97.5)
    print(T.round(1).to_string(index=False))
    worst = T.loc[T.delta.idxmax()]
    verdict = ('ACCEPT' if (D <= -DELTA and hi < 0 and (T.lo <= MAP_GUARD).all()) else
               'REJECT' if lo > 0 else 'INCONCLUSIVE (extend the panel)')
    print(f'\ntempo delta (candidate - incumbent, maps equal, rounds; negative = faster): {D:+.1f}  95% CI [{lo:+.1f}, {hi:+.1f}]')
    print(f'worst map: {worst["map"]} {worst.delta:+.1f} [{worst.lo:+.1f}, {worst.hi:+.1f}]  (guard: no map with lower bound > {MAP_GUARD:+.0f})')
    print(f'VERDICT: {verdict}   (accept rule: delta <= -{DELTA:.0f} rounds, CI upper bound < 0, map guard)')
    return T


DELTA = 3.0          # rounds: the smallest improvement worth shipping (~ +5 win points at 50 %, ~50 Elo in the field)
MAP_GUARD = 5.0      # rounds: no single map may be significantly more than 5 rounds slower


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--db', default='corpus')
    ap.add_argument('--where', default='')
    ap.add_argument('--cand', default='')
    ap.add_argument('--inc', default='')
    a = ap.parse_args()
    if a.cmd == 'compare':
        cmd_compare(a.cand, a.inc, a.db, a.where)
    else:
        {'build': cmd_build, 'validate': cmd_validate}.get(a.cmd, lambda: cmd_score(a.db, a.where))()
