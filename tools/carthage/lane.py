#!/usr/bin/env python3
"""Carthage lane (P2-T tester) runner, copied from tools/verso/lane.py (gate and scoring unchanged). Verso lane (X-1) runner: panels, data games, CPU probe and the D-032 gate. Forked from tools/maelle/lane.py
(Maelle, itself from Renoir's tools/ra/lane.py); the gate code is unchanged.

An *arm* is a bot directory plus a VERSO_PARAMS string and a head blob (VERSO_POLICY), local games only:

    PY=.venv/bin/python
    $PY tools/verso/lane.py arm NAME BOT [--params "lam_dir=1"] [--policy build/carthage/models/x.bin] [--alias BOT2]
    $PY tools/verso/lane.py run   ARM [--panel pool|gen|both|train] [--seeds 1,2,3] [--jobs 12] [--dump] [--extract]
    $PY tools/carthage/lane.py score ARM --parent ARM [--seeds 1,2,3] [--phase all|late]
        [--gate d032|learned125] [--json OUT]
    $PY tools/verso/lane.py import ARM RUN_DIR      # adopt another lane's finished runs of the same behaviour
    $PY tools/verso/lane.py cpu   BOT

A bare bot directory name is an arm with no params. Panels (fixed): pool = run_panel.ZOO x LIVE_MAPS x both seats
(160 games / seed); gen = GEN_OPPS x maps/new + maps/var/*_tr + maps/pub/*_rec x both seats (248 games / seed).
train = data games only, never scored: TRAIN_MAPS (in neither panel) + LIVE_MAPS, vs ZOO and a mirror game, at
seeds >= 101 (the D-032 panels use seeds 1-3; the generalisation maps never enter a training set).
synth = data games on the seeded random maps of tools/verso/mapgen.py (build/carthage/maps/vt_*.map): three zoo
opponents per map, both seats, plus a mirror game.
Outputs under build/carthage/runs/<ARM>/<panel>/; dumps under build/carthage/dumps/<ARM>/<panel>/<game>.bin.
Games run at nice VERSO_NICE (default 19): the host is shared and another lane has priority.

Gate (D-032, accept into the lane's stack), on paired fixtures (seed, map, opponent, seat), bootstrap 90 %:
  pool: lower bound of d(econ~) > 0; units@100 and length@100 lower bounds >= -0.02; win lower bound > -0.02;
        no tier-2 rate up > 10 %;
  gen:  lower bound of d(econ) > -0.02;
  per-checkpoint deltas always reported; --phase late judges econ on p@150/p@250 with p@50/p@100 as guards.
econ~ = mean over k in 50/100/150/250 of the median side-game pearls@k / field per-map median (BENCHMARKS form,
as Renoir); gen maps are normalised by renoir-00's frozen per-map medians (tools/ra/gen_reference.json).

For a prospective learned-policy/search arm evaluated under unswbc 1.2.5, use
`score ... --gate learned125 --seeds 1,2,3,4,5`. This is an opt-in local gate;
the default D-032 lane gate is unchanged.
"""
from __future__ import annotations

import argparse, glob, json, math, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features.run_panel import ZOO, LIVE_MAPS  # noqa: E402

GEN_OPPS = ['yuna-v05-core', 'chaewon-y04-probe', 'fenrir-v18-arrival-ready-beds', 'ares-v06-expanded-search-support']
GEN_MAPS = sorted(str(Path(p).relative_to(ROOT / 'maps'))[:-4] for p in
                  glob.glob(str(ROOT / 'maps/new/*.map')) + glob.glob(str(ROOT / 'maps/var/*_tr.map')) +
                  glob.glob(str(ROOT / 'maps/pub/*_rec.map')))
HEAVY = {'slithery_fight', 'schooltime', 'portals', 'pub/slithery_rec', 'pub/portals_rec', 'var/portals_tr'}
CPU_MAPS = ['schooltime', 'portals', 'trauma', 'big_empty']
RESULT = re.compile(r'team (A|B) wins after (\d+) rounds \(([^)]*)\)')
TRAIN_MAPS = ['arena', 'big_empty', 'Colosseum', 'default_small', 'stronghold']  # dilemma_10.map does not load
RUNS = ROOT / 'build/carthage/runs'
DUMPS = ROOT / 'build/carthage/dumps'
ARMS = ROOT / 'build/carthage/arms.json'
NICE = int(os.environ.get('CARTHAGE_NICE', '10'))
HOST = os.environ.get('VERSO_HOST', os.uname().nodename.split('.')[0][:12])
UNSWBC = os.environ.get('UNSWBC', str(Path(sys.executable).parent / 'unswbc'))
ECON = ['pearls@50', 'pearls@100', 'pearls@150', 'pearls@250']
MAT = ['units@100', 'total@100', 'births@100']
HYG = ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k', 'death_invalid_per1k']
DIAG = ['newborn_deaths10_per100', 'top1_share@100', 'total_share@250', 'sprint_cost_per_pearl', 'deaths_per1k',
        'death_h2h_enemy_per1k', 'death_enemy_body_per1k', 'enclosed_death_share', 'portal_death_share']


