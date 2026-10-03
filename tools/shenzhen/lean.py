"""Shenzhen lean decoder: one row per (game, side) with opening, endgame and queen columns, ~0.4 s/game.

Why: the full S-1 decode (tools/s1/build.py) costs ~9 CPU-s/game on the Cowork VM (4 cores), i.e. ~13 h for the 20k
post-change in-scope games; frame.decode alone is ~0.4 s. This table carries what the post-change targets need and
nothing else. Territory and bed capture (beds.resolve) are not here; they stay with the full store.

  python3 build/shenzhen/tree/tools/shenzhen/lean.py --era post --time 140 --jobs 4     # repo root; resumable
Output: build/shenzhen/lean/part-*.parquet (append-only; a game is done once it appears in any part).
Columns (per side): game map team opp side ranked started_at R reason win (official, 1/0/0.5) eng_win n_initial
  at checkpoints c in CK: units@c total@c longest@c eats@c bed@c corpse@c splits@c transits@c tdied3@c deaths@c
  qlen@c (queen length, 0 dead) ; end: units_end total_end longest_end qlen_end opp_qlen_end opp_total_end ...
  queen: q_id q_death_round q_death_cause q_killer_team q_moves q_eats q_splits q_maxlen q_steps
Queen = the side's lowest-id starting dragon (engine 1.2.3; no succession; keeps id and head on a split).
"""
import argparse, collections, json, os, sys, time
from pathlib import Path
ROOT = Path.cwd()
sys.path[:0] = [str(ROOT)]
if sys.platform.startswith('linux') and (ROOT / 'build/s1-pylib').exists():
    sys.path.append(str(ROOT / 'build/s1-pylib'))
import numpy as np, pandas as pd

CK = (10, 25, 50, 100, 150, 250, 400, 490)
DXY = ((0, -1), (1, 0), (0, 1), (-1, 0))   # N E S W (frame.py convention: y grows south)
OUT = ROOT / 'build' / 'shenzhen' / 'lean'
CORPUS = ROOT / 'public_replays' / 'corpus'


def side_rows(path, gid, meta):
    from tools.analysis.features.frame import decode
    g = decode(str(path))
    R, W, H, nbr = g['last_round'], g['W'], g['H'], g['nbr']
    rounds, ev = g['rounds'], g['events']
    init = rounds[0]
    queen = {t: min((i for i, (tt, _) in init.items() if tt == t), default=None) for t in 'AB'}
    # per-dragon cumulative events by round
    def cum(rows_by_side):
        return {t: np.cumsum(rows_by_side[t]) for t in 'AB'}
    z = lambda: {t: np.zeros(R + 2) for t in 'AB'}
    eats, bed, corpse, splits, deaths, transits, tdied3 = z(), z(), z(), z(), z(), z(), z()
    death_of = {d['id']: d for d in ev['deaths']}
    q = {t: dict(q_moves=0, q_steps=0, q_eats=0, q_splits=0) for t in 'AB'}
    for e in ev['eats']:
        r, t = e['round'], e['team']
        if 0 <= r <= R:
            eats[t][r] += 1
            if e.get('origin') == 'bed':
                bed[t][r] += 1
            elif e.get('origin') in ('ally_corpse', 'enemy_corpse', 'corpse') or (e.get('origin') or '').endswith('corpse'):
                corpse[t][r] += 1
            if e['id'] == queen[t]:
                q[t]['q_eats'] += 1
    for s in ev['splits']:
        if 0 <= s['round'] <= R:
            splits[s['team']][s['round']] += 1
            if s['parent'] == queen[s['team']]:
                q[s['team']]['q_splits'] += 1
    for d in ev['deaths']:
        if 0 <= d['round'] <= R:
            deaths[d['team']][d['round']] += 1
    for a in ev['actions']:
        r, i, t = a['round'], a['id'], a['team']
        if a['kind'] != 'move' or not a.get('dirs') or not (0 <= r <= R):
            continue
        if i == queen[t]:
            q[t]['q_moves'] += 1
            q[t]['q_steps'] += len(a['dirs'])
        b = rounds[r].get(i)
        if b is None:
            continue
        cur = b[1][0]
        for d in a['dirs']:
            nx = nbr[cur][d] if d < 4 else None
            if nx is None:
                break
            gx = ((cur[0] + DXY[d][0]) % W, (cur[1] + DXY[d][1]) % H)
            if nx != gx:
                transits[t][r] += 1
                dd = death_of.get(i)
                if dd and 0 <= dd['round'] - r <= 3:
                    tdied3[t][r] += 1
            cur = nx
    C = {k: cum(v) for k, v in dict(eats=eats, bed=bed, corpse=corpse, splits=splits, deaths=deaths, transits=transits,
                                     tdied3=tdied3).items()}

    def state(r, t):
        rr = min(r, R)
        bodies = [len(b) for (tt, b) in rounds[rr].values() if tt == t]
        qb = rounds[rr].get(queen[t])
        return len(bodies), sum(bodies), max(bodies, default=0), (len(qb[1]) if qb else 0)
    qmax = {t: max((len(rounds[r][queen[t]][1]) for r in range(R + 1) if queen[t] in rounds[r]), default=0) for t in 'AB'}
    fin = g['final']
    res_a = meta.get('result_a')
    out = []
    for t in 'AB':
        o = 'B' if t == 'A' else 'A'
        row = dict(game=gid, map=('Prisoners Dilemma 10' if g['map'] == 'Prisoners Dilemma' and g.get('n_initial') == 10 else g['map']),
                   side=t, team=str(meta['team_a'] if t == 'A' else meta['team_b']), opp=str(meta['team_b'] if t == 'A' else meta['team_a']),
                   ranked=bool(meta.get('ranked')), started_at=str(meta.get('started_at')), R=R, reason=g['reason'],
                   eng_win=1.0 if g['winner'] == t else 0.0 if g['winner'] == o else 0.5, n_initial=g.get('n_initial'),
                   win=(None if res_a is None else (res_a if t == 'A' else 1 - res_a)))
        for c in CK:
            u, tot, lg, ql = state(c, t)
            ou, otot, olg, oql = state(c, o)
            cc = min(c, R)
            row.update({f'units@{c}': u, f'total@{c}': tot, f'longest@{c}': lg, f'qlen@{c}': ql, f'opp_total@{c}': otot,
                        f'opp_qlen@{c}': oql, f'alive@{c}': int(c <= R)})
            for k, v in C.items():
                row[f'{k}@{c}'] = float(v[t][cc])
        f, fo = fin[t], fin[o]
        row.update(units_end=f['units'], total_end=f['total'], longest_end=f['longest'], qlen_end=f['queen'],
                   opp_units_end=fo['units'], opp_total_end=fo['total'], opp_longest_end=fo['longest'], opp_qlen_end=fo['queen'])
        for k, v in C.items():
            row[f'{k}_end'] = float(v[t][R])
        qd = death_of.get(queen[t])
        row.update(q_id=queen[t], q_death_round=(qd['round'] if qd else None), q_death_cause=(qd['cause'] if qd else None),
                   q_killer_team=(None if not qd or qd.get('killer_team') is None else ('self' if qd.get('killer_team') == t else 'enemy')),
                   q_mutual=bool(qd and qd.get('mutual')), q_maxlen=qmax[t], **q[t])
        out.append(row)
    return out


