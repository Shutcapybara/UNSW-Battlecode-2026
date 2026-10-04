"""Teacher side list for BC (macro §5): post-m2 RANKED games of the current top ten, train split only (D-046/D-049
via splits v2), one row per teacher side, with Elo x recency weights. Unranked games are excluded outright (decoys
live there, and ranked/unranked are separate populations).

    python3 tools/learn/teachers.py [--top 10] [--half-life-days 2]
 -> build/learn/kageyama/teachers_v1.parquet + docs/learning/datasets/kageyama-teachers-v1.json (LEARN_DOCS_ROOT)

Weight = w_elo * w_time:  w_elo = clip((elo_at_game - 1500) / 500, 0.2, 1.0)  (the side's ladder Elo before the game),
                          w_time = 0.5 ** (age_days / half_life)  (age from the newest game in the list).
Per-team subsets (mimic datasets) are the same file filtered by `team`.
"""
import argparse, hashlib, json, os, sys
from pathlib import Path
ROOT = Path.cwd()
PY = ROOT / 'build' / 's1-pylib'
if sys.platform.startswith('linux') and PY.exists():
    sys.path.append(str(PY))
VERSION = 1


def main():
    import pandas as pd, numpy as np
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=10)
    ap.add_argument('--half-life-days', type=float, default=2.0)
    ap.add_argument('--split-file', default='build/learn/splits/games_split_v2.parquet')
    a = ap.parse_args()
    S = pd.read_parquet(a.split_file)
    G = pd.read_parquet(ROOT / 'build/s1/corpus/games.parquet', columns=['game', 'elo_a', 'elo_b', 'result_a', 'seed'])
    T = pd.read_parquet(ROOT / 'build/s1/corpus/teams.parquet')
    top = T[T.crank <= a.top][['team', 'name', 'crank']].copy()
    top['team'] = top.team.astype(str)
    g = S[(S.map_era == 'post-m2') & (S.ranked == True) & (S.split == 'train')].merge(G, on='game', how='left')
    rows = []
    for side, tc, ec in (('A', 'team_a', 'elo_a'), ('B', 'team_b', 'elo_b')):
        x = g[g[tc].astype(str).isin(set(top.team))].copy()
        x['side'] = side
        x['team'] = x[tc].astype(str)
        x['elo'] = x[ec]
        x['outcome'] = np.where(x.result_a.isna(), np.nan, x.result_a if side == 'A' else 1 - x.result_a)
        rows.append(x)
    x = pd.concat(rows, ignore_index=True).merge(top, on='team', how='left')
    x['on_disk'] = [(ROOT / f'public_replays/corpus/replays/{gid}.replay').exists() for gid in x.game]
    t = pd.to_datetime(x.started_at, utc=True)
    age = (t.max() - t).dt.total_seconds() / 86400
    x['w_elo'] = ((x.elo.fillna(1500) - 1500) / 500).clip(0.2, 1.0)
    x['w_time'] = 0.5 ** (age / a.half_life_days)
    x['weight'] = x.w_elo * x.w_time
    keep = ['game', 'side', 'team', 'name', 'crank', 'elo', 'outcome', 'map', 'map_hash', 'series_key', 'split', 'consumed_by',
            'started_at', 'seed', 'on_disk', 'w_elo', 'w_time', 'weight']
    x = x[keep].sort_values(['started_at', 'game', 'side']).reset_index(drop=True)
    out = ROOT / 'build/learn/kageyama'
    out.mkdir(parents=True, exist_ok=True)
    x.to_parquet(out / f'teachers_v{VERSION}.parquet', index=False)
    digest = hashlib.sha256('\n'.join(f'{a_},{b_}' for a_, b_ in zip(x.game, x.side)).encode()).hexdigest()
    by_team = x.groupby(['crank', 'team']).agg(sides=('game', 'size'), on_disk=('on_disk', 'sum'),
                                               win=('outcome', 'mean'), weight=('weight', 'sum')).reset_index()
    by_map = x.groupby('map').agg(sides=('game', 'size'), weight=('weight', 'sum')).reset_index()
    man = dict(version=VERSION, rule=__doc__.strip().split('\n\n')[0], args=vars(a), sides=int(len(x)),
               games=int(x.game.nunique()), on_disk=int(x.on_disk.sum()), sha256_game_side=digest,
               file=f'build/learn/kageyama/teachers_v{VERSION}.parquet',
               teams=[dict(crank=int(r.crank), team=r.team, sides=int(r.sides), on_disk=int(r.on_disk),
                           win=round(float(r.win), 3), weight=round(float(r.weight), 1)) for r in by_team.itertuples()],
               maps=[dict(map=r.map, sides=int(r.sides), weight=round(float(r.weight), 1)) for r in by_map.itertuples()],
               note='Team names are data. Ladder snapshot = teams.parquet at build time (cranks move; rebuild weekly).')
    p = Path(os.environ.get('LEARN_DOCS_ROOT', ROOT)) / f'docs/learning/datasets/kageyama-teachers-v{VERSION}.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(man, indent=1, default=str))
    print(by_team.to_string(index=False)); print(by_map.to_string(index=False))
    print('sides', len(x), 'games', x.game.nunique(), 'on disk', int(x.on_disk.sum()), digest[:16])


if __name__ == '__main__':
    main()
