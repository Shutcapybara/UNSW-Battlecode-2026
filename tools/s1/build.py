"""s1 store builder: replays -> parquet tables for DuckDB (tools/s1/q.py).

  python3 tools/s1/build.py games                         # corpus games + teams tables from index + ladder (seconds)
  python3 tools/s1/build.py corpus --jobs 4 --time 170     # decode the next batch of corpus games (incremental, resumable)
  python3 tools/s1/build.py corpus --era post              # only games of one rules era (games.era, ERA_SWITCH below)
  python3 tools/s1/build.py local --glob 'build/ra/runs/*/*/replays/*.replay' --jobs 4
  python3 tools/s1/build.py status

Stores: build/s1/corpus/ and build/s1/local/ with sides/ series/ deaths/ transits/ splits/ as part-*.parquet (append-only;
one part per batch) plus games.parquet, teams.parquet (corpus). Corpus scope: every game with a current top-50 side
(non-dev ladder order, latest snapshot) or team 7 (us). Order: balanced round-robin over (team, map), newest first, us first.
Run from the repo root. Never commit build/.
"""
import argparse, bisect, collections, glob, hashlib, json, os, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
for p in (ROOT / 'build' / 's1-pylib',):   # Linux (Cowork VM) only: packages installed with pip --target
    if sys.platform.startswith('linux') and p.exists() and str(p) not in sys.path:
        sys.path.append(str(p))
import numpy as np
import pandas as pd

CORPUS = ROOT / 'public_replays' / 'corpus'
OUT = ROOT / 'build' / 's1'
US = 7
# unswbc 1.2.3 rules on the live server (sprint ceil(L/4) free steps; tiebreak queen -> longest -> total). Last old-rule
# game finished 2026-10-01 05:57:53Z, first new-rule game 09:26:58Z, none in between (tools/antioch/era.py, sprint pricing)
ERA_SWITCH = '2026-10-01T06:00:00+00:00'
TABLES = ('sides', 'series', 'deaths', 'transits', 'splits')
# event columns always present in series (cumulated as c_<name>), so every part has the same schema
XEV = ('idle', 'turnaround', 'steps', 'transits', 'transit_blind', 'transit_double', 'transit_contested', 'transit_died3',
       'transit_died_same', 'sonar_recv', 'sonar_recv_ally', 'sonar_recv_enemy', 'sonar_recv_self', 'own_goals',
       'deaths_post_transit', 'deaths_crowd', 'deaths_enclosed', 'deaths_newborn', 'deaths_near_portal')
FEV = ('eats', 'eats_bed', 'eats_ally_corpse', 'eats_enemy_corpse', 'eats_unknown', 'bed_spawns', 'splits', 'moves', 'sprints',
       'sprint_cost', 'suicides', 'no_action', 'tle', 'deaths', 'death_wall', 'death_self', 'death_ally_body', 'death_enemy_body',
       'death_h2h_enemy', 'death_h2h_ally', 'death_suicide', 'death_invalid', 'length_lost', 'kills', 'kill_length', 'rays',
       'rays_refracted', 'rays_N', 'rays_E', 'rays_S', 'rays_W', 'ray_kelp', 'ray_ally', 'ray_ally_head', 'ray_enemy',
       'ray_enemy_head', 'ray_empty', 'dragon_turns')
STR_COLS = {'game', 'map', 'side', 'team', 'opp', 'bot', 'opponent', 'cls', 'cause', 'map_class', 'map_hash', 'reason',
            'result', 'entry', 'exit', 'pair', 'beds_source', 'death_cause', 'killer_team', 'source', 'run', 'cohort',
            'opp_cohort', 'toolkit', 'seed', 'file', 'decoded_winner', 'path', 'error'}


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


# ------------------------------------------------------------------ games / teams (corpus)
def load_ladders():
    snaps = []
    for f in sorted((CORPUS / 'ladder').glob('*.json')):
        t = datetime.strptime(f.stem, '%Y%m%dT%H%M%SZ').timestamp()
        snaps.append((t, {x['id']: x for x in json.loads(f.read_text())}, f.stem))
    return snaps


def cohort_of(rank):
    if rank is None:
        return 'other'
    return 'top10' if rank <= 10 else 'r11_30' if rank <= 30 else 'r31_50' if rank <= 50 else 'other'


