#!/usr/bin/env python3
"""Paired H-S1 portal transit-death analysis for Carthage lane replays.

    python tools/carthage/portal_memory_report.py carthage-11-portal-memory \
        --parent carthage-05-free-sprint --seeds 1,2,3

Reads the lane's fixed pool/gen fixture lists and replays. Outputs exact target-
side portal transits and deaths within three rounds, with game-cluster paired
bootstrap intervals and Portals/Trauma/Schooltime map rows.
"""
import argparse
import json
import multiprocessing
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.carthage import lane  # noqa: E402
from tools.replay_stats.portal_deaths import portal_metrics  # noqa: E402


def one(args):
    panel, bot, fx, parent = args
    root = lane.RUNS / bot / panel / 'replays'
    replay = root / (fx['game'] + '.replay')
    if not replay.exists():
        return dict(panel=panel, bot=bot, game=fx['game'], map=fx['map'], seat=fx['seat'], error='missing replay')
    try:
        m = portal_metrics(replay)
        side = fx['seat']
        deaths = {}
        for d in m['deaths']:
            if d['team'] == side:
                deaths.setdefault(d['id'], []).append(d['round'])
        transits = m['steps'][side]
        died3 = sum(any(r <= death_round <= r + 3 for death_round in deaths.get(dragon, ()))
                    for r, dragon, _pid, _entry, _exit in transits)
        return dict(panel=panel, bot=bot, game=fx['game'], seed=fx['seed'], map=fx['map'], opp=fx['opp'],
                    seat=side, parent=parent, transits=len(transits), died3=died3,
                    verified_moves=m['verified'], mismatched_moves=m['mismatched'], error=None)
    except Exception as exc:
        return dict(panel=panel, bot=bot, game=fx['game'], map=fx['map'], seat=fx['seat'],
                    error=f'{type(exc).__name__}: {exc}')


def summarize(rows):
    n = sum(r['transits'] for r in rows)
    d = sum(r['died3'] for r in rows)
    return dict(games=len(rows), transits=n, died3=d, rate=(d / n if n else None),
                verified_moves=sum(r.get('verified_moves', 0) for r in rows),
                mismatched_moves=sum(r.get('mismatched_moves', 0) for r in rows))


def paired_bootstrap(candidate, parent, reps=3000, seed=17):
    import numpy as np

    c = {(r['seed'], r['map'], r['opp'], r['seat']): r for r in candidate}
    p = {(r['seed'], r['map'], r['opp'], r['seat']): r for r in parent}
    keys = sorted(set(c) & set(p))
    if not keys:
        return dict(n=0, delta=None, interval90=None, relative_drop=None)
    ca = np.array([[c[k]['died3'], c[k]['transits']] for k in keys], dtype=float)
    pa = np.array([[p[k]['died3'], p[k]['transits']] for k in keys], dtype=float)

    def rate(a, ix):
        v = a[ix].sum(axis=0)
        return v[0] / v[1] if v[1] else float('nan')

    ix = np.arange(len(keys))
    rc, rp = rate(ca, ix), rate(pa, ix)
    delta = rc - rp
    rng = np.random.default_rng(seed)
    boot = np.empty(reps)
    for i in range(reps):
        sample = rng.integers(0, len(keys), len(keys))
        boot[i] = rate(ca, sample) - rate(pa, sample)
    lo, hi = np.nanpercentile(boot, [5, 95])
    return dict(n=len(keys), candidate_rate=float(rc), parent_rate=float(rp), delta=float(delta),
                interval90=[float(lo), float(hi)],
                relative_drop=(float((rp - rc) / rp) if rp else None))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot')
    ap.add_argument('--parent', required=True)
    ap.add_argument('--seeds', default='1,2,3')
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--out')
    a = ap.parse_args()
    seeds = [int(x) for x in a.seeds.split(',')]
    try:
        multiprocessing.set_start_method('fork')
    except RuntimeError:
        pass

    results = {'candidate': a.bot, 'parent': a.parent, 'seeds': seeds, 'panels': {}}
    errors = []
    for panel in ('pool', 'gen'):
        cfx = lane.fixtures(a.bot, panel, seeds)
        pfx = lane.fixtures(a.parent, panel, seeds)
        tasks = [(panel, a.bot, fx, False) for fx in cfx] + [(panel, a.parent, fx, True) for fx in pfx]
        with ProcessPoolExecutor(a.jobs) as pool:
            rows = list(pool.map(one, tasks, chunksize=4))
        errors.extend(r for r in rows if r.get('error'))
        cand = [r for r in rows if r['bot'] == a.bot and not r.get('error')]
        parent = [r for r in rows if r['bot'] == a.parent and not r.get('error')]
        c_by_map, p_by_map = {}, {}
        for m in sorted({r['map'] for r in cand + parent}):
            c_by_map[m] = summarize([r for r in cand if r['map'] == m])
            p_by_map[m] = summarize([r for r in parent if r['map'] == m])
        focus = {}
        for m in sorted({r['map'] for r in cand + parent}):
            if m.split('/')[-1].lower().startswith(('portals', 'trauma', 'schooltime')):
                cr, pr = c_by_map[m]['rate'], p_by_map[m]['rate']
                focus[m] = dict(candidate=c_by_map[m], parent=p_by_map[m],
                                relative_drop=((pr - cr) / pr if pr else None))
        results['panels'][panel] = dict(candidate=summarize(cand), parent=summarize(parent),
                                        paired=paired_bootstrap(cand, parent), focus_maps=focus)
    results['errors'] = errors
    txt = json.dumps(results, indent=2)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(txt + '\n')
    print(txt)


if __name__ == '__main__':
    main()
