"""S1-Q3: the opening, component by component. Run from the repo root.

  python3 tools/s1/q3.py curves [BUDGET_S] [force]   # cached medians per (kind, map, group, round, stat); resumable
  python3 tools/s1/q3.py figs [stat ...]             # one figure per stat -> docs/findings/s1-figs/q3/
  python3 tools/s1/q3.py gap                         # top-10 minus us, per stat x checkpoint, ranked -> build/s1/out/q3/gap.csv
  python3 tools/s1/q3.py sides                       # single-number opening features, lead transitions, seat asymmetry

Kinds: raw (per map), norm (÷ field median on the same map and round; per map and pooled over maps), delta (change over
the previous 5 rounds, per map). Groups: cohorts top10 / r11_30 / r31_50 / us, each top-10 team ('team:<name>'), and
local bots ('local:<bot>', pool runs only; S1_LOCAL=a,b to choose).
"""
import os, sys, time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import numpy as np
import pandas as pd

S1 = ROOT / 'build' / 's1'
OUT = S1 / 'out' / 'q3'
FIG = ROOT / 'docs' / 'findings' / 's1-figs' / 'q3'
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 600)

STATS = {
    'space': ['seen_share', 'territory', 'bed_territory', 'beds_seen_share', 'beds_reached_share'],
    'pearls': ['c_eats', 'c_eats_bed', 'pearls_per_dt', 'bed_pearls_per_dt', 'steps_per_pearl', 'bed_capture', 'corpse_pearl_share'],
    'production': ['c_splits', 'births_per_dt', 'units'],
    'material': ['total', 'longest', 'top1_share', 'mean_len', 'total_share', 'units_share', 'material_gap_rel'],
    'deaths': ['c_deaths', 'deaths_per1k', 'c_own_goals', 'own_goals_per1k', 'own_goal_share', 'c_death_wall', 'c_death_self',
               'c_death_ally_body', 'c_death_h2h_ally', 'c_death_enemy_body', 'c_death_h2h_enemy', 'c_death_suicide',
               'c_deaths_enclosed', 'c_deaths_newborn', 'c_deaths_near_portal', 'c_deaths_crowd', 'c_deaths_post_transit',
               'c_length_lost', 'c_kills'],
    'portals': ['c_transits', 'transits_per_dt', 'transit_died3_share', 'transit_blind_share', 'transit_double_share',
                'c_transit_died3', 'c_transit_blind', 'c_transit_double'],
    'movement': ['disp_per_turn', 'disp_mean', 'disp_max', 'idle_share', 'turnaround_share', 'kelp_adj_mean', 'reach_le8_share',
                 'reach5_mean', 'c_steps'],
    'swarm': ['swarm_rg', 'nn_dist_mean', 'pair_dist_mean', 'clustered_share', 'swarm_density'],
    'contact': ['contact_share', 'enemy_head_view_share', 'enemy_head_dist_mean', 'enemy_head_dist_min'],
    'sonar': ['rays_per_dt', 'sonar_recv_per_dt', 'c_rays', 'c_sonar_recv'],
}
FAMILY = {s: f for f, v in STATS.items() for s in v}
DELTA = ['units', 'total', 'c_eats', 'seen_share', 'territory', 'c_splits', 'c_deaths', 'c_own_goals', 'c_transits',
         'disp_mean', 'swarm_rg', 'beds_reached_share', 'longest']
ROUNDS = sorted(set(list(range(0, 21, 2)) + list(range(20, 151, 5)) + list(range(150, 501, 25))))
LOCAL = os.environ.get('S1_LOCAL', 'renoir-00-base').split(',')
COHORT = "case when cohort in ('top10','r11_30','r31_50','us') then cohort end"
US_SINCE = os.environ.get('S1_US_SINCE', '2026-09-29 06:00:00+00')   # our current submission era (no TLE turns after this)
US_NOW = f"case when cohort = 'us' and started_at >= '{US_SINCE}' then 'us_now' end"
STYLE = {'top10': ('#1f5fa8', 2.4), 'r11_30': ('#5aa0dc', 1.4), 'r31_50': ('#a8cbe8', 1.4), 'us': ('#d1495b', 2.4), 'us_now': ('#f28e2b', 1.8)}


def con():
    from tools.s1.q import connect
    return connect('corpus')


def cache_dir():
    d = OUT / 'cache'
    d.mkdir(parents=True, exist_ok=True)
    return d