def arms():
    return json.load(open(ARMS)) if ARMS.exists() else {}


def arm_full(arm):
    a = arms().get(arm)
    if a:
        return dict(bot=a['bot'], params=a.get('params', ''), policy=a.get('policy', ''), alias=a.get('alias', []))
    if (ROOT / 'bots' / arm).is_dir():
        return dict(bot=arm, params='', policy='', alias=[])
    raise SystemExit(f'unknown arm {arm}')


def arm_spec(arm):
    """-> (bot dir name, VERSO_PARAMS string)"""
    a = arm_full(arm)
    return a['bot'], a['params']


def cmd_arm(a):
    A = arms()
    spec = dict(bot=a.bot, params=a.params or '', policy=a.policy or '', alias=a.alias or [])
    if a.name in A and {k: A[a.name].get(k) or type(v)() for k, v in spec.items()} != spec:
        raise SystemExit(f'arm {a.name} exists with different spec: {A[a.name]}')
    if spec['policy'] and not (ROOT / spec['policy']).is_file():
        raise SystemExit(f"no head blob at {spec['policy']}")
    A[a.name] = spec
    ARMS.parent.mkdir(parents=True, exist_ok=True)
    ARMS.write_text(json.dumps(A, indent=1, sort_keys=True))
    print(a.name, A[a.name])


def cmd_import(a):
    """Adopt finished runs of a behaviour-identical bot from another lane's tree (features only, by symlink)."""
    spec = arm_full(a.bot)
    n = 0
    for panel in ('pool', 'gen'):
        for f in sorted(glob.glob(str(Path(a.src) / panel / 'features*'))):
            dst = RUNS / a.bot / panel / ('features-import-' + Path(f).name.split('-')[-1])
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                dst.symlink_to(Path(f).resolve()); n += 1
    print(f'imported {n} feature sets into arm {a.bot} (bot names accepted: {[spec["bot"]] + spec["alias"]})')


def fixtures(bot, panel, seeds):
    data = panel in ('train', 'synth')
    if data and min(seeds) < 101:
        raise SystemExit('data games use seeds >= 101 (the panels own the low seeds)')
    if not data and max(seeds) >= 101:
        raise SystemExit('seeds >= 101 are reserved for data games')
    synth = sorted(p.stem for p in (ROOT / 'build/carthage/maps').glob('vt_*.map'))
    opps, maps = {'pool': (ZOO, LIVE_MAPS), 'gen': (GEN_OPPS, GEN_MAPS),
                  'train': (ZOO + [bot], TRAIN_MAPS + LIVE_MAPS), 'synth': (ZOO + [bot], synth)}[panel]
    out = []
    for seed in seeds:
        for oi, opp in enumerate(opps):
            if opp == bot and not data:
                continue
            for mi, m in enumerate(maps):
                # synthetic maps: three zoo opponents per map (rotating with the map and the seed) plus the mirror
                if panel == 'synth' and opp != bot and (oi - mi - seed) % len(ZOO) >= 3:
                    continue
                for a, b in (((bot, opp),) if opp == bot else ((bot, opp), (opp, bot))):
                    tag = m.replace('/', '+')
                    out.append(dict(panel=panel, map=m, seed=seed, botA=a, botB=b, opp=opp,
                                    seat='A' if a == bot else 'B', game=f's{seed}__{tag}__{a}__{b}'))
    return out


def installed_runtime_version():
    p = subprocess.run([UNSWBC, '--version'], capture_output=True, text=True, cwd=ROOT, check=True)
    match = re.search(r'unswbc\s+(\d+\.\d+\.\d+)', p.stdout + p.stderr)
    if not match:
        raise SystemExit('could not read the installed unswbc version from --version')
    return match.group(1)


