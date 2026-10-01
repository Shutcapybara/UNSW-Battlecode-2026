"""s1 query CLI over the s1 store (DuckDB on parquet). Run from the repo root.

  python3 tools/s1/q.py cols series                      # list columns of a view
  python3 tools/s1/q.py sql "select cohort, median(\"pearls@100\") from sides group by 1"
  python3 tools/s1/q.py curve units --rmax 150 [--norm] [--delta] [--by cohort|top10|team|run] [--maps pooled|all|Default,Devil]
  python3 tools/s1/q.py gap [--stats a,b] [--at 25,50,100,150]  # top-10 minus us, per stat x checkpoint, ranked
  python3 tools/s1/q.py norms                            # rebuild field medians (auto when the store grew)
  --db corpus|local picks the store behind the unprefixed views (sides, series, deaths, transits, splits);
  c_* / l_* prefixed views always exist when the store does. --out FILE.png writes a plot; --csv FILE writes the table.

Views: games, teams (corpus); sides (feature-lab row + s1 extras + elo, gap, cohort, crank, name, opp_*);
series (every round 0-150, every 5 to 500, terminal state carried forward, ended flag; c_* = cumulative events);
series_n (every numeric column divided by the field median on the same map and round); series_z (the same as a
field z-score: (x - field mean) / field SD, same map and round; robust for low counts); series_d (rounds %5 == 0,
d5_<col> = change over the previous 5 rounds); sides_n / sides_z (per-map field-median ratio / z-score); deaths, transits, splits.
The field = every corpus side-game in the store. Local stores are normalised against the corpus field.
"""
import argparse, os, re, sys, time
from pathlib import Path

ROOT = Path.cwd()
PY = ROOT / 'build' / 's1-pylib'
if sys.platform.startswith('linux') and PY.exists():
    sys.path.append(str(PY))
import duckdb
import pandas as pd

S1 = ROOT / 'build' / 's1'
TABLES = ('sides', 'series', 'deaths', 'transits', 'splits')
KEYS = {'game', 'side', 'round', 'map', 'team', 'opp', 'source', 'run', 'ended', 'id', 'R', 'rounds', 'cells'}
COHORTS = ['top10', 'r11_30', 'r31_50', 'us']
NORM_GAMES = int(os.environ.get('S1_NORM_GAMES', '1500'))
# S1_ERA=pre|post restricts the corpus views and the field norms to one rules era (games.era; unswbc 1.2.3 switch-over
# 2026-10-01 06:00Z); norms are cached per era. Unset = both eras pooled (the pre-1-Oct behaviour)
ERA = os.environ.get('S1_ERA', '')   # field sample per map for the medians / means / SDs
# derived per side-round columns (cumulative ratios up to the round); added to series, normalised like the rest
DERIVED_LIST = [
    ('pearls_per_dt', 'c_eats / nullif(c_dragon_turns, 0)'),
    ('bed_pearls_per_dt', 'c_eats_bed / nullif(c_dragon_turns, 0)'),
    ('corpse_pearl_share', '(c_eats - c_eats_bed) / nullif(c_eats, 0)'),
    ('steps_per_pearl', 'c_steps / nullif(c_eats, 0)'),
    ('bed_capture', 'c_eats_bed / nullif(c_bed_spawns, 0)'),
    ('births_per_dt', 'c_splits / nullif(c_dragon_turns, 0)'),
    ('deaths_per1k', '1000 * c_deaths / nullif(c_dragon_turns, 0)'),
    ('own_goals_per1k', '1000 * c_own_goals / nullif(c_dragon_turns, 0)'),
    ('own_goal_share', 'c_own_goals / nullif(c_deaths, 0)'),
    ('transits_per_dt', 'c_transits / nullif(c_dragon_turns, 0)'),
    ('transit_died3_share', 'c_transit_died3 / nullif(c_transits, 0)'),
    ('transit_blind_share', 'c_transit_blind / nullif(c_transits, 0)'),
    ('transit_double_share', 'c_transit_double / nullif(c_transits, 0)'),
    ('rays_per_dt', 'c_rays / nullif(c_dragon_turns, 0)'),
    ('sonar_recv_per_dt', 'c_sonar_recv / nullif(c_dragon_turns, 0)'),
    ('idle_share', 'c_idle / nullif(c_dragon_turns, 0)'),
    ('turnaround_share', 'c_turnaround / nullif(c_moves, 0)'),
    ('units_share', 'units / nullif(units + opp_units, 0)'),
    ('total_share', 'total / nullif(total + opp_total, 0)'),
    ('pearls_share', 'c_eats / nullif(c_eats + opp_c_eats, 0)'),
    ('material_gap_rel', '(total - opp_total) / nullif(greatest(total, opp_total), 0)'),
]


