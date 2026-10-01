"""Verso tier 2: fit decision heads (XGBoost on the GPU) and write boosters for export.py.

    # cycle 0: `dir` head on corpus targets (another team's first step F/R/L), v5 features only
    .venv/bin/python tools/verso/train_heads.py corpus --name c0-hb --teams 62[:cap][,70:600] [--cap 3000] [--leaves 255]
                                                       [--rounds 3000] [--mirror] [--won-only]
    # cycle >= 1: heads on our own dumps (tools/verso/dataset.py)
    .venv/bin/python tools/verso/train_heads.py own --name c1-q --data build/verso/data/c1 --head q|dir ...

Corpus rows are HB-1's v5 actor-turn rows (tools/team_recon_claude/features_v5.py), which are bit-identical to
the bot's own v5 block (hb1_features.hpp). They are read from the lanes that extracted them:
team 62 Heartbreaker (../wt-hb1/build/hb1), 70 cheji bt and 206 Stockfish (../wt-tt/build/tt/team<id>).
Held-out = 20 % of each team's corpus games, by game, seed 62 (HB-1's split for team 62).
Writes build/verso/models/<name>/{dir.ubj, dir.ubj.features.json, meta.json, check.npy}.
"""
from __future__ import annotations

import argparse, glob, json, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

TEAM_ROOT = {62: C.ROOT.parent / 'wt-hb1/build/hb1', 70: C.ROOT.parent / 'wt-tt/build/tt/team70',
             206: C.ROOT.parent / 'wt-tt/build/tt/team206'}


def _rows(args):
    import pandas as pd
    path, cap, cols, max_round = args
    d = pd.read_parquet(path, columns=cols + ['y_family', 'y_first'])
    d = d[(d.y_family == 'move') & d.y_first.isin(C.RELS)]
    if max_round:
        d = d[d['round'] <= max_round]
    if cap and len(d) > cap:
        rng = np.random.default_rng(int(Path(path).stem) + 7)
        d = d.iloc[np.sort(rng.choice(len(d), cap, replace=False))]
    y = d.y_first.map({'F': 0, 'R': 1, 'L': 2}).to_numpy(np.int8)
    return d[cols].to_numpy(np.float32), y


SINCE = ''
EXTRA_HOLDOUT = {}   # team -> build dir whose own held-out games must also stay out of training


def corpus_xy(team, cols, cap, jobs, won_only=False, max_round=0):
    import pandas as pd
    root = TEAM_ROOT[team]
    G = pd.read_parquet(root / 'games.parquet')
    G = G[G.set == 'corpus']
    test = C.holdout(G.game.astype(int).tolist())
    if team in EXTRA_HOLDOUT:   # e.g. HB-1's 163 held-out games, so old and new models share a test set
        G0 = pd.read_parquet(Path(EXTRA_HOLDOUT[team]) / 'games.parquet')
        test |= C.holdout(G0[G0.set == 'corpus'].game.astype(int).tolist())
    if won_only:
        G = G[G.won]
    if SINCE:
        G = G[G.t >= pd.Timestamp(SINCE, tz='UTC')]
    out = {}
    for part, games in (('train', [g for g in G.game.astype(int) if g not in test]),
                        ('test', [g for g in G.game.astype(int) if g in test])):
        paths = [str(root / 'v5' / 'corpus' / f'{g}.parquet') for g in games]
        paths = [p for p in paths if Path(p).exists()]
        with Pool(jobs) as pool:
            parts = pool.map(_rows, [(p, cap, cols, max_round) for p in paths], chunksize=8)
        out[part] = (np.concatenate([p[0] for p in parts]), np.concatenate([p[1] for p in parts]), len(paths))
    return out


def fit_softmax(Xtr, ytr, Xva, yva, feats, leaves, rounds, lr=0.1, seed=C.SEED, weight=None):
    import xgboost as xgb
    params = dict(device='cuda', tree_method='hist', grow_policy='lossguide', max_leaves=leaves, max_depth=0,
                  learning_rate=lr, objective='multi:softprob', num_class=3, seed=seed, max_bin=256)
    dtr = xgb.QuantileDMatrix(Xtr, label=ytr, weight=weight, feature_names=feats, max_bin=256)
    dva = xgb.QuantileDMatrix(Xva, label=yva, feature_names=feats, ref=dtr)
    b = xgb.train(params, dtr, num_boost_round=rounds, evals=[(dva, 'va')], early_stopping_rounds=30,
                  verbose_eval=200)
    return b[: b.best_iteration + 1]


