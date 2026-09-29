"""Aggregate a feature run into tables + an interactive report (F1 feature lab).

python -m tools.analysis.features.report --run build/zoo/z1/features --index build/zoo/z1/index.jsonl --out build/zoo/z1/report
Writes: quantiles.csv (feature x map x result), strength.csv, stability.csv, identity.csv, validation.json,
phases.parquet, report_body.html (no page skeleton, for publishing) and report.html (standalone).
Main tables use seed 1 only (the full round robin); stability uses the seed 1-3 fixtures.
"""
import argparse, json, math, os
import numpy as np
import pandas as pd

from .registry import REGISTRY
from . import phases as ph

WIN, LOSS = '#2a78d6', '#eb6834'
CAT = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
MAP_ORDER = ['Portals', 'Prisoners Dilemma', 'Devil', 'Trophy', 'Autarky', 'Default', 'Queen Of Spades', 'Schooltime',
             'Slithery Fight', 'Trauma']
HEADLINE = [
    ('total_share@100', 'Our share of total length at r100'),
    ('bed_capture_share', 'Share of all bed spawns we ate'),
    ('top1_share@250', 'Longest / total at r250 (crown concentration)'),
    ('splits_0_100', 'Splits in rounds 0-99'),
    ('deaths_per1k', 'Own deaths per 1k dragon-turns'),
    ('contact_share_mean', 'Mean share of our dragons with an enemy in view'),
    ('seen_share@100', 'Share of map seen by r100'),
    ('bed_territory@100', 'Bed-weighted territory at r100'),
    ('rays_per_dt', 'Sonar rays per dragon-turn'),
    ('rays_toward_com_share', 'Share of rays aimed toward allied centre'),
    ('enclosed_death_share', 'Share of deaths while enclosed'),
    ('epg_tau2', 'Expected pearl gain (tau 2)'),
    ('epg_conversion', 'Bed pearls eaten / EPG'),
    ('phase_t1', 'Opening ends (HMM, round)'),
    ('phase_t2', 'Crown race starts (HMM, round)'),
    ('economy_pearls_per100dt', 'Pearls per 100 dragon-turns inside the economy phase'),
    ('crown_deaths_per1k', 'Deaths per 1k dragon-turns inside the crown phase'),
]
import re as _re
LEADING = lambda n: bool(_re.search(r'@(25|50|100)$|_0_50$|_50_100$|_0_100$|^first_|^seen50$|^phase_t1$|^rule_t1$|^cp_t1$', n))


def theme(fig, h=360):
    fig.update_layout(template='simple_white', height=h, margin=dict(l=50, r=20, t=70, b=40),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#8a8986', size=12),
                      legend=dict(orientation='h', yanchor='bottom', y=1.08, x=0), hoverlabel=dict(font_size=12))
    fig.update_xaxes(showgrid=False, linecolor='rgba(128,128,128,.4)', tickcolor='rgba(128,128,128,.4)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,.18)', linecolor='rgba(128,128,128,.4)', zeroline=False)
    return fig


def auc(x, y):
    """P(feature of a winner > loser) via ranks; y in {0,1}"""
    m = ~np.isnan(x)
    x, y = x[m], y[m]
    n1, n0 = (y == 1).sum(), (y == 0).sum()
    if n1 < 3 or n0 < 3:
        return float('nan')
    r = pd.Series(x).rank().to_numpy()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def quantiles(f, feats):
    rows = []
    for feat in feats:
        for mp in MAP_ORDER + ['ALL']:
            d = f if mp == 'ALL' else f[f['map'] == mp]
            for res in ('win', 'loss', 'all'):
                x = (d if res == 'all' else d[d['result'] == res])[feat].astype(float).dropna()
                if not len(x):
                    continue
                q = [5, 25, 50, 75, 95] if mp == 'ALL' else [10, 25, 50, 75, 90]
                row = dict(feature=feat, map=mp, result=res, n=len(x), mean=x.mean())
                for p in q:
                    row[f'p{p}'] = float(np.percentile(x, p))
                rows.append(row)
    return pd.DataFrame(rows)


def strength(f, feats):
    rows = []
    d = f[f['result'] != 'draw']
    for feat in feats:
        per = []
        for mp, g in d.groupby('map'):
            a = auc(g[feat].astype(float).to_numpy(), (g['result'] == 'win').astype(int).to_numpy())
            if a == a:
                per.append((a, len(g)))
        if not per:
            continue
        w = sum(n for _, n in per)
        a = sum(a * n for a, n in per) / w
        rows.append(dict(feature=feat, family=REGISTRY.get(feat, {}).get('family', 'derived'), auc_within_map=a,
                         strength=abs(a - 0.5) * 2, maps=len(per), leading=LEADING(feat),
                         auc_min=min(x for x, _ in per), auc_max=max(x for x, _ in per)))
    return pd.DataFrame(rows).sort_values('strength', ascending=False)


def icc(df, feat, key):
    g = df[[key, feat]].dropna().groupby(key)[feat]
    groups = [v.to_numpy(float) for _, v in g if len(v) >= 2]
    if len(groups) < 4:
        return float('nan')
    k = np.mean([len(v) for v in groups])
    grand = np.concatenate(groups).mean()
    msb = sum(len(v) * (v.mean() - grand) ** 2 for v in groups) / (len(groups) - 1)
    msw = sum(((v - v.mean()) ** 2).sum() for v in groups) / (sum(len(v) for v in groups) - len(groups))
    den = msb + (k - 1) * msw
    return (msb - msw) / den if den > 0 else float('nan')


def nearest_centroid(X, y):
    """leave-one-out nearest-centroid accuracy"""
    X = np.nan_to_num(X)
    labels = sorted(set(y))
    y = np.array(y)
    sums = {l: X[y == l].sum(0) for l in labels}
    cnt = {l: (y == l).sum() for l in labels}
    ok = 0
    for i in range(len(X)):
        best, bl = None, None
        for l in labels:
            c = cnt[l] - (y[i] == l)
            if c == 0:
                continue
            mu = (sums[l] - (X[i] if y[i] == l else 0)) / c
            dd = ((X[i] - mu) ** 2).sum()
            if best is None or dd < best:
                best, bl = dd, l
        ok += bl == y[i]
    return ok / len(X)


def bradley_terry(F1, iters=200):
    """zoo-only rating (Elo-like scale, 400/log10) from seed-1 side-games; draws count half"""
    bots = sorted(F1['bot'].unique())
    A = F1[F1['side'] == 'A']
    r = {b: 0.0 for b in bots}
    for _ in range(iters):
        grad = {b: 0.0 for b in bots}
        hess = {b: 1e-6 for b in bots}
        for x in A.itertuples():
            p = 1 / (1 + math.exp(-(r[x.bot] - r[x.opponent])))
            grad[x.bot] += x.won - p
            grad[x.opponent] -= x.won - p
            hess[x.bot] += p * (1 - p)
            hess[x.opponent] += p * (1 - p)
        for b in bots:   # weak Gaussian prior (lam 0.1) keeps undefeated / winless bots finite
            r[b] += max(-1.0, min(1.0, (grad[b] - 0.1 * r[b]) / (hess[b] + 0.1)))
        m = sum(r.values()) / len(r)
        r = {b: v - m for b, v in r.items()}
    return {b: v * 400 / math.log(10) for b, v in r.items()}


