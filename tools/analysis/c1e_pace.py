#!/usr/bin/env python3
"""C1-E field pace targets: aggregate the F1 feature parquets over corpus ranked games.

Builds the field's first-100/250-round pace profile by map and cohort (top 10, ranks 11-30,
band 55-85, team 7) plus the two comparisons the builders need: winner-minus-loser gaps at
r50/r100 within top-30 games, and team-7-minus-band gaps. Ranked games only; both sides
pooled. Cohorts come from the ladder snapshot nearest each game's start.

  python tools/analysis/c1e_pace.py --batches 'build/c1e/features-*' \
      --index build/c1e/ranked_games.jsonl --ladder public_replays/corpus/ladder \
      --out-md docs/analysis/C1-pace-targets.md --out-json game_stats/field_pace_targets.json

Every metric is defined in docs/analysis/FEATURES.md (F1 registry); this script only
aggregates, it never re-decodes.
"""
import argparse, glob, json, math, os, sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MAP_CLASS = {'Portals': 'compact', 'Prisoners Dilemma': 'compact', 'Devil': 'compact', 'Trophy': 'compact'}
DEATH_CLASSES = ('wall', 'self', 'ally_body', 'enemy_body', 'h2h_enemy', 'h2h_ally', 'suicide', 'invalid')
# series columns summed over rounds 0-99 (and 0-49 for the r50 pearl count)
SERIES_SUMS = ['moves', 'eats', 'dragon_turns', 'deaths', 'splits'] + ['death_' + c for c in DEATH_CLASSES]


def cohort_of(rank, team_id):
    if team_id == 7:
        return 'team7'
    if rank is None:
        return None
    if rank <= 10:
        return 'top10'
    if rank <= 30:
        return 'r11_30'
    if 55 <= rank <= 85:
        return 'band'
    return None


