"""Hinata R1 — V0: a GBT value model on Φ's features plus queen terms, per regime and checkpoint.

  python3 tools/hinata/v0.py dry   [--era post-m2]            # coverage only: rows/games per map x checkpoint, no outcomes read
  python3 tools/hinata/v0.py smoke                             # plumbing on maps outside LIVE_MAPS_M2 (pre era; no queen)
  python3 tools/hinata/v0.py fit   --splits docs/learning/splits/<manifest>.json [--era post-m2] [--out build/hinata/v0]
  python3 tools/hinata/v0.py confirm --splits ... --model build/hinata/v0/<run>   # ONE-SHOT held-out-map score (frozen)

States: checkpoint rows of games still running at that round (ended rows dropped; --include-ended for Φ-table
comparability only).
Label: games.result_a (server verdict; draws dropped), per side (B = 1 − A).
Features (opponent-relative, map-free; Φ(us) = 1 − Φ(them) is enforced by mirror averaging):
  Φ's six:  total_share, units_share, longest_rel, pearls_share, territory_share, deaths_share
  queen:    q_alive_own, q_alive_opp, q_len_rel (queen length own vs opp; dead = 0), q_vs_longest_opp
            (own queen length relative to the opponent's longest dragon: the queen→longest tiebreak chain)
Regime (diagnostic, NOT deployable as-is): Chongqing C7-03 RL-share classes — A = elimination (7 maps),
B+C+D+E = round-limit (10 maps). A structural regime classifier is a separate rung item.
Validation: leave-one-map-out over TRAINING maps only (held-out maps from the frozen manifest are never loaded by
`fit`), Φ logistic refit on identical folds as the baseline, both scored on side-A rows (one row per game).
Gate (P-hinata-01, frozen before any outcome is read): per regime x checkpoint x map_era, AUC(V0) ≥ AUC(Φ);
round-limit r50 AUC ≥ 0.66; calibration slope in [0.9, 1.1] from r25 on.
"""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path.cwd()
S1 = ROOT / 'build' / 's1' / 'corpus'
CPS = (10, 25, 50, 100, 150, 250, 400)
QCPS = (25, 50, 100, 150, 250, 400)          # q_len@k exists for these
POOL = ('Schooltime', 'Portals', 'Slithery Fight', 'Queen Of Spades', 'Default', 'Trophy', 'Prisoners Dilemma',
        'Autarky', 'Devil', 'Trauma', 'Australia', 'Islands', 'Around UNSW', 'Maze', 'weakhold', 'Stripes',
        'Tower Defense')
ELIM_M2 = ('Devil', 'Trophy', 'Stripes', 'Tower Defense', 'Queen Of Spades', 'Default', 'Autarky')   # C7-03 class A
RL_POST = ('Portals', 'Trauma', 'Slithery Fight', 'Schooltime')                                       # Antioch, post era
PHI = ['total_share', 'units_share', 'longest_rel', 'pearls_share', 'territory_share', 'deaths_share']
QUEEN = ['q_alive_own', 'q_alive_opp', 'q_len_rel', 'q_vs_longest_opp']
FEATS = PHI + QUEEN
LQ = PHI + ['q_alive_c', 'q_len_c']          # P-hinata-02: antisymmetric queen terms for the no-intercept logit
MODEL = 'gbt'                                 # set from --model-class


def prep_lq(x):
    x = x.copy()
    x['q_alive_c'] = ((x.q_alive_own - x.q_alive_opp) / 2 + 0.5).fillna(0.5)
    x['q_len_c'] = x.q_len_rel.fillna(0.5)
    return x
GBT = dict(n_estimators=300, learning_rate=0.03, num_leaves=15, min_child_samples=40, subsample=0.8,
           subsample_freq=1, colsample_bytree=0.9, reg_lambda=1.0, verbose=-1, n_jobs=2)


def regime(era, m):
    if era == 'post-m2':
        return 'elim' if m in ELIM_M2 else 'rl'
    return 'rl' if m in RL_POST else 'elim'