def build_games():
    snaps = load_ladders()
    times = [s[0] for s in snaps]
    latest = snaps[-1][1]
    order = sorted((x for x in latest.values() if not x.get('dev')), key=lambda x: x['rank'])
    crank = {x['id']: k + 1 for k, x in enumerate(order)}
    teams = pd.DataFrame([dict(team=str(i), name=x['name'], ladder_rank=x['rank'], elo_now=x['elo'], dev=bool(x.get('dev')),
                               crank=crank.get(i), cohort='us' if i == US else ('dev' if x.get('dev') else cohort_of(crank.get(i))))
                          for i, x in latest.items()])
    rows = []
    for line in open(CORPUS / 'index.jsonl'):
        g = json.loads(line)
        if not g.get('started_at'):
            continue
        t = ts(g['started_at'])
        k = max(0, bisect.bisect_right(times, t) - 1)
        snap_t, snap, _ = snaps[k]
        ra, rb = snap.get(g['team_a'], {}), snap.get(g['team_b'], {})
        w = g.get('winner')
        rows.append(dict(game=str(g['game_id']), game_id=g['game_id'], team_a=str(g['team_a']), team_b=str(g['team_b']),
                         map=g['map_name'], ranked=bool(g['ranked']), autoscrim=bool(g.get('autoscrim_window')),
                         started_at=pd.Timestamp(g['started_at']), series_id=g.get('series_id'), seed=g.get('seed'),
                         map_hash=g.get('map_hash', '')[:12],
                         elo_a=ra.get('elo'), elo_b=rb.get('elo'), rank_a=ra.get('rank'), rank_b=rb.get('rank'),
                         snap_lag_min=(t - snap_t) / 60, snap_before=t >= snap_t,
                         result_a=1.0 if w == 'a' else 0.0 if w == 'b' else 0.5, era='post' if t >= ts(ERA_SWITCH) else 'pre',
                         in_scope=(g['team_a'] in crank and crank[g['team_a']] <= 50) or (g['team_b'] in crank and crank[g['team_b']] <= 50)
                         or US in (g['team_a'], g['team_b'])))
    games = pd.DataFrame(rows).drop_duplicates('game')
    games['elo_gap'] = games.elo_a - games.elo_b
    (OUT / 'corpus').mkdir(parents=True, exist_ok=True)
    games.to_parquet(OUT / 'corpus' / 'games.parquet', index=False)
    teams.to_parquet(OUT / 'corpus' / 'teams.parquet', index=False)
    (OUT / 'corpus' / 'cohort.json').write_text(json.dumps(dict(snapshot=snaps[-1][2], top50=[i for i, _ in sorted(crank.items(), key=lambda kv: kv[1])][:50])))
    print(f'games {len(games)} (in scope {int(games.in_scope.sum())}), teams {len(teams)}, ladder {snaps[-1][2]}, snapshots {len(snaps)}')
    return games, teams


def corpus_queue(games, teams, done):
    """balanced order: round-robin over (team, map) of in-scope teams, newest game first; team 7 first."""
    cr = dict(zip(teams.team, teams.crank))
    scope = set(t for t, c in cr.items() if c is not None and c == c and c <= 50) | {str(US)}
    g = games[games.in_scope & ~games.game.isin(done)].sort_values('started_at', ascending=False)
    lists = collections.defaultdict(list)
    for row in g.itertuples():
        for t in (row.team_a, row.team_b):
            if t in scope:
                lists[(t, row.map)].append(row.game)
    keys = sorted(lists, key=lambda k: (k[0] != str(US), cr.get(k[0]) or 0, k[1]))
    out, seen = [], set()
    # team 7 gets the head of the queue in full
    for k in [k for k in keys if k[0] == str(US)]:
        for x in lists[k]:
            if x not in seen:
                seen.add(x); out.append(x)
    depth = max((len(v) for v in lists.values()), default=0)
    for d in range(depth):
        for k in keys:
            v = lists[k]
            if d < len(v) and v[d] not in seen:
                seen.add(v[d]); out.append(v[d])
    return out


# ------------------------------------------------------------------ one game
def bot_name(path):
    """bot directory name from the replay header path (drops build dirs such as .unswbc-build and trailing slashes)"""
    parts = [p for p in str(path).replace('\\', '/').split('/') if p and not p.startswith('.unswbc') and p not in ('build', 'src')]
    return parts[-1] if parts else str(path)