def derived_sql(con, view):
    """derived columns; a cumulative event column absent from every part means zero events (substituted by 0)"""
    have = set(con.execute(f'describe {view}').df().column_name)
    out = []
    for n, e in DERIVED_LIST:
        e2 = re.sub(r'\b(c_[a-z0-9_]+|opp_[a-z0-9_]+)\b', lambda m: m.group(1) if m.group(1) in have else '0', e)
        out.append(f'{e2} as "{n}"')
    return ', '.join(out)
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_rows', 400)


def _glob(store, t):
    return str(S1 / store / t / 'part-*.parquet')


def _has(store, t):
    return any((S1 / store / t).glob('part-*.parquet')) if (S1 / store / t).exists() else False


def numeric_cols(con, view, exclude=KEYS):
    d = con.execute(f'describe {view}').df()
    return [c for c, t in zip(d.column_name, d.column_type) if t in ('DOUBLE', 'BIGINT', 'INTEGER', 'FLOAT') and c not in exclude]


def q(c):
    return '"' + c.replace('"', '""') + '"'


def _int(x):
    try:
        return int(x)
    except ValueError:
        return 0


def ensure_norms(con, force=False):
    """per map x round field medians of every numeric series column, and per map medians of every sides column"""
    parts = sorted(p.name for p in (S1 / 'corpus' / 'sides').glob('part-*.parquet'))
    sfx = f'_{ERA}' if ERA else ''
    stamp = S1 / 'corpus' / f'norms{sfx}.stamp'
    fs, fd = S1 / 'corpus' / f'norm_series{sfx}.parquet', S1 / 'corpus' / f'norm_sides{sfx}.parquet'
    key = str(len(parts))
    # rebuilt when forced (q.py norms) or when the store has grown by more than 50 % since the last build
    if not force and fs.exists() and fd.exists() and stamp.exists() and (os.environ.get('S1_FREEZE') or len(parts) <= 1.5 * _int(stamp.read_text())):
        return
    t0 = time.time()
    # exact medians / means / SDs over a fixed hash sample of up to NORM_GAMES games per map (both sides), one map and a
    # batch of columns at a time; per-map results are cached so an interrupted rebuild resumes
    maps = [r[0] for r in con.execute("select distinct map from c_sides").fetchall()]
    tmp = S1 / 'corpus' / 'norms_parts'
    tmp.mkdir(exist_ok=True)
    ck = tmp / f'current{sfx}.key'          # an interrupted rebuild keeps its key, so the cached maps stay valid
    if ck.exists():
        key = ck.read_text()
    else:
        ck.write_text(key)
    budget = float(os.environ.get('S1_NORM_BUDGET', '1e9'))
    for view, keys, out in (('c_series_e', ['map', 'round'], fs), ('c_sides_e', ['map'], fd)):
        cols = numeric_cols(con, view)
        frames = []
        for m in maps:
            pf = tmp / f'{view}-{m.replace(" ", "_")}-{key}{sfx}.parquet'
            if pf.exists():
                frames.append(pd.read_parquet(pf))
                continue
            if time.time() - t0 > budget:
                raise SystemExit(f'[norms: budget reached at {view} {m}; re-run to continue]')
            sample = (f"game in (select game from c_sides where map = '{m}' group by game "
                      f"order by hash(game) limit {NORM_GAMES})")
            parts_m = []
            for i in range(0, len(cols), 16):
                aggs = ', '.join(f'median({q(c)}) as {q(c)}, avg({q(c)}) as {q("mu:" + c)}, stddev_samp({q(c)}) as {q("sd:" + c)}'
                                 for c in cols[i:i + 16])
                parts_m.append(con.execute(f"select {', '.join(keys)}, count(*) as n_field, {aggs} from {view} "
                                           f"where map = ? and {sample} group by all order by all", [m]).df().set_index(keys))
            d = parts_m[0]
            for x in parts_m[1:]:
                d = d.join(x.drop(columns='n_field'))
            d = d.reset_index()
            d.to_parquet(pf, index=False)
            frames.append(d)
        pd.concat(frames).to_parquet(out, index=False)
    ck.rename(tmp / f'done-{key}{sfx}.key')
    stamp.write_text(key)
    print(f'[norms rebuilt in {time.time() - t0:.0f}s]', file=sys.stderr)


