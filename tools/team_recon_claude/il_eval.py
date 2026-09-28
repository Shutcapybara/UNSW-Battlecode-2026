"""Refit frozen configs on the train split and score the untouched test split once."""
import json, sys, pickle
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, accuracy_score, f1_score, confusion_matrix, recall_score
sys.path.insert(0, str(Path(__file__).parent))
from il_common import load, feature_sets

feat, manifest, outd, sub = sys.argv[1], sys.argv[2], Path(sys.argv[3]), int(sys.argv[4])
sp = json.load(open(outd / 'splits.json'))
D, m, games = load(feat, manifest, sub)
split = {g: k for k in ('train', 'val', 'test') for g in sp[k]}
D['split'] = D.game.map(split)
FS = feature_sets(D)
classes = sorted(D.y_first.unique())
Y = D.y_first.map({c: i for i, c in enumerate(classes)}).values
tri = np.flatnonzero((D.split == 'train').values)
rng = np.random.default_rng(0)
if len(tri) > 400000:
    tri = rng.choice(tri, 400000, replace=False)
tei = np.flatnonzero((D.split == 'test').values)


def score(P, idx, tag):
    y = Y[idx]; pred = P.argmax(1); g = D.game.values[idx]
    P2 = np.clip(P, 1e-6, 1); P2 /= P2.sum(1, keepdims=True)
    r = dict(tag=tag, n=len(idx), games=len(set(g)), acc=accuracy_score(y, pred),
             acc_game_bal=pd.Series(pred == y).groupby(g).mean().mean(),
             macro_f1=f1_score(y, pred, average='macro'), logloss=log_loss(y, P2, labels=list(range(len(classes)))))
    for c, v in zip(classes, recall_score(y, pred, average=None, labels=list(range(len(classes))), zero_division=0)):
        r['recall_' + c] = v
    return r


res, preds = [], {}
prior = np.bincount(Y[tri], minlength=len(classes)) / len(tri)
res.append(score(np.tile(prior, (len(tei), 1)), tei, 'majority|test'))
cfgs = [('hgb', 'legal_all'), ('hgb', 'view'), ('hgb', 'DIAG_priv'), ('tree_d6', 'view+mem'), ('tree_d3', 'view')]
fitted = {}
for kind, fs in cfgs:
    cols = FS[fs]
    X = D.iloc[tri][cols].values.astype(np.float32)
    if kind == 'hgb':
        clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, max_leaf_nodes=63, min_samples_leaf=100,
                                             early_stopping=True, validation_fraction=0.1, random_state=0).fit(X, Y[tri])
    else:
        clf = DecisionTreeClassifier(max_depth=int(kind[6:]), min_samples_leaf=200, random_state=0).fit(X, Y[tri])
    P = np.zeros((len(tei), len(classes)))
    P[:, clf.classes_] = clf.predict_proba(D.iloc[tei][cols].values.astype(np.float32))
    res.append(score(P, tei, f'{kind}|{fs}|test'))
    preds[f'{kind}|{fs}'] = P
    fitted[f'{kind}|{fs}'] = (clf, cols)
    if kind.startswith('tree'):
        (outd / f'rules_{kind}_{fs}.txt').write_text(export_text(clf, feature_names=cols, class_names=classes, show_weights=True))
    print(kind, fs, flush=True)
R = pd.DataFrame(res)
R.to_csv(outd / 'test_results.csv', index=False)
print(R.round(3).to_string())
best = preds['hgb|legal_all']
T = D.iloc[tei][['game', 'round', 'dragon', 'map', 'length', 'units', 'y_first', 'y_seq', 'y_split', 'vis_enemy_heads', 'free_dirs']].copy()
T['pred'] = [classes[i] for i in best.argmax(1)]
T['p_max'] = best.max(1)
for i, c in enumerate(classes):
    T['p_' + c] = best[:, i]
T.to_parquet(outd / 'test_predictions.parquet')
print(pd.crosstab(T.y_first, T.pred))
T['ok'] = T.y_first == T.pred
T['stage'] = pd.cut(T['round'], [-1, 50, 100, 250, 400, 500], labels=['0-50', '50-100', '100-250', '250-400', '400-500'])
print(T.groupby('stage', observed=True).ok.mean().round(3))
print(T.groupby('map').ok.mean().round(3))
print(T.groupby('free_dirs').ok.agg(['mean', 'size']).round(3))
pickle.dump(dict(fitted=fitted, classes=classes), open(outd / 'test_models.pkl', 'wb'))
