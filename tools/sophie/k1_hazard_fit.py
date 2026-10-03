"""K-1 Part 2: cell-level hazard models (field and ours) with leave-one-map-out validation, and Poisson trees
that propose signatures.

    python tools/sophie/k1_hazard_fit.py glm   -> build/sophie/agg2/glm.json
    python tools/sophie/k1_hazard_fit.py trees -> build/sophie/agg2/trees.json

Unit: a cell of a map, per cohort; y = deaths of a class with the head on that cell, exposure = head-turns on it.
Field = every non-team-7 side (top10 included); ours = team 7 live (corpus); local = the V06 lane base (renoir-00-base)
on pool + gen maps (used only for the gen-map transfer check).
"""
import json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import PoissonRegressor
from sklearn.tree import DecisionTreeRegressor

REPO = Path(os.environ.get('K1_REPO', Path(__file__).resolve().parents[2]))
AGG = REPO / os.environ.get('K1_AGG', 'build/sophie/agg2')
CLASSES = ['wall', 'self', 'ally_body', 'h2h_ally', 'h2h_enemy', 'trapped', 'newborn', 'transit', 'crowd23', 'fight']
STRUCT = ['deg1', 'deg2', 'deg3', 'kelp0', 'kelp1', 'dead_any', 'dead_log', 'portal2', 'portal5', 'land_low', 'bed3', 'bed6',
          'is_bed', 'cluster_log', 'spawn_log', 'wrap', 'region_small', 'region_log', 'reach5']
SCALAR = ['tiles_log', 'kelp_share', 'portal_present', 'cap_per_tile', 'contact_n', 'no_contact']
TERRAIN = {'Prisoners Dilemma 10': 'Prisoners Dilemma'}


def base_name(m):
    m = m.replace(' tr', '')
    return TERRAIN.get(m, m)


def load(cohorts):
    R = pd.read_parquet(AGG / 'cellrows.parquet')
    M = pd.read_parquet(AGG / 'mapfeat.parquet').drop_duplicates('map_hash').set_index('map_hash')
    R = R[R['cohort'].isin(cohorts)].copy()
    R['cohort'] = R['cohort'].replace({'top10': 'field'})
    R['mapkey'] = R['map']
    num = [c for c in R.columns if c.startswith('n_') or c.startswith('len_')] + ['expo']
    feats = ['deg', 'kelp_d', 'dead', 'portal_d', 'land', 'bed3', 'bed6', 'bed_d', 'cluster', 'spawn_d', 'wrap', 'region', 'reach5', 'is_bed']
    R = R.join(M[['tiles', 'kelp_share', 'portal_cells', 'bed_capacity', 'contact']], on='map_hash')
    g = R.groupby(['cohort', 'mapkey', 'x', 'y'])
    A = g[num].sum().join(g[feats + ['tiles', 'kelp_share', 'portal_cells', 'bed_capacity', 'contact']].first()).reset_index()
    A['terrain'] = A['mapkey'].map(base_name)
    return A


def design(A):
    X = pd.DataFrame(index=A.index)
    for k in (1, 2, 3):
        X[f'deg{k}'] = (A['deg'] == k).astype(float)
    X['kelp0'] = (A['kelp_d'] == 0).astype(float)
    X['kelp1'] = (A['kelp_d'] == 1).astype(float)
    X['dead_any'] = (A['dead'] > 0).astype(float)
    X['dead_log'] = np.log1p(A['dead'])
    X['portal2'] = (A['portal_d'] <= 2).astype(float)
    X['portal5'] = ((A['portal_d'] > 2) & (A['portal_d'] <= 5)).astype(float)
    X['land_low'] = ((A['land'] <= 3) & (A['portal_d'] <= 5)).astype(float)
    X['bed3'] = A['bed3']
    X['bed6'] = A['bed6']
    X['is_bed'] = A['is_bed']
    X['cluster_log'] = np.log1p(A['cluster'])
    X['spawn_log'] = np.log1p(A['spawn_d'].clip(upper=60))
    X['wrap'] = A['wrap']
    X['region_small'] = (A['region'] < 20).astype(float)
    X['region_log'] = np.log1p(A['region'])
    X['reach5'] = A['reach5'] / 61
    X['tiles_log'] = np.log(A['tiles'])
    X['kelp_share'] = A['kelp_share']
    X['portal_present'] = (A['portal_cells'] > 0).astype(float)
    X['cap_per_tile'] = A['bed_capacity'] / A['tiles']
    X['contact_n'] = A['contact'].clip(upper=60) / 60
    X['no_contact'] = (A['contact'] >= 999).astype(float)
    return X


def fit_pois(X, y, w, alpha=1e-3):
    mu, sd = X.mean(), X.std().replace(0, 1)
    m = PoissonRegressor(alpha=alpha, max_iter=1000)
    m.fit((X - mu) / sd, y, sample_weight=w)
    return m, mu, sd


def pred(model, X):
    m, mu, sd = model
    return m.predict((X - mu) / sd)