def connect(db='corpus', norms=True):
    con = duckdb.connect()
    con.execute("set threads to 4")
    (S1 / 'tmp').mkdir(parents=True, exist_ok=True)
    con.execute(f"set memory_limit = '{os.environ.get('S1_MEM', '1500MB')}'")
    # spill directory: the Cowork VM cannot delete inside the connected folder, so it spills to its own /tmp
    tmpdir = '/tmp/s1-duckdb' if sys.platform.startswith('linux') and str(ROOT).startswith('/sessions') else str(S1 / 'tmp')
    con.execute(f"set temp_directory = '{tmpdir}'")
    con.execute("set preserve_insertion_order = false")
    have = {}
    for store, pre in (('corpus', 'c_'), ('local', 'l_')):
        have[store] = _has(store, 'sides')
        if not have[store]:
            continue
        for t in TABLES:
            if _has(store, t):
                con.execute(f"create view {pre}{t}_all as select * from read_parquet('{_glob(store, t)}', union_by_name=true, filename=true)")
        # a game decoded twice (two hosts) keeps the rows of its first committed part
        con.execute(f"create view {pre}canon as select game, min(filename) as part from {pre}sides_all group by game")
        for t in TABLES:
            if _has(store, t):
                pf = "replace(filename, '/{t}/', '/sides/')".format(t=t)
                con.execute(f"create view {pre}{t}_raw as select * exclude (filename) from {pre}{t}_all x "
                            f"where exists (select 1 from {pre}canon c where c.game = x.game and c.part = {pf})")
    if have['corpus']:
        con.execute(f"create view games as select * from '{S1 / 'corpus' / 'games.parquet'}'")
        con.execute(f"create view teams as select * from '{S1 / 'corpus' / 'teams.parquet'}'")
        ew = f"where g.era = '{ERA}'" if ERA else ''
        con.execute(f"""create view c_sides as select s.*, g.ranked, g.autoscrim, g.started_at, g.series_id, g.era,
            case when s.side = 'A' then g.elo_a else g.elo_b end as elo, case when s.side = 'A' then g.elo_b else g.elo_a end as opp_elo,
            case when s.side = 'A' then g.elo_a - g.elo_b else g.elo_b - g.elo_a end as gap,
            coalesce(t.cohort, 'other') as cohort, t.crank, t.name, coalesce(o.cohort, 'other') as opp_cohort, o.crank as opp_crank, o.name as opp_name
            from c_sides_raw s left join games g on g.game = s.game left join teams t on t.team = s.team left join teams o on o.team = s.opp {ew}""")
    if have['local']:
        con.execute("""create view l_sides as select s.*, s.team as name, 'local' as cohort, cast(null as double) as crank, 'local' as era,
            s.opp as opp_name, 'local' as opp_cohort from l_sides_raw s""")
    for store, pre in (('corpus', 'c_'), ('local', 'l_')):
        if not have[store]:
            continue
        sa = 'started_at' if store == 'corpus' else 'cast(null as timestamptz) as started_at'
        con.execute(f"""create view {pre}key as select game, side, cohort, crank, name, won, result, reason, map_class, opp_cohort, opp_name, run,
                        {sa}, era from {pre}sides""")
        # a missing cumulative event value means the game never had that event: zero, not unknown
        cz = [c for c in con.execute(f'describe {pre}series_raw').df().column_name if c.startswith(('c_', 'opp_c_'))]
        rep = ', '.join(f'coalesce({q(c)}, 0) as {q(c)}' for c in cz)
        con.execute(f"create view {pre}series_z0 as select * replace ({rep}) from {pre}series_raw")
        con.execute(f"create view {pre}series_b as select *, {derived_sql(con, pre + 'series_z0')} from {pre}series_z0")
        con.execute(f"create view {pre}series as select s.*, k.* exclude (game, side) from {pre}series_b s join {pre}key k using (game, side)")
        if store == 'corpus':   # the norms read this (era-scoped through c_key)
            con.execute("create view c_series_e as select s.* from c_series_b s semi join c_key k using (game, side)")
        for t in ('deaths', 'transits', 'splits'):
            if _has(store, t):
                con.execute(f"create view {pre}{t} as select x.*, k.* exclude (game, side) from {pre}{t}_raw x join {pre}key k using (game, side)")
    if have['corpus'] and norms:
        con.execute("create view c_sides_e as select s.* from c_sides_raw s semi join c_key k using (game, side)")
        ensure_norms(con)
        sfx = f'_{ERA}' if ERA else ''
        fs, fd = S1 / 'corpus' / f'norm_series{sfx}.parquet', S1 / 'corpus' / f'norm_sides{sfx}.parquet'
        con.execute(f"create view norm_series as select * from '{fs}'")
        con.execute(f"create view norm_sides as select * from '{fd}'")
        ncols = set(numeric_cols(con, 'norm_series'))
        zcols = {c[3:] for c in ncols if c.startswith('mu:')}
        for pre in ('c_', 'l_'):
            if not con.execute(f"select count(*) from information_schema.tables where table_name = '{pre}series'").fetchone()[0]:
                continue
            cols = [c for c in numeric_cols(con, f'{pre}series') if c in ncols and c != 'n_field' and ':' not in c]
            sel = ', '.join(f's.{q(c)} / nullif(n.{q(c)}, 0) as {q(c)}' for c in cols)
            con.execute(f"create view {pre}series_n as select s.game, s.side, s.round, s.map, s.team, s.ended, s.cohort, s.crank, s.name, s.won, "
                        f"s.run, s.started_at, n.n_field, {sel} from {pre}series s left join norm_series n using (map, round)")
            zc = [c for c in numeric_cols(con, f'{pre}series') if c in zcols]
            sel = ', '.join(f'(s.{q(c)} - n.{q("mu:" + c)}) / nullif(n.{q("sd:" + c)}, 0) as {q(c)}' for c in zc)
            if zc:
                con.execute(f"create view {pre}series_z as select s.game, s.side, s.round, s.map, s.team, s.ended, s.cohort, s.crank, s.name, "
                            f"s.won, s.run, s.started_at, n.n_field, {sel} from {pre}series s left join norm_series n using (map, round)")
            scols = [c for c in numeric_cols(con, f'{pre}sides') if c in set(numeric_cols(con, 'norm_sides')) and c != 'n_field']
            zs = [c for c in scols if 'mu:' + c in set(numeric_cols(con, 'norm_sides'))]
            if zs:
                sel = ', '.join(f'(s.{q(c)} - n.{q("mu:" + c)}) / nullif(n.{q("sd:" + c)}, 0) as {q(c)}' for c in zs)
                con.execute(f"create view {pre}sides_z as select s.game, s.side, s.map, s.team, s.cohort, s.crank, s.name, s.won, s.run, "
                            f"n.n_field, {sel} from {pre}sides s left join norm_sides n using (map)")
            sel = ', '.join(f's.{q(c)} / nullif(n.{q(c)}, 0) as {q(c)}' for c in scols)
            con.execute(f"create view {pre}sides_n as select s.game, s.side, s.map, s.team, s.cohort, s.crank, s.name, s.won, s.run, "
                        f"n.n_field, {sel} from {pre}sides s left join norm_sides n using (map)")
    for pre in ('c_', 'l_'):
        if con.execute(f"select count(*) from information_schema.tables where table_name = '{pre}series'").fetchone()[0]:
            cols = numeric_cols(con, f'{pre}series')
            sel = ', '.join(f'{q(c)} - lag({q(c)}) over w as {q("d5_" + c)}' for c in cols)
            con.execute(f"create view {pre}series_d as select *, {sel} from {pre}series where round % 5 = 0 "
                        f"window w as (partition by game, side order by round)")
    pre = 'c_' if db == 'corpus' else 'l_'
    for v in ('sides', 'series', 'series_n', 'series_z', 'series_d', 'sides_n', 'sides_z', 'deaths', 'transits', 'splits'):
        if con.execute(f"select count(*) from information_schema.tables where table_name = '{pre}{v}'").fetchone()[0]:
            con.execute(f"create view {v} as select * from {pre}{v}")
    return con


