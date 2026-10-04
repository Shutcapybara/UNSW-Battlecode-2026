"""Shenzhen: opening components, top-10 vs us (live team 7), z against the post-change field of the same map.
z = (x - field mean_map) / field sd_map, field = all in-scope sides in the lean table (balanced sample) on that map.
Also field percentile of the cohort median. Two views: all games, and vs top-10 opponents only (same opposition)."""
import duckdb, os, sys
M2 = os.environ.get('SZ_M2', '1')   # '1' post-map-swap (2 Oct 03:49Z) only, '0' pre-swap only, 'all'
import numpy as np, pandas as pd
c = duckdb.connect()
c.sql("create view L0 as select distinct on (game, side) * from 'build/shenzhen/lean/*.parquet'")
c.sql("create view T as select * from 'build/s1/corpus/teams.parquet'")
d = c.sql("""select L0.*, case when L0.team='7' then 'us' when T.crank<=10 then 'top10' when T.crank<=30 then 'r11_30' else 'rest' end cohort,
   case when L0.opp='7' then 'us' when T2.crank<=10 then 'top10' else 'rest' end opp_cohort
   from L0 left join T on T.team=L0.team left join T T2 on T2.team=L0.opp""").df()
ts = pd.to_datetime(d.started_at, utc=True, format='mixed'); sw = pd.Timestamp('2026-10-02T03:49:00Z')
d = d[{'1': ts >= sw, '0': ts < sw}.get(M2, ts.notna())]
comps = ['transits', 'bed', 'splits', 'units', 'total', 'longest', 'eats', 'corpse', 'deaths', 'tdied3']
rows = []
for ck in (25, 50, 100, 150):
    for comp in comps:
        col = f'{comp}@{ck}'
        x = d[d[f'alive@{ck}'] == 1] if ck > 100 else d
        g = x.groupby('map')[col]
        z = ((x[col] - g.transform('mean')) / g.transform('std').replace(0, np.nan))
        x = x.assign(z=z)
        for view, sub in (('all', x), ('vs_top10', x[x.opp_cohort == 'top10'])):
            m = sub.groupby('cohort').z.mean()
            n = sub.groupby('cohort').z.size()
            if 'top10' in m and 'us' in m:
                # bootstrap over games for the gap
                a, b = sub[sub.cohort == 'top10'].z.dropna().values, sub[sub.cohort == 'us'].z.dropna().values
                rng = np.random.default_rng(1)
                bs = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(400)]
                rows.append(dict(r=ck, comp=comp, view=view, top10=round(m['top10'], 2), us=round(m['us'], 2),
                                 gap=round(m['top10'] - m['us'], 2), lo=round(np.percentile(bs, 5), 2), hi=round(np.percentile(bs, 95), 2),
                                 n_top=n['top10'], n_us=n['us'],
                                 med_top=x[x.cohort == 'top10'][col].median(), med_us=x[x.cohort == 'us'][col].median()))
out = pd.DataFrame(rows)
print(out[out.view == (sys.argv[1] if len(sys.argv) > 1 else 'all')].to_string(index=False))
