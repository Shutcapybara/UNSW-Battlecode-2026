#!/usr/bin/env python3
"""Per-map decomposition for Clair candidates (the lead's direction, 1 Oct: work the problem by map as well as
collectively, without overfitting).

  PY tools/clair/by_map.py BOT [--parent PARENT] [--seeds 1,2,3]

Prints, per panel:
  per-map paired econ|n and win deltas with 90% fixture-bootstrap CIs (n per map);
  the tr-consistency check - pool delta on live map M vs gen delta on its transposed twin var/M_tr
  (a mechanism that gains on M and loses on M_tr is reading layout identity, not structure);
  a predictability-weighted pooled econ delta where the weight is S-1 Q2's per-map slope^2
  (maps where knowing the team predicts little - Portals - count less; slopes parsed from the
  docs/findings table, see SLOPES below; unweighted beside it for comparison).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/clair'))

import numpy as np  # noqa: E402

from lane import RUNS, load, normalise  # noqa: E402

K = ['seed', 'mapkey', 'opp', 'side']

# S-1 Q2 (docs/findings/2026-09-30-s1-Q2-map-predictability.md, in-scope slope per 100 Elo / 10)
SLOPES = {  # map: in-scope slope per 100 Elo (docs/findings/2026-09-30-s1-Q2-map-predictability.md table)
    'portals': 0.29, 'dilemma': 0.32, 'trauma': 0.35, 'default': 0.38, 'trophy': 0.39,
    'slithery_fight': 0.42, 'queen_of_spades': 0.44, 'devil': 0.45, 'autarky': 0.46, 'schooltime': 0.49,
}
TR = {'schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma',
      'autarky', 'devil', 'trauma'}


def pair_frames(bot, parent, seeds, panel):
    Fc, Fp = load(bot, panel, seeds), load(parent, panel, seeds)
    if Fc is None or Fp is None or not len(Fc) or not len(Fp):
        return None
    Fc, Fp = normalise(Fc, panel), normalise(Fp, panel)
    return Fc[K + ['econ|n', 'win']].merge(Fp[K + ['econ|n', 'win']], on=K, suffixes=('_c', '_p'))


def map_delta(m, rng, n=400):
    d = (m['econ|n_c'] - m['econ|n_p']).to_numpy(float)
    w = (m['win_c'] - m['win_p']).to_numpy(float)
    bs = [np.median(rng.choice(d, len(d))) for _ in range(n)]
    return (float(np.median(d)), float(np.percentile(bs, 5)), float(np.percentile(bs, 95)),
            float(w.mean()), int(len(d)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--parent', default='hb1-14-prior-r540')
    ap.add_argument('--seeds', default='1,2,3')
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(',')]
    rng = np.random.default_rng(5)
    print(f"== {a.bot} vs {a.parent} seeds {seeds} - per map (paired econ|n median delta [90% CI], dWin, n)")
    res = {}
    for panel in ('pool', 'gen'):
        m = pair_frames(a.bot, a.parent, seeds, panel)
        if m is None:
            continue
        rows = {}
        for mk, g in m.groupby('mapkey'):
            rows[mk] = map_delta(g, rng)
        res[panel] = rows
        print(f"[{panel}]")
        for mk in sorted(rows, key=lambda k: -res[panel][k][0]):
            e, lo, hi, w, n = rows[mk]
            print(f"  {mk:24s} {e:+.3f} [{lo:+.3f},{hi:+.3f}]  win {w:+.3f}  n={n}")
    if 'pool' in res:
        # predictability-weighted pooled pool delta
        num = den = 0.0
        for mk, (e, lo, hi, w, n) in res['pool'].items():
            s = SLOPES.get(mk.replace('+', '/').split('/')[-1])
            if s is None:
                continue
            num += (s * s) * e; den += s * s
        if den:
            un = float(np.mean([v[0] for v in res['pool'].values()]))
            print(f"pooled pool econ delta: unweighted {un:+.3f}  slope^2-weighted {num / den:+.3f}")
    if 'pool' in res and 'gen' in res:
        print("tr-consistency (pool M vs gen M_tr; sign agreement = structure, disagreement = layout identity):")
        for m0 in TR:
            gk = 'var+' + m0 + '_tr'
            if m0 in res['pool'] and gk in res['gen']:
                e0 = res['pool'][m0][0]; e1 = res['gen'][gk][0]
                tag = 'AGREE' if e0 * e1 > 0 else ('both~0' if abs(e0) < 0.03 and abs(e1) < 0.03 else 'DISAGREE')
                print(f"  {m0:18s} pool {e0:+.3f}  vs  {gk:24s} {e1:+.3f}   {tag}")


if __name__ == '__main__':
    main()