# ------------------------------------------------------------------ curves
def group_expr(by):
    if by == 'cohort':
        return "case when cohort in ('top10','r11_30','r31_50','us') then cohort end"
    if by == 'top10':
        return "case when cohort = 'top10' then name when cohort = 'us' then 'us' end"
    if by in ('team', 'name'):
        return 'name'
    if by == 'run':
        return 'run'
    return by


def curve(con, stat, view, by='cohort', maps='pooled', rmin=0, rmax=150, agg='median', where='', stride=1):
    g = group_expr(by)
    w = f'and ({where})' if where else ''
    aggf = {'median': 'median', 'mean': 'avg', 'p25': 'quantile_cont({}, 0.25)', 'p75': 'quantile_cont({}, 0.75)'}[agg]
    val = aggf.format(q(stat)) if '{}' in aggf else f'{aggf}({q(stat)})'
    mapcol = "'pooled'" if maps == 'pooled' else 'map'
    mw = ''
    if maps not in ('pooled', 'all'):
        mw = 'and map in (' + ','.join(f"'{m}'" for m in maps.split(',')) + ')'
    sql = f"""select {mapcol} as map, {g} as grp, round, {val} as v, count(*) as n
              from {view} where round between {rmin} and {rmax} and round % {stride} = 0 and {g} is not null {w} {mw}
              group by all order by map, grp, round"""
    return con.execute(sql).df()