def load_ladders(ladder_dir):
    """[(utc_datetime, {team_id: rank})] sorted by snapshot stamp."""
    out = []
    for p in sorted(Path(ladder_dir).glob('*.json')):
        stamp = datetime.strptime(p.stem, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
        ranks = {e['id']: e['rank'] for e in json.load(open(p)) if not e.get('dev')}
        out.append((stamp, ranks))
    return out


def rank_at(ladders, team_id, when):
    """Rank of team in the latest snapshot at or before `when` (earliest snapshot if none yet)."""
    ranks = ladders[0][1]
    for stamp, r in ladders:
        if stamp <= when:
            ranks = r
        else:
            break
    return ranks.get(team_id)


def q(xs, p):
    xs = sorted(x for x in xs if x == x and x is not None)
    return xs[int(round(p * (len(xs) - 1)))] if xs else float('nan')


def cell(xs):
    """median (q1 - q3) with NaN dropped; n in brackets when values were missing."""
    vals = [x for x in xs if x == x and x is not None]
    if not vals:
        return '—'
    med, q1, q3 = q(vals, .5), q(vals, .25), q(vals, .75)
    txt = f'{fmt(med)} ({fmt(q1)}–{fmt(q3)})'
    if len(vals) < len(xs):
        txt += f' [{len(vals)}]'
    return txt


def fmt(x):
    if x != x:
        return '—'
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f'{x:.2f}' if abs(x) >= 1 else f'{x:.3f}'


def med(xs):
    return q(xs, .5)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--batches', default='build/c1e/features-*')
    ap.add_argument('--index', default='build/c1e/ranked_games.jsonl')
    ap.add_argument('--corpus-index', default='public_replays/corpus/index.jsonl')
    ap.add_argument('--ladder', default='public_replays/corpus/ladder')
    ap.add_argument('--out-md', default='docs/analysis/C1-pace-targets.md')
    ap.add_argument('--out-json', default='game_stats/field_pace_targets.json')
    ap.add_argument('--beds', default='game_stats/live_beds.json',
                    help='live bed-map reconstruction (tools/analysis/c1e_beds.py); rendered as its own section')
    a = ap.parse_args(argv)

    index_rows = [json.loads(l) for l in open(ROOT / a.index)]
    games = {r['game_id']: r for r in index_rows}
    corpus_lines = sum(1 for _ in open(ROOT / a.corpus_index))
    newest = max(r['fetched_at'] for r in (json.loads(l) for l in open(ROOT / a.corpus_index)))
    ladders = load_ladders(ROOT / a.ladder)

    feat = pd.concat([pd.read_parquet(Path(d) / 'features.parquet') for d in sorted(glob.glob(str(ROOT / a.batches)))
                      if (Path(d) / 'features.parquet').exists()], ignore_index=True)
    series = pd.concat([pd.read_parquet(Path(d) / 'series.parquet', columns=['game', 'side', 'round', 'units'] + SERIES_SUMS)
                        for d in sorted(glob.glob(str(ROOT / a.batches)))
                        if (Path(d) / 'series.parquet').exists()], ignore_index=True)
    feat['game'] = feat['game'].astype(int)
    series['game'] = series['game'].astype(int)

    # ---- per-round-window sums from the series ----
    s100 = series[series['round'] < 100].groupby(['game', 'side'], as_index=False)[SERIES_SUMS].sum()
    s100 = s100.rename(columns={c: c + '_100' for c in SERIES_SUMS})
    s50 = series[series['round'] < 50].groupby(['game', 'side'], as_index=False)['eats'].sum().rename(columns={'eats': 'eats_50'})
    # units at r200 (terminal state carried forward, same rule as the checkpoint features:
    # the row at round min(200, R))
    at_round = series[series['round'] <= 200]
    u200 = at_round.loc[at_round.groupby(['game', 'side'])['round'].idxmax(), ['game', 'side', 'units']] \
        .rename(columns={'units': 'units_r200'})

    df = feat.merge(s100, on=['game', 'side'], how='left').merge(s50, on=['game', 'side'], how='left') \
             .merge(u200, on=['game', 'side'], how='left')

    # ---- context join (teams, winner, autoscrim, cohorts) ----
    ctx = []
    for gid, r in games.items():
        when = datetime.fromisoformat(r['started_at'].replace('Z', '+00:00'))
        ra = rank_at(ladders, r['team_a'], when)
        rb = rank_at(ladders, r['team_b'], when)
        ctx.append(dict(game=gid, team_a=r['team_a'], team_b=r['team_b'], winner=r['winner'],
                        autoscrim=bool(r.get('autoscrim_window')), rank_a=ra, rank_b=rb,
                        cohort_a=cohort_of(ra, r['team_a']), cohort_b=cohort_of(rb, r['team_b']),
                        mirror=r['team_a'] == r['team_b']))
    ctx = pd.DataFrame(ctx)
    df = df.merge(ctx, on='game', how='left')

    def cohort_of_row(row):
        return row['cohort_a'] if row['side'] == 'A' else row['cohort_b']

    df['cohort'] = df.apply(cohort_of_row, axis=1)

    # ---- derived metrics (definitions follow the F1 registry) ----
    dt = df['dragon_turns_100'].where(df['dragon_turns_100'] > 0)
    df['pearls_r100'] = df['eats_100']
    df['pearls_r50'] = df['eats_50']
    df['pearls_per_dt_r100'] = df['eats_100'] / dt
    df['moves_per_pearl_r100'] = df['moves_100'] / df['eats_100'].where(df['eats_100'] > 0)
    df['splits_per100dt_r100'] = 100 * df['splits_100'] / dt   # churn rate, same 0-99 convention
    df['longest_r50'] = df['longest@50']   # only r100 is in STATS; the winner-loser gap also needs r50
    for c in DEATH_CLASSES:
        df['death_%s_per1k_r100' % c] = 1000 * df['death_' + c + '_100'] / dt
    df['deaths_per1k_r100'] = 1000 * df['deaths_100'] / dt
    # cross-check the series-derived rate against the checkpoint feature
    bad = (df['pearls_per_dt_r100'] - df['pearls_per100dt_0_100'] / 100).abs().fillna(0).max()
    assert bad < 1e-6, f'pearls/dt mismatch vs pearls_per100dt_0_100: {bad}'

    STATS = [('units_r25', 'units@25'), ('units_r50', 'units@50'), ('units_r100', 'units@100'),
             ('units_r200', 'units_r200'), ('total_r50', 'total@50'), ('total_r100', 'total@100'),
             ('total_r250', 'total@250'), ('longest_r100', 'longest@100'), ('splits_r100', 'splits_100'),
             ('first_pearl', 'first_pearl'), ('pearls_r100', 'pearls_r100'), ('pearls_r50', 'pearls_r50'),
             ('pearls_per_dt_r100', 'pearls_per_dt_r100'), ('moves_per_pearl_r100', 'moves_per_pearl_r100'),
             ('deaths_per1k_r100', 'deaths_per1k_r100')] + \
            [('death_%s_per1k_r100' % c, 'death_%s_per1k_r100' % c) for c in DEATH_CLASSES] + \
            [('units_share_r100', 'units_share@100'), ('total_share_r100', 'total_share@100'),
             ('territory_r50', 'territory@50'), ('territory_r100', 'territory@100'), ('territory_r250', 'territory@250'),
             ('bed_territory_r100', 'bed_territory@100'), ('bed_share_r100', 'bed_expected_share@100'),
             ('density_ratio_r100', 'density_ratio@100'), ('seen_share_r100', 'seen_share@100'),
             ('enclosed_share_r100', 'enclosed_share@100'), ('reach_mean_r100', 'reach_mean@100'),
             ('epg_tau2', 'epg_tau2'), ('epg_conversion', 'epg_conversion'), ('contact_share_mean', 'contact_share_mean'),
             ('splits_per100dt_r100', 'splits_per100dt_r100'), ('splits_0_50', 'splits_0_50'),
             ('splits_50_100', 'splits_50_100'), ('splits_100_250', 'splits_100_250'),
             ('splits_250_500', 'splits_250_500'), ('newborn_deaths10_per100', 'newborn_deaths10_per100'),
             ('peak_units', 'peak_units')]
    KEY2SRC = dict(STATS)
    # unify column names on the metric keys so every downstream use is name-identical to the JSON
    for k, src in STATS:
        if k != src:
            df[k] = df[src]

    df['map_class'] = df['map'].map(lambda m: MAP_CLASS.get(m, 'open'))
    cohorts = ['top10', 'r11_30', 'band', 'team7']

    def block(frame, key_cols):
        """{key: {cohort: {stat: median}}}"""
        out = {}
        for key, grp_key in frame.groupby(key_cols):
            key = key if isinstance(key, tuple) else (key,)
            d = out.setdefault(key, {})
            for c in cohorts:
                g = grp_key[grp_key['cohort'] == c]
                if not len(g):
                    continue
                d[c] = {'n_side_games': int(len(g))}
                for k, src in STATS:
                    d[c][k] = med(g[src].tolist())
        return out

    by_map = block(df, ['map'])
    by_class = block(df, ['map_class'])
    by_all = {'ALL': block(df.assign(_k='ALL'), ['_k'])[('ALL',)]}

    # ---- winner-minus-loser within top-30 games ----
    top30 = df[df['cohort'].isin(['top10', 'r11_30'])]
    pairs = top30.merge(top30, on='game', suffixes=('_w', '_l'))
    both = pairs[(pairs['side_w'] != pairs['side_l'])
                 & (pairs['winner_w'].str.lower() == pairs['side_w'].str.lower())]
    GAP_SRC = {('units', 50): 'units_r50', ('units', 100): 'units_r100',
               ('total', 50): 'total_r50', ('total', 100): 'total_r100',
               ('pearls', 50): 'pearls_r50', ('pearls', 100): 'pearls_r100',
               ('longest', 50): 'longest_r50', ('longest', 100): 'longest_r100'}
    gaps = pd.DataFrame({'game': both['game'], 'map_class': both['map_class_w']})
    for (k, r), src in GAP_SRC.items():
        gaps[f'{k}_r{r}'] = both[src + '_w'] - both[src + '_l']
    wl_all = {f'{k}_r{r}': med(gaps[f'{k}_r{r}'].tolist()) for k in ('units', 'total', 'pearls', 'longest') for r in (50, 100)}
    wl_class = {cls: {f'{k}_r{r}': med(gaps.loc[gaps['map_class'] == cls, f'{k}_r{r}'].tolist())
                      for k in ('units', 'total', 'pearls', 'longest') for r in (50, 100)}
                for cls in ('compact', 'open')}
    wl_n = int(len(gaps))

    # ---- team 7 minus band (pooled; per-class in the reading) ----
    t7 = df[df['cohort'] == 'team7']
    band = df[df['cohort'] == 'band']
    t7_band = {'n_team7': int(len(t7)), 'n_band': int(len(band))}
    for k, _ in STATS:
        t7_band[k] = med(t7[k].tolist()) - med(band[k].tolist())

    # ---- covariates: autoscrim window and side ----
    auto = {}
    for c in ('top10', 'r11_30', 'band'):
        g = df[df['cohort'] == c]
        auto[c] = {k: dict(zip(('in', 'out'), (med(g[g['autoscrim']][k].tolist()), med(g[~g['autoscrim']][k].tolist()))))
                   for k in ('units_r100', 'total_r100', 'pearls_per_dt_r100', 'moves_per_pearl_r100')}
    side_check = {k: dict(zip(('A', 'B'), (med(df[df['side'] == 'A'][k].tolist()), med(df[df['side'] == 'B'][k].tolist()))))
                  for k in ('units_r100', 'total_r100', 'pearls_per_dt_r100', 'first_pearl')}

    # ---- JSON ----
    out = {'_meta': {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'corpus_index_lines': corpus_lines, 'newest_fetched_at': newest,
        'ranked_side_games': int(len(df)), 'ranked_games': int(df['game'].nunique()),
        'index_games_without_features': int(len(games) - df['game'].nunique()),
        'mirror_games': int(df.drop_duplicates('game')['mirror'].sum()),
        'ladder_snapshots': len(ladders), 'ladder_last': ladders[-1][0].isoformat(),
        'definitions': 'docs/analysis/FEATURES.md (F1 registry); metrics at rX are rounds 0..X-1',
        'cohort_rule': 'team 7 fixed; top10 = rank<=10, r11_30 = 11-30, band = 55-85 in the ladder snapshot nearest game start',
    },
        '_winner_loser_gap_top30': {'n_games': wl_n, 'ALL': wl_all, 'by_class': wl_class},
        '_team7_minus_band': t7_band,
        '_autoscrim_covariate': auto, '_side_check': side_check}
    for m, d in by_map.items():
        out[m[0]] = d
    # class entries are descriptive only (director, 29 Sep: a class target held the bot back on
    # Schooltime) - never a sibling of the per-map keys the sweeps read
    out['_class_descriptive'] = {m[0]: d for m, d in by_class.items()}
    out.update(by_all)
    Path(ROOT / a.out_json).parent.mkdir(parents=True, exist_ok=True)

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, float) and o != o:
            return None
        return o

    json.dump(clean(out), open(ROOT / a.out_json, 'w'), indent=1, sort_keys=True, allow_nan=False)

    # ---- markdown ----
    COHORT_LABEL = {'top10': 'top 10', 'r11_30': 'ranks 11–30', 'band': 'band 55–85', 'team7': 'team 7'}
    L = []
    L.append('# C1-E — the field\'s pace targets (first 100/250 rounds, by cohort and map)')
    L.append('')
    L.append(f"Generated {out['_meta']['generated_at'][:19]}Z from the public corpus: index `{a.corpus_index}` "
             f"({corpus_lines} lines, newest `fetched_at` {newest}), {len(games)} ranked completed games, "
             f"{len(df)} side-games with features. Cohorts from {len(ladders)} ladder snapshots "
             f"(nearest game start; last {ladders[-1][0].isoformat()[:16]}Z). Ranked games only; both sides pooled. "
             'Cells are **median (q1–q3)**; bracketed counts appear when NaNs (never-ate, zero-denominator) were dropped. '
             'All metric definitions: `docs/analysis/FEATURES.md`.')
    L.append('')
    L.append('> Reading keys: units = living dragons at round start; total = summed length; pearls/dt = pearls per '
             'dragon-turn in rounds 0-99 (x100 for the per-100-dt display); moves/pearl = move commands per pearl eaten '
             'in rounds 0-99; deaths per 1k dragon-turns in rounds 0-99; by-r100 counters are rounds 0-99. The JSON '
             'medians the sweeps consume: `' + a.out_json + '` (`{"map": {"cohort": {"units_r100": ...}}}`).')
    L.append('')
    L.append('> **Targets are per-map, never per-class.** Top-10 units-at-r100 medians run from ~5–8 on Prisoners '
             'Dilemma to ~60 on Slithery Fight; a class-level target held the bot back on Schooltime (an open map '
             'whose top-10 game is a 41-unit swarm while the open-class median is ~15). The class tables at the end '
             'are descriptive only and are excluded from the JSON the sweeps read.')
    L.append('')

    def table(sel, title):
        """sel: boolean Series over df selecting the table's population."""
        L.append(f'### {title}')
        L.append('')
        L.append('| cohort | n | units r25 | r50 | r100 | r200 | total r50 | r100 | r250 | longest r100 | splits r100 |')
        L.append('|---|---|---|---|---|---|---|---|---|---|---|')
        for c in cohorts:
            g = df[sel & (df['cohort'] == c)]
            if not len(g):
                continue
            L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                COHORT_LABEL[c], len(g),
                *(cell(g[s].tolist()) for s, _ in STATS[:9])))
        L.append('')
        L.append('| cohort | first pearl | pearls r100 | pearls/100dt | moves/pearl | deaths/1k | wall | self | ally-body | enemy-body | h2h | suicide |')
        L.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
        for c in cohorts:
            g = df[sel & (df['cohort'] == c)]
            if not len(g):
                continue
            h2h = (g['death_h2h_enemy_per1k_r100'] + g['death_h2h_ally_per1k_r100']).tolist()
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                COHORT_LABEL[c],
                cell(g['first_pearl'].tolist()), cell(g['pearls_r100'].tolist()),
                cell((g['pearls_per_dt_r100'] * 100).tolist()), cell(g['moves_per_pearl_r100'].tolist()),
                cell(g['deaths_per1k_r100'].tolist()), cell(g['death_wall_per1k_r100'].tolist()),
                cell(g['death_self_per1k_r100'].tolist()), cell(g['death_ally_body_per1k_r100'].tolist()),
                cell(g['death_enemy_body_per1k_r100'].tolist()), cell(h2h),
                cell(g['death_suicide_per1k_r100'].tolist())))
        L.append('')
        L.append('| cohort | units share r100 | total share r100 | territory r50 | r100 | r250 | bed terr r100 | bed share r100 | density r100 | seen r100 | enclosed r100 |')
        L.append('|---|---|---|---|---|---|---|---|---|---|---|')
        for c in cohorts:
            g = df[sel & (df['cohort'] == c)]
            if not len(g):
                continue
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                COHORT_LABEL[c],
                cell(g['units_share_r100'].tolist()), cell(g['total_share_r100'].tolist()),
                cell(g['territory_r50'].tolist()), cell(g['territory_r100'].tolist()), cell(g['territory_r250'].tolist()),
                cell(g['bed_territory_r100'].tolist()), cell(g['bed_share_r100'].tolist()),
                cell(g['density_ratio_r100'].tolist()), cell(g['seen_share_r100'].tolist()),
                cell(g['enclosed_share_r100'].tolist())))
        L.append('')
        L.append('| cohort | access epg2 | conversion | contact mean | splits/100dt r100 | splits 0–50 | 50–100 | 100–250 | 250–500 | newborn deaths ≤10r /100 births | peak units |')
        L.append('|---|---|---|---|---|---|---|---|---|---|---|')
        for c in cohorts:
            g = df[sel & (df['cohort'] == c)]
            if not len(g):
                continue
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                COHORT_LABEL[c],
                cell(g['epg_tau2'].tolist()), cell(g['epg_conversion'].tolist()),
                cell(g['contact_share_mean'].tolist()), cell(g['splits_per100dt_r100'].tolist()),
                cell(g['splits_0_50'].tolist()), cell(g['splits_50_100'].tolist()),
                cell(g['splits_100_250'].tolist()), cell(g['splits_250_500'].tolist()),
                cell(g['newborn_deaths10_per100'].tolist()), cell(g['peak_units'].tolist())))
        L.append('')

    maps_present = [m for (m,) in sorted(by_map)]
    for m in maps_present:
        table(df['map'] == m, m)
    for cls, title in (('compact', 'Map class compact (Portals, Dilemma, Devil, Trophy) — DESCRIPTIVE ONLY, do not target'),
                       ('open', 'Map class open (the other six) — DESCRIPTIVE ONLY, do not target')):
        if (cls,) in by_class:
            table(df['map_class'] == cls, title)
    table(df['map'].notna(), 'All maps pooled')

    L.append('### Winner − loser within top-30 games')
    L.append('')
    L.append(f'Median (winner − loser) over {wl_n} ranked games with both sides in the top 30.')
    L.append('')
    L.append('| | units r50 | units r100 | total r50 | total r100 | pearls r50 | pearls r100 | longest r50 | longest r100 |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    L.append('| all maps | %s |' % ' | '.join(fmt(wl_all[f'{k}_r{r}']) for k in ('units', 'total', 'pearls', 'longest') for r in (50, 100)))
    for cls in ('compact', 'open'):
        L.append('| %s | %s |' % (cls, ' | '.join(fmt(wl_class[cls][f'{k}_r{r}']) for k in ('units', 'total', 'pearls', 'longest') for r in (50, 100))))
    L.append('')
    L.append('### Team 7 − band (medians, pooled over maps)')
    L.append('')
    L.append(f"team 7 n = {t7_band['n_team7']} ranked side-games vs band n = {t7_band['n_band']}; "
             'positive = team 7 higher (for first-pearl, positive = later).')
    L.append('')
    L.append('| units r25 | r50 | r100 | r200 | total r50 | r100 | r250 | longest r100 | splits r100 | first pearl | pearls r100 | pearls/100dt | moves/pearl | deaths/1k |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    L.append('| %s |' % ' | '.join(
        fmt(100 * t7_band['pearls_per_dt_r100'] if k == 'pearls_per_dt_r100' else t7_band[k]) for k in (
            'units_r25', 'units_r50', 'units_r100', 'units_r200', 'total_r50', 'total_r100', 'total_r250',
            'longest_r100', 'splits_r100', 'first_pearl', 'pearls_r100', 'pearls_per_dt_r100', 'moves_per_pearl_r100',
            'deaths_per1k_r100')))
    L.append('')
    L.append('| territory r50 | r100 | r250 | bed terr r100 | density r100 | splits/100dt r100 | splits 0–50 | 50–100 | 100–250 | newborn deaths/100 | peak units |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    L.append('| %s |' % ' | '.join(
        fmt(100 * t7_band[k] if k == 'splits_per100dt_r100' else t7_band[k]) for k in (
            'territory_r50', 'territory_r100', 'territory_r250', 'bed_territory_r100', 'density_ratio_r100',
            'splits_per100dt_r100', 'splits_0_50', 'splits_50_100', 'splits_100_250',
            'newborn_deaths10_per100', 'peak_units')))
    L.append('')
    L.append('### Covariates')
    L.append('')
    L.append('Autoscrim-window medians (in / out), top-30 and band — the pooling covariate:')
    L.append('')
    L.append('| cohort | units r100 in | out | pearls/100dt in | out | moves/pearl in | out |')
    L.append('|---|---|---|---|---|---|---|')
    for c in ('top10', 'r11_30', 'band'):
        r = auto[c]
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (
            COHORT_LABEL[c], fmt(r['units_r100']['in']), fmt(r['units_r100']['out']),
            fmt(100 * r['pearls_per_dt_r100']['in']), fmt(100 * r['pearls_per_dt_r100']['out']),
            fmt(r['moves_per_pearl_r100']['in']), fmt(r['moves_per_pearl_r100']['out'])))
    L.append('')
    L.append('Side A vs side B medians (all cohorts pooled): ' + '; '.join(
        f'{k} A {fmt(v["A"])} vs B {fmt(v["B"])}' for k, v in side_check.items()) + '.')
    L.append('')

    # ---- live bed maps (reconstructed; see tools/analysis/c1e_beds.py) ----
    beds_path = ROOT / a.beds
    if beds_path.exists():
        beds = json.load(open(beds_path))
        L.append('## Live bed maps (walls match the local files; beds do not always)')
        L.append('')
        L.append(f"Reconstructed from bed-origin spawn events over {beds['_games']} ranked games "
                 f"(`tools/analysis/c1e_beds.py` → `{a.beds}`, per-cell empirical rates included). Live replay map "
                 'texts carry no TILE spawn fields, so the F1 bed features (density ratio, bed territory, EPG) are '
                 'NaN on corpus replays; and the local map files under-represent the live beds on four maps.')
        L.append('')
        L.append('| map | layouts (games) | live beds per layout | local file | live-only cells |')
        L.append('|---|---|---|---|---|')
        for m, layouts in sorted(beds['maps'].items()):
            cells = ', '.join(f"{d['bed_count']} (n={d['n_games']})" for d in layouts.values())
            only = ', '.join(str(d.get('live_only', '—')) for d in layouts.values())
            L.append('| %s | %d | %s | %s | %s |' % (
                m, len(layouts), cells,
                ', '.join(str(d.get('local_file_beds', '—')) for d in layouts.values()), only))
        L.append('')

    L.append('## Reading')
    L.append('')
    L.append(READING)
    L.append('')
    L.append('## Caveats')
    L.append('')
    for c in CAVEATS:
        L.append('- ' + c)
    Path(ROOT / a.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(ROOT / a.out_md).write_text('\n'.join(L) + '\n')
    print(f'wrote {a.out_md} and {a.out_json}: {len(df)} side-games, {len(by_map)} maps, wl_n={wl_n}')


READING = '''1. The ladder is visible at every checkpoint and never closes: top 10 hold 7/11/19/30 units at r25/r50/r100/r200
   (band 6/9/15/23) and 78 vs 64 total length at r250. The gap opens continuously — there is no single phase to win.
2. The mechanism is efficiency, not schedules: top-30 eat 8.5 pearls per 100 dragon-turns at 11.7 moves per pearl;
   the band 7.6 at 13.2; team 7 6.8 at 14.8. Pace follows efficiency — P1's conclusion, now field-wide and by map.
3. Schooltime separates the top from everyone: top-10 median 41 units at r100 vs the band's 15 (splits 67 vs 16,
   pearls/100dt 9.6 vs 4.1, moves/pearl 10 vs 24, total r250 193 vs 100). It is the one map the top ten play
   as a swarm-economy game and nobody else does.
4. Trauma and Queen Of Spades are production gaps (16 vs 8 and 11 vs 7 units at r100; splits 29 vs 12 and 24 vs 17);
   Portals and Trophy are efficiency gaps at matched unit counts (Portals 22 vs 21 units, but 11.4 vs 10.9 pearls/100dt
   and 8.8 vs 9.1 moves/pearl compounding to 77 vs 73 total by r250).
5. Slithery Fight is the band's best map — everyone churns (160-167 splits by r100) and the band already eats faster
   than the top 10 (12.7 vs 9.9 pearls/100dt) — but dies into kelp doing it (band 8.9, ranks 11-30 23 wall deaths/1k).
6. Prisoners Dilemma inverts the script: top-10 medians are 8 units and 22 total at r250 vs the band's 5 and 30 —
   shorter and fewer dragons win there; length races are the wrong target on PD.
7. Winner - loser inside the top 30: compact games are half-decided at r50 (winner +5 units, +17 pearls) and settled
   by r100 (+14 units, +56 pearls); open games are not (+1 unit at r50, +4 at r100). Early pressure pays where the
   map is tight.
8. The crown is not the currency: the winner's longest-margin median is 0-1 segments even in decided compact games;
   units and total length decide — consistent with A1's "decided by r250 without crown differences".
9. Survival: h2h is the leading death cause for every cohort (5.5-7.4/1k dt); the top 10's wall and self deaths have
   median 0 while the band leaks (wall up to 23/1k on Slithery, self 1.6/1k pooled). Team 7's signature is different:
   15.9 invalid deaths per 1k dt on Portals (median; timeouts/invalid actions) — a self-inflicted leak no one else has.
10. Team 7 vs band (n=31 ranked side-games, directional): level at r25, -1 unit at r100, then the economy gap
    compounds: -8 splits, -15 pearls by r100, -20 total by r250, +1.6 moves/pearl, while dying less (14 vs 20/1k).
    The opening is only ~1 unit behind; the economy behind the opening is the deficit.
11. Space (added 29 Sep): only Queen Of Spades is a territory map - the top 10 hold 74% of cells at r100 and 92% at
    r250 (seen 95%) while the band holds ~49%; on Schooltime the top 10 hold 65% vs 50%. On Trauma, Portals and
    Slithery territory is exactly 50/50 for every cohort - those maps are won on production and efficiency, not space.
12. Churn (added 29 Sep): a third of all newborns die within 10 rounds in every cohort (~34/100 births pooled; the
    top 10 do not churn less, they replace faster). On Slithery and Portals half of all newborns die young
    (48-49/100). The 64-dragon cap is hit by everyone on Slithery and by the top 10 on Schooltime (peak 64, q1=q3).
    Schooltime production happens almost entirely in rounds 50-100 (top-10 splits 54 vs the band's 11 in that window).
13. Live beds (added 29 Sep): the local map files under-represent the live bed maps - Schooltime has 444 live bed
    cells vs 326 local (+36%), Slithery 497 vs 339 (+47%), QoS 472 vs 442, Devil 176 vs 174; Autarky, Default,
    Portals, Trauma, Trophy match exactly, and Prisoners Dilemma has FOUR layouts in the pool (88/88/76/76 beds).
    Fixtures on Schooltime/Slithery train on a poorer economy than the field plays; the reconstructed maps with
    per-cell rates are in game_stats/live_beds.json.'''

CAVEATS = [
    'No submission ids since 28 Sep (D-023): cohort profiles pool team versions; a team mid-experiment still counts as that team.',
    'The corpus covers one day (28 Sep) and is still being fetched while this table regenerates; the header states the index line count and newest fetched_at used. Cohorts use the ladder snapshot nearest each game\'s start.',
    'Ranked games only (unranked batches contain other teams\' candidates); ~60% of ranked games sit in autoscrim windows — the covariate table shows in/out medians nearly identical, so they are pooled.',
    'Team 7 has few ranked games (n=31 pooled, 2-5 per map); its row is directional, not a distribution, and its per-map cells should not be read as medians.',
    'Top-10 per-map counts are 25-48 side-games: quartiles are coarse; medians are the deliverable.',
    'Autoscrim self-games (mirror matches, team_a = team_b) are included where present (count in _meta.mirror_games).',
    'Side asymmetry exists (pooled side B runs ~2 units / ~4 total ahead at r100) but is second-order next to cohort; sides are pooled everywhere.',
    'Semantics: units/total/longest at rX are start-of-round snapshots (r100 = start of round 100); all by-r100 counters cover rounds 0-99.',
    'Bed-dependent F1 stats (density ratio, bed territory, bed_expected_share, EPG, conversion) are NaN on live replays: live map texts carry no TILE spawn fields. The live bed maps reconstructed from spawn events are in game_stats/live_beds.json; local fixtures under-represent live beds on Schooltime (+118 cells), Slithery (+158), QoS (+30), Devil (+2), and Prisoners Dilemma has four layouts.',
    'Targets are per-map (director, 29 Sep): the class tables are descriptive only and are excluded from the sweep JSON (_class_descriptive).',
]

if __name__ == '__main__':
    main()