def beyond_rating(F1, feats, rating):
    """logit P(win) = rating gap (offset) + beta * within-map z(feature): does the feature predict the result given who played?"""
    d = F1[F1['result'] != 'draw']
    off = np.array([(rating[b] - rating[o]) * math.log(10) / 400 for b, o in zip(d['bot'], d['opponent'])])
    y = (d['result'] == 'win').to_numpy(float)
    Z = within_map_z(d, feats)
    rows = []
    ll0 = float(np.sum(y * off - np.log1p(np.exp(off))))
    for f in feats:
        z = Z[f].to_numpy(float)
        if np.nanstd(z) == 0:
            continue
        b = 0.0
        for _ in range(30):
            eta = off + b * z
            p = 1 / (1 + np.exp(-eta))
            g = np.sum((y - p) * z)
            h = np.sum(p * (1 - p) * z * z) + 1e-9
            b = float(np.clip(b + g / h, -20, 20))
        eta = off + b * z
        ll = float(np.sum(y * eta - np.log1p(np.exp(eta))))
        rows.append(dict(feature=f, beta_per_sd=b, lr_chi2=2 * (ll - ll0)))
    return pd.DataFrame(rows)


def within_map_z(f, feats):
    Z = f[feats].astype(float).copy()
    for mp, idx in f.groupby('map').groups.items():
        sub = Z.loc[idx]
        Z.loc[idx] = (sub - sub.mean()) / sub.std().replace(0, np.nan)
    return Z.fillna(0).clip(-4, 4)


def phase_conditioned(F, S):
    """per side-game rates inside each HMM phase: duration, pearls / 100 dragon-turns, deaths / 1k, splits / 100, rays / dragon-turn"""
    key = F.set_index(['game', 'side'])[['phase_t1', 'phase_t2', 'rounds']]
    out = []
    for (g, s), d in S.groupby(['game', 'side']):
        if (g, s) not in key.index:
            continue
        t1, t2, R = key.loc[(g, s)]
        R = int(R)
        t1 = R if t1 != t1 or t1 is None else int(t1)
        t2 = R if t2 != t2 or t2 is None else int(max(t2, t1))
        d = d.set_index('round')
        row = dict(game=g, side=s)
        for nm, lo, hi in (('opening', 0, t1), ('economy', t1, t2), ('crown', t2, R)):
            w = d.loc[lo:hi - 1] if hi > lo else d.iloc[0:0]
            dt = w['dragon_turns'].sum() if 'dragon_turns' in w else 0
            row[f'{nm}_rounds'] = hi - lo
            row[f'{nm}_pearls_per100dt'] = 100 * w['eats'].sum() / dt if dt else np.nan
            row[f'{nm}_deaths_per1k'] = 1000 * w['deaths'].sum() / dt if dt and 'deaths' in w else np.nan
            row[f'{nm}_splits_per100dt'] = 100 * w['splits'].sum() / dt if dt and 'splits' in w else np.nan
            row[f'{nm}_rays_per_dt'] = w['rays'].sum() / dt if dt and 'rays' in w else np.nan
        out.append(row)
    return F.merge(pd.DataFrame(out), on=['game', 'side'], how='left')


def flags(F1, feats, ST, STAB):
    """per feature: zero share, variance explained by map (eta2_map), by bot within map (eta2_bot), bimodality, strength, ICC"""
    rows = []
    stv = ST.set_index('feature')
    icv = STAB.set_index('feature')['icc'] if len(STAB) else pd.Series(dtype=float)
    for f in feats:
        x = F1[f].astype(float)
        m = x.notna()
        if m.sum() < 20:
            continue
        d = F1.loc[m, ['map', 'bot']].assign(x=x[m])
        tot = ((d['x'] - d['x'].mean()) ** 2).sum()
        mapm = d.groupby('map')['x'].transform('mean')
        within = ((d['x'] - mapm) ** 2).sum()
        botm = d.groupby(['map', 'bot'])['x'].transform('mean')
        bot_ss = ((botm - mapm) ** 2).sum()
        d = d.assign(res=d['x'] - botm, opponent=F1.loc[m, 'opponent'])
        oppm = d.groupby(['map', 'opponent'])['res'].transform('mean')
        opp_ss = (oppm ** 2).sum()
        z = (d['x'] - mapm) / d.groupby('map')['x'].transform('std').replace(0, np.nan)
        z = z.dropna()
        n = len(z)
        bc = float('nan')
        if n > 10 and z.std() > 0:
            sk, ku = z.skew(), z.kurt()
            bc = (sk ** 2 + 1) / (ku + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))
        row = dict(feature=f, family=REGISTRY.get(f, {}).get('family', 'derived'), n=int(m.sum()),
                   zero_share=float((d['x'] == 0).mean()), eta2_map=float(1 - within / tot) if tot > 0 else float('nan'),
                   eta2_bot_within_map=float(bot_ss / within) if within > 0 else float('nan'),
                   eta2_opp_within_map=float(opp_ss / within) if within > 0 else float('nan'), bimodality=bc,
                   auc=float(stv.loc[f, 'auc_within_map']) if f in stv.index else float('nan'),
                   leading=LEADING(f), icc=float(icv.get(f, float('nan'))))
        fl = []
        if row['zero_share'] > 0.95:
            fl.append('all-zero')
        if row['eta2_map'] == row['eta2_map'] and row['eta2_map'] > 0.9:
            fl.append('map-locked')
        if row['eta2_bot_within_map'] == row['eta2_bot_within_map'] and row['eta2_bot_within_map'] > 0.8:
            fl.append('bot-locked')
        if bc == bc and bc > 0.555:
            fl.append('bimodal')
        if row['icc'] == row['icc'] and row['icc'] < 0.3:
            fl.append('seed-noisy')
        row['flags'] = ' '.join(fl)
        rows.append(row)
    return pd.DataFrame(rows)