def run_one(fx, root, spec, dump=None, runtime_version=None):
    rep = root / 'replays' / (fx['game'] + '.replay')
    if rep.exists():
        return None
    t = time.time()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('VERSO_', 'MAELLE_'))}
    data = fx['panel'] in ('train', 'synth')
    if spec['params'] or data:
        env['VERSO_PARAMS'] = ','.join(x for x in (spec['params'], f"seed={fx['seed']}" if data else '') if x)
    mp = f"build/carthage/maps/{fx['map']}.map" if fx['panel'] == 'synth' else f"maps/{fx['map']}.map"
    if spec['policy']:
        env['VERSO_POLICY'] = str((ROOT / spec['policy']).resolve())
    if dump is not None:
        dump.mkdir(parents=True, exist_ok=True)
        df = dump / (fx['game'] + '.bin')
        if df.exists():
            df.unlink()  # a killed game's partial dump
        env['VERSO_DUMP'] = str(df)
    try:
        p = subprocess.run((['nice', '-n', str(NICE)] if NICE else []) + [UNSWBC, 'run', '--seed', str(fx['seed']), '--no-logs', '--no-indicator', '--no-draw',
                            '-o', str(rep) + '.tmp', mp, f"bots/{fx['botA']}", f"bots/{fx['botB']}"],
                           capture_output=True, text=True, timeout=1800, cwd=ROOT, env=env)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired:
        out, rc = 'timeout', -9
    m = RESULT.search(out)
    row = dict(fx, seconds=round(time.time() - t, 1), rc=rc, host=os.uname().nodename,
               runtime_version=runtime_version,
               winner=m.group(1) if m else ('draw' if 'draw' in out.lower() else None),
               rounds=int(m.group(2)) if m else None, reason=m.group(3) if m else out.strip()[-200:])
    if os.path.exists(str(rep) + '.tmp'):
        os.replace(str(rep) + '.tmp', rep)
    row['replay'] = str(rep.relative_to(root))
    return row


def prebuild(bot):
    """compile once before parallel games (concurrent first builds race on .unswbc-build)"""
    try:
        from unswbc.project import Project
        Project.from_dir(str(ROOT / 'bots' / bot)).compile()
    except Exception as e:  # the game itself will report a real build error
        print('prebuild:', type(e).__name__, str(e)[:200], flush=True)


def cmd_run(a):
    seeds = [int(s) for s in a.seeds.split(',')]
    spec = arm_full(a.bot)
    bot, params = spec['bot'], spec['params']
    runtime_version = installed_runtime_version()
    prebuild(bot)
    for o in set(ZOO) | set(GEN_OPPS):  # opponents too: concurrent first builds race on .unswbc-build
        prebuild(o)
    panels = ['pool', 'gen'] if a.panel == 'both' else [a.panel]
    t0 = time.time()
    for panel in panels:
        root = RUNS / a.bot / panel
        (root / 'replays').mkdir(parents=True, exist_ok=True)
        (root / 'arm.json').write_text(json.dumps(dict(arm=a.bot, **spec)))
        dump = DUMPS / a.bot / panel if a.dump else None
        fx = fixtures(bot, panel, seeds)
        if a.shard:
            k, n = map(int, a.shard.split('/'))
            fx = [f for i, f in enumerate(fx) if i % n == k]
        if a.reverse:
            fx = fx[::-1]
        todo = [f for f in fx if not (root / 'replays' / (f['game'] + '.replay')).exists()
                and f['game'] not in claimed(root)]
        if a.budget:  # chunked host: long games first, and never start one late (it would be killed)
            todo.sort(key=lambda f: f['map'] not in HEAVY)
        else:  # heavy maps first so the tail is short
            todo.sort(key=lambda f: (f['map'] not in HEAVY, f['seed']))
        print(f'[{panel}] {len(fx)} fixtures, {len(todo)} to run', flush=True)
        done = 0
        with open(root / f'index-{HOST}.jsonl', 'a') as idx, ThreadPoolExecutor(a.jobs) as ex:
            it = iter(todo); live = set()
            def fill():
                while len(live) < a.jobs and (not a.budget or time.time() - t0 < a.budget):
                    f = next(it, None)
                    if f is None:
                        return
                    if f['game'] in claimed(root):
                        continue
                    if a.budget and f['map'] in HEAVY and time.time() - t0 > max(5.0, a.budget - 90):
                        continue
                    live.add(ex.submit(run_one, f, root, spec, dump, runtime_version))
            fill()
            while live:
                fin = next(as_completed(live)); live.discard(fin)
                row = fin.result(); done += 1
                if row:
                    idx.write(json.dumps(row) + '\n'); idx.flush()
                    if done % 20 == 0 or row['rc'] != 0:
                        print(f"[{panel}] {done}/{len(todo)} {time.time() - t0:.0f}s rc={row['rc']} {row['game']}", flush=True)
                fill()
        left = len([f for f in fx if not (root / 'replays' / (f['game'] + '.replay')).exists()])
        print(f'[{panel}] ran {done}, {left} left in this shard on this host', flush=True)
        if a.budget and time.time() - t0 >= a.budget:
            break
    if a.extract:
        for panel in panels:
            if panel not in ('train', 'synth'):
                extract(a.bot, panel)


