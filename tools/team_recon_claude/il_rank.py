"""Hierarchical candidate-ranking imitation model.

family model (move / split / suicide) x candidate ranker over {F,R,L} first steps.
The ranker sees each candidate's own descriptors (c?_*) in a shared column space plus
decision context, so one learned scoring function ranks all three candidates
(a conditional-logit-style choice model fitted with gradient-boosted trees).
    python3 il_rank.py FEAT MANIFEST OUT SPLITS SUB [--test]
"""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, accuracy_score, f1_score, recall_score
sys.path.insert(0, str(Path(__file__).parent))
from il_common import load, feature_sets

feat, manifest, outd, splits, sub = sys.argv[1:6]
test = '--test' in sys.argv
outd = Path(outd); outd.mkdir(parents=True, exist_ok=True)
sp = json.load(open(splits))
D, m, games = load(feat, manifest, int(sub))
D = D.copy()
D['split'] = D.game.map({g: k for k in ('train', 'val', 'test') for g in sp[k]})
FS = feature_sets(D)
legal = FS['legal_all']
cand_cols = sorted({c[3:] for c in D.columns if c[:1] == 'c' and c[1:2] in 'FRLB' and c[2:3] == '_'})
ctx = [c for c in legal if not (c[:1] == 'c' and c[1:2] in 'FRLB' and c[2:3] == '_') and not c.startswith('g_')]
grid = [c for c in legal if c.startswith('g_')]
classes = ['F', 'L', 'R', 'split', 'suicide']
Y = D.y_first.map({c: i for i, c in enumerate(classes)}).values
tr = np.flatnonzero((D.split == 'train').values)
ev = np.flatnonzero((D.split == ('test' if test else 'val')).values)
rng = np.random.default_rng(0)
if len(tr) > 400000:
    tr = rng.choice(tr, 400000, replace=False)
fam = np.where(D.y_first.isin(['F', 'L', 'R']), 0, np.where(D.y_first == 'split', 1, 2))
t = time.time()
famclf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=63, min_samples_leaf=100, early_stopping=True,
                                        random_state=0).fit(D.iloc[tr][legal].values.astype(np.float32), fam[tr])


def long_table(idx):
    X = D.iloc[idx]
    parts = []
    for k, rel in enumerate('FRL'):
        c = X[[f'c{rel}_{n}' for n in cand_cols]].values.astype(np.float32)
        parts.append(np.hstack([c, np.full((len(X), 1), k, np.float32), X[ctx].values.astype(np.float32)]))
    return parts


mv = tr[fam[tr] == 0]
parts = long_table(mv)
Xl = np.vstack(parts)
yl = np.concatenate([(D.y_first.values[mv] == rel).astype(int) for rel in 'FRL'])
ranker = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=63, min_samples_leaf=100, early_stopping=True,
                                        random_state=0).fit(Xl, yl)
print('fit', round(time.time() - t), 's', flush=True)
pf = famclf.predict_proba(D.iloc[ev][legal].values.astype(np.float32))
sc = np.column_stack([ranker.predict_proba(p)[:, 1] for p in long_table(ev)])
sc = sc / np.clip(sc.sum(1, keepdims=True), 1e-9, None)
P = np.zeros((len(ev), 5))
P[:, 0] = pf[:, 0] * sc[:, 0]; P[:, 2] = pf[:, 0] * sc[:, 1]; P[:, 1] = pf[:, 0] * sc[:, 2]
P[:, 3] = pf[:, 1]; P[:, 4] = pf[:, 2]
y = Y[ev]; pred = P.argmax(1); g = D.game.values[ev]
P2 = np.clip(P, 1e-6, 1); P2 /= P2.sum(1, keepdims=True)
r = dict(tag=f"rank|{'test' if test else 'val'}", n=len(ev), games=len(set(g)), acc=accuracy_score(y, pred),
         acc_game_bal=pd.Series(pred == y).groupby(g).mean().mean(), macro_f1=f1_score(y, pred, average='macro'),
         logloss=log_loss(y, P2, labels=list(range(5))))
for c, v in zip(classes, recall_score(y, pred, average=None, labels=list(range(5)), zero_division=0)):
    r['recall_' + c] = v
mvmask = fam[ev] == 0
r['move_dir_acc_given_move'] = float((sc[mvmask].argmax(1) == np.array([{'F': 0, 'R': 1, 'L': 2}[v] for v in D.y_first.values[ev][mvmask]])).mean())
print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, indent=0))
pd.DataFrame([r]).to_csv(outd / f"rank_{'test' if test else 'val'}.csv", index=False)
import pickle
pickle.dump(dict(fam=famclf, ranker=ranker, legal=legal, ctx=ctx, cand_cols=cand_cols), open(outd / 'rank_models.pkl', 'wb'))
