"""s1 question scripts: python3 tools/s1/questions.py q1|q2|q3|q4 -> build/s1/out/<q>/ tables + figures.

Q1 map specialists (index + ladder only), Q2 map predictability (index + ladder; elimination rate from the store),
Q3 opening component breakdown (store), Q4 portals and own goals (store). Findings: docs/findings/2026-10-0x-s1-*.md.
"""
import json, sys, warnings
from pathlib import Path

ROOT = Path.cwd()
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')

S1 = ROOT / 'build' / 's1'
OUT = S1 / 'out'
FIG = ROOT / 'docs' / 'findings' / 's1-figs'
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 500)


def games(min_map_games=500):
    g = pd.read_parquet(S1 / 'corpus' / 'games.parquet')
    n = g['map'].value_counts()
    g = g[g['map'].isin(n[n >= min_map_games].index)]      # drops retired maps seen in a handful of 26 Sep games
    t = pd.read_parquet(S1 / 'corpus' / 'teams.parquet')
    return g, t


def team_view(g):
    """one row per (game, team): y = team result, gap = team elo - opp elo at game time (nearest earlier snapshot)"""
    a = g.assign(team=g.team_a, opp=g.team_b, y=g.result_a, gap=g.elo_gap, seatA=1.0)
    b = g.assign(team=g.team_b, opp=g.team_a, y=1 - g.result_a, gap=-g.elo_gap, seatA=0.0)
    v = pd.concat([a, b])[['game', 'team', 'opp', 'map', 'y', 'gap', 'seatA', 'ranked', 'snap_before', 'started_at']]
    return v[v.gap.notna() & (v.y != 0.5)]


