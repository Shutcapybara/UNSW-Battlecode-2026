"""Benchmark-feature screen: which metrics are safe to compare on and to optimise locally.

python -m tools.analysis.features.benchmarks --zoo build/zoo/z1/features --field 'DIR*' --index … --ladder … --out OUT

For each candidate metric (raw, relative to the opponent, normalised by map, and both):
  zoo  seed ICC (80 fixtures x 3 seeds)             -> how much of a side-game is the seed
       within-map variance shares: bot / opponent / residual (seed 1)   -> what an optimiser can move vs what it cannot
       cross-map consistency: leave-one-map-out correlation of bot means -> does a gain on 9 maps carry to the 10th
       win signal beyond the zoo rating (log-odds per within-map sd)
  field win signal beyond Elo; team share of within-map variance; cross-map consistency of team means (teams >= 40 games)
  both  side-games needed to resolve a 0.2 between-bot-sd change at 80% power (from the residual sd)
Units: side-game unless named.
"""
import argparse, glob, json, math, os

import numpy as np
import pandas as pd

from .compare import attach_meta, load_runs, beyond_elo, zscore_by_map
from .report import bradley_terry, beyond_rating

AVOIDABLE = ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k', 'death_invalid_per1k']


def derive(F, ref_medians=None):
    """add candidate variants; ref_medians = per-map medians used for map normalisation (fixed external reference)"""
    F = F.copy()
    F['avoidable_deaths_per1k'] = F[AVOIDABLE].fillna(0).sum(axis=1)
    F['avoidable_death_share'] = np.where(F['deaths_per1k'] > 0, F['avoidable_deaths_per1k'] / F['deaths_per1k'], np.nan)
    F['enemy_caused_deaths_per1k'] = F[['death_enemy_body_per1k', 'death_h2h_enemy_per1k']].fillna(0).sum(axis=1)
    for c in (50, 100, 150, 250):
        F[f'bed_yield@{c}'] = F[f'bed_pearls@{c}'] / (F['bed_capacity'] * c)            # map-normalised by construction
    F['pearls_per100dt_0_100'] = F['pearls_per100dt_0_100']
    # relative (opponent) versions: ours / (ours + theirs) within the game
    key = ['game']
    for c in ('pearls@50', 'pearls@100', 'pearls@150', 'pearls@250', 'bed_pearls@100', 'pearls_per100dt_0_100', 'avoidable_deaths_per1k',
              'deaths_per1k', 'births@100'):
        other = F[key + ['side', c]].copy()
        other['side'] = other['side'].map({'A': 'B', 'B': 'A'})
        m = F[key + ['side']].merge(other, on=key + ['side'], how='left')[c].to_numpy(float)
        a = F[c].to_numpy(float)
        F[f'{c}|rel'] = np.where(a + m > 0, a / (a + m), 0.5)
    # map-normalised versions: value / per-map reference median
    if ref_medians is not None:
        for c in ('pearls@50', 'pearls@100', 'pearls@150', 'pearls@250', 'total@100', 'units@100', 'avoidable_deaths_per1k',
                  'pearls_per100dt_0_100', 'births@100'):
            med = F['map'].map(ref_medians[c]).replace(0, np.nan)
            F[f'{c}|map'] = F[c] / med
    return F


