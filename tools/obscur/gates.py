#!/usr/bin/env python3
"""Obscur (H-1) gate audit: verdicts of past pairs under the D-032 gate as the lanes run it and under the proposed
revision (claude/obscur-status.md, "Gate audit"). Uses tools/obscur/rescore.py's loader.

  NOW  (verso/rc/maelle lane.py): econ~ (difference of per-checkpoint medians), plain row bootstrap, 90 %;
       pool econ~ lb > 0; gen econ~ lb > -0.02; pool units@100, length@100 lb >= -0.02; pool win lb > -0.02;
       tier-2 (pool and gen means of per-1k rates) up <= 10 % where the parent rate > 0.05.
  PROP (H-1 proposal):
       fixture-cluster bootstrap (map x opp x seat, seeds together), 90 %;
       economy = paired per-game mean of the four-checkpoint mean (D-032's literal "economy mean"), econ~ reported;
       the economy, win, units@100, length@100 clauses are judged on the two panels weighted equally
       (combined lb: econ > 0; win, units, length >= -0.02), and neither panel may regress on its own:
       per-panel econ and win cluster upper bound > 0 (a significant loss on either panel fails);
       tier-2 as NOW;
       endgame guard: conversion (win rate among round-limit games), combined point estimate >= -0.03;
       late route (a change that acts after a phase boundary): econ judged on p150/p250, or on conversion
       combined lb > 0, with the r100 clauses as guards.

    .venv/bin/python tools/obscur/gates.py PAIRS.json [--boot 1000]
"""
import argparse, json, sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rescore as R  # noqa: E402

HYG = ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k']
R.COLS += HYG


def st(m):
    s = {}
    s['med'] = np.mean([m[c + '|n_c'].median() - m[c + '|n_p'].median() for c in R.ECON])
    s['late_mean'] = float(((m['pearls@150|n_c'] + m['pearls@250|n_c']) - (m['pearls@150|n_p'] + m['pearls@250|n_p'])).mean() / 2)
    s['mean'] = float((m['econ_c'] - m['econ_p']).mean())
    s['win'] = float((m['win_c'] - m['win_p']).mean())
    for c in R.MAT:
        s[c] = float(m[c + '|n_c'].median() - m[c + '|n_p'].median())
    rc, rp = m[m['rl_c'] == 1], m[m['rl_p'] == 1]
    s['conv'] = float(rc['win_c'].mean() - rp['win_p'].mean()) if len(rc) and len(rp) else 0.0
    return s


def boot(m, nb, cluster, rng):
    if cluster:
        groups = list(m.groupby(R.CL).indices.values())
        idx = lambda: np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
    else:
        idx = lambda: rng.integers(0, len(m), len(m))
    return pd.DataFrame([st(m.iloc[idx()]) for _ in range(nb)])


def tier2(m):
    bad = []
    for h in HYG:
        p, c = m[h + '_p'].mean(), m[h + '_c'].mean()
        if p > 0.05 and c > 1.10 * p:
            bad.append(f'{h.split("_")[1]}+{100 * (c / p - 1):.0f}%')
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pairs')
    ap.add_argument('--boot', type=int, default=1000)
    a = ap.parse_args()
    rng = np.random.default_rng(11)
    keep_extra = HYG
    out = []
    for pr in json.load(open(a.pairs)):
        ms = {}
        for panel in ('pool', 'gen'):
            c, p = R.load(*pr['cand'], panel), R.load(*pr['parent'], panel)
            if c is None or p is None:
                continue
            keep = R.KEY + ['econ', 'win', 'rl', 'lead', 'longest@499'] + [x + '|n' for x in R.ECON + R.MAT] + keep_extra
            ms[panel] = c[keep].merge(p[keep], on=R.KEY, suffixes=('_c', '_p'))
        if len(ms) < 2:
            print('skip (needs both panels):', pr['name']); continue
        q = lambda b, k, x: float(b[k].quantile(x))
        P = {pn: dict(pt=st(ms[pn]), bp=boot(ms[pn], a.boot, False, rng), bc=boot(ms[pn], a.boot, True, rng),
                      t2=tier2(ms[pn])) for pn in ms}
        pool, gen = P['pool'], P['gen']
        # ---- NOW
        why = []
        if q(pool['bp'], 'med', .05) <= 0: why.append(f"pool econ~ lb {q(pool['bp'], 'med', .05):+.3f}")
        if q(gen['bp'], 'med', .05) <= -0.02: why.append(f"gen econ~ lb {q(gen['bp'], 'med', .05):+.3f}")
        for k in ('units@100', 'total@100'):
            if q(pool['bp'], k, .05) < -0.02: why.append(f"pool {k} lb {q(pool['bp'], k, .05):+.3f}")
        if q(pool['bp'], 'win', .05) <= -0.02: why.append(f"pool win lb {q(pool['bp'], 'win', .05):+.3f}")
        t2 = [f'{pn}:{x}' for pn in P for x in P[pn]['t2']]
        now = 'ACCEPT' if not why and not t2 else 'REJECT'
        # ---- PROP
        comb = {k: 0.5 * (pool['bc'][k].values + gen['bc'][k].values) for k in pool['bc'].columns}
        cpt = {k: 0.5 * (pool['pt'][k] + gen['pt'][k]) for k in pool['pt']}
        cl = lambda k: float(np.quantile(comb[k], .05))
        wp = []
        if cl('mean') <= 0: wp.append(f"comb econ lb {cl('mean'):+.3f}")
        for k in ('win', 'units@100', 'total@100'):
            if cl(k) < -0.02: wp.append(f"comb {k} lb {cl(k):+.3f}")
        for pn in P:
            for k in ('mean', 'win'):
                if q(P[pn]['bc'], k, .95) <= 0: wp.append(f"{pn} {k} ub {q(P[pn]['bc'], k, .95):+.3f}")
        if cpt['conv'] < -0.03: wp.append(f"comb conv {cpt['conv']:+.3f}")
        prop = 'ACCEPT' if not wp and not t2 else 'REJECT'
        late_ok = (cl('late_mean') > 0 or cl('conv') > 0) and not t2 and \
            all(cl(k) >= -0.02 for k in ('win', 'units@100', 'total@100'))
        r = dict(pair=pr['name'], NOW=now, NOW_why='; '.join(why + t2), PROP=prop, PROP_why='; '.join(wp + t2),
                 PROP_late='ACCEPT' if late_ok else 'REJECT',
                 comb_econ=f"{cpt['mean']:+.3f} [{cl('mean'):+.3f}]", comb_econ_med=f"{cpt['med']:+.3f} [{cl('med'):+.3f}]",
                 comb_win=f"{cpt['win']:+.3f} [{cl('win'):+.3f}]", comb_conv=f"{cpt['conv']:+.3f} [{cl('conv'):+.3f}]",
                 comb_late=f"{cpt['late_mean']:+.3f} [{cl('late_mean'):+.3f}]")
        out.append(r)
        for k, v in r.items():
            print(f'{k:>14}: {v}')
        print()
    Path(a.pairs).with_suffix('.gates.json').write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
