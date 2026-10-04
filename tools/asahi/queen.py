#!/usr/bin/env python3
"""Per game-side queen table from the engine's own result block (FRAME_VERSION 7 `final[side]['queen']`: the team's
original lowest-id dragon's length at the end, 0 once dead, no succession), plus the dragons-table derivation for a
cross-check. Writes <run>/queen.parquet: game, side, queen_end, queen_body, reason, winner, last_round, q_alive_dragons.

    python tools/asahi/queen.py BOT --panel both [--jobs 14]
"""
from __future__ import annotations

import argparse, glob, os, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/asahi'))
os.chdir(ROOT)
import panel as P  # noqa: E402


def one(args):
    path, cache = args
    from tools.analysis.features.frame import load
    g = load(path, cache_dir=cache)
    return [dict(game=Path(path).stem, side=t, queen_end=int(g['final'][t].get('queen', 0)),
                 queen_body=int(g['final'][t].get('queen_body', -1)), reason=g['reason'], winner=g['winner'],
                 last_round=int(g['last_round'])) for t in 'AB']


def main():
    import pandas as pd
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--panel', default='both'); ap.add_argument('--jobs', type=int, default=14)
    a = ap.parse_args()
    jobs = min(a.jobs, int(os.environ.get('ASAHI_MAX_WORKERS', '14')))
    for panel in (['pool', 'gen'] if a.panel == 'both' else [a.panel]):
        root = P.run_root(a.bot, panel)
        reps = sorted(glob.glob(str(root / 'replays/*.replay')))
        with ProcessPoolExecutor(jobs) as ex:
            rows = [r for rs in ex.map(one, [(p, str(root / 'frames')) for p in reps], chunksize=4) for r in rs]
        Q = pd.DataFrame(rows)
        dp = root / 'features' / 'dragons.parquet'
        if dp.exists():
            D = pd.read_parquet(dp, columns=['game', 'id', 'side', 'died', 'initial'])
            q = D[D['initial'].astype(bool)].sort_values('id').groupby(['game', 'side']).first().reset_index()
            q['q_alive_dragons'] = q['died'].isna().astype(int)
            Q = Q.merge(q[['game', 'side', 'id', 'died', 'q_alive_dragons']], on=['game', 'side'], how='left')
        Q.to_parquet(root / 'queen.parquet', index=False)
        alive = (Q.queen_end > 0)
        print(panel, len(Q), 'sides; header queen alive', int(alive.sum()),
              '; dragons-table alive', int(Q.get('q_alive_dragons', pd.Series(dtype=int)).sum()),
              '; disagree', int((alive.astype(int) != Q.get('q_alive_dragons', alive.astype(int))).sum()))
        print(Q[alive].head(5).to_string())


if __name__ == '__main__':
    main()