def claimed(root):
    """games another host has already finished (its index was copied in as index-<host>.jsonl)"""
    out = set()
    for f in glob.glob(str(root / 'index*.jsonl')):
        for line in open(f):
            try:
                r = json.loads(line)
                if r.get('rc') == 0:
                    out.add(r['game'])
            except Exception:
                pass
    return out


def extracted(root):
    import pandas as pd
    got = set()
    for f in glob.glob(str(root / 'features*/features.parquet')):
        got |= set(pd.read_parquet(f, columns=['game'])['game'])
    return got


def extract(bot, panel, limit=0):
    root = RUNS / bot / panel
    have = extracted(root)
    reps = [p for p in sorted(glob.glob(str(root / 'replays/*.replay'))) if Path(p).stem not in have]
    if not reps:
        print(f'[{panel}] nothing new to extract'); return
    if limit:
        reps = reps[:limit]
    feat = root / f'features-{HOST}-{int(time.time())}'
    idx = root / 'index-all.tmp.jsonl'
    with open(idx, 'w') as o:
        for f in glob.glob(str(root / 'index-*.jsonl')):
            if not f.endswith('.tmp.jsonl'):
                o.write(open(f).read())
    subprocess.run(['nice', '-n', str(NICE), sys.executable, '-m', 'tools.analysis.features', 'extract', *reps,
                    '--index', str(idx), '--out', str(feat), '--jobs', str(int(os.environ.get('CARTHAGE_XJOBS', '8')))],
                   cwd=ROOT, check=True)
    print(f'[{panel}] extracted {len(reps)} -> {feat.name}')


def load(bot, panel, seeds):
    import pandas as pd
    fs = sorted(glob.glob(str(RUNS / bot / panel / 'features*/features.parquet')))
    if not fs:
        return None
    F = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True).drop_duplicates(['game', 'side'])
    spec = arm_full(bot)
    F = F[F['bot'].isin([spec['bot']] + spec['alias'])].copy()
    parts = F['game'].str.split('__', expand=True)
    F['seed'] = parts[0].str[1:].astype(int)
    F['mapkey'] = parts[1]
    F['opp'] = F['opponent']
    F = F[F['seed'].isin(seeds)]
    F['win'] = F['result'].map({'win': 1.0, 'draw': 0.5, 'loss': 0.0})
    return F


def normalise(F, panel):
    import numpy as np
    if panel == 'pool':
        ref = json.load(open(ROOT / 'docs/analysis/benchmarks/map_reference_medians.json'))
        for c in ECON + MAT:
            F[c + '|n'] = F[c] / F['map'].map(ref[c]).replace(0, np.nan)
    else:
        gp = ROOT / 'tools/ra/gen_reference.json'
        ref = json.load(open(gp)) if gp.exists() else None
        for c in ECON + MAT:
            if ref is None:
                F[c + '|n'] = np.nan
            else:
                F[c + '|n'] = F[c] / F['mapkey'].map(lambda k: max(1.0, ref.get(k, {}).get(c, np.nan)))
    F['econ|n'] = F[[c + '|n' for c in ECON]].mean(axis=1)
    return F


def summary(F):
    s = {'n': int(len(F)), 'win': float(F['win'].mean())}
    for c in ECON + MAT:
        s[c + '|n'] = float(F[c + '|n'].mean())
    s['econ|n'] = float(sum(s[c + '|n'] for c in ECON) / 4)
    for c in ECON + MAT:  # BENCHMARKS convention: medians per side-game
        s[c + '|n~'] = float(F[c + '|n'].median())
    s['econ|n~'] = float(sum(s[c + '|n~'] for c in ECON) / 4)
    for c in ECON + MAT + HYG + DIAG:
        if c in F:
            s[c] = float(F[c].mean())
    return s


