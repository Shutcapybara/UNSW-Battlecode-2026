"""Shenzhen: sprint tax (segments paid for multi-step moves), queen vs all dragons, per side (post-m2 sample).
Rows: game side team opp R q_paid q_paid_after250 q_steps_multi all_paid all_multi_moves all_moves q_alive_end
  python3 build/shenzhen/tree/tools/shenzhen/qpay.py --time 150"""
import argparse, collections, os, sys, time
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
import pandas as pd
OUT = ROOT / 'build/shenzhen/qpay'


def one(a):
    gid, ta, tb = a
    from tools.analysis.features.frame import decode
    try:
        g = decode(f'public_replays/corpus/replays/{gid}.replay')
    except Exception:
        return []
    init = g['rounds'][0]; R = g['last_round']
    queen = {t: min(i for i, (tt, _) in init.items() if tt == t) for t in 'AB'}
    c = {t: collections.Counter() for t in 'AB'}
    for x in g['events']['actions']:
        if x['kind'] != 'move' or not x.get('dirs'):
            continue
        t = x['team']; p = x.get('paid') or 0; k = c[t]
        k['all_moves'] += 1; k['all_paid'] += p; k['all_multi'] += len(x['dirs']) > 1
        if x['id'] == queen[t]:
            k['q_moves'] += 1; k['q_paid'] += p; k['q_multi'] += len(x['dirs']) > 1
            if x['round'] >= 250: k['q_paid250'] += p
    return [dict(game=gid, side=t, team={'A': ta, 'B': tb}[t], opp={'A': tb, 'B': ta}[t], R=R,
                 q_alive_end=g['final'][t]['queen'] > 0, qlen_end=g['final'][t]['queen'], **c[t]) for t in 'AB']


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--time', type=float, default=150); a = ap.parse_args(); t0 = time.time()
    import duckdb, multiprocessing as mp
    L = duckdb.sql("""select distinct L.game, L.team, L.opp from 'build/shenzhen/lean/*.parquet' L
        join 'build/s1/corpus/teams.parquet' T on T.team=L.team join 'build/s1/corpus/teams.parquet' T2 on T2.team=L.opp
        where L.side='A' and cast(L.started_at as timestamptz) >= '2026-10-02 03:49:00+00' and L.R>=499
        and (T.crank<=10 or T2.crank<=10 or L.team='7' or L.opp='7')""").df()
    done = set(duckdb.sql(f"select distinct game from '{OUT}/part-*.parquet'").df().game) if OUT.exists() and list(OUT.glob('part-*.parquet')) else set()
    L = L[~L.game.isin(done)].sample(frac=1, random_state=5)
    us = L[(L.team == '7') | (L.opp == '7')]; L = pd.concat([us.head(80), L[~L.game.isin(us.game.head(80))]])
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
    print('games', n, f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
