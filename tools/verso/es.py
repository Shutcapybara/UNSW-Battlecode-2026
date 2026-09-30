"""Verso tier 3, continuous knobs: SPSA on the opening objective (tempo-style net income) over the opening
parameter set of a phase platform (verso-p3-platform: value = base + belief * (opening - base)).

    .venv/bin/python tools/verso/es.py run NAME --arm BASE_ARM [--iters 30] [--fixtures 60] [--jobs 13]
    .venv/bin/python tools/verso/es.py show NAME

BASE_ARM gives the bot, the head blob and the base VERSO_PARAMS; the optimiser moves only "o.<knob>" values (the
opening set) in KNOBS below. Each iteration draws a fresh batch of data fixtures (train + synthetic maps, a zoo
opponent, both seats, seed 1000 + iteration — never a D-032 panel fixture), plays theta+ and theta- on the same
fixtures, and scores the paired difference of the side's net income N(t) = income - unrecovered loss (S-1's tempo
quantities, tools/s1/tempo_gate.extract) averaged over t = 10..150 and divided by the map's own mean level:

    J = mean over fixtures of  mean_t [N+(t) - N-(t)] / mean_t N_map(t)

(a relative net-income gain; the horizontal tempo lag needs a reference curve per map, which the batch is too
small to supply — the tempo gate itself is run on the held-out panels at the end). The step is
theta += clip(a * J / (2 c) * delta, +-max_step) in units of each knob's scale. History (every evaluation) is
appended to build/verso/es/NAME/history.jsonl; the run resumes from it.
"""
from __future__ import annotations

import argparse, json, os, shutil, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common as C
import lane as L

# knob -> (scale, lower bound, upper bound); start = the compiled base value (read from the bot's params.hpp)
KNOBS = {
    'pearl_value': (2.0, 1.0, 30.0), 'bed_value': (2.0, 0.0, 30.0), 'memory_value': (1.5, 0.0, 30.0),
    'unseen_value': (1.5, 0.0, 30.0), 'dive_value': (1.0, 0.0, 30.0), 'target_gamma': (0.02, 0.80, 0.99),
    'own_target_discount': (0.10, 0.0, 1.0), 'enemy_target_discount': (0.15, 0.0, 1.0),
    'goal_weight': (0.4, 0.0, 5.0), 'crowd_weight': (0.3, 0.0, 3.0), 'visit_weight': (0.08, 0.0, 1.0),
    'momentum_weight': (0.2, 0.0, 2.0), 'trap_farm_factor': (0.08, 0.0, 1.0), 'split_value': (2.0, 0.0, 30.0),
    'bed_wait': (3.0, 0.0, 30.0), 'lam_dir': (0.4, 0.0, 4.0), 'opening_production_until': (10.0, 0.0, 150.0),
    'search_cap': (40.0, 40.0, 600.0),
}
ES = C.B / 'es'


def base_values(bot, base_params):
    import re
    txt = (C.ROOT / 'bots' / bot / 'params.hpp').read_text()
    out = {}
    for k in KNOBS:
        m = re.search(r'static inline (?:double|int) %s = ([-0-9.e]+);' % k, txt)
        if m:
            out[k] = float(m.group(1))
    for kv in base_params.split(','):
        if '=' in kv:
            k, v = kv.split('=')
            k = k[2:] if k.startswith('p.') else k
            if k in KNOBS:
                out[k] = float(v)
    return out


def fixtures(it, n, bot):
    rng = np.random.default_rng(90001 + it)
    synth = sorted(p.stem for p in (C.ROOT / 'build/verso/maps').glob('vt_*.map'))
    maps = [('train', m) for m in L.TRAIN_MAPS + L.LIVE_MAPS if m != 'arena'] + [('synth', m) for m in synth]
    pick = rng.choice(len(maps), n, replace=n > len(maps))
    out = []
    for i in pick:
        panel, m = maps[i]
        opp = L.ZOO[int(rng.integers(len(L.ZOO)))]
        for a, b in ((bot, opp), (opp, bot)):
            out.append(dict(panel=panel, map=m, seed=1000 + it, botA=a, botB=b, opp=opp,
                            seat='A' if a == bot else 'B', game=f's{1000 + it}__{m}__{a}__{b}'))
    seen, uniq = set(), []
    for f in out:
        if f['game'] not in seen:
            seen.add(f['game']); uniq.append(f)
    return uniq


def play(fx, root, spec, jobs):
    (root / 'replays').mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(jobs) as ex:
        rows = list(ex.map(lambda f: L.run_one(f, root, spec), fx))
    return [r for r in rows if r]


def net_income(root, bot):
    """-> {game: mean_t N(t) over t = 10..150 for the side played by `bot`, map}"""
    from tools.s1 import tempo_gate as TG
    import multiprocessing as mp
    out = {}
    files = sorted((root / 'replays').glob('*.replay'))
    with mp.get_context('fork').Pool(8) as pool:
        res = pool.map(TG.extract, files, chunksize=2)
    for p, r in zip(files, res):
        if 'error' in r:
            continue
        for side, s in r['sides'].items():
            if s['team'] == bot:
                N = np.asarray(s['income'], float) - np.asarray(s['loss'], float)
                out[p.stem] = (float(N[TG.IDX].mean()), r['map'], float(s['won']))
    return out