def load(eras, maps=None, exclude=(), include_ended=False):
    """Both sides, checkpoint rows, with queen state at the checkpoint. Held-out maps are filtered in SQL."""
    con = duckdb.connect(); con.execute('set threads to 3')
    q = lambda xs: ','.join("'" + x.replace("'", "''") + "'" for x in xs)
    wm = f"and map in ({q(maps)})" if maps else ''
    wx = f"and map not in ({q(exclude)})" if exclude else ''
    qlen = ', '.join(f'"q_len@{k}" as ql{k}' for k in QCPS)
    sql = f"""
    with g as (select game, map, map_era, ranked, result_a, started_at, series_id from read_parquet('{S1}/games.parquet')
               where in_scope and result_a in (0, 1) and map_era in ({q(eras)}) {wm} {wx}),
         s as (select game, side, round, total, opp_total, units, opp_units, longest, opp_longest, c_eats, opp_c_eats,
                      territory, opp_territory, c_deaths, opp_c_deaths, ended
               from read_parquet('{S1}/series/part-*.parquet', union_by_name=true)
               where round in ({','.join(map(str, CPS))}) and game in (select game from g) {'' if include_ended else 'and coalesce(ended, 0) = 0'}),
         q as (select game, side, any_value(q_death_round) as qd, {', '.join(f'any_value(ql{k}) as ql{k}' for k in QCPS)}
               from (select game, side, q_death_round, {qlen}
                     from read_parquet('{S1}/sides/part-*.parquet', union_by_name=true) where game in (select game from g))
               group by 1, 2)
    select s.*, g.map, g.map_era, g.ranked, g.series_id, g.started_at,
           case when s.side = 'A' then g.result_a else 1 - g.result_a end as y,
           qo.qd as qd_own, qp.qd as qd_opp,
           {', '.join(f'qo.ql{k} as ql{k}_own, qp.ql{k} as ql{k}_opp' for k in QCPS)}
    from s join g using (game)
    left join q qo on qo.game = s.game and qo.side = s.side
    left join q qp on qp.game = s.game and qp.side <> s.side"""
    d = con.execute(sql).df().drop_duplicates(['game', 'side', 'round']).reset_index(drop=True)
    sh = lambda a, b: np.where((a + b) > 0, a / (a + b).replace(0, np.nan), 0.5)
    d['total_share'] = sh(d.total, d.opp_total)
    d['units_share'] = sh(d.units, d.opp_units)
    mx = np.maximum(d.longest, d.opp_longest).replace(0, np.nan)
    d['longest_rel'] = ((d.longest - d.opp_longest) / mx).fillna(0) / 2 + 0.5
    d['pearls_share'] = sh(d.c_eats, d.opp_c_eats)
    d['territory_share'] = sh(d.territory.fillna(0), d.opp_territory.fillna(0))
    d['deaths_share'] = sh(d.c_deaths, d.opp_c_deaths)
    has_q = d.map_era.isin(['post', 'post-m2'])               # queen rule exists from 1.2.3 on
    alive = lambda qd: np.where(qd.isna() | (qd > d['round']), 1.0, 0.0)
    d['q_alive_own'] = np.where(has_q, alive(d.qd_own), np.nan)
    d['q_alive_opp'] = np.where(has_q, alive(d.qd_opp), np.nan)
    lo, lp = np.full(len(d), np.nan), np.full(len(d), np.nan)
    for k in QCPS:
        m = (d['round'] == k).to_numpy()
        lo[m], lp[m] = d.loc[m, f'ql{k}_own'], d.loc[m, f'ql{k}_opp']
    lo = np.where(d.q_alive_own == 0, 0, lo); lp = np.where(d.q_alive_opp == 0, 0, lp)
    den = np.maximum(lo, lp); den = np.where(den > 0, den, np.nan)
    d['q_len_rel'] = np.where(np.isnan(lo) | np.isnan(lp), np.nan, np.nan_to_num((lo - lp) / den) / 2 + 0.5)
    dl = np.maximum(lo, d.opp_longest.to_numpy(float)); dl = np.where(dl > 0, dl, np.nan)
    d['q_vs_longest_opp'] = np.where(np.isnan(lo), np.nan, np.nan_to_num((lo - d.opp_longest) / dl) / 2 + 0.5)
    d['regime'] = [regime(e, m) for e, m in zip(d.map_era, d['map'])]
    return d


