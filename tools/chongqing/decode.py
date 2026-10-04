"""chongqing: prioritised incremental decode of post-change corpus games into the s1 store.

  python3 tools/chongqing/decode.py --jobs 3 --time 110 [--era post]

Order: team 7 first, then current top-10 sides (balanced over team x map, newest first), then the builder's own
balanced round-robin over the remaining in-scope games. Resumable; one Cowork VM call per batch (<= 180 s).
Run from the repo root (wt-chongqing has build/ and public_replays/ symlinked to the main checkout).
"""
import argparse, collections, sys, time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from tools.s1 import build as B


def priority_queue(games, teams, done):
    cr = dict(zip(teams.team, teams.crank))
    top10 = set(t for t, c in cr.items() if c is not None and c == c and c <= 10)
    us = str(B.US)
    g = games[games.in_scope & ~games.game.isin(done)].sort_values('started_at', ascending=False)
    out, seen = [], set()
    for row in g.itertuples():
        if us in (row.team_a, row.team_b) and row.game not in seen:
            seen.add(row.game); out.append(row.game)
    lists = collections.defaultdict(list)
    for row in g.itertuples():
        if row.game in seen:
            continue
        for t in (row.team_a, row.team_b):
            if t in top10:
                lists[(t, row.map)].append(row.game)
    depth = max((len(v) for v in lists.values()), default=0)
    keys = sorted(lists, key=lambda k: (cr.get(k[0]) or 0, k[1]))
    for d in range(depth):
        for k in keys:
            v = lists[k]
            if d < len(v) and v[d] not in seen:
                seen.add(v[d]); out.append(v[d])
    n_us, n_top = sum(1 for x in out if x in set(g[(g.team_a == us) | (g.team_b == us)].game)), len(out)
    rest = [x for x in B.corpus_queue(games, teams, done | seen)]
    print(f'queue: us {n_us}, top10 {n_top - n_us}, rest {len(rest)}')
    return out + rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--time', type=float, default=110)
    ap.add_argument('--era', default='post')
    ap.add_argument('--map-era', default='post-m2', help="games.map_era to decode first ('' = no filter)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--flush", type=int, default=40)
    a = ap.parse_args()
    games, teams = B.build_games()
    store = B.OUT / 'corpus'
    done = B.done_games(store)
    if a.era:
        games = games[games.era == a.era]
    if a.map_era:
        games = games[games.map_era == a.map_era]
    q = priority_queue(games, teams, done)
    if a.limit:
        q = q[:a.limit]
    print(f'done {len(done)}, queue {len(q)}')
    meta = games.set_index('game')[['team_a', 'team_b']].to_dict('index')
    tasks = ((B.CORPUS / 'replays' / f'{gid}.replay', gid, dict(meta[gid], source='corpus')) for gid in q
             if (B.CORPUS / 'replays' / f'{gid}.replay').exists())
    B.run_batch(store, tasks, a.jobs, a.time, flush_every=a.flush)


if __name__ == '__main__':
    main()