def plot_curves(df, title, out, ylabel):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    maps = list(dict.fromkeys(df['map']))
    n = len(maps)
    cols = min(n, 4)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 3.0 * rows), squeeze=False, sharex=True)
    order = [g for g in ['top10', 'r11_30', 'r31_50', 'us'] if g in set(df.grp)] + sorted(set(df.grp) - set(COHORTS) - {'us'}) + (['us'] if 'us' in set(df.grp) and 'us' not in COHORTS else [])
    order = list(dict.fromkeys(order))
    style = {'top10': ('#1f5fa8', '-'), 'r11_30': ('#4f9bd9', '-'), 'r31_50': ('#9cc3e6', '-'), 'us': ('#d1495b', '-')}
    for k, m in enumerate(maps):
        ax = axes[k // cols][k % cols]
        d = df[df.map == m]
        for gi, gname in enumerate(order):
            x = d[d.grp == gname]
            if x.empty:
                continue
            c, ls = style.get(gname, (None, '-'))
            ax.plot(x['round'], x['v'], ls, color=c, lw=2.2 if gname in ('us', 'top10') else 1.2, label=f'{gname}')
        ax.set_title(m, fontsize=9)
        ax.grid(alpha=0.3)
        if ylabel and 'norm' in ylabel:
            ax.axhline(1.0, color='grey', lw=0.8, ls=':')
    for k in range(n, rows * cols):
        axes[k // cols][k % cols].axis('off')
    axes[0][0].legend(fontsize=7, loc='best')
    fig.suptitle(title, fontsize=11)
    fig.supxlabel('round', fontsize=9)
    fig.supylabel(ylabel, fontsize=9)
    fig.tight_layout()
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110)
    plt.close(fig)


def cmd_curve(con, a):
    view = 'series_n' if a.norm else 'series_d' if a.delta else 'series'
    stat = ('d5_' + a.stat) if a.delta else a.stat
    stride = 5 if a.delta else a.stride
    df = curve(con, stat, view, a.by, a.maps, a.rmin, a.rmax, a.agg, a.where, stride)
    if a.maps == 'pooled' and not a.norm:
        print('# note: pooled raw curves mix maps; use --norm for map-free pooling', file=sys.stderr)
    cps = [c for c in (10, 25, 50, 75, 100, 150, 250, 400, 500) if a.rmin <= c <= a.rmax]
    t = df[df['round'].isin(cps)].pivot_table(index=['map', 'grp'], columns='round', values='v')
    n = df.groupby(['map', 'grp'])['n'].max().rename('n')
    print(t.join(n).round(3).to_string())
    if a.out:
        label = f"{a.agg} {stat}" + (' (/ field median, same map & round)' if a.norm else '')
        plot_curves(df, f'{stat} by {a.by}' + (' — normalised' if a.norm else '') + (' — change per 5 rounds' if a.delta else ''), a.out, label + (' norm' if a.norm else ''))
        print('plot:', a.out)
    if a.csv:
        df.to_csv(a.csv, index=False)


GAP_STATS = ['units', 'total', 'longest', 'c_eats', 'c_eats_bed', 'c_splits', 'c_deaths', 'c_own_goals', 'seen_share',
             'territory', 'bed_territory', 'beds_seen_share', 'beds_reached_share', 'disp_per_turn', 'disp_max', 'swarm_rg',
             'nn_dist_mean', 'clustered_share', 'c_transits', 'c_transit_died3', 'c_rays', 'c_sonar_recv', 'c_idle',
             'reach_le8_share', 'contact_share', 'enemy_head_view_share', 'kelp_adj_mean', 'density_ratio', 'top1_share']


def cmd_gap(con, a):
    stats = a.stats.split(',') if a.stats else GAP_STATS
    cps = [int(x) for x in a.at.split(',')]
    have = set(numeric_cols(con, 'series_n'))
    rows = []
    for s in stats:
        if s not in have:
            continue
        df = con.execute(f"""select round, cohort, median({q(s)}) as n_med from series_n
                             where round in ({','.join(map(str, cps))}) and cohort in ('top10','us') group by all""").df()
        raw = con.execute(f"""select round, cohort, median({q(s)}) as r_med, quantile_cont({q(s)}, 0.75) - quantile_cont({q(s)}, 0.25) as iqr
                              from series where round in ({','.join(map(str, cps))}) and cohort in ('top10','us') group by all""").df()
        for c in cps:
            x = df[df['round'] == c].set_index('cohort')['n_med']
            y = raw[raw['round'] == c].set_index('cohort')
            if 'top10' in x and 'us' in x:
                rows.append(dict(stat=s, round=c, top10_norm=x['top10'], us_norm=x['us'], gap_norm=x['top10'] - x['us'],
                                 top10_raw=y['r_med'].get('top10'), us_raw=y['r_med'].get('us')))
    out = pd.DataFrame(rows)
    out['abs_gap'] = out.gap_norm.abs()
    out = out.sort_values('abs_gap', ascending=False)
    print(out.drop(columns='abs_gap').round(3).to_string(index=False))
    if a.csv:
        out.to_csv(a.csv, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['sql', 'cols', 'curve', 'gap', 'norms', 'views'])
    ap.add_argument('arg', nargs='?')
    ap.add_argument('--db', default='corpus', choices=['corpus', 'local'])
    ap.add_argument('--norm', action='store_true')
    ap.add_argument('--delta', action='store_true')
    ap.add_argument('--by', default='cohort')
    ap.add_argument('--maps', default='all')
    ap.add_argument('--rmin', type=int, default=0)
    ap.add_argument('--rmax', type=int, default=150)
    ap.add_argument('--stride', type=int, default=1)
    ap.add_argument('--agg', default='median')
    ap.add_argument('--where', default='')
    ap.add_argument('--stats', default='')
    ap.add_argument('--at', default='25,50,100,150')
    ap.add_argument('--out', default='')
    ap.add_argument('--csv', default='')
    ap.add_argument('--limit', type=int, default=200)
    a = ap.parse_args()
    con = connect(a.db)
    if a.cmd == 'norms':
        ensure_norms(con, force=True)
    elif a.cmd == 'views':
        print(con.execute("select table_name from information_schema.tables order by 1").df().to_string(index=False))
    elif a.cmd == 'cols':
        print(con.execute(f'describe {a.arg}').df()[['column_name', 'column_type']].to_string(index=False))
    elif a.cmd == 'sql':
        df = con.execute(a.arg).df()
        print(df.head(a.limit).to_string(index=False))
        if a.csv:
            df.to_csv(a.csv, index=False)
    elif a.cmd == 'curve':
        a.stat = a.arg
        cmd_curve(con, a)
    elif a.cmd == 'gap':
        cmd_gap(con, a)


if __name__ == '__main__':
    main()
