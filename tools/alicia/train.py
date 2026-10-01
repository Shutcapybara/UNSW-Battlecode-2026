#!/usr/bin/env python3
"""Alicia (RL-1) optimiser for layer (a): antithetic evolution strategies over Ares evaluation weights.

One generation = one paired batch: the centre, the parent (all defaults) and N antithetic pairs centre +/- sigma*eps
play the SAME fixtures (maps x both seats, opponents drawn per fixture, seed = seed_base + generation). Fitness is
tools/alicia/reward.py's R; ranks are centred within the generation (never compared across seeds); the centre moves
by Adam on the rank-shaped antithetic gradient. A checkpoint (JSON) is written after every generation; --resume
continues from it. Summary rows (one per policy per generation) go to game_stats/runs/alicia-train-<run>.jsonl.

    python3 tools/alicia/train.py --run s1 --stage 1 --gens 16 [--pairs 8] [--jobs 14] [--resume]
"""
from __future__ import annotations

import argparse, json, math, os, random, re, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.alicia import env as E  # noqa: E402
from tools.alicia.reward import Curve, policy_reward  # noqa: E402

ZOO = ['fenrir-v18-arrival-ready-beds', 'yuna-v05-core', 'chaewon-y04-probe', 'sinbad-v07-divecap',
       'gavroche-v32-supported-divecap', 'ouroboros-m01-vibing-mimic', 'kazuha-s01-swarm-dissolve',
       'hunter-v20-portal-scouts']  # == tools.analysis.features.run_panel.ZOO
POOL = ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma',
        'autarky', 'devil', 'trauma']
HELD_IN = ['arena', 'big_empty', 'Colosseum', 'default_small', 'stronghold']  # on neither panel (dilemma_10.map fails the engine's map check)

# (name, kind). kind: log = th0*e^u; gamma = horizon 1/(1-g) moves log; hyst = 1 + (h0-1)e^u; clip1 = min(1, th0 e^u);
# int = round(th0 e^u) >= 1
SPACE = [('pearl_value', 'log'), ('memory_value', 'log'), ('bed_value', 'log'), ('unseen_value', 'log'),
         ('dive_value', 'log'), ('target_gamma', 'gamma'), ('own_target_discount', 'clip1'),
         ('enemy_target_discount', 'clip1'), ('target_hysteresis', 'hyst'), ('momentum_weight', 'log'),
         ('visit_weight', 'log'), ('goal_weight', 'log'), ('sprint_cost', 'log'), ('crowd_weight', 'log'),
         ('trap_weight', 'log'), ('threat_weight', 'log'), ('w_bed_block', 'log'), ('w_flank', 'log'),
         ('density_ally_weight', 'log'), ('density_enemy_weight', 'log'), ('split_value', 'log'),
         ('material_unit_value', 'log'), ('search_cap', 'int'), ('search_cap_late', 'int')]
U_MAX = 1.2


def defaults(bot=E.BOT):
    txt = (ROOT / 'bots' / bot / 'params.hpp').read_text()
    out = {}
    for name, _ in SPACE:
        m = re.search(rf'static (?:inline|constexpr) (?:double|int) {name} = ([^;]+);', txt)
        out[name] = float(m.group(1))
    return out


def decode(u, d0):
    """u vector -> Params overrides (only the ones that differ from the default are emitted)."""
    out = {}
    for (name, kind), x in zip(SPACE, u):
        th0 = d0[name]
        if kind == 'log':
            v = th0 * math.exp(x)
        elif kind == 'clip1':
            v = min(1.0, th0 * math.exp(x))
        elif kind == 'gamma':
            v = 1 - 1 / ((1 / (1 - th0)) * math.exp(x))
        elif kind == 'hyst':
            v = 1 + (th0 - 1) * math.exp(x)
        elif kind == 'int':
            v = max(1, int(round(th0 * math.exp(x))))
        if kind != 'int':
            v = float(f'{v:.6g}')
        if abs(x) > 1e-12 and v != th0:
            out[name] = v
    return out


def fixtures_for(stage, gen, seed_base, rng, maps=None):
    maps = maps or (POOL + (HELD_IN if stage >= 2 else []))
    fx = []
    for m in maps:
        opps = rng.sample(ZOO, 2)  # a different opponent per seat
        for seat, o in zip('AB', opps):
            fx.append(dict(map=m, seat=seat, seed=seed_base + gen, opp=o))
    return fx


