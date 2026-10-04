"""Shenzhen H-SZ28 (and the unit-11 check): eats by the frame's own origin label (bed / ally_corpse / enemy_corpse) and
corpse-pearl flow per side: corpse pearls a side's deaths create (spawns with origin = side), who eats them, and how many
are left uneaten. Post-m2 games on the cap maps with a top-ten side or us.
  python3 build/shenzhen/tree/tools/shenzhen/corpse.py --time 150"""
import argparse, collections, os, sys, time
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
import pandas as pd
OUT = ROOT / 'build/shenzhen/corpse'
def one(a):
    gid, ta, tb, mp = a
    from tools.analysis.features.frame import decode
    try:
        g = decode(f'public_replays/corpus/replays/{gid}.replay')
    except Exception:
        return []
    c = {t: collections.Counter() for t in 'AB'}
    for e in g['events']['eats']:
        ph = 'early' if e['round'] < 150 else 'late'
        c[e['team']][f"{e.get('origin') or 'unknown'}_{ph}"] += 1
    made = collections.Counter(s['origin'] for s in g['events']['spawns'] if s['origin'] in ('A', 'B') and s['round'] >= 150)
    for t in 'AB':
        o = 'B' if t == 'A' else 'A'
        c[t]['corpse_made_late'] = made[t]
        c[t]['corpse_eaten_by_enemy_late'] = c[o]['enemy_corpse_late']
    return [dict(game=gid, map=mp, side=t, team={'A': ta, 'B': tb}[t], R=g['last_round'], win=g['winner'] == t, **c[t]) for t in 'AB']
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--time', type=float, default=150); a = ap.parse_args(); t0 = time.time()
    import duckdb, multiprocessing as mp
    L = duckdb.sql("""select distinct L.game, L.team, L.opp, L.map from 'build/shenzhen/lean/*.parquet' L
        join 'build/s1/corpus/teams.parquet' T on T.team=L.team join 'build/s1/corpus/teams.parquet' T2 on T2.team=L.opp
        where L.side='A' and cast(L.started_at as timestamptz) >= '2026-10-02 04:31:00+00'
        and L.map in ('Slithery Fight','Around UNSW','Islands','Trauma','Portals')
        and (T.crank<=10 or T2.crank<=10 or L.team='7' or L.opp='7')""").df()
    done = set(duckdb.sql(f"select distinct game from '{OUT}/part-*.parquet'").df().game) if OUT.exists() and list(OUT.glob('part-*.parquet')) else set()
    L = L[~L.game.isin(done)].sample(frac=1, random_state=3)
    us = L[(L.team == '7') | (L.opp == '7')]; L = pd.concat([us.head(60), L[~L.game.isin(us.game.head(60))]])
    print('done', len(done), 'queue', len(L), flush=True)
    rows, n = [], 0
    with mp.get_context('fork').Pool(4) as p:
        it = iter([(r.game, r.team, r.opp, r.map) for r in L.itertuples()]); pend = collections.deque()
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
        pd.DataFrame(rows).fillna(0).to_parquet(str(f) + '.tmp', index=False); os.rename(str(f) + '.tmp', f)
    print('games', n, f'{time.time() - t0:.0f}s')
if __name__ == '__main__':
    main()
