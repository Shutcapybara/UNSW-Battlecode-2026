"""S1 strategy atlas: one behaviour space for local bots and live team-versions, strength kept separate.

  python3 tools/s1/atlas_analysis.py [--source panel|existing] [--k 0]

Local bots: side-games from the fixed overnight panel (run 'atlas-panel'; --source existing uses the decoded experiment
replays instead, whose opponents vary). Live: corpus team-versions = team x UTC day with >= 40 side-games on >= 6 maps.
Behaviour vector = mean field z-score per map of bot-owned rates and shares (FEATS), then the mean over maps (maps count
equally). Strength: local = Bradley-Terry on the panel results; both = tempo (rounds behind the frozen top-ten curves,
tools/s1/tempo_gate.py definition); live also has Elo at game time.
Outputs: build/atlas/out/*.csv, docs/findings/s1-figs/atlas/*.png, and a printed summary used by the findings doc.
"""
import argparse, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
os.environ.setdefault('S1_FREEZE', '1')
import numpy as np
import pandas as pd

ATLAS = ROOT / 'build' / 'atlas'
OUT = ATLAS / 'out'
FIG = ROOT / 'docs' / 'findings' / 's1-figs' / 'atlas'
PANEL = ['fenrir-v20-crowded-resource-revalue', 'gavroche-v66-supported-safe', 'hunter-v20-portal-scouts',
         'tyr-v12-devil-scout-tiebreak', 'sinbad-v07-divecap', 'kraken-v04-eval']
F150 = ['pearls_per_dt', 'bed_pearls_per_dt', 'corpse_pearl_share', 'births_per_dt', 'own_goals_per1k', 'transits_per_dt',
        'rays_per_dt', 'idle_share', 'turnaround_share', 'disp_per_turn', 'clustered_share', 'nn_dist_mean', 'swarm_rg',
        'enemy_head_dist_mean', 'contact_share', 'top1_share', 'mean_len', 'kelp_adj_mean', 'reach_le8_share',
        'steps_per_pearl', 'transit_died3_share']
F50 = ['pearls_per_dt', 'births_per_dt', 'disp_per_turn', 'transits_per_dt', 'clustered_share']
FS = ['death_suicide_per1k', 'death_invalid_per1k', 'child_len_le3_share', 'sprint_share', 'first_split', 'first_pearl',
      'rays_toward_enemy_share', 'ray_refracted_share', 'seen50']
# outcome-flavoured columns kept out of the behaviour vector (they measure how well, not how)
STRENGTHY = {'pearls_per_dt', 'bed_pearls_per_dt', 'pearls_per_dt_r50', 'mean_len', 'steps_per_pearl'}
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 200)


def sel(cols, suffix=''):
    return ', '.join('avg("%s") as "%s%s"' % (c, c, suffix) for c in cols)


def side_features(c, view_s, view_sides, where_s, where_sides, key):
    """per (key, map) means of the behaviour features; `key` is a SQL expression naming the unit"""
    hs = set(c.execute(f'describe {view_s}').df().column_name)
    f150, f50 = [x for x in F150 if x in hs], [x for x in F50 if x in hs]
    a = c.execute(f"select {key} as unit, map, count(*) as n, {sel(f150)} from {view_s} where round = 150 and {where_s} group by 1, 2").df()
    b = c.execute(f"select {key} as unit, map, {sel(f50, '_r50')} from {view_s} where round = 50 and {where_s} group by 1, 2").df()
    hd = set(c.execute(f'describe {view_sides}').df().column_name)
    fs = [x for x in FS if x in hd]
    d = c.execute(f"select {key} as unit, map, {sel(fs)} from {view_sides} where {where_sides} group by 1, 2").df()
    return a.merge(b, on=['unit', 'map'], how='left').merge(d, on=['unit', 'map'], how='left')


