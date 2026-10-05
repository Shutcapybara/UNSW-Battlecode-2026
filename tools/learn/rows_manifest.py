"""Manifest of a sharded teacher-row build (Data lane, kageyama): per-shard rows and sha256, totals by blocks_src,
teacher team and map, oracle F/R/L move counts, NaN check of hb_f_* on oracle moves, shard sizes, and overlap with the
frozen R2 confirmation cohort (games and series; must be 0). Reads only meta/label columns, never x_* values.
    python rows_manifest.py SHARD_DIR OUT.json [--cohort build/learn/kageyama/r2_confirm_cohort_v1.parquet] [--part K --nparts N]
With --part, only shards K::N are read and OUT.json.partK is written (pickle of the raw tallies); --combine N merges."""
import pickle
import argparse, collections, hashlib, json
from pathlib import Path
import pyarrow.parquet as pq

ap = argparse.ArgumentParser()
ap.add_argument('dir'); ap.add_argument('out')
ap.add_argument('--cohort', default='build/learn/kageyama/r2_confirm_cohort_v1.parquet')
ap.add_argument('--part', type=int, default=-1); ap.add_argument('--nparts', type=int, default=1)
ap.add_argument('--combine', type=int, default=0)
a = ap.parse_args()
D = Path(a.dir)
fs = sorted(p for p in D.glob('*.parquet'))
if a.part >= 0:
    fs = fs[a.part::a.nparts]
C = pq.read_table(a.cohort, columns=['game', 'series_key']).to_pydict()
cg, cs = set(map(str, C['game'])), set(C['series_key'])
cnt = {k: collections.Counter() for k in ('src', 'team', 'map', 'map_oracle_share_den', 'map_oracle_share_num')}
tot = collections.Counter(); shards = {}; series = set(); games = set(); schema0 = None; bad_schema = []
for p in ([] if a.combine else fs):
    f = pq.ParquetFile(p)
    names = f.schema_arrow.names
    if schema0 is None:
        schema0 = names
    elif names != schema0:
        bad_schema.append(p.name)
    hb = [c for c in names if c.startswith('hb_f_')]
    t = f.read(columns=['game', 'map', 'series_key', 'teacher_team', 'side', 'team_a', 'team_b', 'blocks_src', 'y_kind', 'y_first'] + hb).to_pandas()
    shards[p.name] = dict(rows=len(t), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    games |= set(t.game.astype(str)); series |= set(t.series_key)
    tot['rows'] += len(t)
    team = t.team_a.where(t.side == 'A', t.team_b).astype(str)
    o = t.blocks_src == 'oracle'
    mv = o & (t.y_kind == 0)
    frl = mv & t.y_first.isin([0, 1, 3])
    tot['oracle_rows'] += int(o.sum()); tot['oracle_moves'] += int(mv.sum()); tot['oracle_frl'] += int(frl.sum())
    if hb:
        tot['hb_f_nan_cells_on_oracle_moves'] += int(t.loc[mv, hb].isna().values.sum())
    for k, v in t.blocks_src.value_counts().items(): cnt['src'][k] += int(v)
    for k, v in team[frl].value_counts().items(): cnt['team'][k] += int(v)
    for k, v in t.loc[frl, 'map'].value_counts().items(): cnt['map'][k] += int(v)
    for k, v in t['map'].value_counts().items(): cnt['map_oracle_share_den'][k] += int(v)
    for k, v in t.loc[o, 'map'].value_counts().items(): cnt['map_oracle_share_num'][k] += int(v)
if a.part >= 0:
    pickle.dump(dict(cnt=cnt, tot=tot, shards=shards, series=series, games=games, schema0=schema0, bad=bad_schema),
                open(f'{a.out}.part{a.part}', 'wb'))
    raise SystemExit(0)
if a.combine:
    for k in range(a.combine):
        P = pickle.load(open(f'{a.out}.part{k}', 'rb'))
        for c in cnt: cnt[c].update(P['cnt'][c])
        tot.update(P['tot']); shards.update(P['shards']); series |= P['series']; games |= P['games']
        bad_schema += P['bad'] + ([f'part{k}'] if schema0 is not None and P['schema0'] != schema0 else [])
        schema0 = schema0 or P['schema0']
    shards = dict(sorted(shards.items()))
share = {m: round(cnt['map_oracle_share_num'][m] / n, 4) for m, n in cnt['map_oracle_share_den'].items()}
rep = dict(dir=str(D), shards=len(fs), empty_markers=sorted(p.name for p in (D / '_empty').glob('*')) if (D / '_empty').exists() else [],
           games=len(games), series=len(series), totals=dict(tot), rows_by_blocks_src=dict(cnt['src']),
           oracle_frl_by_teacher=dict(cnt['team']), oracle_frl_by_map=dict(cnt['map']), oracle_share_by_map=share,
           max_shard_bytes=max(s['bytes'] for s in shards.values()), total_bytes=sum(s['bytes'] for s in shards.values()),
           schema_mismatch=bad_schema, n_columns=len(schema0 or []),
           cohort_overlap=dict(games=len(games & cg), series=len(series & cs)), shard_detail=shards)
Path(a.out).write_text(json.dumps(rep, indent=1))
print(json.dumps({k: v for k, v in rep.items() if k != 'shard_detail'}, indent=1))
