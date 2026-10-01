#!/usr/bin/env python3
"""Obscur (H-1): per-map and per-structure-cluster deltas of arms vs a parent, both panels.

Clusters use only structure a bot can observe (tile count, portal edges per 100 tiles, beds per 100 tiles) plus the
parent's own regime on the map (share of its games decided by elimination) as an analysis label — never a map name.
For each arm: per-map paired mean economy delta, win delta, and per cluster the mean over fixtures with a fixture-cluster
bootstrap 90 % interval. A cluster gain with no loss elsewhere is a D-036 structure-gated candidate.

    .venv/bin/python tools/obscur/permap.py ARM[:BOT] ... [--parent verso-05-hb800-prior] [--seeds 1] [--csv OUT]
"""
import argparse, sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rescore as R  # noqa: E402

RUNS = str(ROOT / 'build/obscur/runs')


def structure(mapkey):
    p = ROOT / 'maps' / (mapkey.replace('+', '/') + '.map')
    tiles = beds = portal = kelp = 0
    for line in open(p):
        t = line.split()
        if not t:
            continue
        if t[0] == 'TILE' and len(t) >= 4:
            tiles += 1; beds += t[3] == '1'
        elif t[0] == 'EDGE' and len(t) >= 3:
            portal += t[2] == '2'; kelp += t[2] == '1'
    return dict(tiles=tiles, portal100=100 * portal / max(1, tiles), beds100=100 * beds / max(1, tiles),
                kelp100=100 * kelp / max(1, tiles))


def clusters(row):
    out = ['large' if row.tiles >= 1100 else 'small',
           'portal-dense' if row.portal100 >= 3 else 'portal-sparse',
           'bed-rich' if row.beds100 >= 10 else 'bed-poor',
           'elim-regime' if row.elim >= 0.5 else 'limit-regime']
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('arms', nargs='+')
    ap.add_argument('--parent', default='verso-05-hb800-prior')
    ap.add_argument('--seeds', default='1')
    ap.add_argument('--csv')
    ap.add_argument('--boot', type=int, default=500)
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(',')]
    rng = np.random.default_rng(3)
    rows, crow = [], []
    for panel in ('pool', 'gen'):
        P = R.load(RUNS, a.parent, a.parent, panel)
        P = P[P.seed.isin(seeds)]
        reg = P.groupby('mapkey').apply(lambda d: (d['reason'] == 'elimination').mean(), include_groups=False)
        st = pd.DataFrame({k: structure(k) for k in P.mapkey.unique()}).T
        st['elim'] = reg
        for spec in a.arms:
            arm, bot = (spec.split(':') + [None])[:2]
            bot = bot or (arm if (ROOT / 'bots' / arm).is_dir() else a.parent)
            C = R.load(RUNS, arm, bot, panel)
            if C is None:
                continue
            C = C[C.seed.isin(seeds)]
            m = C[R.KEY + ['econ', 'win']].merge(P[R.KEY + ['econ', 'win']], on=R.KEY, suffixes=('_c', '_p'))
            m['de'] = m.econ_c - m.econ_p; m['dw'] = m.win_c - m.win_p
            for mk, d in m.groupby('mapkey'):
                rows.append(dict(arm=arm, panel=panel, map=mk, n=len(d), d_econ=d.de.mean(), d_win=d.dw.mean(),
                                 **st.loc[mk].to_dict()))
            m = m.join(st, on='mapkey')
            for _, r in st.iterrows():
                pass
            labs = m.apply(lambda r: clusters(r), axis=1)
            for i, dim in enumerate(('size', 'portals', 'beds', 'regime')):
                m[dim] = labs.str[i]
                for lab, d in m.groupby(dim):
                    groups = list(d.groupby(R.CL).indices.values())
                    bs = []
                    for _ in range(a.boot):
                        idx = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
                        bs.append(d.iloc[idx][['de', 'dw']].mean().values)
                    bs = np.array(bs)
                    crow.append(dict(arm=arm, panel=panel, dim=dim, cluster=lab, maps=d.mapkey.nunique(), n=len(d),
                                     d_econ=round(d.de.mean(), 3), econ_lo=round(np.quantile(bs[:, 0], .05), 3),
                                     econ_hi=round(np.quantile(bs[:, 0], .95), 3), d_win=round(d.dw.mean(), 3),
                                     win_lo=round(np.quantile(bs[:, 1], .05), 3), win_hi=round(np.quantile(bs[:, 1], .95), 3)))
    M, Cl = pd.DataFrame(rows), pd.DataFrame(crow)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 2000)
    print(Cl.to_string(index=False))
    piv = M.pivot_table(index=['panel', 'map'], columns='arm', values='d_econ').round(3)
    print(piv.to_string())
    if a.csv:
        M.to_csv(a.csv, index=False); Cl.to_csv(Path(a.csv).with_suffix('.clusters.csv'), index=False)


if __name__ == '__main__':
    main()
