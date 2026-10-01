"""A shaped-reward target: a win-probability potential Φ(state, round), fitted on the corpus and validated out of sample.

  python3 tools/antioch/value_target.py fit [--era post] [--queen build/antioch/queen.parquet] [--out build/antioch/value]

Label: the server's result (games.result_a; correct under the 1.2.3 tiebreak), not the store's decoded `won`.
Features at a checkpoint are opponent-relative and map-free, so Φ(us) = 1 − Φ(them):
  total_share, units_share, longest_rel = (L − L_opp) / max(L, L_opp), pearls_share (c_eats), territory_share,
  deaths_share (c_deaths), and, where the queen table covers the game, queen_diff = own queen alive − enemy queen alive.
Models per checkpoint: logistic regression on the centred shares (no map, no team, no seat) and a small GBT for comparison.
Validation:
  * leave-one-map-out (fit on 9 ladder maps, score the 10th): the out-of-sample rule;
  * pre -> post transfer (fit pre, score post);
  * baselines: total_share alone; own income only (c_eats ÷ per-map median at the round: the tempo family, opponent-blind).
Metrics: AUC, Brier, log loss, calibration slope; reported per checkpoint and per map.
"""
import argparse, json, os, sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
if (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import duckdb
import numpy as np
import pandas as pd

S1 = ROOT / 'build' / 's1' / 'corpus'
LADDER = ('Autarky', 'Default', 'Devil', 'Portals', 'Prisoners Dilemma', 'Queen Of Spades', 'Schooltime', 'Slithery Fight',
          'Trauma', 'Trophy')
CPS = (10, 25, 50, 100, 150, 250, 400)
FEATS = ['total_share', 'units_share', 'longest_rel', 'pearls_share', 'territory_share', 'deaths_share']


def load():
    con = duckdb.connect()
    con.execute("set threads to 4")
    maps = ','.join(f"'{m}'" for m in LADDER)
    cps = ','.join(str(c) for c in CPS)
    sql = f"""
    with s as (select * from read_parquet('{S1}/series/part-*.parquet', union_by_name=true)
               where map in ({maps}) and round in ({cps}) and side = 'A')
    select s.game, s.map, s.round, g.era, g.result_a as y, g.team_a, g.team_b,
           s.total, s.opp_total, s.units, s.opp_units, s.longest, s.opp_longest, s.c_eats, s.opp_c_eats,
           s.territory, s.opp_territory, s.c_deaths, s.opp_c_deaths, s.ended
    from s join read_parquet('{S1}/games.parquet') g using (game)
    where g.result_a in (0, 1)"""
    d = con.execute(sql).df().drop_duplicates(['game', 'round'])
    sh = lambda a, b: np.where((a + b) > 0, a / (a + b).replace(0, np.nan), 0.5)
    d['total_share'] = sh(d.total, d.opp_total)
    d['units_share'] = sh(d.units, d.opp_units)
    mx = np.maximum(d.longest, d.opp_longest).replace(0, np.nan)
    d['longest_rel'] = ((d.longest - d.opp_longest) / mx).fillna(0) / 2 + 0.5
    d['pearls_share'] = sh(d.c_eats, d.opp_c_eats)
    d['territory_share'] = sh(d.territory.fillna(0), d.opp_territory.fillna(0))
    d['deaths_share'] = sh(d.c_deaths, d.opp_c_deaths)
    med = d.groupby(['era', 'map', 'round']).c_eats.transform('median').replace(0, np.nan)
    d['income_rel'] = (d.c_eats / med).fillna(1.0)
    return d


def metrics(y, p):
    from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
    p = np.clip(p, 1e-4, 1 - 1e-4)
    lo = np.log(p / (1 - p))
    from sklearn.linear_model import LogisticRegression
    slope = LogisticRegression(C=1e6).fit(lo.reshape(-1, 1), y).coef_[0, 0] if len(set(y)) > 1 else np.nan
    return dict(auc=roc_auc_score(y, p) if len(set(y)) > 1 else np.nan, brier=brier_score_loss(y, p), logloss=log_loss(y, p, labels=[0, 1]),
                calib_slope=slope, n=len(y))


def fit_lr(X, y):
    from sklearn.linear_model import LogisticRegression
    # symmetric potential: centred shares, no intercept (Φ(us) = 1 − Φ(them))
    return LogisticRegression(C=1.0, fit_intercept=False, max_iter=1000).fit(X - 0.5, y)


def lomo(d, feats, model='lr'):
    from sklearn.ensemble import HistGradientBoostingClassifier
    rows = []
    for cp in CPS:
        x = d[d['round'] == cp]
        ps = np.full(len(x), np.nan)
        for m in LADDER:
            tr, te = (x['map'] != m).to_numpy(), (x['map'] == m).to_numpy()
            if te.sum() < 20 or tr.sum() < 100:
                continue
            Xtr, Xte = x.loc[tr, feats].to_numpy(float), x.loc[te, feats].to_numpy(float)
            if model == 'lr':
                ps[te] = fit_lr(Xtr, x.y.to_numpy()[tr]).predict_proba(Xte - 0.5)[:, 1]
            else:
                ps[te] = HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05).fit(Xtr, x.y.to_numpy()[tr]).predict_proba(Xte)[:, 1]
        ok = ~np.isnan(ps)
        rows.append(dict(round=cp, **metrics(x.y.to_numpy()[ok], ps[ok])))
    return pd.DataFrame(rows).set_index('round')


