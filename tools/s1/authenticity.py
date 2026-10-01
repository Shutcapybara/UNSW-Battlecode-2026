"""Authenticity tags for live replays: is this side-game the bot the team's rating belongs to?  (S1-F step 1)

  python3 tools/s1/authenticity.py build      -> build/s1/corpus/authenticity.parquet
  python3 tools/s1/authenticity.py report

Anchor: a team's ranked games in the same version window (UTC day; neighbouring days pooled when a day has < 12 ranked
side-games). Fingerprint: features that are implementation constants and pass an outcome-invariance screen (within-team
ranked winners vs losers, median KS < 0.15). Score: robust distance to the anchor (median / MAD per feature, MAD floored
by the typical within-team MAD), calibrated against the anchor's own leave-one-out distances -> p_real (1 = typical of the
ranked bot). Decoy = p_real < 0.05 inside a team-day whose low-p unranked games also under-perform Elo by >= 0.15 (n >= 15).
The result and the win rate are never inputs to the per-game score.
"""
import json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT); sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import numpy as np
import pandas as pd

OUT = ROOT / 'build' / 's1' / 'corpus' / 'authenticity.parquet'
CAND = ['ray_refracted_share', 'rays_N_share', 'rays_E_share', 'rays_S_share', 'rays_W_share', 'rays_toward_enemy_share',
        'rays_away_enemy_share', 'rays_toward_com_share', 'death_suicide_per1k', 'death_invalid_per1k',
        'child_len_1_2_share_0_150', 'child_len_3_3_share_0_150', 'child_len_4_5_share_0_150', 'first_split',
        'log_rays', 'has_rays', 'sprint_share', 'splits_0_50', 'transits@50', 'first_pearl']
MIN_RANKED = 12


def load():
    import duckdb
    cols = ', '.join(f's."{c}"' for c in CAND if c not in ('log_rays', 'has_rays'))
    df = duckdb.sql(f"""select s.game, s.side, s.team, s.map, s.won::double as won, s.rays_per_dt, {cols},
        g.ranked, g.autoscrim, g.started_at,
        case when s.side = 'A' then g.elo_a else g.elo_b end as elo_me, case when s.side = 'A' then g.elo_b else g.elo_a end as elo_op
        from read_parquet('build/s1/corpus/sides/*.parquet', union_by_name=true) s join 'build/s1/corpus/games.parquet' g using (game)""").df()
    df['log_rays'] = np.log1p(df.rays_per_dt.fillna(0))
    df['has_rays'] = (df.rays_per_dt.fillna(0) > 0.5).astype(float)
    df['ex'] = 1 / (1 + 10 ** (-(df.elo_me - df.elo_op) / 400))
    df['day'] = pd.to_datetime(df.started_at, utc=True).dt.strftime('%m-%d')
    return df


def ks(a, b):
    a, b = np.sort(a[~np.isnan(a)]), np.sort(b[~np.isnan(b)])
    if len(a) < 8 or len(b) < 8:
        return np.nan
    x = np.concatenate([a, b])
    return float(np.max(np.abs(np.searchsorted(a, x, 'right') / len(a) - np.searchsorted(b, x, 'right') / len(b))))


def screen(df):
    R = df[df.ranked]
    rows = []
    for f in CAND:
        k = [ks(g[g.won > .5][f].values.astype(float), g[g.won < .5][f].values.astype(float)) for _, g in R.groupby('team')]
        within = R.groupby('team')[f].apply(lambda s: np.nanmedian(np.abs(s - s.median()))).median()
        between = R.groupby('team')[f].median().std()
        rows.append(dict(feature=f, outcome_ks=np.nanmedian(k), within_mad=within, between_sd=between,
                         ratio=between / (1.4826 * within + 1e-9)))
    S = pd.DataFrame(rows)
    S['keep'] = (S.outcome_ks < 0.15) & (S.ratio > 0.5)
    return S


def anchors(df):
    """reference rows per (team, day): ranked games that day, widened to +-1 day when thin"""
    R = df[df.ranked]
    days = sorted(df.day.unique())
    ref = {}
    for (t, d), _ in df.groupby(['team', 'day']):
        i = days.index(d)
        for w in (0, 1, 2):
            win = set(days[max(0, i - w): i + w + 1])
            r = R[(R.team == t) & R.day.isin(win)]
            if len(r) >= MIN_RANKED:
                ref[(t, d)] = (r, w)
                break
    return ref


