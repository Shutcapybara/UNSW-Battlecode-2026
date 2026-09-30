"""HB-1 Q4: does the direction model improve with more data, larger trees and more rounds?

    .venv/bin/python tools/hb1/q4_direction_scale.py [--jobs N]

Training rows: move turns (F/R/L) from the 654 Q1 training games, capped per game at 1,200 (the hb1-01 setting),
3,000 and 6,000. Test rows: exactly the Q1 held-out direction rows (build/hb1/q1/direction.parquet, 163 games),
so every number is comparable with hb1-01's 0.829. GPU XGBoost, lr 0.1, early stop 30 on a 10 % validation split,
up to 3,000 rounds. mem_initial and map-identifying columns excluded. Writes game_stats/runs/hb1-q4-direction-scale.json.
"""
import argparse, glob, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_decisions as Q1

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / 'hb1'
OUT = ROOT / 'game_stats' / 'runs' / 'hb1-q4-direction-scale.json'
CAPS = (1200, 3000, 6000)
LEAVES = (63, 255)


def _rows(args):
    path, cap = args
    d = pd.read_parquet(path)
    d = d[(d.y_family == 'move') & d.y_first.isin(['F', 'R', 'L'])]
    if len(d) > cap:
        rng = np.random.default_rng(int(Path(path).stem) + 7)
        d = d.iloc[np.sort(rng.choice(len(d), cap, replace=False))]
    for c in d.columns:
        if not pd.api.types.is_numeric_dtype(d[c]) and c not in Q1.LABELS and c not in Q1.MAP_ID:
            d[c] = d[c].astype(str)
    return d


def main():
    import xgboost as xgb
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    test_games = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    train_paths = [p for p in sorted(glob.glob(str(B / 'v5' / 'corpus' / '*.parquet')))
                   if int(Path(p).stem) not in test_games]
    te = pd.read_parquet(B / 'q1' / 'direction.parquet')
    te = te[te.game.astype(int).isin(test_games)]
    Xte, yte = Q1.xy('direction', te)
    cols = [c for c in Xte.columns if c != 'mem_initial']
    Xte = Xte[cols]
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    res['n_test'] = int(len(yte))
    for cap in CAPS:
        with Pool(a.jobs) as pool:
            tr = pd.concat(pool.map(_rows, [(p, cap) for p in train_paths], chunksize=8), ignore_index=True)
        Xtr, ytr = Q1.xy('direction', tr)
        Xtr = Xtr.reindex(columns=cols, fill_value=0)
        del tr
        va = np.random.default_rng(Q1.SEED).random(len(ytr)) < 0.1
        for leaves in LEAVES:
            key = f'cap{cap}_leaves{leaves}'
            if key in res:
                print(key, res[key], flush=True)
                continue
            t0 = time.time()
            m = xgb.XGBClassifier(device='cuda', tree_method='hist', grow_policy='lossguide', max_leaves=leaves,
                                  max_depth=0, learning_rate=0.1, n_estimators=3000, early_stopping_rounds=30,
                                  random_state=Q1.SEED, objective='multi:softprob')
            m.fit(Xtr[~va], ytr[~va], eval_set=[(Xtr[va], ytr[va])], verbose=False)
            p = m.predict_proba(Xte)
            res[key] = dict(n_train=int((~va).sum()), rounds=int(m.best_iteration) + 1,
                            acc=float((p.argmax(1) == yte).mean()), sec=round(time.time() - t0))
            print(key, res[key], flush=True)
            OUT.write_text(json.dumps(res, indent=1))
        del Xtr, ytr


if __name__ == '__main__':
    main()
