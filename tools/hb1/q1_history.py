"""HB-1 Q1 follow-up: does recent history carry direction signal beyond the v5 row?

    .venv/bin/python tools/hb1/q1_history.py [--jobs N]

History is derived per dragon from its own earlier v5 rows (what the dragon itself knows): its last K relative
actions, turns since it last turned, an EWMA of its turn rate and left/right balance, and pearls eaten over the
last 10 turns. The direction rows are re-drawn exactly as q1_decisions (same per-game seed and cap), fitted with the
same GPU GBT on the same held-out games: v5 alone vs v5 + history. Writes game_stats/runs/hb1-q1-history.json.
"""
import argparse, glob, json, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_decisions as Q1

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / 'hb1'
OUT = ROOT / 'game_stats' / 'runs' / 'hb1-q1-history.json'
K = 6
CODE = {'F': 0, 'R': 1, 'L': 2, 'split': 3}


def history(d):
    d = d.sort_values(['dragon', 'round'], kind='stable')
    a = d.y_first.map(CODE).fillna(4).astype(np.int8)
    g = a.groupby(d.dragon)
    h = pd.DataFrame(index=d.index)
    for k in range(1, K + 1):
        h[f'hist_a{k}'] = g.shift(k).fillna(-1)
    turn = a.isin([1, 2]).astype(float)
    lr = np.where(a == 1, 1.0, np.where(a == 2, -1.0, 0.0))
    prev = lambda s: s.groupby(d.dragon).shift(1)
    h['hist_turn_ewm'] = prev(turn.groupby(d.dragon).transform(lambda s: s.ewm(alpha=0.3).mean())).fillna(0)
    h['hist_lr_ewm'] = prev(pd.Series(lr, index=d.index).groupby(d.dragon)
                            .transform(lambda s: s.ewm(alpha=0.3).mean())).fillna(0)
    idx = pd.Series(np.arange(len(d)), index=d.index)
    last_turn = idx.where(turn > 0).groupby(d.dragon).transform(lambda s: s.ffill())
    h['hist_since_turn'] = (idx - prev(last_turn)).fillna(99).clip(upper=99)
    ate = (d.mem_len_delta > 0).astype(float)
    h['hist_eat10'] = ate.groupby(d.dragon).transform(lambda s: s.rolling(10, min_periods=1).sum()).fillna(0)
    return h.loc[d.sort_index().index]


def _one(path):
    d = pd.read_parquet(path)
    d = pd.concat([d, history(d)], axis=1)
    rng = np.random.default_rng(int(Path(path).stem))
    # same draw order as q1_decisions._sample: gate first, then alloc, direction
    for k in ('gate', 'alloc'):
        s = {'gate': d[d.split_elig == 1], 'alloc': d[d.y_family == 'split']}[k]
        if Q1.CAP[k] and len(s) > Q1.CAP[k]:
            rng.choice(len(s), Q1.CAP[k], replace=False)
    s = d[(d.y_family == 'move') & d.y_first.isin(['F', 'R', 'L'])]
    if len(s) > Q1.CAP['direction']:
        s = s.iloc[np.sort(rng.choice(len(s), Q1.CAP['direction'], replace=False))]
    for c in s.columns:
        if not pd.api.types.is_numeric_dtype(s[c]) and c not in Q1.LABELS and c not in Q1.MAP_ID:
            s[c] = s[c].astype(str)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=6)
    a = ap.parse_args()
    p = B / 'q1' / 'direction_hist.parquet'
    if not p.exists():
        with Pool(a.jobs) as pool:
            d = pd.concat(pool.imap_unordered(_one, sorted(glob.glob(str(B / 'v5' / 'corpus' / '*.parquet'))),
                                              chunksize=4), ignore_index=True)
        d.to_parquet(p)
    d = pd.read_parquet(p)
    ref = pd.read_parquet(B / 'q1' / 'direction.parquet', columns=['game', 'dragon', 'round'])
    same = len(ref) == len(d) and (ref.sort_values(['game', 'dragon', 'round']).to_numpy() ==
                                   d[['game', 'dragon', 'round']].sort_values(['game', 'dragon', 'round']).to_numpy()).all()
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    test_games = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    te = d.game.astype(int).isin(test_games).to_numpy()
    X, y = Q1.xy('direction', d)
    hcols = [c for c in X.columns if c.startswith('hist_')]
    base = [c for c in X.columns if not c.startswith('hist_')]
    res = dict(rows_match_q1_sample=bool(same), n_train=int((~te).sum()), n_test=int(te.sum()), hist_cols=hcols)
    for name, cols in (('v5', base), ('v5+hist', list(X.columns)), ('v5+hist_minus_lag1', [c for c in X.columns
                                                                                         if c != 'hist_a1'])):
        m, pr = Q1.fit_gbt(X.loc[~te, cols], y[~te], X.loc[te, cols], y[te])
        res[name] = Q1.score(pr, m.classes_, y[te])
        print(name, res[name], flush=True)
    m, pr = Q1.fit_mlp(X.loc[~te], y[~te], X.loc[te], y[te])
    res['mlp_v5+hist'] = Q1.score(pr, m[1], y[te])
    print('mlp_v5+hist', res['mlp_v5+hist'], flush=True)
    res['d_acc_gbt'] = res['v5+hist']['acc'] - res['v5']['acc']
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != 'hist_cols'}, indent=1))


if __name__ == '__main__':
    main()
