"""Verso diagnostic: where an arm's economy change comes from — bed pearls vs corpse pearls, material, deaths.

    .venv/bin/python tools/verso/decomp.py ARM --parent P [--seeds 1] [--panels pool,gen]

pearls@k counts every pearl eaten, including the corpses of our own dragons (L29), so an arm that dies less can
"lose economy" while it gains material. This table separates the two on the paired fixtures.
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane as L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('arm'); ap.add_argument('--parent', required=True)
    ap.add_argument('--seeds', default='1'); ap.add_argument('--panels', default='pool,gen')
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(',')]
    for panel in a.panels.split(','):
        c, p = L.load(a.arm, panel, seeds), L.load(a.parent, panel, seeds)
        if c is None or p is None or not len(c) or not len(p):
            continue
        k = ['seed', 'mapkey', 'opp', 'side']
        cols = [f'{x}@{r}' for r in (50, 100, 150, 250) for x in ('pearls', 'bed_pearls', 'total', 'units', 'deaths', 'births')]
        m = c[k + cols + ['win', 'rounds']].merge(p[k + cols + ['win', 'rounds']], on=k, suffixes=('_c', '_p'))
        print(f'[{panel}] {a.arm} vs {a.parent}: {len(m)} paired; win {m.win_p.mean():.3f} -> {m.win_c.mean():.3f}; '
              f'rounds {m.rounds_p.mean():.0f} -> {m.rounds_c.mean():.0f}')
        print('  round | pearls | bed pearls | corpse share | total length | units | deaths | births   (parent -> arm, change)')
        for r in (50, 100, 150, 250):
            def f(x):
                u, v = m[f'{x}@{r}_p'].mean(), m[f'{x}@{r}_c'].mean()
                return f'{u:.1f} -> {v:.1f} ({(v / u - 1) * 100:+.0f} %)'
            cs = lambda s: 1 - m[f'bed_pearls@{r}_{s}'].sum() / max(1, m[f'pearls@{r}_{s}'].sum())
            print(f'  r{r:<4d} | {f("pearls")} | {f("bed_pearls")} | {cs("p"):.3f} -> {cs("c"):.3f} | {f("total")} | '
                  f'{f("units")} | {f("deaths")} | {f("births")}')


if __name__ == '__main__':
    main()