def pool(V, min_n=10):
    feats = [x for x in V.columns if x not in ('unit', 'map', 'n')]
    g = V.groupby('unit')
    P = g[feats].mean()                       # each map counts equally
    P['n'] = g.n.sum()
    P['maps'] = g.size()
    return P[P.n >= min_n], feats


def bt(rows, ridge=0.5):
    from scipy.optimize import minimize
    r = rows[rows.winner.isin(['A', 'B'])]
    bots = pd.Index(sorted(set(r.a) | set(r.b)))
    a, b = bots.get_indexer(r.a), bots.get_indexer(r.b)
    y = (r.winner == 'A').values.astype(float)
    n = len(bots)

    def f(x):
        s, c0 = x[:n], x[n]
        z = s[a] - s[b] + c0
        e = 1 / (1 + np.exp(-z)) - y
        g = np.bincount(a, e, minlength=n) - np.bincount(b, e, minlength=n) + ridge * s
        return np.sum(np.logaddexp(0, z) - y * z) + 0.5 * ridge * np.sum(s * s), np.concatenate([g, [e.sum()]])
    x = minimize(f, np.zeros(n + 1), jac=True, method='L-BFGS-B').x
    games = pd.concat([r.a, r.b]).value_counts()
    return pd.DataFrame(dict(bot=bots, panel_elo=1500 + x[:n] * 400 / np.log(10), panel_games=games.reindex(bots).values,
                             panel_win=[((r.a == bb) & (r.winner == 'A') | (r.b == bb) & (r.winner == 'B')).sum() / games[bb] for bb in bots]))


def tempo_units(c, view, where, key, max_per_unit=80):
    """tempo per side-game (tempo_gate definition), averaged per unit (maps equal)"""
    from tools.s1.tempo_gate import tempo, REF
    ref = json.loads(Path(REF).read_text())['maps']
    df = c.execute(f"""select {key} as unit, game, side, map, round,
            coalesce(c_eats_bed, 0) + coalesce(c_eats_enemy_corpse, 0) as income,
            coalesce(c_length_lost, 0) - coalesce(c_eats_ally_corpse, 0) as loss
            from {view} where round % 5 = 0 and round <= 150 and {where}""").df()
    df = df[df['map'].isin(ref)]
    keys = df[['unit', 'game', 'side']].drop_duplicates()
    keys = keys.groupby('unit').head(max_per_unit)
    df = df.merge(keys, on=['unit', 'game', 'side'])
    out = []
    for (u, g, s, m), x in df.sort_values('round').groupby(['unit', 'game', 'side', 'map']):
        if len(x) < 31:
            continue
        out.append(dict(unit=u, map=m, tempo=tempo(dict(income=x.income.values, loss=x.loss.values), ref[m])))
    T = pd.DataFrame(out)
    return T.groupby(['unit', 'map']).tempo.median().groupby('unit').mean().rename('tempo')


def pca(X, k=8):
    mu = X.mean(0)
    U, S, Vt = np.linalg.svd(X - mu, full_matrices=False)
    ev = S ** 2 / np.sum(S ** 2)
    return (X - mu) @ Vt[:k].T, Vt[:k], ev[:k]


