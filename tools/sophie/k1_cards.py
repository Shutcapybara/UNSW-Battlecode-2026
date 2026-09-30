"""K-1 Part 1: per-map trouble cards (literal + general), us vs the field, BENCHMARKS three-number form.

    python tools/sophie/k1_cards.py [--us-filter all|ranked] --out game_stats/runs/sophie-trouble-<tag>.json

Rates are pooled (sum of events / sum of dragon-turns x 1000) per cohort and map; the field percentile is
the mean over our side-games of the share of field side-games on the same map with a worse value (ties half),
so 0.5 = field-typical and higher = better, for every metric (deaths: fewer is better).
"""
import argparse, json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(os.environ.get('K1_REPO', Path(__file__).resolve().parents[2]))
AGG = REPO / os.environ.get('K1_AGG', 'build/sophie/agg')
CLASSES = ['wall', 'self', 'ally_body', 'h2h_ally', 'enemy_body', 'h2h_enemy', 'suicide', 'invalid']
CTX = {'nb': 'newborn', 'tr': 'trapped', 'po': 'portal', 'tx': 'transit', 'cr': 'crowd23', 'fi': 'fight'}
RBL = ['r0-49', 'r50-99', 'r100-249', 'r250+']
LBL = ['L1-3', 'L4-7', 'L8-15', 'L16+']
RB_EDGES = [0, 50, 100, 250, 10 ** 6]
LB_EDGES = [1, 4, 8, 16, 10 ** 6]


def pct_vs(field_vals, ours, higher_better):
    f = np.sort(np.asarray(field_vals, float))
    f = f[~np.isnan(f)]
    out = []
    for v in ours:
        if v != v or not len(f):
            continue
        lo = np.searchsorted(f, v, 'left')
        hi = np.searchsorted(f, v, 'right')
        below, ties = lo, hi - lo
        above = len(f) - hi
        beat = (below if higher_better else above) + 0.5 * ties
        out.append(beat / len(f))
    return float(np.mean(out)) if out else float('nan')


