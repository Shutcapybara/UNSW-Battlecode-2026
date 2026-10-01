"""Post-change opening references: S-1 Q3's components, top ten vs field vs us, per map and pooled, per era.

  S1_ERA=post python3 tools/antioch/opening_refs.py table [--local-run carthage-00-base] [--out build/antioch/opening_post.csv]
  S1_ERA=post python3 tools/antioch/opening_refs.py stability [--boot 400]
  python3 tools/antioch/opening_refs.py shift                 # pre vs post field medians on the ten ladder maps (no S1_ERA)

Components (Q3): bed conversion (c_eats_bed, bed_capture), production (c_splits, units), early portal use (c_transits),
territory (territory), plus material (total) as the outcome. Checkpoints r25/50/100/150. "us" is a local store run (a
tester's 1.2.3 base panel replays decoded with `build.py local --tag <run>`), normalised against the same era's corpus field;
the corpus has no post-change team-7 games. Field = every corpus side-game of the era on the ten ladder maps.
Values: per-map field percentile of the cohort median (the D-037 form), and the field z-gap (top ten − field, us − field).
"""
import argparse, os, sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from tools.s1 import q as Q   # noqa: E402

LADDER = ('Autarky', 'Default', 'Devil', 'Portals', 'Prisoners Dilemma', 'Queen Of Spades', 'Schooltime', 'Slithery Fight',
          'Trauma', 'Trophy')
STATS = {'bed pearls (cum.)': 'c_eats_bed', 'bed capture': 'bed_capture', 'splits (cum.)': 'c_splits', 'units': 'units',
         'transits (cum.)': 'c_transits', 'territory': 'territory', 'total length': 'total'}
CPS = (25, 50, 100, 150)
LOCALMAP = {'autarky': 'Autarky', 'default': 'Default', 'devil': 'Devil', 'portals': 'Portals', 'dilemma': 'Prisoners Dilemma',
            'queen_of_spades': 'Queen Of Spades', 'schooltime': 'Schooltime', 'slithery_fight': 'Slithery Fight',
            'trauma': 'Trauma', 'trophy': 'Trophy'}


def frame(con, local_run=None):
    import pandas as pd
    cols = ', '.join(Q.q(c) for c in STATS.values())
    maps = ','.join(f"'{m}'" for m in LADDER)
    c = con.execute(f"select game, side, map, round, cohort, name, {cols} from c_series where round in {CPS} and map in ({maps})").df()
    c['grp'] = c.cohort
    out = [c]
    if local_run:
        have = con.execute("select count(*) from information_schema.tables where table_name = 'l_series'").fetchone()[0]
        if have:
            l = con.execute(f"select game, side, map, round, team, {cols} from l_series where round in {CPS} and run = ?",
                            [local_run]).df()
            l = l[l.team.str.contains(local_run, regex=False)]
            l['map'] = l.map.map(lambda m: LOCALMAP.get(m.lower().replace(' ', '_'), m))
            l['grp'] = 'us(local)'
            out.append(l)
    return pd.concat(out, ignore_index=True)


def pct(field, v):
    import numpy as np
    f = np.sort(field[~np.isnan(field)])
    return float(np.searchsorted(f, v, side='right')) / len(f) if len(f) else float('nan')