def score(df, feats, floor):
    ref = anchors(df)
    df['p_real'], df['dist'], df['window'], df['enrich'] = np.nan, np.nan, np.nan, np.nan
    for (t, d), idx in df.groupby(['team', 'day']).groups.items():
        if (t, d) not in ref:
            continue
        r, w = ref[(t, d)]
        X = r[feats].astype(float)
        med = X.median()
        mad = np.maximum(1.4826 * (X - med).abs().median(), floor)
        def dist(Y):
            z = ((Y.astype(float) - med) / mad).abs().clip(upper=6)
            return z.mean(axis=1, skipna=True)
        # leave-one-out calibration on the anchor (approximate: distances of anchor rows to the anchor median)
        dref = np.sort(dist(X).values)
        dg = dist(df.loc[idx, feats])
        df.loc[idx, 'dist'] = dg.values
        df.loc[idx, 'p_real'] = 1 - np.searchsorted(dref, dg.values, 'right') / (len(dref) + 1)
        df.loc[idx, 'window'] = w
        # neighbourhood layer: share of ranked games among the k nearest team-window games, relative to the base rate.
        # A decoy bot forms its own cluster that ranked games never visit (enrichment ~ 0); a real bot's unranked games
        # sit among its ranked ones whatever the game length or result.
        pool = df[(df.team == t) & df.day.isin(sorted({x for x in df.day.unique()
                    if abs(int(x[-2:]) - int(d[-2:])) <= max(w, 0)} | {d}))]
        Zp = (((pool[feats].astype(float) - med) / mad).clip(-6, 6)).fillna(0).values
        Zg = (((df.loc[idx, feats].astype(float) - med) / mad).clip(-6, 6)).fillna(0).values
        rk = pool.ranked.values
        base = rk.mean()
        k = int(min(25, max(5, len(pool) // 10)))
        enr = np.empty(len(Zg))
        for j0 in range(0, len(Zg), 500):
            D = np.abs(Zg[j0:j0 + 500, None, :] - Zp[None, :, :]).mean(-1)
            D[D == 0] = 1e-9 * np.random.default_rng(0).random(D[D == 0].shape)  # ties among identical fingerprints
            nn = np.argsort(D, 1)[:, 1:k + 1]
            enr[j0:j0 + 500] = rk[nn].mean(1) / max(base, 1e-9)
        df.loc[idx, 'enrich'] = enr
    return df


def flag(df):
    df['decoy'] = False
    df['team_day_flag'] = False
    U = df[~df.ranked & df.p_real.notna()]
    for (t, d), g in U.groupby(['team', 'day']):
        lo = g[g.enrich < 0.25]
        if len(lo) >= 15 and (lo.won - lo.ex).mean() <= -0.15:
            df.loc[lo.index, 'decoy'] = True
            df.loc[g.index, 'team_day_flag'] = True
    df['authentic'] = df.ranked | ((df.enrich >= 0.5) & ~df.decoy)
    return df


def cmd_build():
    df = load()
    S = screen(df)
    feats = S[S.keep].feature.tolist()
    floor = pd.Series({r.feature: max(1.4826 * r.within_mad, 0.25 * r.between_sd, 1e-3) for r in S.itertuples()})[feats]
    df = flag(score(df, feats, floor))
    keep = ['game', 'side', 'team', 'map', 'day', 'ranked', 'autoscrim', 'won', 'ex', 'p_real', 'dist', 'window', 'enrich', 'decoy',
            'team_day_flag', 'authentic', 'rays_per_dt'] + feats
    df[keep].to_parquet(OUT)
    S.to_csv(OUT.with_name('authenticity_features.csv'), index=False)
    print(S.round(3).to_string(index=False))
    print('fingerprint features:', feats)
    print(f'wrote {OUT} ({len(df)} side-games)')


def cmd_report():
    df = pd.read_parquet(OUT)
    U = df[~df.ranked & df.p_real.notna()]
    print(f'unranked side-games with an anchor: {len(U)} of {(~df.ranked).sum()}; ranked {df.ranked.sum()}')
    print('share p_real < 0.05 among unranked: %.3f (5 %% expected if unranked = ranked bot); enrichment < 0.25: %.3f' % ((U.p_real < .05).mean(), (U.enrich < .25).mean()))
    g = U.groupby('team').agg(n=('p_real', 'size'), low=('enrich', lambda s: (s < .25).mean()), decoy=('decoy', 'mean'),
                              resid_low=('won', lambda s: np.nan), auth=('authentic', 'mean'))
    for t, x in U.groupby('team'):
        lo, hi = x[x.enrich < .25], x[x.enrich >= .5]
        g.loc[t, 'resid_low'] = (lo.won - lo.ex).mean() if len(lo) >= 10 else np.nan
        g.loc[t, 'resid_auth'] = (hi.won - hi.ex).mean() if len(hi) >= 10 else np.nan
    g['resid_all'] = U.groupby('team').apply(lambda x: (x.won - x.ex).mean())
    print(g.sort_values('decoy', ascending=False).round(2).head(15).to_string())
    print('\ncontrols (|unranked residual| < 0.05, n >= 100): mean low-p share %.3f, decoy share %.3f' % tuple(
        g[(g.resid_all.abs() < .05) & (g.n >= 100)][['low', 'decoy']].mean()))
    s = df[(df.team == '91') & ~df.ranked & df.p_real.notna()]
    silent = s.rays_per_dt < 1
    print('\nSSS unranked: sonar-silent %d, flagged decoy %.2f / enrich<.25 %.2f; sonar-active %d, flagged %.2f / enrich<.25 %.2f' % (
        silent.sum(), s[silent].decoy.mean(), (s[silent].enrich < .25).mean(), (~silent).sum(), s[~silent].decoy.mean(),
        (s[~silent].enrich < .25).mean()))
    print('\ndecoy side-games by team:', df[df.decoy].team.value_counts().to_dict())
    print('authentic share of all side-games: %.3f' % df.authentic.mean())


if __name__ == '__main__':
    {'build': cmd_build, 'report': cmd_report}[sys.argv[1]]()
