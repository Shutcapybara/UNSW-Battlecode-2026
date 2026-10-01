"""Split-stall diagnostic: why do we stop compounding units after round 25?

  python3 tools/s1/splitstall.py run [--per 15] [--jobs 4] [--budget 160]   (resumable; appends build/s1/out/splitstall/*.json)
  python3 tools/s1/splitstall.py report

For every dragon-turn of a chosen side in rounds 20-100: length at the start of the turn, whether the dragon is split-eligible
(length >= 4), what it did (move / split / suicide), whether it ate, and how many free exits its head had (neighbour cells
that are not kelp and not occupied by any body at the start of the turn). Cohorts: team 7 since 29 Sep 06:00 ("us_now") and
the top ten, ranked games only (unranked top-ten games include decoys, see S1-F-fingerprinting).
Decides: policy (eligible but declined) vs foraging (rarely eligible) vs churn (children die before compounding).
"""
import argparse, json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT); sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
OUT = ROOT / 'build' / 's1' / 'out' / 'splitstall'
REPL = ROOT / 'public_replays' / 'corpus' / 'replays'
WINDOWS = [(20, 40), (40, 60), (60, 100)]


def choose(per):
    import duckdb
    con = duckdb.connect()
    con.execute("create view s as select * from read_parquet('build/s1/corpus/sides/*.parquet', union_by_name=true)")
    con.execute("create view g as select * from 'build/s1/corpus/games.parquet'")
    top = [str(t) for t in json.loads((ROOT / 'build' / 's1' / 'corpus' / 'cohort.json').read_text())['top50'] if str(t) != '7'][:10]
    con.execute('create table top10 as select unnest(?::varchar[]) as team', [top])
    rows = con.execute("""
      with x as (select s.game, s.map, s.side, s.team, g.ranked, g.started_at,
                   case when s.team = '7' and g.started_at >= timestamp '2026-09-29 06:00:00' then 'us_now'
                        when s.team in (select team from top10) then 'top10' end as cohort
                 from s join g using (game))
      select cohort, map, game, side, team from (
        select *, row_number() over (partition by cohort, map order by hash(game || side)) k from x
        where cohort = 'us_now' or (cohort = 'top10' and ranked)) where k <= ?""", [per]).fetchall()
    return rows


def dragon_turns(path, side):
    from tools.analysis.features.frame import decode
    g = decode(path)
    nbr, rounds, ev = g['nbr'], g['rounds'], g['events']
    acts = {(a['round'], a['id']): a for a in ev['actions']}
    ate = {}
    for e in ev['eats']:
        ate[(e['round'], e['id'])] = ate.get((e['round'], e['id']), 0) + 1
    born = {s['child']: s['round'] for s in ev['splits']}
    died = {d['id']: d['round'] for d in ev['deaths']}
    out = []
    for r in range(20, min(101, len(rounds))):
        snap = rounds[r]
        occ = set(c for (_, b) in snap.values() for c in b)
        for i, (t, b) in snap.items():
            if t != side or (r, i) not in acts:
                continue
            a = acts[(r, i)]
            L = len(b)
            free = sum(1 for d in range(4) if nbr[b[0]][d] is not None and nbr[b[0]][d] not in occ)
            out.append((r, i, L, a['kind'] or 'none', ate.get((r, i), 0), free,
                        r - born[i] if i in born else -1, (died[i] - r) if i in died else 999))
    return dict(map=g['map'], rows=out)


def cmd_run(a):
    OUT.mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in OUT.glob('*.json')}
    todo = [(c, m, gid, sd, t) for c, m, gid, sd, t in choose(a.per) if f'{gid}_{sd}' not in done and (REPL / f'{gid}.replay').exists()]
    print(f'{len(todo)} side-games to do', file=sys.stderr)
    import multiprocessing as mp
    t0 = time.time()
    with mp.get_context('fork').Pool(a.jobs) as pool:
        res = pool.imap_unordered(_one, todo)
        for k in res:
            if time.time() - t0 > a.budget:
                pool.terminate(); break
    print(f'{len(list(OUT.glob("*.json")))} done', file=sys.stderr)


def _one(x):
    c, m, gid, sd, t = x
    try:
        d = dragon_turns(REPL / f'{gid}.replay', sd)
    except Exception as e:
        d = dict(error=str(e))
    d.update(cohort=c, game=gid, side=sd, team=t)
    p = OUT / f'{gid}_{sd}.json'
    p.with_suffix('.tmp').write_text(json.dumps(d)); os.replace(p.with_suffix('.tmp'), p)
    return gid


def cmd_report(a):
    import pandas as pd, numpy as np
    recs = []
    for p in OUT.glob('*.json'):
        d = json.loads(p.read_text())
        if 'rows' not in d:
            continue
        df = pd.DataFrame(d['rows'], columns=['round', 'id', 'L', 'act', 'ate', 'free', 'age', 'to_death'])
        df['cohort'], df['map'], df['g'] = d['cohort'], d['map'], p.stem
        recs.append(df)
    D = pd.concat(recs)
    D['win'] = pd.cut(D['round'], [19, 39, 59, 100], labels=['r20-39', 'r40-59', 'r60-100'])
    D['elig'] = D.L >= 4
    D['split'] = D.act == 'split'
    D['open2'] = D.free >= 2
    def summ(x):
        e = x[x.elig]
        e2 = e[e.open2]
        kids = x[(x.age >= 0) & (x.age <= 0)]
        return pd.Series(dict(
            side_games=x.g.nunique(), dragons_per_round=len(x) / max(x.g.nunique(), 1) / max(x['round'].nunique(), 1),
            eat_rate=x.ate.mean(), elig_share=x.elig.mean(), L2_share=(x.L <= 2).mean(), L3_share=(x.L == 3).mean(),
            split_rate_elig=e.split.mean(), split_rate_elig_open=e2.split.mean(), declined_elig_per_dragon_round=(x.elig & ~x.split).mean(),
            elig_L_median=e.L.median(), elig_L_ge6=(x.L >= 6).mean(),
            eat_rate_L2=x[x.L <= 2].ate.mean(), eat_rate_L3=x[x.L == 3].ate.mean(), free_mean=x.free.mean(),
            cramped=(x.free <= 1).mean(), suicide_rate=(x.act == 'suicide').mean()))
    T = D.groupby(['cohort', 'win']).apply(summ).round(3)
    print(T.T.to_string())
    # per map (pooled windows r20-59)
    M = D[D['round'] < 60].groupby(['map', 'cohort']).apply(lambda x: pd.Series(dict(
        n=x.g.nunique(), eat=x.ate.mean(), elig=x.elig.mean(), split_e=x[x.elig].split.mean()))).round(3).unstack('cohort')
    print(M.to_string())
    T.to_csv(OUT.parent / 'splitstall_summary.csv'); M.to_csv(OUT.parent / 'splitstall_maps.csv')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['run', 'report'])
    ap.add_argument('--per', type=int, default=15, help='side-games per cohort x map')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--budget', type=int, default=150)
    a = ap.parse_args()
    {'run': cmd_run, 'report': cmd_report}[a.cmd](a)
