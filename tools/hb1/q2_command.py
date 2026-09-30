"""HB-1 Q2: command-level accuracy of a policy with and without the wrapper (tools/hb1/wrapper.py).

    .venv/bin/python tools/hb1/q2_command.py [--jobs N] [--per-game 1500]

Same held-out corpus games as Q1 (seed 62), plus the era-labelled set (the 27 Sep packet's 66.45 % was measured
on that era). Writes game_stats/runs/hb1-q2-command.json.
"""
import argparse, glob, json, sys, time, os
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wrapper as W
import q1_decisions as Q1

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / os.environ.get('HB_BUILD', 'hb1')   # HB_BUILD/HB_TEAM/HB_TAG: other teams (lane tt)
TAG = os.environ.get('HB_TAG', 'hb1')
OUT = ROOT / 'game_stats' / 'runs' / f'{TAG}-q2-command.json'
PER = int(1500 * float(os.environ.get('HB_CAP_FACTOR', 1)))   # scaled like q1_decisions' caps (memory)


def _sample(path):
    d = pd.read_parquet(path)
    if len(d) > PER:
        rng = np.random.default_rng(int(Path(path).stem))
        d = d.iloc[np.sort(rng.choice(len(d), PER, replace=False))]
    for c in d.columns:
        if not pd.api.types.is_numeric_dtype(d[c]) and c not in Q1.LABELS and c not in Q1.MAP_ID:
            d[c] = d[c].astype(str)
    return d


def load(s, jobs):
    p = B / 'q1' / f'cmd_{s}.parquet'
    if not p.exists():
        with Pool(jobs) as pool:
            d = pd.concat(pool.imap_unordered(_sample, sorted(glob.glob(str(B / 'v5' / s / '*.parquet'))), chunksize=4),
                          ignore_index=True)
        d.to_parquet(p)
    return pd.read_parquet(p)


def feats(d, cols=None):
    X = d[[c for c in d.columns if c not in Q1.LABELS and c not in Q1.MAP_ID]].copy()
    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype('category').cat.codes
    X = X.astype(np.float32)
    return X if cols is None else X.reindex(columns=cols, fill_value=0)


def full(p, classes):
    P = np.zeros((len(p), len(W.CMDS)))
    P[:, np.asarray(classes)] = p
    return P


def evaluate(d, y, P):
    raw = P.argmax(1)
    wr = W.apply(d, P)
    ok, forced = W.masks(d)
    fam_obs = y >= 3
    r = dict(n=len(y), raw=float((raw == y).mean()), wrapped=float((wr == y).mean()),
             family_wrapped=float(((wr >= 3) == fam_obs).mean()),
             raw_invalid=float((~ok[np.arange(len(y)), raw]).mean()),
             forced_rows=float((forced >= 0).mean()), forced_acc=float((wr[forced >= 0] == y[forced >= 0]).mean()),
             obs_outside_wrapper=float((~ok[np.arange(len(y)), y] & (forced < 0)).mean()))
    for name, m in (('move', ~fam_obs), ('split', fam_obs)):
        r[f'{name}_rows_wrapped'] = float((wr[m] == y[m]).mean())
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=14)
    a = ap.parse_args()
    cor = load('corpus', a.jobs)
    has_era = any((B / 'v5' / 'era').glob('*.parquet'))
    era = load('era', a.jobs) if has_era else cor.iloc[:0]
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    rng = np.random.default_rng(Q1.SEED)
    test_games = set(rng.choice(games, len(games) // 5, replace=False).tolist())
    te = cor.game.astype(int).isin(test_games).to_numpy()
    X = feats(cor)
    y = W.label(cor)
    Xe, ye = (feats(era, list(X.columns)), W.label(era)) if has_era else (X.iloc[:0], y[:0])
    res = dict(train_rows=int((~te).sum()), test_rows=int(te.sum()), era_rows=len(era),
               label_dist={W.CMDS[i]: int((y == i).sum()) for i in range(len(W.CMDS))})
    prior = np.bincount(y[~te], minlength=len(W.CMDS)) / (~te).sum()
    res['prior'] = dict(test=evaluate(cor[te], y[te], np.tile(prior, (te.sum(), 1))),
                        era=evaluate(era, ye, np.tile(prior, (len(era), 1))) if has_era else None)
    print('prior', res['prior'], flush=True)
    for name, f in (('tree4', Q1.fit_tree), ('gbt', Q1.fit_gbt), ('mlp', Q1.fit_mlp)):
        t0 = time.time()
        m, p = f(X[~te], y[~te], X[te], y[te])
        classes = m[1] if name == 'mlp' else m.classes_
        if name == 'mlp' and has_era:
            import torch
            net = m[0]
            mu, sd = X[~te].astype(np.float64).mean(0), X[~te].astype(np.float64).std(0) + 1e-6
            with torch.no_grad():
                xe = torch.tensor(((Xe.astype(np.float64) - mu) / sd).to_numpy(), dtype=torch.float32,
                                  device=next(net.parameters()).device)
                pe = torch.cat([net(c).softmax(1) for c in xe.split(65536)]).cpu().numpy()
        else:
            pe = m.predict_proba(Xe) if has_era else None
        res[name] = dict(test=evaluate(cor[te], y[te], full(p, classes)),
                         era=evaluate(era, ye, full(pe, classes)) if has_era else None,
                         sec=round(time.time() - t0, 1))
        print(name, json.dumps(res[name]), flush=True)
        OUT.write_text(json.dumps(res, indent=1))
    print('\n| model | corpus held-out raw | wrapped | era raw | era wrapped | raw invalid (corpus) |')
    print('|---|---:|---:|---:|---:|---:|')
    for k in ('prior', 'tree4', 'gbt', 'mlp'):
        r = res[k]
        e = r['era'] or dict(raw=float('nan'), wrapped=float('nan'))
        print(f"| {k} | {r['test']['raw']:.4f} | {r['test']['wrapped']:.4f} | {e['raw']:.4f} | "
              f"{e['wrapped']:.4f} | {r['test']['raw_invalid']:.4f} |")


if __name__ == '__main__':
    main()