def cmd_corpus(a):
    import xgboost as xgb
    _, names = C.schema(a.bot)
    blk = C.block(names)
    feats = [n for n, b in zip(names, blk) if b == 'v5']
    global SINCE
    SINCE = a.since or ''
    for eh in (a.extra_holdout or []):
        k, v = eh.split('=')
        EXTRA_HOLDOUT[int(k)] = v
    for tr_ in (a.team_root or []):
        k, v = tr_.split('=')
        TEAM_ROOT[int(k)] = Path(v).resolve()
    teams = [int(t.split(':')[0]) for t in a.teams.split(',')]
    caps = {int(t.split(':')[0]): int(t.split(':')[1]) for t in a.teams.split(',') if ':' in t}
    out = C.MODELS / a.name
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    tr, te, meta = [], {}, dict(name=a.name, teams=teams, cap=a.cap, leaves=a.leaves, mirror=a.mirror,
                                won_only=a.won_only, features=len(feats), by_team={})
    for t in teams:
        d = corpus_xy(t, feats, caps.get(t, a.cap), a.jobs, a.won_only, a.max_round)
        tr.append(d['train'][:2]); te[t] = d['test'][:2]
        meta['by_team'][t] = dict(train_games=d['train'][2], test_games=d['test'][2],
                                  train_rows=int(len(d['train'][1])), test_rows=int(len(d['test'][1])))
        print(t, meta['by_team'][t], f'{time.time() - t0:.0f}s', flush=True)
    X = np.concatenate([x for x, _ in tr]); y = np.concatenate([v for _, v in tr])
    del tr
    va = np.random.default_rng(C.SEED).random(len(y)) < 0.1
    Xva, yva = X[va], y[va]
    Xtr, ytr = X[~va], y[~va]
    del X
    if a.mirror:
        Xm, ym = C.mirror(Xtr, ytr, feats)
        Xtr = np.concatenate([Xtr, Xm]); ytr = np.concatenate([ytr, ym])
        del Xm
    b = fit_softmax(Xtr, ytr, Xva, yva, feats, a.leaves, a.rounds)
    b.save_model(str(out / 'dir.ubj'))
    (out / 'dir.ubj.features.json').write_text(json.dumps(feats))
    meta.update(rounds=int(b.num_boosted_rounds()), train_rows=int(len(ytr)), sec=round(time.time() - t0),
                roots={t: str(TEAM_ROOT[t]) for t in teams})
    for t, (Xt, yt) in te.items():
        p = b.predict(xgb.DMatrix(Xt, feature_names=feats))
        meta['by_team'][t]['acc'] = float((p.argmax(1) == yt).mean())
        if a.mirror:  # mirror consistency: the mirrored state should get the mirrored answer
            Xm, ym = C.mirror(Xt, yt.copy(), feats)
            meta['by_team'][t]['acc_mirrored'] = float((b.predict(xgb.DMatrix(Xm, feature_names=feats)).argmax(1) == ym).mean())
    # schema-ordered probe rows for the C++ parity check
    k = list(te)[0]
    chk = np.zeros((min(3000, len(te[k][0])), len(names)), np.float32)
    chk[:, [names.index(f) for f in feats]] = te[k][0][: len(chk)]
    np.save(out / 'check.npy', chk)
    (out / 'meta.json').write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


# ----------------------------------------------------------------------------------------------- own data
def rel_of(H):
    """relative first step of each row: 0 F, 1 R, 2 L, -1 for anything else (split, sprint, reverse)."""
    r = (H[:, 12] - H[:, 7]) % 4
    k = np.full(len(H), -1, np.int8)
    ok = (H[:, 11] == 0) & (H[:, 13] == 1) & (H[:, 12] >= 0)
    k[ok & (r == 0)] = 0; k[ok & (r == 1)] = 1; k[ok & (r == 3)] = 2
    return k


def target(Y, horizon, unit_value):
    import dataset as D
    i = D.YCOLS.index(f'dlen_{horizon}')
    return Y[:, i] + unit_value * Y[:, i + 1]