CANDIDATES = [
    # (name, family, kind)
    ('pearls@100', 'economy', 'raw'), ('pearls@100|map', 'economy', 'map'), ('pearls@100|rel', 'economy', 'relative'),
    ('pearls@50|rel', 'economy', 'relative'), ('pearls@150|rel', 'economy', 'relative'), ('pearls@250|rel', 'economy', 'relative'),
    ('pearls@50|map', 'economy', 'map'), ('pearls@150|map', 'economy', 'map'), ('pearls@250|map', 'economy', 'map'),
    ('bed_yield@100', 'economy', 'capacity'), ('bed_yield@250', 'economy', 'capacity'), ('bed_pearls@100|rel', 'economy', 'relative'),
    ('pearls_per100dt_0_100', 'economy', 'rate'), ('pearls_per100dt_0_100|rel', 'economy', 'relative'), ('pearls_per100dt_0_100|map', 'economy', 'map'),
    ('pearls_per100dt_100_250', 'economy', 'rate'), ('bed_capture_share', 'economy', 'relative'), ('epg_conversion', 'economy', 'rate'),
    ('total@100', 'material', 'raw'), ('total@100|map', 'material', 'map'), ('total_share@100', 'material', 'relative'),
    ('units@100|map', 'material', 'map'), ('units_share@100', 'material', 'relative'), ('total_share@250', 'material', 'relative'),
    ('territory@100', 'space', 'relative'), ('seen_share@100', 'space', 'capacity'), ('top1_share@100', 'concentration', 'raw'),
    ('births@100|map', 'production', 'map'), ('births@100|rel', 'production', 'relative'), ('newborn_deaths10_per100', 'production', 'rate'),
    ('deaths_per1k', 'survival', 'rate'), ('deaths_per1k|rel', 'survival', 'relative'),
    ('avoidable_deaths_per1k', 'survival', 'rate'), ('avoidable_deaths_per1k|map', 'survival', 'map'), ('avoidable_deaths_per1k|rel', 'survival', 'relative'),
    ('avoidable_death_share', 'survival', 'rate'), ('death_wall_per1k', 'survival', 'rate'), ('death_self_per1k', 'survival', 'rate'),
    ('death_ally_body_per1k', 'survival', 'rate'), ('death_h2h_ally_per1k', 'survival', 'rate'), ('death_invalid_per1k', 'survival', 'rate'),
    ('enemy_caused_deaths_per1k', 'survival', 'rate'), ('death_rate_enclosed_per1k', 'risk', 'rate'), ('enclosed_share_mean', 'risk', 'rate'),
    ('kill_length_ratio', 'fighting', 'relative'), ('sprint_cost_per_pearl', 'movement', 'rate'),
]


# field-relative yardsticks: per map, where does a side sit against the field and against the top of the field?
FIELD_REL = [('pearls@50', 'up'), ('pearls@100', 'up'), ('pearls@150', 'up'), ('pearls@250', 'up'), ('units@100', 'up'),
             ('total@100', 'up'), ('births@100', 'up'), ('avoidable_deaths_per1k', 'down'), ('death_wall_per1k', 'down'),
             ('death_self_per1k', 'down'), ('death_ally_body_per1k', 'down'), ('death_h2h_ally_per1k', 'down')]


def field_refs(Fd, top_ids):
    """per map and metric: field median, p10, p25, p75, p90, and the median of the top-10 teams' side-games"""
    out = {}
    for c, _ in FIELD_REL:
        out[c] = {}
        for mp, g in Fd.groupby('map'):
            x = g[c].astype(float).dropna()
            t = g[g['team'].isin(top_ids)][c].astype(float).dropna()
            out[c][mp] = dict(median=float(x.median()), p10=float(x.quantile(.1)), p25=float(x.quantile(.25)), p75=float(x.quantile(.75)),
                              p90=float(x.quantile(.9)), top10=float(t.median()) if len(t) >= 10 else float('nan'), n=int(len(x)),
                              sorted=np.sort(x.to_numpy()))
    return out


def apply_field_rel(F, refs):
    """adds |top (ratio to top-10 median, up metrics), |p90 (ratio to field 90th percentile, up metrics),
    |xs (excess over the field median, down metrics), |xstop (excess over the top-10 median, down metrics),
    |pct (percentile in the field on the same map, oriented so higher = better, all metrics)"""
    F = F.copy()
    for c, d in FIELD_REL:
        mp = F['map']
        get = lambda k: mp.map({m: v[k] for m, v in refs[c].items()}).astype(float)
        x = F[c].astype(float)
        if d == 'up':
            F[f'{c}|top'] = x / get('top10').replace(0, np.nan)
            F[f'{c}|p90'] = x / get('p90').replace(0, np.nan)
        else:
            F[f'{c}|xs'] = x - get('median')
            F[f'{c}|xstop'] = x - get('top10')
        pct = np.full(len(F), np.nan)
        for m, ref in refs[c].items():
            idx = np.where((mp == m).to_numpy() & x.notna().to_numpy())[0]
            if len(idx) and ref['n']:
                v = x.to_numpy()[idx]
                lo = np.searchsorted(ref['sorted'], v, 'left')
                hi = np.searchsorted(ref['sorted'], v, 'right')
                q = (lo + hi) / 2 / ref['n']                       # mid-rank percentile among field sides on this map
                pct[idx] = q if d == 'up' else 1 - q
        F[f'{c}|pct'] = pct
    return F