def mirror(X, feats):
    """The same state seen from the other side: shares -> 1 − share, own/opp queen alive swapped."""
    M = X.copy()
    for f in feats:
        if f in ('q_alive_own', 'q_alive_opp'):
            continue
        if f == 'q_vs_longest_opp':      # not exactly mirrorable without opp-queen vs own-longest; leave NaN
            M[:, feats.index(f)] = np.nan
            continue
        M[:, feats.index(f)] = 1 - X[:, feats.index(f)]
    if 'q_alive_own' in feats and 'q_alive_opp' in feats:
        i, j = feats.index('q_alive_own'), feats.index('q_alive_opp')
        M[:, i], M[:, j] = X[:, j], X[:, i]
    return M


def fit_gbt(X, y, feats):
    import lightgbm as lgb
    Xa = np.vstack([X, mirror(X, feats)]); ya = np.concatenate([y, 1 - y])
    return lgb.LGBMClassifier(**GBT).fit(Xa, ya)


def pred_gbt(m, X, feats):
    return 0.5 * (m.predict_proba(X)[:, 1] + 1 - m.predict_proba(mirror(X, feats))[:, 1])


def fit_phi(X, y):
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(C=1.0, fit_intercept=False, max_iter=1000).fit(X - 0.5, y)


def metrics(y, p):
    from sklearn.metrics import roc_auc_score, brier_score_loss
    from sklearn.linear_model import LogisticRegression
    p = np.clip(p, 1e-4, 1 - 1e-4); lo = np.log(p / (1 - p))
    two = len(set(y)) > 1
    return dict(auc=roc_auc_score(y, p) if two else np.nan, brier=brier_score_loss(y, p),
                slope=LogisticRegression(C=1e6).fit(lo.reshape(-1, 1), y).coef_[0, 0] if two else np.nan, n=len(y))


def lomo(d, min_test=20, min_train=100):
    """Out-of-fold predictions by map, per (map_era, regime, round). Train on both sides, score side A."""
    out = []
    for (era, reg, cp), x in d.groupby(['map_era', 'regime', 'round']):
        maps = sorted(x['map'].unique())
        for m in maps:
            tr, te = x[x['map'] != m], x[(x['map'] == m) & (x.side == 'A')]
            if len(te) < min_test or tr.game.nunique() < min_train:
                continue
            ytr = tr.y.to_numpy(float)
            ph = fit_phi(tr[PHI].to_numpy(float), ytr)
            if MODEL == 'lr_q':
                tr, te = prep_lq(tr), prep_lq(te)
                lq = fit_phi(tr[LQ].to_numpy(float), ytr); pv = lq.predict_proba(te[LQ].to_numpy(float) - 0.5)[:, 1]
            else:
                pv = pred_gbt(fit_gbt(tr[FEATS].to_numpy(float), ytr, FEATS), te[FEATS].to_numpy(float), FEATS)
            out.append(pd.DataFrame(dict(game=te.game, map=m, map_era=era, regime=reg, round=cp, y=te.y,
                                         p_v0=pv,
                                         p_phi=ph.predict_proba(te[PHI].to_numpy(float) - 0.5)[:, 1])))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def table(oof):
    rows = []
    for (era, reg, cp), x in oof.groupby(['map_era', 'regime', 'round']):
        a, b = metrics(x.y.to_numpy(), x.p_v0.to_numpy()), metrics(x.y.to_numpy(), x.p_phi.to_numpy())
        rows.append(dict(map_era=era, regime=reg, round=cp, n=a['n'], maps=x['map'].nunique(), auc_v0=a['auc'], auc_phi=b['auc'],
                         d_auc=a['auc'] - b['auc'], brier_v0=a['brier'], brier_phi=b['brier'], slope_v0=a['slope'], slope_phi=b['slope']))
    return pd.DataFrame(rows)


def gate(t):
    """P-hinata-01 frozen gate. Returns (verdict, reasons)."""
    why = []
    for r in t.itertuples():
        if r.d_auc < 0:
            why.append(f'{r.map_era}/{r.regime}/r{r.round}: AUC {r.auc_v0:.3f} < Φ {r.auc_phi:.3f}')
        if r.round >= 25 and not (0.9 <= r.slope_v0 <= 1.1):
            why.append(f'{r.map_era}/{r.regime}/r{r.round}: slope {r.slope_v0:.2f} outside [0.9, 1.1]')
    rl50 = t[(t.regime == 'rl') & (t['round'] == 50)]
    for r in rl50.itertuples():
        if r.auc_v0 < 0.66:
            why.append(f'{r.map_era}/rl/r50: AUC {r.auc_v0:.3f} < 0.66')
    return ('PASS' if not why else 'FAIL'), why


