"""S1-Q4: portals and own goals, by cohort and map. Run from the repo root.

  python3 tools/s1/q4.py tables [--rmax 150]   # -> build/s1/out/q4/*.csv, printed summaries
  python3 tools/s1/q4.py figs                  # -> docs/findings/s1-figs/q4/*.png

Portal unit = one transit (a move step whose destination is not the geometric neighbour). A transit is:
  died_same_move  the dragon died in the round of the transit, as the mover
  died_within3    the dragon died within 3 rounds of the transit (per-transit survival = 1 - this)
  blind           the exit cell was outside every 7x7 view of the side at the start of the round
  double          another dragon of the same side went through the same portal pair within +-2 rounds
  contested       an enemy dragon went through the same portal pair within +-2 rounds
Own goals = deaths classed wall, self, ally_body, h2h_ally, invalid (F1 classes; suicide is separate).
"""
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import pandas as pd

S1 = ROOT / 'build' / 's1'
OUT = S1 / 'out' / 'q4'
FIG = ROOT / 'docs' / 'findings' / 's1-figs' / 'q4'
COHORT = "case when cohort in ('top10','r11_30','r31_50','us') then cohort end"
ORDER = ['top10', 'r11_30', 'r31_50', 'us']
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 400)


def con(db='corpus'):
    from tools.s1.q import connect
    return connect(db)


def transit_table(c, rmax, by_map, local=False):
    g = "'local:' || name" if local else COHORT
    mapc = 'map, ' if by_map else ''
    lw = "and run like '%/pool'" if local else ''
    return c.execute(f"""
        select {mapc}{g} as grp, count(*) as transits, count(distinct game || side) as side_games,
               avg(died_same_move) as died_same_move, avg(died_within3) as died3, 1 - avg(died_within3) as surv3,
               avg(died_within10) as died10, avg(blind) as blind_share, avg(double) as double_share,
               avg(contested) as contested_share,
               avg(case when blind = 1 then died_within3 end) as died3_blind,
               avg(case when blind = 0 then died_within3 end) as died3_seen,
               avg(case when double = 1 then died_within3 end) as died3_double,
               avg(case when double = 0 then died_within3 end) as died3_single,
               avg(case when contested = 1 then died_within3 end) as died3_contested,
               avg(case when age <= 10 then died_within3 end) as died3_newborn,
               avg(length) as mean_len, avg(case when age <= 10 then 1.0 else 0 end) as newborn_share
        from {'l_transits' if local else 'transits'} where round <= {rmax} and {g} is not null {lw}
        group by all order by all""").df()


def side_rates(c, rmax, by_map, local=False):
    """per side-game rates up to rmax from series (median over side-games) + pooled rate"""
    g = "'local:' || name" if local else COHORT
    mapc = 'map, ' if by_map else ''
    lw = "and run like '%/pool'" if local else ''
    v = 'l_series' if local else 'series'
    return c.execute(fill_missing(c, v, f"""
        select {mapc}{g} as grp, count(*) as side_games,
               median(c_transits) as transits_med, avg(c_transits) as transits_mean,
               1000 * sum(c_transits) / sum(c_dragon_turns) as transits_per1k_dt,
               1000 * sum(c_deaths_post_transit) / sum(c_dragon_turns) as post_transit_deaths_per1k,
               1000 * sum(c_deaths_near_portal) / sum(c_dragon_turns) as near_portal_deaths_per1k,
               100 * sum(c_transit_died3) / nullif(sum(c_transits), 0) as died3_per100_transits,
               1000 * sum(c_own_goals) / sum(c_dragon_turns) as own_goals_per1k,
               1000 * sum(c_death_wall) / sum(c_dragon_turns) as wall_per1k,
               1000 * sum(c_death_self) / sum(c_dragon_turns) as self_per1k,
               1000 * sum(c_death_ally_body) / sum(c_dragon_turns) as ally_body_per1k,
               1000 * sum(c_death_h2h_ally) / sum(c_dragon_turns) as h2h_ally_per1k,
               1000 * sum(c_death_invalid) / sum(c_dragon_turns) as invalid_per1k,
               1000 * sum(c_death_suicide) / sum(c_dragon_turns) as suicide_per1k,
               1000 * sum(c_death_enemy_body + c_death_h2h_enemy) / sum(c_dragon_turns) as enemy_deaths_per1k,
               1000 * sum(c_deaths) / sum(c_dragon_turns) as deaths_per1k,
               sum(c_own_goals) / nullif(sum(c_deaths), 0) as own_goal_share,
               sum(c_length_lost) / nullif(sum(c_eats), 0) as length_lost_per_pearl
        from {v} where round = {rmax} and {g} is not null {lw} group by all order by all""")).df()


def fill_missing(c, view, sql):
    """a cumulative event column absent from every part of a store means zero events"""
    import re
    have = set(c.execute(f'describe {view}').df().column_name)
    return re.sub(r'\b(c_[a-z0-9_]+)\b', lambda m: m.group(1) if m.group(1) in have else '0', sql)


def own_goal_context(c, rmax, local=False):
    g = "'local:' || name" if local else COHORT
    lw = "and run like '%/pool'" if local else ''
    return c.execute(f"""
        select {g} as grp, cls, count(*) as n,
               avg(enclosed) as enclosed, avg(case when reach5 <= 8 then 1.0 else 0 end) as reach_le8,
               avg(newborn) as newborn, avg(near_portal) as near_portal,
               avg(transit_within3) as post_transit, avg(crowd) as crowd,
               avg(ally_heads3) as ally_heads3, avg(enemy_heads3) as enemy_heads3,
               median(length) as len_med, avg(case when length <= 2 then 1.0 else 0 end) as len_le2, median(age) as age_med
        from {'l_deaths' if local else 'deaths'} where round <= {rmax} and {g} is not null {lw}
          and cls in ('wall', 'self', 'ally_body', 'h2h_ally', 'invalid')
        group by all order by 1, 3 desc""").df()


