"""Zoo vs field comparison (F1 → A2): raw pooled coverage, sampling impact, hierarchical team effects, Elo control.

python -m tools.analysis.features.compare --zoo build/zoo/z1/features --zoo-report build/zoo/z1/report \
    --field DIR[,DIR…] --index public_replays/corpus/index.jsonl --ladder public_replays/corpus/ladder --out OUT

Units: side-game (raw), team (hierarchical: shrunken per-team means of within-map z-scores), game pairs for Elo models.
Field = every corpus side-game whose team is not ours (team 7); ours = team 7's side-games (live), kept separate.
Zoo = seed-1 side-games of the local panel. Phases for both come from the zoo-fitted HMM (hmm.json), so they mean the same.
"""
import argparse, glob, json, math, os
from bisect import bisect_right
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .registry import REGISTRY
from . import phases as ph
from .report import phase_conditioned, auc, theme, CAT, MAP_ORDER, inline_plotly, _rgba, LEADING

OURS = 7
EXCLUDE_FAMILIES = {'compute', 'context'}
ZOO_C, WIN_C, LOSS_C = '#8a8986', '#2a78d6', '#eb6834'


# ---------------------------------------------------------------- loading
def load_runs(dirs, name):
    parts = [pd.read_parquet(os.path.join(d, name + '.parquet')) for d in dirs if os.path.exists(os.path.join(d, name + '.parquet'))]
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def ladder_lookup(ladder_dir):
    snaps = []
    for f in sorted(glob.glob(os.path.join(ladder_dir, '*.json'))):
        stamp = datetime.strptime(os.path.basename(f)[:15], '%Y%m%dT%H%M%S').replace(tzinfo=timezone.utc).timestamp()
        rows = json.load(open(f))
        snaps.append((stamp, {r['id']: (r['elo'], r['rank'], r.get('name', '')) for r in rows}))
    times = [s[0] for s in snaps]

    def at(team, iso):
        t = datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp() if iso else times[-1]
        k = max(bisect_right(times, t) - 1, 0)          # latest snapshot at or before the game (earliest if none)
        for j in list(range(k, -1, -1)) + list(range(k + 1, len(snaps))):
            if team in snaps[j][1]:
                return snaps[j][1][team]
        return (np.nan, np.nan, '')
    latest = snaps[-1][1] if snaps else {}
    return at, latest


def attach_meta(F, index_path, ladder_dir):
    idx = {}
    for line in open(index_path):
        r = json.loads(line)
        idx[str(r['game_id'])] = r
    at, latest = ladder_lookup(ladder_dir)
    rows = []
    for g, s in zip(F['game'].astype(str), F['side']):
        r = idx.get(g)
        if r is None:
            rows.append({})
            continue
        me, op = (r['team_a'], r['team_b']) if s == 'A' else (r['team_b'], r['team_a'])
        e1, k1, n1 = at(me, r.get('finished_at'))
        e2, k2, n2 = at(op, r.get('finished_at'))
        rows.append(dict(team=me, opp_team=op, elo=e1, opp_elo=e2, rank_at=k1, team_name=n1, ranked=r.get('ranked'),
                         autoscrim_window=r.get('autoscrim_window'), finished_at=r.get('finished_at'), watch_team=r.get('watch_team')))
    M = pd.DataFrame(rows, index=F.index)
    return pd.concat([F, M], axis=1), latest


def zoo_phases(S, hmm):
    scale = {k: tuple(v) for k, v in hmm['scale'].items()}
    model = dict(mu=np.array(hmm['mu']), var=np.array(hmm['var']), A=np.array(hmm['A']), pi=np.array(hmm['pi']))
    out = []
    for (g, s), d in S.groupby(['game', 'side']):
        sig = ph.signals(d.sort_values('round'))
        X = ph.binned(sig, scale)
        row = dict(game=g, side=s)
        if X is not None:
            _, t1, t2 = ph.decode_hmm(model, ph.hmm_view(X))
            row.update(phase_t1=t1, phase_t2=t2)
        out.append(row)
    return pd.DataFrame(out)


