"""Fixed-recipe imitation check (recipe frozen from the Vibing++ study): chronological whole-game
70/10/20 split, HGB (120 iters x 31 leaves) on v4 view+mem and legal_all; depth-6 tree; majority.
Test scored once.   python3 il_quick.py FEAT MANIFEST SUB OUT.json"""
import sys, json, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from il_common import load, feature_sets
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, log_loss
feat, man, sub, outp = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
D, m, games = load(feat, man, sub)
D = D.copy()
n = len(games); tr = set(games[:int(.8 * n)]); te = set(games[int(.8 * n):])
D['split'] = np.where(D.game.isin(te), 'test', 'train')
FS = feature_sets(D)
classes = sorted(D.y_first.unique())
Y = D.y_first.map({c: i for i, c in enumerate(classes)}).values
tri = np.flatnonzero((D.split == 'train').values); tei = np.flatnonzero((D.split == 'test').values)
res = dict(sub=sub, games_train=len(tr), games_test=len(te), rows_test=len(tei), classes=classes,
           class_share_test={c: float((D.y_first.values[tei] == c).mean()) for c in classes})
prior = np.bincount(Y[tri], minlength=len(classes)) / len(tri)
res['majority_acc'] = float((Y[tei] == prior.argmax()).mean())
for name, fs, clf in [('hgb_view+mem', 'view+mem', HistGradientBoostingClassifier(max_iter=120, max_leaf_nodes=31, min_samples_leaf=100, random_state=0)),
                      ('hgb_legal_all', 'legal_all', HistGradientBoostingClassifier(max_iter=120, max_leaf_nodes=31, min_samples_leaf=100, random_state=0)),
                      ('tree_d6_view+mem', 'view+mem', DecisionTreeClassifier(max_depth=6, min_samples_leaf=200, random_state=0))]:
    cols = FS[fs]
    clf.fit(D.iloc[tri][cols].values.astype(np.float32), Y[tri])
    P = np.zeros((len(tei), len(classes))); P[:, clf.classes_] = clf.predict_proba(D.iloc[tei][cols].values.astype(np.float32))
    pred = P.argmax(1)
    res[name] = dict(acc=float(accuracy_score(Y[tei], pred)), macro_f1=float(f1_score(Y[tei], pred, average='macro')),
                     logloss=float(log_loss(Y[tei], np.clip(P, 1e-6, 1) / np.clip(P, 1e-6, 1).sum(1, keepdims=True), labels=list(range(len(classes))))))
    fd = D.iloc[tei].free_dirs.values
    res[name]['acc_by_free_dirs'] = {int(k): float((pred[fd == k] == Y[tei][fd == k]).mean()) for k in sorted(set(fd)) if (fd == k).sum() > 200}
    print(name, res[name], flush=True)
json.dump(res, open(outp, 'w'), indent=1)
