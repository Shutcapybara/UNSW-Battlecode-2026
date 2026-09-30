"""HB-1 Q1 follow-up: is the direction residual noise (a stochastic or hidden-state policy) or a fixable gap?

    .venv/bin/python tools/hb1/q1_calibration.py

Refits the v5 direction GBT (same rows, same held-out games as q1_decisions) and reports on the held-out rows:
reliability by confidence bin (mean max-probability vs accuracy), expected calibration error, mean entropy, and
the share of rows where the policy looks near-deterministic (max p >= 0.95) vs near-tied (top-2 gap < 0.2).
If the model is calibrated, mean max-probability is the accuracy it expects; residual mass on near-tied rows is
what a sampled policy or unseen state would produce. Writes game_stats/runs/hb1-q1-calibration.json.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_decisions as Q1

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / 'hb1'
OUT = ROOT / 'game_stats' / 'runs' / 'hb1-q1-calibration.json'


def main():
    d = pd.read_parquet(B / 'q1' / 'direction.parquet')
    games = sorted(pd.read_parquet(B / 'games.parquet').query("set == 'corpus'").game.astype(int))
    test_games = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    te = d.game.astype(int).isin(test_games).to_numpy()
    X, y = Q1.xy('direction', d)
    m, p = Q1.fit_gbt(X[~te], y[~te], X[te], y[te])
    yt = y[te]
    pred = p.argmax(1)
    conf = p.max(1)
    srt = np.sort(p, 1)
    gap = srt[:, -1] - srt[:, -2]
    ent = -(p * np.log(np.clip(p, 1e-9, 1))).sum(1)
    bins = np.array([0, .4, .5, .6, .7, .8, .9, .95, 1.0001])
    rel = []
    ece = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        k = (conf >= lo) & (conf < hi)
        if k.sum():
            acc, mc = float((pred[k] == yt[k]).mean()), float(conf[k].mean())
            rel.append(dict(bin=f'{lo:.2f}-{min(hi, 1):.2f}', share=float(k.mean()), mean_conf=mc, acc=acc))
            ece += k.mean() * abs(acc - mc)
    near_det, tied = conf >= 0.95, gap < 0.2
    res = dict(n_test=int(te.sum()), acc=float((pred == yt).mean()), mean_max_prob=float(conf.mean()),
               expected_acc_if_sampled=float((p ** 2).sum(1).mean()), ece=float(ece), mean_entropy_nats=float(ent.mean()),
               share_near_deterministic=float(near_det.mean()), acc_near_deterministic=float((pred[near_det] == yt[near_det]).mean()),
               share_near_tied=float(tied.mean()), acc_near_tied=float((pred[tied] == yt[tied]).mean()),
               errors_on_near_tied=float((tied & (pred != yt)).sum() / max(1, (pred != yt).sum())),
               reliability=rel)
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != 'reliability'}, indent=1))
    print(pd.DataFrame(rel).round(3).to_string(index=False))


if __name__ == '__main__':
    main()
