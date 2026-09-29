#!/usr/bin/env python3
"""Maelle weight fitters over MAELLE_PARAMS on paired fixtures (SF-1 Part 2).

    PY=.venv/bin/python
    # one weight: a paired grid over values (each value is a lane arm), a quadratic fitted to the paired objective,
    # and a bootstrap interval of its optimum (CLOP-style regression; value 0 = the parent arm, reused)
    $PY tools/maelle/tune.py scan --bot maelle-02-features --var wt_food --values -0.6,-0.3,0.3,0.6 \
        --parent maelle-01-nodevil [--base "wt_x=0.2"] [--panel pool] [--seeds 1] [--jobs 14]
    # the active set jointly: SPSA, plus and minus arms on the same fixture batch each iteration
    $PY tools/maelle/tune.py spsa --bot maelle-02-features --vars wt_food=0.3,wm_ally=-0.2 --iters 12 --batch 40

Objective per side-game (J): econ (mean of the four normalised pearls@k) + 0.5 * mean(units@100, length@100)
normalised - 0.08 * ally head-on deaths per 1k. The material credit and the head-on price keep the fit off the
churn economy (L29); the accept test is always the D-032 gate in lane.py, never J. Every evaluation is logged
(params, fixture, all metrics) to build/maelle/tune/<name>/evals.jsonl and the summary to game_stats/runs/maelle/.
"""
from __future__ import annotations

import argparse, json, math, os, random, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools' / 'maelle'))
import lane  # noqa: E402

TUNE = ROOT / 'build/maelle/tune'
OUT = ROOT / 'game_stats/runs/maelle'
KEY = ['seed', 'mapkey', 'opp', 'side']


def fmt(v):
    return f'{v:.4g}'


def params_str(d):
    return ','.join(f'{k}={fmt(v)}' for k, v in sorted(d.items()) if v != 0)


def parse_params(s):
    out = {}
    for kv in filter(None, (s or '').split(',')):
        k, v = kv.split('=')
        out[k.strip()] = float(v)
    return out


def register(name, bot, params):
    A = lane.arms()
    spec = dict(bot=bot, params=params)
    if name in A and A[name] != spec:
        raise SystemExit(f'arm {name} exists with a different spec')
    A[name] = spec
    lane.ARMS.parent.mkdir(parents=True, exist_ok=True)
    lane.ARMS.write_text(json.dumps(A, indent=1, sort_keys=True))


def play(jobs_list, jobs):
    """jobs_list: (arm, panel, fixture). Runs missing games across all arms in one pool, then extracts."""
    todo, bots = [], set()
    for arm, panel, fx in jobs_list:
        bot, params = lane.arm_spec(arm)
        bots.add(bot)
        root = lane.RUNS / arm / panel
        (root / 'replays').mkdir(parents=True, exist_ok=True)
        if not (root / 'arm.json').exists():
            (root / 'arm.json').write_text(json.dumps(dict(arm=arm, bot=bot, params=params)))
        if not (root / 'replays' / (fx['game'] + '.replay')).exists() and fx['game'] not in lane.claimed(root):
            todo.append((root, params, fx))
    for b in bots:
        lane.prebuild(b)
    todo.sort(key=lambda t: t[2]['map'] not in lane.HEAVY)
    t0 = time.time()
    print(f'play: {len(todo)} games to run', flush=True)
    with ThreadPoolExecutor(jobs) as ex:
        futs = {ex.submit(lane.run_one, fx, root, params): root for root, params, fx in todo}
        for i, f in enumerate(as_completed(futs), 1):
            row = f.result()
            if row:
                with open(futs[f] / f'index-{lane.HOST}.jsonl', 'a') as idx:
                    idx.write(json.dumps(row) + '\n')
            if i % 25 == 0:
                print(f'  {i}/{len(todo)} {time.time() - t0:.0f}s', flush=True)
    done = set()
    for arm, panel, _ in jobs_list:
        if (arm, panel) not in done:
            done.add((arm, panel))
            lane.extract(arm, panel)


def frame(arm, panel, seeds):
    F = lane.load(arm, panel, seeds)
    if F is None or not len(F):
        return None
    F = lane.normalise(F, panel)
    F['J'] = objective(F)
    F['panel'] = panel
    return F


def objective(F):
    mat = 0.5 * (F['units@100|n'].fillna(0) + F['total@100|n'].fillna(0))
    return F['econ|n'].fillna(0) + 0.5 * mat - 0.08 * F['death_h2h_ally_per1k'].fillna(0)


METRICS = ['J', 'econ|n', 'pearls@50|n', 'pearls@100|n', 'pearls@150|n', 'pearls@250|n', 'units@100|n',
           'total@100|n', 'win'] + lane.HYG


def paired(Fc, Fp):
    k = KEY + ['panel']
    return Fc[k + METRICS].merge(Fp[k + METRICS], on=k, suffixes=('_c', '_p'))


