"""HB-1 Q1: structure before parameters — five decisions, three model capacities, drop-family ablations.

    .venv/bin/python tools/hb1/q1_decisions.py [--jobs N] [--rebuild] [--no-ablate]

Decisions (all on Heartbreaker's own actor-turn rows from build/hb1/v5/corpus, features_v5):
  gate       split-eligible turns: split or not
  alloc      split turns: child size (capped at 8)
  direction  move turns: first relative step F/R/L
  sonar      turns that emitted: relative ray mask (the action just taken is an input)
  late       r>=350, eligible, length>=8: split or not (the concentration weakness)
Holdout is by game (20 %, fixed seed); map-identifying columns are excluded (OOS rule).
Writes build/hb1/q1/<decision>.parquet samples and game_stats/runs/hb1-q1-gaps.json.
"""
import argparse, glob, json, re, time, os
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / os.environ.get('HB_BUILD', 'hb1')   # HB_BUILD/HB_TEAM/HB_TAG: other teams (lane tt)
TAG = os.environ.get('HB_TAG', 'hb1')
Q = B / 'q1'
OUT = ROOT / 'game_stats' / 'runs' / f'{TAG}-q1-gaps.json'
SEED = 62
CAP = dict(gate=1200, direction=1200, sonar=600, alloc=None, late=None)
MAP_ID = {'W', 'H', 'x', 'y', 'xn', 'yn', 'facing_abs', 'map', 'game', 'dragon'}
LABELS = {'y_family', 'y_first', 'y_nsteps', 'y_seq', 'y_split', 'y_child', 'y_parent', 'y_sonar_n',
          'y_sonar_mask', 'y_sonar_v', 'y_sonar_vset', 'post_died', 'post_reason'}


def family(c):
    if c.startswith('g_'):
        return 'grid'
    if re.match(r'c[FRLB]_', c) or c in ('free_dirs', 'n_exit_ord', 'n_exit_portal', 'n_exit_any'):
        return 'cand'
    if c.startswith(('vis_', 'pearl_', 'enemy_', 'ally_', 'near_')):
        return 'local'
    if c.startswith('echo_') or c in ('n_msgs', 'mem_msgs_total'):
        return 'msgs'
    if c.startswith('mem_'):
        return 'memory'
    if c.startswith('act_'):
        return 'action'
    return 'scalar'


def _sample(path):
    d = pd.read_parquet(path)
    rng = np.random.default_rng(int(Path(path).stem))
    out = {}
    for c in d.columns:
        if not pd.api.types.is_numeric_dtype(d[c]) and c not in LABELS and c not in MAP_ID:
            d[c] = d[c].astype(str)
    sel = dict(
        gate=d[d.split_elig == 1],
        alloc=d[d.y_family == 'split'],
        direction=d[(d.y_family == 'move') & d.y_first.isin(['F', 'R', 'L'])],
        sonar=d[d.y_sonar_n > 0],
        late=d[(d['round'] >= 350) & (d.split_elig == 1) & (d.length >= 8)],
    )
    for k, s in sel.items():
        if CAP[k] and len(s) > CAP[k]:
            s = s.iloc[np.sort(rng.choice(len(s), CAP[k], replace=False))]
        out[k] = s
    return out


def build(jobs):
    Q.mkdir(parents=True, exist_ok=True)
    fs = sorted(glob.glob(str(B / 'v5' / 'corpus' / '*.parquet')))
    parts = {k: [] for k in CAP}
    with Pool(jobs) as p:
        for o in p.imap_unordered(_sample, fs, chunksize=4):
            for k, v in o.items():
                parts[k].append(v)
    for k, v in parts.items():
        pd.concat(v, ignore_index=True).to_parquet(Q / f'{k}.parquet')


