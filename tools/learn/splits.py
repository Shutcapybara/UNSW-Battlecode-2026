"""Frozen Phase 3 splits (D-046 §3), applied to every game the programme knows. Data lane (kageyama).

    python3 tools/learn/splits.py games      # -> build/learn/splits/games_split_v1.parquet + docs/learning/splits/kageyama-games-v1.json
    python3 tools/learn/splits.py fixtures   # -> docs/learning/splits/kageyama-fixtures-v1.json

Rules (frozen by the Chair, never re-drawn):
  held-out maps   every game whose map NAME is Autarky, Maze or Trauma (D-049), in every map_era -> split 'heldout_map'
  series buckets  bucket = int(sha256('D-046/' + series_id), 16) mod 10; 0 test, 1 validation, 2-9 train. A game with
                  no series id is its own series ('game:' + game id) — reported separately.
  gate seeds      local games on seeds 1-5 are never training rows (seeds 1-3 gate, 4-5 reserve); training rollouts
                  use seeds >= 1000. Server games carry server seeds and are split by series only.
"""
import hashlib, json, os, sys
from pathlib import Path

ROOT = Path.cwd()
DOCS = Path(os.environ.get('LEARN_DOCS_ROOT', ROOT))   # docs/ outputs go to the lane's own tree, not the shared checkout
PY = ROOT / 'build' / 's1-pylib'
if sys.platform.startswith('linux') and PY.exists():
    sys.path.append(str(PY))

HELDOUT_MAPS = ('Autarky', 'Maze', 'Trauma')      # D-049 (10:59Z) corrected D-046's Trophy to Autarky; frozen
HELDOUT_FILES = ('autarky', 'maze', 'trauma')
GATE_SEEDS = (1, 2, 3, 4, 5)
TRAIN_SEED_MIN = 1000
SPLIT_VERSION = 2
CONSUMED = {   # series whose games entered a fit (D-051 §6): never usable as clean evaluation for that card
    'P-2': 'build/hinata/v0/fit-lq/train_rows.parquet',   # sha256 c958e8c7..., P-2 / P-hinata-02 at 10:52Z
}


def bucket(series_id):
    return int(hashlib.sha256(('D-046/' + str(series_id)).encode()).hexdigest(), 16) % 10


def split_of(map_name, series_id, game_id=None):
    if map_name in HELDOUT_MAPS:
        return 'heldout_map'
    sid = series_id if series_id else f'game:{game_id}'
    b = bucket(sid)
    return 'test' if b == 0 else 'val' if b == 1 else 'train'


def local_split(map_file, seed):
    """A locally generated game (panel / self-play): held-out maps by file stem, gate seeds excluded."""
    stem = Path(str(map_file)).stem
    if stem in HELDOUT_FILES:
        return 'heldout_map'
    if int(seed) in GATE_SEEDS or int(seed) < TRAIN_SEED_MIN:
        return 'gate_or_reserved_seed'
    return 'train'