def fit_reg(Xtr, ytr, Xva, yva, feats, leaves, rounds, lr, seed=C.SEED, min_child=50):
    import xgboost as xgb
    params = dict(device='cuda', tree_method='hist', grow_policy='lossguide', max_leaves=leaves, max_depth=0,
                  learning_rate=lr, objective='reg:squarederror', seed=seed, max_bin=256,
                  min_child_weight=min_child, subsample=0.8, colsample_bytree=0.8, reg_lambda=5.0)
    dtr = xgb.QuantileDMatrix(Xtr, label=ytr, feature_names=feats, max_bin=256)
    dva = xgb.QuantileDMatrix(Xva, label=yva, feature_names=feats, ref=dtr)
    b = xgb.train(params, dtr, num_boost_round=rounds, evals=[(dva, 'va')], early_stopping_rounds=40,
                  verbose_eval=False)
    return b[: b.best_iteration + 1]


def predict(b, X, feats):
    import xgboost as xgb
    return b.predict(xgb.DMatrix(X, feature_names=feats))


def select_features(names, blocks):
    blk = C.block(names)
    keep = [i for i, b in enumerate(blk) if b in blocks]
    # the clock is kept as a soft prior (s_clock / round); nothing in the schema identifies the map
    return keep, [names[i] for i in keep]


