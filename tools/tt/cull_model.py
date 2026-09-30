"""TT: when do the top teams kill their own small dragons? The cull decision as a sixth Q1-style decision.

    HB_TEAM=70 HB_BUILD=tt/team70 HB_TAG=tt70 .venv/bin/python tools/tt/cull_model.py [--jobs N] [--per-game 400]

Rows: the team's actor-turns at length <= 3 (where ~90 % of self-kills happen), sampled per game. Label: self-kill
(an invalid command, or a backward step into the own neck). Same held-out games and feature exclusions as Q1.
Reports the rate by round / nearest ally head / units, a depth-4 tree (rules), a GBT (accuracy, AUC, top features).
Writes game_stats/runs/<TAG>-cull.json.
"""
import argparse, glob, json, os, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'hb1'))
import q1_decisions as Q1

B, TAG = Q1.B, Q1.TAG
PER = 400


def _rows(path):
    d = pd.read_parquet(path)
    d = d[d.length <= 3]
    d = d.assign(y_cull=(~d.y_first.isin(['F', 'R', 'L', 'split'])).astype(int))
    if len(d) > PER:
        rng = np.random.default_rng(int(Path(path).stem) + 11)
        keep = np.zeros(len(d), bool)
        keep[rng.choice(len(d), PER, replace=False)] = True
        keep |= d.y_cull.to_numpy() == 1                     # keep every cull; weights restore the base rate
        w = np.where(d.y_cull.to_numpy() == 1, 1.0, (len(d) - d.y_cull.sum()) / max(1, (keep & (d.y_cull.to_numpy() == 0)).sum()))
        d = d.assign(w=w)[keep]
    else:
        d = d.assign(w=1.0)
    for c in d.columns:
        if not pd.api.types.is_numeric_dtype(d[c]) and c not in Q1.LABELS and c not in Q1.MAP_ID:
            d[c] = d[c].astype(str)
    return d


def main():
    global PER
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--per-game', type=int, default=PER)
    a = ap.parse_args()
    PER = a.per_game
    with Pool(a.jobs) as pool:
        d = pd.concat(pool.map(_rows, sorted(glob.glob(str(B / 'v5' / 'corpus' / '*.parquet'))), chunksize=8), ignore_index=True)
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    test_games = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    te = d.game.astype(int).isin(test_games).to_numpy()
    y, w = d.y_cull.to_numpy(), d.w.to_numpy()
    X = d[[c for c in d.columns if c not in Q1.LABELS and c not in Q1.MAP_ID and c not in ('y_cull', 'w', 'mem_initial')]].copy()
    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype('category').cat.codes
    X = X.astype(np.float32)
    rate = lambda m: float((y[m] * w[m]).sum() / max(1e-9, w[m].sum()))
    res = dict(rows=len(d), culls=int(y.sum()), base_rate=rate(np.ones(len(y), bool)))
    rb = pd.cut(d['round'], [0, 100, 200, 250, 300, 350, 400, 450, 501], right=False)
    res['by_round'] = {str(k): rate((rb == k).to_numpy()) for k in rb.cat.categories}
    nh = d.near_ally_head.clip(upper=7)
    res['by_near_ally_head'] = {int(k): rate((nh == k).to_numpy()) for k in sorted(nh.unique())}
    ub = pd.cut(d.units_frac, [0, .25, .5, .75, .95, 1.01], right=False)
    res['by_units_frac'] = {str(k): rate((ub == k).to_numpy()) for k in ub.cat.categories}
    res['by_length'] = {int(k): rate((d.length == k).to_numpy()) for k in sorted(d.length.unique())}
    res['by_exits'] = {int(k): rate((d.n_exit_any.clip(upper=3) == k).to_numpy()) for k in sorted(d.n_exit_any.clip(upper=3).unique())}
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.metrics import roc_auc_score
    import xgboost as xgb
    t = DecisionTreeClassifier(max_depth=4, min_samples_leaf=50, random_state=Q1.SEED).fit(X[~te], y[~te], sample_weight=w[~te])
    res['tree4_rules'] = export_text(t, feature_names=list(X.columns), max_depth=4)
    pt = t.predict_proba(X[te])[:, 1]
    m = xgb.XGBClassifier(device='cuda', tree_method='hist', grow_policy='lossguide', max_leaves=63, max_depth=0,
                          learning_rate=0.1, n_estimators=300, random_state=Q1.SEED)
    m.fit(X[~te], y[~te], sample_weight=w[~te])
    pg = m.predict_proba(X[te])[:, 1]
    acc = lambda p: float((((p >= 0.5) == y[te]) * w[te]).sum() / w[te].sum())
    res['majority'] = float(1 - rate(te))
    res['tree4'] = dict(acc=acc(pt), auc=float(roc_auc_score(y[te], pt, sample_weight=w[te])))
    res['gbt'] = dict(acc=acc(pg), auc=float(roc_auc_score(y[te], pg, sample_weight=w[te])),
                      recall_at_half=float(((pg >= 0.5) & (y[te] == 1)).sum() / max(1, (y[te] == 1).sum())))
    imp = m.get_booster().get_score(importance_type='total_gain')
    res['top_gain'] = sorted(imp.items(), key=lambda kv: -kv[1])[:20]
    (ROOT / 'game_stats' / 'runs' / f'{TAG}-cull.json').write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ('tree4_rules', 'top_gain')}, indent=1))
    print('top gain:', [k for k, _ in res['top_gain'][:12]])
    print(res['tree4_rules'])


if __name__ == '__main__':
    main()