def log_evals(path, tag, params, F):
    with open(path, 'a') as o:
        for r in F.to_dict('records'):
            o.write(json.dumps(dict(tag=tag, params=params, **{k: (r[k] if not isinstance(r[k], float) or
                                                                   math.isfinite(r[k]) else None)
                                                                for k in KEY + ['panel'] + METRICS if k in r})) + '\n')


# ----------------------------------------------------------------- scan
def cmd_scan(a):
    import numpy as np
    seeds = [int(s) for s in a.seeds.split(',')]
    panels = a.panel.split('+')
    base = parse_params(a.base)
    values = [float(v) for v in a.values.split(',')]
    name = a.name or f"scan-{a.var}" + (f"-on-{params_str(base)}" if base else '')
    wd = TUNE / name
    wd.mkdir(parents=True, exist_ok=True)
    arms_ = {}
    for v in values:
        p = dict(base); p[a.var] = v
        arm = f"{a.bot}~{params_str(p)}"
        register(arm, a.bot, params_str(p))
        arms_[v] = arm
    parent = a.parent
    if base:  # value 0 on a non-empty base is its own arm
        arms_[0.0] = f"{a.bot}~{params_str(base)}"
        register(arms_[0.0], a.bot, params_str(base))
    jl = []
    for arm in list(arms_.values()) + ([parent] if not base else []):
        bot, _ = lane.arm_spec(arm)
        for panel in panels:
            for fx in lane.fixtures(bot, panel, seeds):
                jl.append((arm, panel, fx))
    if not a.score_only:
        play(jl, a.jobs)
    ref_arm = arms_.get(0.0, parent)
    Fp = [frame(ref_arm, p, seeds) for p in panels]
    Fp = __import__('pandas').concat([f for f in Fp if f is not None], ignore_index=True)
    ev = wd / 'evals.jsonl'
    ev.unlink(missing_ok=True)
    log_evals(ev, 'ref', params_str(base), Fp)
    rows, D = [], {}
    for v in sorted(arms_):
        if arms_[v] == ref_arm:
            continue
        Fc = __import__('pandas').concat([f for f in (frame(arms_[v], p, seeds) for p in panels) if f is not None],
                                         ignore_index=True)
        log_evals(ev, arms_[v], params_str({**base, a.var: v}), Fc)
        m = paired(Fc, Fp)
        D[v] = m
        rows.append(dict(value=v, n=len(m), **{f'd_{k}': float((m[k + '_c'] - m[k + '_p']).mean()) for k in METRICS}))
    # quadratic fit of the paired dJ over values (0 -> 0 by construction), bootstrap over fixtures
    xs = [0.0] + [r['value'] for r in rows]
    common = None
    for v, m in D.items():
        kk = set(map(tuple, m[KEY + ['panel']].astype(str).to_numpy()))
        common = kk if common is None else common & kk
    rng = np.random.default_rng(11)
    Y = {}
    for v, m in D.items():
        m = m.copy()
        m['_k'] = list(map(tuple, m[KEY + ['panel']].astype(str).to_numpy()))
        m = m[m['_k'].isin(common)].sort_values('_k')
        Y[v] = (m['J_c'] - m['J_p']).to_numpy()
    n = len(next(iter(Y.values()))) if Y else 0
    lo, hi = min(xs), max(xs)

    def fit(ix):
        X = np.array(xs); y = np.array([0.0] + [Y[v][ix].mean() for v in sorted(Y)])
        c = np.polyfit(X, y, 2)
        grid = np.linspace(lo, hi, 201)
        g = np.polyval(c, grid)
        return grid[int(np.argmax(g))], c

    best, coef = fit(np.arange(n)) if n else (0.0, [0, 0, 0])
    boots = [fit(rng.integers(0, n, n))[0] for _ in range(1000)] if n else [0.0]
    q = np.percentile(boots, [5, 50, 95])
    res = dict(name=name, bot=a.bot, var=a.var, base=params_str(base), parent=ref_arm, seeds=seeds, panels=panels,
               n_common=n, rows=rows, quad=[float(c) for c in coef], argmax=float(best),
               argmax_90=[float(q[0]), float(q[2])], argmax_boot_median=float(q[1]),
               edge=bool(best in (lo, hi)))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'{name}.json').write_text(json.dumps(res, indent=1))
    print(f"== scan {a.var} on [{params_str(base)}] vs {ref_arm}, {n} common fixtures, panels {panels} seeds {seeds}")
    print('  value   n    dJ      d_econ  d_p50   d_p100  d_p150  d_p250  d_u100  d_t100  d_win   d_h2hA')
    for r in rows:
        print(f"  {r['value']:+6.3f} {r['n']:4d} {r['d_J']:+.4f} {r['d_econ|n']:+.4f} {r['d_pearls@50|n']:+.4f} "
              f"{r['d_pearls@100|n']:+.4f} {r['d_pearls@150|n']:+.4f} {r['d_pearls@250|n']:+.4f} "
              f"{r['d_units@100|n']:+.4f} {r['d_total@100|n']:+.4f} {r['d_win']:+.4f} {r['d_death_h2h_ally_per1k']:+.3f}")
    print(f"  quadratic dJ = {coef[0]:+.4f} w^2 {coef[1]:+.4f} w {coef[2]:+.4f}; argmax {best:+.3f} "
          f"(bootstrap 90 % [{q[0]:+.3f}, {q[2]:+.3f}]){'  AT THE EDGE of the scanned range' if res['edge'] else ''}")