def cmd_own(a):
    """Tier 3 (A): Monte-Carlo Q from exploratory self-play.
    Stage 1 fits V(s) on every move row (cross-fitted by game); stage 2 fits, per first step k, the residual
    return G - V(s) of the rows that took k (mirror-augmented). The `q` head is the three residual regressors; the
    bot adds beta * (A_k - max A) to the path score."""
    import dataset as D
    _, names = C.schema(a.bot)
    cols, feats = select_features(names, set(a.blocks.split(',')))
    out = C.MODELS / a.name
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    Hs, Xs, Ys, Gs, off = [], [], [], [], 0
    for arm in a.data.split(','):
        H, X, Y, G, gn = D.load(arm, a.panel, cols=cols, limit=a.limit or None)
        Hs.append(H); Xs.append(X); Ys.append(Y); Gs.append(G + off); off += len(gn)
    H, X, Y, G = np.concatenate(Hs), np.concatenate(Xs), np.concatenate(Ys), np.concatenate(Gs)
    del Hs, Xs, Ys
    k = rel_of(H)
    keep = k >= 0
    H, X, Y, G, k = H[keep], X[keep], Y[keep], G[keep], k[keep]
    y = target(Y, a.horizon, a.unit_value).astype(np.float32)
    explored = (H[:, 14] & 1) > 0
    rng = np.random.default_rng(C.SEED)
    gperm = rng.permutation(off)
    fold = np.empty(off, np.int8)
    fold[gperm] = np.arange(off) % 5          # fold 0 = held-out games; 1-4 train (1 also early-stop validation)
    f = fold[G]
    te, va = f == 0, f == 1
    tr = ~te
    print(f'rows {len(y)} (explored {int(explored.sum())}), games {off}, features {len(feats)}, '
          f'target mean {y.mean():.3f} sd {y.std():.3f}, load {time.time() - t0:.0f}s', flush=True)
    # ---- stage 1: V(s), cross-fitted over two halves of the training games
    half = (f >= 3)
    v = np.zeros(len(y), np.float32)
    vb = []
    for side in (False, True):
        fit_rows = tr & (half == side) & ~va
        b = fit_reg(X[fit_rows], y[fit_rows], X[va], y[va], feats, a.leaves, a.rounds, a.lr)
        vb.append(b)
        pred_rows = tr & (half != side)
        v[pred_rows] = predict(b, X[pred_rows], feats)
    v[te] = 0.5 * (predict(vb[0], X[te], feats) + predict(vb[1], X[te], feats))
    resid = y - v
    r2_v = 1 - float(((y[te] - v[te]) ** 2).mean() / y[te].var())
    print(f'V: held-out R2 {r2_v:.4f}, rounds {[int(b.num_boosted_rounds()) for b in vb]}, {time.time() - t0:.0f}s', flush=True)
    # ---- stage 2: residual regressors per first step, mirror-augmented
    Xm, km = C.mirror(X, k.copy(), feats)
    A = np.zeros((len(y), 3), np.float32)
    meta = dict(name=a.name, data=a.data, blocks=a.blocks, horizon=a.horizon, unit_value=a.unit_value,
                rows=int(len(y)), explored=int(explored.sum()), games=int(off), features=len(feats),
                r2_v=r2_v, heads={})
    for kk in range(3):
        sel = k == kk
        selm = km == kk
        Xk = np.concatenate([X[sel & tr & ~va], Xm[selm & tr & ~va]])
        yk = np.concatenate([resid[sel & tr & ~va], resid[selm & tr & ~va]])
        Xv = np.concatenate([X[sel & va], Xm[selm & va]])
        yv = np.concatenate([resid[sel & va], resid[selm & va]])
        b = fit_reg(Xk, yk, Xv, yv, feats, a.leaves, a.rounds, a.lr)
        b.save_model(str(out / f'q_{C.RELS[kk]}.ubj'))
        (out / f'q_{C.RELS[kk]}.ubj.features.json').write_text(json.dumps(feats))
        A[:, kk] = predict(b, X, feats)
        m = sel & te
        meta['heads'][C.RELS[kk]] = dict(
            rounds=int(b.num_boosted_rounds()), train_rows=int(len(yk)), test_rows=int(m.sum()),
            r2=1 - float(((resid[m] - A[m, kk]) ** 2).mean() / resid[m].var()),
            corr=float(np.corrcoef(resid[m], A[m, kk])[0, 1]))
        print(kk, meta['heads'][C.RELS[kk]], f'{time.time() - t0:.0f}s', flush=True)
    # ---- held-out diagnostics: does following argmax A pay in realised residual return?
    best = A.argmax(1)
    adv_taken = A[np.arange(len(y)), k] - A.max(1)
    rep = {}
    for label, rows in (('explored', te & explored), ('greedy', te & ~explored)):
        ag = rows & (best == k)
        dg = rows & (best != k)
        rep[label] = dict(n=int(rows.sum()), agree_share=float(ag.sum() / max(1, rows.sum())),
                          resid_when_agree=float(resid[ag].mean()) if ag.any() else None,
                          resid_when_disagree=float(resid[dg].mean()) if dg.any() else None,
                          died_when_agree=float(Y[ag, D.YCOLS.index(f'died_{a.horizon}')].mean()) if ag.any() else None,
                          died_when_disagree=float(Y[dg, D.YCOLS.index(f'died_{a.horizon}')].mean()) if dg.any() else None)
    # realised residual by decile of the predicted advantage of the taken step (explored rows, held out)
    rows = te & explored
    if rows.sum() > 100:
        q = np.quantile(adv_taken[rows], np.linspace(0, 1, 6))
        rep['explored_by_adv_quintile'] = [
            dict(adv=float(adv_taken[rows & (adv_taken >= lo) & (adv_taken <= hi)].mean()),
                 resid=float(resid[rows & (adv_taken >= lo) & (adv_taken <= hi)].mean()))
            for lo, hi in zip(q[:-1], q[1:])]
    meta['heldout'] = rep
    meta['sec'] = round(time.time() - t0)
    chk = np.zeros((min(3000, int(te.sum())), len(names)), np.float32)
    chk[:, cols] = X[te][: len(chk)]
    np.save(out / 'check.npy', chk)
    (out / 'meta.json').write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


# ------------------------------------------------------------------------------------ hindsight targets (B)
def load_hind(arms, panel, cols, horizon, limit=0, emb=''):
    """-> H, X, R (hindsight [n, 9]), game index; only rows with a hindsight label."""
    import dataset as D
    import relabel as RL
    import glob
    Hs, Xs, Rs, Gs, gi = [], [], [], [], 0
    for arm in arms.split(','):
        fs = sorted(f for f in glob.glob(str(C.B / 'data' / arm / panel / '*.npz'))
                    if not f.endswith(('.tmp.npz', '.view.npz')))
        for f in (fs[:limit] if limit else fs):
            hp = RL.hind_path(f, horizon)
            if not hp.exists():
                continue
            z = np.load(f)
            R = np.load(hp)
            ok = ~np.isnan(R[:, 0])
            X = z['X'][ok][:, cols]
            if emb:   # tier-1 state of the same rows (tools/verso/train_repr.py embed), appended as extra columns
                X = np.concatenate([X, np.load(f[:-4] + f'.emb-{emb}.npy')[ok]], 1)
            Hs.append(z['H'][ok]); Xs.append(X); Rs.append(R[ok])
            Gs.append(np.full(int(ok.sum()), gi, np.int32)); gi += 1
    return np.concatenate(Hs), np.concatenate(Xs), np.concatenate(Rs), np.concatenate(Gs), gi


