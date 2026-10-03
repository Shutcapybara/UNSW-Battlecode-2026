"""Shenzhen unit 2: cheap lean-table tests for H-SZ6 (crown endurance), H-SZ8 (when crowns grow),
H-SZ9 (queen-policy matchups), H-SZ10 (elimination as the answer to queen keepers). Post-m2 only."""
import duckdb, sys
import pandas as pd, numpy as np
c = duckdb.connect()
d = c.sql("""select distinct on (game, side) L.*, coalesce(T.crank, 999) crank, T.name from 'build/shenzhen/lean/*.parquet' L
  left join 'build/s1/corpus/teams.parquet' T on T.team = L.team""").df()
d = d[pd.to_datetime(d.started_at, utc=True, format='mixed') >= pd.Timestamp('2026-10-02T03:49Z')]
o = d[['game', 'side', 'team', 'crank', 'q_moves', 'q_eats', 'qlen_end', 'R', 'q_death_round']].copy()
o['side'] = o.side.map({'A': 'B', 'B': 'A'})
d = d.merge(o.add_prefix('o_').rename(columns={'o_game': 'game', 'o_side': 'side'}), on=['game', 'side'])
d['coh'] = np.where(d.team == '7', 'us', np.where(d.crank <= 10, 'top10', np.where(d.crank <= 50, 'r11_50', 'other')))
d['rl'] = d.R >= 499
# team queen policy = share of that team's RL games with queen alive at end (m2), min 20 RL games
pol = d[d.rl].groupby('team').agg(n=('rl', 'size'), keep=('qlen_end', lambda s: (s > 0).mean()))
pol = pol[pol.n >= 20]
d['o_keep'] = d.o_team.map(pol.keep)
d['o_policy'] = pd.cut(d.o_keep, [-0.01, 0.15, 0.35, 1.0], labels=['opp_no_queen', 'opp_some', 'opp_keeper'])
q = sys.argv[1:] or ['sz6', 'sz8', 'sz9', 'sz10']
if 'sz6' in q:
    print('== H-SZ6 crown endurance: top-10 win by queen fate (all games, m2)')
    x = d[d.coh == 'top10'].copy()
    x['fate'] = pd.cut(x.q_death_round.fillna(999), [-1, 10, 50, 150, 300, 498, 1000],
                       labels=['dead<=10', '11-50', '51-150', '151-300', '301-498', 'alive/never'])
    print(x.groupby('fate', observed=True).agg(n=('win', 'size'), win=('win', 'mean'), rl=('rl', 'mean')).round(3).to_string())
if 'sz8' in q:
    print('== H-SZ8 when crowns grow: median queen length by checkpoint, RL games with queen alive at end (m2)')
    x = d[d.rl & (d.qlen_end > 0)]
    cols = ['qlen@50', 'qlen@100', 'qlen@150', 'qlen@250', 'qlen@400', 'qlen@490', 'q_eats']
    print(x[x.crank <= 12].groupby('name')[cols].median().join(x.groupby('name').size().rename('n')).query('n>=10').to_string())
if 'sz9' in q:
    print('== H-SZ9 matchups: win by own cohort x opponent queen policy (m2)')
    print(d.pivot_table(index='coh', columns='o_policy', values='win', aggfunc='mean', observed=True).round(3).to_string())
    print(d.pivot_table(index='coh', columns='o_policy', values='win', aggfunc='size', observed=True).to_string())
    print('-- top-10 teams individually vs opponent policy')
    t = d[d.crank <= 10]
    print(t.pivot_table(index='name', columns='o_policy', values='win', aggfunc='mean', observed=True).round(2).to_string())
if 'sz10' in q:
    print('== H-SZ10 how games end, by cohort vs top-10 opponents (m2)')
    x = d[d.o_crank <= 10]
    x = x.assign(endk=np.where(~x.rl, np.where(x.win == 1, 'elim_win', 'elim_loss'), np.where(x.win == 1, 'rl_win', 'rl_loss')))
    print(pd.crosstab(x.coh, x.endk, normalize='index').round(3).to_string())
    print(x.groupby('coh').size().to_string())