def process(args):
    path, gid, meta = args
    from tools.analysis.features.frame import decode
    from tools.analysis.features.extract import extract
    from tools.analysis.features.beds import resolve
    from tools.s1 import extras as X
    try:
        g = decode(path)
        out = extract(g)
        beds, _ = resolve(g)
        x = X.run(g, out, beds)
    except Exception as e:
        return dict(error=f'{type(e).__name__}: {e}', game=gid, path=str(path))
    R = x['R']
    side_team = {'A': meta.get('team_a', bot_name(g['botA'])), 'B': meta.get('team_b', bot_name(g['botB']))}
    mapname = 'Prisoners Dilemma 10' if g['map'] == 'Prisoners Dilemma' and g.get('n_initial') == 10 else g['map']
    ctx = dict(game=gid, map=mapname, source=meta.get('source', ''), run=meta.get('run', ''))
    # ---- sides
    sides = []
    for row in out['side_rows']:
        t = row['side']
        r = dict(row)
        r.update(ctx, team=side_team[t], opp=side_team['B' if t == 'A' else 'A'], R=R, decoded_winner=g['winner'])
        r.update(x['sides'][t])
        sides.append(r)
    # ---- series: stored rounds, cumulative events, padded to LAST with the terminal state
    ser = {(s['side'], s['round']): s for s in out['series']}
    samp = {(s['side'], s['round']): s for s in out['samples']}
    ev_keys = set()
    base_state = ('units', 'total', 'longest', 'mean_len', 'top1_share', 'top3_share', 'len_cv', 'len_gini', 'small_share',
                  'big_share', 'seen_share', 'visited_share', 'contact_share', 'density_ratio', 'pearls_on_board')
    for s in out['series']:
        for k in s:
            if k not in base_state and k not in ('game', 'side', 'round', 'leader_change', 'new_seen'):
                ev_keys.add(k)
    series = []
    rounds_all = X.stored_rounds()
    for t in 'AB':
        cum = {k: np.cumsum([ser[(t, r)].get(k, 0.0) for r in range(R + 1)]) for k in sorted(ev_keys)}
        xe = {k: np.cumsum(x['events'][t][k]) if k in x['events'][t] else np.zeros(R + 1) for k in set(XEV) | set(x['events'][t])}
        for k in FEV:
            cum.setdefault(k, np.zeros(R + 1))
        xc = x['cols'][t]
        last_s = None
        for r in rounds_all:
            rr = min(r, R)
            row = dict(game=gid, map=mapname, side=t, team=side_team[t], round=r, ended=int(r > R))
            s = ser[(t, rr)]
            for k in base_state:
                row[k] = s.get(k)
            for k, v in cum.items():
                row['c_' + k] = float(v[rr])
            for k, v in xe.items():
                row['c_' + k] = float(v[rr])
            for k, v in xc.items():
                if rr in v:
                    row[k] = v[rr]
                elif r > R and last_s is not None and k in last_s:
                    row[k] = last_s[k]
            key = (t, rr - rr % 5)
            sm = samp.get((t, rr)) or (samp.get(key) if r % 5 == 0 else None)
            if sm is None and r > R:
                sm = samp.get((t, R))
            if sm:
                for k in ('territory', 'contested', 'bed_territory', 'bed_expected_share', 'access_tau2', 'reach_mean', 'enclosed_share'):
                    row[k] = sm.get(k)
            if r == rr:
                last_s = row
            series.append(row)
    # opponent state on the same row (material gap without a self-join)
    idx = {(r_['side'], r_['round']): r_ for r_ in series}
    for r_ in series:
        o_ = idx[('B' if r_['side'] == 'A' else 'A', r_['round'])]
        for k in ('units', 'total', 'longest', 'c_eats', 'c_splits', 'c_deaths', 'territory', 'seen_share'):
            r_['opp_' + k] = o_.get(k)
    # ---- deaths, transits, splits
    xd = {(d['game'], d['id']): d for d in x['deaths']}
    deaths = []
    for d in out['deaths']:
        r = dict(d)
        r.update(xd.get((d['game'], d['id']), {}))
        r.update(ctx, team=side_team[d['side']])
        r.pop('killer_team', None)
        r['killer_team'] = d.get('killer_team')
        deaths.append(r)
    transits = [dict(x_, **ctx, team=side_team[x_['side']]) for x_ in x['transits']]
    splits = [dict(x_, **ctx, team=side_team[x_['side']]) for x_ in x['splits']]
    for d in deaths:
        d['game'] = gid
    return dict(game=gid, sides=sides, series=series, deaths=deaths, transits=transits, splits=splits)


# ------------------------------------------------------------------ writing
def frame(rows):
    df = pd.DataFrame(rows)
    for c in df.columns:
        if c in STR_COLS:
            df[c] = df[c].map(lambda v: None if v is None or (isinstance(v, float) and v != v) else str(v))
        else:
            df[c] = pd.to_numeric(df[c].map(lambda v: float(v) if isinstance(v, (bool, np.bool_)) else v), errors='coerce').astype('float64')
    return df


def write_parts(store, batch):
    """all tables to temp files first, then rename; the sides part is renamed last and is the commit marker"""
    stamp = time.strftime('%Y%m%dT%H%M%S') + f'-{os.getpid()}'
    tmps = []
    for tname in TABLES:
        rows = [r for b in batch for r in b[tname]]
        if not rows:
            continue
        d = store / tname
        d.mkdir(parents=True, exist_ok=True)
        tmp = d / f'.part-{stamp}.parquet.tmp'
        frame(rows).to_parquet(tmp, index=False)
        tmps.append((tname, tmp, d / f'part-{stamp}.parquet'))
    for tname, tmp, dst in sorted(tmps, key=lambda x: x[0] == 'sides'):
        tmp.rename(dst)