# ---------------------------------------------------------------- statistics
def zscore_by_map(df, feats, ref):
    """z-score every row's features using the per-map mean/sd of the reference frame (the field)"""
    Z = pd.DataFrame(index=df.index, columns=feats, dtype=float)
    for mp, idx in df.groupby('map').groups.items():
        r = ref[ref['map'] == mp][feats].astype(float)
        mu, sd = r.mean(), r.std().replace(0, np.nan)
        Z.loc[idx] = ((df.loc[idx, feats].astype(float) - mu) / sd).values
    return Z


def coverage(field, zoo, feats, weights=None, min_n=30):
    """per feature: share of field side-games outside the zoo's per-map 5-95% range (each game vs its own map)"""
    rows = []
    w_all = weights if weights is not None else pd.Series(1.0, index=field.index)
    for f in feats:
        lo_hi = zoo.groupby('map')[f].quantile([0.05, 0.95]).unstack()
        med_z = zoo.groupby('map')[f].median()
        iqr_z = (zoo.groupby('map')[f].quantile(0.75) - zoo.groupby('map')[f].quantile(0.25))
        x = field[f].astype(float)
        m = x.notna() & field['map'].isin(lo_hi.index)
        if m.sum() < min_n:
            continue
        lo = field.loc[m, 'map'].map(lo_hi[0.05])
        hi = field.loc[m, 'map'].map(lo_hi[0.95])
        below, above = (x[m] < lo).astype(float), (x[m] > hi).astype(float)
        w = w_all[m]
        res = field.loc[m, 'result']
        wwin = w * (res == 'win')
        shift = []
        for mp, g in field[m].groupby('map'):
            if iqr_z.get(mp, 0) and iqr_z[mp] > 0:
                shift.append(((g[f].median() - med_z[mp]) / iqr_z[mp], len(g)))
        rows.append(dict(feature=f, family=REGISTRY.get(f, {}).get('family', 'phase' if f.startswith(('opening_', 'economy_', 'crown_', 'phase')) else 'derived'),
                         n=int(m.sum()), below=float((below * w).sum() / w.sum()), above=float((above * w).sum() / w.sum()),
                         outside=float(((below + above) * w).sum() / w.sum()),
                         outside_win=float(((below + above) * wwin).sum() / wwin.sum()) if wwin.sum() else np.nan,
                         median_shift_iqr=float(sum(a * n for a, n in shift) / sum(n for _, n in shift)) if shift else np.nan))
    return pd.DataFrame(rows)


def team_effects(Zf, teams, min_n=8):
    """empirical-Bayes shrunken team means of within-map z; returns effects (team x feature) and tau2/sigma2 per feature"""
    eff, info = {}, {}
    for f in Zf.columns:
        d = pd.DataFrame(dict(z=Zf[f].astype(float), team=teams)).dropna()
        g = d.groupby('team')['z']
        n, mu, var = g.size(), g.mean(), g.var(ddof=1)
        keep = n >= min_n
        if keep.sum() < 5:
            continue
        sigma2 = float((var[keep] * (n[keep] - 1)).sum() / (n[keep] - 1).sum())
        grand = float(d['z'].mean())
        tau2 = max(float(((mu[keep] - grand) ** 2).mean() - (sigma2 / n[keep]).mean()), 1e-6)
        shrink = tau2 / (tau2 + sigma2 / n)
        eff[f] = (grand + (mu - grand) * shrink)[keep]
        info[f] = dict(tau2=tau2, sigma2=sigma2, icc_team=tau2 / (tau2 + sigma2), teams=int(keep.sum()))
    return pd.DataFrame(eff), pd.DataFrame(info).T