def curves(budget=150, force=False):
    t0 = time.time()
    c = con()
    have = set(c.execute('describe series').df().column_name)
    have_n = set(c.execute('describe series_n').df().column_name)
    stats = [s for v in STATS.values() for s in v if s in have]
    maps = [r[0] for r in c.execute("select distinct map from sides order by 1").fetchall()]
    # cache key = the norms build (curves are recomputed when the field medians are rebuilt, or with 'force')
    stamp = (S1 / 'corpus' / 'norms.stamp').read_text()
    has_local = c.execute("select count(*) from information_schema.tables where table_name = 'l_series_n'").fetchone()[0] > 0
    rl = ','.join(map(str, ROUNDS))
    jobs = ([('raw', m) for m in maps] + [('z', 'pooled'), ('norm', 'pooled')] + [('z', m) for m in maps]
            + [('norm', m) for m in maps] + [('delta', m) for m in maps])
    cd = cache_dir()
    n_done = 0
    for kind, m in jobs:
        f = cd / f'{kind}-{m.replace(" ", "_")}.parquet'
        st = cd / (f.name + '.stamp')
        if f.exists() and st.exists() and not force and st.read_text() == stamp:
            continue
        if time.time() - t0 > budget:
            print(f'[curves: budget reached after {n_done} jobs; re-run to continue]')
            return False
        view = slim(c, kind, m, stamp)
        cols = DELTA if kind == 'delta' else [s for s in stats if kind not in ('norm', 'z') or s in have_n]
        cols = [('d5_' + x) if kind == 'delta' else x for x in cols]
        mw = ''
        rw = 'true'
        frames = []
        for i in range(0, len(cols), 12):
            cs = cols[i:i + 12]
            fn = 'avg' if kind in ('z', 'delta') else 'median'   # z-scores and 5-round changes are averaged; levels take the median
            agg = ', '.join(f'{fn}("{x}") as "{x}"' for x in cs)
            for g in (COHORT, US_NOW, "case when cohort = 'top10' then 'team:' || name end"):
                d = c.execute(f"select {g} as grp, round, count(*) as n, {agg} from {view} where {rw} {mw} and {g} is not null group by all").df()
                frames.append(d.melt(id_vars=['grp', 'round', 'n'], var_name='stat', value_name='v'))
            if has_local and kind != 'delta':
                lv = {'raw': 'l_series', 'norm': 'l_series_n', 'z': 'l_series_z'}[kind]
                lcols = set(c.execute(f'describe {lv}').df().column_name)
                cs2 = [x for x in cs if x in lcols]
                if cs2:
                    agg2 = ', '.join(f'{fn}("{x}") as "{x}"' for x in cs2)
                    names = ','.join(f"'{x}'" for x in LOCAL)
                    lmw = '' if m == 'pooled' else f"and map = '{m}'"
                    d = c.execute(f"select 'local:' || name as grp, round, count(*) as n, {agg2} from {lv} where round in ({rl}) {lmw} "
                                  f"and name in ({names}) and run like '%/pool' group by all").df()
                    if len(d):
                        frames.append(d.melt(id_vars=['grp', 'round', 'n'], var_name='stat', value_name='v'))
        out = pd.concat(frames).assign(kind=kind, map=m)
        if kind == 'delta':
            out['stat'] = out['stat'].str[3:]
        out.to_parquet(f, index=False)
        st.write_text(stamp)
        n_done += 1
    print(f'[curves complete: {n_done} jobs this call, {time.time() - t0:.0f}s]')
    return True