def q1(min_games=40):
    import statsmodels.api as sm
    from scipy.stats import chi2
    g, t = games()
    top = json.loads((S1 / 'corpus' / 'cohort.json').read_text())['top50'] + [7]
    names = dict(zip(t.team, t.name)); crank = dict(zip(t.team, t.crank))
    v = team_view(g)
    maps = sorted(v['map'].unique())
    rows, eff = [], []
    import statsmodels.api as sm2
    vv0 = v.assign(g100=v.gap.clip(-800, 800) / 100)
    beta_field = sm2.Logit(vv0.y, sm2.add_constant(vv0[['g100', 'seatA']])).fit(disp=0).params['g100']
    print(f'field gap slope per 100 Elo (all games, seat held): {beta_field:.3f} (Elo formula: 0.576)')
    gid = v.game.astype(int)
    tmed = v.groupby('team').started_at.transform('median')
    for sens, vv in (('all', v), ('snap_before', v[v.snap_before]), ('ranked', v[v.ranked]),
                     ('half_odd', v[gid % 2 == 1]), ('half_even', v[gid % 2 == 0]),
                     ('early', v[v.started_at <= tmed]), ('late', v[v.started_at > tmed])):
        for tid in map(str, top):
            d = vv[vv.team == tid].copy()
            if len(d) < min_games or d.y.nunique() < 2:
                continue
            d['g100'] = d.gap.clip(-800, 800) / 100
            X0 = sm.add_constant(d[['g100', 'seatA']])
            M = pd.get_dummies(d['map']).reindex(columns=maps, fill_value=0).astype(float)
            M = M.loc[:, M.sum() > 0]
            # sum-to-zero map effects: deviation of each map from the team's own average map
            base = M.columns[-1]
            Z = M.drop(columns=base).sub(M[base], axis=0)
            X1 = pd.concat([X0, Z], axis=1)
            try:
                f0 = sm.Logit(d.y, X0).fit(disp=0)
                f1 = sm.Logit(d.y, X1).fit(disp=0, method='bfgs', maxiter=500)
            except Exception:
                continue
            lr = 2 * (f1.llf - f0.llf)
            df = Z.shape[1]
            p = chi2.sf(lr, df)
            b = f1.params['g100']
            try:
                cov = f1.cov_params()
                if not np.isfinite(cov.values).all():
                    continue
            except Exception:
                continue          # singular fit (separation on a map with few games): the team is skipped
            me = {m: (f1.params[m], np.sqrt(cov.loc[m, m])) for m in Z.columns}
            # the base map's effect is minus the sum of the others
            L = np.zeros(len(f1.params)); idx = list(f1.params.index)
            for m in Z.columns:
                L[idx.index(m)] = -1
            me[base] = (float(L @ f1.params.values), float(np.sqrt(L @ cov.values @ L)))
            rows.append(dict(sample=sens, team=tid, name=names.get(tid), crank=crank.get(tid), n=len(d), win=d.y.mean(),
                             beta_gap100=f0.params['g100'], beta_gap100_fe=b, lr=lr, df=df, p=p,
                             max_abs_map_elo=max(abs(x[0]) for x in me.values()) / b * 100 if b > 0 else np.nan))
            nm = d.groupby('map').size()
            for m, (e, se) in me.items():
                eff.append(dict(sample=sens, team=tid, name=names.get(tid), crank=crank.get(tid), map=m, n=int(nm.get(m, 0)),
                                logit=e, se=se, lo=e - 1.96 * se, hi=e + 1.96 * se, elo_equiv_field=e / beta_field * 100,
                                elo_equiv=e / b * 100 if b > 0 else np.nan, elo_lo=(e - 1.96 * se) / b * 100 if b > 0 else np.nan,
                                elo_hi=(e + 1.96 * se) / b * 100 if b > 0 else np.nan, win_on_map=d[d['map'] == m].y.mean()))
    R = pd.DataFrame(rows)
    E = pd.DataFrame(eff)
    # Benjamini-Hochberg within each sample
    for s in R['sample'].unique():
        m = R['sample'] == s
        p = R.loc[m, 'p'].values
        o = np.argsort(p); q = np.empty_like(p); n = len(p)
        q[o] = np.minimum.accumulate((p[o] * n / (np.arange(n) + 1))[::-1])[::-1]
        R.loc[m, 'q_bh'] = np.minimum(q, 1)
    (OUT / 'q1').mkdir(parents=True, exist_ok=True)
    R.to_csv(OUT / 'q1' / 'teams.csv', index=False)
    E.to_csv(OUT / 'q1' / 'map_effects.csv', index=False)
    # reliability: do map effects replicate across disjoint halves of each team's games?
    for x, y in (('half_odd', 'half_even'), ('early', 'late')):
        A = E[E['sample'] == x].set_index(['team', 'map']).logit
        B = E[E['sample'] == y].set_index(['team', 'map']).logit
        j = pd.concat([A.rename('a'), B.rename('b')], axis=1).dropna()
        per = j.groupby(level=0).apply(lambda d: d.a.corr(d.b))
        print(f'split {x}/{y}: pooled r = {j.a.corr(j.b):.3f} over {len(j)} team-maps; median per-team r = {per.median():.3f}; '
              f'share of teams r>0: {(per > 0).mean():.2f}')
    a = R[R['sample'] == 'all'].sort_values('crank')
    print(a[['team', 'name', 'crank', 'n', 'win', 'beta_gap100', 'lr', 'df', 'p', 'q_bh', 'max_abs_map_elo']].round(4).to_string(index=False))
    sig = a[a.q_bh < 0.05].team
    e = E[(E['sample'] == 'all') & E.team.isin(sig) & ((E.lo > 0) | (E.hi < 0))].sort_values(['crank', 'elo_equiv'])
    print('\nsignificant map effects (team LR q<0.05 and map CI excludes 0), gap-equivalent Elo:')
    print(e[['name', 'crank', 'map', 'n', 'win_on_map', 'elo_equiv_field', 'elo_equiv', 'elo_lo', 'elo_hi']].round(1).to_string(index=False))
    # per-map summary: how many teams are significantly strong / weak there
    es = E[(E['sample'] == 'all') & E.team.isin(sig)]
    print(es.assign(pos=(es.lo > 0), neg=(es.hi < 0)).groupby('map').agg(strong=('pos', 'sum'), weak=('neg', 'sum'),
          sd_elo=('elo_equiv_field', 'std')).round(1).to_string())
    print('\nteam 7 (us):'); print(E[(E['sample'] == 'all') & (E.team == '7')][['map', 'n', 'win_on_map', 'elo_equiv_field', 'lo', 'hi']].round(2).to_string(index=False))
    for s in ('snap_before', 'ranked'):
        b = R[R['sample'] == s]
        print(f'\nsensitivity {s}: teams tested {len(b)}, q<0.05: {int((b.q_bh < 0.05).sum())}; teams also q<0.05 in all: '
              f'{sorted(set(b[b.q_bh < 0.05].name) & set(a[a.q_bh < 0.05].name))}')
    # heatmap
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    H = E[E['sample'] == 'all'].assign(crank=lambda x: x.crank.fillna(99)).pivot_table(index=['crank', 'name'], columns='map', values='elo_equiv_field').sort_index()
    S = E[E['sample'] == 'all'].assign(crank=lambda x: x.crank.fillna(99)).assign(s=lambda x: (x.lo > 0) | (x.hi < 0)).pivot_table(index=['crank', 'name'], columns='map', values='s').sort_index()
    fig, ax = plt.subplots(figsize=(10, 14))
    im = ax.imshow(H.clip(-400, 400).values, cmap='RdBu', vmin=-400, vmax=400, aspect='auto')
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            v = H.values[i, j]
            if v == v:
                ax.text(j, i, f'{v:.0f}' + ('*' if S.values[i, j] else ''), ha='center', va='center', fontsize=6)
    ax.set_xticks(range(H.shape[1])); ax.set_xticklabels(H.columns, rotation=40, ha='right', fontsize=8)
    ax.set_yticks(range(H.shape[0])); ax.set_yticklabels([f'{int(c)} {n}' for c, n in H.index], fontsize=7)
    fig.colorbar(im, ax=ax, label='map effect, gap-equivalent Elo (vs team average map)', shrink=0.5)
    ax.set_title('Q1: per-team map effects (logit with elo gap + seat; * = 95% CI excludes 0)')
    fig.tight_layout(); FIG.mkdir(parents=True, exist_ok=True); fig.savefig(FIG / 'q1-map-effects.png', dpi=110)
    return R, E


