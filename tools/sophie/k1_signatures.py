"""K-1 Part 2: evaluate the fixed signatures (hazard.SIGNATURES) per class: field vs us vs local (V06) on pool and
gen maps; per-terrain ratios; rest-of-map ratio. Writes the ratio table hazard.profile() uses and the per-map profiles.
"""
import json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(os.environ.get('K1_REPO', Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hazard  # noqa: E402
from k1_hazard_fit import AGG, base_name  # noqa: E402

CLS = ['wall', 'self', 'ally_body', 'h2h_ally', 'trapped', 'newborn', 'transit', 'crowd23', 'fight', 'h2h_enemy']
POOL = {'Autarky', 'Default', 'Devil', 'Portals', 'Prisoners Dilemma', 'Prisoners Dilemma 10', 'Queen Of Spades', 'Schooltime',
        'Slithery Fight', 'Trauma', 'Trophy'}


def main(out_json, out_ratio, out_profiles):
    R = pd.read_parquet(AGG / 'cellrows.parquet')
    R['cohort'] = R['cohort'].replace({'top10': 'field'})
    R['terrain'] = R['map'].map(base_name)
    R['gen'] = ~R['map'].isin(POOL)
    recs = R.to_dict('records')
    for k, (_, f) in hazard.SIGNATURES.items():
        R[k] = [bool(f(r)) for r in recs]
    R['_rest'] = ~R[list(hazard.SIGNATURES)].any(axis=1)
    groups = {'field_pool': (R['cohort'] == 'field'), 'us_pool': (R['cohort'] == 'us'),
              'v06_pool': (R['cohort'] == 'local') & ~R['gen'], 'v06_gen': (R['cohort'] == 'local') & R['gen']}
    res, ratios = {}, {}
    for sig in list(hazard.SIGNATURES) + ['_rest']:
        res[sig] = {}
        ratios[sig] = {}
        for c in CLS:
            e = {}
            for gname, gm in groups.items():
                G = R[gm]
                base = G[f'n_{c}'].sum() / max(G['expo'].sum(), 1)
                m = G[sig]
                rate = G[m][f'n_{c}'].sum() / max(G[m]['expo'].sum(), 1)
                # per-map ratio (leaf rate / that map's rate), maps with >= 2000 head-turns in the signature
                per = []
                for mp, d in G.groupby('map'):
                    dm = d[d[sig]]
                    if dm['expo'].sum() >= 2000 and d[f'n_{c}'].sum() > 0:
                        per.append((dm[f'n_{c}'].sum() / dm['expo'].sum()) / (d[f'n_{c}'].sum() / d['expo'].sum()))
                e[gname] = dict(ratio=rate / base if base else None, rate_per1k=1000 * rate,
                                expo_share=float(G[m]['expo'].sum() / max(G['expo'].sum(), 1)),
                                death_share=float(G[m][f'n_{c}'].sum() / max(G[f'n_{c}'].sum(), 1)),
                                len_share=float(G[m][f'len_{c}'].sum() / max(G[f'len_{c}'].sum(), 1)),
                                maps_gt1=int(sum(p > 1 for p in per)), maps=len(per),
                                per_map_median=float(np.median(per)) if per else None)
            f_, u_ = e['field_pool'], e['us_pool']
            e['us_over_field'] = (u_['rate_per1k'] / f_['rate_per1k']) if f_['rate_per1k'] else None
            res[sig][c] = e
            ratios[sig][c] = round(f_['ratio'], 3) if f_['ratio'] else 1.0
    json.dump(res, open(out_json, 'w'), indent=1)
    json.dump(ratios, open(out_ratio, 'w'), indent=1)
    # per-map hazard profiles for the 39 maps (pool + maps/new + maps/var *_tr)
    files = sorted(set([p for p in (REPO / 'maps').glob('*.map')
                        if p.stem in ('autarky', 'default', 'devil', 'portals', 'dilemma', 'dilemma_10', 'queen_of_spades',
                                      'schooltime', 'slithery_fight', 'trauma', 'trophy')]
                       + list((REPO / 'maps/new').glob('*.map')) + list((REPO / 'maps/var').glob('*_tr.map'))))
    rows = []
    for p in files:
        pr = hazard.profile(str(p), ratios)
        row = dict(file=str(p.relative_to(REPO)), map=pr['name'], W=pr['W'], H=pr['H'],
                   **{k: round(v, 4) for k, v in pr['scalars'].items()},
                   **{'share_' + k: round(v, 4) for k, v in pr['share'].items()},
                   **{'idx_' + k: round(v, 3) for k, v in pr['index'].items()})
        rows.append(row)
    P = pd.DataFrame(rows)
    P.to_csv(out_profiles, index=False)
    print(P[['file'] + [c for c in P.columns if c.startswith('share_')]].to_string())


if __name__ == '__main__':
    main(*sys.argv[1:4])