def slim(c, kind, m, stamp):
    """per (kind, map) slim parquet of the rows and columns the curves need (a streaming copy: bounded memory)"""
    d = cache_dir() / 'slim'
    d.mkdir(exist_ok=True)
    if m == 'pooled':
        # the pooled rows are the union of the per-map slims (values are already normalised within each map)
        maps = [r[0] for r in c.execute("select distinct map from sides order by 1").fetchall()]
        files = [slim(c, kind, mm, stamp) for mm in maps]
        return "read_parquet([" + ', '.join(x[len("read_parquet("):-1] for x in files) + "])"
    f = d / f'v2-{kind}-{m.replace(" ", "_")}-{stamp.strip()}.parquet'
    if not f.exists():
        view = {'raw': 'series', 'norm': 'series_n', 'z': 'series_z', 'delta': 'series_d'}[kind]
        have = set(c.execute(f'describe {view}').df().column_name)
        cols = [('d5_' + x) if kind == 'delta' else x for x in (DELTA if kind == 'delta' else [s for v in STATS.values() for s in v])]
        cols = [x for x in cols if x in have]
        rw = 'round % 5 = 0 and round <= 150' if kind == 'delta' else f"round in ({','.join(map(str, ROUNDS))})"
        mw = '' if m == 'pooled' else f"and map = '{m}'"
        sel = ', '.join(f'"{x}"' for x in cols)
        if kind == 'delta':
            # the window runs on the map's filtered rows only (the series_d view would sort the whole store)
            base = [x for x in DELTA if x in set(c.execute('describe series').df().column_name)]
            b = ', '.join(f'"{x}"' for x in base)
            c.execute(f"copy (select game, side, cohort, name, started_at, round, {b} from series where round % 5 = 0 and round <= 150 {mw}) to '{f}.base' (format parquet)")
            d5 = ', '.join(f'"{x}" - lag("{x}") over w as "d5_{x}"' for x in base)
            c.execute(f"copy (select cohort, name, started_at, round, {d5} from read_parquet('{f}.base') window w as (partition by game, side order by round)) "
                      f"to '{f}.tmp' (format parquet)")
            os.replace(f'{f}.base', d / ('_' + f.name + '.base'))
        else:
            c.execute(f"copy (select cohort, name, started_at, round, {sel} from {view} where {rw} {mw}) to '{f}.tmp' (format parquet)")
        os.replace(f'{f}.tmp', f)
    return f"read_parquet('{f}')"


def load():
    return pd.concat(pd.read_parquet(f) for f in cache_dir().glob('*.parquet'))  # slim/ is a subdirectory, not globbed


