#!/usr/bin/env python3
"""C1-C efficiency ledger: rank the early-game leaks by length lost, us vs band vs top.

Aggregates the F1 feature parquets (never re-decodes) over three populations:
  - corpus ranked games (build/c1e/features-*): cohorts top10 / r11_30 / band / team7ranked,
    exactly the C1-E cohort convention (ladder snapshot nearest game start);
  - our live games (build/c1c/features-team7): every team-7 corpus game of the day, our side
    only, ranked and dev games both, broken out by live submission id;
  - local fixtures (build/c1c/features-yuna): yuna-v03-core vs fenrir-v18 / kazuha-s01,
    seeds 1-3, both sides - the exact-pair baseline the chassis fixes will be measured on.

Leak classes are defined on the F1 per-death rows (overlap allowed, definitions in the
generated doc): newborn (age<=10 child), trapped (enclosed at death, not suicide),
portal (died within 2 cells of a portal), crowd23 (length<=3 dying into own-side bodies),
plus the cause classes wall/self/ally_body/h2h_enemy/invalid for context. The ranking
currency is length lost per 1k dragon-turns in rounds 0-99 (also 0-249 in the JSON).

  python tools/analysis/c1c_ledger.py --batches 'build/c1e/features-*' \
      --index build/c1e/ranked_games.jsonl --corpus-index public_replays/corpus/index.jsonl \
      --ladder public_replays/corpus/ladder --team7 build/c1c/features-team7 \
      --local build/c1c/features-yuna \
      --out-md docs/analysis/C1-efficiency-ledger.md --out-json game_stats/efficiency_ledger.json
"""
import argparse, glob, json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
from tools.analysis.c1e_pace import load_ladders, rank_at, cohort_of, q, cell, fmt, med  # noqa: E402

WINDOWS = (100, 250)
CAUSES = ('wall', 'self', 'ally_body', 'enemy_body', 'h2h_enemy', 'h2h_ally', 'suicide', 'invalid')
LEAKS = ('newborn', 'trapped', 'portal', 'crowd23')
CLASSES = tuple('lk_' + l for l in LEAKS) + tuple('cause_' + c for c in CAUSES)
SERIES_COLS = ['game', 'side', 'round', 'total', 'eats', 'moves', 'dragon_turns', 'splits',
               'length_lost', 'sprint_cost']
COHORT_LABEL = {'top10': 'top 10', 'r11_30': 'ranks 11-30', 'band': 'band 55-85',
                'team7ranked': 'team 7 ranked', 'team7live': 'team 7 live (all)',
                'yunalocal': 'yuna-v03-core local', 'opplocal': 'local opponents'}
COHORTS = list(COHORT_LABEL)


def leak_flags(d):
    """1/0 count and length-weighted columns per leak/cause class on death rows; classes overlap."""
    d = d.copy()
    for c in ('newborn', 'enclosed', 'near_portal'):
        d[c] = d[c].fillna(False).astype(bool)
    d['lk_newborn'] = d['newborn'].astype(int)
    d['lk_trapped'] = (d['enclosed'] & (d['cls'] != 'suicide')).astype(int)
    d['lk_portal'] = d['near_portal'].astype(int)
    d['lk_crowd23'] = ((d['length'] <= 3) & d['cls'].isin(['self', 'ally_body', 'h2h_ally'])).astype(int)
    for c in CAUSES:
        d['cause_' + c] = (d['cls'] == c).astype(int)
    for k in CLASSES:
        d['lenw_' + k] = d['length'] * d[k]
    return d


def load_batch(d, src):
    d = Path(d)
    feat = pd.read_parquet(d / 'features.parquet', columns=['game', 'side', 'map', 'bot', 'first_pearl',
                                                            'child_len_median', 'enclosed_share_mean'])
    ser = pd.read_parquet(d / 'series.parquet', columns=SERIES_COLS)
    dea = leak_flags(pd.read_parquet(d / 'deaths.parquet'))
    dra = pd.read_parquet(d / 'dragons.parquet', columns=['game', 'side', 'born', 'died', 'initial', 'eats',
                                                          'eats_per_100'])
    for df in (feat, ser, dea, dra):
        df['src'] = src
    return feat, ser, dea, dra


