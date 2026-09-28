"""Live-versus-local transfer (Q4): absolute calibration per source, paired common cells per experiment, trajectory
matching of live opponents to local opponents, and the toolkit strata of the ledger.

    python -m tools.analysis.transfer --state LIVE/state/state.json --ledger game_stats.parquet \
        --series build/a1_local_series.csv [--source-map build/a1_source_map.json]

`--source-map` is the fingerprint join produced on the Mac (registry candidate → bots/ directory); the default is the
mapping recorded on 2026-09-28. Needs pandas + pyarrow. Prints Markdown.
"""
import argparse
import json

import numpy as np
import pandas as pd

from .live_record import games_table, load_state

LIVE_MAPS = {'schooltime': 'Schooltime', 'portals': 'Portals', 'slithery_fight': 'Slithery Fight', 'queen_of_spades': 'Queen Of Spades', 'default': 'Default',
             'trophy': 'Trophy', 'dilemma': 'Prisoners Dilemma', 'autarky': 'Autarky', 'devil': 'Devil', 'trauma': 'Trauma'}
DEFAULT_SOURCES = {9508: 'fenrir-v18-arrival-ready-beds', 8540: 'bifrost-v01-portal-memory', 9639: 'ein-dog-v02-momentum', 9663: 'yuna-v02-core',
                   9980: 'tidus-t02-spread-only', 10013: 'yuna-v03-core'}
SERIES_ALIAS = {'ein-dog-x08-momentum-scoped': 'ein-dog-v02-momentum', 'yuna-x10-core-nocong': 'yuna-v03-core'}   # identical fingerprints
EXPERIMENTS = [(8540, 9508), (9639, 9508), (9663, 9508), (9980, 9663)]
FEATS = ['u100', 'ou100', 't250', 'ot250', 'l400', 'ol400']


def ledger_long(ledger, bots):
    L = ledger[ledger['map'].isin(LIVE_MAPS) & (ledger['mode'] == 'native')].copy()
    L['map_name'] = L['map'].map(LIVE_MAPS)
    out = []
    for me, other in (('a', 'b'), ('b', 'a')):
        t = L[L[f'bot_{me}'].isin(bots)].copy()
        t['bot'], t['opp'], t['side'] = t[f'bot_{me}'], t[f'bot_{other}'], me.upper()
        t['s'] = t[f'{me}_wins'].fillna(0) + 0.5 * t['draws'].fillna(0)
        out.append(t[['bot', 'opp', 'side', 'map_name', 'runner_version', 's']])
    return pd.concat(out)


def absolute(G, live, sources):
    rows = []
    for sub, bot in sources.items():
        g, lv = G[G.bot == bot], live[live.submission == sub]
        if not len(g) or not len(lv):
            continue
        rows.append(dict(source=sub, bot=bot, local_n=len(g), local_opponents=g.opp.nunique(), local_share=round(g.s.mean(), 3), live_n=len(lv), live_share=round(lv.score.mean(), 3),
                         live_minus_local_pp=round(100 * (lv.score.mean() - g.s.mean()), 0),
                         worst_map=max(((m, int(round(100 * (lv[lv.map_name == m].score.mean() - g[g.map_name == m].s.mean())))) for m in set(g.map_name) & set(lv.map_name)), key=lambda kv: abs(kv[1]), default=None)))
    return pd.DataFrame(rows)


def paired(G, sources):
    rows = []
    for cand, ctrl in EXPERIMENTS:
        gc, gk = G[G.bot == sources[cand]], G[G.bot == sources[ctrl]]
        cc, ck = gc.groupby(['map_name', 'opp']).s.mean(), gk.groupby(['map_name', 'opp']).s.mean()
        common = cc.index.intersection(ck.index)
        rows.append(dict(candidate=cand, control=ctrl, common_cells=len(common), local_delta=(round(float((cc[common] - ck[common]).mean()), 3) if len(common) else None)))
    return pd.DataFrame(rows)