def kmeans(X, k, seed=0, restarts=20):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(200):
            lab = ((X[:, None] - C[None]) ** 2).sum(-1).argmin(1)
            C2 = np.array([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
            if np.allclose(C2, C):
                break
            C = C2
        w = ((X - C[lab]) ** 2).sum()
        if best is None or w < best[0]:
            best = (w, lab, C)
    return best[1], best[2], best[0]


def silhouette(X, lab):
    D = np.sqrt(((X[:, None] - X[None]) ** 2).sum(-1))
    s = []
    for i in range(len(X)):
        same = lab == lab[i]
        if same.sum() <= 1:
            s.append(0)
            continue
        a = D[i, same].sum() / (same.sum() - 1)
        b = min(D[i, lab == j].mean() for j in set(lab) if j != lab[i])
        s.append((b - a) / max(a, b))
    return float(np.mean(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default='panel', choices=['panel', 'existing'])
    ap.add_argument('--stage', default='all', choices=['all', 'local', 'live', 'livetempo', 'report'],
                    help='local / live / livetempo compute and cache one part (each fits a short shell call); report uses the caches')
    ap.add_argument('--refresh', action='store_true', help='recompute cached parts')
    ap.add_argument('--k', type=int, default=0, help='niches (0 = choose by silhouette, 6..14)')
    ap.add_argument('--live-min', type=int, default=40)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    run = 'atlas-panel' if a.source == 'panel' else 'atlas-existing'
    cl, cv, ct = OUT / f'cache_local_{a.source}.pkl', OUT / 'cache_live.pkl', OUT / 'cache_live_tempo.pkl'
    state = {}

    def con():
        if 'c' not in state:
            from tools.s1.q import connect
            c = connect('corpus')
            c.execute("""create temp table lv as select game, side, team, cohort, crank, name,
                         team || '@' || strftime(started_at, '%m-%d') as unit, elo, won
                         from c_sides where cohort in ('top10', 'r11_30', 'r31_50', 'us') and started_at is not null""")
            c.execute("create temp view lvs as select s.*, lv.unit from c_series_z s join lv using (game, side)")
            c.execute("create temp view lvd as select d.*, lv.unit from c_sides_z d join lv using (game, side)")
            state['c'] = c
        return state['c']
    if a.stage in ('all', 'local') and (a.refresh or not cl.exists()):
        Vl = side_features(con(), 'l_series_z', 'l_sides_z', f"run = '{run}'", f"run = '{run}'", 'name')
        Tl = tempo_units(con(), 'l_series', f"run = '{run}'", 'name')
        pd.to_pickle((Vl, Tl), cl)
        print('cached local', len(Vl))
    if a.stage in ('all', 'live') and (a.refresh or not cv.exists()):
        Vv = side_features(con(), 'lvs', 'lvd', 'true', 'true', 'unit')
        meta = con().execute("select unit, any_value(team) as team, any_value(name) as name, any_value(cohort) as cohort, "
                             "any_value(crank) as crank, avg(elo) as elo, avg(won) as win, count(*) as games from lv group by 1").df().set_index('unit')
        pd.to_pickle((Vv, meta), cv)
        print('cached live', len(Vv))
    if a.stage in ('all', 'livetempo') and (a.refresh or not ct.exists()):
        c = con()
        c.execute("create temp table lvt as select game, side, unit from (select game, side, unit, row_number() over (partition by unit order by hash(game)) k from lv) where k <= 60")
        c.execute("create temp view lvr2 as select s.*, lvt.unit from c_series s join lvt using (game, side)")
        Tv = tempo_units(c, 'lvr2', 'true', 'unit', max_per_unit=60)
        pd.to_pickle(Tv, ct)
        print('cached live tempo', len(Tv))
    if a.stage not in ('all', 'report'):
        return
    Vl, Tl = pd.read_pickle(cl)
    Vv, meta = pd.read_pickle(cv)
    Tv = pd.read_pickle(ct)
    Pl, feats = pool(Vl)
    if a.source == 'panel':
        rows = pd.DataFrame([json.loads(l) for l in open(ATLAS / 'panel' / 'index.jsonl')])
        S = bt(rows).set_index('bot')
    else:
        S = pd.read_parquet(ATLAS / 'bots_existing.parquet').set_index('bot').rename(columns={'bt_elo': 'panel_elo', 'bt_games': 'panel_games'})
    Pl = Pl.join(S[['panel_elo', 'panel_games']], how='left').join(Tl, how='left')
    Pl['world'] = 'local'
    Pv, _ = pool(Vv, min_n=a.live_min)
    Pv = Pv[Pv.maps >= 6]
    Pv = Pv.join(meta, how='left').join(Tv, how='left')
    Pv['world'] = 'live'
    # ---------------- joint behaviour space
    beh = [f for f in feats if f not in STRENGTHY and f in Pv.columns]
    J = pd.concat([Pl[beh + ['world']], Pv[beh + ['world']]])
    X = J[beh].astype(float).fillna(0).clip(-4, 4).values
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
    Z, L, ev = pca(Xs, 8)
    load = pd.DataFrame(L.T, index=beh, columns=[f'PC{i + 1}' for i in range(L.shape[0])])
    if a.k:
        k = a.k
    else:
        best = None
        for kk in range(6, 15):
            lab_, _, _ = kmeans(Z, kk)
            s_ = silhouette(Z, lab_)
            if best is None or s_ > best[0]:
                best = (s_, kk)
        k = best[1]
    lab, C, _ = kmeans(Z, k)
    J = J.assign(niche=lab, **{f'PC{i + 1}': Z[:, i] for i in range(Z.shape[1])})
    J.index.name = 'unit'
    Lx = J[J.world == 'local'].join(Pl[['panel_elo', 'panel_games', 'tempo', 'n']])
    Vx = J[J.world == 'live'].join(Pv[['team', 'name', 'cohort', 'crank', 'elo', 'win', 'games', 'tempo']])
    # novelty among local bots (mean distance to 5 nearest local neighbours in PCA space)
    zl = Lx[[f'PC{i + 1}' for i in range(Z.shape[1])]].values
    D = np.sqrt(((zl[:, None] - zl[None]) ** 2).sum(-1))
    np.fill_diagonal(D, np.inf)
    Lx['novelty'] = np.sort(D, 1)[:, :5].mean(1)
    # ---------------- strength vs behaviour, in both worlds
    rows = []
    for col in [f'PC{i + 1}' for i in range(Z.shape[1])] + beh:
        src = J[col] if col.startswith('PC') else J[col]
        r = dict(feature=col,
                 local_elo=Lx[col].corr(Lx.panel_elo, method='spearman') if col.startswith('PC') else Pl[col].corr(Pl.panel_elo, method='spearman'),
                 local_tempo=-(Lx[col].corr(Lx.tempo, method='spearman') if col.startswith('PC') else Pl[col].corr(Pl.tempo, method='spearman')),
                 live_elo=Vx[col].corr(Vx.elo, method='spearman') if col.startswith('PC') else Pv[col].corr(Pv.elo, method='spearman'),
                 live_tempo=-(Vx[col].corr(Vx.tempo, method='spearman') if col.startswith('PC') else Pv[col].corr(Pv.tempo, method='spearman')))
        rows.append(r)
    SB = pd.DataFrame(rows)
    SB['sign_agree'] = np.sign(SB.local_elo) == np.sign(SB.live_elo)
    # ---------------- niches
    nrows = []
    for j in range(k):
        l_, v_ = Lx[Lx.niche == j], Vx[Vx.niche == j]
        topl = l_.sort_values('panel_elo', ascending=False).head(3)
        topv = v_.sort_values('elo', ascending=False).head(4)
        nrows.append(dict(niche=j, local=len(l_), live=len(v_), live_top10=int((v_.cohort == 'top10').sum()), live_us=int((v_.cohort == 'us').sum()),
                          local_best_elo=l_.panel_elo.max(), local_median_tempo=l_.tempo.median(), live_median_elo=v_.elo.median(),
                          live_best_elo=v_.elo.max(), live_median_tempo=v_.tempo.median(),
                          local_top=', '.join(f'{u} ({e:.0f})' for u, e in zip(topl.index, topl.panel_elo)),
                          live_top=', '.join(f'{nm} {u.split("@")[1]} ({e:.0f})' for u, nm, e in zip(topv.index, topv['name'].fillna('?'), topv.elo))))
    NT = pd.DataFrame(nrows)
    # ---------------- anchors: nearest local bots to each team-7 live day
    anc = []
    for u, row in Vx[Vx.cohort == 'us'].iterrows():
        z = row[[f'PC{i + 1}' for i in range(Z.shape[1])]].values.astype(float)
        d = np.sqrt(((zl - z) ** 2).sum(1))
        o = np.argsort(d)[:5]
        anc.append(dict(live_unit=u, niche=row.niche, nearest=', '.join(f'{Lx.index[i]} ({d[i]:.2f})' for i in o)))
    AN = pd.DataFrame(anc)
    # ---------------- save
    load.to_csv(OUT / 'loadings.csv')
    Lx.to_csv(OUT / 'local_bots.csv')
    Vx.to_csv(OUT / 'live_versions.csv')
    SB.to_csv(OUT / 'strength_vs_behaviour.csv', index=False)
    NT.to_csv(OUT / 'niches.csv', index=False)
    AN.to_csv(OUT / 'anchors.csv', index=False)
    print(f'source {a.source}: {len(Lx)} local bots, {len(Vx)} live team-versions, {len(beh)} behaviour features, k={k}')
    print('variance explained:', np.round(ev, 3).tolist())
    for i in range(4):
        pc = f'PC{i + 1}'
        s_ = load[pc].sort_values()
        print(f'{pc}: - ' + ', '.join(f'{x} {v:+.2f}' for x, v in s_.head(4).items()) + '   | + ' + ', '.join(f'{x} {v:+.2f}' for x, v in s_.tail(4)[::-1].items()))
    print('\nstrength vs behaviour (Spearman; tempo sign flipped so + = faster):')
    print(SB.round(2).head(8).to_string(index=False))
    print('\nfeatures most tied to strength in BOTH worlds:')
    SBf = SB[~SB.feature.str.startswith('PC')].assign(both=lambda d: np.minimum(d.local_elo.abs(), d.live_elo.abs()) * np.sign(d.local_elo) * d.sign_agree)
    print(SBf.sort_values('both', key=lambda s: -s.abs()).round(2).head(12).to_string(index=False))
    print('\nniches:'); print(NT.round(1).to_string(index=False))
    print('\nanchors (team-7 live days -> nearest local bots):'); print(AN.to_string(index=False))
    figures(Lx, Vx, C, ev)


def figures(Lx, Vx, C, ev):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
    for ax, (x, y) in zip(axes, (('PC1', 'PC2'), ('PC3', 'PC4'))):
        o = Vx[Vx.cohort != 'top10']
        ax.scatter(o[x], o[y], s=14, c='#bbbbbb', label='live r11-50', alpha=0.7)
        t = Vx[Vx.cohort == 'top10']
        ax.scatter(t[x], t[y], s=40, c='#1f5fa8', label='live top 10', alpha=0.85, edgecolor='white', lw=0.4)
        u = Vx[Vx.cohort == 'us']
        ax.scatter(u[x], u[y], s=70, c='#d1495b', marker='*', label='live us (team 7)')
        sc = ax.scatter(Lx[x], Lx[y], s=16, c=Lx.panel_elo, cmap='viridis', marker='^', label='local bots (colour = strength)', alpha=0.85)
        for j, cc in enumerate(C):
            ax.annotate(str(j), (cc[int(x[2:]) - 1], cc[int(y[2:]) - 1]), fontsize=11, weight='bold', color='black')
        ax.set_xlabel(f'{x} ({ev[int(x[2:]) - 1]:.0%})'); ax.set_ylabel(f'{y} ({ev[int(y[2:]) - 1]:.0%})')
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8, loc='best')
    fig.colorbar(sc, ax=axes[1], label='local strength (panel Elo)')
    fig.suptitle('Strategy atlas: local bots and live team-versions in one behaviour space (numbers = niche centres)')
    fig.tight_layout(); fig.savefig(FIG / 'atlas-pca.png', dpi=90); plt.close(fig)


if __name__ == '__main__':
    main()