def fill_curves(series, cols, R=500):
    """per side-game, reindex rounds 0..R; state columns carried forward after the game ends"""
    out = []
    for (g, s), d in series.groupby(['game', 'side']):
        d = d.set_index('round')[cols].reindex(range(R + 1)).ffill()
        d['game'], d['side'] = g, s
        out.append(d.reset_index())
    return pd.concat(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', required=True)
    ap.add_argument('--index')
    ap.add_argument('--out', required=True)
    ap.add_argument('--title', default='F1 feature lab: zoo panel z1')
    ap.add_argument('--notes', default=None, help='HTML fragment with findings, inserted under the summary')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    rd = lambda n: pd.read_parquet(os.path.join(a.run, n + '.parquet')) if os.path.exists(os.path.join(a.run, n + '.parquet')) else pd.DataFrame()
    F, S, SM, DR, DE, CK, EX = (rd(n) for n in ('features', 'series', 'samples', 'dragons', 'deaths', 'checks', 'exposure'))
    F['seed'] = F['seed'] if 'seed' in F else F['game'].str.extract(r'^s(\d+)__')[0].astype(float)
    F['splits_0_100'] = F['splits_0_50'].fillna(0) + F['splits_50_100'].fillna(0)
    # fixtures for stability: same map, same bots in the same seats
    F['fixture'] = F['game'].str.replace(r'^s\d+__', '', regex=True) + '|' + F['side']
    # ---------------- phases ----------------
    scale = ph.pooled_scale(S)
    prow = []
    for (g, s), d in S.groupby(['game', 'side']):
        prow.append(dict(game=g, side=s, **ph.detect(d.sort_values('round'), scale, max_k=3)))
    P = pd.DataFrame(prow)
    # pooled left-to-right HMM on seed-1 side-games, initialised from the rule markers; decode everything
    seqs, inits, keys = [], [], []
    seed1 = set(F.loc[F['seed'] == 1, 'game'])
    allseq = {}
    for (g, s), d in S.groupby(['game', 'side']):
        sig = ph.signals(d.sort_values('round'))
        X = ph.binned(sig, scale)
        if X is None:
            continue
        X = ph.hmm_view(X)
        allseq[(g, s)] = X
        if g in seed1:
            t1, t2 = ph.rule_phases(sig)
            seqs.append(X)
            inits.append(ph.rule_path(len(X), t1, t2))
    HMM = ph.fit_hmm(seqs, inits)
    hm = []
    for (g, s), X in allseq.items():
        path, t1, t2 = ph.decode_hmm(HMM, X)
        hm.append(dict(game=g, side=s, hmm_t1=t1, hmm_t2=t2))
    P = P.merge(pd.DataFrame(hm), on=['game', 'side'], how='left')
    P.to_parquet(os.path.join(a.out, 'phases.parquet'), index=False)
    with open(os.path.join(a.out, 'hmm.json'), 'w') as fh:
        json.dump(dict(signals=ph.HMM_SIGNALS, states=ph.STATES, scale=scale, mu=HMM['mu'].tolist(), var=HMM['var'].tolist(),
                       A=HMM['A'].tolist(), pi=HMM['pi'].tolist(), loglik=HMM['loglik']), fh, indent=1)
    F = F.merge(P, on=['game', 'side'], how='left')
    F['phase_t1'], F['phase_t2'] = F['hmm_t1'], F['hmm_t2']
    F = phase_conditioned(F, S)
    F1 = F[F['seed'] == 1].copy()
    PHASED = [c for c in F.columns if c.startswith(('opening_', 'economy_', 'crown_'))]
    feats = [c for c in F.columns if c in REGISTRY or c in ('splits_0_100', 'cp_t1', 'cp_t2', 'rule_t1', 'rule_t2') or c in PHASED]
    feats = [c for c in feats if pd.api.types.is_numeric_dtype(F[c])]
    Q = quantiles(F1, feats)
    Q.to_csv(os.path.join(a.out, 'quantiles.csv'), index=False)
    ST = strength(F1, feats)
    RATING = bradley_terry(F1)
    ST = ST.merge(beyond_rating(F1, feats, RATING), on='feature', how='left')
    json.dump(RATING, open(os.path.join(a.out, 'zoo_rating.json'), 'w'), indent=1)
    ST.to_csv(os.path.join(a.out, 'strength.csv'), index=False)
    # stability on the seed 1-3 fixtures
    stab_fx = F.groupby('fixture')['seed'].nunique()
    stab_fx = stab_fx[stab_fx >= 3].index
    FS = F[F['fixture'].isin(stab_fx)]
    STAB = pd.DataFrame([dict(feature=x, family=REGISTRY.get(x, {}).get('family', 'derived'), icc=icc(FS, x, 'fixture'),
                              fixtures=len(stab_fx)) for x in feats])
    STAB.to_csv(os.path.join(a.out, 'stability.csv'), index=False)
    # identity vs outcome per family (seed 1, within-map standardised)
    Z = within_map_z(F1, feats)
    fams = sorted({REGISTRY[x]['family'] for x in feats if x in REGISTRY})
    ID = []
    dec = F1['result'] != 'draw'
    for fam in fams + ['ALL']:
        cols = [x for x in feats if fam == 'ALL' or REGISTRY.get(x, {}).get('family') == fam]
        cols = [c for c in cols if not c.startswith(('phase', 'cp_'))]
        if not cols:
            continue
        ID.append(dict(family=fam, features=len(cols), bot_accuracy=nearest_centroid(Z[cols].to_numpy(), list(F1['bot'])),
                       bot_chance=1 / F1['bot'].nunique(),
                       outcome_accuracy=nearest_centroid(Z[dec][cols].to_numpy(), list(F1[dec]['result']))))
    ID = pd.DataFrame(ID)
    ID.to_csv(os.path.join(a.out, 'identity.csv'), index=False)
    FL = flags(F1, feats, ST, STAB)
    FL.to_csv(os.path.join(a.out, 'flags.csv'), index=False)
    # ---------------- validation (V0, V3) ----------------
    val = {}
    val['v0'] = CK.groupby('check')['residual'].agg(lambda r: float((r == 0).mean())).to_dict() if len(CK) else {}
    val['v0_n'] = int(CK['game'].nunique()) if len(CK) else 0
    pc = os.path.join(os.path.dirname(a.run.rstrip('/')), '..', 'probes', 'probe_check.json')
    for cand in (pc, 'build/zoo/probes/probe_check.json'):
        if os.path.exists(cand):
            pr = json.load(open(cand))
            val['probe'] = f"{sum(r['passed'] for r in pr)}/{len(pr)}"
            val['probe_detail'] = pr
            break
    SM1 = SM[SM['game'].isin(F1['game'])]
    epg = []
    for tau in (1, 2, 4):
        cs = [np.corrcoef(g[f'access_tau{tau}'], g['bed_eats_next10'])[0, 1] for _, g in SM1.groupby('map') if g['bed_eats_next10'].std() > 0]
        epg.append(dict(tau=tau, mean_within_map_r=float(np.nanmean(cs))))
    val['epg_calibration'] = epg
    piv = SM1.pivot_table(index=['game', 'round'], columns='side', values=['bed_territory', 'bed_eats_next10', 'bed_expected_share', 'territory'])
    tr = pd.DataFrame(dict(terr=piv[('bed_territory', 'A')], exp=piv[('bed_expected_share', 'A')], cells=piv[('territory', 'A')],
                           share=piv[('bed_eats_next10', 'A')] / (piv[('bed_eats_next10', 'A')] + piv[('bed_eats_next10', 'B')]))).dropna()
    val['territory_vs_next_bed_share_r'] = {k: float(np.corrcoef(tr[k], tr['share'])[0, 1]) for k in ('terr', 'exp', 'cells')} if len(tr) > 10 else {}
    haz = None
    if len(EX):
        EX1 = EX[EX['game'].isin(F1['game'])]
        bins = [-1, 2, 5, 10, 15, 20, 30, 45, 61]
        EX1 = EX1.assign(b=pd.cut(EX1['reach5'], bins))
        DE1 = DE[DE['game'].isin(F1['game']) & (DE['cls'] != 'suicide')].assign(b=lambda d: pd.cut(d['reach5'], bins))
        expo = EX1.groupby('b', observed=False)['sampled_turns'].sum() * 5
        dth = DE1.groupby('b', observed=False).size()
        haz = pd.DataFrame(dict(exposure=expo, deaths=dth)).assign(per1k=lambda d: 1000 * d['deaths'] / d['exposure'])
        haz.index = haz.index.astype(str)
        val['enclosure_hazard'] = haz.reset_index().rename(columns={'b': 'reach5'}).to_dict('records')
    if len(DR):
        DR1 = DR[DR['game'].isin(F1['game']) & (DR['turns'] >= 20)]
        val['density_vs_eats_spearman'] = float(np.nanmean([g['density_ratio'].rank().corr(g['eats_per_100'].rank()) for _, g in DR1.groupby('map')]))
    def agree(x, y):
        d = P.dropna(subset=[x, y])
        return float((abs(d[x] - d[y]) <= 15).mean()) if len(d) else None
    val['phase_agreement'] = dict(t1_within15=agree('rule_t1', 'hmm_t1'), t2_within15=agree('rule_t2', 'hmm_t2'),
                                  t1_cp_hmm=agree('cp_t1', 'hmm_t1'), t2_cp_hmm=agree('cp_t2', 'hmm_t2'),
                                  t2_missing=dict(rule=float(P['rule_t2'].isna().mean()), hmm=float(P['hmm_t2'].isna().mean())),
                                  k_distribution=P['cp_k'].value_counts().sort_index().to_dict(),
                                  labels=P['cp_labels'].value_counts().head(8).to_dict())
    with open(os.path.join(a.out, 'validation.json'), 'w') as fh:
        json.dump(val, fh, indent=1, default=str)
    html = build_html(a, F, F1, S, P, Q, ST, STAB, ID, val, haz, SM1, tr, DE, DR, EX, FL)
    with open(os.path.join(a.out, 'report_body.html'), 'w') as fh:
        fh.write(inline_plotly(html))
    with open(os.path.join(a.out, 'report.html'), 'w') as fh:
        fh.write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                 f'<title>F1 feature lab</title></head><body>{html}</body></html>')
    print(json.dumps(dict(side_games=len(F), seed1=len(F1), features=len(feats), out=a.out), default=str))


