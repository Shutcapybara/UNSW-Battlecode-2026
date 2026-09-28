import json
from pathlib import Path
import numpy as np
import pandas as pd

CAT = ['facing_abs', 'mem_last_family', 'mem_last_rel']
CAT_LEVELS = {'facing_abs': ['east', 'north', 'south', 'west'],
              'mem_last_family': ['move', 'none', 'split', 'sprint', 'tle'],
              'mem_last_rel': ['B', 'F', 'L', 'R', 'none']}


def load(feat, manifest, sub=None, rows_per_game=4000, seed=0, games=None):
    m = pd.read_csv(manifest, dtype={'game_id': str})
    m = m[m.status == 'ok']
    if sub:
        m = m[m.target_submission.isin(sub if isinstance(sub, (list, tuple, set)) else [sub])]
    if games is not None:
        m = m[m.game_id.isin(games)]
    m = m.sort_values('completed_at')
    frames = []
    for gid in m.game_id:
        f = Path(feat) / f'{gid}.parquet'
        if not f.exists():
            continue
        x = pd.read_parquet(f)
        x = x[x.y_family.isin(['move', 'split'])]
        if rows_per_game and len(x) > rows_per_game:
            x = x.sample(rows_per_game, random_state=seed)
        for c in x.columns:
            if x[c].dtype == 'float64':
                x[c] = x[c].astype('float32')
            elif x[c].dtype == 'int64':
                x[c] = x[c].astype('int32')
        frames.append(x)
    D = pd.concat(frames, ignore_index=True)
    D['game'] = D['game'].astype(str)
    D['y_first'] = np.where(D.y_family == 'split', np.where(D.y_split == 1, 'suicide', 'split'), D.y_first)
    for c in CAT:
        if c in D and D[c].dtype == object:
            D[c] = pd.Categorical(D[c], categories=CAT_LEVELS[c]).codes
    games = [g for g in m.game_id if g in set(D.game)]
    return D, m, games


def feature_sets(D):
    ids = ['game', 'round', 'dragon', 'map', 'split']
    ys = [c for c in D.columns if c.startswith('y_') or c == 'post_died']
    priv = [c for c in D.columns if c.startswith('priv_')]
    mem = [c for c in D.columns if c.startswith('mem_')]
    absxy = ['x', 'y', 'xn', 'yn', 'facing_abs', 'W', 'H', 'mem_initial']
    msg = ['n_msgs', 'n_msgs_all', 'n_msgs_u32', 'mem_msgs_total'] + [c for c in D.columns if c.startswith('echo_')]
    allf = [c for c in D.columns if c not in ids + ys]
    legal = [c for c in allf if c not in priv]
    return {
        'view': [c for c in legal if c not in mem + absxy + msg],
        'view+abs': [c for c in legal if c not in mem + msg],
        'view+mem': [c for c in legal if c not in absxy + msg],
        'legal_all': legal,
        'DIAG_priv': allf,
    }
