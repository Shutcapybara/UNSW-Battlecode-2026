"""H-SZ28 birth-cohort fates (corpse2.py), us vs top ten, per map; game-clustered 90 % bootstrap of the share eaten by the enemy."""
import duckdb, pandas as pd, numpy as np
d = duckdb.sql("select * from 'build/shenzhen/corpse2/part-*.parquet'").df().fillna(0)
T = pd.read_parquet('build/s1/corpus/teams.parquet'); cr = dict(zip(T.team, T.crank))
d['coh'] = d.team.map(lambda t: 'us' if t == '7' else 'top10' if (cr.get(t) or 999) <= 10 else 'rest')
for c in ['born','all_self','all_enemy','all_uneaten','contact_born','home_born','contact_enemy','home_enemy','contact_self','home_self']:
    if c not in d: d[c] = 0
print('games', d.game.nunique())
def boot(x, num, den, B=500):
    rng = np.random.default_rng(0); v = x[[num, den]].values
    return np.percentile([v[i, 0].sum() / max(1, v[i, 1].sum()) for i in (rng.integers(0, len(v), len(v)) for _ in range(B))], [5, 95]).round(3)
rows = []
for (m, c), x in d[d.coh.isin(['top10', 'us'])].groupby(['map', 'coh']):
    b = x.born.sum()
    rows.append(dict(map=m, coh=c, sides=len(x), born=int(b), self=round(x.all_self.sum() / b, 3), enemy=round(x.all_enemy.sum() / b, 3),
                     enemy_ci=boot(x, 'all_enemy', 'born'), uneaten=round(x.all_uneaten.sum() / b, 3),
                     contact_share=round(x.contact_born.sum() / b, 3),
                     enemy_if_contact=round(x.contact_enemy.sum() / max(1, x.contact_born.sum()), 3),
                     enemy_if_home=round(x.home_enemy.sum() / max(1, x.home_born.sum()), 3)))
print(pd.DataFrame(rows).to_string(index=False))
