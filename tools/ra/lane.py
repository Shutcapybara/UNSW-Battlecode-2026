#!/usr/bin/env python3
"""Renoir lane (R-2 `ra`) runner: panels, CPU probe and the BENCHMARKS gate in three commands.

    PY=/tmp/ra-venv/bin/python   # any python >= 3.11 with unswbc 1.2.2, pandas, pyarrow
    $PY tools/ra/lane.py run   BOT [--panel pool|gen|both] [--seeds 1] [--jobs 4] [--shard k/n]
    $PY tools/ra/lane.py cpu   BOT                      # sandbox (judge pricing) on the dense fixtures
    $PY tools/ra/lane.py score BOT [--parent BOT] [--seeds 1] [--json OUT]

Panels (fixed; the lane may not pick opponents):
  pool = tools.analysis.features.run_panel.ZOO x LIVE_MAPS x both seats            (160 games / seed)
  gen  = GEN_OPPS x GEN_MAPS (maps/new + maps/var/*_tr + maps/pub/*_rec) x seats   (248 games / seed)
Outputs under build/ra/runs/<BOT>/<panel>/ (replays, index.jsonl, features/).

Scoring: the pool is normalised by the field's per-map medians
(docs/analysis/benchmarks/map_reference_medians.json, the BENCHMARKS yardstick). The gen maps have no field
reference, so they are normalised by the lane base's own per-map medians (tools/ra/gen_reference.json, frozen from
renoir-00's seed-1 gen run) -- 1.0 = the base on that map. Gate = BENCHMARKS "How to use it" step 4 on the pool,
plus a non-negative economy and win rate on gen.
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
RUNS = ROOT / 'build/ra/runs'
HOST = os.environ.get('RA_HOST', os.uname().nodename.split('.')[0][:12])
UNSWBC = os.environ.get('UNSWBC', str(Path(sys.executable).parent / 'unswbc'))
ECON = ['pearls@50', 'pearls@100', 'pearls@150', 'pearls@250']
MAT = ['units@100', 'total@100', 'births@100']
HYG = ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k', 'death_invalid_per1k']
DIAG = ['newborn_deaths10_per100', 'top1_share@100', 'total_share@250', 'sprint_cost_per_pearl', 'deaths_per1k',
        'death_h2h_enemy_per1k', 'death_enemy_body_per1k', 'enclosed_death_share', 'portal_death_share']


def fixtures(bot, panel, seeds):
    opps, maps = (ZOO, LIVE_MAPS) if panel == 'pool' else (GEN_OPPS, GEN_MAPS)
    out = []
    for seed in seeds:
        for opp in opps:
            if opp == bot:
                continue
            for m in maps:
                for a, b in ((bot, opp), (opp, bot)):
                    tag = m.replace('/', '+')
                    out.append(dict(panel=panel, map=m, seed=seed, botA=a, botB=b, opp=opp,
                                    seat='A' if a == bot else 'B', game=f's{seed}__{tag}__{a}__{b}'))
    return out


def run_one(fx, root):
    rep = root / 'replays' / (fx['game'] + '.replay')
    if rep.exists():
        return None
    t = time.time()
    try:
        p = subprocess.run([UNSWBC, 'run', '--seed', str(fx['seed']), '--no-logs', '--no-indicator', '--no-draw',
                            '-o', str(rep) + '.tmp', f"maps/{fx['map']}.map", f"bots/{fx['botA']}", f"bots/{fx['botB']}"],
                           capture_output=True, text=True, timeout=1800, cwd=ROOT)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired:
        out, rc = 'timeout', -9
    m = RESULT.search(out)
    row = dict(fx, seconds=round(time.time() - t, 1), rc=rc, host=os.uname().nodename,
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
    prebuild(a.bot)
    panels = ['pool', 'gen'] if a.panel == 'both' else [a.panel]
    t0 = time.time()
    for panel in panels:
        root = RUNS / a.bot / panel
        (root / 'replays').mkdir(parents=True, exist_ok=True)
        fx = fixtures(a.bot, panel, seeds)
        if a.shard:
            k, n = map(int, a.shard.split('/'))
            fx = [f for i, f in enumerate(fx) if i % n == k]
        if a.reverse:
            fx = fx[::-1]
        todo = [f for f in fx if not (root / 'replays' / (f['game'] + '.replay')).exists()
                and f['game'] not in claimed(root)]
        if a.budget:  # chunked host: long games first, and never start one late (it would be killed)
            todo.sort(key=lambda f: f['map'] not in HEAVY)
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
                    live.add(ex.submit(run_one, f, root))
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
    subprocess.run([sys.executable, '-m', 'tools.analysis.features', 'extract', *reps,
                    '--index', str(idx), '--out', str(feat), '--jobs', str(os.cpu_count() or 2)],
                   cwd=ROOT, check=True)
    print(f'[{panel}] extracted {len(reps)} -> {feat.name}')


def load(bot, panel, seeds):
    import pandas as pd
    fs = sorted(glob.glob(str(RUNS / bot / panel / 'features*/features.parquet')))
    if not fs:
        return None
    F = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True).drop_duplicates(['game', 'side'])
    F = F[F['bot'] == bot].copy()
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


def bootstrap(Fc, Fp, n=400, seed=7):
    """paired bootstrap over fixtures: 90% interval of the econ~ and win deltas"""
    import numpy as np
    k = ['seed', 'mapkey', 'opp', 'side']
    cols = [c + '|n' for c in ECON]
    m = Fc[k + cols + ['win']].merge(Fp[k + cols + ['win']], on=k, suffixes=('_c', '_p'))
    if len(m) < 10:
        return {}
    rng = np.random.default_rng(seed)
    C = m[[c + '_c' for c in cols]].to_numpy(float); P = m[[c + '_p' for c in cols]].to_numpy(float)
    wc = m['win_c'].to_numpy(float); wp = m['win_p'].to_numpy(float)
    de, dw = [], []
    for _ in range(n):
        i = rng.integers(0, len(m), len(m))
        de.append(float(np.mean(np.nanmedian(C[i], axis=0) - np.nanmedian(P[i], axis=0))))
        dw.append(float(wc[i].mean() - wp[i].mean()))
    q = lambda a: [round(float(np.percentile(a, 5)), 3), round(float(np.percentile(a, 95)), 3)]
    return {'econ~_delta_90': q(de), 'win_delta_90': q(dw), 'n': int(len(m))}


def gate(sc, sp, gc, gp):
    """BENCHMARKS step 4 on the pool + non-negative gen. Returns (verdict, reasons)."""
    why, ok = [], True
    d_econ = sc['econ|n~'] - sp['econ|n~']
    if d_econ < 0.05:
        ok = False; why.append(f'pool econ~ {d_econ:+.3f} < +0.05 (mean {sc["econ|n"] - sp["econ|n"]:+.3f})')
    for c in ('units@100|n~', 'total@100|n~'):
        if sc[c] < sp[c]:
            ok = False; why.append(f'{c} down {sc[c] - sp[c]:+.3f}')
    hyg_up = []
    for c in HYG:
        if sp.get(c, 0) > 0.05 and sc.get(c, 0) > 1.10 * sp[c]:
            hyg_up.append(f'{c} +{100 * (sc[c] / sp[c] - 1):.0f}%')
    if hyg_up:
        ok = False; why += hyg_up
    if sc['win'] < sp['win']:
        ok = False; why.append(f"pool win {sc['win'] - sp['win']:+.3f}")
    if gc and gp:
        if gc['econ|n'] < gp['econ|n']:
            ok = False; why.append(f"gen econ {gc['econ|n'] - gp['econ|n']:+.3f}")
        if gc['win'] < gp['win']:
            ok = False; why.append(f"gen win {gc['win'] - gp['win']:+.3f}")
    hyg_down = [c for c in HYG if sp.get(c, 0) > 0.05 and sc.get(c, 0) < 0.9 * sp[c]]
    if ok:
        return 'ACCEPT', why
    if hyg_down and abs(d_econ) < 0.05 and not hyg_up and sc['win'] >= sp['win'] - 0.01:
        return 'HOLD', why + ['hygiene down: ' + ', '.join(hyg_down)]
    return 'REJECT', why


def cmd_score(a):
    seeds = [int(s) for s in a.seeds.split(',')]
    res = {'bot': a.bot, 'parent': a.parent, 'seeds': seeds}
    for panel in ('pool', 'gen'):
        Fc = load(a.bot, panel, seeds)
        if Fc is None or not len(Fc):
            continue
        Fc = normalise(Fc, panel)
        res[panel] = {'cand': summary(Fc)}
        if a.parent:
            Fp = load(a.parent, panel, seeds)
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
                res[panel]['boot'] = bootstrap(Fc, Fp)
                # per-map econ delta (diagnostic)
                mc = Fc.groupby('mapkey')['econ|n'].mean(); mp = Fp.groupby('mapkey')['econ|n'].mean()
                res[panel]['map_econ_delta'] = {k: round(float(mc[k] - mp[k]), 3) for k in mc.index if k in mp.index}
    if a.parent and 'pool' in res and 'parent' in res['pool']:
        g = res.get('gen', {})
        v, why = gate(res['pool']['cand'], res['pool']['parent'], g.get('cand'), g.get('parent'))
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
                print('  bootstrap 90%: ' + json.dumps(res[panel]['boot']))
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
    (ROOT / 'tools/ra/gen_reference.json').write_text(json.dumps(dict(sorted(ref.items())), indent=1))
    print(f'wrote gen_reference.json from {a.bot}: {len(ref)} maps')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.add_argument('bot'); r.add_argument('--panel', default='both')
    r.add_argument('--seeds', default='1'); r.add_argument('--jobs', type=int, default=4); r.add_argument('--shard')
    r.add_argument('--extract', action='store_true'); r.add_argument('--budget', type=float, default=0)
    r.add_argument('--reverse', action='store_true')
    s = sub.add_parser('score'); s.add_argument('bot'); s.add_argument('--parent'); s.add_argument('--seeds', default='1')
    s.add_argument('--json')
    c = sub.add_parser('cpu'); c.add_argument('bot'); c.add_argument('--opp', default='ares-v06-expanded-search-support')
    c.add_argument('--extra'); c.add_argument('--wall', type=float, default=30.0)
    e = sub.add_parser('extract'); e.add_argument('bot'); e.add_argument('--panel', default='both')
    e.add_argument('--limit', type=int, default=0)
    g = sub.add_parser('genref'); g.add_argument('bot')
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


if __name__ == '__main__':
    main()