def beyond_elo(df, feats, Z):
    """logit P(win) = Elo expected-score logit (offset) + beta * z(feature); side-games with both ratings known"""
    d = df[(df['result'] != 'draw') & df['elo'].notna() & df['opp_elo'].notna()]
    off = ((d['elo'] - d['opp_elo']) * math.log(10) / 400).to_numpy(float)
    y = (d['result'] == 'win').to_numpy(float)
    ll0 = float(np.sum(y * off - np.log1p(np.exp(off))))
    rows = []
    for f in feats:
        z = np.nan_to_num(Z.loc[d.index, f].to_numpy(float))
        if np.std(z) == 0:
            continue
        b = 0.0
        for _ in range(30):
            p = 1 / (1 + np.exp(-(off + b * z)))
            b = float(np.clip(b + np.sum((y - p) * z) / (np.sum(p * (1 - p) * z * z) + 1e-9), -20, 20))
        eta = off + b * z
        ll = float(np.sum(y * eta - np.log1p(np.exp(eta))))
        rows.append(dict(feature=f, beta_elo=b, lr_chi2_elo=2 * (ll - ll0), n=len(d)))
    return pd.DataFrame(rows), float(np.mean((1 / (1 + np.exp(-off)) > 0.5) == (y == 1)))


def raw_auc(df, feats):
    d = df[df['result'] != 'draw']
    out = {}
    for f in feats:
        per = [(auc(g[f].astype(float).to_numpy(), (g['result'] == 'win').astype(int).to_numpy()), len(g)) for _, g in d.groupby('map')]
        per = [(a, n) for a, n in per if a == a]
        out[f] = sum(a * n for a, n in per) / sum(n for _, n in per) if per else np.nan
    return pd.Series(out)


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--zoo', required=True)
    ap.add_argument('--zoo-report', required=True)
    ap.add_argument('--field', required=True, help='comma list of extract output dirs (globs allowed)')
    ap.add_argument('--index', required=True)
    ap.add_argument('--ladder', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--notes')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    dirs = sorted(sum((glob.glob(x) for x in a.field.split(',')), []))
    hmm = json.load(open(os.path.join(a.zoo_report, 'hmm.json')))
    # zoo
    Z0 = pd.read_parquet(os.path.join(a.zoo, 'features.parquet'))
    Z0 = Z0[Z0['game'].str.startswith('s1__')].copy()
    Szoo = pd.read_parquet(os.path.join(a.zoo, 'series.parquet'))
    Szoo = Szoo[Szoo['game'].isin(Z0['game'])]
    Z0 = Z0.merge(zoo_phases(Szoo, hmm), on=['game', 'side'], how='left')
    Z0 = phase_conditioned(Z0, Szoo)
    # field
    F0 = load_runs(dirs, 'features')
    Sf = load_runs(dirs, 'series')
    F0['game'] = F0['game'].astype(str)
    Sf['game'] = Sf['game'].astype(str)
    F0 = F0.merge(zoo_phases(Sf, hmm), on=['game', 'side'], how='left')
    F0 = phase_conditioned(F0, Sf)
    F0, latest = attach_meta(F0, a.index, a.ladder)
    if 'dragons_start' in F0:   # the 10-dragon Prisoners Dilemma is a different game; the zoo only has the 6-dragon one
        pd10 = (F0['map'] == 'Prisoners Dilemma') & (F0['dragons_start'] == 10)
        F0.loc[pd10, 'map'] = 'Prisoners Dilemma 10'
    for D in (Z0, F0):
        D['splits_0_100'] = D['splits_0_50'].fillna(0) + D['splits_50_100'].fillna(0)
    ours = F0[F0['team'] == OURS].copy()
    field = F0[(F0['team'] != OURS) & (F0['opp_team'] != OURS) & F0['team'].notna()].copy()
    feats = [c for c in Z0.columns if c in F0.columns and pd.api.types.is_numeric_dtype(Z0[c]) and pd.api.types.is_numeric_dtype(F0[c])
             and (c in REGISTRY or c.startswith(('opening_', 'economy_', 'crown_')) or c == 'splits_0_100')
             and REGISTRY.get(c, {}).get('family') not in EXCLUDE_FAMILIES]
    # sampling: games per team, weights
    per_team = field.groupby('team').size()
    w_team = 1.0 / field['team'].map(per_team)
    top_ids = [t for t, v in sorted(latest.items(), key=lambda kv: kv[1][1]) if t != OURS][:10]
    COV = coverage(field, Z0, feats)
    COVw = coverage(field, Z0, feats, w_team).set_index('feature')[['outside', 'outside_win', 'below', 'above']].add_suffix('_teamw')
    COVt = coverage(field[field['team'].isin(top_ids)], Z0, feats).set_index('feature')[['outside', 'below', 'above']].add_suffix('_top10')
    COV = COV.set_index('feature').join(COVw).join(COVt).reset_index()
    # hierarchical
    Zf = zscore_by_map(field, feats, field)
    Zz = zscore_by_map(Z0, feats, field)
    TE, TI = team_effects(Zf, field['team'])
    BE = pd.DataFrame({f: Zz[f].groupby(Z0['bot']).mean() for f in feats if f in TE})   # zoo bots: ~140 side-games each, shrinkage negligible
    hier = []
    for f in TE.columns:
        lo, hi = BE[f].min(), BE[f].max()
        te = TE[f].dropna()
        top = te[te.index.isin(top_ids)]
        hier.append(dict(feature=f, teams=len(te), team_outside_zoo_bots=float(((te < lo) | (te > hi)).mean()),
                         top10_outside=float(((top < lo) | (top > hi)).mean()) if len(top) else np.nan,
                         icc_team=float(TI.loc[f, 'icc_team']), zoo_bot_range=float(hi - lo), team_sd=float(te.std())))
    HIER = pd.DataFrame(hier)
    COV = COV.merge(HIER, on='feature', how='left')
    # Elo
    BEL, elo_acc = beyond_elo(field, feats, Zf)
    AUCf = raw_auc(field, feats).rename('auc_field')
    zst = pd.read_csv(os.path.join(a.zoo_report, 'strength.csv')).set_index('feature')[['auc_within_map', 'beta_per_sd', 'lr_chi2']]
    team_rating = pd.Series({t: v[0] for t, v in latest.items()})
    elo_corr = {f: TE[f].dropna().rank().corr(team_rating.reindex(TE[f].dropna().index).rank()) for f in TE.columns}
    STR = BEL.set_index('feature').join(AUCf).join(zst.add_prefix('zoo_')).join(pd.Series(elo_corr, name='team_effect_vs_rating_spearman'))
    STR['leading'] = [LEADING(f) for f in STR.index]
    STR = STR.reset_index().rename(columns={'index': 'feature'})
    # save
    COV.to_csv(os.path.join(a.out, 'coverage.csv'), index=False)
    STR.to_csv(os.path.join(a.out, 'field_strength.csv'), index=False)
    TE.to_csv(os.path.join(a.out, 'team_effects.csv'))
    BE.to_csv(os.path.join(a.out, 'zoo_bot_effects.csv'))
    meta = dict(field_side_games=len(field), field_games=int(field['game'].nunique()), teams=int(field['team'].nunique()),
                ours_side_games=len(ours), zoo_side_games=len(Z0), features=len(feats), index_lines=sum(1 for _ in open(a.index)),
                newest_finished=str(field['finished_at'].max()), elo_only_accuracy=elo_acc, top10=top_ids,
                games_per_team_quantiles=per_team.quantile([.5, .9, .99]).to_dict(), max_team_share=float(per_team.max() / per_team.sum()))
    json.dump(meta, open(os.path.join(a.out, 'meta.json'), 'w'), indent=1, default=str)
    html = build_html(a, meta, field, ours, Z0, feats, COV, STR, TE, BE, TI, per_team, latest, top_ids)
    open(os.path.join(a.out, 'compare.html'), 'w', encoding='utf-8').write(html)
    open(os.path.join(a.out, 'compare_inline.html'), 'w', encoding='utf-8').write(inline_plotly(html))
    print(json.dumps(meta, default=str)[:600])


# ---------------------------------------------------------------- report
def build_html(a, meta, field, ours, Z0, feats, COV, STR, TE, BE, TI, per_team, latest, top_ids):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    figs = []

    def add(section, title, caption, fig):
        figs.append((section, title, caption, fig if isinstance(fig, str) else
                     fig.to_html(full_html=False, include_plotlyjs=False, config=dict(displaylogo=False, responsive=True, modeBarButtonsToRemove=['toImage']))))

    name = lambda t: f"{t} {latest.get(t, (0, 0, ''))[2]}".strip()
    maps = [m for m in MAP_ORDER if m in set(field['map'])]
    # --- sampling
    pt = per_team.sort_values(ascending=False)
    fig = go.Figure(go.Bar(x=[name(t) for t in pt.index], y=pt.values, marker_color=CAT[0],
                           customdata=[latest.get(t, (np.nan,))[0] for t in pt.index],
                           hovertemplate='%{x}: %{y} side-games, rating %{customdata}<extra></extra>'))
    fig.update_xaxes(showticklabels=False, title='teams, most-sampled first')
    fig.update_yaxes(title='side-games in the corpus')
    add('Sampling', 'How unevenly the corpus samples teams', f"Unit: side-game, field only (team {OURS} excluded). {meta['teams']} teams; median "
        f"{meta['games_per_team_quantiles'][0.5]:.0f} side-games per team, 90th percentile {meta['games_per_team_quantiles'][0.9]:.0f}; the most-sampled team is "
        f"{meta['max_team_share']:.1%} of all side-games. The watch list decides this, not the game.", theme(fig, 320))
    d = COV.dropna(subset=['outside', 'outside_teamw'])
    fig = go.Figure(go.Scatter(x=d['outside'], y=d['outside_teamw'], mode='markers', marker=dict(size=8, color=CAT[0], opacity=.7),
                               customdata=np.stack([d['feature'], d['icc_team'].fillna(np.nan)], 1),
                               hovertemplate='<b>%{customdata[0]}</b><br>raw outside %{x:.0%} · team-weighted %{y:.0%}<br>team ICC %{customdata[1]:.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', line=dict(color='#8a8986', dash='dot', width=1), hoverinfo='skip', showlegend=False))
    fig.update_xaxes(title='share of field side-games outside the zoo 5–95% (raw)', tickformat='.0%', range=[0, 1])
    fig.update_yaxes(title='same, each team weighted equally', tickformat='.0%', range=[0, 1])
    diff = (d['outside_teamw'] - d['outside']).abs()
    add('Sampling', 'Does the uneven sampling change the answer? Raw vs team-weighted coverage failure',
        f"Unit: feature. Each dot is one feature; on the diagonal the sampling makes no difference. Median absolute difference "
        f"{diff.median():.1%}, 90th percentile {diff.quantile(.9):.1%}. Team ICC (hover) is the share of within-map variance that sits between teams: "
        f"median {COV['icc_team'].median():.2f}.", theme(fig, 460))
    # --- coverage ranking
    top = COV.sort_values('outside', ascending=False).head(35).iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=top['feature'], x=top['below'], name='field below zoo 5%', orientation='h', marker_color=CAT[1]))
    fig.add_trace(go.Bar(y=top['feature'], x=top['above'], name='field above zoo 95%', orientation='h', marker_color=CAT[0]))
    fig.add_trace(go.Scatter(y=top['feature'], x=top['outside_win'], mode='markers', name='winners only', marker=dict(symbol='line-ns-open', size=14, color='#15191b', line=dict(width=2))))
    fig.add_trace(go.Scatter(y=top['feature'], x=top['outside_teamw'], mode='markers', name='team-weighted', marker=dict(symbol='diamond', size=8, color=CAT[3])))
    fig.update_layout(barmode='stack')
    fig.update_xaxes(tickformat='.0%', title='share of field side-games outside the zoo range for the same map')
    add('Coverage', 'Where the zoo does not cover the field (top 35 features)', 'Unit: field side-game, each compared with the zoo 5–95% range on its '
        'own map (so the map mix cannot create a gap). If the zoo were representative, about 10% would fall outside. Orange = the field is lower '
        'than anything the zoo does, blue = higher.', theme(fig, 900))
    # family summary
    fam = COV.groupby('family')[['outside', 'outside_win', 'outside_teamw', 'team_outside_zoo_bots']].median().sort_values('outside')
    fig = go.Figure([go.Bar(x=fam.index, y=fam[c], name=n, marker_color=CAT[i]) for i, (c, n) in enumerate(
        (('outside', 'side-games (raw)'), ('outside_win', 'winning side-games'), ('outside_teamw', 'team-weighted'), ('team_outside_zoo_bots', 'teams outside the zoo bots\' range')))])
    fig.update_yaxes(tickformat='.0%', title='median over the family\'s features')
    add('Coverage', 'Coverage failure by family', 'Median over features in each family. The last bar is hierarchical: the share of field teams whose '
        'shrunken team effect lies outside the range spanned by our eight bots.', theme(fig, 380))
    # distributions for the worst-covered headline-ish features
    show = [f for f in COV.sort_values('outside', ascending=False)['feature'] if not f.startswith(('units@', 'total@', 'longest@', 'pearls@', 'bed_pearls@', 'births@', 'deaths@', 'kills@'))][:12]
    for f in show:
        fig = go.Figure()
        for lab, D, clr in (('zoo', Z0, ZOO_C), ('field winners', field[field['result'] == 'win'], WIN_C), ('field losers', field[field['result'] == 'loss'], LOSS_C)):
            fig.add_trace(go.Box(x=D['map'], y=D[f], name=lab, marker_color=clr, boxpoints=False))
        fig.update_layout(boxmode='group')
        fig.update_xaxes(categoryorder='array', categoryarray=maps)
        r = COV.set_index('feature').loc[f]
        meta_f = REGISTRY.get(f, dict(unit='', definition=''))
        add('Distributions', f'{f}', f"{meta_f.get('definition', '')} ({meta_f.get('unit', '')}). Outside the zoo range: {r['outside']:.0%} of field side-games "
            f"({r['below']:.0%} below, {r['above']:.0%} above); winners {r['outside_win']:.0%}; teams outside the zoo bots {r['team_outside_zoo_bots']:.0%}.", theme(fig, 360))
    # --- team map (PCA of team effects on a fingerprint set)
    fp = [f for f in ['rays_per_dt', 'ray_refracted_share', 'rays_toward_com_share', 'child_len_median', 'splits_0_100', 'units_share@100', 'territory@100',
                      'top1_share@250', 'sprint_share', 'death_wall_per1k', 'death_h2h_enemy_per1k', 'bed_capture_share', 'seen_share@100',
                      'contact_share_mean', 'density_ratio_mean', 'phase_t1'] if f in TE.columns and f in BE.columns]
    T = TE[fp].dropna()
    B = BE[fp].dropna()
    mu, sd = T.mean(), T.std().replace(0, 1)
    X = ((T - mu) / sd).to_numpy()
    U, Sv, Vt = np.linalg.svd(X - X.mean(0), full_matrices=False)
    PT = (X - X.mean(0)) @ Vt[:2].T
    PB = (((B - mu) / sd).to_numpy() - X.mean(0)) @ Vt[:2].T
    ev = Sv ** 2 / (Sv ** 2).sum()
    nn = []
    for i, t in enumerate(T.index):
        dmin = np.min(np.linalg.norm(((B - mu) / sd).to_numpy() - X[i], axis=1))
        nn.append(dmin)
    nn = pd.Series(nn, index=T.index)
    ratings = [latest.get(t, (np.nan,))[0] for t in T.index]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=PT[:, 0], y=PT[:, 1], mode='markers', name='field teams',
                             marker=dict(size=[6 + 10 * math.sqrt(per_team.get(t, 1) / per_team.max()) for t in T.index], color=ratings,
                                         colorscale=[[0, '#cde2fb'], [1, '#0d366b']], colorbar=dict(title='rating'), line=dict(width=1, color='rgba(255,255,255,.7)')),
                             customdata=np.stack([[name(t) for t in T.index], ratings, [per_team.get(t, 0) for t in T.index], nn.values], 1),
                             hovertemplate='<b>%{customdata[0]}</b><br>rating %{customdata[1]} · %{customdata[2]} side-games<br>distance to nearest zoo bot %{customdata[3]:.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=PB[:, 0], y=PB[:, 1], mode='markers+text', name='zoo bots', text=[b.split('-')[0] for b in B.index], textposition='top center',
                             marker=dict(size=13, symbol='x', color=CAT[1]), hovertemplate='%{text}<extra></extra>'))
    fig.update_xaxes(title=f'PC1 ({ev[0]:.0%})')
    fig.update_yaxes(title=f'PC2 ({ev[1]:.0%})')
    load = pd.DataFrame(Vt[:2].T, index=fp, columns=['PC1', 'PC2']).round(2)
    ltxt = '; '.join(f"PC{k + 1}: " + ', '.join(f"{i} {v:+.2f}" for i, v in load[f'PC{k + 1}'].abs().sort_values(ascending=False).head(4).items())
                     for k in range(2))
    add('Teams', 'Strategy map: field teams vs our bots', f"Unit: team (≥ 8 side-games; shrunken means of within-map z-scores over {len(fp)} fingerprint features), "
        f"our eight zoo bots projected in. Colour = latest rating, size = games in the corpus. Largest loadings (absolute) — {ltxt}. "
        f"Median distance from a field team to its nearest zoo bot {nn.median():.2f} sd-units; top-10 teams {nn[nn.index.isin(top_ids)].median():.2f}.", theme(fig, 560))
    far = nn.sort_values(ascending=False).head(15)
    rows = ''.join(f"<tr><td>{name(t)}</td><td>{latest.get(t, (np.nan,))[0]}</td><td>{latest.get(t, (0, np.nan))[1]}</td><td>{per_team.get(t, 0)}</td><td>{v:.2f}</td>"
                   f"<td>{', '.join(f'{f} {TE.loc[t, f]:+.1f}' for f in (TE.loc[t, fp] - B.mean()).abs().sort_values(ascending=False).head(3).index)}</td></tr>"
                   for t, v in far.items())
    add('Teams', 'Teams least like anything in the zoo', 'Distance to the nearest zoo bot in the fingerprint space; the last column lists the three '
        'features where the team is furthest from the zoo average (team effect in field sd).',
        f'<div class="tbl"><table><thead><tr><th>team</th><th>rating</th><th>rank</th><th>side-games</th><th>distance</th><th>most different on</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>')
    # --- Elo
    s = STR.dropna(subset=['lr_chi2_elo'])
    s = s[s['leading']].sort_values('lr_chi2_elo', ascending=False).head(20).iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=s['feature'], x=s['beta_elo'], orientation='h', name='field (beyond Elo)', marker_color=CAT[0]))
    fig.add_trace(go.Bar(y=s['feature'], x=s['zoo_beta_per_sd'], orientation='h', name='zoo (beyond zoo rating)', marker_color=ZOO_C))
    fig.update_layout(barmode='group')
    fig.update_xaxes(title='log-odds of winning per within-map sd, strength held fixed')
    add('Strength', 'Leading features that predict live results beyond Elo, next to the zoo equivalent',
        f"Unit: field side-game with both ratings known (n = {int(s['n'].max()) if len(s) else 0}); Elo expected score is a fixed offset (Elo alone "
        f"calls {meta['elo_only_accuracy']:.0%} of results). Leading = by r100. Ratings are the nearest earlier ladder snapshot, so games before the first "
        "snapshot use the earliest one.", theme(fig, 620))
    s2 = STR.dropna(subset=['team_effect_vs_rating_spearman']).copy()
    s2 = s2.reindex(s2['team_effect_vs_rating_spearman'].abs().sort_values(ascending=False).index).head(20).iloc[::-1]
    fig = go.Figure(go.Bar(y=s2['feature'], x=s2['team_effect_vs_rating_spearman'], orientation='h',
                           marker_color=[CAT[0] if v > 0 else CAT[1] for v in s2['team_effect_vs_rating_spearman']]))
    fig.update_xaxes(range=[-1, 1], title='Spearman: team effect vs team rating')
    add('Strength', 'Which traits go with a higher rating (team level)', 'Unit: team. Positive = stronger teams do more of it. These are strength '
        'traits across teams; features with a strong within-game effect but no rating correlation are tactics, not identity.', theme(fig, 560))
    # --- phases
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Opening ends (t1)', 'Crown race starts (t2)'])
    for j, c in enumerate(('phase_t1', 'phase_t2')):
        for lab, D, clr in (('zoo', Z0, ZOO_C), ('field winners', field[field['result'] == 'win'], WIN_C), ('field losers', field[field['result'] == 'loss'], LOSS_C)):
            fig.add_trace(go.Box(x=D['map'], y=D[c], name=lab, marker_color=clr, boxpoints=False, legendgroup=lab, showlegend=j == 0), 1, j + 1)
    fig.update_layout(boxmode='group')
    fig.update_xaxes(categoryorder='array', categoryarray=maps)
    add('Phases', 'Phase timing, zoo vs field', 'Both decoded with the HMM fitted on the zoo, so the states mean the same thing on both sides. '
        'Unit: side-game; a missing t2 means the side never entered the crown state.', theme(fig, 420))
    # --- ours
    oc = coverage(ours, Z0, feats, min_n=15) if len(ours) >= 15 else pd.DataFrame()
    if len(oc):
        oc = oc.sort_values('outside', ascending=False).head(15).iloc[::-1]
        fig = go.Figure([go.Bar(y=oc['feature'], x=oc['below'], name='below zoo', orientation='h', marker_color=CAT[1]),
                         go.Bar(y=oc['feature'], x=oc['above'], name='above zoo', orientation='h', marker_color=CAT[0])])
        fig.update_layout(barmode='stack')
        fig.update_xaxes(tickformat='.0%')
        add('Our live games', f'Our live games (team {OURS}) vs the zoo', f"Unit: our side-games in the corpus (n = {len(ours)}). Where our own live play "
            'falls outside what the same kind of bots do locally: an environment shift, because the opponents differ.', theme(fig, 520))
    # assemble
    toc, body, sec = [], [], None
    for section, title, caption, div in figs:
        if section != sec:
            sec = section
            sid = 's-' + section.lower().replace(' ', '-')
            body.append(f'<h2 id="{sid}">{section}</h2>')
            toc.append(f'<a href="#{sid}">{section}</a>')
        body.append(f'<figure class="card"><figcaption><h3>{title}</h3><p>{caption}</p></figcaption>{div}</figure>')
    notes = open(a.notes).read() if a.notes and os.path.exists(a.notes) else ''
    worst = COV.sort_values('outside', ascending=False).head(5)
    css = open(os.path.join(os.path.dirname(__file__), 'report_style.css')).read() if os.path.exists(os.path.join(os.path.dirname(__file__), 'report_style.css')) else ''
    return f"""<meta charset="utf-8"><title>Zoo Field Coverage</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500&display=swap">
<style>{css}</style>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@{_pjs()}/plotly.min.js"></script>
<main>
<h1>Zoo vs field: what our local bots do not cover</h1>
<p>{meta['field_games']} corpus games ({meta['field_side_games']} side-games, {meta['teams']} teams; team {OURS} excluded and shown separately) against
{meta['zoo_side_games']} seed-1 zoo side-games (panel z1, 8 bots, unswbc 1.2.2). Corpus index lines {meta['index_lines']}, newest game {meta['newest_finished']}.
Regenerate: <code>python -m tools.analysis.features.compare …</code>.</p>
<div class="kpis">
<div class="kpi"><b>{meta['field_games']}</b><span>field games</span></div>
<div class="kpi"><b>{meta['teams']}</b><span>teams</span></div>
<div class="kpi"><b>{COV['outside'].median():.0%}</b><span>median share of field side-games outside the zoo range (10% if representative)</span></div>
<div class="kpi"><b>{COV['team_outside_zoo_bots'].median():.0%}</b><span>median share of teams outside our bots' range</span></div>
</div>
<p>Worst covered: {', '.join(f"<code>{r.feature}</code> {r.outside:.0%}" for r in worst.itertuples())}.</p>
{notes}
<nav>{''.join(toc)}</nav>
{''.join(body)}
</main>"""


def _pjs():
    from plotly.offline import get_plotlyjs_version
    return get_plotlyjs_version()


if __name__ == '__main__':
    main()
