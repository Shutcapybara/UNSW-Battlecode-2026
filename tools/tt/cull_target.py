"""TT: which ally does a small dragon die next to? Cull rate by the visible length of the nearest ally.

    HB_BUILD=tt/team206 HB_TAG=tt206 .venv/bin/python tools/tt/cull_target.py FROM_ROUND [--games N]

Rows: length <= 3, round >= FROM_ROUND. The nearest ally head (egocentric 7x7 grid, occ code 5) and the visible
length of its dragon (flood over connected ally cells, codes 4/5, from that head - an approximation when two allies
touch). Reports the cull rate by distance and by that length. Writes game_stats/runs/<TAG>-cull-target.json.
"""
import argparse, glob, json, os, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / os.environ.get('HB_BUILD', 'hb1')
TAG = os.environ.get('HB_TAG', 'hb1')
OFF = [(f, r) for f in range(-3, 4) for r in range(-3, 4)]
COLS = ['round', 'length', 'y_first', 'units', 'unit_limit'] + [f'g_{f}_{r}_occ' for f, r in OFF]
FROM = 250


def one(path):
    d = pd.read_parquet(path, columns=COLS)
    d = d[(d.length <= 3) & (d['round'] >= FROM)]
    if d.empty:
        return []
    occ = d[[f'g_{f}_{r}_occ' for f, r in OFF]].to_numpy().reshape(-1, 7, 7)
    cull = (~d.y_first.isin(['F', 'R', 'L', 'split'])).to_numpy()
    out = []
    for i in range(len(d)):
        g = occ[i]
        heads = np.argwhere(g == 5)
        if len(heads) == 0:
            out.append((99, 0, 0, cull[i]))
            continue
        dist = np.abs(heads - 3).sum(1)
        j = int(dist.argmin())
        h = tuple(heads[j])
        seen, st = {h}, [h]
        while st:                                     # connected ally cells from that head
            a = st.pop()
            for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                b = (a[0] + da, a[1] + db)
                if 0 <= b[0] < 7 and 0 <= b[1] < 7 and b not in seen and g[b] == 4:
                    seen.add(b); st.append(b)
        big = 0
        for hh in heads:                              # longest visible ally anywhere in view (same flood)
            hh = tuple(hh); s2, st = {hh}, [hh]
            while st:
                a = st.pop()
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    b = (a[0] + da, a[1] + db)
                    if 0 <= b[0] < 7 and 0 <= b[1] < 7 and b not in s2 and g[b] == 4:
                        s2.add(b); st.append(b)
            big = max(big, len(s2))
        out.append((int(dist[j]), len(seen), big, cull[i]))
    return out


def main():
    global FROM
    ap = argparse.ArgumentParser()
    ap.add_argument('from_round', type=int)
    ap.add_argument('--games', type=int, default=300)
    a = ap.parse_args()
    FROM = a.from_round
    fs = sorted(glob.glob(str(B / 'v5' / 'corpus' / '*.parquet')))
    fs = fs[::max(1, len(fs) // a.games)][:a.games]
    rows = []
    with Pool(12) as pool:
        for r in pool.imap_unordered(one, fs, chunksize=4):
            rows += r
    d = pd.DataFrame(rows, columns=['dist', 'near_len', 'max_len', 'cull'])
    lb = lambda s: pd.cut(s, [-1, 0, 2, 4, 6, 9, 14, 99], labels=['none', '1-2', '3-4', '5-6', '7-9', '10-14', '15+'])
    res = dict(rows=len(d), culls=int(d.cull.sum()), base=float(d.cull.mean()), from_round=FROM)
    adj = d[d.dist <= 1]
    res['adjacent_by_near_len'] = adj.groupby(lb(adj.near_len), observed=True).cull.agg(['mean', 'size']).round(4).to_dict('index')
    d2 = d[(d.dist >= 2) & (d.dist <= 3)]
    res['dist2_3_by_near_len'] = d2.groupby(lb(d2.near_len), observed=True).cull.agg(['mean', 'size']).round(4).to_dict('index')
    res['by_max_len_in_view'] = d.groupby(lb(d.max_len), observed=True).cull.agg(['mean', 'size']).round(4).to_dict('index')
    res['by_dist'] = d.groupby(d.dist.clip(upper=7)).cull.agg(['mean', 'size']).round(4).to_dict('index')
    (ROOT / 'game_stats' / 'runs' / f'{TAG}-cull-target.json').write_text(json.dumps(res, indent=1, default=str))
    for k, v in res.items():
        print(k, v if not isinstance(v, dict) else {str(a): (round(b['mean'], 4), int(b['size'])) for a, b in v.items()})


if __name__ == '__main__':
    main()
