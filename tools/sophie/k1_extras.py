"""K-1 extras: (a) structure-only GLM trained on the field's pool cells, tested within each gen map on the V06 lane
base's deaths; (b) our excess per class split into 'where we go' (exposure mix over signatures) and 'how we die there'
(rate); (c) per-map hot cells (our rate vs the field's on the same cell) with their signatures -> small JSON."""
import json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hazard  # noqa: E402
from k1_hazard_fit import load, design, fit_pois, pred, dev, STRUCT, AGG  # noqa: E402

CLS = ['wall', 'self', 'ally_body', 'h2h_ally', 'trapped', 'newborn', 'transit', 'crowd23', 'fight']
POOL = {'Autarky', 'Default', 'Devil', 'Portals', 'Prisoners Dilemma', 'Prisoners Dilemma 10', 'Queen Of Spades', 'Schooltime',
        'Slithery Fight', 'Trauma', 'Trophy'}


def main(out):
    A = load(['us', 'field', 'top10', 'local'])
    A = A[A['expo'] > 0].copy()
    X = design(A)
    recs = A.to_dict('records')
    sigs = list(hazard.SIGNATURES)
    A['sig'] = [next((k for k in sigs if hazard.SIGNATURES[k][1](r)), '_rest') for r in recs]   # first match, for the mix split
    res = dict(gen_transfer={}, decomposition={}, hot_cells={})
    F = A['cohort'] == 'field'
    G = (A['cohort'] == 'local') & ~A['mapkey'].isin(POOL)
    LP = (A['cohort'] == 'local') & A['mapkey'].isin(POOL)
    for c in CLS:
        yc = f'n_{c}'
        fm = fit_pois(X[F][STRUCT], A[F][yc] / A[F]['expo'], A[F]['expo'])
        per = {}
        for mp in sorted(A[G]['mapkey'].unique()):
            s = G & (A['mapkey'] == mp)
            y = A[s][yc]
            if y.sum() < 20:
                continue
            mu = pred(fm, X[s][STRUCT]) * A[s]['expo']
            mu = mu * y.sum() / max(mu.sum(), 1e-9)
            flat = y.sum() / A[s]['expo'].sum() * A[s]['expo']
            per[mp] = round(1 - dev(y, mu) / dev(y, flat), 3) if dev(y, flat) > 0 else None
        vals = [v for v in per.values() if v is not None]
        lp = LP
        y = A[lp][yc]
        mu = pred(fm, X[lp][STRUCT]) * A[lp]['expo']
        res['gen_transfer'][c] = dict(field_model_on_v06_gen_D2_within=per, median=float(np.median(vals)) if vals else None,
                                      n_maps=len(vals))
        # decomposition of our excess (pool): per signature bucket
        U = A['cohort'] == 'us'
        eu = A[U].groupby('sig')['expo'].sum() / A[U]['expo'].sum()
        ef = A[F].groupby('sig')['expo'].sum() / A[F]['expo'].sum()
        ru = A[U].groupby('sig')[yc].sum() / A[U].groupby('sig')['expo'].sum()
        rf = A[F].groupby('sig')[yc].sum() / A[F].groupby('sig')['expo'].sum()
        idx = ef.index.union(eu.index)
        eu, ef, ru, rf = (s.reindex(idx).fillna(0) for s in (eu, ef, ru, rf))
        total_u, total_f = float((eu * ru).sum()), float((ef * rf).sum())
        mix = float(((eu - ef) * rf).sum())
        rate = float((eu * (ru - rf)).sum())
        res['decomposition'][c] = dict(us_per1k=1000 * total_u, field_per1k=1000 * total_f, excess_per1k=1000 * (total_u - total_f),
                                       from_where_we_go=1000 * mix, from_how_we_die_there=1000 * rate,
                                       by_signature={k: dict(mix=round(1000 * float((eu[k] - ef[k]) * rf[k]), 3),
                                                             rate=round(1000 * float(eu[k] * (ru[k] - rf[k])), 3),
                                                             expo_us=round(float(eu[k]), 4), expo_field=round(float(ef[k]), 4))
                                                     for k in idx})
        print(c, 'gen D2 median', res['gen_transfer'][c]['median'], 'n', len(vals), '| excess', round(1000 * (total_u - total_f), 2),
              'mix', round(1000 * mix, 2), 'rate', round(1000 * rate, 2), flush=True)
    # hot cells per pool map: all-death (non-suicide) length lost per 1k head-turns, us vs field on the same cell
    A['len_any'] = sum(A[f'len_{c}'] for c in ['wall', 'self', 'ally_body', 'h2h_ally', 'h2h_enemy', 'enemy_body'])
    for mp in sorted(A[A['cohort'] == 'us']['mapkey'].unique()):
        u = A[(A['cohort'] == 'us') & (A['mapkey'] == mp)].set_index(['x', 'y'])
        f = A[F & (A['mapkey'] == mp)].set_index(['x', 'y'])
        j = u[['expo', 'len_any', 'sig']].join(f[['expo', 'len_any']], rsuffix='_f', how='inner')
        j = j[(j['expo'] >= 300) & (j['expo_f'] >= 1000)]
        j['us_rate'] = 1000 * j['len_any'] / j['expo']
        j['f_rate'] = 1000 * j['len_any_f'] / j['expo_f']
        j['excess_len'] = (j['us_rate'] - j['f_rate']) * j['expo'] / 1000     # our extra length lost on this cell
        top = j.sort_values('excess_len', ascending=False).head(8)
        res['hot_cells'][mp] = dict(total_excess_len=float(j['excess_len'].sum()), share_top8=float(top['excess_len'].sum() / max(j['excess_len'].clip(lower=0).sum(), 1)),
                                    by_signature={k: round(float(v), 1) for k, v in j.groupby('sig')['excess_len'].sum().items()},
                                    top=[dict(x=int(x), y=int(y), sig=r['sig'], us_len_per1k=round(r['us_rate'], 1), field_len_per1k=round(r['f_rate'], 1),
                                              us_headturns=int(r['expo']), excess_len=round(r['excess_len'], 1)) for (x, y), r in top.iterrows()])
    json.dump(res, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1])