def gid_of(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return -1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--batches', default='build/c1e/features-*')
    ap.add_argument('--index', default='build/c1e/ranked_games.jsonl')
    ap.add_argument('--corpus-index', default='public_replays/corpus/index.jsonl')
    ap.add_argument('--ladder', default='public_replays/corpus/ladder')
    ap.add_argument('--team7', default='build/c1c/features-team7')
    ap.add_argument('--local', default='build/c1c/features-yuna')
    ap.add_argument('--out-md', default='docs/analysis/C1-efficiency-ledger.md')
    ap.add_argument('--out-json', default='game_stats/efficiency_ledger.json')
    a = ap.parse_args(argv)

    feats, sers, deaths, dras = [], [], [], []
    for d in sorted(glob.glob(str(ROOT / a.batches))):
        if not (Path(d) / 'features.parquet').exists():
            continue
        f, s, de, dr = load_batch(d, 'corpus')
        feats.append(f); sers.append(s); deaths.append(de); dras.append(dr)
    for path, src in ((ROOT / a.team7, 'team7'), (ROOT / a.local, 'local')):
        if (path / 'features.parquet').exists():
            f, s, de, dr = load_batch(path, src)
            feats.append(f); sers.append(s); deaths.append(de); dras.append(dr)
    feat = pd.concat(feats, ignore_index=True).drop_duplicates(['src', 'game', 'side'])
    series = pd.concat(sers, ignore_index=True).drop_duplicates(['src', 'game', 'side', 'round'])
    deaths = pd.concat(deaths, ignore_index=True)
    dragons = pd.concat(dras, ignore_index=True)
    feat['gid'] = feat['game'].map(gid_of)

    # ---- cohort / context joins ----
    games = {r['game_id']: r for r in (json.loads(l) for l in open(ROOT / a.index))}
    corpus_idx = {r['game_id']: r for r in (json.loads(l) for l in open(ROOT / a.corpus_index))}
    ladders = load_ladders(ROOT / a.ladder)
    ctx = {}
    for gid, r in games.items():
        when = datetime.fromisoformat(r['started_at'].replace('Z', '+00:00'))
        ra, rb = rank_at(ladders, r['team_a'], when), rank_at(ladders, r['team_b'], when)
        ctx[gid] = dict(cohort_a=cohort_of(ra, r['team_a']), cohort_b=cohort_of(rb, r['team_b']))
    feat['cohort'] = pd.Series(None, index=feat.index, dtype=object)
    feat['team7_keep'] = False
    feat['ranked_live'] = False
    cm = feat['src'] == 'corpus'
    for s, k in (('A', 'cohort_a'), ('B', 'cohort_b')):
        m = cm & feat['side'].eq(s)
        feat.loc[m, 'cohort'] = feat.loc[m, 'gid'].map(lambda g: ctx.get(g, {}).get(k)).values
    # C1-E calls the ranked team-7 cohort 'team7'; keep its name distinct from the live population
    feat.loc[feat['cohort'] == 'team7', 'cohort'] = 'team7ranked'
    # team 7 ranked games keep the C1-E cohort name; the live population is the team7 batch, our side
    t7row = corpus_idx.get
    tm = feat['src'] == 'team7'
    feat.loc[tm, 'team7_keep'] = [
        t7row(g, {}).get('team_a') == 7 if s == 'A' else t7row(g, {}).get('team_b') == 7
        for g, s in zip(feat.loc[tm, 'gid'], feat.loc[tm, 'side'])]
    feat.loc[tm & feat['team7_keep'], 'cohort'] = 'team7live'
    feat.loc[tm, 'ranked_live'] = [bool(t7row(g, {}).get('ranked')) for g in feat.loc[tm, 'gid']]
    loc = feat['src'] == 'local'
    feat.loc[loc & feat.loc[loc, 'bot'].eq('yuna-v03-core'), 'cohort'] = 'yunalocal'
    feat.loc[loc & ~feat.loc[loc, 'bot'].eq('yuna-v03-core'), 'cohort'] = 'opplocal'

    # ---- per-window series sums and totals ----
    parts = [feat]
    t0 = series[series['round'] == 0][['src', 'game', 'side', 'total']].rename(columns={'total': 'total@0'})
    parts.append(t0)
    for W in WINDOWS:
        cols = ['eats', 'moves', 'dragon_turns', 'splits', 'length_lost', 'sprint_cost']
        sw = series[series['round'] < W].groupby(['src', 'game', 'side'], as_index=False)[cols].sum()
        sw = sw.rename(columns={c: c + f'_{W}' for c in cols})
        parts.append(sw)
        sr = series[series['round'] <= W]
        tw = sr.loc[sr.groupby(['src', 'game', 'side'])['round'].idxmax(), ['src', 'game', 'side', 'total']] \
              .rename(columns={'total': f'total@{W}'})
        parts.append(tw)
        aggcols = CLASSES + tuple('lenw_lk_' + l for l in LEAKS)
        agg = {f'{k}_{W}': (k, 'sum') for k in aggcols}
        agg[f'n_{W}'] = ('length', 'size')
        agg[f'len_{W}'] = ('length', 'sum')
        dw = deaths[deaths['round'] < W].groupby(['src', 'game', 'side'], as_index=False).agg(**agg)
        parts.append(dw)
    ch = dragons[~dragons['initial'].astype(bool)]
    for W in WINDOWS:
        cw = ch[ch['born'] < W].groupby(['src', 'game', 'side']).agg(
            **{f'births_{W}': ('eats', 'size'),
               f'never_ate_{W}': ('eats', lambda x: int((x == 0).sum())),
               f'child_eats_med_{W}': ('eats_per_100', 'median')}).reset_index()
        parts.append(cw)

    df = parts[0]
    for p in parts[1:]:
        df = df.merge(p, on=['src', 'game', 'side'], how='left')
    fill0 = [c for c in df.columns if c.startswith(('eats_', 'moves_', 'dragon_turns_', 'splits_',
                                                    'length_lost_', 'sprint_cost_', 'lk_', 'cause_',
                                                    'lenw_', 'n_10', 'n_25', 'len_10', 'len_25',
                                                    'births', 'never_ate'))]
    df[fill0] = df[fill0].fillna(0)

    # ---- derived ----
    STATS = ['first_pearl', 'child_len_median']
    for W in WINDOWS:
        dt = df[f'dragon_turns_{W}'].where(df[f'dragon_turns_{W}'] > 0)
        eat = df[f'eats_{W}'].where(df[f'eats_{W}'] > 0)
        k = 1000 / dt
        df[f'pearls_per100dt_{W}'] = 100 * df[f'eats_{W}'] / dt
        df[f'moves_per_pearl_{W}'] = df[f'moves_{W}'] / eat
        df[f'death_len_per_pearl_{W}'] = df[f'length_lost_{W}'] / eat
        df[f'sprint_cost_per_pearl_{W}'] = df[f'sprint_cost_{W}'] / eat
        df[f'len_per_pearl_{W}'] = (df[f'total@{W}'] - df['total@0'] + df[f'length_lost_{W}']) / eat
        df[f'lenlost_per1k_{W}'] = df[f'len_{W}'] * k
        df[f'deaths_per1k_{W}'] = df[f'n_{W}'] * k
        for lk in LEAKS:
            df[f'{lk}_n_per1k_{W}'] = df[f'lk_{lk}_{W}'] * k
            df[f'{lk}_len_per1k_{W}'] = df[f'lenw_lk_{lk}_{W}'] * k
            df[f'{lk}_len_share_{W}'] = df[f'lenw_lk_{lk}_{W}'] / df[f'len_{W}'].where(df[f'len_{W}'] > 0)
        for c in CAUSES:
            df[f'cause_{c}_per1k_{W}'] = df[f'cause_{c}_{W}'] * k
        df[f'never_ate_share_{W}'] = df[f'never_ate_{W}'] / df[f'births_{W}'].where(df[f'births_{W}'] > 0)
        df[f'newborn10_per100_{W}'] = 100 * df[f'lk_newborn_{W}'] / df[f'births_{W}'].where(df[f'births_{W}'] > 0)
        STATS += [f'pearls_per100dt_{W}', f'moves_per_pearl_{W}', f'len_per_pearl_{W}',
                  f'death_len_per_pearl_{W}', f'sprint_cost_per_pearl_{W}', f'lenlost_per1k_{W}',
                  f'deaths_per1k_{W}'] + \
                 [f'{lk}_len_per1k_{W}' for lk in LEAKS] + [f'{lk}_n_per1k_{W}' for lk in LEAKS] + \
                 [f'cause_{c}_per1k_{W}' for c in CAUSES] + \
                 [f'never_ate_share_{W}', f'newborn10_per100_{W}', f'child_eats_med_{W}']
    # length identity: len/pearl + sprint/pearl should be 1 (splits conserve, eats add 1)
    res = (df['len_per_pearl_100'] + df['sprint_cost_per_pearl_100'] - 1).abs().max()

    # ---- aggregate tables ----
    maps_present = sorted(df['map'].dropna().unique())
    by_map = {}
    for m in maps_present + ['ALL']:
        key = m
        sel = df['map'].notna() if m == 'ALL' else df['map'] == m
        for c in COHORTS:
            g = df[sel & (df['cohort'] == c)]
            if not len(g):
                continue
            d = by_map.setdefault(key, {}).setdefault(c, {'n': int(len(g))})
            for stat in STATS:
                d[stat] = med(g[stat].tolist())

    # ---- falsifier: team7live vs band IQR ----
    fals = {'pooled': [], 'by_map': {}}
    band_pool, t7_pool = df[df['cohort'] == 'band'], df[df['cohort'] == 'team7live']
    for stat in STATS:
        b, t = band_pool[stat].dropna().tolist(), t7_pool[stat].dropna().tolist()
        if not b or not t:
            continue
        q1, q3 = q(b, .25), q(b, .75)
        tm = med(t)
        if tm < q1 or tm > q3:
            fals['pooled'].append(dict(stat=stat, team7=tm, band_q1=q1, band_med=med(b), band_q3=q3,
                                       side='below' if tm < q1 else 'above'))
    for m in maps_present:
        for stat in STATS:
            b = band_pool[band_pool['map'] == m][stat].dropna().tolist()
            t = t7_pool[t7_pool['map'] == m][stat].dropna().tolist()
            if not b or not t:
                continue
            q1, q3 = q(b, .25), q(b, .75)
            tm = med(t)
            if tm < q1 or tm > q3:
                fals['by_map'].setdefault(m, []).append(
                    dict(stat=stat, team7=tm, band_q1=q1, band_med=med(b), band_q3=q3))

    # ---- ranking: us-vs-band gap in leak length lost (r100) ----
    ranking = []
    for m in maps_present + ['ALL']:
        bm = band_pool if m == 'ALL' else band_pool[band_pool['map'] == m]
        tm2 = t7_pool if m == 'ALL' else t7_pool[t7_pool['map'] == m]
        for stat, lk in [(f'{l}_len_per1k_100', l) for l in LEAKS] + [('death_len_per_pearl_100', 'all_death_len')]:
            b, t = bm[stat].dropna().tolist(), tm2[stat].dropna().tolist()
            if not b or not t:
                continue
            ranking.append(dict(map=m, leak=lk, team7=med(t), band=med(b), gap=med(t) - med(b)))
    ranking.sort(key=lambda r: -r['gap'])

    # ---- local exact pairs ----
    pairs = []
    yl, ol = df[df['cohort'] == 'yunalocal'], df[df['cohort'] == 'opplocal']
    for m in maps_present:
        for lk in LEAKS:
            stat = f'{lk}_len_per1k_100'
            y, o = yl[yl['map'] == m][stat].dropna().tolist(), ol[ol['map'] == m][stat].dropna().tolist()
            if not y or not o:
                continue
            pairs.append(dict(map=m, leak=lk, yuna=med(y), opp=med(o), gap=med(y) - med(o)))
    pairs.sort(key=lambda r: -r['gap'])

    # ---- per-submission breakout (our live games; submission id from the corpus index - the
    # replay header text is empty for our side in team-7 replays) ----
    bysub = {}
    tl = df[(df['src'] == 'team7') & df['team7_keep']]
    tl_sub = [t7row(g, {}).get('bot_a') if s == 'A' else t7row(g, {}).get('bot_b')
              for g, s in zip(tl['gid'], tl['side'])]
    tl = tl.assign(sub=tl_sub)
    for b, g in tl.groupby(tl['sub'].fillna('?')):
        bysub[b] = {'n': int(len(g))}
        for stat in [f'{lk}_len_per1k_100' for lk in LEAKS] + ['pearls_per100dt_100', 'moves_per_pearl_100',
                                                              'lenlost_per1k_100', 'never_ate_share_100',
                                                              'deaths_per1k_100', 'sprint_cost_per_pearl_100',
                                                              'cause_wall_per1k_100', 'cause_invalid_per1k_100']:
            bysub[b][stat] = med(g[stat].tolist())

    out = {'_meta': {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'definitions': 'leak classes on F1 death rows; rates per 1k dragon-turns in rounds 0..W-1; '
                       'newborn=age<=10 child; trapped=enclosed(reach5<=15) at death, not suicide; '
                       'portal=died within 2 cells of a portal; crowd23=len<=3 into self/ally body',
        'identity_residual_max': float(res),
        'populations': {c: int((df['cohort'] == c).sum()) for c in COHORTS if (df['cohort'] == c).any()},
    },
        'by_map': by_map, 'ranking_team7_minus_band_r100': ranking, 'falsifier': fals,
        'local_pairs_yuna_minus_opp': pairs, 'team7_by_submission': bysub}

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, float) and o != o:
            return None
        if isinstance(o, (np.floating, np.integer)):
            return float(o)
        return o

    Path(ROOT / a.out_json).parent.mkdir(parents=True, exist_ok=True)
    json.dump(clean(out), open(ROOT / a.out_json, 'w'), indent=1, sort_keys=True)

    # ---- markdown ----
    L = ['# C1-C efficiency ledger: leaks ranked by length lost (us vs band vs top)', '',
         f"Generated {out['_meta']['generated_at'][:19]}Z from the F1 feature parquets (`tools/analysis/c1c_ledger.py`). "
         'Populations: corpus ranked (C1-E batches, cohorts as in C1-E); team-7 live corpus games of 28 Sep '
         '(our side only; ranked and dev games); local fixtures yuna-v03-core vs fenrir-v18/kazuha-s01 '
         '(seeds 1-3, both sides). Cells are median (q1-q3), NaNs dropped. '
         f"Length identity |len/pearl + sprint/pearl - 1| max = {res:.4f}.", '',
         '> Leak classes overlap by design: **newborn** = child died within 10 rounds of birth; **trapped** = '
         'enclosed at death (<=15 cells reachable in 5 steps, bodies blocking), suicide excluded; **portal** = death '
         'head within 2 cells of a portal; **crowd23** = length<=3 dying into own-side bodies (self/ally/h2h-ally). '
         'The causes (wall/self/ally-body/h2h-enemy/invalid) are the disjoint F1 classes. Currency: length lost '
         'per 1k dragon-turns, rounds 0-99. never-ate ch = share of children that never eat a pearl in their life.', '']

    def leak_table(sel, title):
        L.append(f'### {title}')
        L.append('')
        L.append('| cohort | n | pearls/100dt | moves/pearl | len/pearl | death-len/pearl | lenlost/1k | newborn len/1k | trapped len/1k | portal len/1k | crowd23 len/1k | wall | self | ally-body | h2h-enemy | invalid | never-ate ch | newborn/100 |')
        L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
        for c in COHORTS:
            g = df[sel & (df['cohort'] == c)]
            if not len(g):
                continue
            L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                COHORT_LABEL[c], len(g),
                cell(g['pearls_per100dt_100'].tolist()), cell(g['moves_per_pearl_100'].tolist()),
                cell(g['len_per_pearl_100'].tolist()), cell(g['death_len_per_pearl_100'].tolist()),
                cell(g['lenlost_per1k_100'].tolist()),
                cell(g['newborn_len_per1k_100'].tolist()), cell(g['trapped_len_per1k_100'].tolist()),
                cell(g['portal_len_per1k_100'].tolist()), cell(g['crowd23_len_per1k_100'].tolist()),
                cell(g['cause_wall_per1k_100'].tolist()), cell(g['cause_self_per1k_100'].tolist()),
                cell(g['cause_ally_body_per1k_100'].tolist()), cell(g['cause_h2h_enemy_per1k_100'].tolist()),
                cell(g['cause_invalid_per1k_100'].tolist()), cell(g['never_ate_share_100'].tolist()),
                cell(g['newborn10_per100_100'].tolist())))
        L.append('')

    for m in maps_present:
        leak_table(df['map'] == m, m)
    leak_table(df['cohort'].notna(), 'All maps pooled')

    L.append('### Ranking: team 7 live − band, length lost per 1k dt (r100)')
    L.append('')
    L.append('| map | leak | team7 | band | gap |')
    L.append('|---|---|---|---|---|')
    for r in ranking[:30]:
        L.append('| %s | %s | %s | %s | %s |' % (r['map'], r['leak'], fmt(r['team7']), fmt(r['band']), fmt(r['gap'])))
    L.append('')
    L.append('### Local exact pairs: yuna-v03-core − opponent (fenrir-v18/kazuha-s01), r100')
    L.append('')
    L.append('| map | leak | yuna | opp | gap |')
    L.append('|---|---|---|---|---|')
    for r in pairs[:20]:
        L.append('| %s | %s | %s | %s | %s |' % (r['map'], r['leak'], fmt(r['yuna']), fmt(r['opp']), fmt(r['gap'])))
    L.append('')
    L.append('### Team 7 live by submission (our side, 28 Sep games)')
    L.append('')
    L.append('| submission | n | pearls/100dt | moves/pearl | lenlost/1k | newborn len/1k | trapped len/1k | portal len/1k | crowd23 len/1k | never-ate | sprint/pearl | wall | invalid |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for b, r in sorted(bysub.items(), key=lambda kv: -kv[1]['n']):
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            b, r['n'], fmt(r['pearls_per100dt_100']), fmt(r['moves_per_pearl_100']), fmt(r['lenlost_per1k_100']),
            fmt(r['newborn_len_per1k_100']), fmt(r['trapped_len_per1k_100']), fmt(r['portal_len_per1k_100']),
            fmt(r['crowd23_len_per1k_100']), fmt(r['never_ate_share_100']), fmt(r['sprint_cost_per_pearl_100']),
            fmt(r['cause_wall_per1k_100']), fmt(r['cause_invalid_per1k_100'])))
    L.append('')
    L.append("### Falsifier check: team-7-live statistics outside the band's interquartile range")
    L.append('')
    L.append(f'{len(fals["pooled"])} of {len(STATS)} statistics (pooled over maps) sit outside band q1-q3:')
    L.append('')
    L.append('| stat | team7 | band q1 | band med | band q3 | side |')
    L.append('|---|---|---|---|---|---|')
    for r in fals['pooled']:
        L.append('| %s | %s | %s | %s | %s | %s |' % (r['stat'], fmt(r['team7']), fmt(r['band_q1']),
                                                      fmt(r['band_med']), fmt(r['band_q3']), r['side']))
    L.append('')
    Path(ROOT / a.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(ROOT / a.out_md).write_text('\n'.join(L) + '\n')
    print(f'wrote {a.out_md} and {a.out_json}: populations {out["_meta"]["populations"]}, '
          f'falsifier outside-IQR {len(fals["pooled"])}/{len(STATS)}')


if __name__ == '__main__':
    main()