def centred_ranks(x):
    x = np.asarray(x); r = np.empty(len(x)); r[np.argsort(x)] = np.arange(len(x))
    return r / (len(x) - 1) - 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', required=True)
    ap.add_argument('--stage', type=int, default=1)
    ap.add_argument('--gens', type=int, default=16)
    ap.add_argument('--pairs', type=int, default=8)
    ap.add_argument('--sigma', type=float, default=0.20)
    ap.add_argument('--lr', type=float, default=0.05)
    ap.add_argument('--reward', default='curve', choices=['curve', 'gate'])
    ap.add_argument('--opt', default='adam', choices=['adam', 'sgd'],
                    help='sgd: step = lr * gradient, so a signal-free coordinate barely moves (s1 finding: Adam '
                         'normalises noise into a fixed-size random walk)')
    ap.add_argument('--beta', type=float, default=None, help='terminal weight; default by stage (1,2: 0; 3: 0.25->0.5)')
    ap.add_argument('--seed-base', type=int, default=1000)
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--maps', help='comma list overriding the stage maps (smoke tests only)')
    ap.add_argument('--init', help='checkpoint JSON to start the centre from (stage chaining)')
    a = ap.parse_args()

    out = ROOT / 'build/alicia/train' / a.run
    out.mkdir(parents=True, exist_ok=True)
    ck = out / 'ckpt.json'
    log_rows = ROOT / 'game_stats/runs' / f'alicia-train-{a.run}.jsonl'
    log_rows.parent.mkdir(parents=True, exist_ok=True)
    d0 = defaults()
    D = len(SPACE)
    if a.resume and ck.exists():
        st = json.loads(ck.read_text())
        u, m, v, gen0 = np.array(st['u']), np.array(st['m']), np.array(st['v']), st['gen'] + 1
    else:
        u = np.array(json.loads(Path(a.init).read_text())['u']) if a.init else np.zeros(D)
        m, v, gen0 = np.zeros(D), np.zeros(D), 0
    curve = Curve()
    E.prebuild(E.BOT)
    for o in ZOO:
        E.prebuild(o)

    def say(s):
        print(time.strftime('%H:%M:%S'), s, flush=True)

    for gen in range(gen0, a.gens):
        rng = random.Random(a.seed_base * 7919 + gen)
        nrng = np.random.default_rng(a.seed_base * 104729 + gen)
        eps = nrng.standard_normal((a.pairs, D))
        pols = [('centre', u.copy()), ('parent', np.zeros(D))]
        for k in range(a.pairs):
            pols.append((f'p{k}+', np.clip(u + a.sigma * eps[k], -U_MAX, U_MAX)))
            pols.append((f'p{k}-', np.clip(u - a.sigma * eps[k], -U_MAX, U_MAX)))
        base_fx = fixtures_for(a.stage, gen, a.seed_base, rng, a.maps.split(',') if a.maps else None)
        allfx = []
        for tag, uu in pols:
            prm = decode(uu, d0)
            for f in base_fx:
                allfx.append(dict(f, params=prm, tag=tag))
        t0 = time.time()
        say(f'gen {gen}: {len(pols)} policies x {len(base_fx)} fixtures = {len(allfx)} games')
        rows = E.run(allfx, str(out / 'games.jsonl'), a.jobs, log=say)
        by = {}
        for f, r in zip(allfx, rows):
            by.setdefault(f['tag'], []).append((f, r))
        # pair on fixtures every policy completed (paired batch)
        ok = set(range(len(base_fx)))
        for tag, lst in by.items():
            ok &= {i for i, (_, r) in enumerate(lst) if r is not None}
        beta = a.beta if a.beta is not None else (0.0 if a.stage < 3 else (0.25 if gen < a.gens // 2 else 0.5))
        par = [by['parent'][i][1] for i in sorted(ok)]
        summ = {}
        for tag, lst in by.items():
            rs = [lst[i][1] for i in sorted(ok)]
            summ[tag] = policy_reward(rs, par if tag != 'parent' else None, beta, curve, a.reward)
        if summ['parent'] is None:
            say('no usable fixtures this generation; skipping update'); continue
        # the parent's own penalty is 0 by definition
        R = {t: s['R'] for t, s in summ.items() if s}
        plus = [R.get(f'p{k}+') for k in range(a.pairs)]
        minus = [R.get(f'p{k}-') for k in range(a.pairs)]
        valid = [k for k in range(a.pairs) if plus[k] is not None and minus[k] is not None]
        ranks = centred_ranks([plus[k] for k in valid] + [minus[k] for k in valid])
        rp, rm = ranks[:len(valid)], ranks[len(valid):]
        g = sum((rp[i] - rm[i]) * eps[k] for i, k in enumerate(valid)) / (len(valid) * a.sigma)
        t = gen + 1
        m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g * g
        if a.opt == 'sgd':
            step = a.lr * g
        else:  # Adam ascent
            step = a.lr * (m / (1 - 0.9 ** t)) / (np.sqrt(v / (1 - 0.999 ** t)) + 1e-8)
        u_prev = u.copy()
        u = np.clip(u + step, -U_MAX, U_MAX)
        dt = time.time() - t0
        with open(log_rows, 'a') as fh:
            for tag, uu in pols:
                s = summ.get(tag)
                fh.write(json.dumps(dict(run=a.run, stage=a.stage, gen=gen, seed=a.seed_base + gen, beta=beta, tag=tag,
                                         n_fixtures=len(ok), params=decode(uu, d0), u=[round(float(x), 4) for x in uu],
                                         **(s or {}))) + '\n')
        c, p_ = summ['centre'], summ['parent']
        say(f"gen {gen} done {dt/60:.1f} min on {len(ok)} fixtures: R centre {c['R']:.4f} parent {p_['R']:.4f} "
            f"(d {c['R'] - p_['R']:+.4f}); C {c['C']:.4f} vs {p_['C']:.4f}; P centre {c['P']:.3f}; "
            f"best member {max(R, key=R.get)} {max(R.values()):.4f}; |step| {np.abs(step).max():.3f}")
        moved = sorted(zip(SPACE, u), key=lambda z: -abs(z[1]))[:6]
        say('  largest moves: ' + ', '.join(f'{n}{x:+.2f}' for (n, _), x in moved))
        ck.write_text(json.dumps(dict(run=a.run, stage=a.stage, gen=gen, u=u.tolist(), u_prev=u_prev.tolist(),
                                      m=m.tolist(), v=v.tolist(), params=decode(u, d0), space=SPACE,
                                      sigma=a.sigma, lr=a.lr, opt=a.opt, pairs=a.pairs, seed_base=a.seed_base), indent=1))
        (out / f'ckpt-g{gen:02d}.json').write_text(ck.read_text())
    say('done')


if __name__ == '__main__':
    main()
