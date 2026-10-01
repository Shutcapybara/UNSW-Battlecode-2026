"""HB-1 Q4: fit the mimic's four GBTs on the training games and export them as a C++ header.

    .venv/bin/python tools/hb1/q4_fit_export.py

Models (GPU XGBoost, same settings as Q1), fitted on the 654 Q1 training games only; the 163 held-out games stay
untouched for fidelity. mem_initial is dropped (the bot cannot observe it).
  gate       split-eligible turns: split?                         (binary)
  alloc      split turns: child size 2..8                         (multiclass)
  direction  move turns: F / R / L                                (multiclass)
  sonar      emitting turns: relative ray mask, given the action  (multiclass)
Writes bots/hb1-01-structured/hb1_models.hpp and build/hb1/export/<model>_check.csv (held-out feature rows with the
Python margins) for the C++ evaluator parity check, and game_stats/runs/hb1-q4-export.json.
"""
import glob, json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_decisions as Q1

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / os.environ.get('HB_BUILD', 'hb1')    # lane tt: other teams
TAG = os.environ.get('HB_TAG', 'hb1')
EXP = B / 'export'
HDR = ROOT / 'bots' / os.environ.get('HB_BOT', 'hb1-01-structured') / 'hb1_models.hpp'
OUT = ROOT / 'game_stats' / 'runs' / f'{TAG}-q4-export.json'
DROP = {'mem_initial'}
MODELS = tuple(os.environ.get('HB_MODELS', 'gate,alloc,direction,sonar').split(','))
# boosting-round caps: the near-rule decisions need far fewer trees than direction (header size; see status)
ROUNDS = dict(gate=120, alloc=40, direction=300, sonar=40, cull=120)
CULL_PER_GAME = 400


def _cull_rows(path):
    """All turns (self-kill = an invalid command or a backward step), sampled uniformly per game - unweighted, so the
    model's probabilities stay calibrated to the team's real self-kill rate."""
    import numpy as np
    d = pd.read_parquet(path)
    if len(d) > CULL_PER_GAME:
        d = d.iloc[np.sort(np.random.default_rng(int(Path(path).stem) + 3).choice(len(d), CULL_PER_GAME, replace=False))]
    for c in d.columns:
        if not pd.api.types.is_numeric_dtype(d[c]) and c not in Q1.LABELS and c not in Q1.MAP_ID:
            d[c] = d[c].astype(str)
    return d


def load(k):
    if k != 'cull':
        return pd.read_parquet(B / 'q1' / f'{k}.parquet')
    p = B / 'q1' / 'cull.parquet'
    if not p.exists():
        from multiprocessing import Pool
        with Pool(12) as pool:
            pd.concat(pool.map(_cull_rows, sorted(glob.glob(str(B / 'v5' / 'corpus' / '*.parquet'))), chunksize=8),
                      ignore_index=True).to_parquet(p)
    return pd.read_parquet(p)


def xy(k, d):
    if k != 'cull':
        return Q1.xy(k, d)
    X, _ = Q1.xy('gate', d)
    return X, (~d.y_first.isin(['F', 'R', 'L', 'split'])).astype(int).to_numpy()


def flatten(booster, feats):
    """-> list of trees, each a list of nodes (feat, thr, yes, no, missing, leaf) with node ids = list index."""
    fi = {f: i for i, f in enumerate(feats)}
    trees = []
    for js in booster.get_dump(dump_format='json'):
        t = json.loads(js)
        nodes = {}

        def walk(n):
            if 'leaf' in n:
                nodes[n['nodeid']] = (-1, 0.0, -1, -1, -1, float(n['leaf']))
                return
            nodes[n['nodeid']] = (fi[n['split']], float(n['split_condition']), n['yes'], n['no'], n['missing'], 0.0)
            for c in n['children']:
                walk(c)
        walk(t)
        remap = {nid: i for i, nid in enumerate(sorted(nodes))}
        trees.append([(f, th, remap.get(y, -1), remap.get(no, -1), remap.get(m, -1), lf)
                      for nid, (f, th, y, no, m, lf) in sorted(nodes.items())])
    return trees


def leaves_sum(trees, x, k):
    s = np.zeros(k)
    for i, t in enumerate(trees):
        n = 0
        while t[n][0] >= 0:
            f, th, y, no, m, _ = t[n]
            v = x[f]
            n = m if np.isnan(v) else (y if np.float32(v) < np.float32(th) else no)
        s[i % k] += t[n][5]
    return s


