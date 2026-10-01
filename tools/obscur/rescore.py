#!/usr/bin/env python3
"""Obscur (H-1) gate audit: re-score past candidate/parent pairs under D-032 variants.

Reads finished lane runs (features.parquet, the verso/maelle/rc layout <runs>/<arm>/<panel>/features*/) and prints,
per pair and panel, the economy delta under
  med   — D-032 as the lanes implement it: mean over p50..p250 of [median(cand) - median(parent)] (econ~)
  mean  — mean of paired per-game differences of the four-checkpoint mean (D-032's literal "economy mean")
each with a plain row bootstrap (rows = seed x map x opp x seat, as every lane gate) and a fixture-cluster
bootstrap (clusters = map x opp x seat, seeds kept together; tools/rb/gate.py's form), plus
  win, units@100, length@100 (cluster bootstrap), and endgame terms:
  L499  — median longest@499 delta (parent-relative; no field reference exists)
  conv  — win rate in games reaching the round limit (reason != elimination)
  lead_loss — P(loss | round limit, total_margin_end > 0)
and the combined-panel form: one economy statistic over pool + gen fixtures with the two panels weighted equally.

    .venv/bin/python tools/obscur/rescore.py PAIRS.json [--boot 2000]
PAIRS.json: [{"name":..., "cand": [runs_dir, arm, bot], "parent": [runs_dir, arm, bot]}, ...]
"""
import argparse, glob, json, sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ECON = ['pearls@50', 'pearls@100', 'pearls@150', 'pearls@250']
MAT = ['units@100', 'total@100']
KEY = ['seed', 'mapkey', 'opp', 'side']
CL = ['mapkey', 'opp', 'side']
COLS = ['game', 'side', 'bot', 'opponent', 'map', 'result', 'reason', 'longest@499', 'total_margin_end'] + ECON + MAT


def load(runs, arm, bot, panel):
    fs = sorted(glob.glob(f'{runs}/{arm}/{panel}/features*/features.parquet'))
    if not fs:
        return None
    F = pd.concat([pd.read_parquet(f, columns=[c for c in COLS if c in pd.read_parquet(f).columns]) for f in fs],
                  ignore_index=True).drop_duplicates(['game', 'side'])
    F = F[F['bot'] == bot].copy()
    if not len(F):
        print(f'no rows for {bot} in {runs}/{arm}/{panel}', file=sys.stderr)
        return None
    p = F['game'].str.split('__', expand=True)
    F['seed'] = p[0].str[1:].astype(int)
    F['mapkey'] = p[1]
    F['opp'] = F['opponent']
    F = F[F['seed'].isin([1, 2, 3])]
    F['win'] = F['result'].map({'win': 1.0, 'draw': 0.5, 'loss': 0.0})
    if panel == 'pool':
        ref = json.load(open(ROOT / 'docs/analysis/benchmarks/map_reference_medians.json'))
        for c in ECON + MAT:
            F[c + '|n'] = F[c] / F['map'].map(ref[c]).replace(0, np.nan)
    else:
        ref = json.load(open(ROOT / 'tools/ra/gen_reference.json'))
        for c in ECON + MAT:
            F[c + '|n'] = F[c] / F['mapkey'].map(lambda k: max(1.0, ref.get(k, {}).get(c, np.nan)))
    F['econ'] = F[[c + '|n' for c in ECON]].mean(axis=1)
    F['rl'] = (F['reason'] != 'elimination').astype(float)
    F['lead'] = ((F['rl'] == 1) & (F['total_margin_end'] > 0)).astype(float)
    return F


def stats(m):
    """m: merged paired frame (suffixes _c/_p) -> dict of statistics"""
    s = {}
    s['med'] = np.mean([m[c + '|n_c'].median() - m[c + '|n_p'].median() for c in ECON])
    s['mean'] = float((m['econ_c'] - m['econ_p']).mean())
    s['win'] = float((m['win_c'] - m['win_p']).mean())
    for c in MAT:
        s[c] = float(m[c + '|n_c'].median() - m[c + '|n_p'].median())
    s['L499'] = float(m['longest@499_c'].median() - m['longest@499_p'].median())
    rc, rp = m[m['rl_c'] == 1], m[m['rl_p'] == 1]
    s['conv'] = float(rc['win_c'].mean() - rp['win_p'].mean()) if len(rc) and len(rp) else np.nan
    lc, lp = m[m['lead_c'] == 1], m[m['lead_p'] == 1]
    s['lead_loss'] = float((lc['win_c'] == 0).mean() - (lp['win_p'] == 0).mean()) if len(lc) and len(lp) else np.nan
    return s


def boot(m, nb, cluster, rng):
    if cluster:
        g = m.groupby(CL).indices
        groups = list(g.values())
        out = []
        for _ in range(nb):
            pick = rng.integers(0, len(groups), len(groups))
            out.append(stats(m.iloc[np.concatenate([groups[i] for i in pick])]))
    else:
        out = [stats(m.iloc[rng.integers(0, len(m), len(m))]) for _ in range(nb)]
    return pd.DataFrame(out)


def pair(c, p):
    keep = KEY + ['econ', 'win', 'rl', 'lead', 'longest@499'] + [x + '|n' for x in ECON + MAT]
    return c[keep].merge(p[keep], on=KEY, suffixes=('_c', '_p'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pairs')
    ap.add_argument('--boot', type=int, default=1000)
    a = ap.parse_args()
    rng = np.random.default_rng(7)
    rows = []
    for pr in json.load(open(a.pairs)):
        ms = {}
        for panel in ('pool', 'gen'):
            c, p = load(*pr['cand'], panel), load(*pr['parent'], panel)
            if c is None or p is None:
                continue
            m = pair(c, p)
            if not len(m):
                continue
            ms[panel] = m
            pt = stats(m)
            bp, bc = boot(m, a.boot, False, rng), boot(m, a.boot, True, rng)
            lo = lambda b, k: float(b[k].quantile(0.05))
            hi = lambda b, k: float(b[k].quantile(0.95))
            r = dict(pair=pr['name'], panel=panel, n=len(m), nclus=m.groupby(CL).ngroups)
            for k in ('med', 'mean', 'win', 'units@100', 'total@100', 'L499', 'conv', 'lead_loss'):
                r[k] = round(pt[k], 4)
                r[k + '_lo_plain'] = round(lo(bp, k), 4)
                r[k + '_lo_clus'] = round(lo(bc, k), 4)
                r[k + '_hi_clus'] = round(hi(bc, k), 4)
            rows.append(r)
        if len(ms) == 2:  # combined: equal panel weight, cluster bootstrap within each panel
            for k in ('med', 'mean'):
                pts = [stats(ms[pn])[k] for pn in ('pool', 'gen')]
                bs = [boot(ms[pn], a.boot, True, rng)[k].values for pn in ('pool', 'gen')]
                comb = 0.5 * (bs[0] + bs[1])
                rows.append(dict(pair=pr['name'], panel='comb', n=len(ms['pool']) + len(ms['gen']),
                                 **{k: round(0.5 * sum(pts), 4), k + '_lo_clus': round(float(np.quantile(comb, 0.05)), 4),
                                    k + '_hi_clus': round(float(np.quantile(comb, 0.95)), 4)}))
    R = pd.DataFrame(rows)
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60); pd.set_option('display.max_rows', 500)
    print(R.to_string(index=False))
    out = Path(a.pairs).with_suffix('.out.json')
    R.to_json(out, orient='records', indent=1)
    print('->', out)


if __name__ == '__main__':
    main()