def paired(Fc, Fp, key):
    k = ['seed', 'mapkey', 'opp', 'side']
    m = Fc[k + [key]].merge(Fp[k + [key]], on=k, suffixes=('_c', '_p'))
    b = int((m[key + '_c'] > m[key + '_p']).sum()); w = int((m[key + '_c'] < m[key + '_p']).sum())
    n = b + w
    p = 1.0
    if n:  # two-sided sign test
        x = min(b, w)
        p = min(1.0, 2 * sum(math.comb(n, i) for i in range(x + 1)) / 2 ** n)
    return dict(better=b, same=int(len(m) - n), worse=w, p=round(p, 4))


def bootstrap(Fc, Fp, n=1000, seed=7, phase='all'):
    """Paired bootstrap over common fixtures (seed, map, opponent, seat): 90 % intervals (5th, 95th percentile)
    of the delta in econ~ (median per checkpoint, mean of the checkpoints judged), each checkpoint's median, the
    per-game-mean economy, units@100 and length(total)@100 medians, and the win rate."""
    import numpy as np
    k = ['seed', 'mapkey', 'opp', 'side']
    cols = [c + '|n' for c in ECON + MAT]
    m = Fc[k + cols + ['win']].merge(Fp[k + cols + ['win']], on=k, suffixes=('_c', '_p'))
    if len(m) < 10:
        return {}
    rng = np.random.default_rng(seed)
    C = m[[c + '_c' for c in cols]].to_numpy(float); P = m[[c + '_p' for c in cols]].to_numpy(float)
    wc = m['win_c'].to_numpy(float); wp = m['win_p'].to_numpy(float)
    judged = [0, 1, 2, 3] if phase == 'all' else [2, 3]
    def stat(ix):
        med = np.nanmedian(C[ix], axis=0) - np.nanmedian(P[ix], axis=0)
        mean = np.nanmean(C[ix][:, :4], axis=0) - np.nanmean(P[ix][:, :4], axis=0)
        return np.concatenate([[med[judged].mean(), mean[judged].mean()], med[:4], med[4:6],
                               [wc[ix].mean() - wp[ix].mean()]])
    names = ['econ~', 'econ_mean', 'p50', 'p100', 'p150', 'p250', 'units100', 'total100', 'win']
    point = stat(np.arange(len(m)))
    B = np.array([stat(rng.integers(0, len(m), len(m))) for _ in range(n)])
    lo, hi = np.percentile(B, 5, axis=0), np.percentile(B, 95, axis=0)
    return {'n': int(len(m)), 'phase': phase,
            **{nm: [round(float(point[i]), 4), round(float(lo[i]), 4), round(float(hi[i]), 4)] for i, nm in enumerate(names)}}


def gate(sc, sp, boot, gboot):
    """D-032 accept gate. -> (verdict, reasons). boot/gboot: bootstrap() dicts for pool/gen."""
    why, ok = [], True
    if not boot:
        return 'INCOMPLETE', ['no paired pool fixtures']
    lb = lambda d, k: d[k][1]
    if lb(boot, 'econ~') <= 0:
        ok = False; why.append(f"pool d econ~ {boot['econ~'][0]:+.3f} lb {lb(boot, 'econ~'):+.3f} <= 0")
    if boot.get('phase') == 'late':
        for c in ('p50', 'p100'):
            if lb(boot, c) < -0.02:
                ok = False; why.append(f"early guard {c} lb {lb(boot, c):+.3f} < -0.02")
    for c in ('units100', 'total100'):
        if lb(boot, c) < -0.02:
            ok = False; why.append(f"{c} lb {lb(boot, c):+.3f} < -0.02")
    if lb(boot, 'win') <= -0.02:
        ok = False; why.append(f"pool win lb {lb(boot, 'win'):+.3f} <= -0.02")
    hyg_up, hyg_down = [], []
    for c in HYG:
        if sp.get(c, 0) > 0.05 and sc.get(c, 0) > 1.10 * sp[c]:
            hyg_up.append(f'{c} +{100 * (sc[c] / sp[c] - 1):.0f}%')
        if sp.get(c, 0) > 0.05 and sc.get(c, 0) < 0.90 * sp[c]:
            hyg_down.append(c)
    if hyg_up:
        ok = False; why += hyg_up
    if not gboot:
        ok = False; why.append('gen panel missing')
    elif lb(gboot, 'econ~') <= -0.02:
        ok = False; why.append(f"gen d econ~ {gboot['econ~'][0]:+.3f} lb {lb(gboot, 'econ~'):+.3f} <= -0.02")
    if ok:
        return 'ACCEPT', why
    guards_ok = not hyg_up and all(lb(boot, c) >= -0.02 for c in ('units100', 'total100')) and lb(boot, 'win') > -0.02
    if hyg_down and guards_ok and boot['econ~'][0] > -0.01:
        return 'HOLD', why + ['hygiene down: ' + ', '.join(hyg_down)]
    return 'REJECT', why


