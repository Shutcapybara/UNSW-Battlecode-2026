"""chongqing: light DuckDB connector over the s1 corpus store for the Cowork VM (post-era parts only by default).

  python3 tools/chongqing/qq.py "select cohort, count(*) from sides group by 1"
  python3 tools/chongqing/qq.py --era all "select ..."          # every part (slow over the mount)

Views: games, teams (store), sides / deaths / splits / transits / series (parts written on or after PART_FROM, i.e. the
post-change decodes; joined to games for era/ranked/started_at and to teams for cohort/crank/name, era-filtered).
Cohorts come from the latest ladder snapshot (post-reset ranks since 1 Oct 17:09Z). Run from the repo root.
tools/s1/q.py stays the reference CLI; its view set (series_n/_z, norms) binds too slowly over the mounted store.
"""
import argparse, os, sys, time
from pathlib import Path

ROOT = Path.cwd()
PY = ROOT / 'build' / 's1-pylib'
if sys.platform.startswith('linux') and PY.exists():
    sys.path.append(str(PY))
import duckdb

S1 = ROOT / 'build' / 's1' / 'corpus'
PART_FROM = 'part-202610'      # parts written from 1 Oct (October) carry only post-change games (build.py corpus --era post)
TABLES = ('sides', 'deaths', 'splits', 'transits', 'series')


def connect(era='post', threads=3, mem='1200MB'):
    con = duckdb.connect()
    con.execute(f"set threads to {threads}")
    con.execute(f"set memory_limit = '{mem}'")
    con.execute("set preserve_insertion_order = false")
    con.execute("set temp_directory = '/tmp/chongqing-duckdb'")
    con.execute(f"create view games as select * from '{S1 / 'games.parquet'}'")
    con.execute(f"create view teams as select * from '{S1 / 'teams.parquet'}'")
    glob = 'part-*.parquet' if era == 'all' else f'{PART_FROM}*.parquet'
    ew = '' if era == 'all' else f"where g.era = '{era}'"
    for t in TABLES:
        d = S1 / t
        if not d.exists() or not any(d.glob(glob)):
            continue
        con.execute(f"create view {t}_all as select * from read_parquet('{d / glob}', union_by_name=true, filename=true)")
        if t == 'sides':
            con.execute("create view canon as select game, min(filename) as part from sides_all group by game")
        pf = f"replace(filename, '/{t}/', '/sides/')"
        con.execute(f"create view {t}_raw as select * exclude (filename) from {t}_all x "
                    f"where exists (select 1 from canon c where c.game = x.game and c.part = {pf})")
    con.execute(f"""create view sides as select s.*, g.ranked, g.autoscrim, g.started_at, g.series_id, g.era, g.map_era, g.map_hash,
        case when s.side = 'A' then g.elo_a else g.elo_b end as elo, case when s.side = 'A' then g.elo_b else g.elo_a end as opp_elo,
        coalesce(t.cohort, 'other') as cohort, t.crank, t.name, coalesce(o.cohort, 'other') as opp_cohort, o.crank as opp_crank, o.name as opp_name
        from sides_raw s left join games g on g.game = s.game left join teams t on t.team = s.team left join teams o on o.team = s.opp {ew}""")
    con.execute("create view key as select game, side, cohort, crank, name, won, result, reason, ranked, started_at, era, map_era, opp_cohort, opp_name from sides")
    for t in TABLES[1:]:
        if con.execute(f"select count(*) from information_schema.tables where table_name = '{t}_raw'").fetchone()[0]:
            con.execute(f"create view {t} as select x.*, k.* exclude (game, side) from {t}_raw x join key k using (game, side)")
    return con


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sql')
    ap.add_argument('--era', default='post')
    ap.add_argument('--csv', default='')
    a = ap.parse_args()
    import pandas as pd
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60); pd.set_option('display.max_rows', 400)
    t0 = time.time()
    con = connect(a.era)
    df = con.execute(a.sql).df()
    if a.csv:
        df.to_csv(a.csv, index=False)
    print(df.to_string(index=False))
    print(f'[{len(df)} rows, {time.time() - t0:.1f}s]', file=sys.stderr)


if __name__ == '__main__':
    main()
