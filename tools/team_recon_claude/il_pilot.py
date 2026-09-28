"""Imitation-learning pilot: model ladder on legal decision rows.

    python3 il_pilot.py FEATDIR MANIFEST OUTDIR [--sub 8264] [--max-train-rows N]

Splits: whole games only.  (1) chronological: oldest 70% of games (by
completed_at) train, next 10% validation (model/depth selection), newest 20%
test — test touched once after selection.  (2) leave-one-map-out on train+val
games for transfer.  Metrics on game-balanced and natural views.
"""
import argparse, json, time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, accuracy_score, f1_score, confusion_matrix, recall_score

ap = argparse.ArgumentParser()
ap.add_argument('feat'); ap.add_argument('manifest'); ap.add_argument('out')
ap.add_argument('--sub', type=int); ap.add_argument('--max-train-rows', type=int, default=400000)
ap.add_argument('--label', default='y_first'); ap.add_argument('--rows-per-game', type=int, default=4000); ap.add_argument('--splits'); ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
import sys as _s; _s.path.insert(0, str(Path(__file__).parent))
from il_common import load as _load
m = pd.read_csv(a.manifest, dtype={'game_id': str})
m = m[m.status == 'ok']
if a.sub:
    m = m[m.target_submission == a.sub]
m = m.sort_values('completed_at')
frames = []
for gid in m.game_id:
    f = Path(a.feat) / f'{gid}.parquet'
    if f.exists():
        x = pd.read_parquet(f)
        x = x[x.y_family.isin(['move', 'split'])]
        if len(x) > a.rows_per_game:
            x = x.sample(a.rows_per_game, random_state=0)
        for c in x.columns:
            if x[c].dtype == 'float64':
                x[c] = x[c].astype('float32')
            elif x[c].dtype == 'int64':
                x[c] = x[c].astype('int32')
        frames.append(x)
D = pd.concat(frames, ignore_index=True)
D['game'] = D['game'].astype(str)
D = D[D.y_family.isin(['move', 'split'])].copy()
# label: family+first ego direction; split subdivided into suicide(SPLIT 1) vs real split
D['y_first'] = np.where(D.y_family == 'split', np.where(D.y_split == 1, 'suicide', 'split'), D.y_first)
games = [g for g in m.game_id if g in set(D.game)]
n = len(games)
tr, va, te = games[:int(.7 * n)], games[int(.7 * n):int(.8 * n)], games[int(.8 * n):]
if a.splits:
    _sp = json.load(open(a.splits)); tr, va, te = _sp['train'], _sp['val'], _sp['test']
split = {g: 'train' for g in tr} | {g: 'val' for g in va} | {g: 'test' for g in te}
D['split'] = D.game.map(split)
cat_cols = ['facing_abs', 'mem_last_family', 'mem_last_rel']
for c in cat_cols:
    D[c] = D[c].astype('category').cat.codes
ids = ['game', 'round', 'dragon', 'map', 'split']
ys = [c for c in D.columns if c.startswith('y_') or c == 'post_died']
priv = [c for c in D.columns if c.startswith('priv_')]
mem = [c for c in D.columns if c.startswith('mem_')]
absxy = ['x', 'y', 'xn', 'yn', 'facing_abs', 'W', 'H']
msg = ['n_msgs_all', 'n_msgs_u32', 'mem_msgs_total'] + [c for c in D.columns if c.startswith('echo_')]
allf = [c for c in D.columns if c not in ids + ys]
legal = [c for c in allf if c not in priv]
FS = {
    'view': [c for c in legal if c not in mem + absxy + msg],
    'view+abs': [c for c in legal if c not in mem + msg],
    'view+mem': [c for c in legal if c not in absxy + msg],
    'legal_all': legal,
    'DIAG_priv': allf,
}
json.dump({k: v for k, v in FS.items()}, open(out / 'feature_sets.json', 'w'), indent=0)
json.dump(dict(train=tr, val=va, test=te), open(out / 'splits.json', 'w'))
classes = sorted(D.y_first.unique())
Y = D.y_first.map({c: i for i, c in enumerate(classes)}).values
rng = np.random.default_rng(a.seed)
trmask = (D.split == 'train').values
tri = np.flatnonzero(trmask)
if len(tri) > a.max_train_rows:
    tri = rng.choice(tri, a.max_train_rows, replace=False)
