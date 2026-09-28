"""Train the deployable clone model on v4 'view+mem' features.
Phase 1: capacity sweep, fit on train, score val.  Phase 2 (--final CAP): refit on train+val, export JSON, parity-check."""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss
sys.path.insert(0, str(Path(__file__).parent))
from il_common import load, feature_sets
import export_hgb

feat, manifest, splits, outd = sys.argv[1:5]
final = sys.argv[sys.argv.index('--final') + 1] if '--final' in sys.argv else None
outd = Path(outd); outd.mkdir(parents=True, exist_ok=True)
sp = json.load(open(splits))
D, m, games = load(feat, manifest, 8264)
D = D.copy()
D['split'] = D.game.map({g: k for k in ('train', 'val', 'test') for g in sp[k]})
FS = feature_sets(D)
cols = FS['view+mem']
json.dump(cols, open(outd / 'clone_features.json', 'w'))
classes = ['F', 'L', 'R', 'split', 'suicide']
D = D[D.y_first.isin(classes)]
Y = D.y_first.map({c: i for i, c in enumerate(classes)}).values
X = D[cols].values.astype(np.float32)
caps = {'s': (60, 15), 'm': (120, 31), 'l': (300, 63)}
if final is None:
    tr = np.flatnonzero((D.split == 'train').values); va = np.flatnonzero((D.split == 'val').values)
    res = []
    for k, (it, lv) in caps.items():
        t = time.time()
        c = HistGradientBoostingClassifier(max_iter=it, max_leaf_nodes=lv, min_samples_leaf=100, early_stopping=False,
                                           random_state=0).fit(X[tr], Y[tr])
        P = c.predict_proba(X[va])
        n_nodes = sum(len(tp.nodes) for itp in c._predictors for tp in itp)
        res.append(dict(cap=k, iters=it, leaves=lv, acc=accuracy_score(Y[va], P.argmax(1)), logloss=log_loss(Y[va], P),
                        nodes=n_nodes, fit_s=round(time.time() - t)))
        print(res[-1], flush=True)
    pd.DataFrame(res).to_csv(outd / 'capacity_val.csv', index=False)
else:
    it, lv = caps[final]
    tr = np.flatnonzero(D.split.isin(['train', 'val']).values)
    c = HistGradientBoostingClassifier(max_iter=it, max_leaf_nodes=lv, min_samples_leaf=100, early_stopping=False,
                                       random_state=0).fit(X[tr], Y[tr])
    export_hgb.export(c, cols, classes, outd / 'model.json')
    pr = export_hgb.Predictor(outd / 'model.json')
    te = np.flatnonzero((D.split == 'test').values)
    rng = np.random.default_rng(0); sample = rng.choice(te, 2000, replace=False)
    P = c.predict_proba(X[sample])
    diffs, agree = [], 0
    for j, i in enumerate(sample):
        row = dict(zip(cols, X[i].tolist()))
        q = pr.proba(row)
        qv = np.array([q[k] for k in classes])
        diffs.append(np.abs(qv - P[j]).max()); agree += qv.argmax() == P[j].argmax()
    json.dump(dict(cap=final, max_abs_prob_diff=float(max(diffs)), argmax_agreement=agree / len(sample), n=len(sample)),
              open(outd / 'export_parity.json', 'w'))
    print('parity', max(diffs), agree / len(sample))
