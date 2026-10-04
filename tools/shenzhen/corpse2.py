"""Shenzhen H-SZ28 by birth cohort (Himeji H28-03): every corpse pearl born in rounds [150, R-50] is followed for 50 rounds.
Fate: eaten by its own side / by the other side / uneaten. Consumer = first eat at that cell after the birth round
(a cell holds at most one pearl). Also split by the donor's death context: an enemy head within 3 (Chebyshev, torus)
of the donor's head at death ('contact') or not ('home').
  python3 build/shenzhen/tree/tools/shenzhen/corpse2.py --time 150"""
import argparse, bisect, collections, os, sys, time
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
import pandas as pd
OUT = ROOT / 'build/shenzhen/corpse2'
HZ = 50
def one(a):
    gid, ta, tb, mp = a
    from tools.analysis.features.frame import decode
    try:
        g = decode(f'public_replays/corpus/replays/{gid}.replay')
    except Exception:
        return []
    W, H, R = g['W'], g['H'], g['last_round']
    cd = lambda p, q: max(min(abs(p[0] - q[0]), W - abs(p[0] - q[0])), min(abs(p[1] - q[1]), H - abs(p[1] - q[1])))
    death = {d['id']: d for d in g['events']['deaths']}
    ctx = {}
    for i, d in death.items():
        r = max(0, min(d['round'], R)); t = d['team']
        heads = [b[0] for (tt, b) in g['rounds'][r].values() if tt != t]
        h = d.get('head')
        ctx[i] = 'contact' if h is not None and any(cd(h, x) <= 3 for x in heads) else 'home'
    eats_by_cell = collections.defaultdict(list)
    for e in g['events']['eats']:
        eats_by_cell[tuple(e['cell'])].append((e['round'], e['team']))
    for v in eats_by_cell.values(): v.sort()
    c = {t: collections.Counter() for t in 'AB'}
    for s in g['events']['spawns']:
        side = s['origin']
        if side not in ('A', 'B') or not (150 <= s['round'] <= R - HZ):
            continue
        k = ctx.get(s.get('donor'), 'home')
        lst = eats_by_cell.get(tuple(s['cell']), [])
        j = bisect.bisect_left(lst, (s['round'], ''))
        fate = 'uneaten'
        if j < len(lst) and lst[j][0] <= s['round'] + HZ:
            fate = 'self' if lst[j][1] == side else 'enemy'
        c[side][f'{k}_{fate}'] += 1; c[side][f'all_{fate}'] += 1; c[side][f'{k}_born'] += 1; c[side]['born'] += 1
    return [dict(game=gid, map=mp, side=t, team={'A': ta, 'B': tb}[t], win=g['winner'] == t, **c[t]) for t in 'AB']
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--time', type=float, default=150); a = ap.parse_args(); t0 = time.time()
    import duckdb, multiprocessing as mp
    L = duckdb.sql("""select distinct L.game, L.team, L.opp, L.map from 'build/shenzhen/lean/*.parquet' L
        join 'build/s1/corpus/teams.parquet' T on T.team=L.team join 'build/s1/corpus/teams.parquet' T2 on T2.team=L.opp
        where L.side='A' and cast(L.started_at as timestamptz) >= '2026-10-02 04:31:00+00' and L.R >= 250
        and L.map in ('Slithery Fight','Around UNSW','Islands','Trauma','Portals','Australia')
        and (T.crank<=10 or T2.crank<=10 or L.team='7' or L.opp='7')""").df()
    done = set(duckdb.sql(f"select distinct game from '{OUT}/part-*.parquet'").df().game) if OUT.exists() and list(OUT.glob('part-*.parquet')) else set()
    L = L[~L.game.isin(done)].sample(frac=1, random_state=4)
    us = L[(L.team == '7') | (L.opp == '7')]; L = pd.concat([us.head(70), L[~L.game.isin(us.game.head(70))]])
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