def cmd_fit(a):
    d = load()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    res = {}
    for era in ('pre', 'post'):
        e = d[d.era == era]
        print(f'\n===== era {era}: games {e.game.nunique()}  (per checkpoint rows: {e[e["round"] == 50].shape[0]})')
        for lab, feats, model in (('Φ logistic, 6 shares', FEATS, 'lr'), ('Φ GBT, 6 shares', FEATS, 'gbt'),
                                  ('total_share only', ['total_share'], 'lr'), ('own income only (tempo family)', ['income_rel'], 'gbt')):
            if lab.startswith('own'):
                r = lomo(e.assign(income_rel=e.income_rel), ['income_rel'], 'gbt')
            else:
                r = lomo(e, feats, model)
            res[(era, lab)] = r
            print(f'-- {lab}  (leave-one-map-out)'); print(r[['auc', 'brier', 'calib_slope', 'n']].round(3).T.to_string())
    # pre -> post transfer of the logistic Φ
    pre, post = d[d.era == 'pre'], d[d.era == 'post']
    rows, coefs = [], {}
    for cp in CPS:
        a_, b_ = pre[pre['round'] == cp], post[post['round'] == cp]
        if len(b_) < 50:
            continue
        m = fit_lr(a_[FEATS].to_numpy(float), a_.y.to_numpy())
        mp = fit_lr(b_[FEATS].to_numpy(float), b_.y.to_numpy())
        coefs[cp] = dict(pre=dict(zip(FEATS, m.coef_[0].round(2))), post=dict(zip(FEATS, mp.coef_[0].round(2))))
        rows.append(dict(round=cp, **metrics(b_.y.to_numpy(), m.predict_proba(b_[FEATS].to_numpy(float) - 0.5)[:, 1])))
    print('\n-- pre-fitted logistic Φ scored on post games'); print(pd.DataFrame(rows).set_index('round')[['auc', 'brier', 'calib_slope', 'n']].round(3).T.to_string())
    print('\n-- coefficients (centred shares; pre vs post fitted on all maps)')
    for cp, c in coefs.items():
        print(cp, 'pre', c['pre'], '\n    post', c['post'])
    # per-map AUC of the post logistic Φ at r50 and r150 (leave-one-map-out predictions)
    for cp in (50, 150):
        x = post[post['round'] == cp]
        pm = []
        for m in LADDER:
            tr, te = x['map'] != m, x['map'] == m
            if te.sum() < 20:
                continue
            p = fit_lr(x.loc[tr, FEATS].to_numpy(float), x.y[tr].to_numpy()).predict_proba(x.loc[te, FEATS].to_numpy(float) - 0.5)[:, 1]
            pm.append(dict(map=m, **metrics(x.y[te].to_numpy(), p)))
        print(f'\n-- post logistic Φ per held-out map at r{cp}'); print(pd.DataFrame(pm).set_index('map')[['auc', 'brier', 'calib_slope', 'n']].round(3).to_string())
    if a.queen and Path(a.queen).exists():
        q = pd.read_parquet(a.queen)
        qa = q[q.side == 'A'][['game', 'queen_death_round', 'queen_len@100']].rename(columns={'queen_death_round': 'qd_a'})
        qb = q[q.side == 'B'][['game', 'queen_death_round']].rename(columns={'queen_death_round': 'qd_b'})
        p2 = post.merge(qa, on='game').merge(qb, on='game')
        alive = lambda qd, r: (qd.isna() | (qd > r)).astype(float)
        p2['queen_diff'] = (alive(p2.qd_a, p2['round']) - alive(p2.qd_b, p2['round'])) / 2 + 0.5
        f2 = FEATS + ['queen_diff']
        print(f'\n-- post, queen-augmented Φ (games with queen rows: {p2.game.nunique()}), leave-one-map-out')
        r1, r2 = lomo(p2, FEATS), lomo(p2, f2)
        print(pd.concat({'6 shares': r1[['auc', 'brier']], '+ queen_diff': r2[['auc', 'brier']]}, axis=1).round(3).T.to_string())
        for cp in (250, 400):
            x = p2[p2['round'] == cp]
            m = fit_lr(x[f2].to_numpy(float), x.y.to_numpy())
            print(f'   coef r{cp}:', dict(zip(f2, m.coef_[0].round(2))))
    # the deliverable: per-checkpoint coefficients of the post Φ fitted on all maps
    allc = {cp: dict(zip(FEATS, fit_lr(post[post['round'] == cp][FEATS].to_numpy(float), post[post['round'] == cp].y.to_numpy()).coef_[0].round(3)))
            for cp in CPS if (post['round'] == cp).sum() > 50}
    (out / 'phi_post.json').write_text(json.dumps({str(k): v for k, v in allc.items()}, indent=1))
    print('\nwrote', out / 'phi_post.json')


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    f = sp.add_parser('fit'); f.add_argument('--queen'); f.add_argument('--out', default='build/antioch/value')
    a = ap.parse_args()
    cmd_fit(a)


if __name__ == '__main__':
    main()
