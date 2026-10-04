"""Shenzhen pass 2 (post-m2 games with a top-10 side): can the enemy queen be found, and how are crowns fed.
Rows kind='vis'  (game, side, team, opp, alive_rounds, seen_rounds [queen segment within the enemy's 7x7 vision of any enemy head],
                  first_seen, home50/150/300/490 [torus Chebyshev distance of queen head from its spawn head; -1 dead])
     kind='feed' (game, side, team, meal_round, donor_cause, donor_len, donor_age, lag [meal round - donor death round])
  python3 build/shenzhen/tree/tools/shenzhen/qsight.py --time 150"""
import argparse, collections, os, sys, time
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
import pandas as pd
OUT = ROOT / 'build/shenzhen/qsight'


def one(args):
    gid, ta, tb = args
    from tools.analysis.features.frame import decode
    try:
        g = decode(f'public_replays/corpus/replays/{gid}.replay')
    except Exception:
        return []
    W, H, R = g['W'], g['H'], g['last_round']
    team = {'A': ta, 'B': tb}
    init = g['rounds'][0]
    queen = {t: min(i for i, (tt, _) in init.items() if tt == t) for t in 'AB'}
    spawn = {t: init[queen[t]][1][0] for t in 'AB'}
    cd = lambda a, b: max(min(abs(a[0] - b[0]), W - abs(a[0] - b[0])), min(abs(a[1] - b[1]), H - abs(a[1] - b[1])))
    rows = []
    for t in 'AB':
        o = 'B' if t == 'A' else 'A'
        alive = seen = 0; first = None; home = {}
        for r in range(R + 1):
            rd = g['rounds'][r]; q = rd.get(queen[t])
            if q is None:
                continue
            if r in (50, 150, 300, 490):
                home[r] = cd(q[1][0], spawn[t])
            if r < 5:
                continue
            alive += 1
            heads = [b[0] for (tt, b) in rd.values() if tt == o]
            if any(cd(s, h) <= 3 for h in heads for s in q[1]):
                seen += 1
                if first is None: first = r
        rows.append(dict(kind='vis', game=gid, side=t, team=team[t], opp=team[o], alive_rounds=alive, seen_rounds=seen,
                         first_seen=first, **{f'home{c}': home.get(c, -1) for c in (50, 150, 300, 490)}))
    death = {d['id']: d for d in g['events']['deaths']}
    born = {}
    for s in g['events']['splits']:
        born[s['child']] = s['round']
    for e in g['events']['eats']:
        t = e['team']
        if e['id'] != queen[t] or e.get('donor') is None:
            continue
        d = death.get(e['donor'])
        if d is None or d['team'] != t:
            continue
        rows.append(dict(kind='feed', game=gid, side=t, team=team[t], meal_round=e['round'], donor_cause=d['cause'],
                         donor_len=d.get('length'), donor_age=d.get('age'), lag=e['round'] - d['round']))
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--time', type=float, default=150); a = ap.parse_args(); t0 = time.time()
    import duckdb, multiprocessing as mp
    L = duckdb.sql("""select distinct L.game, L.team, L.opp from 'build/shenzhen/lean/*.parquet' L
        join 'build/s1/corpus/teams.parquet' T on T.team=L.team join 'build/s1/corpus/teams.parquet' T2 on T2.team=L.opp
        where L.side='A' and cast(L.started_at as timestamptz) >= '2026-10-02 03:49:00+00' and L.R>=150
        and (T.crank<=10 or T2.crank<=10 or L.team='7' or L.opp='7')""").df()
    done = set()
    if OUT.exists() and list(OUT.glob('part-*.parquet')):
        done = set(duckdb.sql(f"select distinct game from '{OUT}/part-*.parquet'").df().game)
    L = L[~L.game.isin(done)].sample(frac=1, random_state=11)
    print('done', len(done), 'queue', len(L), flush=True)
    rows, n = [], 0
    with mp.get_context('fork').Pool(4) as p:
        it = iter([(r.game, r.team, r.opp) for r in L.itertuples()]); pend = collections.deque()
        for _ in range(8):
            x = next(it, None)
            if x: pend.append(p.apply_async(one, (x,)))
        while pend:
            rows += pend.popleft().get(); n += 1
            if time.time() - t0 < a.time:
                x = next(it, None)
                if x: pend.append(p.apply_async(one, (x,)))
    OUT.mkdir(parents=True, exist_ok=True)
    if rows:
        f = OUT / f'part-{time.strftime("%Y%m%dT%H%M%S")}-{os.getpid()}.parquet'
        pd.DataFrame(rows).to_parquet(str(f) + '.tmp', index=False); os.rename(str(f) + '.tmp', f)
    print('games', n, 'rows', len(rows), f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
