"""Hinata R2 (P1) — behaviour-cloning direction head on encoder v1 rows (draft card P-hinata-03). DEVELOPMENT ONLY.

  fit  --rows <parquet>[,<parquet>...] --teachers build/learn/kageyama/teachers_v1.parquet --run build/hinata/r2/<run>
       [--cv series5|lomo|game] [--frac 1.0] [--budget 150] [--rounds 400]

What it does (one change: the head; features are encoder v1 exactly as Data writes them):
  rows   dataset.py output (meta + x_* int16 + y_*); kept: teacher sides only (inner join on game, side), move turns
         (y_kind == 0) with y_first in F/R/B/L. Refuses any row whose split is not 'train' or whose map is held out.
  label  y_first (0 F, 1 R, 2 B, 3 L), relative to the facing at turn start (labels.py v1).
  model  LightGBM multiclass, 4 classes; sample weight = teacher weight (Elo x recency, teachers_v1) — reported both ways.
  cv     series5: 5 folds grouped by series_key (hash-assigned, so a series never straddles train and test);
         lomo: leave-one-map-out over the training maps; game: leave-one-game-out (plumbing on tiny files only).
  out    oof.parquet, metrics.json (accuracy overall / queen turns / per map / per teacher team, majority-class and
         'forward' baselines, log loss, learning curve when --frac < 1), registry.json (data sha, code sha, params, size).
Never reads held-out maps, test or validation buckets; no map identity in features (encoder v1 emits none; asserted).
Resumable: each fold's model is saved; a rerun skips finished folds. Use --budget <= 150 s on the VM.
"""
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path.cwd(); HELDOUT = ROOT / 'docs/learning/splits/heldout-maps.json'
PARAMS = dict(objective='multiclass', num_class=4, learning_rate=0.08, num_leaves=63, min_data_in_leaf=100,
              feature_fraction=0.5, bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, verbose=-1, num_threads=3, seed=7)
BANNED = ('map', 'width', 'height', 'abs_x', 'abs_y', 'x_x', 'x_y', 'facing_abs')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(paths, teachers):
    hm = set(json.loads(HELDOUT.read_text())['heldout_maps'])
    d = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    assert (d.split == 'train').all(), f'non-train rows: {d.split.value_counts().to_dict()}'
    assert not d['map'].isin(hm).any(), 'held-out map rows present'
    t = pd.read_parquet(teachers)[['game', 'side', 'team', 'weight']]
    d = d.merge(t, on=['game', 'side'], how='inner')
    d = d[(d.y_kind == 0) & d.y_first.between(0, 3)].reset_index(drop=True)
    X = [c for c in d.columns if c.startswith('x_')]
    assert not [c for c in X if any(b == c[2:] or c[2:].startswith(b + '_') for b in BANNED)], 'map-identity column in features'
    return d, X


def folds(d, cv):
    if cv == 'game':
        return {g: (d.game == g).to_numpy() for g in sorted(d.game.unique())}
    if cv == 'lomo':
        return {m: (d['map'] == m).to_numpy() for m in sorted(d['map'].unique())}
    k = d.series_key.map(lambda s: int(hashlib.sha256(f'hinata-r2/{s}'.encode()).hexdigest(), 16) % 5)
    return {f'f{i}': (k == i).to_numpy() for i in range(5)}


def acc(y, p, m=None):
    m = np.ones(len(y), bool) if m is None else m
    return dict(n=int(m.sum()), acc=float((p.argmax(1)[m] == y[m]).mean()) if m.any() else None)


def main():
    import lightgbm as lgb
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['fit'])
    ap.add_argument('--rows', required=True); ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet')
    ap.add_argument('--run', required=True); ap.add_argument('--cv', default='series5', choices=['series5', 'lomo', 'game'])
    ap.add_argument('--frac', type=float, default=1.0); ap.add_argument('--budget', type=float, default=150); ap.add_argument('--rounds', type=int, default=400)
    ap.add_argument('--unweighted', action='store_true')
    a = ap.parse_args(); t0 = time.time(); run = Path(a.run); run.mkdir(parents=True, exist_ok=True)
    paths = a.rows.split(','); d, X = load(paths, a.teachers)
    if a.frac < 1:                                     # learning-curve point: subsample training SERIES, not rows
        keep = d.series_key.map(lambda s: int(hashlib.sha256(f'frac/{s}'.encode()).hexdigest(), 16) % 1000 < a.frac * 1000)
        d = d[keep].reset_index(drop=True)
    y = d.y_first.to_numpy(int); w = np.ones(len(d)) if a.unweighted else d.weight.to_numpy(float)
    F = folds(d, a.cv); P = np.full((len(d), 4), np.nan)
    for name, te in F.items():
        mf = run / f'model_{name}.txt'
        if not mf.exists():
            if time.time() - t0 > a.budget:
                print('budget reached; rerun to resume'); break
            tr = ~te
            b = lgb.train(PARAMS, lgb.Dataset(d.loc[tr, X].to_numpy(np.float32), y[tr], weight=w[tr]), num_boost_round=a.rounds)
            b.save_model(str(mf))
        b = lgb.Booster(model_file=str(mf)); P[te] = b.predict(d.loc[te, X].to_numpy(np.float32))
    done = ~np.isnan(P).any(1)
    oof = d.loc[done, ['game', 'side', 'dragon', 'round', 'map', 'team', 'series_key', 'x_is_queen', 'y_first']].assign(
        p_F=P[done, 0], p_R=P[done, 1], p_B=P[done, 2], p_L=P[done, 3])
    oof.to_parquet(run / 'oof.parquet')
    yy, pp = y[done], P[done]; q = d.loc[done, 'x_is_queen'].to_numpy() == 1
    prior = np.bincount(y, minlength=4) / len(y)
    met = dict(rows=int(len(d)), scored=int(done.sum()), folds_done=int(sum((run / f'model_{n}.txt').exists() for n in F)), folds=len(F),
               all=acc(yy, pp), queen=acc(yy, pp, q), nonqueen=acc(yy, pp, ~q),
               baseline_majority=float((yy == prior.argmax()).mean()) if len(yy) else None, class_share=prior.round(4).tolist(),
               logloss=float(-np.mean(np.log(np.clip(pp[np.arange(len(yy)), yy], 1e-9, 1)))) if len(yy) else None,
               per_map={m: acc(yy, pp, (oof['map'] == m).to_numpy()) for m in sorted(oof['map'].unique())},
               per_team={t: acc(yy, pp, (oof.team == t).to_numpy()) for t in sorted(oof.team.unique())},
               interval='none (development; the gate interval is whole-series bootstrap, card §4)')
    (run / 'metrics.json').write_text(json.dumps(met, indent=1))
    models = sorted(run.glob('model_*.txt'))
    reg = dict(artifact='hinata-p1-dev', status='development', rows_sha=[sha(p) for p in paths], teachers_sha=sha(a.teachers),
               code_sha=sha(__file__), features=f'encoder v1: {len(X)} x_* columns', label='labels v1 y_first, move turns',
               params=PARAMS, rounds=a.rounds, cv=a.cv, frac=a.frac, weighted=not a.unweighted,
               model_bytes=int(np.mean([m.stat().st_size for m in models])) if models else None, metrics=met)
    (run / 'registry.json').write_text(json.dumps(reg, indent=1, default=str))
    print(json.dumps({k: met[k] for k in ('rows', 'scored', 'folds_done', 'folds', 'all', 'queen', 'baseline_majority', 'logloss')}, indent=1),
          f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