def clean_orphans(store):
    """drop parts whose batch never committed (no sides part with the same stamp) and stale temp files"""
    ok = {f.name for f in (store / 'sides').glob('part-*.parquet')}
    trash = store / '_orphans'     # moved, not deleted (the Cowork VM cannot delete without a prompt)
    old = lambda f: time.time() - f.stat().st_mtime > 1800   # never touch a batch another host may still be writing
    for t in TABLES:
        bad = [f for f in (store / t).glob('.part-*.tmp') if old(f)]
        if t != 'sides':
            bad += [f for f in (store / t).glob('part-*.parquet') if f.name not in ok and old(f)]
        for f in bad:
            trash.mkdir(exist_ok=True)
            f.rename(trash / f'{t}-{f.name}')


def done_games(store, clean=True):
    import pyarrow.parquet as pq
    if clean and (store / 'sides').exists():
        clean_orphans(store)
    done = set()
    for f in (store / 'sides').glob('part-*.parquet'):
        done.update(pq.read_table(f, columns=['game']).column('game').to_pylist())
    errf = store / 'errors.jsonl'
    if errf.exists():
        done.update(json.loads(l)['game'] for l in open(errf))
    return done


def run_batch(store, tasks, jobs, budget, flush_every=200):
    import multiprocessing as mp
    t0 = time.time()
    batch, n_ok, n_err = [], 0, 0
    ctx = mp.get_context('fork' if sys.platform.startswith('linux') else 'spawn')
    with ctx.Pool(jobs, maxtasksperchild=50) as pool:
        it = iter(tasks)
        pending = collections.deque()
        for _ in range(jobs * 2):
            a = next(it, None)
            if a is None:
                break
            pending.append(pool.apply_async(process, (a,)))
        while pending:
            res = pending.popleft().get()
            if 'error' in res:
                n_err += 1
                with open(store / 'errors.jsonl', 'a') as f:
                    f.write(json.dumps(res) + '\n')
            else:
                batch.append(res)
                n_ok += 1
            if len(batch) >= flush_every:
                write_parts(store, batch)
                batch = []
            if time.time() - t0 < budget:
                a = next(it, None)
                if a is not None:
                    pending.append(pool.apply_async(process, (a,)))
    if batch:
        write_parts(store, batch)
    dt = time.time() - t0
    print(f'processed {n_ok} ok, {n_err} errors in {dt:.0f}s ({dt / max(n_ok, 1):.2f}s/game wall)')
    return n_ok


def cmd_corpus(a):
    games, teams = build_games()
    store = OUT / 'corpus'
    done = done_games(store)
    if a.era:
        games = games[games.era == a.era]
    q = corpus_queue(games, teams, done)
    if a.limit:
        q = q[:a.limit]
    print(f'done {len(done)}, queue {len(q)}')
    meta = games.set_index('game')[['team_a', 'team_b']].to_dict('index')
    tasks = ((CORPUS / 'replays' / f'{gid}.replay', gid, dict(meta[gid], source='corpus')) for gid in q
             if (CORPUS / 'replays' / f'{gid}.replay').exists())
    run_batch(store, tasks, a.jobs, a.time)


def cmd_local(a):
    store = OUT / 'local'
    store.mkdir(parents=True, exist_ok=True)
    done = done_games(store)
    paths = sorted(set(p for g in a.glob for p in glob.glob(g, recursive=True)))
    tasks = []
    for p in paths:
        rel = os.path.relpath(p, ROOT)
        run = a.tag or str(Path(rel).parent.parent if Path(rel).parent.name == 'replays' else Path(rel).parent)
        gid = f'{run}/{Path(p).stem}'
        if gid not in done:
            tasks.append((p, gid, dict(source='local', run=run)))
    print(f'local: {len(paths)} replays, {len(tasks)} new')
    run_batch(store, tasks[:a.limit] if a.limit else tasks, a.jobs, a.time)


def cmd_status(a):
    for s in ('corpus', 'local'):
        store = OUT / s
        if store.exists():
            d = done_games(store, clean=False)
            parts = {t: len(list((store / t).glob('part-*.parquet'))) for t in TABLES}
            print(s, 'games done', len(d), 'parts', parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['games', 'corpus', 'local', 'status'])
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 2)))
    ap.add_argument('--time', type=float, default=1e9, help='stop submitting new games after this many seconds')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--glob', action='append', default=[])
    ap.add_argument('--tag', default='')
    ap.add_argument('--era', default='', help="corpus: decode only games of this rules era ('pre' / 'post')")
    a = ap.parse_args()
    dict(games=lambda a: build_games(), corpus=cmd_corpus, local=cmd_local, status=cmd_status)[a.cmd](a)


if __name__ == '__main__':
    main()
