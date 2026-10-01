"""Tempo gate: is the candidate faster than its parent in the opening? One command, one verdict.

  python3 tools/s1/tempo_gate.py CAND PARENT [--jobs N] [--maps pool|gen|all]

CAND and PARENT are replay folders from the same panel: a scorecard/run_panel dir (with replays/ inside), a replays/ dir,
or a renoir-style run dir. Fixtures are paired on the file name s<seed>__<map>__<A>__<B>.replay with the bot's own name
masked, so the same seed, map, opponent and seat are compared. Nothing else is needed: no corpus store, no DuckDB.
The reference is the frozen top-10 curve set docs/analysis/benchmarks/tempo_reference.json.

Output: a per-map table, the pooled tempo delta with a 95 % bootstrap interval, the guards, and one line:
  VERDICT: ACCEPT | NO GAIN | REJECT | INCONCLUSIVE (with the number of fixtures that would settle it)
    ACCEPT        delta <= -3 rounds, CI upper < 0, and no map significantly slower by more than 5 rounds
    NO GAIN       the CI excludes a 3-round gain (lower bound > -3): keep the parent
    REJECT        the CI lies above 0: the candidate is slower
    INCONCLUSIVE  otherwise: add seeds, do not tune on the same games

Definition (docs/analysis/BENCHMARKS.md, "Tempo"): tempo = mean over t = 10, 20, ..., 150 of the horizontal lag, in rounds,
between the side's net income  N(t) = income(t) - [loss(t) - loss_top10(t)]  and the top-10 median income curve on the same
map. income = bed pearls + enemy-corpse pearls eaten; loss = own length lost minus own corpse pearls eaten back.
Maps without a top-10 curve (maps/new, _tr variants) use the parent's median curves as the reference.
"""
import argparse, hashlib, json, os, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
import numpy as np

