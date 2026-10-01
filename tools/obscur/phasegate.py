#!/usr/bin/env python3
"""Obscur (H-1) phase gate — one coherent evaluation over the whole game (proposal "D-032b", claude/obscur-status.md).

Every number is a paired candidate-minus-parent delta on the same fixture (seed, map, opponent, seat), on both
panels, the two panels weighted equally, with a fixture-cluster bootstrap (map x opponent x seat, seeds kept
together; 90 % intervals). Each phase has its own measure, read on the fixtures where that phase is played *in the
parent's game* (conditioning on the parent, never on the candidate, so a candidate that ends games earlier is not
judged on a different population):

  opening   tempo (rounds behind the top-ten net-income curve, r10-150; tools/s1/tempo_gate.py's own functions;
            negative = faster), all fixtures. Net of churn by construction.
  midgame   total_share@250 (our length / both sides' length at r250; BENCHMARKS' strongest win predictor, log-odds 2.2,
            cross-map 0.59), fixtures where the parent's game is still running at r250.
  endgame   win, fixtures where the parent's game reaches r400 (conversion: who holds the length race at r500).
  outcome   win, all fixtures.
  guards    units@100|n and total@100|n (dust), tier-2 death rates (means; > +10 % fails), and the per-map twin rule
            (report only here: tools/obscur/permap.py).

Verdict:
  REJECT  outcome ub < 0 on either panel; or any phase significantly worse on the combined panels (tempo lb > 0
          rounds, midgame or endgame ub < 0); or a dust guard lb < -0.03; or a tier-2 rate up > 10 % on both panels.
  ACCEPT  not REJECT; outcome lb > -0.02; and at least one phase significantly better by a useful amount (tempo ub < 0
          and point <= -1.5 rounds; midgame lb > 0 and point >= +0.01; endgame lb > 0 and point >= +0.02).
  HOLD    otherwise (no phase moved; or one tier-2 panel up > 10 %): queue for stacking.
The old economy statistics (econ~ and the per-game mean of p@50..250|n) are printed as diagnostics.

    .venv/bin/python tools/obscur/phasegate.py PAIRS.json [--boot 1000] [--jobs 6] [--seeds 1,2,3] [--no-tempo]
PAIRS.json as tools/obscur/rescore.py: [{"name", "cand": [runs_dir, arm, bot], "parent": [runs_dir, arm, bot]}].
"""
import argparse, json, sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).resolve().parent))
import rescore as R  # noqa: E402

HYG = ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k']
EXTRA = ['total_share@250', 'rounds'] + HYG
for c in EXTRA:
    if c not in R.COLS:
        R.COLS.append(c)


def tempo_rows(runs, arm, bot, panel, jobs, seeds):
    """per-fixture tempo for one arm/panel, keyed like R.KEY; reference = frozen top-10 curve or the PARENT's median
    curve on maps without one (set later by the caller through ref_parent)"""
    import tools.s1.tempo_gate as TG
    d = Path(runs) / arm / panel / 'replays'
    files = [f for f in sorted(d.glob('*.replay')) if int(f.name.split('__')[0][1:]) in seeds]
    import multiprocessing as mp
    with mp.get_context('fork').Pool(jobs) as pool:
        games = [g for g in pool.map(TG.extract, files, chunksize=4) if 'error' not in g]
    rows = []
    for g in games:
        parts = g['game'].split('__')
        seed, mk, A, B = int(parts[0][1:]), parts[1], parts[2], parts[3]
        for side, s in g['sides'].items():
            if s['team'] == bot:
                rows.append(dict(seed=seed, mapkey=mk, opp=B if side == 'A' else A, side=side, map=g['map'],
                                 income=s['income'], loss=s['loss']))
    return rows


def add_tempo(rc, rp):
    import tools.s1.tempo_gate as TG
    ref = json.loads(TG.REF.read_text())
    refs = {}
    for m in {r['map'] for r in rp}:
        if m in ref['maps']:
            refs[m] = ref['maps'][m]
        else:
            pm = [r for r in rp if r['map'] == m]
            refs[m] = dict(income=np.median([r['income'] for r in pm], axis=0).tolist(),
                           loss=np.median([r['loss'] for r in pm], axis=0).tolist())
    out = []
    for rows in (rc, rp):
        df = pd.DataFrame([dict(seed=r['seed'], mapkey=r['mapkey'], opp=r['opp'], side=r['side'],
                                tempo=TG.tempo(r, refs[r['map']])) for r in rows if r['map'] in refs])
        out.append(df)
    return out


def stats(m):
    s = {}
    s['tempo'] = float((m['tempo_c'] - m['tempo_p']).mean()) if 'tempo_c' in m and m['tempo_c'].notna().any() else np.nan
    mid = m[m['rounds_p'] >= 250]
    s['mid'] = float((mid['total_share@250_c'] - mid['total_share@250_p']).mean())
    end = m[m['rounds_p'] >= 400]
    s['end'] = float((end['win_c'] - end['win_p']).mean())
    s['win'] = float((m['win_c'] - m['win_p']).mean())
    for c in R.MAT:
        s[c] = float((m[c + '|n_c'] - m[c + '|n_p']).mean())
    s['econ~'] = np.mean([m[c + '|n_c'].median() - m[c + '|n_p'].median() for c in R.ECON])
    s['econ_mean'] = float((m['econ_c'] - m['econ_p']).mean())
    return s


