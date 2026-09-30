"""HB-1 Q4 (hb1-03): fit the scaled direction model and write it as a binary blob the bot memory-maps.

    .venv/bin/python tools/hb1/q4_export_direction_blob.py [--cap 3000] [--leaves 255] [--jobs N]

Same training games / test rows as q4_direction_scale.py (best point: 3,000 rows per game, 255 leaves, early stop).
Blob layout (little-endian): b'HB1D', int32 K, n_feat, n_trees, n_nodes, n_classes; float32 base[K];
int32 classes[n_classes]; int32 len + '\\n'-joined feature names (padded to 8); int32 tree_start[n_trees] (padded
to 8); nodes as the C++ hb1::Node layout {int16 f; float32 t; int32 yes, no, miss; float32 leaf} (24 bytes).
Writes build/hb1/export/direction_v03.bin, direction_v03_check.csv and game_stats/runs/hb1-q4-direction-v03.json.
"""
import argparse, json, struct, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_decisions as Q1
import q4_direction_scale as S
import q4_fit_export as E

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / 'hb1'
NODE = np.dtype([('f', '<i2'), ('t', '<f4'), ('yes', '<i4'), ('no', '<i4'), ('miss', '<i4'), ('leaf', '<f4')], align=True)


def pad8(b):
    return b + b'\0' * (-len(b) % 8)


def main():
    import xgboost as xgb
    from multiprocessing import Pool
    ap = argparse.ArgumentParser()
    ap.add_argument('--cap', type=int, default=3000)
    ap.add_argument('--leaves', type=int, default=255)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    assert NODE.itemsize == 24, NODE.itemsize
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    test_games = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    paths = [p for p in sorted(B.glob('v5/corpus/*.parquet')) if int(p.stem) not in test_games]
    te = pd.read_parquet(B / 'q1' / 'direction.parquet')
    te = te[te.game.astype(int).isin(test_games)]
    Xte, yte = Q1.xy('direction', te)
    cols = [c for c in Xte.columns if c != 'mem_initial']
    Xte = Xte[cols]
    with Pool(a.jobs) as pool:
        tr = pd.concat(pool.map(S._rows, [(str(p), a.cap) for p in paths], chunksize=8), ignore_index=True)
    Xtr, ytr = Q1.xy('direction', tr)
    Xtr = Xtr.reindex(columns=cols, fill_value=0)
    del tr
    va = np.random.default_rng(Q1.SEED).random(len(ytr)) < 0.1
    m = xgb.XGBClassifier(device='cuda', tree_method='hist', grow_policy='lossguide', max_leaves=a.leaves, max_depth=0,
                          learning_rate=0.1, n_estimators=3000, early_stopping_rounds=30, random_state=Q1.SEED,
                          objective='multi:softprob')
    m.fit(Xtr[~va], ytr[~va], eval_set=[(Xtr[va], ytr[va])], verbose=False)
    p = m.predict_proba(Xte)
    acc = float((p.argmax(1) == yte).mean())
    bst = m.get_booster()
    best = int(m.best_iteration) + 1
    bst = bst[:best]                                   # keep exactly the early-stopped trees
    bst.set_param({'device': 'cpu'})
    trees = E.flatten(bst, cols)
    K = 3
    samp = Xte.iloc[:300].to_numpy(np.float64)
    marg = bst.predict(xgb.DMatrix(samp, feature_names=cols), output_margin=True).reshape(len(samp), K)
    base = np.array([marg[i] - E.leaves_sum(trees, samp[i], K) for i in range(len(samp))])
    assert np.abs(base - base[0]).max() < 1e-3, np.abs(base - base[0]).max()
    base = base[0]
    chk = Xte.iloc[:2000].copy()
    cm = bst.predict(xgb.DMatrix(chk.to_numpy(np.float64), feature_names=cols), output_margin=True).reshape(len(chk), K)
    for j in range(K):
        chk[f'__margin{j}'] = cm[:, j]
    chk.to_csv(B / 'export' / 'direction_v03_check.csv', index=False)
    starts, nodes = [], []
    for t in trees:
        starts.append(len(nodes))
        nodes += t
    arr = np.zeros(len(nodes), NODE)
    arr['f'], arr['t'], arr['yes'], arr['no'], arr['miss'], arr['leaf'] = map(np.array, zip(*nodes))
    names = '\n'.join(cols).encode()
    classes = [int(c) for c in m.classes_]
    blob = (b'HB1D' + struct.pack('<5i', K, len(cols), len(trees), len(nodes), len(classes)) +
            struct.pack(f'<{K}f', *base) + struct.pack(f'<{len(classes)}i', *classes))
    blob = pad8(blob + struct.pack('<i', len(names)) + names)
    blob = pad8(blob + np.array(starts, '<i4').tobytes())
    blob += arr.tobytes()
    out = B / 'export' / 'direction_v03.bin'
    out.write_bytes(blob)
    res = dict(cap=a.cap, leaves=a.leaves, n_train=int((~va).sum()), rounds=best, trees=len(trees), nodes=len(nodes),
               acc_heldout=acc, n_test=int(len(yte)), blob_mb=round(len(blob) / 1e6, 1), base=base.tolist())
    (ROOT / 'game_stats' / 'runs' / 'hb1-q4-direction-v03.json').write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
