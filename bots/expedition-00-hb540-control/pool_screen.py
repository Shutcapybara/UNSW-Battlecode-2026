#!/usr/bin/env python3
"""Complete seed-1 pool descriptions and frozen Q2 weighting sensitivity; no gate."""
import argparse
import json
from pathlib import Path
from statistics import mean
import campaign as c
import report

Q2 = c.ROOT / 'docs/findings/2026-09-30-s1-Q2-map-predictability.md'
Q2_SHA = '7eccf8b55040e6de6bc6af54bfee2eb4aefaa010042e0a8fea551e436c2f9ad3'
# Rounded published slopes in fixed order. Keep cohorts separate; the source's
# 0.16/0.49 Portals/Schooltime illustration mixes top-50 and in-scope columns.
MAPS = ['autarky', 'default', 'devil', 'dilemma', 'portals', 'queen_of_spades',
        'schooltime', 'slithery_fight', 'trauma', 'trophy']
SLOPES = {
    'old_in_scope': [.46, .38, .45, .32, .29, .44, .49, .42, .35, .39],
    'old_top50_pairs': [.41, .29, .37, .33, .16, .53, .47, .27, .36, .29],
    'clean_excluding_sss_star_cutlery': [.59, .51, .64, .47, .42, .56, .64, .51, .49, .52],
}


def normalized_weights(slopes):
    if len(slopes) != len(MAPS) or any(s <= 0 for s in slopes):
        raise ValueError('Require a positive slope for every pool map')
    squared = [s * s for s in slopes]
    return dict(zip(MAPS, [s / sum(squared) for s in squared]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', choices=c.QUEUE, default=c.QUEUE[0])
    args = ap.parse_args()
    if c.sha(Q2) != Q2_SHA:
        raise ValueError('Q2 source changed; reconcile before applying frozen slopes')
    wanted = c.panel.expected('z1', [1])
    rows, features = {}, {}
    aid = report.analysis_id()
    for bot in (c.panel.PARENT, args.candidate):
        dest = c.run_dir(bot, 'z1')
        if json.loads((dest / 'contract.json').read_text()) != c.contract(bot, 'z1'):
            raise ValueError(f'Frozen inputs changed: {bot}')
        available = c.read_rows(bot, 'z1')
        rows[bot] = {k: v for k, v in available.items() if k in wanted}
        if set(rows[bot]) != wanted:
            raise ValueError(f'Incomplete seed-1 pool: {bot}: {len(rows[bot])}/{len(wanted)}')
        features[bot] = {k: report.canonical(v, dest, aid)[0] for k, v in rows[bot].items()}
    parent, child = rows[c.panel.PARENT], rows[args.candidate]
    pf, cf = features[c.panel.PARENT], features[args.candidate]
    keys = sorted(wanted)
    maps = report.measurement_sensitivity(keys, child, parent, cf, pf)
    refs = json.loads((c.ROOT / 'docs/analysis/benchmarks/field_references.json').read_text())
    pooled = {}
    for measurement in ('arena', 'replay'):
        def matrix(botrows, feats):
            return [[(botrows[k]['us'][a] if measurement == 'arena' else feats[k][r]) /
                     refs[r][c.panel.gate.NAME[k[0]]]['median']
                     for _, a, r in c.panel.gate.ECON] for k in keys]
        pooled[measurement] = report.economy_estimands(matrix(child, cf), matrix(parent, pf))
    for m in MAPS:
        mk = [k for k in keys if k[0] == m]
        pw = [c.panel.gate.win(parent[k]) for k in mk]
        cw = [c.panel.gate.win(child[k]) for k in mk]
        maps[m]['outcomes'] = dict(parent_points=sum(pw), candidate_points=sum(cw),
            mean_delta=mean([a-b for a,b in zip(cw,pw)]),
            better=sum(a>b for a,b in zip(cw,pw)), worse=sum(a<b for a,b in zip(cw,pw)))
    policies = {'equal': dict.fromkeys(MAPS, 1 / len(MAPS))}
    policies.update({n: normalized_weights(s) for n, s in SLOPES.items()})
    weighted = {}
    for name, weights in policies.items():
        weighted[name] = dict(weights=weights,
            arena_mean=sum(weights[m]*maps[m]['arena_mean_economy_delta'] for m in MAPS),
            replay_mean=sum(weights[m]*maps[m]['replay_mean_economy_delta'] for m in MAPS),
            win_points_delta=sum(weights[m]*maps[m]['outcomes']['mean_delta'] for m in MAPS))
    out = dict(candidate=args.candidate, parent=c.panel.PARENT, seed=1, paired=len(keys),
        status='COMPLETE SEED-1 POOL SCREEN ONLY; NO GATE VERDICT',
        source_sha256=c.sha(Path(__file__)), analysis_sha256=aid, report_sha256=c.sha(Path(report.__file__)),
        q2_source_sha256=Q2_SHA, slopes=SLOPES, pooled_estimands=pooled, weighting=weighted, maps=maps,
        limitations='One fixed seed; no independent-seed or full-panel claim. Squared rounded Elo slopes '
        'are counterfactual weights, not validated economy reliability weights. No gate or threshold changes. '
        'Weighted means are not pooled medians; pooled medians above use all 160 normalized rows per side.')
    dest = c.STORE / f'{args.candidate}-seed1-pool-screen.json'
    dest.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
