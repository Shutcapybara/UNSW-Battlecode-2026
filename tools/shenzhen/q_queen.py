"""Shenzhen queen/endgame tables from the lean table (build/shenzhen/lean). Era post only (the lean table is post)."""
import duckdb, os, sys
# map era: on 2026-10-02 03:49Z the live server replaced Autarky, Slithery Fight, Prisoners Dilemma, Trophy, Default and
# Schooltime (queen re-ordered out of the spawn pocket on Autarky/Slithery/PD; Trophy queen moved; a few EDGE changes).
# SZ_M2=1 keeps only games started after the swap (all maps), the live state of the game.
M2 = os.environ.get('SZ_M2', '1') == '1'
c = duckdb.connect()
c.sql("create view L0 as select distinct on (game, side) * from 'build/shenzhen/lean/*.parquet'")
c.sql("create view T as select * from 'build/s1/corpus/teams.parquet'")
c.sql("""create view L as select L0.*, coalesce(T.crank, 999) crank, T.name,
  case when L0.team='7' then 'us' when T.crank<=10 then 'top10' when T.crank<=30 then 'r11_30' when T.crank<=50 then 'r31_50' else 'other' end cohort,
  (R>=499) rl, (qlen_end>0) qalive, cast(started_at as timestamptz) st,
  map in ('Slithery Fight','Autarky','Prisoners Dilemma','Prisoners Dilemma 10') pocket
  from L0 left join T on T.team=L0.team""" + (" where cast(L0.started_at as timestamptz) >= '2026-10-02 03:49:00+00'" if M2 else ""))
Q = dict(
cohort="""select cohort, count(*) n_side, round(avg(rl::int),3) rl_share,
  round(avg(case when rl then qalive::int end),3) q_alive_rl,
  round(avg(case when rl and not pocket then qalive::int end),3) q_alive_rl_nopocket,
  median(case when rl and qalive then qlen_end end) qlen_alive_med,
  round(avg(case when rl then win end),3) win_rl,
  round(avg(win),3) win_all,
  sum((reason='queen' and win=1)::int) q_dec_w, sum((reason='queen' and win=0)::int) q_dec_l,
  round(avg(case when rl and win=0 then (total_end>opp_total_end)::int end),3) rl_loss_total_lead,
  median(case when rl then longest_end end) longest_end_rl, median(case when rl then total_end end) total_end_rl,
  median(q_death_round) q_death_med
  from L group by 1 order by case cohort when 'top10' then 0 when 'r11_30' then 1 when 'r31_50' then 2 when 'other' then 3 else 4 end""",
team="""select crank, name, count(*) n, sum(rl::int) n_rl, round(avg(case when rl and not pocket then qalive::int end),2) qalive_np,
  median(case when rl and qalive then qlen_end end) qlen, round(avg(case when rl then win end),2) win_rl, round(avg(win),2) win,
  sum((reason='queen' and win=1)::int) qW, sum((reason='queen' and win=0)::int) qL,
  round(median(q_moves/(R+1.0)),2) q_move_share, median(q_eats) q_eats, median(q_splits) q_splits, median(q_death_round) q_dr,
  round(avg(case when q_killer_team='enemy' then 1.0 when q_death_cause is not null then 0.0 end),2) q_enemy_killed
  from L where crank<=12 or team='7' group by 1,2 order by 1""",
causes="""select cohort, q_death_cause, count(*) n, round(count(*)*1.0/sum(count(*)) over (partition by cohort),3) frac
  from L where q_death_cause is not null and not pocket group by 1,2 order by 1,3 desc""",
maps="""select map, cohort, count(*) n_rl, round(avg(qalive::int),3) qalive, round(avg((q_death_round<=10)::int),3) qdead_r10,
  round(avg((reason='queen')::int),3) qdec, round(avg(win),3) win from L where rl and cohort in ('top10','us','other') group by 1,2 order by 1,2""",
clock="""select date_trunc('hour', st) - (extract(hour from st)::int % 12) * interval 1 hour h12, cohort, count(*) n_rl,
  round(avg(case when not pocket then qalive::int end),3) qalive_np, round(avg((reason='queen')::int),3) queen_decided
  from L where rl group by 1,2 having count(*)>=20 order by 1,2""",
)
for k in (sys.argv[1:] or Q):
    print('==', k); print(c.sql(Q[k]).df().to_string(index=False))
