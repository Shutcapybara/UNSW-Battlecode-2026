"""TT: does the dragon's internal map (tools/tt/features_map.py) carry signal beyond the v5 row?

    .venv/bin/python tools/tt/q1_mapmem.py SRC_BUILD MAP_DIR TAG [--per-game 600] [--jobs N]

Games: those with map rows in MAP_DIR/v6. Rows: v5 rows joined to map rows on (dragon, round); direction rows (moves
F/R/L) and split-gate rows (eligible turns) sampled per game. Held-out = 20 % of these games (seed 62). GPU GBT on
v5 alone vs v5 + map features. Writes game_stats/runs/<TAG>-mapmem.json.
"""
import argparse, glob, json, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'hb1'))
import q1_decisions as Q1

PER = 600
SRC = None


def _one(mp):
    gid = int(Path(mp).stem)
    v = pd.read_parquet(Path(SRC) / 'v5' / 'corpus' / f'{gid}.parquet')
    m = pd.read_parquet(mp).drop(columns=['game'])
    d = v.merge(m, on=['dragon', 'round'], how='inner')
    rng = np.random.default_rng(gid)
    out = {}
    for k, sel in (('direction', (d.y_family == 'move') & d.y_first.isin(['F', 'R', 'L'])), ('gate', d.split_elig == 1)):
        s = d[sel]
        if len(s) > PER:
            s = s.iloc[np.sort(rng.choice(len(s), PER, replace=False))]
        for c in s.columns:
            if not pd.api.types.is_numeric_dtype(s[c]) and c not in Q1.LABELS and c not in Q1.MAP_ID:
                s = s.assign(**{c: s[c].astype(str)})
        out[k] = s
    return out


def main():
    global PER, SRC
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('mapdir'); ap.add_argument('tag')
    ap.add_argument('--per-game', type=int, default=PER)
    ap.add_argument('--jobs', type=int, default=12)
    a = ap.parse_args()
    PER, SRC = a.per_game, a.src
    files = sorted(glob.glob(str(Path(a.mapdir) / 'v6' / '*.parquet')))
    with Pool(a.jobs) as pool:
        parts = pool.map(_one, files, chunksize=4)
    games = sorted(int(Path(f).stem) for f in files)
    test = set(np.random.default_rng(Q1.SEED).choice(games, len(games) // 5, replace=False).tolist())
    res = dict(games=len(games), test_games=len(test))
    for k in ('direction', 'gate'):
        d = pd.concat([p[k] for p in parts], ignore_index=True)
        te = d.game.astype(int).isin(test).to_numpy()
        X, y = Q1.xy(k, d)
        mm = [c for c in X.columns if c.startswith('mm_') or '_mm_' in c]
        base = [c for c in X.columns if c not in mm and c != 'mem_initial']
        r = dict(n_train=int((~te).sum()), n_test=int(te.sum()), map_cols=mm)
        for name, cols in (('v5', base), ('v5+map', base + mm)):
            m, p = Q1.fit_gbt(X.loc[~te, cols], y[~te], X.loc[te, cols], y[te])
            r[name] = Q1.score(p, m.classes_, y[te])
            if name == 'v5+map':
                imp = m.m.get_booster().get_score(importance_type='total_gain')
                rank = sorted(imp.items(), key=lambda kv: -kv[1])
                r['map_feature_ranks'] = [(i + 1, f) for i, (f, _) in enumerate(rank) if f in mm][:8]
        r['gain_pp'] = 100 * (r['v5+map']['acc'] - r['v5']['acc'])
        res[k] = r
        print(f"{a.tag} {k}: v5 {r['v5']['acc']:.4f} -> v5+map {r['v5+map']['acc']:.4f} ({r['gain_pp']:+.2f} pp; "
              f"test rows {r['n_test']:,}); map features by gain rank {r['map_feature_ranks'][:5]}", flush=True)
    (ROOT / 'game_stats' / 'runs' / f'{a.tag}-mapmem.json').write_text(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