def side_game_rates(S, D):
    """per side-game counts and length lost per class / context / band; returns a wide frame keyed like S"""
    key = ['set', 'game', 'side']
    D = D.copy()
    D['rb'] = pd.cut(D['r'], RB_EDGES, right=False, labels=RBL)
    D['lb'] = pd.cut(D['L'], LB_EDGES, right=False, labels=LBL)
    parts = []
    for c in CLASSES:
        m = D['cls'] == c
        parts.append(D[m].groupby(key).size().rename(f'n_{c}'))
        parts.append(D[m].groupby(key)['L'].sum().rename(f'len_{c}'))
    for k, name in CTX.items():
        m = D[k].astype(bool)
        if k == 'tr':
            pass
        parts.append(D[m].groupby(key).size().rename(f'n_ctx_{name}'))
        parts.append(D[m].groupby(key)['L'].sum().rename(f'len_ctx_{name}'))
    notsu = D['cls'] != 'suicide'
    parts.append(D[notsu].groupby(key).size().rename('n_all'))
    parts.append(D[notsu].groupby(key)['L'].sum().rename('len_all'))
    avoid = D['cls'].isin(['wall', 'self', 'ally_body', 'h2h_ally'])
    parts.append(D[avoid].groupby(key).size().rename('n_avoidable'))
    parts.append(D[avoid & (D['nb'])].groupby(key).size().rename('n_newborn10'))
    W = pd.concat(parts, axis=1).fillna(0)
    X = S.set_index(key).join(W).fillna({c: 0 for c in W.columns}).reset_index()
    for c in W.columns:
        pass
    return X, D


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--us-filter', default='all')
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    S = pd.read_parquet(AGG / 'sides.parquet')
    D = pd.read_parquet(AGG / 'deaths.parquet')
    S = S[S['set'].isin(['us', 'field'])].copy()
    if a.us_filter == 'ranked':
        S = S[(S['cohort'] != 'us') | (S['ranked'] == True)]  # noqa: E712
    D = D[D['set'].isin(['us', 'field'])]
    X, D = side_game_rates(S, D)
    # newborn deaths per 100 births (all newborn deaths, any cause)
    nbk = D[D['nb']].groupby(['set', 'game', 'side']).size().rename('n_newborn_any')
    X = X.set_index(['set', 'game', 'side']).join(nbk).fillna({'n_newborn_any': 0}).reset_index()
    k = 1000 / X['dt'].clip(lower=1)
    rate_cols = [c for c in X.columns if c.startswith('n_') or c.startswith('len_')]
    for c in rate_cols:
        X[c + '_per1k'] = X[c] * k
    X['pearls_per100dt'] = 100 * X['pearls@500'] / X['dt'].clip(lower=1)
    X['pearls_per100dt_r100'] = 100 * X['pearls@100'] / X['dt100'].clip(lower=1)
    X['moves_per_pearl'] = X['steps'] / X['pearls@500'].clip(lower=1)
    X['newborn_per100births'] = 100 * X['n_newborn_any'] / X['births'].where(X['births'] > 0)
    X['behind100'] = (X['total100'] < X['opp_total100']).astype(float)
    X['total100_share'] = X['total100'] / (X['total100'] + X['opp_total100']).clip(lower=1)
    X['stationary_per1k'] = X['stationary'] * k
    X['oscillation_per1k'] = X['oscillation'] * k
    X['transit_deaths_per100'] = 100 * X['transit_deaths'] / X['transits'].where(X['transits'] > 0)
    X['rays_per_dt'] = X['sonar'] / X['dt'].clip(lower=1)
    X['corpse_ally_share'] = X['corpse_ally'] / X['pearls@500'].clip(lower=1)
    # band-specific denominators
    for i, rb in enumerate(RBL):
        X[f'dt_{rb}'] = sum(X[f'dt_rb{i}_lb{j}'] for j in range(4))
    for j, lb in enumerate(LBL):
        X[f'dt_{lb}'] = sum(X[f'dt_rb{i}_lb{j}'] for i in range(4))
    us, fld = X[X['cohort'] == 'us'], X[X['cohort'] != 'us']
    top = X[X['cohort'] == 'top10']
    general = [('pearls@50', 1), ('pearls@100', 1), ('pearls@150', 1), ('pearls@250', 1), ('units100', 1), ('total100', 1),
               ('births@100', 1), ('pearls_per100dt', 1), ('pearls_per100dt_r100', 1), ('moves_per_pearl', 0),
               ('newborn_per100births', 0), ('total100_share', 1), ('behind100', 0), ('stationary_per1k', 0),
               ('oscillation_per1k', 0), ('transits', None), ('transit_deaths_per100', 0), ('first_split', None),
               ('last_split', None), ('rays_per_dt', None), ('corpse_ally_share', None), ('tle', 0), ('won', 1)]
    literal = [(f'n_{c}_per1k', 0) for c in CLASSES] + [(f'len_{c}_per1k', 0) for c in CLASSES] + \
              [(f'n_ctx_{n}_per1k', 0) for n in CTX.values()] + [(f'len_ctx_{n}_per1k', 0) for n in CTX.values()] + \
              [('n_all_per1k', 0), ('len_all_per1k', 0), ('n_avoidable_per1k', 0)]
    cards = {}
    maps = sorted(us['map'].unique())
    for mp in maps + ['ALL']:
        u = us if mp == 'ALL' else us[us['map'] == mp]
        f = fld if mp == 'ALL' else fld[fld['map'] == mp]
        t = top if mp == 'ALL' else top[top['map'] == mp]
        card = dict(n_us=int(len(u)), n_field=int(len(f)), n_top10=int(len(t)), literal={}, general={}, bands={}, ctx_x_class={})
        for col, hb in literal:
            # pooled rate = sum(count)/sum(dt); percentile on per-side-game rates (map-matched for ALL)
            base = col[:-6]
            pooled = lambda df: float(1000 * df[base].sum() / max(df['dt'].sum(), 1))
            if mp == 'ALL':
                pc = float(np.nanmean([pct_vs(fld[fld['map'] == m][col], us[us['map'] == m][col], False) for m in maps]))
            else:
                pc = pct_vs(f[col], u[col], False)
            card['literal'][col] = dict(us=pooled(u), field=pooled(f), top10=pooled(t), excess_top10=pooled(u) - pooled(t),
                                        excess_field=pooled(u) - pooled(f), pct=pc)
        for col, hb in general:
            med = lambda df: float(df[col].median()) if len(df) else float('nan')
            ent = dict(us=med(u), field=med(f), top10=med(t))
            if col.startswith('pearls@') or col in ('units100', 'total100', 'births@100'):
                ent['ratio_field'] = ent['us'] / ent['field'] if ent['field'] else float('nan')
                ent['ratio_top10'] = ent['us'] / ent['top10'] if ent['top10'] else float('nan')
            if col in ('behind100', 'won', 'tle'):
                ent = dict(us=float(u[col].mean()), field=float(f[col].mean()), top10=float(t[col].mean()))
            if hb is not None:
                if mp == 'ALL':
                    ent['pct'] = float(np.nanmean([pct_vs(fld[fld['map'] == m][col], us[us['map'] == m][col], bool(hb)) for m in maps]))
                else:
                    ent['pct'] = pct_vs(f[col], u[col], bool(hb))
            card['general'][col] = ent
        # first-behind among games behind at r100
        ub = u[u['behind100'] == 1]
        card['general']['first_behind_round_med'] = dict(us=float(ub['first_behind'].median()) if len(ub) else None,
                                                        field=float(f[f['behind100'] == 1]['first_behind'].median()))
        # class x round band and class x length band (pooled per 1k dragon-turns in that band)
        uD = D[(D['cohort'] == 'us') & (True if mp == 'ALL' else D['map'] == mp)]
        fD = D[(D['cohort'] != 'us') & (True if mp == 'ALL' else D['map'] == mp)]
        if a.us_filter == 'ranked':
            keep = set(u['game'])
            uD = uD[uD['game'].isin(keep)]
        for bname, labels, col in (('round', RBL, 'rb'), ('length', LBL, 'lb')):
            tab = {}
            for lab in labels:
                du, df_ = u[f'dt_{lab}'].sum(), f[f'dt_{lab}'].sum()
                row = {}
                for c in CLASSES[:6]:
                    nu = int(((uD[col] == lab) & (uD['cls'] == c)).sum())
                    nf = int(((fD[col] == lab) & (fD['cls'] == c)).sum())
                    row[c] = dict(us=1000 * nu / max(du, 1), field=1000 * nf / max(df_, 1), n_us=nu)
                tab[lab] = dict(dt_us=int(du), dt_field=int(df_), rates=row)
            card['bands'][bname] = tab
        for kx, name in CTX.items():
            row = {}
            for c in CLASSES[:6]:
                nu = int((uD[kx].astype(bool) & (uD['cls'] == c)).sum())
                nf = int((fD[kx].astype(bool) & (fD['cls'] == c)).sum())
                row[c] = dict(us=1000 * nu / max(u['dt'].sum(), 1), field=1000 * nf / max(f['dt'].sum(), 1), n_us=nu)
            card['ctx_x_class'][name] = row
        # seat / spawn asymmetry
        if mp != 'ALL':
            hs = sorted(X[X['map'] == mp]['map_hash'].unique())
            def spawn(df):
                return [('P' if (s == 'A') == (h == hs[0]) else 'Q') for s, h in zip(df['side'], df['map_hash'])]
            u2, f2 = u.assign(spawn=spawn(u)), f.assign(spawn=spawn(f))
            card['seat'] = {sp: dict(us_win=float(u2[u2['spawn'] == sp]['won'].mean()) if (u2['spawn'] == sp).any() else None,
                                     n_us=int((u2['spawn'] == sp).sum()),
                                     field_win=float(f2[f2['spawn'] == sp]['won'].mean())) for sp in ('P', 'Q')}
        cards[mp] = card
    out = dict(us_filter=a.us_filter, n_side_games=dict(us=int(len(us)), field=int(len(fld)), top10=int(len(top))),
               definitions=__doc__, cards=cards)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1, default=lambda o: None if o != o else o)
    X.to_parquet(AGG / f'sidegame_rates_{a.us_filter}.parquet')
    print('wrote', a.out)


if __name__ == '__main__':
    main()