def table(a):
    import numpy as np, pandas as pd
    con = Q.connect('corpus')
    if a.local_run and (Q.S1 / 'local' / 'sides').exists():
        pass
    d = frame(con, a.local_run)
    field = d[d.grp != 'us(local)']
    rows = []
    for lab, st in STATS.items():
        for cp in CPS:
            per = []
            for m in LADDER:
                f = field[(field.map == m) & (field['round'] == cp)][st].to_numpy(float)
                mu, sd = np.nanmean(f), np.nanstd(f)
                for g in ('top10', 'us(local)'):
                    x = d[(d.map == m) & (d['round'] == cp) & (d.grp == g)][st].to_numpy(float)
                    if len(x) < 5:
                        continue
                    per.append(dict(stat=lab, round=cp, map=m, grp=g, n=len(x), n_field=len(f), median=np.nanmedian(x),
                                    field_median=np.nanmedian(f), pctile=pct(f, np.nanmedian(x)),
                                    z=(np.nanmean(x) - mu) / sd if sd > 0 else np.nan))
            rows += per
    t = pd.DataFrame(rows)
    t['era'] = os.environ.get('S1_ERA', 'pooled')
    if a.out:
        t.to_csv(a.out, index=False)
    pooled = t.groupby(['stat', 'round', 'grp']).agg(z=('z', 'mean'), pctile=('pctile', 'median'), maps=('map', 'nunique'),
                                                    n=('n', 'sum')).reset_index()
    w = pooled.pivot_table(index=['stat', 'round'], columns='grp', values=['z', 'pctile']).round(2)
    if ('z', 'top10') in w and ('z', 'us(local)') in w:
        w[('gap', 'top10-us')] = (w[('z', 'top10')] - w[('z', 'us(local)')]).round(2)
    print(w.to_string())
    print('\nn per map (top10 / field at r50):', t[(t['round'] == 50) & (t.grp == 'top10')].set_index('map')[['n', 'n_field']].to_dict('index'))


def stability(a):
    """bootstrap (games) half-width of the field median and of the top-10 percentile per map at r50, vs n"""
    import numpy as np, pandas as pd
    con = Q.connect('corpus')
    d = frame(con)
    rng = np.random.default_rng(0)
    rows = []
    for st in ('c_eats_bed', 'c_splits', 'total', 'c_transits'):
        for m in LADDER:
            x = d[(d.map == m) & (d['round'] == 50)]
            f = x[st].to_numpy(float)
            t = x[x.grp == 'top10'][st].to_numpy(float)
            if len(f) < 20:
                continue
            med = np.nanmedian(f)
            bs = [np.nanmedian(rng.choice(f, len(f))) for _ in range(a.boot)]
            pc = [pct(rng.choice(f, len(f)), np.nanmedian(rng.choice(t, len(t)))) for _ in range(a.boot)] if len(t) >= 5 else [np.nan]
            rows.append(dict(stat=st, map=m, n_field=len(f), n_top10=len(t), field_median=med,
                             med_halfwidth_rel=(np.quantile(bs, .95) - np.quantile(bs, .05)) / 2 / med if med else np.nan,
                             top10_pctile=np.nanmedian(pc), pctile_halfwidth=(np.nanquantile(pc, .95) - np.nanquantile(pc, .05)) / 2))
    s = pd.DataFrame(rows)
    print(s.round(3).to_string())
    print('\nmedian over maps:', s.groupby('stat')[['n_field', 'n_top10', 'med_halfwidth_rel', 'pctile_halfwidth']].median().round(3).to_string())


def shift(a):
    """pre vs post field medians per map (ten ladder maps), r25/50/100/150"""
    import numpy as np, pandas as pd
    con = Q.connect('corpus', norms=False)
    cols = ', '.join(Q.q(c) for c in STATS.values())
    maps = ','.join(f"'{m}'" for m in LADDER)
    d = con.execute(f"select s.map, s.round, g.era, {cols} from c_series_b s join games g using (game) "
                    f"where s.round in {CPS} and s.map in ({maps})").df()
    m = d.groupby(['era', 'map', 'round'])[list(STATS.values())].median()
    n = d[d['round'] == 50].groupby(['era', 'map']).size().unstack(0)
    r = (m.loc['post'] / m.loc['pre']).round(2)
    print('post / pre field median, per map and checkpoint'); print(r.to_string())
    print('\nside-games per map (r50):'); print(n.to_string())
    pooled = r.groupby(level='round').median()
    print('\nmedian over maps:'); print(pooled.to_string())


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    t = sp.add_parser('table'); t.add_argument('--local-run'); t.add_argument('--out')
    s = sp.add_parser('stability'); s.add_argument('--boot', type=int, default=400)
    sp.add_parser('shift')
    a = ap.parse_args()
    dict(table=table, stability=stability, shift=shift)[a.cmd](a)


if __name__ == '__main__':
    main()