def var_shares(F, f, who='bot'):
    d = F[['map', who, 'opponent' if who == 'bot' else 'opp_team', f]].dropna()
    if len(d) < 50 or d[f].std() == 0:
        return dict(share_map=np.nan, share_bot=np.nan, share_opp=np.nan, share_resid=np.nan, resid_sd=np.nan, bot_sd=np.nan)
    opp = 'opponent' if who == 'bot' else 'opp_team'
    x = d[f].astype(float)
    tot = ((x - x.mean()) ** 2).sum()
    mm = d.groupby('map')[f].transform('mean')
    bm = d.groupby(['map', who])[f].transform('mean')
    r1 = x - bm
    om = r1.groupby([d['map'], d[opp]]).transform('mean')
    res = r1 - om
    bot_ss, opp_ss, res_ss = ((bm - mm) ** 2).sum(), (om ** 2).sum(), (res ** 2).sum()
    return dict(share_map=float(((mm - x.mean()) ** 2).sum() / tot), share_bot=float(bot_ss / tot), share_opp=float(opp_ss / tot),
                share_resid=float(res_ss / tot), resid_sd=float(res.std()), bot_sd=float((bm - mm).std()))


def seed_icc(F, f):
    d = F[['fixture', f]].dropna()
    g = [v.to_numpy(float) for _, v in d.groupby('fixture')[f] if len(v) >= 2]
    if len(g) < 10:
        return np.nan
    k = np.mean([len(v) for v in g])
    grand = np.concatenate(g).mean()
    msb = sum(len(v) * (v.mean() - grand) ** 2 for v in g) / (len(g) - 1)
    msw = sum(((v - v.mean()) ** 2).sum() for v in g) / (sum(len(v) for v in g) - len(g))
    return float((msb - msw) / (msb + (k - 1) * msw)) if msb + (k - 1) * msw > 0 else np.nan