def gate_learned125(pool_c, pool_p, pool_b, gen_c, gen_p, gen_b):
    """D-045 local acceptance gate for learned/search arms evaluated under 1.2.5."""
    if not pool_b or not gen_b or not pool_c or not pool_p or not gen_c or not gen_p:
        return 'INCOMPLETE', ['both complete paired panels and declared parent are required']
    incomplete = []
    for panel, boot in (('pool', pool_b), ('gen', gen_b)):
        for metric in ('win', 'econ~', 'units100', 'total100'):
            values = boot.get(metric)
            if not isinstance(values, list) or len(values) < 2 or not math.isfinite(values[1]):
                incomplete.append(f'{panel} {metric} lower bound is missing or non-finite')
    if incomplete:
        return 'INCOMPLETE', incomplete
    reasons = []
    for panel, boot, win_floor in (('pool', pool_b, 0.0), ('gen', gen_b, -0.02)):
        if boot['win'][1] <= win_floor:
            reasons.append(f'{panel} win lower bound {boot["win"][1]:+.3f} <= {win_floor:+.3f}')
    for panel, boot in (('pool', pool_b), ('gen', gen_b)):
        if boot['econ~'][1] <= -0.03:
            reasons.append(f'{panel} econ~ lower bound {boot["econ~"][1]:+.3f} <= -0.030')
        for metric in ('units100', 'total100'):
            if boot[metric][1] < -0.02:
                reasons.append(f'{panel} {metric} lower bound {boot[metric][1]:+.3f} < -0.020')
        cand, parent = (pool_c, pool_p) if panel == 'pool' else (gen_c, gen_p)
        for metric in HYG:
            if metric not in cand or metric not in parent:
                incomplete.append(f'{panel} missing tier-2 metric {metric}')
                continue
            c, p = cand[metric], parent[metric]
            if p > 0.05 and c > 1.10 * p:
                reasons.append(f'{panel} {metric} {p:.2f}->{c:.2f}/1k (>10%)')
            elif metric == 'death_invalid_per1k' and p <= 0.05 and c > 0:
                reasons.append(f'{panel} new invalid deaths {p:.2f}->{c:.2f}/1k')
    if incomplete:
        return 'INCOMPLETE', incomplete
    return ('REJECT', reasons) if reasons else ('ACCEPT', ['all D-045 local learned-arm checks pass'])


def require_full_learned_coverage(arm, panel, seeds, F):
    """Learned-arm scores are final only on the complete, fixed five-seed panels."""
    if F is None or not len(F):
        raise SystemExit(f'--gate learned125: no {panel} features for {arm}')
    bot = arm_full(arm)['bot']
    expected = {fx['game'] for fx in fixtures(bot, panel, seeds)}
    actual = set(F['game'].astype(str))
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise SystemExit(f'--gate learned125: incomplete {panel} coverage for {arm}: '
                         f'{len(missing)} missing, {len(extra)} unexpected; '
                         f'first missing={missing[:3]}')
    logged = set()
    for path in (RUNS / arm / panel).glob('index*.jsonl'):
        for line in path.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            reason = str(row.get('reason', '')).lower()
            if (row.get('game') in expected and row.get('runtime_version') == '1.2.5'
                    and row.get('rc') == 0 and row.get('winner') in ('A', 'B', 'draw')
                    and not any(marker in reason for marker in ('timeout', 'timed out', 'tle'))):
                logged.add(row['game'])
    unverified = sorted(expected - logged)
    if unverified:
        raise SystemExit(f'--gate learned125: {len(unverified)} {panel} fixtures for {arm} lack a '
                         f'successful unswbc 1.2.5 run record; first={unverified[:3]}')