def work(args):
    try:
        return side_rows(*args)
    except Exception as e:
        return dict(error=f'{type(e).__name__}: {e}', game=args[1])


def done_games():
    if not OUT.exists():
        return set()
    import duckdb
    fs = list(OUT.glob('part-*.parquet'))
    return set(duckdb.sql(f"select distinct game from read_parquet({[str(f) for f in fs]}, union_by_name=true)").df().game) if fs else set()


def flush(rows):
    if not rows:
        return
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%dT%H%M%S') + f'-{os.getpid()}'
    tmp = OUT / f'.part-{stamp}.tmp'
    pd.DataFrame(rows).to_parquet(tmp, index=False)
    tmp.rename(OUT / f'part-{stamp}.parquet')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--era', default='post')
    ap.add_argument('--time', type=float, default=140)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--flush', type=int, default=150)
    ap.add_argument('--all', action='store_true', help='include games outside the store scope (top-50 or us)')
    a = ap.parse_args()
    t0 = time.time()
    games = pd.read_parquet(ROOT / 'build/s1/corpus/games.parquet')
    teams = pd.read_parquet(ROOT / 'build/s1/corpus/teams.parquet')
    g = games[(games.era == a.era) & (games.in_scope | a.all)]
    done = done_games()
    g = g[~g.game.isin(done)].sort_values('started_at', ascending=False)
    cr = dict(zip(teams.team, teams.crank))
    pri = lambda r: min(0 if '7' in (r.team_a, r.team_b) else (cr.get(r.team_a) or 999), cr.get(r.team_b) or 999)
    # us first; then round-robin over (map, best rank tier) newest first so a partial table stays balanced
    g = g.assign(p=[pri(r) for r in g.itertuples()])
    g['tier'] = pd.cut(g.p, [-1, 0, 10, 30, 50, 10**6], labels=False)
    g['k'] = g.groupby(['tier', 'map']).cumcount()
    g = g.sort_values(['k', 'tier'])
    g = pd.concat([g[g.tier == 0], g[g.tier != 0]])
    print(f'done {len(done)} queue {len(g)}', flush=True)
    import multiprocessing as mp
    tasks = [(CORPUS / 'replays' / f'{r.game}.replay', r.game, dict(team_a=r.team_a, team_b=r.team_b, ranked=r.ranked,
              started_at=r.started_at, result_a=r.result_a)) for r in g.itertuples() if (CORPUS / 'replays' / f'{r.game}.replay').exists()]
    rows, n, nerr = [], 0, 0
    with mp.get_context('fork').Pool(a.jobs, maxtasksperchild=100) as pool:
        it = iter(tasks); pend = collections.deque()
        for _ in range(a.jobs * 3):
            x = next(it, None)
            if x is None: break
            pend.append(pool.apply_async(work, (x,)))
        while pend:
            res = pend.popleft().get()
            if isinstance(res, dict):
                nerr += 1
                with open(OUT.parent / 'lean-errors.jsonl', 'a') as f:
                    f.write(json.dumps(res) + '\n')
            else:
                rows += res; n += 1
            if len(rows) >= 2 * a.flush:
                flush(rows); rows = []
            if time.time() - t0 < a.time:
                x = next(it, None)
                if x is not None:
                    pend.append(pool.apply_async(work, (x,)))
    flush(rows)
    print(f'processed {n} ok, {nerr} errors in {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
