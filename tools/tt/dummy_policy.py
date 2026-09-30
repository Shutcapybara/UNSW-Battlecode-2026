"""TT: decisive dummy-bot test - does a policy model trained on the team's ranked games predict its unranked games
as well as held-out ranked games? (Same idea as HB-1 Q3 transfer.)

    HB_TEAM=264 HB_BUILD=tt/team264 HB_TAG=tt264 .venv/bin/python tools/tt/dummy_policy.py [--per-game 300]

Split-gate and direction rows sampled per game (Q1's sampler and features). GPU GBT fitted on 70 % of the ranked
games; scored on the other 30 % of ranked games and on all unranked games, overall and per 6-hour window (windows
with enough of both). A same-bot team shows equal accuracy; a dummy or a different version shows a clear drop on
unranked. Writes game_stats/runs/<HB_TAG>-dummy-policy.json.
"""
import argparse, glob, json, os, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'hb1'))
import q1_decisions as Q1

B, TAG = Q1.B, Q1.TAG


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--per-game', type=int, default=300)
    ap.add_argument('--jobs', type=int, default=12)
    a = ap.parse_args()
    Q1.CAP = dict(gate=a.per_game, direction=a.per_game, sonar=1, alloc=None, late=None)
    g = pd.read_parquet(B / 'games.parquet').query("set == 'corpus'")
    g['game'] = g.game.astype(int)
    with Pool(a.jobs) as pool:
        parts = pool.map(Q1._sample, sorted(glob.glob(str(B / 'v5' / 'corpus' / '*.parquet'))), chunksize=8)
    t0 = g.t.min().floor('h')
    g['w'] = ((g.t - t0) / pd.Timedelta(hours=6)).astype(int)
    res = {}
    for k in ('gate', 'direction'):
        d = pd.concat([p[k] for p in parts], ignore_index=True)
        d['game'] = d.game.astype(int)
        d = d.merge(g[['game', 'ranked', 'w']], on='game')
        rk = sorted(d[d.ranked].game.unique())
        test_rk = set(np.random.default_rng(Q1.SEED).choice(rk, int(len(rk) * 0.3), replace=False).tolist())
        tr = (d.ranked & ~d.game.isin(test_rk)).to_numpy()
        te_r = d.game.isin(test_rk).to_numpy()
        te_u = (~d.ranked).to_numpy()
        X, y = Q1.xy(k, d)
        X = X[[c for c in X.columns if c != 'mem_initial']]
        m, _ = Q1.fit_gbt(X[tr], y[tr], X[te_r][:10], y[te_r][:10])
        pred = m.predict(X)
        ok = pred == y
        r = dict(train_rows=int(tr.sum()), ranked_heldout=float(ok[te_r].mean()), unranked=float(ok[te_u].mean()),
                 n_ranked_heldout=int(te_r.sum()), n_unranked=int(te_u.sum()))
        per = []
        for w in sorted(d.w.unique()):
            mr, mu = te_r & (d.w == w).to_numpy(), te_u & (d.w == w).to_numpy()
            if mr.sum() >= 500 and mu.sum() >= 500:
                per.append(dict(win=int(w), ranked=float(ok[mr].mean()), unranked=float(ok[mu].mean()),
                                n_r=int(mr.sum()), n_u=int(mu.sum())))
        r['by_window'] = per
        res[k] = r
        print(f"{TAG} {k}: fitted on {r['train_rows']:,} ranked rows -> ranked held-out {r['ranked_heldout']:.4f} "
              f"({r['n_ranked_heldout']:,}), unranked {r['unranked']:.4f} ({r['n_unranked']:,}), "
              f"gap {r['ranked_heldout'] - r['unranked']:+.4f}")
        for p in per:
            print(f"    window {p['win']:3d}: ranked {p['ranked']:.4f} ({p['n_r']:,})  unranked {p['unranked']:.4f} ({p['n_u']:,})")
    (ROOT / 'game_stats' / 'runs' / f'{TAG}-dummy-policy.json').write_text(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