def post_transit_causes(c, rmax):
    return c.execute(f"""
        with x as (select {COHORT} as grp, cls, count(*) as n from deaths
                   where round <= {rmax} and transit_within3 = 1 and {COHORT} is not null group by all)
        select grp, cls, n, n / sum(n) over (partition by grp) as share from x order by 1, 3 desc""").df()


def tables(rmax_list=(150, 500)):
    c = con()
    has_local = c.execute("select count(*) from information_schema.tables where table_name = 'l_transits'").fetchone()[0] > 0
    OUT.mkdir(parents=True, exist_ok=True)
    for rmax in rmax_list:
        tag = f'r{rmax}'
        T = transit_table(c, rmax, False)
        S = side_rates(c, rmax, False)
        if has_local:
            T = pd.concat([T, transit_table(c, rmax, False, True)])
            S = pd.concat([S, side_rates(c, rmax, False, True)])
        Tm = transit_table(c, rmax, True)
        Sm = side_rates(c, rmax, True)
        O = own_goal_context(c, rmax)
        if has_local:
            O = pd.concat([O, own_goal_context(c, rmax, True)])
        P = post_transit_causes(c, rmax)
        for name, df in (('transits', T), ('rates', S), ('transits_by_map', Tm), ('rates_by_map', Sm), ('own_goal_context', O),
                         ('post_transit_causes', P)):
            df.to_csv(OUT / f'{name}_{tag}.csv', index=False)
        print(f'\n======== rounds 0-{rmax}')
        print('\n-- per transit (pooled maps)'); print(T.round(3).to_string(index=False))
        print('\n-- per side-game rates (pooled maps; sums over side-games / dragon-turns)'); print(S.round(3).to_string(index=False))
        print('\n-- per transit, by map: died within 3 rounds')
        print(Tm.pivot_table(index='map', columns='grp', values='died3')[[x for x in ORDER if x in set(Tm.grp)]].round(3).to_string())
        print('\n-- per transit, by map: transits (count)')
        print(Tm.pivot_table(index='map', columns='grp', values='transits')[[x for x in ORDER if x in set(Tm.grp)]].to_string())
        print('\n-- by map: transits per 1k dragon-turns')
        print(Sm.pivot_table(index='map', columns='grp', values='transits_per1k_dt')[[x for x in ORDER if x in set(Sm.grp)]].round(1).to_string())
        print('\n-- by map: own goals per 1k dragon-turns')
        print(Sm.pivot_table(index='map', columns='grp', values='own_goals_per1k')[[x for x in ORDER if x in set(Sm.grp)]].round(1).to_string())
        print('\n-- by map: post-transit deaths per 1k dragon-turns')
        print(Sm.pivot_table(index='map', columns='grp', values='post_transit_deaths_per1k')[[x for x in ORDER if x in set(Sm.grp)]].round(2).to_string())
        print('\n-- own-goal deaths: context shares'); print(O.round(3).to_string(index=False))
        print('\n-- deaths within 3 rounds of a transit: class mix'); print(P.round(3).to_string(index=False))


def figures(rmax=150):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    Tm = pd.read_csv(OUT / f'transits_by_map_r{rmax}.csv')
    Sm = pd.read_csv(OUT / f'rates_by_map_r{rmax}.csv')
    cols = {'top10': '#1f5fa8', 'r11_30': '#5aa0dc', 'r31_50': '#a8cbe8', 'us': '#d1495b'}
    panels = [(Tm, 'died3', 'per-transit death within 3 rounds'), (Tm, 'blind_share', 'blind landing share'),
              (Tm, 'double_share', 'same-pair double share'), (Sm, 'transits_per1k_dt', 'transits per 1k dragon-turns'),
              (Sm, 'post_transit_deaths_per1k', 'post-transit deaths per 1k dragon-turns'), (Sm, 'own_goals_per1k', 'own goals per 1k dragon-turns'),
              (Sm, 'wall_per1k', 'wall deaths per 1k'), (Sm, 'self_per1k', 'self deaths per 1k'), (Sm, 'ally_body_per1k', 'ally-body deaths per 1k'),
              (Sm, 'h2h_ally_per1k', 'ally head-on deaths per 1k')]
    fig, axes = plt.subplots(len(panels), 1, figsize=(11, 2.6 * len(panels)))
    for ax, (df, col, title) in zip(axes, panels):
        P = df.pivot_table(index='map', columns='grp', values=col)
        P = P[[x for x in ORDER if x in P.columns]]
        P.plot.bar(ax=ax, color=[cols[x] for x in P.columns], width=0.8, legend=ax is axes[0])
        ax.set_title(f'{title} (rounds 0-{rmax})', fontsize=9)
        ax.set_xlabel('')
        ax.tick_params(labelsize=7, labelrotation=0)
        ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / f'q4-portals-owngoals-r{rmax}.png', dpi=70)
    plt.close(fig)
    print('figure:', FIG / f'q4-portals-owngoals-r{rmax}.png')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'tables':
        tables()
    elif cmd == 'figs':
        figures(150)
        figures(500)
