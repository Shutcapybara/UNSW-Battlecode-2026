#!/usr/bin/env python3
"""Alicia (RL-1) learning curve from game_stats/runs/alicia-train-<run>.jsonl: per generation, the centre policy
against the parent on the same fixtures (paired), the population spread, and which parameters moved.

    python3 tools/alicia/report.py s1 [--md OUT]
"""
from __future__ import annotations

import argparse, json, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATS = ['pearls@50', 'pearls@100', 'pearls@150', 'pearls@250', 'units@100', 'total@100']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--md')
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(ROOT / f'game_stats/runs/alicia-train-{a.run}.jsonl') if l.strip()]
    gens = sorted({r['gen'] for r in rows})
    L = [f'**Learning curve, run `{a.run}`**: centre minus parent on the same fixtures (paired). '
         'Percentile deltas are in field-percentile points.', '',
         '| gen | seed | n | R parent | ΔR centre | ΔC | Δpct p@50 | p@100 | p@150 | p@250 | units@100 | length@100 | P centre | Δwin | best member ΔR | pop. sd R |',
         '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    dR = []
    for g in gens:
        G = {r['tag']: r for r in rows if r['gen'] == g and 'R' in r}
        c, p = G.get('centre'), G.get('parent')
        if not c or not p:
            continue
        pop = [r['R'] for t, r in G.items() if t.startswith('p') and t != 'parent']
        dR.append(c['R'] - p['R'])
        L.append(f"| {g} | {p['seed']} | {p['n']} | {p['R']:.3f} | {c['R'] - p['R']:+.3f} | {c['C'] - p['C']:+.3f} | "
                 + ' | '.join(f"{c['pct_' + s] - p['pct_' + s]:+.3f}" for s in STATS)
                 + f" | {c['P']:.3f} | {c['win'] - p['win']:+.3f} | {max(pop) - p['R']:+.3f} | {statistics.pstdev(pop):.3f} |")
    if dR:
        k = min(4, len(dR))
        L += ['', f'Mean ΔR over all generations {statistics.mean(dR):+.4f}; over the last {k} {statistics.mean(dR[-k:]):+.4f}.']
    last = max(gens)
    c = next((r for r in rows if r['gen'] == last and r['tag'] == 'centre'), None)
    if c:
        L += ['', f'Centre evaluated in generation {last}, parameters that differ from the parent '
              '(u = log-multiplier, positive means raised):', '', '| param | value | u |', '|---|---:|---:|']
        names = [n for n, _ in json.loads((ROOT / f'build/alicia/train/{a.run}/ckpt.json').read_text())['space']]
        us = dict(zip(names, c['u']))
        for n in sorted(names, key=lambda n: -abs(us[n])):
            if n in c['params']:
                L.append(f"| `{n}` | {c['params'][n]} | {us[n]:+.2f} |")
    txt = '\n'.join(L)
    print(txt)
    if a.md:
        Path(a.md).write_text(txt + '\n')


if __name__ == '__main__':
    main()