REF = ROOT / 'docs' / 'analysis' / 'benchmarks' / 'tempo_reference.json'
CACHE = ROOT / 'build' / 's1' / 'tempo_cache'
T = np.arange(0, 151, 5)
TS = np.arange(10, 151, 10)
IDX = [int(t // 5) for t in TS]
LAG_MIN = -60
DELTA = 3.0         # rounds: smallest gain worth accepting (~ +5 win points at 50 %, ~ 50 Elo)
MAP_GUARD = 5.0     # rounds: no map may be significantly slower by more than this
GUARDS = [('own_goals_per1k', 'own goals /1k dragon-turns', 'down'), ('h2h_ally_per1k', 'ally head-on /1k', 'down'),
          ('transit_died3', 'per-transit death within 3 rounds', 'down'), ('newborn_dead10', 'newborns dead within 10 rounds',
          'down'), ('total150', 'total length at r150', 'up'), ('won', 'win share', 'up')]


# ---------------------------------------------------------------- per-replay extraction (cached)
def extract(path):
    path = Path(path)
    st = path.stat()
    key = hashlib.sha1(f'{path.resolve()}|{st.st_size}|{st.st_mtime_ns}|v1'.encode()).hexdigest()[:16]
    cf = CACHE / f'{path.stem[:80]}.{key}.json'
    if cf.exists():
        return json.loads(cf.read_text())
    from tools.s1.build import process
    r = process((str(path), path.stem, {'source': 'tempo'}))
    if 'error' in r:
        return {'error': r['error'], 'game': path.stem}
    out = {'game': path.stem, 'sides': {}}
    ser = {}
    for row in r['series']:
        if row['round'] % 5 == 0 and row['round'] <= 150:
            ser.setdefault(row['side'], {})[int(row['round'])] = row
    sd = {s['side']: s for s in r['sides']}
    for side, rows in ser.items():
        g = lambda k, rr: float(rows[rr].get(k) or 0.0)
        r150 = rows[150]
        dt = max(g('c_dragon_turns', 150), 1.0)
        s = sd[side]
        out['map'] = s['map']
        out['sides'][side] = dict(
            team=s['team'], won=s['won'],
            income=[g('c_eats_bed', t) + g('c_eats_enemy_corpse', t) for t in T],
            loss=[g('c_length_lost', t) - g('c_eats_ally_corpse', t) for t in T],
            total150=g('total', 150), own_goals_per1k=1000 * g('c_own_goals', 150) / dt,
            h2h_ally_per1k=1000 * g('c_death_h2h_ally', 150) / dt,
            transit_died3=(g('c_transit_died3', 150) / g('c_transits', 150)) if g('c_transits', 150) else None,
            newborn_dead10=(g('c_deaths_newborn', 150) / g('c_splits', 150)) if g('c_splits', 150) else None)
    CACHE.mkdir(parents=True, exist_ok=True)
    cf.write_text(json.dumps(out))
    return out


def load_dir(d, jobs):
    d = Path(d)
    rd = d / 'replays' if (d / 'replays').is_dir() else d
    files = sorted(rd.glob('*.replay'))
    if not files:
        raise SystemExit(f'no .replay files under {d}')
    import multiprocessing as mp
    ctx = mp.get_context('fork' if sys.platform.startswith('linux') else 'spawn')
    t0 = time.time()
    with ctx.Pool(jobs) as pool:
        res = pool.map(extract, files, chunksize=4)
    bad = [r for r in res if 'error' in r]
    print(f'{d}: {len(res) - len(bad)} replays ({len(bad)} unreadable) in {time.time() - t0:.0f}s', file=sys.stderr)
    return [r for r in res if 'error' not in r]


def protagonist(games):
    """the bot present in every game of the folder"""
    from collections import Counter
    c = Counter(s['team'] for g in games for s in g['sides'].values())
    return c.most_common(1)[0][0]


# ---------------------------------------------------------------- tempo
def lag(v, R, t):
    R = np.maximum.accumulate(np.asarray(R, float)) + np.arange(len(R)) * 1e-6
    if v <= R[0]:
        x = float(t)
    elif v >= R[-1]:
        slope = max((R[-1] - R[-7]) / 30.0, 1e-3)
        x = float(t - (T[-1] + (v - R[-1]) / slope))
    else:
        x = float(t - np.interp(v, R, T))
    return float(np.clip(x, LAG_MIN, t))


def tempo(side, ref):
    I, D = np.asarray(side['income'], float), np.asarray(side['loss'], float)
    N = I - (D - np.asarray(ref['loss'], float))
    return float(np.mean([lag(N[i], ref['income'], t) for i, t in zip(IDX, TS)]))


def fixture_key(game, bot):
    parts = game.split('__')
    return '__'.join('@BOT' if p == bot else p for p in parts)


def rows_for(games, bot):
    out = []
    for g in games:
        for side, s in g['sides'].items():
            if s['team'] == bot:
                out.append(dict(key=fixture_key(g['game'], bot), map=g['map'], side=side, **s))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cand')
    ap.add_argument('parent')
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument('--maps', default='all', choices=['all', 'pool', 'gen'])
    ap.add_argument('--boots', type=int, default=4000)
    a = ap.parse_args()
    ref = json.loads(REF.read_text())
    Gc, Gp = load_dir(a.cand, a.jobs), load_dir(a.parent, a.jobs)
    bc, bp = protagonist(Gc), protagonist(Gp)
    C, P = rows_for(Gc, bc), rows_for(Gp, bp)
    maps = sorted({r['map'] for r in C} & {r['map'] for r in P})
    if a.maps != 'all':
        maps = [m for m in maps if (m in ref['maps']) == (a.maps == 'pool')]
    # reference per map: frozen top-10 curves, else the parent's median curves on that map
    refs = {}
    for m in maps:
        if m in ref['maps']:
            refs[m] = dict(ref['maps'][m], kind='top10')
        else:
            pm = [r for r in P if r['map'] == m]
            refs[m] = dict(income=np.median([r['income'] for r in pm], axis=0).tolist(),
                           loss=np.median([r['loss'] for r in pm], axis=0).tolist(), kind='parent')
    for r in C + P:
        if r['map'] in refs:
            r['tempo'] = tempo(r, refs[r['map']])
    pc = {r['key']: r for r in P if r['map'] in refs}
    pairs = [(r, pc[r['key']]) for r in C if r['key'] in pc]
    paired = len(pairs) >= 0.5 * min(len(C), len(P))
    rng = np.random.default_rng(1)
    rows, boot_by_map = [], []
    for m in maps:
        if paired:
            d = np.array([c['tempo'] - p['tempo'] for c, p in pairs if c['map'] == m])
            if len(d) < 3:
                continue
            est = d.mean()
            bs = rng.choice(d, (a.boots, len(d))).mean(axis=1)
            nc = npar = len(d)
            cm = np.mean([c['tempo'] for c, p in pairs if c['map'] == m]); pm = np.mean([p['tempo'] for c, p in pairs if c['map'] == m])
        else:
            x = np.array([r['tempo'] for r in C if r['map'] == m]); y = np.array([r['tempo'] for r in P if r['map'] == m])
            if len(x) < 3 or len(y) < 3:
                continue
            est = x.mean() - y.mean()
            bs = rng.choice(x, (a.boots, len(x))).mean(axis=1) - rng.choice(y, (a.boots, len(y))).mean(axis=1)
            nc, npar, cm, pm = len(x), len(y), x.mean(), y.mean()
        boot_by_map.append(bs)
        rows.append((m, refs[m]['kind'], nc, npar, cm, pm, est, np.percentile(bs, 2.5), np.percentile(bs, 97.5)))
    if not rows:
        raise SystemExit('no map has 3+ games for both bots')
    tot = np.mean(boot_by_map, axis=0)
    D = float(np.mean([r[6] for r in rows]))
    lo, hi = np.percentile(tot, 2.5), np.percentile(tot, 97.5)
    se = tot.std()
    print(f'\nTEMPO  candidate {bc}  vs  parent {bp}   ({"paired on " + str(len(pairs)) + " fixtures" if paired else "unpaired (file names do not pair)"})')
    print(f'{"map":24s} {"ref":6s} {"n":>5s} {"cand":>7s} {"parent":>7s} {"delta":>7s}   95% CI')
    for m, k, nc, npar, cm, pm, est, l, h in rows:
        flag = '  <- slower' if l > MAP_GUARD else ''
        print(f'{m[:24]:24s} {k:6s} {nc:5d} {cm:7.1f} {pm:7.1f} {est:+7.1f}   [{l:+.1f}, {h:+.1f}]{flag}')
    print(f'\ntempo delta (candidate - parent, rounds, maps weighted equally; negative = faster): {D:+.2f}  95% CI [{lo:+.2f}, {hi:+.2f}]')
    print('\nguards (candidate vs parent, means over the same games; context, not part of the verdict):')
    for k, lab, want in GUARDS:
        cv = [r[k] for r in C if r['map'] in refs and r.get(k) is not None]
        pv = [r[k] for r in P if r['map'] in refs and r.get(k) is not None]
        if cv and pv:
            c_, p_ = float(np.mean(cv)), float(np.mean(pv))
            worse = (c_ > p_ * 1.10) if want == 'down' else (c_ < p_ * 0.90)
            print(f'  {lab:40s} {p_:8.3f} -> {c_:8.3f}{"   (worse by >10%)" if worse else ""}')
    slow_maps = [r[0] for r in rows if r[7] > MAP_GUARD]
    if D <= -DELTA and hi < 0 and not slow_maps:
        v = 'ACCEPT'
    elif D <= -DELTA and hi < 0:
        v = 'MAP GUARD - faster overall, but significantly slower on ' + ', '.join(slow_maps) + '; fix those maps before accepting'
    elif lo > 0:
        v = 'REJECT (slower than the parent)'
    elif lo > -DELTA:
        v = f'NO GAIN (a {DELTA:.0f}-round improvement is excluded; keep the parent)'
    else:
        need = int(np.ceil(len(pairs if paired else C) * (se / (DELTA / 2.8)) ** 2)) if se > 0 else 0
        v = f'INCONCLUSIVE - about {need} fixtures would resolve a {DELTA:.0f}-round change (have {len(pairs if paired else C)})'
    why = (f'delta {D:+.1f} rounds, CI [{lo:+.1f}, {hi:+.1f}]' + (f'; map guard: {", ".join(slow_maps)}' if slow_maps else ''))
    print(f'\nVERDICT: {v}   ({why}; accept rule: delta <= -{DELTA:.0f}, CI upper < 0, no map slower by > {MAP_GUARD:.0f})')


if __name__ == '__main__':
    main()
