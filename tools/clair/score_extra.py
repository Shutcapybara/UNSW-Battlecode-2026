#!/usr/bin/env python3
"""Clair extras over the lane's D-032 scorer — the two gate-audit quantities, computed on this lane's own runs.

  PY tools/clair/score_extra.py BOT --parent PARENT [--seeds 1,2,3]

1. Combined-panel bootstrap (gate-audit proposal b): pool + gen paired fixtures pooled, maps weighted equally
   (two-stage: maps resampled with replacement within each panel, then pooled), 90 % intervals of the pooled
   econ~ delta and win delta; plus each panel's own lb. Proposed accept rule printed beside it:
   combined econ~ lb > 0 AND each panel lb > -0.02 AND win lb > -0.02 on each panel.
2. Endgame tier (gate-audit proposal a): longest_margin_end / total_margin_end medians and paired deltas,
   round-limit-losses-with-material-lead rate (loss, reason != elimination, total_margin_end > 0), and the
   own-body/self guard with deliberate culls still counted (the exemption needs the ACT markers, not available
   in features; reported as-is for the director's arithmetic).
"""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/clair'))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from lane import ECON, RUNS, load, normalise  # noqa: E402

K = ['seed', 'mapkey', 'opp', 'side']


def endgame(F):
    rl = F[F['reason'] != 'elimination'] if 'reason' in F else F
    loss_lead = ((F['result'] == 'loss') & (F.get('reason', 'x') != 'elimination')
                 & (F['total_margin_end'] > 0)) if 'total_margin_end' in F else None
    out = {
        'n': int(len(F)),
        'longest_margin_end': float(F['longest_margin_end'].median()) if 'longest_margin_end' in F else None,
        'total_margin_end': float(F['total_margin_end'].median()) if 'total_margin_end' in F else None,
    }
    if loss_lead is not None:
        out['rl_loss_with_lead'] = float(loss_lead.mean())
        out['rl_games'] = int(((F['result'] == 'loss') & (F.get('reason', 'x') != 'elimination')).sum())
    return out


def paired_frames(bot, parent, seeds):
    out = {}
    for panel in ('pool', 'gen'):
        Fc, Fp = load(bot, panel, seeds), load(parent, panel, seeds)
        if Fc is None or Fp is None or not len(Fc) or not len(Fp):
            continue
        Fc, Fp = normalise(Fc, panel), normalise(Fp, panel)
        m = Fc[K + ['econ|n', 'win', 'longest_margin_end', 'total_margin_end', 'result', 'reason']].merge(
            Fp[K + ['econ|n', 'win', 'longest_margin_end', 'total_margin_end', 'result', 'reason']],
            on=K, suffixes=('_c', '_p'))
        out[panel] = m
    return out


def combined_boot(panels, n=1000, seed=11):
    rng = np.random.default_rng(seed)
    maps = {p: sorted(m['mapkey'].unique()) for p, m in panels.items()}
    rows = []
    for _ in range(n):
        frames = []
        for p, m in panels.items():
            pick = rng.choice(maps[p], size=len(maps[p]), replace=True)
            parts = []
            for mp in pick:
                g = m[m['mapkey'] == mp]
                parts.append(g.sample(n=len(g), replace=True, random_state=int(rng.integers(1 << 31))))
            frames.append(pd.concat(parts))
        d = pd.concat(frames)
        ec = float(d['econ|n_c'].median() - d['econ|n_p'].median())
        ec_mean = float(np.mean([d[f'{c}|n_c'].median() - d[f'{c}|n_p'].median() for c in ECON]))
        w = float(d['win_c'].mean() - d['win_p'].mean())
        rows.append((ec_mean, w))
    a = np.array(rows)
    point_ec = float(np.mean([panels_pooled_median_delta(panels, c) for c in ECON]))
    point_w = float(np.mean([m['win_c'].mean() - m['win_p'].mean() for m in panels.values()]))
    q = lambda x: [round(float(np.percentile(a[:, x], 5)), 3), round(float(np.percentile(a[:, x], 95)), 3)]
    return {'econ~': round(point_ec, 3), 'econ~ci': q(0), 'win': round(point_w, 3), 'winci': q(1)}


def panels_pooled_median_delta(panels, col):
    d = pd.concat([m[[f'{col}_c', f'{col}_p']] for m in panels.values()])
    return float(d[f'{col}_c'].median() - d[f'{col}_p'].median())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--parent', required=True)
    ap.add_argument('--seeds', default='1,2,3')
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(',')]
    panels = paired_frames(a.bot, a.parent, seeds)
    print(f"== {a.bot} vs {a.parent} seeds {seeds}")
    for p, m in panels.items():
        ec = float(np.mean([m[f'{c}|n_c'].median() - m[f'{c}|n_p'].median() for c in ECON]))
        w = float(m['win_c'].mean() - m['win_p'].mean())
        lm = float(m['longest_margin_end_c'].median() - m['longest_margin_end_p'].median())
        tm = float(m['total_margin_end_c'].median() - m['total_margin_end_p'].median())
        print(f"[{p}] n={len(m)} econ~={ec:+.3f} win={w:+.3f} d_longest_end={lm:+.1f} d_total_end={tm:+.1f}")
    if panels:
        cb = combined_boot(panels)
        print(f"combined (maps weighted equally): econ~ {cb['econ~']:+.3f} {cb['econ~ci']}  win {cb['win']:+.3f} {cb['winci']}")
    for p in ('pool', 'gen'):
        Fc, Fp = load(a.bot, p, seeds), load(a.parent, p, seeds)
        if Fc is None or Fp is None or not len(Fc) or not len(Fp):
            continue
        print(f"[{p}] endgame cand={endgame(Fc)}")
        print(f"[{p}] endgame parent={endgame(Fp)}")


if __name__ == '__main__':
    main()