def dev(y_count, mu_count):
    y, mu = np.asarray(y_count, float), np.clip(np.asarray(mu_count, float), 1e-12, None)
    t = np.where(y > 0, y * np.log(np.where(y > 0, y, 1) / mu), 0.0)
    return 2 * np.sum(t - (y - mu))


def glm(out):
    A = load(['us', 'field', 'top10'])
    A = A[A['expo'] > 0]
    X = design(A)
    cols = STRUCT + SCALAR
    res = {}
    for c in CLASSES:
        yc = f'n_{c}'
        r = dict(field={}, us={}, us_vs_field={})
        for coh in ('field', 'us'):
            s = A['cohort'] == coh
            Xs, ys, ws = X[s][cols], (A[s][yc] / A[s]['expo']), A[s]['expo']
            full = fit_pois(Xs, ys, ws)
            coef = dict(zip(cols, (full[0].coef_ / full[2].values).round(4)))       # per raw unit
            r[coh]['coef_per_unit'] = coef
            r[coh]['rate_ratio_per_sd'] = dict(zip(cols, np.exp(full[0].coef_).round(3)))
            # leave-one-terrain-out
            folds = {}
            for tm in sorted(A[s]['terrain'].unique()):
                tr, te = s & (A['terrain'] != tm), s & (A['terrain'] == tm)
                mdl = fit_pois(X[tr][cols], A[tr][yc] / A[tr]['expo'], A[tr]['expo'])
                mu = pred(mdl, X[te][cols]) * A[te]['expo']
                y = A[te][yc]
                flat_pool = A[tr][yc].sum() / A[tr]['expo'].sum() * A[te]['expo']
                flat_map = y.sum() / A[te]['expo'].sum() * A[te]['expo']
                mu_cal = mu * (y.sum() / max(mu.sum(), 1e-9))
                d_null_a, d_mod_a = dev(y, flat_pool), dev(y, mu)
                d_null_w, d_mod_w = dev(y, flat_map), dev(y, mu_cal)
                folds[tm] = dict(n=int(y.sum()), D2_across=1 - d_mod_a / d_null_a if d_null_a > 0 else None,
                                 D2_within=1 - d_mod_w / d_null_w if d_null_w > 0 else None,
                                 pred_over_obs=float(mu.sum() / max(y.sum(), 1)))
            r[coh]['lomo'] = folds
            r[coh]['lomo_median_D2_within'] = float(np.nanmedian([f['D2_within'] for f in folds.values() if f['D2_within'] is not None]))
            r[coh]['lomo_median_D2_across'] = float(np.nanmedian([f['D2_across'] for f in folds.values() if f['D2_across'] is not None]))
        # ours relative to the field: offset = field model's prediction (structure only, fitted on field cells)
        sF, sU = A['cohort'] == 'field', A['cohort'] == 'us'
        fm = fit_pois(X[sF][cols], A[sF][yc] / A[sF]['expo'], A[sF]['expo'])
        base = np.clip(pred(fm, X[sU][cols]), 1e-9, None)
        # regress our/field ratio: y/expo/base with weight expo*base (Poisson with offset log(base))
        rel = fit_pois(X[sU][STRUCT], A[sU][yc] / A[sU]['expo'] / base, A[sU]['expo'] * base)
        r['us_vs_field'] = dict(overall_ratio=float(A[sU][yc].sum() / (base * A[sU]['expo']).sum()),
                                coef_per_unit=dict(zip(STRUCT, (rel[0].coef_ / rel[2].values).round(4))))
        res[c] = r
        print(c, 'field D2 within/across', round(r['field']['lomo_median_D2_within'], 3), round(r['field']['lomo_median_D2_across'], 3),
              '| us', round(r['us']['lomo_median_D2_within'], 3), round(r['us']['lomo_median_D2_across'], 3),
              '| us/field', round(r['us_vs_field']['overall_ratio'], 2), flush=True)
    json.dump(res, open(out, 'w'), indent=1)


if __name__ == '__main__':
    if sys.argv[1] == 'glm':
        glm(AGG / 'glm.json')


RAW = ['deg', 'kelp_d', 'dead', 'portal_d', 'land', 'bed3', 'bed6', 'is_bed', 'cluster', 'spawn_d', 'region', 'reach5']


def leaf_rules(tree, names):
    t = tree.tree_
    out = {}

    def rec(node, conds):
        if t.children_left[node] == -1:
            out[node] = conds
            return
        f, th = names[t.feature[node]], t.threshold[node]
        rec(t.children_left[node], conds + [(f, '<=', th)])
        rec(t.children_right[node], conds + [(f, '>', th)])
    rec(0, [])
    return out


def simplify(conds):
    lo, hi = {}, {}
    for f, op, th in conds:
        if op == '<=':
            hi[f] = min(hi.get(f, np.inf), th)
        else:
            lo[f] = max(lo.get(f, -np.inf), th)
    parts = []
    for f in sorted(set(lo) | set(hi)):
        a, b = lo.get(f), hi.get(f)
        if a is not None and b is not None:
            parts.append(f'{a:g} < {f} <= {b:g}')
        elif a is not None:
            parts.append(f'{f} > {a:g}')
        else:
            parts.append(f'{f} <= {b:g}')
    return ' & '.join(parts)