vai = np.flatnonzero((D.split == 'val').values)
tei = np.flatnonzero((D.split == 'test').values)


def metrics(idx, P, tag):
    y = Y[idx]
    pred = P.argmax(1)
    g = D.game.values[idx]
    acc_g = pd.Series(pred == y).groupby(g).mean().mean()
    P2 = np.clip(P, 1e-6, 1)
    P2 = P2 / P2.sum(1, keepdims=True)
    r = dict(tag=tag, n=len(idx), games=len(set(g)), acc=accuracy_score(y, pred), acc_game_bal=acc_g,
             macro_f1=f1_score(y, pred, average='macro'), logloss=log_loss(y, P2, labels=list(range(len(classes)))))
    rec = recall_score(y, pred, average=None, labels=list(range(len(classes))), zero_division=0)
    for c, v in zip(classes, rec):
        r['recall_' + c] = v
    return r


results = []
# baselines
prior = np.bincount(Y[tri], minlength=len(classes)) / len(tri)
for nm, idx in (('val', vai), ('test', tei)):
    results.append(metrics(idx, np.tile(prior, (len(idx), 1)), f'majority|{nm}'))


def greedy(idx):
    """hand rule: free direction with shortest visible pearl path, prefer F; never split."""
    X = D.iloc[idx]
    P = np.full((len(idx), len(classes)), 1e-3)
    best = []
    for rel in ('F', 'R', 'L'):
        free = (X[f'c{rel}_block'] == 0).values
        pd_ = np.where(free, X[f'c{rel}_pdist'].values + (0 if rel == 'F' else 0.5), 1e9)
        best.append(pd_)
    best = np.array(best).argmin(0)
    for j, rel in enumerate(('F', 'R', 'L')):
        P[best == j, classes.index(rel)] = 1
    return P / P.sum(1, keepdims=True)


for nm, idx in (('val', vai), ('test', tei)):
    results.append(metrics(idx, greedy(idx), f'greedy_pearl|{nm}'))
models = {}
for fs, cols in FS.items():
    Xtr = D.iloc[tri][cols].values.astype(np.float32)
    for depth in (3, 6, 10):
        t = time.time()
        clf = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=200, random_state=0).fit(Xtr, Y[tri])
        Pv = np.zeros((len(vai), len(classes)))
        Pv[:, clf.classes_] = clf.predict_proba(D.iloc[vai][cols].values.astype(np.float32))
        results.append(metrics(vai, Pv, f'tree_d{depth}|{fs}|val') | dict(fit_s=time.time() - t, leaves=clf.get_n_leaves()))
        models[(fs, f'tree_d{depth}')] = clf
    t = time.time()
    hgb = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, max_leaf_nodes=63, min_samples_leaf=100,
                                         early_stopping=True, validation_fraction=0.1, random_state=0).fit(Xtr, Y[tri])
    Pv = np.zeros((len(vai), len(classes)))
    Pv[:, hgb.classes_] = hgb.predict_proba(D.iloc[vai][cols].values.astype(np.float32))
    results.append(metrics(vai, Pv, f'hgb|{fs}|val') | dict(fit_s=time.time() - t, iters=hgb.n_iter_))
    models[(fs, 'hgb')] = hgb
    print(fs, 'done', flush=True)
R = pd.DataFrame(results)
R.to_csv(out / 'val_results.csv', index=False)
print(R[['tag', 'n', 'games', 'acc', 'acc_game_bal', 'macro_f1', 'logloss'] + [c for c in R if c.startswith('recall_')]].round(3).to_string())
import pickle
pickle.dump(dict(models=models, classes=classes, FS=FS), open(out / 'models.pkl', 'wb'))