def q2():
    import statsmodels.api as sm
    g, t = games()
    v = g[g.elo_gap.notna()].copy()
    v['g100'] = v.elo_gap.clip(-800, 800) / 100
    scopes = {'in_scope': v[v.in_scope], 'top50_vs_top50': None, 'all': v}
    cr = dict(zip(t.team, t.crank))
    both = v.team_a.map(cr).le(50) & v.team_b.map(cr).le(50)
    scopes['top50_vs_top50'] = v[both]
    # elimination / length of game from the store where decoded
    elim = None
    try:
        import duckdb
        con = duckdb.connect()
        elim = con.execute(f"""select game, any_value(reason) reason, any_value(R) R from read_parquet('{S1}/corpus/sides/part-*.parquet', union_by_name=true)
                               group by game""").df()
    except Exception:
        pass
    rows = []
    for sname, d0 in scopes.items():
        dn = d0[d0.result_a != 0.5]
        pooled = sm.Logit(dn.result_a, sm.add_constant(dn[['g100']])).fit(disp=0)
        for m, d in d0.groupby('map'):
            d = d[d.result_a != 0.5]
            f = sm.Logit(d.result_a, sm.add_constant(d[['g100']])).fit(disp=0)
            p = f.predict(sm.add_constant(d[['g100']]))
            pp = pooled.predict(sm.add_constant(d[['g100']]))
            base = d.result_a.mean()
            # Brier of gap-only (map-own fit), of the pooled model, and of the constant; skill = 1 - brier/brier_const
            b_own = float(((p - d.result_a) ** 2).mean()); b_const = float(((base - d.result_a) ** 2).mean())
            r = dict(scope=sname, map=m, n=len(d), draws=int((d0[d0['map'] == m].result_a == 0.5).sum()), seatA_win=base,
                     slope100=f.params['g100'], slope_se=f.bse['g100'], intercept=f.params['const'],
                     brier=b_own, brier_pooled=float(((pp - d.result_a) ** 2).mean()), brier_const=b_const, skill=1 - b_own / b_const,
                     upset_rate=float(((d.elo_gap > 100) & (d.result_a == 0) | (d.elo_gap < -100) & (d.result_a == 1)).sum() /
                                      max(1, (d.elo_gap.abs() > 100).sum())))
            if elim is not None:
                e = elim[elim.game.isin(d.game)]
                r.update(n_decoded=len(e), elim_rate=(e.reason == 'elimination').mean() if len(e) else np.nan,
                         tie_rate=(e.reason == 'tie').mean() if len(e) else np.nan, median_R=e.R.median() if len(e) else np.nan)
            rows.append(r)
        rows.append(dict(scope=sname, map='POOLED', n=len(dn), slope100=pooled.params['g100'], slope_se=pooled.bse['g100']))
    R = pd.DataFrame(rows)
    (OUT / 'q2').mkdir(parents=True, exist_ok=True)
    R.to_csv(OUT / 'q2' / 'maps.csv', index=False)
    for s in scopes:
        print(f'\n== {s}')
        print(R[R.scope == s].sort_values('slope100').drop(columns='scope').round(4).to_string(index=False))
    return R


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    {'q1': q1, 'q2': q2}[sys.argv[1]]()