def xy(k, d):
    if k in ('gate', 'late'):
        y = (d.y_family == 'split').astype(int).to_numpy()
    elif k == 'alloc':
        y = d.y_child.clip(upper=8).astype(int).to_numpy()
    elif k == 'direction':
        y = d.y_first.map({'F': 0, 'R': 1, 'L': 2}).to_numpy()
    else:
        y = d.y_sonar_mask.astype(int).to_numpy()
        for a in ('F', 'R', 'L', 'split'):
            d = d.assign(**{f'act_{a}': (d.y_first == a).astype(np.int8)})
    X = d[[c for c in d.columns if c not in LABELS and c not in MAP_ID]].copy()
    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype('category').cat.codes
    return X.astype(np.float32), y


def fit_tree(Xtr, ytr, Xte, yte, depth=4):
    from sklearn.tree import DecisionTreeClassifier
    m = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=50, random_state=SEED).fit(Xtr, ytr)
    return m, m.predict_proba(Xte)


class _XGB:
    """XGBoost on the GPU with HistGBT-like settings (63 leaves, lr 0.1, early stop on 10 %), sklearn-shaped.
    The desktop's cores are shared with the R-lane panels; CPU boosting starves there."""

    def __init__(self, iters):
        self.iters = iters

    def fit(self, X, y):
        import xgboost as xgb
        self.classes_ = np.unique(y)
        yi = np.searchsorted(self.classes_, y)
        va = np.random.default_rng(SEED).random(len(yi)) < 0.1
        obj = dict(objective='binary:logistic') if len(self.classes_) == 2 else dict(objective='multi:softprob')
        self.m = xgb.XGBClassifier(device='cuda', tree_method='hist', grow_policy='lossguide', max_leaves=63,
                                   max_depth=0, learning_rate=0.1, n_estimators=self.iters, early_stopping_rounds=15,
                                   random_state=SEED, **obj)
        self.m.fit(X[~va], yi[~va], eval_set=[(X[va], yi[va])], verbose=False)
        return self

    def predict_proba(self, X):
        return self.m.predict_proba(X)

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(1)]


def fit_gbt(Xtr, ytr, Xte, yte, iters=300):
    m = _XGB(iters).fit(Xtr, ytr)
    return m, m.predict_proba(Xte)