def cmd_score(a):
    seeds = [int(s) for s in a.seeds.split(',')]
    if a.gate == 'learned125':
        from tools.analysis.features.frame import FRAME_VERSION
        if FRAME_VERSION != 7:
            raise SystemExit(f'--gate learned125 requires FRAME_VERSION 7, found {FRAME_VERSION}')
        if seeds != [1, 2, 3, 4, 5]:
            raise SystemExit('--gate learned125 requires exactly --seeds 1,2,3,4,5')
        if a.phase != 'all':
            raise SystemExit('--gate learned125 scores the full game; omit --phase late')
        if not a.parent:
            raise SystemExit('--gate learned125 requires --parent')
    res = {'bot': a.bot, 'parent': a.parent, 'seeds': seeds, 'gate_method': a.gate}
    for panel in ('pool', 'gen'):
        Fc = load(a.bot, panel, seeds)
        if a.gate == 'learned125':
            require_full_learned_coverage(a.bot, panel, seeds, Fc)
        if Fc is None or not len(Fc):
            continue
        Fc = normalise(Fc, panel)
        res[panel] = {'cand': summary(Fc)}
        if a.parent:
            Fp = load(a.parent, panel, seeds)
            if a.gate == 'learned125':
                require_full_learned_coverage(a.parent, panel, seeds, Fp)
            if Fp is not None and len(Fp):
                # compare on the common fixtures only (a partial run is scored against the same games)
                k = ['seed', 'mapkey', 'opp', 'side']
                common = Fc[k].merge(Fp[k], on=k)
                if len(common) < max(len(Fc), len(Fp)):
                    Fc = Fc.merge(common, on=k); Fp = Fp.merge(common, on=k)
                    res[panel]['cand'] = summary(Fc)
                    res[panel]['common_only'] = int(len(common))
                Fp = normalise(Fp, panel)
                res[panel]['parent'] = summary(Fp)
                res[panel]['pairs'] = {k: paired(Fc, Fp, k) for k in ('pearls@100', 'total@100', 'units@100', 'win')}
                res[panel]['boot'] = bootstrap(Fc, Fp, phase=a.phase)
                # per-map econ delta (diagnostic)
                mc = Fc.groupby('mapkey')['econ|n'].mean(); mp = Fp.groupby('mapkey')['econ|n'].mean()
                res[panel]['map_econ_delta'] = {k: round(float(mc[k] - mp[k]), 3) for k in mc.index if k in mp.index}
    if a.gate == 'learned125':
        if 'pool' not in res or 'gen' not in res or 'parent' not in res['pool'] or 'parent' not in res['gen']:
            res['verdict'], res['why'] = 'INCOMPLETE', ['both complete paired panels and declared parent are required']
        else:
            v, why = gate_learned125(res['pool']['cand'], res['pool']['parent'], res['pool'].get('boot'),
                                     res['gen']['cand'], res['gen']['parent'], res['gen'].get('boot'))
            res['verdict'], res['why'] = v, why
    elif a.parent and 'pool' in res and 'parent' in res['pool']:
        g = res.get('gen', {})
        v, why = gate(res['pool']['cand'], res['pool']['parent'], res['pool'].get('boot'), g.get('boot'))
        res['verdict'], res['why'] = v, why
    txt = json.dumps(res, indent=1)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True); Path(a.json).write_text(txt)
    show(res)


def show(res):
    def row(label, s):
        if not s:
            return
        print(f"  {label:7s} n={s['n']:3d} win={s['win']:.3f} econ~={s['econ|n~']:.3f} [" + ' '.join(f"{s[c + '|n~']:.2f}" for c in ECON + MAT) + f"] econ={s['econ|n']:.3f} "
              + ' '.join(f"{c.split('@')[0][0]}{c.split('@')[1][:-2]}={s[c]:.3f}" for c in [x + '|n' for x in ECON + MAT])
              + ' | ' + ' '.join(f"{c.replace('death_', '').replace('_per1k', '')}={s[c]:.2f}" for c in HYG)
              + f" nb10={s.get('newborn_deaths10_per100', float('nan')):.1f}")
    print(f"== {res['bot']} vs parent {res['parent']} seeds {res['seeds']}")
    for panel in ('pool', 'gen'):
        if panel not in res:
            continue
        print(f'[{panel}]')
        row('cand', res[panel]['cand']); row('parent', res[panel].get('parent'))
        if 'pairs' in res[panel]:
            print('  pairs ' + ' '.join(f"{k}:{v['better']}/{v['same']}/{v['worse']} p={v['p']}" for k, v in res[panel]['pairs'].items()))
            if res[panel].get('boot'):
                b = res[panel]['boot']
                print(f"  paired n={b['n']} (point [5%, 95%]): " + '  '.join(
                    f"{k} {v[0]:+.3f} [{v[1]:+.3f},{v[2]:+.3f}]" for k, v in b.items() if isinstance(v, list)))
            print('  map econ delta ' + ' '.join(f'{k}:{v:+.3f}' for k, v in sorted(res[panel]['map_econ_delta'].items())))
    if 'verdict' in res:
        print('VERDICT', res['verdict'], '; '.join(res['why']))