def mask_of(A, conds):
    m = pd.Series(True, index=A.index)
    for f, op, th in conds:
        m &= (A[f] <= th) if op == '<=' else (A[f] > th)
    return m


def trees(out, depth=3):
    A = load(['us', 'field', 'top10'])
    A = A[A['expo'] > 0]
    res = {}
    for c in ['wall', 'self', 'ally_body', 'h2h_ally', 'trapped', 'newborn', 'transit', 'crowd23', 'fight']:
        yc = f'n_{c}'
        F, U = A[A['cohort'] == 'field'], A[A['cohort'] == 'us']
        tr = DecisionTreeRegressor(criterion='poisson', max_depth=depth, min_samples_leaf=150, random_state=0)
        tr.fit(F[RAW], F[yc] / F['expo'], sample_weight=F['expo'])
        rules = leaf_rules(tr, RAW)
        base_f = F[yc].sum() / F['expo'].sum()
        base_u = U[yc].sum() / U['expo'].sum()
        leaves = []
        for node, conds in rules.items():
            mf, mu = mask_of(F, conds), mask_of(U, conds)
            rf = F[mf][yc].sum() / max(F[mf]['expo'].sum(), 1)
            ru = U[mu][yc].sum() / max(U[mu]['expo'].sum(), 1)
            # per-terrain within-map ratio (leaf rate / that map's rate), field and us
            per = {}
            for tm in sorted(F['terrain'].unique()):
                for coh, D_ in (('field', F), ('us', U)):
                    d = D_[D_['terrain'] == tm]
                    mm = mask_of(d, conds)
                    if d['expo'].sum() == 0 or d[mm]['expo'].sum() < 500:
                        continue
                    per.setdefault(tm, {})[coh] = float((d[mm][yc].sum() / d[mm]['expo'].sum()) / (d[yc].sum() / d['expo'].sum()))
                    per[tm][coh + '_expo_share'] = float(d[mm]['expo'].sum() / d['expo'].sum())
                    per[tm][coh + '_death_share'] = float(d[mm][yc].sum() / max(d[yc].sum(), 1))
            leaves.append(dict(rule=simplify(conds), conds=[[f, o, float(t)] for f, o, t in conds],
                               field_rate_per1k=1000 * rf, us_rate_per1k=1000 * ru, field_ratio=rf / base_f, us_ratio=ru / base_u,
                               us_over_field=ru / rf if rf else None,
                               field_expo_share=float(F[mf]['expo'].sum() / F['expo'].sum()),
                               field_death_share=float(F[mf][yc].sum() / F[yc].sum()),
                               us_expo_share=float(U[mu]['expo'].sum() / U['expo'].sum()),
                               us_death_share=float(U[mu][yc].sum() / max(U[yc].sum(), 1)),
                               per_terrain=per,
                               maps_ratio_gt1_field=sum(1 for v in per.values() if v.get('field', 0) > 1),
                               maps_ratio_gt1_us=sum(1 for v in per.values() if v.get('us', 0) > 1), n_maps=len(per)))
        leaves.sort(key=lambda l: -l['field_ratio'])
        # leave-one-terrain-out: refit the tree without the map; the top leaf's ratio on the held-out map
        lomo = {}
        for tm in sorted(F['terrain'].unique()):
            Ft = F[F['terrain'] != tm]
            t2 = DecisionTreeRegressor(criterion='poisson', max_depth=depth, min_samples_leaf=150, random_state=0)
            t2.fit(Ft[RAW], Ft[yc] / Ft['expo'], sample_weight=Ft['expo'])
            r2 = leaf_rules(t2, RAW)
            best = max(r2.values(), key=lambda cs: (Ft[mask_of(Ft, cs)][yc].sum() / max(Ft[mask_of(Ft, cs)]['expo'].sum(), 1)))
            out_ = {}
            for coh, D_ in (('field', F), ('us', U)):
                d = D_[D_['terrain'] == tm]
                mm = mask_of(d, best)
                if d[mm]['expo'].sum() >= 500 and d[yc].sum() > 0:
                    out_[coh] = float((d[mm][yc].sum() / d[mm]['expo'].sum()) / (d[yc].sum() / d['expo'].sum()))
            lomo[tm] = dict(rule=simplify(best), **out_)
        res[c] = dict(base_field_per1k=1000 * base_f, base_us_per1k=1000 * base_u, leaves=leaves, lomo_top_leaf=lomo)
        top = leaves[0]
        print(f"{c:10s} top: {top['rule']:55s} field x{top['field_ratio']:.1f} us x{top['us_ratio']:.1f} us/field {top['us_over_field'] or 0:.2f} "
              f"expo {top['field_expo_share']:.3f} deaths {top['field_death_share']:.2f} maps>1 f{top['maps_ratio_gt1_field']}/u{top['maps_ratio_gt1_us']}/{top['n_maps']}", flush=True)
    json.dump(res, open(out, 'w'), indent=1)


if __name__ == '__main__' and sys.argv[1] == 'trees':
    trees(AGG / 'trees.json')