# ----------------------------------------------------------------- spsa
def cmd_spsa(a):
    import numpy as np
    import pandas as pd
    theta = parse_params(a.vars)
    names = sorted(theta)
    fixed = parse_params(a.base)
    lo = {k: -a.bound for k in names}; hi = {k: a.bound for k in names}
    seeds = [int(s) for s in a.seeds.split(',')]
    panels = a.panel.split('+')
    name = a.name or 'spsa-' + '-'.join(names)
    wd = TUNE / name
    wd.mkdir(parents=True, exist_ok=True)
    ev = wd / 'evals.jsonl'
    hist = wd / 'history.jsonl'
    rng = random.Random(a.seed)
    pool = []
    for panel in panels:
        pool += [(panel, fx) for fx in lane.fixtures(a.bot, panel, seeds)]
    A = 0.1 * a.iters
    start = 0
    if hist.exists():  # resume
        H = [json.loads(l) for l in open(hist)]
        if H:
            theta = H[-1]['theta_next']; start = H[-1]['k'] + 1
            for _ in range(start):
                rng.random()
    for k in range(start, a.iters):
        ck = a.c / (k + 1) ** 0.101
        ak = a.a / (k + 1 + A) ** 0.602
        delta = {n: rng.choice((-1, 1)) for n in names}
        plus = {n: min(hi[n], theta[n] + ck * delta[n]) for n in names}
        minus = {n: max(lo[n], theta[n] - ck * delta[n]) for n in names}
        batch = rng.sample(pool, min(a.batch, len(pool)))
        arms_ = {}
        for tag, p in (('plus', plus), ('minus', minus)):
            ps = params_str({**fixed, **p})
            arm = f"{a.bot}~{ps}" if ps else a.bot
            register(arm, a.bot, ps)
            arms_[tag] = arm
        play([(arms_[t], panel, fx) for t in arms_ for panel, fx in batch], a.jobs)
        games = {fx['game'] for _, fx in batch}
        Fs = {}
        for t, arm in arms_.items():
            parts = [frame(arm, p, seeds) for p in panels]
            F = pd.concat([f for f in parts if f is not None], ignore_index=True)
            F = F[F['game'].isin(games)] if 'game' in F else F
            Fs[t] = F
            log_evals(ev, f'k{k}:{t}', params_str({**fixed, **(plus if t == 'plus' else minus)}), F)
        m = paired(Fs['plus'], Fs['minus'])
        dj = float((m['J_c'] - m['J_p']).mean()) if len(m) else 0.0
        g = {n: dj / (2 * ck * delta[n]) for n in names}
        nxt = {n: float(min(hi[n], max(lo[n], theta[n] + ak * g[n]))) for n in names}
        rec = dict(k=k, ck=ck, ak=ak, theta=theta, delta=delta, plus=plus, minus=minus, n=len(m), dJ=dj,
                   d_econ=float((m['econ|n_c'] - m['econ|n_p']).mean()) if len(m) else 0.0, theta_next=nxt)
        with open(hist, 'a') as o:
            o.write(json.dumps(rec) + '\n')
        print(f"k={k} n={len(m)} dJ(+/-)={dj:+.4f} theta -> " + ' '.join(f"{n}={nxt[n]:+.3f}" for n in names), flush=True)
        theta = nxt
    OUT.mkdir(parents=True, exist_ok=True)
    H = [json.loads(l) for l in open(hist)]
    (OUT / f'{name}.json').write_text(json.dumps(dict(name=name, bot=a.bot, base=params_str(fixed), history=H,
                                                      final=theta), indent=1))
    print('final', params_str(theta))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('scan')
    s.add_argument('--bot', required=True); s.add_argument('--var', required=True); s.add_argument('--values', required=True)
    s.add_argument('--parent', required=True); s.add_argument('--base', default='')
    s.add_argument('--panel', default='pool'); s.add_argument('--seeds', default='1')
    s.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2)); s.add_argument('--name')
    s.add_argument('--score-only', action='store_true')
    p = sub.add_parser('spsa')
    p.add_argument('--bot', required=True); p.add_argument('--vars', required=True); p.add_argument('--base', default='')
    p.add_argument('--iters', type=int, default=12); p.add_argument('--batch', type=int, default=40)
    p.add_argument('--a', type=float, default=0.5); p.add_argument('--c', type=float, default=0.3)
    p.add_argument('--bound', type=float, default=3.0); p.add_argument('--seed', type=int, default=1)
    p.add_argument('--panel', default='pool+gen'); p.add_argument('--seeds', default='1,2,3')
    p.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2)); p.add_argument('--name')
    a = ap.parse_args()
    {'scan': cmd_scan, 'spsa': cmd_spsa}[a.cmd](a)


if __name__ == '__main__':
    main()
