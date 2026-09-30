"""Diff C++ feature rows against the stored v5 rows for some games.

    .venv/bin/python tools/hb1/cpp/check_parity.py GAME [GAME ...]
"""
import subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'build' / 'hb1'
SKIP = {'mem_initial'}


def one(gid):
    g = pd.read_parquet(B / 'games.parquet').set_index('game').loc[gid]
    dump = subprocess.run([sys.executable, str(ROOT / 'tools/hb1/cpp/dump_blocks.py'), g.path, g.side],
                          capture_output=True, text=True, check=True).stdout
    csv = subprocess.run([str(B / 'feat_parity')], input=dump, capture_output=True, text=True, check=True).stdout
    c = pd.read_csv(pd.io.common.StringIO(csv))
    py = pd.read_parquet(B / 'v5' / g.set / f'{gid}.parquet')
    key = ['dragon', 'round']
    m = py.merge(c, on=key, suffixes=('_py', '_cpp'))
    cols = [k for k in c.columns if k not in key and k not in SKIP and k in py.columns]
    bad = {}
    for k in cols:
        a, b = m[k + '_py'].astype(float).to_numpy(), m[k + '_cpp'].astype(float).to_numpy()
        n = int((~np.isclose(a, b, atol=1e-6, equal_nan=True)).sum())
        if n:
            bad[k] = n
    missing = sorted(set(py.columns) - set(c.columns) - {'game', 'map', 'mem_initial'} - {x for x in py.columns if x.startswith(('y_', 'post_'))})
    print(f'game {gid}: py rows {len(py)} cpp rows {len(c)} matched {len(m)}; columns compared {len(cols)}; '
          f'mismatching columns {len(bad)}; missing in cpp {missing}')
    for k, n in sorted(bad.items(), key=lambda t: -t[1])[:15]:
        i = np.flatnonzero(~np.isclose(m[k + '_py'].astype(float), m[k + '_cpp'].astype(float), atol=1e-6))[0]
        print(f'   {k}: {n} rows differ, e.g. dragon {m.dragon.iat[i]} r{m["round"].iat[i]} py={m[k + "_py"].iat[i]} cpp={m[k + "_cpp"].iat[i]}')
    return len(bad) == 0 and len(m) == len(py) == len(c)


if __name__ == '__main__':
    ok = [one(int(g)) for g in sys.argv[1:]]
    print('ALL MATCH' if all(ok) else 'MISMATCH')