def games_manifest():
    import pandas as pd
    S1 = ROOT / 'build' / 's1' / 'corpus'
    g = pd.read_parquet(S1 / 'games.parquet', columns=['game', 'game_id', 'team_a', 'team_b', 'map', 'ranked',
                                                       'started_at', 'series_id', 'seed', 'map_hash', 'map_era', 'in_scope',
                                                       'result_a'])
    g['series_key'] = [s if isinstance(s, str) and s else f'game:{gid}' for s, gid in zip(g.series_id, g.game)]
    g['bucket'] = [bucket(s) for s in g.series_key]
    g['split'] = ['heldout_map' if m in HELDOUT_MAPS else ('test' if b == 0 else 'val' if b == 1 else 'train')
                  for m, b in zip(g['map'], g.bucket)]
    # a series never straddles splits (series buckets are per series; held-out maps are per game but a series is one map)
    # consumed series: any series with a game in a frozen training file (consumed_by = card id)
    g['consumed_by'] = ''
    consumed = {}
    for card, path in CONSUMED.items():
        p = ROOT / path
        if not p.exists():
            consumed[card] = dict(file=path, missing=True)
            continue
        rows = pd.read_parquet(p, columns=['game'])
        games = set(rows.game.astype(str))
        ser = set(g[g.game.astype(str).isin(games)].series_key)
        hit = g.series_key.isin(ser)
        g.loc[hit, 'consumed_by'] = [(c + ',' if c else '') + card for c in g.loc[hit, 'consumed_by']]
        sp = g[g.game.astype(str).isin(games)]
        consumed[card] = dict(file=path, sha256=sha(p), games_in_file=len(games), games_matched=int(len(sp)),
                              series=len(ser), file_games_by_split=sp.split.value_counts().to_dict(),
                              series_by_split=g[hit].drop_duplicates('series_key').split.value_counts().to_dict())
    # held-out-map post-m2 games whose series has no game in the consumed rows (D-051 §6 count)
    hm = g[(g.split == 'heldout_map') & (g.map_era == 'post-m2')].copy()
    hm['clean'] = hm.consumed_by == ''
    hm['decisive'] = hm.result_a.isin([0.0, 1.0])
    clean_counts = []
    for (mp, rk), x in hm.groupby(['map', 'ranked']):
        clean_counts.append(dict(map=mp, ranked=bool(rk), games=int(len(x)), clean=int(x.clean.sum()),
                                 in_scope=int(x.in_scope.fillna(False).sum()),
                                 in_scope_decisive_clean=int((x.clean & x.in_scope.fillna(False) & x.decisive).sum()),
                                 series=int(x.series_key.nunique()), clean_series=int(x[x.clean].series_key.nunique())))
    # by construction a series' non-held-out games share one bucket; a series also holds held-out-map games (a series
    # spans maps), which is intended: held-out maps test map transfer, series buckets test opponents/time
    nh = g[g.split != 'heldout_map']
    straddle = nh.groupby('series_key').split.nunique()
    mixed = int((g.groupby('series_key').split.nunique() > 1).sum())
    out = ROOT / 'build' / 'learn' / 'splits'
    out.mkdir(parents=True, exist_ok=True)
    g[['game', 'game_id', 'series_key', 'bucket', 'split', 'consumed_by', 'map', 'map_hash', 'map_era', 'ranked', 'team_a', 'team_b',
       'started_at', 'in_scope']].to_parquet(out / f'games_split_v{SPLIT_VERSION}.parquet', index=False)
    lines = '\n'.join(f'{a},{b}' for a, b in sorted(zip(g.game.astype(str), g.split))).encode()
    counts = g.groupby(['map_era', 'split']).agg(games=('game', 'size'), series=('series_key', 'nunique'),
                                                ranked=('ranked', 'sum')).reset_index()
    hmap = (g[g['map'].isin(HELDOUT_MAPS)].groupby(['map', 'map_era']).agg(games=('game', 'size'),
            hashes=('map_hash', lambda s: sorted(set(map(str, s))))).reset_index())
    no_series = int((~g.series_id.astype(str).str.len().gt(0) | g.series_id.isna()).sum())
    man = dict(
        split_version=SPLIT_VERSION, decision='D-046 §3', rules=__doc__.split('Rules')[1].strip(),
        n_games=int(len(g)), n_series=int(g.series_key.nunique()), games_without_series=no_series,
        series_straddling_buckets=int((straddle > 1).sum()), series_with_heldout_map_games=mixed,
        sha256_game_split=hashlib.sha256(lines).hexdigest(),
        file=f'build/learn/splits/games_split_v{SPLIT_VERSION}.parquet',
        heldout_map_hashes=[dict(map=r.map, map_era=r.map_era, games=int(r.games), map_hash=r.hashes) for r in hmap.itertuples()],
        counts=[dict(map_era=r.map_era, split=r.split, games=int(r.games), series=int(r.series), ranked=int(r.ranked))
                for r in counts.itertuples()],
        bucket_share={str(b): round(float((g.bucket == b).mean()), 4) for b in range(10)},
        consumed=consumed, heldout_post_m2_clean=clean_counts,
        snapshot_note='The rule is frozen; this digest covers the store snapshot it was built from. New games get '
                      'their split from the same rule (splits.split_of); re-running only adds rows.')
    p = DOCS / 'docs' / 'learning' / 'splits' / f'kageyama-games-v{SPLIT_VERSION}.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(man, indent=1, default=str))
    print(json.dumps({k: man[k] for k in ('n_games', 'n_series', 'games_without_series', 'series_straddling_buckets', 'series_with_heldout_map_games', 'consumed',
                                           'sha256_game_split')}, indent=1))
    print(counts.to_string(index=False))
    print(pd.DataFrame(clean_counts).to_string(index=False))
    return man


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fixtures_manifest():
    sys.path.insert(0, str(ROOT))
    from tools.analysis.features import run_panel as RP
    pool = [dict(map=m, file=f'maps/{m}.map', sha256=sha(ROOT / f'maps/{m}.map'), heldout=Path(m).name in HELDOUT_FILES)
            for m in RP.LIVE_MAPS_M2]
    swapped = ('autarky', 'default', 'dilemma', 'schooltime', 'slithery_fight', 'trophy')
    gen = []
    for m in RP.GEN_MAPS:
        stale = m.startswith('var/') and any(m.startswith(f'var/{s}') for s in swapped)
        gen.append(dict(map=m, file=f'maps/{m}.map', sha256=sha(ROOT / f'maps/{m}.map'), stale_twin=stale,
                        heldout_twin=any(m.startswith(f'var/{h}') for h in HELDOUT_FILES)))
    zoo = [dict(bot=z, fingerprint=RP.runtime_fingerprint(ROOT / 'bots' / z)) for z in RP.ZOO]
    man = dict(split_version=SPLIT_VERSION, decision='D-046 §3', gate_seeds=[1, 2, 3], reserve_seeds=[4, 5],
               training_seed_min=TRAIN_SEED_MIN, both_seats=True, pool=pool, gen=gen, zoo=zoo,
               note='Pool = ZOO x LIVE_MAPS_M2 x both seats; gen = maps/new + var twins, stale twins of the six '
                    'swapped maps excluded until regenerated from maps/live/. Games on gate/reserve seeds are never '
                    'training rows; logs from gate runs are tagged gate and excluded by audit.py.')
    blob = json.dumps(man, sort_keys=True).encode()
    man['sha256_manifest'] = hashlib.sha256(blob).hexdigest()
    p = DOCS / 'docs' / 'learning' / 'splits' / f'kageyama-fixtures-v{SPLIT_VERSION}.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(man, indent=1))
    print('pool', len(pool), 'gen', len(gen), 'stale', sum(x['stale_twin'] for x in gen), 'zoo', len(zoo), man['sha256_manifest'][:16])
    return man


if __name__ == '__main__':
    {'games': games_manifest, 'fixtures': fixtures_manifest}[sys.argv[1]]()