def main():
    import xgboost as xgb
    EXP.mkdir(parents=True, exist_ok=True)
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    test_games = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    res, blobs = {}, []
    for k in MODELS:
        d = load(k)
        te = d.game.astype(int).isin(test_games).to_numpy()
        X, y = xy(k, d)
        X = X[[c for c in X.columns if c not in DROP]]
        m = Q1._XGB(ROUNDS[k]).fit(X[~te], y[~te])
        p = m.predict_proba(X[te])
        acc = float((m.classes_[p.argmax(1)] == y[te]).mean())
        bst = m.m.get_booster()
        bst.set_param({'device': 'cpu'})
        feats = list(X.columns)
        trees = flatten(bst, feats)
        K = 1 if len(m.classes_) == 2 else len(m.classes_)
        # per-class base margin, recovered empirically and checked constant
        samp = X[te].iloc[:500].to_numpy(np.float64)
        marg = bst.predict(xgb.DMatrix(samp, feature_names=feats), output_margin=True).reshape(len(samp), K)
        base = np.array([marg[i] - leaves_sum(trees, samp[i], K) for i in range(len(samp))])
        assert np.abs(base - base[0]).max() < 1e-4, (k, np.abs(base - base[0]).max())
        base = base[0]
        chk = X[te].iloc[:2000].copy()
        cm = bst.predict(xgb.DMatrix(chk.to_numpy(np.float64), feature_names=feats), output_margin=True).reshape(len(chk), K)
        for j in range(K):
            chk[f'__margin{j}'] = cm[:, j]
        chk.to_csv(EXP / f'{k}_check.csv', index=False)
        n_nodes = sum(len(t) for t in trees)
        res[k] = dict(acc_heldout=acc, n_test=int(te.sum()), classes=[int(c) for c in m.classes_], K=K,
                      trees=len(trees), nodes=n_nodes, features=len(feats), base=base.tolist())
        print(k, {a: b for a, b in res[k].items() if a != 'base'}, flush=True)
        blobs.append((k, feats, [int(c) for c in m.classes_], K, base, trees))
    write_header(blobs)
    OUT.write_text(json.dumps(res, indent=1))


def F(x):
    """C++ float literal that always carries a decimal point or exponent."""
    t = f'{x:.8g}'
    if not any(c in t for c in '.en'):
        t += '.0'
    return t + 'f'


def write_header(blobs):
    L = ['// generated by tools/hb1/q4_fit_export.py - do not edit.',
         '// HB-1 mimic models: XGBoost trees fitted on the 654 Q1 training games (Heartbreaker, team 62).',
         '// Node: {feature, threshold, yes, no, missing, leaf}; feature < 0 marks a leaf. x < threshold -> yes.',
         '#pragma once', '#include <array>', '', 'namespace hb1 {',
         'struct Node { short f; float t; int yes, no, miss; float leaf; };',
         'struct Model { char const* name; int n_feat; char const* const* feats; int K; int n_class;',
         '               int const* classes; float const* base; int n_trees; int const* tree_start; Node const* nodes; };', '']
    for k, feats, classes, K, base, trees in blobs:
        L.append(f'inline constexpr char const* {k}_feats[] = {{' + ', '.join(f'"{f}"' for f in feats) + '};')
        L.append(f'inline constexpr int {k}_classes[] = {{' + ', '.join(map(str, classes)) + '};')
        L.append(f'inline constexpr float {k}_base[] = {{' + ', '.join(F(b) for b in base) + '};')
        starts, nodes = [], []
        for t in trees:
            starts.append(len(nodes))
            nodes += t
        L.append(f'inline constexpr int {k}_tree_start[] = {{' + ', '.join(map(str, starts)) + '};')
        L.append(f'inline constexpr Node {k}_nodes[] = {{')
        for i in range(0, len(nodes), 8):
            L.append(''.join(f'{{{f},{F(th)},{y},{no},{m},{F(lf)}}},' for f, th, y, no, m, lf in nodes[i:i + 8]))
        L.append('};')
        L.append(f'inline constexpr Model {k}_model{{"{k}", {len(feats)}, {k}_feats, {K}, {len(classes)}, {k}_classes, '
                 f'{k}_base, {len(trees)}, {k}_tree_start, {k}_nodes}};')
        L.append('')
    L.append('}  // namespace hb1')
    HDR.write_text('\n'.join(L) + '\n')
    print('header', HDR, f'{HDR.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