def boot(m, nb, rng):
    groups = list(m.groupby(R.CL).indices.values())
    return pd.DataFrame([stats(m.iloc[np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])])
                         for _ in range(nb)])


def tier2(m):
    out = {}
    for h in HYG:
        p, c = m[h + '_p'].mean(), m[h + '_c'].mean()
        out[h.split('_')[1] if h != 'death_h2h_ally_per1k' else 'h2h'] = (c / p - 1) if p > 0.05 else 0.0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pairs')
    ap.add_argument('--boot', type=int, default=1000)
    ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--seeds', default='1,2,3')
    ap.add_argument('--no-tempo', action='store_true')
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(',')]
    rng = np.random.default_rng(5)
    out = []
    for pr in json.load(open(a.pairs)):
        ms = {}
        for panel in ('pool', 'gen'):
            c, p = R.load(*pr['cand'], panel), R.load(*pr['parent'], panel)
            if c is None or p is None:
                continue
            c, p = c[c.seed.isin(seeds)], p[p.seed.isin(seeds)]
            keep = R.KEY + ['econ', 'win'] + [x + '|n' for x in R.ECON + R.MAT] + EXTRA
            m = c[keep].merge(p[keep], on=R.KEY, suffixes=('_c', '_p'))
            if not a.no_tempo:
                tsrc = pr.get('tempo_parent', pr['parent'])  # replays may live elsewhere when a lane imported features
                rc_, rp_ = tempo_rows(*pr['cand'], panel, a.jobs, seeds), tempo_rows(*tsrc, panel, a.jobs, seeds)
                if rc_ and rp_:
                    tc, tp = add_tempo(rc_, rp_)
                    m = m.merge(tc.merge(tp, on=R.KEY, suffixes=('_c', '_p')), on=R.KEY, how='left')
                else:
                    print(f"no replays for tempo: {pr['name']} {panel}", file=sys.stderr)
                    m['tempo_c'] = m['tempo_p'] = np.nan
            ms[panel] = m
        if len(ms) < 2:
            print('skip (needs both panels):', pr['name']); continue
        P = {pn: dict(pt=stats(ms[pn]), b=boot(ms[pn], a.boot, rng), t2=tier2(ms[pn]), n=len(ms[pn])) for pn in ms}
        cb = {k: 0.5 * (P['pool']['b'][k].values + P['gen']['b'][k].values) for k in P['pool']['b'].columns}
        cp = {k: 0.5 * (P['pool']['pt'][k] + P['gen']['pt'][k]) for k in P['pool']['pt']}
        lo = lambda k: float(np.nanquantile(cb[k], .05)); hi = lambda k: float(np.nanquantile(cb[k], .95))
        rej, why = [], []
        for pn in P:
            if P[pn]['b']['win'].quantile(.95) < 0: rej.append(f'{pn} win ub {P[pn]["b"]["win"].quantile(.95):+.3f}')
        if not a.no_tempo and np.isfinite(lo('tempo')) and lo('tempo') > 0: rej.append(f'opening slower: tempo lb {lo("tempo"):+.2f} rounds')
        if hi('mid') < 0: rej.append(f'midgame worse: share@250 ub {hi("mid"):+.3f}')
        if hi('end') < 0: rej.append(f'endgame worse: late win ub {hi("end"):+.3f}')
        for k in R.MAT:
            if lo(k) < -0.03: rej.append(f'{k} lb {lo(k):+.3f}')
        t2both = [k for k in P['pool']['t2'] if P['pool']['t2'][k] > 0.10 and P['gen']['t2'][k] > 0.10]
        t2one = [f'{pn}:{k}' for pn in P for k in P[pn]['t2'] if P[pn]['t2'][k] > 0.10 and k not in t2both]
        if t2both: rej.append('tier-2 up >10% on both panels: ' + ','.join(t2both))
        gain = []  # significant AND at least a minimum useful size (half the tempo gate's 3 rounds; 1 pp share; 2 pp win)
        if not a.no_tempo and np.isfinite(hi('tempo')) and hi('tempo') < 0 and cp['tempo'] <= -1.5: gain.append('opening')
        if lo('mid') > 0 and cp['mid'] >= 0.01: gain.append('midgame')
        if lo('end') > 0 and cp['end'] >= 0.02: gain.append('endgame')
        if rej:
            v = 'REJECT'
        elif lo('win') > -0.02 and gain and not t2one:
            v = 'ACCEPT'
        else:
            v = 'HOLD'
        f = lambda k, d=3: f'{cp[k]:+.{d}f} [{lo(k):+.{d}f}, {hi(k):+.{d}f}]'
        r = dict(pair=pr['name'], verdict=v, gains=gain, reasons=rej + (['tier-2 one panel: ' + ','.join(t2one)] if t2one else []),
                 opening_tempo=f('tempo', 2) if not a.no_tempo else 'n/a', midgame_share250=f('mid'), endgame_latewin=f('end'),
                 outcome_win=f('win'), units100=f('units@100'), length100=f('total@100'), diag_econ_med=f('econ~'),
                 diag_econ_mean=f('econ_mean'),
                 per_panel={pn: {k: round(P[pn]['pt'][k], 3) for k in ('tempo', 'mid', 'end', 'win', 'econ~', 'econ_mean')}
                            for pn in P},
                 tier2={pn: {k: round(v2, 3) for k, v2 in P[pn]['t2'].items()} for pn in P})
        out.append(r)
        print(json.dumps(r, indent=1, ensure_ascii=False)); sys.stdout.flush()
    Path(a.pairs).with_suffix('.phase.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
