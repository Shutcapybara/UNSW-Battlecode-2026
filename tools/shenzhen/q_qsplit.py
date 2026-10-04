"""Shenzhen: the queen's first split (round, kept length = parent_len, given = child_len) vs early queen death, by cohort.
Sample: lean-table games on the given maps (default: all), decoded again for the split events (parallel)."""
import duckdb, sys, multiprocessing as mp
import pandas as pd
sys.path.insert(0, '.')
def one(a):
    game, side, q = a
    from tools.analysis.features.frame import decode
    g = decode(f'public_replays/corpus/replays/{game}.replay')
    sp = [s for s in g['events']['splits'] if s['parent'] == q]
    l0 = len(g['rounds'][0][q][1]) if q in g['rounds'][0] else None
    f = sp[0] if sp else None
    early = [s for s in sp if s['round'] <= 10]
    return dict(game=game, side=side, l0=l0, first_r=f['round'] if f else None, kept=f['parent_len'] if f else None,
                given=f['child_len'] if f else None, n_split10=len(early),
                min_kept10=min((s['parent_len'] for s in early), default=None))
if __name__ == '__main__':
    maps = sys.argv[1].split(',') if len(sys.argv) > 1 else None
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    d = duckdb.sql("""select distinct on (game,side) L.*, coalesce(T.crank,999) crank from 'build/shenzhen/lean/*.parquet' L
         left join 'build/s1/corpus/teams.parquet' T on T.team=L.team""").df()
    if maps: d = d[d['map'].isin(maps)]
    d['coh'] = d.crank.map(lambda c: 'top10' if c <= 10 else 'r11_50' if c <= 50 else 'other'); d.loc[d.team == '7', 'coh'] = 'us'
    d = d.groupby('coh', group_keys=False).apply(lambda x: x.sample(min(len(x), n // 4), random_state=1))
    with mp.Pool(4) as p:
        r = pd.DataFrame(p.map(one, [(x.game, x.side, int(x.q_id)) for x in d.itertuples()]))
    m = d.merge(r, on=['game', 'side'])
    m['dead10'] = (m.q_death_round <= 10).astype(float)
    m['small_kept'] = (m.kept <= 2) & (m.first_r <= 10)
    print(m.groupby('coh').agg(n=('dead10', 'size'), dead10=('dead10', 'mean'), split_by10=('n_split10', lambda s: (s > 0).mean()),
          small_kept=('small_kept', 'mean'), kept_med=('kept', 'median'), l0_med=('l0', 'median')).round(2).to_string())
    print(m.groupby(['small_kept']).agg(n=('dead10', 'size'), dead10=('dead10', 'mean')).round(3).to_string())
    print(m.groupby(['coh', 'small_kept']).agg(n=('dead10', 'size'), dead10=('dead10', 'mean')).round(3).to_string())
    m.to_parquet('build/shenzhen/qsplit_sample.parquet')
