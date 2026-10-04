"""Leakage audit (Data lane, kageyama). Re-run on every dataset build; a dataset without a passing audit is not used.

    python3 tools/learn/audit.py DATASET.parquet [...] --purpose train|val [--split-file ...] [--json out.json]

Checks (each must be 0):
  unknown_game        row game not in the frozen split table
  wrong_split         row's frozen split is not the purpose (train rows must be 'train'; val rows 'val')
  heldout_map_name    map name is Maze / Trauma / Trophy
  heldout_map_hash    map_hash equals any held-out map's hash in any era (catches renamed or re-labelled maps)
  test_series         series bucket 0 (test) or 1 (val, for a train set) appears
  map_mismatch        the replay's own map name differs from the split table's
  local_gate_seed     local rows (source=local) on seeds < 1000 (gate 1-3, reserve 4-5, anything below training range)
  local_heldout_map   local rows on maps/live/{maze,trauma,trophy} or their twins
  gate_tag            rows tagged gate
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import splits as SP


def audit(paths, purpose, split_file):
    import pandas as pd
    S = pd.read_parquet(split_file)
    held_hashes = set(S[S['map'].isin(SP.HELDOUT_MAPS)].map_hash.dropna().astype(str))
    S = S.set_index('game')
    want = {'train': {'train'}, 'val': {'val'}, 'test': {'test'}}[purpose]
    rep = dict(purpose=purpose, files=[], rows=0, games=0)
    fails = dict(unknown_game=0, wrong_split=0, heldout_map_name=0, heldout_map_hash=0, test_series=0, map_mismatch=0,
                 local_gate_seed=0, local_heldout_map=0, gate_tag=0)
    games = set()
    for p in paths:
        cols = ['game', 'map']
        import pyarrow.parquet as pq
        have = set(pq.ParquetFile(p).schema.names)
        cols += [c for c in ('map_hash', 'source', 'seed', 'map_file', 'tag') if c in have]
        df = pd.read_parquet(p, columns=cols)
        rep['files'].append(dict(path=str(p), rows=len(df)))
        rep['rows'] += len(df)
        loc = df[df.source == 'local'] if 'source' in df else df.iloc[0:0]
        srv = df.drop(loc.index)
        g = srv.game.astype(str)
        games |= set(g)
        known = g.isin(S.index)
        fails['unknown_game'] += int((~known).sum())
        s = S.reindex(g)
        fails['wrong_split'] += int((known & ~s.split.isin(want).values).sum())
        fails['test_series'] += int((known & (s.bucket.values == 0)).sum()) if purpose != 'test' else 0
        if purpose == 'train':
            fails['test_series'] += int((known & (s.bucket.values == 1)).sum())
        fails['heldout_map_name'] += int(df['map'].isin(SP.HELDOUT_MAPS).sum())
        if 'map_hash' in df:
            fails['heldout_map_hash'] += int(df.map_hash.astype(str).isin(held_hashes).sum())
        fails['map_mismatch'] += int((known & (s['map'].values != srv['map'].values)).sum())
        if len(loc):
            fails['local_gate_seed'] += int((loc.seed.astype(int) < SP.TRAIN_SEED_MIN).sum())
            mf = loc.map_file.astype(str) if 'map_file' in loc else loc['map'].astype(str).str.lower()
            fails['local_heldout_map'] += int(mf.apply(lambda m: any(h in Path(m).stem for h in SP.HELDOUT_FILES)).sum())
        if 'tag' in df:
            fails['gate_tag'] += int((df.tag.astype(str) == 'gate').sum())
    rep['games'] = len(games)
    rep['checks'] = fails
    rep['pass'] = all(v == 0 for v in fails.values())
    return rep


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--purpose', default='train')
    ap.add_argument('--split-file', default='build/learn/splits/games_split_v1.parquet')
    ap.add_argument('--json', default='')
    a = ap.parse_args()
    rep = audit(a.paths, a.purpose, a.split_file)
    print(json.dumps(rep, indent=1))
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=1))
    sys.exit(0 if rep['pass'] else 1)
