"""K-1 Part 2 data: per-cell rows (structure + exposure + deaths per class) for every map with data.

    python tools/sophie/k1_cells.py      -> build/sophie/agg2/cellrows.parquet, build/sophie/agg2/mapfeat.parquet
"""
import json, os, sys
from pathlib import Path
import pandas as pd

REPO = Path(os.environ.get('K1_REPO', Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hazard  # noqa: E402

AGG = REPO / os.environ.get('K1_AGG', 'build/sophie/agg2')
CLS = ['wall', 'self', 'ally_body', 'h2h_ally', 'h2h_enemy', 'enemy_body', 'invalid', 'suicide']
CTX = {'nb': 'newborn', 'tr': 'trapped', 'tx': 'transit', 'cr': 'crowd23', 'fi': 'fight'}


def main():
    idx = json.load(open(REPO / 'build/sophie/maps/index.json'))
    C = pd.read_parquet(AGG / 'cells.parquet')
    D = pd.read_parquet(AGG / 'deaths.parquet', columns=['set', 'map', 'map_hash', 'cohort', 'x', 'y', 'cls', 'L', 'nb', 'tr', 'tx', 'cr', 'fi', 'r'])
    D['set'] = D['set'].where(~D['set'].str.startswith('local'), 'local')
    # terrain is identical across the two seat-hashes of a map: key cells by map name + seat hash kept for rows
    rows, mf = [], []
    for h, name in idx.items():
        f = hazard.cell_features(str(REPO / 'build/sophie/maps' / f'{h}.map'))
        mf.append(dict(map_hash=h, map=name, **f['scalars']))
        cf = pd.DataFrame([dict(x=c[0], y=c[1], **v) for c, v in f['cells'].items()])
        for coh in ('us', 'top10', 'field', 'local'):
            e = C[(C['map_hash'] == h) & (C['cohort'] == coh)][['x', 'y', 'expo']]
            if not len(e):
                continue
            d = D[(D['map_hash'] == h) & (D['cohort'] == coh)]
            t = cf.merge(e, on=['x', 'y'], how='left').fillna({'expo': 0})
            for c in CLS:
                g = d[d['cls'] == c].groupby(['x', 'y']).agg(n=('L', 'size'), ln=('L', 'sum')).reset_index()
                t = t.merge(g.rename(columns={'n': f'n_{c}', 'ln': f'len_{c}'}), on=['x', 'y'], how='left')
            for k, nm in CTX.items():
                g = d[d[k].astype(bool)].groupby(['x', 'y']).agg(n=('L', 'size'), ln=('L', 'sum')).reset_index()
                t = t.merge(g.rename(columns={'n': f'n_{nm}', 'ln': f'len_{nm}'}), on=['x', 'y'], how='left')
            t = t.fillna(0)
            t['map_hash'], t['map'], t['cohort'] = h, name, coh
            rows.append(t)
    R = pd.concat(rows, ignore_index=True)
    M = pd.DataFrame(mf)
    R.to_parquet(AGG / 'cellrows.parquet')
    M.to_parquet(AGG / 'mapfeat.parquet')
    print(R.groupby('cohort').agg(cells=('x', 'size'), expo=('expo', 'sum'), wall=('n_wall', 'sum')))
    print(M.to_string())


if __name__ == '__main__':
    main()