def cross_map(F, f, who, min_n=5):
    """mean over maps of corr(unit mean on this map, unit mean on all other maps), units with >= min_n games on both"""
    d = F[['map', who, f]].dropna()
    rs = []
    for mp in d['map'].unique():
        a = d[d['map'] == mp].groupby(who)[f].agg(['mean', 'size'])
        b = d[d['map'] != mp].groupby(who)[f].agg(['mean', 'size'])
        j = a.join(b, lsuffix='_m', rsuffix='_o', how='inner')
        j = j[(j['size_m'] >= min_n) & (j['size_o'] >= min_n)]
        if len(j) >= 5 and j['mean_m'].std() > 0 and j['mean_o'].std() > 0:
            rs.append(j['mean_m'].rank().corr(j['mean_o'].rank()))
    return float(np.mean(rs)) if rs else np.nan


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--zoo', required=True)
    ap.add_argument('--field', required=True)
    ap.add_argument('--index', required=True)
    ap.add_argument('--ladder', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    Z = pd.read_parquet(os.path.join(a.zoo, 'features.parquet'))
    Z['fixture'] = Z['game'].str.replace(r'^s\d+__', '', regex=True) + '|' + Z['side']
    dirs = sorted(sum((glob.glob(x) for x in a.field.split(',')), []))
    Fd = load_runs(dirs, 'features')
    Fd['game'] = Fd['game'].astype(str)
    Fd, latest = attach_meta(Fd, a.index, a.ladder)
    if 'dragons_start' in Fd:
        Fd.loc[(Fd['map'] == 'Prisoners Dilemma') & (Fd['dragons_start'] == 10), 'map'] = 'Prisoners Dilemma 10'
    Fd = Fd[(Fd['team'] != 7) & (Fd['opp_team'] != 7) & Fd['team'].notna()].copy()
    Fd['bed_capacity'] = Fd['bed_capacity'].astype(float)
    # reference medians per map = the field's (external anchor, fixed): the same yardstick for zoo and field
    tmp = derive(Fd)
    tmp['avoidable_deaths_per1k'] = tmp['avoidable_deaths_per1k']
    ref = {c: tmp.groupby('map')[c].median() for c in ('pearls@50', 'pearls@100', 'pearls@150', 'pearls@250', 'total@100', 'units@100',
                                                        'avoidable_deaths_per1k', 'pearls_per100dt_0_100', 'births@100')}
    Z = derive(Z, ref)
    Fd = derive(Fd, ref)
    top_ids = [t for t, v in sorted(latest.items(), key=lambda kv: kv[1][1]) if t != 7][:10]
    refs = field_refs(Fd, top_ids)
    Z = apply_field_rel(Z, refs)
    Fd = apply_field_rel(Fd, refs)
    extra = []
    for c, d in FIELD_REL:
        fam = 'survival' if 'death' in c else 'economy'
        for suf in (('|top', '|p90', '|pct') if d == 'up' else ('|xs', '|xstop', '|pct')):
            extra.append((c + suf, fam, {'|top': 'top-relative', '|p90': 'field-p90', '|pct': 'field-percentile',
                                         '|xs': 'excess-over-field', '|xstop': 'excess-over-top'}[suf]))
    Z1 = Z[Z['game'].str.startswith('s1__')].copy()
    rating = bradley_terry(Z1)
    cands = [c for c in CANDIDATES + extra if c[0] in Z1.columns and c[0] in Fd.columns]
    feats = [c[0] for c in cands]
    zb = beyond_rating(Z1, feats, rating).set_index('feature')
    Zf = zscore_by_map(Fd, feats, Fd)
    fb, _ = beyond_elo(Fd, feats, Zf)
    fb = fb.set_index('feature')
    counts = Fd.groupby('team').size()
    big = counts[counts >= 40].index
    rows = []
    for name, fam, kind in cands:
        vz = var_shares(Z1, name, 'bot')
        vf = var_shares(Fd.assign(bot=Fd['team'], opponent=Fd['opp_team']), name, 'bot')
        n80 = (2.8 * vz['resid_sd'] / (0.2 * vz['bot_sd'])) ** 2 * 2 if vz['bot_sd'] and vz['bot_sd'] > 0 else np.nan
        rows.append(dict(feature=name, family=fam, kind=kind,
                         zoo_seed_icc=seed_icc(Z, name), zoo_share_map=vz['share_map'], zoo_share_bot=vz['share_bot'], zoo_share_opp=vz['share_opp'],
                         zoo_share_resid=vz['share_resid'], zoo_cross_map=cross_map(Z1, name, 'bot'),
                         zoo_beta=zb['beta_per_sd'].get(name, np.nan), zoo_chi2=zb['lr_chi2'].get(name, np.nan),
                         field_beta=fb['beta_elo'].get(name, np.nan), field_chi2=fb['lr_chi2_elo'].get(name, np.nan),
                         field_share_map=vf['share_map'], field_share_team=vf['share_bot'], field_share_opp=vf['share_opp'],
                         field_cross_map=cross_map(Fd[Fd['team'].isin(big)], name, 'team'),
                         games_for_0p2sd=n80,
                         zoo_median=float(Z1[name].median()), field_median=float(Fd[name].median()),
                         field_win_median=float(Fd[Fd['result'] == 'win'][name].median()),
                         top10_median=float(Fd[Fd['team'].isin([t for t, v in sorted(latest.items(), key=lambda kv: kv[1][1]) if t != 7][:10])][name].median())))
    T = pd.DataFrame(rows)
    # team level: Spearman of a team's mean within-map z (teams with >= 40 side-games) with its latest rating
    tm = Zf[Fd['team'].isin(big)].groupby(Fd['team'])[feats].mean()
    rt = pd.Series({t: v[0] for t, v in latest.items()}).reindex(tm.index)
    T['team_rating_rho'] = T['feature'].map({f: tm[f].rank().corr(rt.rank()) for f in feats})
    T.to_csv(os.path.join(a.out, 'benchmark_screen.csv'), index=False)
    # per-map reference table for the chosen set (field medians / winners' medians / zoo medians)
    Z1.to_parquet(os.path.join(a.out, 'zoo_derived.parquet'), index=False)
    Fd[['game', 'side', 'map', 'team', 'result', 'elo'] + feats].to_parquet(os.path.join(a.out, 'field_derived.parquet'), index=False)
    json.dump({c: {k: float(v) for k, v in s.items()} for c, s in ref.items()}, open(os.path.join(a.out, 'map_reference_medians.json'), 'w'), indent=1)
    json.dump({c: {m: {k: v for k, v in r.items() if k != 'sorted'} for m, r in mp.items()} for c, mp in refs.items()},
              open(os.path.join(a.out, 'field_references.json'), 'w'), indent=1)
    json.dump({c: {m: r['sorted'].tolist() for m, r in mp.items()} for c, mp in refs.items()},
              open(os.path.join(a.out, 'field_distributions.json'), 'w'))
    pd.set_option('display.width', 250)
    print(T.round(2).to_string())


if __name__ == '__main__':
    main()
