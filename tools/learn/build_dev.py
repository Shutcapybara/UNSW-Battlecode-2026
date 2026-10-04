"""Build a teacher dataset from a side list (cloud/any host with unswbc). python build_dev.py SIDES.parquet REPLAY_DIR GAMES.parquet SPLIT.parquet OUT_PREFIX PCT WORKER NWORKERS"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import dataset as DS, audit

sides_f, rdir, games_f, split_f, out, pct, w, nw = sys.argv[1:9]
pct, w, nw = int(pct), int(w), int(nw)
T = pd.read_parquet(sides_f)
seeds = dict(zip(*pd.read_parquet(games_f, columns=['game', 'seed']).astype(str).values.T))
S = pd.read_parquet(split_f).set_index('game')
games = sorted(T.game.unique())[w::nw]
frames, log = [], []
t0 = time.time()
Path(out + '.parts').mkdir(parents=True, exist_ok=True)
for g in games:
    part = Path(out + '.parts') / f'{g}.parquet'
    if part.exists():
        continue
    r = S.loc[g]
    assert r.split == 'train', (g, r.split)
    sides = set(T[T.game == g].side)
    meta = dict(series_key=r.series_key, split=r.split, map_hash=r.map_hash, map_era=r.map_era, ranked=bool(r.ranked),
                team_a=str(r.team_a), team_b=str(r.team_b), teacher_team=','.join(sorted(T[T.game == g].team)),
                dataset_version=DS.DATASET_VERSION, enc_version=DS.E.ENC_VERSION, label_version=DS.LB.LABEL_VERSION,
                source='server')
    rows, st = DS.game_rows(g, (Path(rdir) / f'{g}.replay').read_bytes(), seeds.get(g), sides, pct, True, meta)
    log.append(dict(game=g, **st))
    if rows:
        DS.to_frame(rows).to_parquet(part, index=False, compression='zstd')
    else:
        pd.DataFrame({'game': []}).to_parquet(part)
    del rows
    print(g, st, f'{time.time() - t0:.0f}s', flush=True)
Path(f'{out}.w{w}.log.json').write_text(json.dumps(log, indent=1, default=str))
print('done worker', w)