def offline_policy(X, names, A=None, beta=0.0, lam=1.0):
    """The bot's one-step choice rebuilt from its own dumped numbers: argmax over F/R/L of the hand score of the
    one-step path + lam * h_dir + beta * (A_k - max A), over steps that are OK or a dive. -1 when none is live."""
    idx = {n: i for i, n in enumerate(names)}
    base = np.stack([X[:, idx[f'a{r}_score']] + lam * X[:, idx[f'h_dir_{r}']] for r in C.RELS], 1).astype(np.float64)
    live = np.stack([np.isin(X[:, idx[f'a{r}_status']], (0, 2)) for r in C.RELS], 1)
    if A is not None and beta:
        base = base + beta * (A - A.max(1, keepdims=True))
    base[~live] = -1e9
    ch = base.argmax(1)
    ch[~live.any(1)] = -1
    return ch


def cmd_hind(a):
    """Tier 3 (B): fit, per first step, the hindsight advantage (value of the step minus the best step's value in
    the recorded future, clipped) on every logged move; the `q` head is the three regressors."""
    _, names = C.schema(a.bot)
    cols, feats = select_features(names, set(a.blocks.split(',')))
    full_cols = list(range(len(names)))
    out = C.MODELS / a.name
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    H, Xall, R, G, ng = load_hind(a.data, a.panel, full_cols, a.tag or a.horizon, a.limit, a.emb)
    n_emb = Xall.shape[1] - len(names)
    cols = cols + list(range(len(names), len(names) + n_emb))
    feats = feats + [f'e_{i}' for i in range(n_emb)]
    X = Xall[:, cols]
    val, alive = R[:, 0::3], R[:, 1::3]
    adv = np.clip(val - val.max(1, keepdims=True), -a.clip, 0.0).astype(np.float32)
    rng = np.random.default_rng(C.SEED)
    fold = np.empty(ng, np.int8)
    fold[rng.permutation(ng)] = np.arange(ng) % 5
    f = fold[G]
    te, va = f == 0, f == 1
    tr = ~te & ~va
    print(f'rows {len(adv)}, games {ng}, features {len(feats)}, mean adv {adv.mean(0).round(3).tolist()}, '
          f'load {time.time() - t0:.0f}s', flush=True)
    mirror = not a.no_mirror and not n_emb   # the embedding has no mirror map
    if mirror:
        Xm, _ = C.mirror(X, np.zeros(len(X), np.int8), feats)
    advm = adv[:, [0, 2, 1]]
    A = np.zeros_like(adv)
    meta = dict(name=a.name, data=a.data, blocks=a.blocks, tag=a.tag, emb=a.emb, mirror=bool(mirror), horizon=a.horizon, clip=a.clip, rows=int(len(adv)),
                games=int(ng), features=len(feats), heads={})
    for kk in range(3):
        Xk = np.concatenate([X[tr], Xm[tr]]) if mirror else X[tr]
        yk = np.concatenate([adv[tr, kk], advm[tr, kk]]) if mirror else adv[tr, kk]
        b = fit_reg(Xk, yk, X[va], adv[va, kk], feats, a.leaves, a.rounds, a.lr)
        del Xk
        b.save_model(str(out / f'q_{C.RELS[kk]}.ubj'))
        (out / f'q_{C.RELS[kk]}.ubj.features.json').write_text(json.dumps(feats))
        A[:, kk] = predict(b, X, feats)
        meta['heads'][C.RELS[kk]] = dict(rounds=int(b.num_boosted_rounds()),
                                         r2=1 - float(((adv[te, kk] - A[te, kk]) ** 2).mean() / adv[te, kk].var()))
        print(kk, meta['heads'][C.RELS[kk]], f'{time.time() - t0:.0f}s', flush=True)
    # ---- held-out: regret and fatal-choice rate of the rebuilt policy at several beta
    Xt, At, advt, alt, Ht = Xall[te][:, :len(names)], A[te], adv[te], alive[te], H[te]
    i = np.arange(len(Xt))
    uniq = (advt == 0).sum(1) == 1
    can_live = alt.max(1) == 1

    def stats(ch):
        ok = ch >= 0
        return dict(n=int(ok.sum()), regret=float(-advt[i[ok], ch[ok]].mean()),
                    fatal=float(((alt[i[ok], ch[ok]] == 0) & can_live[ok]).mean()),
                    best=float((advt[i[ok], ch[ok]] == 0).mean()),
                    best_when_unique=float((advt[i[ok & uniq], ch[ok & uniq]] == 0).mean()))
    rep = {}
    rel = rel_of(Ht)
    plain = (rel >= 0) & ((Ht[:, 14] & 1) == 0)
    base = offline_policy(Xt, names)
    rep['offline_vs_recorded_agreement'] = float((base[plain] == rel[plain]).mean())
    rep['recorded_greedy'] = stats(np.where(plain, rel, -1))
    rep['head_alone'] = stats(np.where(Xt[:, names.index('aF_status')] >= 0, At.argmax(1), -1))
    for beta in (0.0, 0.5, 1.0, 2.0, 4.0, 8.0):
        rep[f'policy_beta_{beta}'] = stats(offline_policy(Xt, names, At, beta))
    for lam in (0.0,):
        for beta in (0.0, 1.0, 2.0, 4.0):
            rep[f'nodir_beta_{beta}'] = stats(offline_policy(Xt, names, At, beta, lam=0.0))
    meta['heldout'] = rep
    meta['sec'] = round(time.time() - t0)
    chk = Xall[te][:3000, :len(names)].astype(np.float32)
    np.save(out / 'check.npy', chk)
    (out / 'meta.json').write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('corpus')
    c.add_argument('--name', required=True); c.add_argument('--teams', required=True)
    c.add_argument('--cap', type=int, default=3000); c.add_argument('--leaves', type=int, default=255)
    c.add_argument('--rounds', type=int, default=3000); c.add_argument('--mirror', action='store_true')
    c.add_argument('--won-only', action='store_true'); c.add_argument('--jobs', type=int, default=8)
    c.add_argument('--max-round', type=int, default=0, help='opening specialist: only rows up to this round')
    c.add_argument('--team-root', action='append', help='TEAM=PATH: read that team\'s v5 rows from another build dir')
    c.add_argument('--extra-holdout', action='append', help='TEAM=PATH: also hold out that build dir\'s test games')
    c.add_argument('--since', default='', help='only games finished at or after this UTC date (one policy era)')
    c.add_argument('--bot', default='verso-00-base')
    o = sub.add_parser('own')
    o.add_argument('--name', required=True); o.add_argument('--data', required=True, help='arm[,arm] under build/verso/data')
    o.add_argument('--panel', default='train'); o.add_argument('--blocks', default='v5,ares,t4,h')
    o.add_argument('--horizon', type=int, default=20); o.add_argument('--unit-value', type=float, default=3.0)
    o.add_argument('--leaves', type=int, default=63); o.add_argument('--rounds', type=int, default=1500)
    o.add_argument('--lr', type=float, default=0.05); o.add_argument('--limit', type=int, default=0)
    o.add_argument('--bot', default='verso-p2-platform')
    h = sub.add_parser('hind')
    h.add_argument('--name', required=True); h.add_argument('--data', required=True)
    h.add_argument('--panel', default='train'); h.add_argument('--blocks', default='v5,ares,t4,h')
    h.add_argument('--horizon', type=int, default=20); h.add_argument('--clip', type=float, default=10.0)
    h.add_argument('--tag', default='', help='label set written by relabel.py --tag')
    h.add_argument('--emb', default='', help='append the tier-1 state <game>.emb-NAME.npy (offline comparison)')
    h.add_argument('--no-mirror', action='store_true')
    h.add_argument('--leaves', type=int, default=127); h.add_argument('--rounds', type=int, default=1500)
    h.add_argument('--lr', type=float, default=0.1); h.add_argument('--limit', type=int, default=0)
    h.add_argument('--bot', default='verso-p2-platform')
    a = ap.parse_args()
    if a.cmd == 'corpus':
        cmd_corpus(a)
    elif a.cmd == 'own':
        cmd_own(a)
    elif a.cmd == 'hind':
        cmd_hind(a)


if __name__ == '__main__':
    main()
