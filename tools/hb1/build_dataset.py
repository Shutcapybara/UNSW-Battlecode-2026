"""HB-1 step 0: game tables + v5 rows for every team-62 replay on disk.

    .venv/bin/python tools/hb1/build_dataset.py [--jobs N]

Writes build/hb1/games.parquet (one row per game: corpus + era set) and
build/hb1/v5/{corpus,era}/<game>.parquet (+ .traj.json) via features_v5.
Incremental: already-extracted games are skipped, so it is re-run after each sync.
"""
import argparse, json, os, subprocess, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / os.environ.get('HB_BUILD', 'hb1')   # HB_BUILD/HB_TEAM/HB_TAG: other teams (lane tt)
TAG = os.environ.get('HB_TAG', 'hb1')
TEAM = int(os.environ.get('HB_TEAM', 62))


def games_table():
    rows = []
    for l in open(ROOT / 'public_replays/corpus/index.jsonl'):
        r = json.loads(l)
        if TEAM not in (r['team_a'], r['team_b']) or r['status'] != 'completed':
            continue
        side = 'A' if r['team_a'] == TEAM else 'B'
        p = ROOT / f"public_replays/corpus/replays/{r['game_id']}.replay"
        if not p.exists():
            continue
        rows.append(dict(game=r['game_id'], set='corpus', side=side, opp=r['team_b'] if side == 'A' else r['team_a'],
                         opp_name='', sub=None, map=r['map_name'], ranked=r['ranked'], t=r['finished_at'],
                         series=r['series_id'], won=(r['winner'] or '').upper() == side, path=str(p)))
    man = ROOT / 'experiment_data/team_recon_62_20260927_glm/manifest.jsonl'
    for l in (open(man) if TEAM == 62 and man.exists() else []):   # era set (submission ids) exists for team 62 only
        r = json.loads(l)
        p = ROOT / f"public_replays/team-62/{r['game_id']}.replay"
        if not p.exists():
            continue
        rows.append(dict(game=r['game_id'], set='era', side=r['target_side'], opp=r['opponent_id'],
                         opp_name=r.get('opponent_name', ''), sub=r['target_submission'], map=r['map_name'],
                         ranked=r.get('ranked'), t=r['completed_at'], series=r['series_id'],
                         won=(r['winner'] or '').upper() == r['target_side'], path=str(p)))
    G = pd.DataFrame(rows)
    G['t'] = pd.to_datetime(G.t, utc=True)
    G = G.sort_values('t').drop_duplicates(['set', 'game']).reset_index(drop=True)
    return G


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2))
    a = ap.parse_args()
    B.mkdir(parents=True, exist_ok=True)
    G = games_table()
    G.to_parquet(B / 'games.parquet')
    print('team', TEAM, G.groupby('set').size().to_dict(), 'overlap', len(set(G[G.set == 'corpus'].game) & set(G[G.set == 'era'].game)))
    for s in ('corpus', 'era'):
        g = G[G.set == s]
        if g.empty:
            continue
        sides = {str(r.game): r.side for r in g.itertuples()}
        sp = B / f'sides_{s}.json'
        sp.write_text(json.dumps(sides))
        subprocess.run([sys.executable, str(ROOT / 'tools/team_recon_claude/features_v5.py'), str(B / 'v5' / s), str(sp),
                        *g.path.tolist(), '--jobs', str(a.jobs)], check=True, stdout=subprocess.DEVNULL)
        errs = list((B / 'v5' / s).glob('*.error'))
        print(s, 'parquets', len(list((B / 'v5' / s).glob('*.parquet'))), 'errors', len(errs))