def figures(stats=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    C = load()
    FIG.mkdir(parents=True, exist_ok=True)
    maps = sorted(m for m in C['map'].unique() if m != 'pooled')
    todo = stats or [s for v in STATS.values() for s in v]
    for stat in todo:
        for kind in ('raw', 'delta'):
            if kind == 'delta' and stat not in DELTA:
                continue
            D = C[(C.stat == stat) & (C.kind == kind)]
            if D.empty:
                continue
            N = C[(C.stat == stat) & (C.kind == 'norm') & (C['map'] == 'pooled')]
            Zp = C[(C.stat == stat) & (C.kind == 'z') & (C['map'] == 'pooled')]
            extra = (['pooled norm 0-150', 'pooled z 0-150', 'pooled z, top-10 teams', 'pooled z 0-500'] if kind == 'raw' else [])
            panels = maps + extra
            ncol = 4
            nrow = (len(panels) + ncol - 1) // ncol
            fig, axes = plt.subplots(nrow, ncol, figsize=(4.0 * ncol, 2.7 * nrow), squeeze=False)
            for k, p in enumerate(panels):
                ax = axes[k // ncol][k % ncol]
                if p in maps:
                    d = D[(D['map'] == p) & (D['round'] <= 150)]
                    sel = [g for g in d.grp.unique() if not g.startswith('team:')]
                elif p == 'pooled z, top-10 teams':
                    d = Zp[Zp['round'] <= 150]
                    sel = [g for g in d.grp.unique() if g.startswith('team:')] + ['us']
                else:
                    src = Zp if ' z ' in p else N
                    d = src if p.endswith('500') else src[src['round'] <= 150]
                    sel = [g for g in d.grp.unique() if not g.startswith('team:')]
                for g in sorted(sel, key=lambda g: (g not in STYLE, g)):
                    x = d[d.grp == g].sort_values('round')
                    if x.empty:
                        continue
                    col, lw = STYLE.get(g, (None, 0.9))
                    ax.plot(x['round'], x['v'], '--' if g.startswith('local:') else '-', color=col, lw=lw, label=g.replace('team:', '')[:18])
                ax.set_title(p, fontsize=8)
                ax.tick_params(labelsize=7)
                ax.grid(alpha=0.25)
                if 'norm' in p:
                    ax.axhline(1, color='grey', lw=0.7, ls=':')
                if ' z' in p:
                    ax.axhline(0, color='grey', lw=0.7, ls=':')
                if k == 0 or p == 'pooled z, top-10 teams':
                    ax.legend(fontsize=5.5, loc='best', ncol=2 if p.startswith('pooled z, top') else 1)
            for k in range(len(panels), nrow * ncol):
                axes[k // ncol][k % ncol].axis('off')
            what = ('change over the previous 5 rounds, mean per side-game' if kind == 'delta' else
                    'median per side-game on each map (raw); pooled: median ÷ field median, and mean field z-score (same map and round)')
            fig.suptitle(f'{stat} — {what}', fontsize=10)
            fig.tight_layout()
            fig.savefig(FIG / f'{"delta-" if kind == "delta" else ""}{stat}.png', dpi=60)
            plt.close(fig)
    print('figures:', FIG)


def gap(cps=(25, 50, 100, 150)):
    """top-10 minus us per stat x checkpoint. Ranked by the gap in field SDs (mean z-score, pooled over maps: an effect
    size that is robust for low counts); the median ratio to the field median is shown beside it for interpretation."""
    C = load()
    C = C[~C.grp.str.startswith('team:') & C['round'].isin(cps)]
    Z = C[(C.kind == 'z') & (C['map'] == 'pooled')].pivot_table(index=['stat', 'round'], columns='grp', values='v')
    N = C[(C.kind == 'norm') & (C['map'] == 'pooled')].pivot_table(index=['stat', 'round'], columns='grp', values='v')
    Rw = C[C.kind == 'raw'].groupby(['stat', 'round', 'grp']).v.median().unstack('grp')   # median over maps of map medians
    T = pd.DataFrame({f'z_{k}': Z[k] for k in Z.columns})
    T['gap_z'] = Z['top10'] - Z['us']
    if 'us_now' in Z.columns:
        T['gap_z_now'] = Z['top10'] - Z['us_now']
    for k in ['top10', 'us', 'us_now'] + [x for x in N.columns if x.startswith('local:')]:
        if k in N.columns:
            T[f'ratio_{k}'] = N[k].reindex(T.index)
    T['raw_top10'] = Rw['top10'].reindex(T.index)
    T['raw_us'] = Rw['us'].reindex(T.index)
    T = T.reset_index()
    T['family'] = T.stat.map(FAMILY)
    T = T.sort_values('gap_z', key=lambda s: -s.abs().fillna(0))
    OUT.mkdir(parents=True, exist_ok=True)
    T.to_csv(OUT / 'gap.csv', index=False)
    print(T.round(3).to_string(index=False))
    return T


def gap_matched(lo=1750, hi=1900, cps=(25, 50, 100, 150)):
    """the gap table restricted to games against opponents rated lo..hi at game time (the same opposition for every
    cohort), on the z scale (mean) and raw (median per map, then median over maps)"""
    c = con()
    have = set(c.execute('describe series_z').df().column_name)
    stats = [x for v in STATS.values() for x in v if x in have]
    rows = []
    for i in range(0, len(stats), 15):
        cs = stats[i:i + 15]
        agg = ', '.join(f'avg(z."{x}") as "{x}"' for x in cs)
        for g in (COHORT, US_NOW):
            d = c.execute(f"""select {g} as grp, z.round, count(*) as n, {agg}
                              from series_z z join (select game, side, opp_elo from c_sides) s using (game, side)
                              where z.round in ({','.join(map(str, cps))}) and s.opp_elo between {lo} and {hi}
                              and {g} is not null group by all""").df()
            rows.append(d.melt(id_vars=['grp', 'round', 'n'], var_name='stat', value_name='z'))
    Z = pd.concat(rows).pivot_table(index=['stat', 'round'], columns='grp', values='z')
    N = pd.concat(rows).groupby('grp').n.max()
    T = Z.add_prefix('z_')
    T['gap_z'] = Z['top10'] - Z['us']
    if 'us_now' in Z.columns:
        T['gap_z_now'] = Z['top10'] - Z['us_now']
    T = T.reset_index()
    T['family'] = T.stat.map(FAMILY)
    T = T.sort_values('gap_z', key=lambda s: -s.abs().fillna(0))
    OUT.mkdir(parents=True, exist_ok=True)
    T.to_csv(OUT / f'gap_matched_{lo}_{hi}.csv', index=False)
    print(f'opponents rated {lo}-{hi}; side-games per cohort at a checkpoint: {N.to_dict()}')
    print(T.round(3).to_string(index=False))
    return T


SIDE_FEATS = ['first_pearl', 'first_split', 'first_contact', 'first_enemy_head_view', 'first_fight', 'first_death', 'gap10_round',
              'bed_first_share', 'bed_arrival_median', 'beds_reached@50', 'beds_reached@100', 'beds_reached@150',
              'births_0_150', 'newborn_surv10_0_150', 'newborn_first_pearl_median_0_150', 'newborn_ever_ate_share_0_150',
              'child_len_mean_0_150', 'child_len_1_2_share_0_150', 'child_len_3_3_share_0_150', 'child_len_4_5_share_0_150',
              'child_len_6_up_share_0_150', 'transit_surv3_0_150', 'transits@50', 'transits@100', 'transits@150',
              'splits_0_50', 'splits_50_100', 'seen50', 'pearls@50', 'pearls@100', 'pearls@150', 'units@100', 'total@150']
MEAN_FEATS = ['gap10_ahead', 'lead@50', 'lead@100', 'lead@150', 'lead_flips_50_150', 'won']


def sides():
    c = con()
    have = set(c.execute('describe sides').df().column_name)
    f = [x for x in SIDE_FEATS if x in have]
    agg = ', '.join(f'median("{x}") as "{x}"' for x in f)
    order = ['top10', 'r11_30', 'r31_50', 'us']
    T = c.execute(f"select {COHORT} as grp, count(*) n, {agg} from sides where {COHORT} is not null group by 1").df().set_index('grp').T
    fm = [x for x in MEAN_FEATS if x in have]
    aggm = ', '.join('avg("%s") as "%s"' % (x, x) for x in fm)
    M = c.execute(f"select {COHORT} as grp, {aggm} from sides where {COHORT} is not null group by 1").df().set_index('grp').T
    # normalised (÷ per-map field median) medians for the same features
    fn = [x for x in f if x in set(c.execute('describe sides_n').df().column_name)]
    aggn = ', '.join('median("%s") as "%s"' % (x, x) for x in fn)
    Tn = c.execute(f"select {COHORT} as grp, {aggn} from sides_n where {COHORT} is not null group by 1").df().set_index('grp').T
    out = T[[x for x in order if x in T.columns]].join(Tn[[x for x in order if x in Tn.columns]].add_suffix('_norm'))
    print('medians by cohort (raw | ÷ per-map field median):')
    print(out.round(3).to_string())
    print('\nmeans by cohort:')
    print(M[[x for x in order if x in M.columns]].round(3).to_string())
    tr = c.execute(f"""select {COHORT} as grp, count(*) n,
        avg(case when "lead@50" = 1 then won end) win_if_ahead50, avg(case when "lead@50" = -1 then won end) win_if_behind50,
        avg(case when "lead@100" = 1 then won end) win_if_ahead100, avg(case when "lead@150" = 1 then won end) win_if_ahead150,
        avg(case when "lead@150" = -1 then won end) win_if_behind150,
        avg(case when "lead@50" * "lead@150" = -1 then 1.0 else 0 end) flip_50_150,
        avg(case when "lead@50" = -1 and "lead@150" = 1 then 1.0 when "lead@50" = -1 then 0 end) comeback_50_150,
        avg(case when "lead@50" = 1 and "lead@150" = -1 then 1.0 when "lead@50" = 1 then 0 end) collapse_50_150,
        avg(case when gap10_round <= 50 and gap10_ahead = 1 then 1.0 when gap10_round <= 50 then 0 end) first10pct_ahead_share,
        avg(case when gap10_ahead = 1 then won end) win_if_first10pct_ahead
        from sides where {COHORT} is not null group by 1 order by 1""").df()
    print('\nlead transitions (total length lead at r50 / r100 / r150):')
    print(tr.round(3).to_string(index=False))
    seat = c.execute("""select map, side, count(*) n, avg(won) win, median(c_eats) pearls100, median(units) units100,
                        median(seen_share) seen100, median(territory) terr100, median(c_own_goals) own100, median(c_transits) transits100
                        from series where round = 100 group by all order by 1, 2""").df()
    print('\nseat asymmetry at r100 (all corpus sides):')
    print(seat.round(3).to_string(index=False))
    Tm = c.execute(f"select map, {COHORT} as grp, count(*) n, {agg} from sides where {COHORT} is not null group by all order by 1, 2").df()
    OUT.mkdir(parents=True, exist_ok=True)
    Tm.to_csv(OUT / 'sides_by_map.csv', index=False)
    out.to_csv(OUT / 'sides_by_cohort.csv')
    M.to_csv(OUT / 'sides_means_by_cohort.csv')
    tr.to_csv(OUT / 'lead_transitions.csv', index=False)
    seat.to_csv(OUT / 'seat_r100.csv', index=False)


if __name__ == '__main__':
    cmd, arg = sys.argv[1], sys.argv[2:]
    if cmd == 'curves':
        curves(budget=float(arg[0]) if arg and arg[0] != 'force' else 150, force='force' in arg)
    elif cmd == 'figs':
        figures(arg or None)
    elif cmd == 'gap':
        gap()
    elif cmd == 'gapm':
        gap_matched(*(int(x) for x in arg[:2])) if len(arg) >= 2 else gap_matched()
    elif cmd == 'sides':
        sides()
