"""Pipeline control: same v4 features + same HGB recipe on a known-source local bot (ouroboros-v10-beacon)."""
import glob, sys, json, hashlib
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
sys.path.insert(0, 'tools')
from il_common import feature_sets
fs = sorted(glob.glob(sys.argv[1] + '/*.parquet'))
parts = []
for f in fs:
    x = pd.read_parquet(f); x['gname'] = f.split('/')[-1]
    x = x[x.y_family.isin(['move', 'split'])]
    if len(x) > 4000: x = x.sample(4000, random_state=0)
    parts.append(x)
D = pd.concat(parts, ignore_index=True)
D['y'] = np.where(D.y_family == 'split', np.where(D.y_split == 1, 'suicide', 'split'), D.y_first)
D['split'] = [('test' if int(hashlib.md5(g.encode()).hexdigest(), 16) % 5 == 0 else 'train') for g in D.gname]
cols = feature_sets(D.assign(game=D.gname, round=D['round'], dragon=D.dragon, map=D['map'], split=D.split))['view+mem']
cols = [c for c in cols if c not in ('gname', 'y')]
tr, te = D[D.split == 'train'], D[D.split == 'test']
res = {'games_train': tr.gname.nunique(), 'games_test': te.gname.nunique(), 'rows_test': len(te),
       'class_share_test': te.y.value_counts(normalize=True).round(3).to_dict(),
       'majority': float((te.y == tr.y.mode()[0]).mean())}
for name, clf in [('tree_d6', DecisionTreeClassifier(max_depth=6, min_samples_leaf=200, random_state=0)),
                  ('hgb_m', HistGradientBoostingClassifier(max_iter=120, max_leaf_nodes=31, min_samples_leaf=100, random_state=0))]:
    clf.fit(tr[cols].values.astype(np.float32), tr.y.values)
    p = clf.predict(te[cols].values.astype(np.float32))
    res[name] = float(accuracy_score(te.y.values, p))
    mv = te.y.isin(['F', 'L', 'R']).values
    res[name + '_dir_given_move'] = float((p[mv] == te.y.values[mv]).mean())
print(json.dumps(res, indent=1))
json.dump(res, open(sys.argv[2], 'w'), indent=1)