def trajectories(series_csv, live, sources):
    S = pd.read_csv(series_csv)
    S['map_name'] = S['map'].map(LIVE_MAPS)
    S['candidate'] = S['candidate'].replace(SERIES_ALIAS)
    S['is_cand'] = S['team'] == S['side']
    key = ['run', 'candidate', 'opponent', 'map_name', 'side', 'outcome']

    def pv(df, who):
        d = df[df.is_cand == who].pivot_table(index=key, columns='r', values=['units', 'total', 'longest'], aggfunc='first')
        d.columns = [f'{a}_{b}' for a, b in d.columns]
        return d
    J = pv(S, True).join(pv(S, False), lsuffix='_c', rsuffix='_o').reset_index()
    J['win'] = (J.outcome == J.side).astype(float)
    loc = J[J.side == 'A'].groupby(['candidate', 'opponent']).agg(n=('win', 'size'), share=('win', 'mean'), u100=('units_100_c', 'median'), ou100=('units_100_o', 'median'),
                                                                  t250=('total_250_c', 'median'), ot250=('total_250_o', 'median'), l400=('longest_400_c', 'median'), ol400=('longest_400_o', 'median'))
    lp = live.groupby(['submission', 'opponent', 'opponent_submission']).agg(n=('score', 'size'), share=('score', 'mean'), u100=('s100_units', 'median'), ou100=('o100_units', 'median'),
                                                                             t250=('s250_total', 'median'), ot250=('o250_total', 'median'), l400=('s400_longest', 'median'), ol400=('o400_longest', 'median'))
    lines = []
    for sub, bot in sources.items():
        if bot not in loc.index.get_level_values(0) or sub not in lp.index.get_level_values(0):
            continue
        lc = loc.loc[bot]
        lc = lc[lc.n >= 4]
        if not len(lc):
            continue
        sd = pd.concat([lc[FEATS], lp.loc[sub][FEATS]]).std() + 1e-9
        lines.append(f'### source {sub} ({bot}): {len(lc)} local opponents with ≥ 4 A-side games')
        for (opp, osub), r in lp.loc[sub].iterrows():
            d = (((lc[FEATS] - r[FEATS]) / sd) ** 2).sum(axis=1).pow(0.5).sort_values()
            lines.append(f"- live {opp}/{int(osub)} (share {r.share:.2f}; u100 {r.u100} v {r.ou100}, t250 {r.t250} v {r.ot250}, l400 {r.l400} v {r.ol400}) → "
                         + '; '.join(f'{o} d={v:.2f} (share {lc.loc[o].share:.2f}, n={int(lc.loc[o].n)})' for o, v in d.head(3).items()))
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--state', required=True)
    ap.add_argument('--ledger', required=True)
    ap.add_argument('--series')
    ap.add_argument('--source-map')
    args = ap.parse_args()
    sources = dict(DEFAULT_SOURCES)
    if args.source_map:
        for name, v in json.load(open(args.source_map)).items():
            if v.get('submission') and v.get('bots'):
                sources[v['submission']] = v['bots'][0]
    ledger = pd.read_parquet(args.ledger)
    G = ledger_long(ledger, set(sources.values()))
    df = games_table(load_state(args.state))
    live = df[(df.verified == True) & (df.origin == 'controlled') & (df.side == 'A')]  # noqa: E712
    print('## Absolute calibration (native ledger, live maps, all local opponents vs live controlled A-side)\n')
    print(absolute(G, live, sources).to_markdown(index=False))
    print('\n## Paired common (map, opponent) cells in the ledger per experiment\n')
    print(paired(G, sources).to_markdown(index=False))
    print('\n## Toolkit strata on live maps (ledger rows per runner version)\n')
    print(ledger[ledger['map'].isin(LIVE_MAPS)].groupby(['map', 'runner_version']).size().unstack(fill_value=0).to_markdown())
    if args.series:
        print('\n## Trajectory matching (nearest local opponent by standardised distance on r100/r250/r400 profiles)\n')
        print(trajectories(args.series, live, sources))


if __name__ == '__main__':
    main()
