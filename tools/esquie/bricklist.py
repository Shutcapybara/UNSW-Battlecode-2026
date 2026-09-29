"""Per-map brick list (M-1 Part 1): the BENCHMARKS three-number form (absolute,
gap to the top ten, field percentile) for every tier-1/tier-2 metric, per map —
the pooled scorecard's per-map companion.

    python -m tools.esquie.bricklist --bot esquie-01-nodevil --panels z1,gen

Reads the features parquet the scorecard left under build/zoo/<panel>-<bot>-<fp8>/.
Pool maps get the full three-number form from the fixed field references; gen
maps are raw medians (no reference exists there). Output: TSV to stdout and
game_stats/runs/<bot>-bricklist-<panels>.tsv.

--parent <bot> adds paired per-map deltas (same map, seed, opponent, seat) for
every metric, pooling the parent's panel roots the same way (Part 3 local tests).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
import pandas as pd

from tools.analysis.features.benchmarks import apply_field_rel, derive
from tools.analysis.features.scorecard import CHECKPOINTS, load_refs, panel_root

TIER1 = ['units@100', 'total@100', 'births@100']
TIER2 = ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k',
         'death_h2h_ally_per1k', 'death_invalid_per1k']
POOL = ['devil', 'dilemma', 'portals', 'schooltime', 'slithery_fight', 'queen_of_spades',
        'default', 'trophy', 'autarky', 'trauma']


def rows_for(root: pathlib.Path, bot: str, seeds) -> pd.DataFrame:
    F = pd.read_parquet(root / 'features' / 'features.parquet')
    want = tuple(f's{s}__' for s in seeds)
    rows = F[(F['bot'] == bot) & F['game'].str.startswith(want)].copy()
    if not len(rows):
        raise SystemExit(f'no side-rows for bot {bot} under {root} (seeds {seeds})')
    return rows


def per_map(rows: pd.DataFrame, med, refs) -> pd.DataFrame:
    H = apply_field_rel(derive(rows, med), refs)
    out = []
    for m, g in H.groupby('map'):
        r = {'map': m, 'n': len(g), 'win': float(g['won'].mean())}
        for c in list(CHECKPOINTS) + TIER1:
            r[c] = float(g[c].median())
            r[f'{c}|map'] = float(g[f'{c}|map'].median()) if f'{c}|map' in g else np.nan
            r[f'{c}|top'] = float(g[f'{c}|top'].median()) if f'{c}|top' in g else np.nan
            r[f'{c}|pct'] = float(g[f'{c}|pct'].median()) if f'{c}|pct' in g else np.nan
        for c in TIER2:
            r[c] = float(g[c].median())
            r[f'{c}|xs'] = float(g[f'{c}|xs'].median()) if f'{c}|xs' in g else np.nan
            r[f'{c}|pct'] = float(g[f'{c}|pct'].median()) if f'{c}|pct' in g else np.nan
        cps = [r[f'{c}|pct'] for c in CHECKPOINTS]
        r['econ_pct'] = float(np.nanmean(cps)) if not all(np.isnan(c) for c in cps) else np.nan
        r['economy_map'] = float(np.nanmean([r[f'{c}|map'] for c in CHECKPOINTS]))
        out.append(r)
    return pd.DataFrame(out).set_index('map')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--bot', required=True)
    ap.add_argument('--panels', default='z1,gen')
    ap.add_argument('--seed', default='1,2')
    ap.add_argument('--parent', default=None, help='paired per-map deltas vs this bot')
    a = ap.parse_args(argv)
    seeds = tuple(int(s) for s in a.seed.split(','))
    med, refs = load_refs()

    tables = {}
    for panel in a.panels.split(','):
        rows = rows_for(panel_root(panel, f'bots/{a.bot}'), a.bot, seeds)
        tables[panel] = per_map(rows, med, refs)

    t = tables.get('z1')
    if t is not None:
        cols = (['n', 'win', 'econ_pct', 'economy_map']
                + [f'{c}|map' for c in CHECKPOINTS] + ['units@100|map', 'total@100|map', 'births@100|map']
                + [f'{c}|pct' for c in TIER2])
        print('\n== pool (three-number form: |map = vs field median, |pct = field percentile, '
              'tier2 |pct = share of field beaten, higher=better) ==')
        print(t[cols].to_csv(sep='\t', float_format='%.3f'))

    g = tables.get('gen')
    if g is not None:
        cols = (['n', 'win'] + list(CHECKPOINTS) + ['units@100', 'total@100', 'births@100']
                + list(TIER2))
        print('\n== gen (raw medians, no field reference) ==')
        print(g[cols].to_csv(sep='\t', float_format='%.1f'))

    if a.parent:
        for panel, pt in tables.items():
            def keyed(bot):
                H = apply_field_rel(derive(rows_for(panel_root(panel, f'bots/{bot}'), bot, seeds), med, refs), refs)
                H = H.copy()
                H['seed'] = H['game'].str.split('__').str[0]
                return H.set_index(['map', 'seed', 'opponent', 'side'])
            mc, mp = keyed(a.bot), keyed(a.parent)
            joined = mc.join(mp, rsuffix='_p', how='inner')
            print(f'\n== {panel}: paired per-map deltas {a.bot} - {a.parent} '
                  f'(n pairs {len(joined)}) ==')
            out = []
            for m, gj in joined.groupby('map'):
                r = {'map': m, 'n': len(gj), 'dwin': float(gj['won'].mean() - gj['won_p'].mean())}
                for c in CHECKPOINTS + ['units@100', 'total@100'] + TIER2:
                    r[f'd{c}'] = float((gj[c] - gj[c + '_p']).median())
                out.append(r)
            d = pd.DataFrame(out).set_index('map')
            cols = ['n', 'dwin'] + [f'd{c}' for c in CHECKPOINTS] + ['dunits@100', 'dtotal@100'] \
                   + [f'd{c}' for c in TIER2]
            print(d[cols].to_csv(sep='\t', float_format='%.3f'))

    outp = pathlib.Path(f'game_stats/runs/{a.bot}-bricklist-{a.panels}.tsv')
    with outp.open('w') as fh:
        for panel, t in tables.items():
            fh.write(f'# {panel}\n')
            t.to_csv(fh, sep='\t', float_format='%.4f')
    print(f'\nwrote {outp}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