def series_bootstrap_dauc(oof, B=1000, seed=7):
    """Δ AUC (V0 − Φ) per cell with a game-cluster bootstrap (one row per game per cell, so games are the clusters)."""
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(seed); rows = []
    for k, x in oof.groupby(['map_era', 'regime', 'round']):
        y, a, b = x.y.to_numpy(), x.p_v0.to_numpy(), x.p_phi.to_numpy(); n = len(y); ds = []
        for _ in range(B):
            i = rng.integers(0, n, n)
            if len(set(y[i])) < 2:
                continue
            ds.append(roc_auc_score(y[i], a[i]) - roc_auc_score(y[i], b[i]))
        rows.append(dict(zip(['map_era', 'regime', 'round'], k), d_lo=np.percentile(ds, 5), d_hi=np.percentile(ds, 95)))
    return pd.DataFrame(rows)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def heldout(path):
    j = json.loads(Path(path).read_text())
    hm = j.get('heldout_maps') or j.get('maps') or []
    if len(hm) < 3:
        sys.exit(f'splits manifest {path} lists {len(hm)} held-out maps (< 3); refusing to fit')
    return list(hm), j


def cmd_dry(a):
    d = load([a.era])
    cov = d[d.side == 'A'].groupby(['map', 'round']).size().unstack('round')
    print(f'era {a.era}: games {d.game.nunique()}, rows {len(d)} (no outcomes read)'); print(cov.to_string())
    qc = d[d['round'] == 100][QUEEN].notna().mean().round(3)
    print('queen-feature coverage @r100:', qc.to_dict())


def cmd_smoke(a):
    maps = ['Big Empty', 'Default Small', 'Stronghold']
    d = load(['pre'], maps=maps)
    d['regime'] = 'elim'
    print('smoke rows', len(d), 'games', d.game.nunique())
    oof = lomo(d, min_test=5, min_train=20)
    if len(oof):
        print(table(oof).round(3).to_string(index=False))
    print('smoke OK (plumbing only; maps outside LIVE_MAPS_M2, no queen)')