def fit_mlp(Xtr, ytr, Xte, yte, epochs=12):
    import torch, torch.nn as nn
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    classes = np.unique(ytr)
    ci = {c: i for i, c in enumerate(classes)}
    mu, sd = Xtr.astype(np.float64).mean(0), Xtr.astype(np.float64).std(0) + 1e-6
    t = lambda a: torch.tensor(((a.astype(np.float64) - mu) / sd).to_numpy(), dtype=torch.float32, device=dev)
    xt, xe = t(Xtr), t(Xte)
    yt = torch.tensor([ci[v] for v in ytr], device=dev)
    torch.manual_seed(SEED)
    net = nn.Sequential(nn.Linear(xt.shape[1], 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU(),
                        nn.Linear(128, len(classes))).to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=2e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    n = len(xt)
    for _ in range(epochs):
        net.train()
        for i in torch.randperm(n, device=dev).split(4096):
            opt.zero_grad()
            nn.functional.cross_entropy(net(xt[i]), yt[i]).backward()
            opt.step()
        sched.step()
    net.eval()
    with torch.no_grad():
        p = torch.cat([net(c).softmax(1) for c in xe.split(65536)]).cpu().numpy()
    # align to the full label set of the test split
    return (net, classes), p


def score(p, classes, yte):
    from sklearn.metrics import log_loss, f1_score
    pred = np.asarray(classes)[p.argmax(1)]
    lab = sorted(set(classes) | set(np.unique(yte)))
    P = np.zeros((len(yte), len(lab)))
    for j, c in enumerate(classes):
        P[:, lab.index(c)] = p[:, j]
    P = np.clip(P, 1e-7, 1)
    P /= P.sum(1, keepdims=True)
    return dict(acc=float((pred == yte).mean()), macro_f1=float(f1_score(yte, pred, average='macro')),
                logloss=float(log_loss(yte, P, labels=lab)))


def baselines(k, d, ytr, yte):
    maj = pd.Series(ytr).mode()[0]
    b = dict(majority=float((yte == maj).mean()))
    if k == 'alloc':
        b['child2'] = float((yte == 2).mean())
        b['len_minus_2'] = float((np.minimum(d.length.to_numpy() - 2, 8) == yte).mean())
    if k in ('gate', 'late'):
        b['split_iff_no_ordinary_exit'] = float(((d.n_exit_ord.to_numpy() == 0).astype(int) == yte).mean())
    if k == 'sonar':
        back = d.y_first.map({'F': 11, 'R': 7, 'L': 13, 'split': 15}).to_numpy()
        b['all_but_new_back'] = float((back == yte).mean())
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=14)
    ap.add_argument('--rebuild', action='store_true')
    ap.add_argument('--no-ablate', action='store_true')
    ap.add_argument('--only', nargs='*')
    a = ap.parse_args()
    if a.rebuild or not (Q / 'gate.parquet').exists():
        t0 = time.time(); build(a.jobs); print(f'samples built {time.time() - t0:.0f}s', flush=True)
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    rng = np.random.default_rng(SEED)
    test_games = set(rng.choice(games, len(games) // 5, replace=False).tolist())
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    res['_meta'] = dict(train_games=len(games) - len(test_games), test_games=len(test_games), seed=SEED,
                        excluded=sorted(MAP_ID))
    for k in a.only or CAP:
        d = pd.read_parquet(Q / f'{k}.parquet')
        te = d.game.astype(int).isin(test_games).to_numpy()
        X, y = xy(k, d)
        Xtr, Xte, ytr, yte = X[~te], X[te], y[~te], y[te]
        r = dict(n_train=int((~te).sum()), n_test=int(te.sum()), classes={str(c): int((y == c).sum()) for c in np.unique(y)},
                 baselines=baselines(k, d[te], ytr, yte))
        for name, f in (('tree4', fit_tree), ('gbt', fit_gbt), ('mlp', fit_mlp)):
            t0 = time.time()
            m, p = f(Xtr, ytr, Xte, yte)
            classes = m[1] if name == 'mlp' else m.classes_
            r[name] = score(p, classes, yte) | dict(sec=round(time.time() - t0, 1))
            print(k, name, r[name], flush=True)
            if name == 'tree4':
                from sklearn.tree import export_text
                r['tree4_rules'] = export_text(m, feature_names=list(X.columns), max_depth=4)
        r['gap_tree_to_mlp'] = r['mlp']['acc'] - r['tree4']['acc']
        r['gap_tree_to_gbt'] = r['gbt']['acc'] - r['tree4']['acc']
        if not a.no_ablate:
            fams = sorted({family(c) for c in X.columns})
            r['ablate'] = {}
            for fam in fams:
                keep = [c for c in X.columns if family(c) != fam]
                m, p = fit_gbt(Xtr[keep], ytr, Xte[keep], yte, iters=150)
                s = score(p, m.classes_, yte)
                r['ablate'][fam] = dict(n_cols=len(X.columns) - len(keep), d_acc=s['acc'] - r['gbt']['acc'],
                                        d_logloss=s['logloss'] - r['gbt']['logloss'])
                print(k, 'drop', fam, r['ablate'][fam], flush=True)
        res[k] = r
        OUT.write_text(json.dumps(res, indent=1))
    print('\n| decision | n test | majority | tree4 | GBT | MLP | gap tree->MLP |')
    print('|---|---:|---:|---:|---:|---:|---:|')
    for k in CAP:
        if k in res:
            r = res[k]
            print(f"| {k} | {r['n_test']:,} | {r['baselines']['majority']:.4f} | {r['tree4']['acc']:.4f} | "
                  f"{r['gbt']['acc']:.4f} | {r['mlp']['acc']:.4f} | {r['gap_tree_to_mlp']:+.4f} |")


if __name__ == '__main__':
    main()