def cmd_cpu(a):
    out = RUNS / a.bot / 'cpu'
    out.mkdir(parents=True, exist_ok=True)
    maps = CPU_MAPS + (a.extra.split(',') if a.extra else [])
    rows = []
    for m in maps:
        j = out / f"{m.replace('/', '+')}.json"
        if not j.exists():
            subprocess.run([sys.executable, 'tools/cx/arena.py', f'maps/{m}.map', f'bots/{a.bot}', f'bots/{a.opp}',
                            '--sandbox', '--json', str(j)], cwd=ROOT, check=True, capture_output=True)
        r = json.load(open(j))
        for t in 'AB':
            pts = r['stats'][t].get('points', {})
            rows.append((m, t, pts.get('p50', 0), pts.get('p99', 0), pts.get('max', 0), len(r.get('errors', []))))
    mx = max(x[4] for x in rows)
    for x in rows:
        print(f'{x[0]:28s} {x[1]} p50={x[2] / 1e6:5.2f}M p99={x[3] / 1e6:5.2f}M max={x[4] / 1e6:5.2f}M errors={x[5]}')
    print(f'CPU max {mx / 1e6:.2f}M  ({"OK" if mx <= a.wall * 1e6 else "OVER WALL"} vs {a.wall}M)')
    (out / 'summary.json').write_text(json.dumps(dict(max=mx, rows=rows)))


def cmd_genref(a):
    """Freeze the base's per-map medians on gen (run once, from renoir-00)."""
    F = load(a.bot, 'gen', [1])
    ref = {k: {c: float(g[c].median()) for c in ECON + MAT} for k, g in F.groupby('mapkey')}
    (ROOT / 'build/carthage/gen_reference.json').write_text(json.dumps(dict(sorted(ref.items())), indent=1))
    print(f'wrote gen_reference.json from {a.bot}: {len(ref)} maps')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('bot'); r.add_argument('--panel', default='both', choices=['pool', 'gen', 'both', 'train', 'synth'])
    r.add_argument('--seeds', default='1,2,3'); r.add_argument('--jobs', type=int, default=12); r.add_argument('--shard')
    r.add_argument('--dump', action='store_true')
    r.add_argument('--extract', action='store_true'); r.add_argument('--budget', type=float, default=0)
    r.add_argument('--reverse', action='store_true')
    s = sub.add_parser('score'); s.add_argument('bot'); s.add_argument('--parent'); s.add_argument('--seeds', default='1,2,3')
    s.add_argument('--phase', default='all', choices=['all', 'late'])
    s.add_argument('--gate', default='d032', choices=['d032', 'learned125'],
                   help='d032 (default) or the prospective unswbc 1.2.5 learned-arm gate')
    s.add_argument('--json')
    c = sub.add_parser('cpu'); c.add_argument('bot'); c.add_argument('--opp', default='ares-v06-expanded-search-support')
    c.add_argument('--extra'); c.add_argument('--wall', type=float, default=30.0)
    e = sub.add_parser('extract'); e.add_argument('bot'); e.add_argument('--panel', default='both')
    e.add_argument('--limit', type=int, default=0)
    g = sub.add_parser('genref'); g.add_argument('bot')
    ar = sub.add_parser('arm'); ar.add_argument('name'); ar.add_argument('bot'); ar.add_argument('--params', default='')
    ar.add_argument('--policy', default=''); ar.add_argument('--alias', action='append')
    im = sub.add_parser('import'); im.add_argument('bot'); im.add_argument('src')
    a = ap.parse_args()
    if a.cmd == 'run':
        cmd_run(a)
    elif a.cmd == 'score':
        cmd_score(a)
    elif a.cmd == 'cpu':
        cmd_cpu(a)
    elif a.cmd == 'extract':
        for p in (['pool', 'gen'] if a.panel == 'both' else [a.panel]):
            extract(a.bot, p, a.limit)
    elif a.cmd == 'genref':
        cmd_genref(a)
    elif a.cmd == 'arm':
        cmd_arm(a)
    elif a.cmd == 'import':
        cmd_import(a)


if __name__ == '__main__':
    main()