def build_html(a, F, F1, S, P, Q, ST, STAB, ID, val, haz, SM1, tr, DE, DR, EX, FL):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    figs = []

    def add(section, title, caption, fig):
        figs.append((section, title, caption, fig.to_html(full_html=False, include_plotlyjs=False, config=dict(displaylogo=False, responsive=True, modeBarButtonsToRemove=['toImage']))))

    bots = sorted(F1['bot'].unique())
    bc = {b: CAT[i % 8] for i, b in enumerate(bots)}
    maps = [m for m in MAP_ORDER if m in set(F1['map'])]
    short = lambda b: b.split('-')[0] + '-' + b.split('-')[1]

    # ---- outcomes ----
    A = F1[F1['side'] == 'A']
    wm = pd.DataFrame(index=bots, columns=bots, dtype=float)
    for b in bots:
        for o in bots:
            d = F1[(F1['bot'] == b) & (F1['opponent'] == o)]
            if len(d):
                wm.loc[b, o] = d['won'].mean()
    fig = go.Figure(go.Heatmap(z=wm.values, x=[short(b) for b in bots], y=[short(b) for b in bots], zmin=0, zmax=1,
                               colorscale=[[0, '#e34948'], [0.5, '#f0efec'], [1, '#2a78d6']], text=np.where(np.isnan(wm.values.astype(float)), '', np.round(wm.values.astype(float), 2).astype(str)), texttemplate='%{text}',
                               hovertemplate='%{y} vs %{x}: win rate %{z:.2f}<extra></extra>', colorbar=dict(title='win')))
    add('Outcomes', 'Win rate, row bot vs column bot', 'Unit: side-game, seed 1, 20 games per pair (10 maps x 2 seats).', theme(fig, 440))
    bm = F1.groupby(['bot', 'map'])['won'].mean().unstack()[maps]
    fig = go.Figure(go.Heatmap(z=bm.values, x=maps, y=[short(b) for b in bm.index], zmin=0, zmax=1,
                               colorscale=[[0, '#e34948'], [0.5, '#f0efec'], [1, '#2a78d6']], text=np.round(bm.values, 2), texttemplate='%{text}',
                               hovertemplate='%{y} on %{x}: %{z:.2f}<extra></extra>'))
    add('Outcomes', 'Win rate by bot and map', 'Unit: side-game, seed 1, 14 per cell (7 opponents x 2 seats). Maps ordered compact first.', theme(fig, 420))
    rt = json.load(open(os.path.join(a.out, 'zoo_rating.json')))
    order = sorted(rt, key=rt.get)
    fig = go.Figure(go.Bar(y=[short(b) for b in order], x=[rt[b] for b in order], orientation='h', marker_color=[bc[b] for b in order],
                           hovertemplate='%{y}: %{x:.0f}<extra></extra>'))
    fig.update_xaxes(title='zoo-only Bradley–Terry rating (Elo scale, mean 0)')
    add('Outcomes', 'Zoo rating', 'Fitted on the seed-1 round robin only. It is relational to this zoo and is not comparable with live Elo; '
        'it is used below as the control when asking whether a feature predicts the result beyond who played.', theme(fig, 320))
    rs = F1[F1['side'] == 'A'].groupby('map')['reason'].value_counts(normalize=True).unstack().reindex(maps).fillna(0)
    fig = go.Figure([go.Bar(x=maps, y=rs[c], name=c, marker_color=CAT[i], hovertemplate='%{x}: %{y:.0%} ' + c + '<extra></extra>') for i, c in enumerate(rs.columns)])
    fig.update_layout(barmode='stack', yaxis_tickformat='.0%')
    add('Outcomes', 'How games end, by map', 'Unit: game (seed 1). elimination / longest at r500 / total at r500.', theme(fig, 320))

    # ---- curves (winners vs losers per map) ----
    S1 = S[S['game'].isin(F1['game'])].copy()
    S1 = S1.sort_values(['game', 'side', 'round'])
    S1['cum_pearls'] = S1.groupby(['game', 'side'])['eats'].cumsum()
    S1['cum_births'] = S1.groupby(['game', 'side'])['splits'].cumsum()
    C = fill_curves(S1, ['units', 'total', 'longest', 'cum_pearls', 'seen_share', 'top1_share', 'cum_births'])
    res = F1.set_index(['game', 'side'])[['result', 'map']]
    C = C.join(res, on=['game', 'side'])
    rounds = list(range(0, 501, 5))
    for col, title, unit in (('total', 'Total length', 'segments'), ('units', 'Living dragons', 'dragons'),
                             ('longest', 'Longest dragon', 'segments'), ('cum_pearls', 'Cumulative pearls eaten', 'pearls'),
                             ('cum_births', 'Cumulative births (splits)', 'dragons'),
                             ('seen_share', 'Share of map seen', 'share of cells'), ('top1_share', 'Longest / total', 'share')):
        fig = make_subplots(rows=2, cols=5, subplot_titles=maps, shared_xaxes=True, horizontal_spacing=0.04, vertical_spacing=0.12)
        for k, mp in enumerate(maps):
            r_, c_ = k // 5 + 1, k % 5 + 1
            for resn, colr in (('win', WIN), ('loss', LOSS)):
                d = C[(C['map'] == mp) & (C['result'] == resn) & (C['round'].isin(rounds))].groupby('round')[col]
                q = d.quantile([0.25, 0.5, 0.75]).unstack()
                fig.add_trace(go.Scatter(x=list(q.index) + list(q.index[::-1]), y=list(q[0.75]) + list(q[0.25][::-1]), fill='toself',
                                         fillcolor=colr.replace('#', 'rgba(') if False else _rgba(colr, .15), line=dict(width=0),
                                         hoverinfo='skip', showlegend=False), r_, c_)
                fig.add_trace(go.Scatter(x=q.index, y=q[0.5], line=dict(color=colr, width=2), name=resn, legendgroup=resn,
                                         showlegend=k == 0, hovertemplate=f'{mp} {resn} r%{{x}}: median %{{y:.2f}}<extra></extra>'), r_, c_)
        add('Curves', f'{title}: winners vs losers by map', f'Median and interquartile band over side-games (seed 1, ~56 per result per map); unit {unit}; '
            'terminal state carried forward after the game ends.', theme(fig, 460))

    # ---- phases ----
    PF = F1[['game', 'side', 'bot', 'map', 'result', 'rounds', 'rule_t1', 'rule_t2', 'cp_t1', 'cp_t2', 'cp_k', 'cp_labels', 'hmm_t1', 'hmm_t2']]
    hmm = json.load(open(os.path.join(a.out, 'hmm.json')))
    mu = np.array(hmm['mu'])
    fig = go.Figure(go.Heatmap(z=mu, x=list(hmm['signals']), y=list(hmm['states']), zmid=0, zmin=-1.5, zmax=1.5,
                               colorscale=[[0, '#e34948'], [0.5, '#f0efec'], [1, '#2a78d6']], text=np.round(mu, 2), texttemplate='%{text}',
                               hovertemplate='%{y} · %{x}: %{z:.2f} sd<extra></extra>'))
    stay = np.diag(np.array(hmm['A']))
    add('Phases', 'What each phase looks like: fitted HMM state means', 'Pooled left-to-right 3-state Gaussian HMM over all seed-1 side-games (5-round bins, '
        'signals per living dragon, standardised over the corpus). States are named by their fitted signature, not assumed. '
        f"Expected stay: opening {BIN_(stay[0])} rounds, economy {BIN_(stay[1])} rounds.", theme(fig, 300))
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Opening ends (t1)', 'Crown race starts (t2)'], horizontal_spacing=0.06)
    for j, (hc, rc, cc) in enumerate((('hmm_t1', 'rule_t1', 'cp_t1'), ('hmm_t2', 'rule_t2', 'cp_t2'))):
        for nm, col, clr in (('HMM', hc, CAT[0]), ('rule', rc, CAT[1]), ('changepoint', cc, CAT[2])):
            d = PF.dropna(subset=[col])
            fig.add_trace(go.Box(x=d['map'], y=d[col], name=nm, marker_color=clr, legendgroup=nm, showlegend=j == 0, boxpoints=False), 1, j + 1)
    fig.update_layout(boxmode='group')
    fig.update_xaxes(categoryorder='array', categoryarray=maps)
    add('Phases', 'When the phases change, by map', 'Unit: side-game (seed 1). Rule: discovery collapse (t1) and production stop with rising concentration (t2). '
        'Changepoint: exact 3-segment least-squares fit on six standardised per-dragon signals in 5-round bins.', theme(fig, 420))
    # timeline bars: median t1, t2 per bot x map
    fig = make_subplots(rows=2, cols=5, subplot_titles=maps, shared_yaxes=True, horizontal_spacing=0.03, vertical_spacing=0.12)
    for k, mp in enumerate(maps):
        r_, c_ = k // 5 + 1, k % 5 + 1
        d = PF[PF['map'] == mp].groupby('bot').agg(t1=('hmm_t1', 'median'), t2=('hmm_t2', 'median'), end=('rounds', 'median')).reindex(bots)
        t1 = d['t1'].fillna(d['end'])
        t2 = d['t2'].fillna(d['end']).clip(lower=t1)
        for nm, base, length, clr in (('opening', 0 * t1, t1, CAT[2]), ('economy', t1, t2 - t1, CAT[0]), ('crown race', t2, d['end'] - t2, CAT[3])):
            fig.add_trace(go.Bar(y=[short(b) for b in bots], x=length, base=base, orientation='h', marker_color=clr, name=nm, legendgroup=nm,
                                 showlegend=k == 0, hovertemplate='%{y} ' + nm + ': r%{base:.0f} for %{x:.0f} rounds<extra></extra>'), r_, c_)
    fig.update_layout(barmode='overlay', bargap=0.25)
    add('Phases', 'Median phase timeline by bot and map (HMM)', 'Bars run from 0 to the median game length; a missing t2 means production never '
        'wound down before the game ended, so the economy phase runs to the end.', theme(fig, 560))
    ag = P.dropna(subset=['rule_t1', 'cp_t1'])
    fig = make_subplots(rows=1, cols=2, subplot_titles=['t1: rule (x) vs HMM (y)', 't2: rule (x) vs HMM (y)'])
    for j, (x, y) in enumerate((('rule_t1', 'hmm_t1'), ('rule_t2', 'hmm_t2'))):
        d = P.dropna(subset=[x, y])
        fig.add_trace(go.Scattergl(x=d[x], y=d[y], mode='markers', marker=dict(size=6, color=CAT[0], opacity=.35), showlegend=False,
                                   hovertemplate='rule %{x}, cp %{y}<extra></extra>'), 1, j + 1)
        fig.add_trace(go.Scatter(x=[0, 500], y=[0, 500], mode='lines', line=dict(color='#8a8986', dash='dot', width=1), showlegend=False, hoverinfo='skip'), 1, j + 1)
    add('Phases', 'Do the two detectors agree?', f"Unit: side-game. Share within ±15 rounds: t1 {_pct(val['phase_agreement']['t1_within15'])}, "
        f"t2 {_pct(val['phase_agreement']['t2_within15'])} (changepoint vs HMM: {_pct(val['phase_agreement']['t1_cp_hmm'])}, {_pct(val['phase_agreement']['t2_cp_hmm'])}). BIC-chosen number of changepoints: {val['phase_agreement']['k_distribution']}; "
        f"segment labels: {val['phase_agreement']['labels']}.", theme(fig, 380))

    # ---- headline features ----
    for feat, title in HEADLINE:
        if feat not in F1:
            continue
        fig = go.Figure()
        for resn, clr in (('win', WIN), ('loss', LOSS)):
            d = F1[F1['result'] == resn]
            fig.add_trace(go.Box(x=d['map'], y=d[feat], name=resn, marker_color=clr, boxpoints=False,
                                 hovertemplate='%{x}: %{y}<extra>' + resn + '</extra>'))
        d = F1
        fig.add_trace(go.Box(x=['ALL'] * (d['result'] == 'win').sum(), y=d[d['result'] == 'win'][feat], marker_color=WIN, showlegend=False, boxpoints=False, name='win'))
        fig.add_trace(go.Box(x=['ALL'] * (d['result'] == 'loss').sum(), y=d[d['result'] == 'loss'][feat], marker_color=LOSS, showlegend=False, boxpoints=False, name='loss'))
        fig.update_layout(boxmode='group')
        fig.update_xaxes(categoryorder='array', categoryarray=maps + ['ALL'])
        meta = REGISTRY.get(feat, dict(unit='', definition=''))
        st = ST[ST['feature'] == feat]
        s_txt = f" Within-map AUC for winning {st['auc_within_map'].iloc[0]:.2f}." if len(st) else ''
        add('Features', f'{title}  ·  {feat}', f"Unit: side-game (seed 1); value in {meta.get('unit')}. {meta.get('definition', '')}.{s_txt}", theme(fig, 360))

    # ---- strength ranking ----
    cand = ST[~ST['feature'].str.startswith(('cp_',))]
    top = pd.concat([cand[cand['leading']].head(15), cand[~cand['leading']].head(15)]).sort_values('strength').copy()
    fig = go.Figure(go.Bar(y=top['feature'], x=top['auc_within_map'] - 0.5, base=0.5, orientation='h',
                           marker_color=[CAT[0] if l else CAT[7] for l in top['leading']],
                           customdata=np.stack([top['family'], top['auc_min'], top['auc_max']], 1),
                           hovertemplate='%{y} (%{customdata[0]}): AUC %{x:.2f}, map range %{customdata[1]:.2f}-%{customdata[2]:.2f}<extra></extra>'))
    fig.add_vline(x=0.5, line_color='#8a8986', line_width=1)
    fig.update_xaxes(range=[0, 1], title='within-map AUC for winning (0.5 = no signal)')
    add('Strength', 'Which features separate winners from losers (top 15 leading, top 15 lagging)', 'Blue = leading (measured by r100 or earliest-event), red = lagging. '
        'Lagging material features win trivially; the leading ones are the candidates for cause. Unit: side-game, seed 1, AUC averaged over maps weighted by n.', theme(fig, 760))

    br = ST.dropna(subset=['lr_chi2'])
    br = br[~br['feature'].str.startswith(('cp_',))]
    br = br[br['leading']].sort_values('lr_chi2', ascending=False).head(20).iloc[::-1]
    fig = go.Figure(go.Bar(y=br['feature'], x=br['beta_per_sd'], orientation='h', marker_color=[CAT[0] if b > 0 else CAT[1] for b in br['beta_per_sd']],
                           customdata=np.stack([br['lr_chi2'], br['auc_within_map']], 1),
                           hovertemplate='%{y}: %{x:.2f} log-odds per sd (LR χ² %{customdata[0]:.1f}; raw AUC %{customdata[1]:.2f})<extra></extra>'))
    fig.update_xaxes(title='log-odds of winning per within-map sd, given both bots\' zoo ratings')
    add('Strength', 'Leading features that predict the result beyond who played (top 20 by likelihood ratio)',
        'Logistic model with the zoo-rating gap as a fixed offset: a feature scores only if, for the same matchup strength, games where it '
        'is higher are won more often. Leading = measured by r100. Unit: side-game, seed 1. χ² > 3.8 ≈ p < 0.05 before multiple-comparison correction.', theme(fig, 620))

    # ---- style x strength map ----
    fl = FL.dropna(subset=['eta2_bot_within_map', 'auc'])
    fig = go.Figure()
    for lead, clr, nm in ((True, CAT[0], 'leading (≤ r100)'), (False, CAT[7], 'lagging')):
        d = fl[fl['leading'] == lead]
        fig.add_trace(go.Scatter(x=d['eta2_bot_within_map'], y=(d['auc'] - 0.5).abs() * 2, mode='markers', name=nm,
                                 marker=dict(size=9, color=clr, opacity=.75, line=dict(width=1, color='rgba(255,255,255,.8)')),
                                 customdata=np.stack([d['feature'], d['family'], d['auc'], d['flags'].fillna('')], 1),
                                 hovertemplate='<b>%{customdata[0]}</b> (%{customdata[1]})<br>bot share of within-map variance %{x:.2f}'
                                               '<br>AUC %{customdata[2]:.2f} %{customdata[3]}<extra></extra>'))
    fig.update_xaxes(title='style: share of within-map variance explained by which bot played', range=[0, 1])
    fig.update_yaxes(title='strength: |AUC − 0.5| × 2', range=[0, 1])
    add('Strength', 'Style × strength map of every feature', 'Unit: feature (seed-1 side-games). Top-left = outcome signal that is not a bot signature (the '
        'interesting kind); bottom-right = style fingerprint with no outcome signal; top-right = a bot trait that also wins. Hover for names.', theme(fig, 520))
    ft = FL[FL['flags'].str.len() > 0].sort_values(['flags', 'feature'])
    rows_html = ''.join(f"<tr><td><code>{r.feature}</code></td><td>{r.family}</td><td>{r.flags}</td><td>{r.zero_share:.2f}</td><td>{r.eta2_map:.2f}</td>"
                        f"<td>{r.eta2_bot_within_map:.2f}</td><td>{r.bimodality:.2f}</td><td>{r.icc:.2f}</td></tr>" for r in ft.itertuples())
    figs.append(('Strength', 'Flagged features', 'all-zero = >95% zeros; map-locked = map explains >90% of variance; bot-locked = bot explains >80% of within-map '
                 'variance; bimodal = bimodality coefficient >0.555 on within-map z-scores; seed-noisy = ICC <0.3 across seeds.',
                 f'<div class="tbl"><table><thead><tr><th>feature</th><th>family</th><th>flags</th><th>zero</th><th>η² map</th><th>η² bot</th><th>bimod.</th>'
                 f'<th>ICC</th></tr></thead><tbody>{rows_html}</tbody></table></div>'))

    # ---- style vs strength ----
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ID['family'], y=ID['bot_accuracy'], name='identifies the bot', marker_color=CAT[0]))
    fig.add_trace(go.Bar(x=ID['family'], y=ID['outcome_accuracy'], name='predicts win/loss', marker_color=CAT[1]))
    fig.add_hline(y=float(ID['bot_chance'].iloc[0]), line_dash='dot', line_color=CAT[0], annotation_text='bot chance', annotation_position='top left')
    fig.add_hline(y=0.5, line_dash='dot', line_color=CAT[1], annotation_text='outcome chance', annotation_position='bottom right')
    fig.update_yaxes(range=[0, 1], tickformat='.0%')
    add('Validation', 'Style or strength? Leave-one-out nearest-centroid accuracy by family', 'Unit: side-game (seed 1), features z-scored within map. '
        'A family that names the bot is a style fingerprint; one that names the outcome is a strength signal.', theme(fig, 380))
    fam_icc = STAB.groupby('family')['icc'].median().sort_values()
    fig = go.Figure(go.Bar(x=fam_icc.index, y=fam_icc.values, marker_color=CAT[2], hovertemplate='%{x}: median ICC %{y:.2f}<extra></extra>'))
    fig.update_yaxes(range=[-0.1, 1], title='median ICC over seeds 1-3')
    add('Validation', 'Seed stability (V2) by family', f"Unit: fixture (same map, bots and seats) x 3 seeds, {int(STAB['fixtures'].max()) if len(STAB) else 0} fixtures. "
        'ICC = share of variance that is between fixtures; near 1 = the feature measures the matchup, near 0 = it measures the seed.', theme(fig, 340))
    fig = make_subplots(rows=1, cols=3, subplot_titles=['EPG access vs bed eats in next 10 rounds', 'Enclosure: death hazard by reach', 'Bed territory vs next bed-pearl share'])
    fig.add_trace(go.Bar(x=[f"tau {e['tau']}" for e in val['epg_calibration']], y=[e['mean_within_map_r'] for e in val['epg_calibration']], marker_color=CAT[0],
                         showlegend=False, hovertemplate='%{x}: r=%{y:.2f}<extra></extra>'), 1, 1)
    if haz is not None:
        fig.add_trace(go.Bar(x=list(haz.index), y=haz['per1k'], marker_color=CAT[7], showlegend=False,
                             customdata=np.stack([haz['deaths'], haz['exposure']], 1),
                             hovertemplate='reach %{x}: %{y:.1f} deaths per 1k dragon-turns (%{customdata[0]} deaths / %{customdata[1]:.0f})<extra></extra>'), 1, 2)
    smp = tr.sample(min(3000, len(tr)), random_state=1) if len(tr) else tr
    if len(smp):
        fig.add_trace(go.Scattergl(x=smp['terr'], y=smp['share'], mode='markers', marker=dict(size=5, color=CAT[2], opacity=.25), showlegend=False,
                                   hovertemplate='territory %{x:.2f}, next share %{y:.2f}<extra></extra>'), 1, 3)
    add('Validation', 'Proximal checks (V3): do the constructed measures predict what they claim?',
        f"Left: mean within-map correlation of access (sampled every 5 rounds, per side) with bed pearls eaten in the next 10 rounds. Middle: non-suicide deaths per 1k "
        f"dragon-turns by cells reachable in 5 steps (exposure sampled every 5 rounds). Right: A-side bed territory vs A's share of bed pearls eaten in the next 10 rounds "
        f"(r = {val.get('territory_vs_next_bed_share_r', {}).get('terr', float('nan')):.2f}; plain cell territory r = {val.get('territory_vs_next_bed_share_r', {}).get('cells', float('nan')):.2f}; "
        f"logistic expected share r = {val.get('territory_vs_next_bed_share_r', {}).get('exp', float('nan')):.2f}). Density ratio vs a dragon's pearls per 100 turns: "
        f"Spearman {val.get('density_vs_eats_spearman', float('nan')):.2f}.", theme(fig, 380))

    # ---- deaths, sonar by bot ----
    cls = ['wall', 'self', 'ally_body', 'enemy_body', 'h2h_enemy', 'h2h_ally', 'suicide', 'invalid']
    d = F1.groupby('bot')[[f'death_{c}_per1k' for c in cls]].mean().reindex(bots)
    fig = go.Figure([go.Bar(x=[short(b) for b in bots], y=d[f'death_{c}_per1k'], name=c, marker_color=CAT[i],
                            hovertemplate='%{x}: %{y:.1f} per 1k ' + c + '<extra></extra>') for i, c in enumerate(cls)])
    fig.update_layout(barmode='stack')
    fig.update_yaxes(title='deaths per 1k dragon-turns')
    add('Deaths & sonar', 'How each bot dies', 'Mean over side-games (seed 1). Credit: a body death belongs to the body hit; h2h to the other head.', theme(fig, 380))
    kinds = ['kelp', 'ally', 'ally_head', 'enemy', 'enemy_head', 'empty']
    d = F1.groupby('bot')[[f'ray_hit_{k}_share' for k in kinds] + ['rays_per_dt', 'rays_toward_com_share', 'rays_away_com_share']].mean().reindex(bots)
    fig = make_subplots(rows=1, cols=2, subplot_titles=['What rays hit (share of rays)', 'Rays per dragon-turn and aim'], horizontal_spacing=0.08)
    for i, k in enumerate(kinds):
        fig.add_trace(go.Bar(x=[short(b) for b in bots], y=d[f'ray_hit_{k}_share'], name=k, marker_color=CAT[i], legendgroup='hit'), 1, 1)
    fig.add_trace(go.Bar(x=[short(b) for b in bots], y=d['rays_per_dt'], name='rays / dragon-turn', marker_color=CAT[6]), 1, 2)
    fig.update_layout(barmode='stack')
    add('Deaths & sonar', 'Sonar use by bot', 'Mean over side-games (seed 1). A ray stops at the first kelp or body; "enemy" hits are information leaked to the opponent.', theme(fig, 380))
    # fingerprint heatmap
    hf = [f for f, _ in HEADLINE if f in F1] + ['sprint_share', 'child_len_median', 'pearls_ally_corpse_share', 'corpse_recovered_share', 'contact_share_mean', 'density_ratio_mean']
    Z = within_map_z(F1, hf).assign(bot=F1['bot'].values).groupby('bot').mean().reindex(bots)
    fig = go.Figure(go.Heatmap(z=Z.values.T, x=[short(b) for b in bots], y=hf, zmid=0, zmin=-1.5, zmax=1.5,
                               colorscale=[[0, '#e34948'], [0.5, '#f0efec'], [1, '#2a78d6']], hovertemplate='%{x} · %{y}: %{z:.2f} sd<extra></extra>'))
    add('Deaths & sonar', 'Style fingerprint: bot means in within-map standard deviations', 'Unit: side-game (seed 1). Blue = above the map average, red = below.', theme(fig, 620))

    # ---- assemble ----
    n_games = F1['game'].nunique()
    v0 = val.get('v0', {})
    v0txt = ', '.join(f"{k.replace('_', ' ')} {v:.1%}" for k, v in v0.items())
    toc = []
    body = []
    sec = None
    for i, (section, title, caption, div) in enumerate(figs):
        if section != sec:
            sec = section
            body.append(f'<h2 id="s-{section.lower().replace(" ", "-").replace("&", "")}">{section}</h2>')
            toc.append(f'<a href="#s-{section.lower().replace(" ", "-").replace("&", "")}">{section}</a>')
        body.append(f'<figure class="card"><figcaption><h3>{title}</h3><p>{caption}</p></figcaption>{div}</figure>')
    notes = open(a.notes).read() if a.notes and os.path.exists(a.notes) else ''
    return f"""<title>F1 Feature Lab</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500&display=swap">
<style>
:root {{ --bg:#f5f6f4; --card:#ffffff; --ink:#15191b; --ink2:#51585d; --line:rgba(40,52,58,.14); --accent:#2a78d6; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ color-scheme:dark; --bg:#111415; --card:#191d1f; --ink:#eef1f2; --ink2:#a7afb3; --line:rgba(200,215,220,.14); --accent:#3987e5; }} }}
:root[data-theme="dark"] {{ color-scheme:dark; --bg:#111415; --card:#191d1f; --ink:#eef1f2; --ink2:#a7afb3; --line:rgba(200,215,220,.14); --accent:#3987e5; }}
body {{ background:var(--bg); color:var(--ink); font:15px/1.55 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif; margin:0; }}
main {{ max-width:1180px; margin:0 auto; padding-inline:16px; padding-block:28px 80px; }}
h1, h2, h3 {{ font-family:"IBM Plex Sans Condensed","IBM Plex Sans",system-ui,sans-serif; text-wrap:balance; }}
h1 {{ font-size:30px; font-weight:600; margin:0 0 8px; letter-spacing:-.01em; }}
h2 {{ font-size:21px; font-weight:600; margin:40px 0 8px; padding-top:18px; border-top:1px solid var(--line); scroll-margin-top:56px; }}
h3 {{ font-size:16px; font-weight:600; margin:0 0 4px; }}
p {{ color:var(--ink2); margin:4px 0; max-width:78ch; }}
code {{ font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:.9em; }}
nav {{ position:sticky; top:env(safe-area-inset-top,0px); z-index:5; background:var(--bg); display:flex; flex-wrap:wrap; gap:6px 16px; padding-block:10px; border-bottom:1px solid var(--line); }}
nav a {{ color:var(--ink2); text-decoration:none; font-size:13px; text-transform:uppercase; letter-spacing:.06em; }} nav a:hover, nav a:focus-visible {{ color:var(--accent); }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:8px; margin:14px 0; padding:14px 14px 6px; }}
.card figcaption p {{ font-size:13px; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:10px; margin:18px 0 8px; }}
.kpi {{ border-left:3px solid var(--accent); padding:2px 12px; }}
.kpi b {{ display:block; font:600 24px "IBM Plex Sans Condensed",system-ui,sans-serif; font-variant-numeric:tabular-nums; }} .kpi span {{ color:var(--ink2); font-size:12px; }}
.notes {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px 18px; margin:16px 0; }}
.notes li {{ margin:6px 0; color:var(--ink); max-width:95ch; }} .notes h3 {{ margin-top:8px; }}
.tbl {{ overflow:auto; max-height:420px; }} table {{ border-collapse:collapse; font-size:13px; width:100%; font-variant-numeric:tabular-nums; }}
th, td {{ text-align:left; padding:4px 8px; border-bottom:1px solid var(--line); white-space:nowrap; }} th {{ position:sticky; top:0; background:var(--card); }}
.js-plotly-plot {{ max-width:100%; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@{_pjs_version()}/plotly.min.js"></script>
<main>
<h1>{a.title}</h1>
<p>Seeded round robin of {F1['bot'].nunique()} bots on {len(maps)} live maps, both seats, {F1['toolkit'].iloc[0] if 'toolkit' in F1 else 'unswbc ?'}, seed 1
({n_games} games); seeds 2-3 on four pairs for stability ({F['game'].nunique() - n_games} games). Every number is regenerated by
<code>python -m tools.analysis.features extract … && python -m tools.analysis.features.report …</code>.</p>
<div class="kpis">
<div class="kpi"><b>{n_games}</b><span>seed-1 games</span></div>
<div class="kpi"><b>{len(F1)}</b><span>side-games (unit of most tables)</span></div>
<div class="kpi"><b>{len([c for c in F1.columns if c in REGISTRY])}</b><span>registered features</span></div>
<div class="kpi"><b>{min(v0.values()) if v0 else float('nan'):.1%}</b><span>worst V0 identity pass rate</span></div>
<div class="kpi"><b>{val.get('probe', '—')}</b><span>V1 probe checks passed</span></div>
</div>
<p>V0 bookkeeping identities (share of side-games passing exactly): {v0txt}.</p>
{notes}
<nav>{''.join(toc)}</nav>
{''.join(body)}
</main>"""


def _pjs_version():
    from plotly.offline import get_plotlyjs_version
    return get_plotlyjs_version()   # the figures' JSON needs the plotly.js this plotly.py was built against


def inline_plotly(html):
    """swap the CDN tag for the bundled plotly.js (for hosts that block CDNs or pin other versions)"""
    import re, plotly
    js = plotly.offline.get_plotlyjs().replace('\ufffd', '\\ufffd')
    return re.sub(r'<script src="https://cdn.jsdelivr.net/npm/plotly[^"]*"></script>', lambda m: '<script>' + js + '</script>', html)


def BIN_(p):
    return f'{5 / (1 - p):.0f}' if p < 1 else '∞'


def _rgba(h, a):
    h = h.lstrip('#')
    return f'rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})'


def _pct(x):
    return '—' if x is None or x != x else f'{x:.0%}'


if __name__ == '__main__':
    main()
