"""Shenzhen hazard pass (post-m2 sample): per-dragon exposure and enemy-caused deaths, queen vs non-queen, by killer
team; queen exposure (distance to nearest enemy / ally head); queen meals by origin and phase.
  python3 build/shenzhen/tree/tools/shenzhen/hazard.py --time 150      # resumable; build/shenzhen/hazard/part-*.parquet
Rows: kind='exp'  (game, side, team, opp, queen, lbin, dragon_rounds, enemy_deaths, h2h_deaths, body_deaths)
      kind='qexp' (game, side, team, opp, rounds, e3 (enemy head within 3), e6, a3 (ally head within 3), dmin_mean)
      kind='meal' (game, side, team, phase, origin, n)
Queen = lowest-id starting dragon of the side. Distances are torus Manhattan (ignore walls/portals: an upper bound on danger)."""
import argparse, collections, os, sys, time
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
import pandas as pd, numpy as np
OUT = ROOT / 'build/shenzhen/hazard'
LB = lambda L: '2-3' if L <= 3 else '4-6' if L <= 6 else '7-12' if L <= 12 else '13+'


def one(args):
    gid, ta, tb = args
    from tools.analysis.features.frame import decode
    try:
        g = decode(f'public_replays/corpus/replays/{gid}.replay')
    except Exception as e:
        return []
    W, H, R = g['W'], g['H'], g['last_round']
    team = {'A': ta, 'B': tb}
    init = g['rounds'][0]
    queen = {t: min(i for i, (tt, _) in init.items() if tt == t) for t in 'AB'}
    death = {d['id']: d for d in g['events']['deaths']}
    exp = collections.Counter(); dth = collections.Counter()
    qx = {t: collections.Counter() for t in 'AB'}
    dist = lambda a, b: min(abs(a[0] - b[0]), W - abs(a[0] - b[0])) + min(abs(a[1] - b[1]), H - abs(a[1] - b[1]))
    for r in range(R + 1):
        rd = g['rounds'][r]
        heads = {'A': [], 'B': []}
        for i, (t, b) in rd.items():
            heads[t].append((i, b[0]))
            exp[(t, i == queen[t], LB(len(b)))] += 1
        for t in 'AB':
            q = rd.get(queen[t])
            if q is None or r < 10:
                continue
            o = 'B' if t == 'A' else 'A'
            de = min((dist(q[1][0], h) for _, h in heads[o]), default=99)
            da = min((dist(q[1][0], h) for i, h in heads[t] if i != queen[t]), default=99)
            c = qx[t]; c['rounds'] += 1; c['e3'] += de <= 3; c['e6'] += de <= 6; c['a3'] += da <= 3; c['dsum'] += min(de, 40)
    for d in g['events']['deaths']:
        if d.get('killer_team') is None or d['killer_team'] == d['team'] or d['round'] > R:
            continue
        b = g['rounds'][max(0, d['round'])].get(d['id'])
        L = len(b[1]) if b else d.get('length', 2)
        dth[(d['team'], d['id'] == queen[d['team']], LB(L), d['cause'])] += 1
    rows = []
    for (t, isq, lb), n in exp.items():
        rows.append(dict(kind='exp', game=gid, side=t, team=team[t], opp=team['B' if t == 'A' else 'A'], queen=isq, lbin=lb,
                         dragon_rounds=n, enemy_deaths=sum(v for k, v in dth.items() if k[:3] == (t, isq, lb)),
                         h2h_deaths=dth.get((t, isq, lb, 'h2h'), 0), body_deaths=dth.get((t, isq, lb, 'body'), 0)))
    for t in 'AB':
        c = qx[t]
        rows.append(dict(kind='qexp', game=gid, side=t, team=team[t], opp=team['B' if t == 'A' else 'A'], rounds=c['rounds'],
                         e3=c['e3'], e6=c['e6'], a3=c['a3'], dmin_mean=c['dsum'] / c['rounds'] if c['rounds'] else None))
    meals = collections.Counter()
    for e in g['events']['eats']:
        t = e['team']
        if e['id'] == queen[t] and 0 <= e['round'] <= R:
            ph = 'r0-149' if e['round'] < 150 else 'r150-399' if e['round'] < 400 else 'r400+'
            meals[(t, ph, e.get('origin') or 'unknown')] += 1
    for (t, ph, org), n in meals.items():
        rows.append(dict(kind='meal', game=gid, side=t, team=team[t], phase=ph, origin=org, n=n))
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--time', type=float, default=150); ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args(); t0 = time.time()
    import duckdb, multiprocessing as mp
    L = duckdb.sql("select distinct game, team, opp, side from 'build/shenzhen/lean/*.parquet' where side='A' and cast(started_at as timestamptz) >= '2026-10-02 03:49:00+00'").df()
    done = set()
    if OUT.exists() and list(OUT.glob('part-*.parquet')):
        done = set(duckdb.sql(f"select distinct game from '{OUT}/part-*.parquet'").df().game)
    L = L[~L.game.isin(done)].sample(frac=1, random_state=7)
    us = L[(L.team == '7') | (L.opp == '7')]; L = pd.concat([us, L[~L.game.isin(us.game)]])
    print('done', len(done), 'queue', len(L), flush=True)
    rows, n = [], 0
    with mp.get_context('fork').Pool(a.jobs) as p:
        it = iter([(r.game, r.team, r.opp) for r in L.itertuples()]); pend = collections.deque()
        for _ in range(a.jobs * 2):
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
