"""D-075 trial statistic. For each window: mean(score - E) with OUR rating fixed at --fixed (1725), whole-series
bootstrap 1,000 x seed 7 (5/95, linear); performance rating (rating at which the window's score equals its expectation)
with the same bootstrap; and the figure at the activation anchor (our rating at the window's first game).
Windows: --sub ID[:FROM_ISO] (ranked games of that submission from FROM), --ref ID:BEFORE_ISO:N (last N ranked games,
extended to a series boundary, before BEFORE). Run from the repo root."""
import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_monitor as lm  # noqa: E402


def iso(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def series(gs):
    by, order = {}, []
    for g in gs:
        if g['series'] not in by:
            order.append(g['series'])
        by.setdefault(g['series'], []).append(g)
    return [by[s] for s in order]


def perf(sc, ro):
    lo, hi = 800.0, 3000.0
    for _ in range(60):
        m = (lo + hi) / 2
        e = (1 / (1 + 10 ** ((ro - m) / 400))).sum()
        lo, hi = (m, hi) if e < sc.sum() else (lo, m)
    return (lo + hi) / 2


def window(ser, fixed, anchor, label):
    S = [np.array([g['score'] for g in s]) for s in ser]
    R = [np.array([g['ro'] for g in s]) for s in ser]
    rng = np.random.default_rng(7)
    def stat(idx, a):
        sc = np.concatenate([S[i] for i in idx]); ro = np.concatenate([R[i] for i in idx])
        return (sc - 1 / (1 + 10 ** ((ro - a) / 400))).mean(), sc, ro
    allidx = list(range(len(ser)))
    m, sc, ro = stat(allidx, fixed)
    ma = stat(allidx, anchor)[0] if anchor else float('nan')
    p = perf(sc, ro)
    bm, bp = [], []
    for _ in range(1000):
        idx = rng.integers(0, len(ser), len(ser))
        x, s2, r2 = stat(idx, fixed)
        bm.append(x); bp.append(perf(s2, r2))
    n = sum(len(s) for s in ser)
    w = int(sc.sum()); l = n - w
    print(f'{label}: n {n} games / {len(ser)} series, W-L {sc.sum():g}-{n - sc.sum():g}; '
          f'score-E @{fixed}: {m:+.3f} [{np.percentile(bm, 5):+.3f}, {np.percentile(bm, 95):+.3f}]; '
          f'perf rating {p:.0f} [{np.percentile(bp, 5):.0f}, {np.percentile(bp, 95):.0f}]; '
          f'@activation anchor {anchor}: {ma:+.3f}')
    return np.array([sum(g['score'] - 1 / (1 + 10 ** ((g['ro'] - fixed) / 400)) for g in s) for s in ser]), \
        np.array([len(s) for s in ser])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sub', action='append', default=[])
    ap.add_argument('--ref', action='append', default=[])
    ap.add_argument('--fixed', type=float, default=1725)
    ap.add_argument('--maxgames', type=int, default=0, help='cut each --sub window at the first series boundary >= N')
    a = ap.parse_args()
    repo = Path('.')
    since = datetime.now(timezone.utc) - timedelta(days=14)
    ladders = lm.load_ladders(repo / 'public_replays/corpus/ladder', since - timedelta(hours=2))
    keys = [t for t, _ in ladders]
    allg = [g for g in lm.own_games(repo / 'public_replays/corpus/index.jsonl', since) if g['ranked']]
    allg.sort(key=lambda g: g['at'])
    def prep(gs):
        out = []
        for g in gs:
            ro = lm.rating_at(ladders, keys, g['at'], g['opp'])
            if ro is not None:
                g = dict(g); g['ro'] = ro; out.append(g)
        return out
    res = {}
    for spec in a.ref:
        sid, before, n = spec.split(':', 2) if spec.count(':') == 2 else (None, None, None)
        sid, rest = spec.split(':', 1); before, n = rest.rsplit(':', 1); n = int(n)
        gs = [g for g in allg if g['bot'] == sid and g['at'] < iso(before)]
        ids, k = [], 0
        for g in reversed(gs):
            if not ids or ids[-1] != g['series']:
                if k >= n:
                    break
                ids.append(g['series'])
            k += 1
        gs = prep([g for g in gs if g['series'] in set(ids)])
        anc = lm.rating_at(ladders, keys, gs[0]['at'], lm.TEAM) if gs else None
        res['ref ' + sid] = window(series(gs), a.fixed, anc, f'ref {sid} (last {n} before {before})')
    for spec in a.sub:
        sid, _, frm = spec.partition(':')
        gs = [g for g in allg if g['bot'] == sid and (not frm or g['at'] >= iso(frm))]
        if a.maxgames:
            ids, k = [], 0
            for g in gs:
                if not ids or ids[-1] != g['series']:
                    if k >= a.maxgames:
                        break
                    ids.append(g['series'])
                k += 1
            gs = [g for g in gs if g['series'] in set(ids)]
        gs = prep(gs)
        if not gs:
            print(f'sub {sid}: no ranked games with an expectation'); continue
        anc = lm.rating_at(ladders, keys, gs[0]['at'] - timedelta(minutes=1), lm.TEAM)
        res['sub ' + sid] = window(series(gs), a.fixed, anc, f'sub {sid} (from {gs[0]["at"]:%H:%MZ} to {gs[-1]["at"]:%H:%MZ})')
    refs = [k for k in res if k.startswith('ref')]
    rng = np.random.default_rng(7)
    for k in res:
        if k.startswith('sub') and refs:
            (ns, nc), (rs, rc) = res[k], res[refs[0]]
            d = ns.sum() / nc.sum() - rs.sum() / rc.sum()
            i = rng.integers(0, len(ns), (1000, len(ns))); j = rng.integers(0, len(rs), (1000, len(rs)))
            bd = ns[i].sum(1) / nc[i].sum(1) - rs[j].sum(1) / rc[j].sum(1)
            print(f'{k} - {refs[0]} @{a.fixed:g}: {d:+.3f} [{np.percentile(bd, 5):+.3f}, {np.percentile(bd, 95):+.3f}]')


if __name__ == '__main__':
    main()