def cmd_fit(a):
    """Resumable (the VM kills calls at 3 min): each call fills missing rounds in the run dir, then finalises."""
    hm, man = heldout(a.splits)
    run = Path(a.run) if a.run else Path(a.out) / ('fit-' + hashlib.sha256(Path(a.splits).read_bytes()).hexdigest()[:8])
    run.mkdir(parents=True, exist_ok=True)
    cache = run / 'train_rows.parquet'
    if cache.exists():
        d = pd.read_parquet(cache)
    else:
        d = load(a.era.split(','), exclude=hm, include_ended=a.include_ended); d.to_parquet(cache)
    assert not set(d['map']) & set(hm), 'held-out map leaked into training rows'
    t0, budget = time.time(), float(a.budget)
    for cp in CPS:
        f = run / f'oof_r{cp}.parquet'
        if f.exists():
            continue
        if time.time() - t0 > budget:
            print('budget spent; call again to continue'); return
        x = d[d['round'] == cp]
        lomo(x).to_parquet(f)
        for (era, reg), xx in x.groupby(['map_era', 'regime']):
            if MODEL == 'lr_q':
                xx = prep_lq(xx); m = fit_phi(xx[LQ].to_numpy(float), xx.y.to_numpy(float))
                (run / f'v0b_{era}_{reg}_r{cp}.json').write_text(json.dumps(dict(zip(LQ, m.coef_[0].round(4)))))
                continue
            fit_gbt(xx[FEATS].to_numpy(float), xx.y.to_numpy(float), FEATS).booster_.save_model(str(run / f'v0_{era}_{reg}_r{cp}.txt'))
        print(f'r{cp} done {time.time() - t0:.0f}s', flush=True)
    oof = pd.concat([pd.read_parquet(run / f'oof_r{cp}.parquet') for cp in CPS], ignore_index=True)
    oof.to_parquet(run / 'oof.parquet')
    t = table(oof).merge(series_bootstrap_dauc(oof, B=int(a.boot)), on=['map_era', 'regime', 'round'])
    verdict, why = gate(t)
    t.to_csv(run / 'lomo.csv', index=False)
    commit = subprocess.run(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    reg_entry = dict(artifact='hinata-v0', rung='R1', run=str(run), code_sha=sha(__file__), repo_head=commit,
                     splits=str(a.splits), splits_sha=sha(a.splits), heldout_maps=hm, eras=a.era,
                     data=dict(games=int(d.game.nunique()), rows=int(len(d)), maps=sorted(d['map'].unique()),
                               train_rows_sha=sha(cache)),
                     features=LQ if MODEL == 'lr_q' else FEATS, hyper=dict(C=1.0, intercept=False) if MODEL == 'lr_q' else GBT, model_class=MODEL, bootstrap=dict(B=int(a.boot), seed=7, interval='90% percentile, game clusters'),
                     verdict=verdict, reasons=why, finished=time.strftime('%FT%TZ', time.gmtime()))
    (run / 'registry.json').write_text(json.dumps(reg_entry, indent=1, default=str))
    print(t.round(3).to_string(index=False)); print('GATE', verdict); [print('  -', w) for w in why]
    print('wrote', run)


def cmd_confirm(a):
    """One-shot: score the frozen models on the held-out maps. Refuses to run twice for the same run dir."""
    hm, _ = heldout(a.splits)
    run = Path(a.model); flag = run / 'CONFIRMED'
    if flag.exists():
        sys.exit(f'{run} already confirmed on held-out maps; never re-run (D-045 frozen splits)')
    import lightgbm as lgb
    d = load(a.era.split(','), maps=hm); d = d[d.side == 'A']
    tr = load(a.era.split(','), exclude=hm)  # running states only, as in fit
    rows = []
    for (era, reg, cp), x in d.groupby(['map_era', 'regime', 'round']):
        if MODEL == 'lr_q':
            f = run / f'v0b_{era}_{reg}_r{int(cp)}.json'
            if not f.exists():
                continue
            w = json.loads(f.read_text()); xq = prep_lq(x)
            pv = 1 / (1 + np.exp(-((xq[LQ].to_numpy(float) - 0.5) @ np.array([w[k] for k in LQ]))))
        else:
            f = run / f'v0_{era}_{reg}_r{cp}.txt'
            if not f.exists():
                continue
            b = lgb.Booster(model_file=str(f)); X = x[FEATS].to_numpy(float)
            pv = 0.5 * (b.predict(X) + 1 - b.predict(mirror(X, FEATS)))
        t_ = tr[(tr.map_era == era) & (tr.regime == reg) & (tr['round'] == cp)]
        pp = fit_phi(t_[PHI].to_numpy(float), t_.y.to_numpy(float)).predict_proba(x[PHI].to_numpy(float) - 0.5)[:, 1]
        a_, b_ = metrics(x.y.to_numpy(), pv), metrics(x.y.to_numpy(), pp)
        rows.append(dict(map_era=era, regime=reg, round=cp, n=a_['n'], auc_v0=a_['auc'], auc_phi=b_['auc'], slope_v0=a_['slope'], slope_phi=b_['slope']))
    t = pd.DataFrame(rows); t.to_csv(run / 'heldout.csv', index=False); flag.write_text(time.strftime('%FT%TZ', time.gmtime()))
    print(t.round(3).to_string(index=False))


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    for c in ('dry', 'smoke', 'fit', 'confirm'):
        p = sp.add_parser(c); p.add_argument('--era', default='post-m2'); p.add_argument('--splits')
        p.add_argument('--out', default='build/hinata/v0'); p.add_argument('--model'); p.add_argument('--run')
        p.add_argument('--budget', default='120'); p.add_argument('--model-class', default='gbt', choices=['gbt', 'lr_q']); p.add_argument('--boot', default='1000')
        p.add_argument('--include-ended', action='store_true', help='keep checkpoint rows after the game ended (Φ-table comparability only)')
    a = ap.parse_args()
    global MODEL
    MODEL = a.model_class
    if a.cmd in ('fit', 'confirm') and not a.splits:
        sys.exit('--splits <frozen manifest> is required (Data proposes, Chair records in D-045)')
    dict(dry=cmd_dry, smoke=cmd_smoke, fit=cmd_fit, confirm=cmd_confirm)[a.cmd](a)


if __name__ == '__main__':
    main()