def paired_J(a, b):
    """relative net-income gain of arm a over arm b on their common fixtures -> (J, se, n, win diff)"""
    keys = sorted(set(a) & set(b))
    if not keys:
        return 0.0, 0.0, 0, 0.0
    level = {}
    for k in keys:
        level.setdefault(a[k][1], []).extend([a[k][0], b[k][0]])
    d = np.array([(a[k][0] - b[k][0]) / max(1.0, float(np.mean(level[a[k][1]]))) for k in keys])
    w = np.mean([a[k][2] - b[k][2] for k in keys])
    return float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else 0.0, len(d), float(w)


def params_of(base_params, theta):
    o = ','.join(f'o.{k}={v:.6g}' for k, v in theta.items())
    return ','.join(x for x in (base_params, o) if x)


def cmd_run(a):
    spec0 = L.arm_full(a.arm)
    bot = spec0['bot']
    L.prebuild(bot)
    for o in L.ZOO:
        L.prebuild(o)
    d = ES / a.name
    d.mkdir(parents=True, exist_ok=True)
    hist_p = d / 'history.jsonl'
    hist = [json.loads(l) for l in open(hist_p)] if hist_p.exists() else []
    names = list(KNOBS)
    theta0 = base_values(bot, spec0['params'])
    x = np.array([theta0[k] / KNOBS[k][0] for k in names])          # in units of each knob's scale
    lo = np.array([KNOBS[k][1] / KNOBS[k][0] for k in names]); hi = np.array([KNOBS[k][2] / KNOBS[k][0] for k in names])
    for h in hist:
        if h['kind'] == 'step':
            x = np.array(h['x_after'])
    start = 1 + max([h['iter'] for h in hist if h['kind'] == 'step'], default=0)
    th = lambda v: {k: float(np.clip(v[i], lo[i], hi[i]) * KNOBS[k][0]) for i, k in enumerate(names)}
    for it in range(start, a.iters + 1):
        rng = np.random.default_rng(777 + it)
        delta = rng.choice([-1.0, 1.0], len(names))
        ck = a.c / it ** 0.101
        ak = a.a / (it + 5) ** 0.602
        fx = fixtures(it, a.fixtures, bot)
        res = {}
        for sign, tag in ((+1, 'plus'), (-1, 'minus')):
            root = d / f'it{it:03d}' / tag
            spec = dict(spec0, params=params_of(spec0['params'], th(x + sign * ck * delta)))
            play(fx, root, spec, a.jobs)
            res[tag] = net_income(root, bot)
        J, se, n, dw = paired_J(res['plus'], res['minus'])
        step = np.clip(ak * J / (2 * ck) * delta, -a.max_step, a.max_step)
        x = np.clip(x + step, lo, hi)
        row = dict(kind='step', iter=it, J=J, se=se, n=n, dwin=dw, c=ck, a=ak, delta=delta.tolist(),
                   x_after=x.tolist(), theta=th(x))
        with open(hist_p, 'a') as f:
            f.write(json.dumps(row) + '\n')
        print(f'it {it}: J {J:+.4f} +- {se:.4f} (n {n}, dwin {dw:+.3f})  |step| {np.abs(step).mean():.3f}', flush=True)
        for tag in ('plus', 'minus'):   # the tempo cache keeps what is needed; replays are not
            shutil.rmtree(d / f'it{it:03d}' / tag / 'replays', ignore_errors=True)
        if it % a.check_every == 0:     # current theta against the base on a fixed held-out-from-ES batch
            fxv = fixtures(100000, a.fixtures, bot)
            rb, rc = d / 'check' / 'base', d / 'check' / f'it{it:03d}'
            play(fxv, rb, spec0, a.jobs)
            play(fxv, rc, dict(spec0, params=params_of(spec0['params'], th(x))), a.jobs)
            Jv, sev, nv, dwv = paired_J(net_income(rc, bot), net_income(rb, bot))
            with open(hist_p, 'a') as f:
                f.write(json.dumps(dict(kind='check', iter=it, J=Jv, se=sev, n=nv, dwin=dwv, theta=th(x))) + '\n')
            print(f'   check vs base at it {it}: J {Jv:+.4f} +- {sev:.4f} (n {nv}, dwin {dwv:+.3f})', flush=True)
            shutil.rmtree(rc / 'replays', ignore_errors=True)
    print('theta:', json.dumps(th(x)))
    print('VERSO_PARAMS:', params_of(spec0['params'], th(x)))


def cmd_show(a):
    hist = [json.loads(l) for l in open(ES / a.name / 'history.jsonl')]
    for h in hist:
        if h['kind'] == 'check':
            print(f"check it {h['iter']}: J {h['J']:+.4f} +- {h['se']:.4f} dwin {h['dwin']:+.3f}")
    steps = [h for h in hist if h['kind'] == 'step']
    if steps:
        print('iters', len(steps), 'mean J', np.mean([h['J'] for h in steps]).round(4))
        print(json.dumps(steps[-1]['theta'], indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('name'); r.add_argument('--arm', required=True)
    r.add_argument('--iters', type=int, default=30); r.add_argument('--fixtures', type=int, default=60)
    r.add_argument('--jobs', type=int, default=13); r.add_argument('--a', type=float, default=12.0)
    r.add_argument('--c', type=float, default=1.0); r.add_argument('--max-step', type=float, default=0.3)
    r.add_argument('--check-every', type=int, default=5)
    s = sub.add_parser('show'); s.add_argument('name')
    a = ap.parse_args()
    {'run': cmd_run, 'show': cmd_show}[a.cmd](a)


if __name__ == '__main__':
    main()
