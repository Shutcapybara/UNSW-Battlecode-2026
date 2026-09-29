#!/usr/bin/env python3
"""C1-C frame pass: portal transits and per-dragon first-pearl lag, from the F1 decode cache.

The ledger (c1c_ledger.py) aggregates parquets only; these two statistics need the raw
frames, so they run on the cached decodes of the populations we own (team-7 live corpus
games and the local yuna-v03-core fixtures). A portal transit is a head move to a cell
that is not a neighbour of the previous head (nbr already resolves wrap, so only portal
jumps qualify). First-pearl lag is rounds from a dragon's birth to its first eat.

  python tools/analysis/c1c_frames.py --cache build/c1c/frame-cache \
      --team7-list build/c1c/team7_replays.txt --local-index build/c1c/yuna-fixture/index.jsonl \
      --out build/c1c/frames_stats.json
"""
import argparse, glob, gzip, json, os, pickle, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def side_stats(g, W=100):
    """{side: dict(transits, eats, lags, newborn_lags, noeat20, births)} over rounds < W."""
    nbr = g['nbr']
    rounds = g['rounds']
    out = {}
    prev_head = {}          # id -> (round, head)
    transits = {'A': 0, 'B': 0}
    for r, snap in enumerate(rounds[:W + 1]):
        for i, (t, b) in snap.items():
            h = b[0]
            if i in prev_head and prev_head[i][0] == r - 1:
                if h not in nbr[prev_head[i][1]]:
                    transits[t] += 1
            prev_head[i] = (r, h)
    born = {i: 0 for i in rounds[0]}
    for sp in g['events']['splits']:
        born[sp['child']] = sp['round']
    born = {i: b for i, b in born.items() if b < W}
    died_at = {}
    for d in g['events']['deaths']:
        died_at.setdefault(d['id'], d['round'])
    first_eat = {}
    eats = {'A': 0, 'B': 0}
    for e in g['events']['eats']:
        if e['round'] < W:
            eats[e['team']] += 1
            if e['id'] not in first_eat:
                first_eat[e['id']] = e['round']
    for t in 'AB':
        initial = set(rounds[0])
        lags = [first_eat[i] - born[i] for i in born if i in first_eat]
        child_lags = [first_eat[i] - born[i] for i in born if i in first_eat and i not in initial]
        noeat20 = sum(1 for i in born if i not in first_eat and min(died_at.get(i, W), W) - born[i] > 20)
        childborn = sum(1 for i in born if i not in initial)
        out[t] = dict(transits=transits[t], eats=eats[t], n_dragons=len(born), child_births=childborn,
                      lag_median=statistics.median(lags) if lags else None,
                      child_lag_median=statistics.median(child_lags) if child_lags else None,
                      noeat20=noeat20)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', default='build/c1c/frame-cache')
    ap.add_argument('--team7-list', default='build/c1c/team7_replays.txt')
    ap.add_argument('--corpus-index', default='public_replays/corpus/index.jsonl')
    ap.add_argument('--local-index', default='build/c1c/yuna-fixture/index.jsonl')
    ap.add_argument('--out', default='build/c1c/frames_stats.json')
    a = ap.parse_args(argv)

    by_stem = {}
    for p in glob.glob(str(ROOT / a.cache / '*.pkl.gz')):
        stem = Path(p).name.split('.')[0]
        by_stem.setdefault(stem, p)

    rows = []
    t7 = {Path(l.strip()).stem for l in open(ROOT / a.team7_list) if l.strip()}
    corpus_idx = {str(r['game_id']): r for r in (json.loads(l) for l in open(ROOT / a.corpus_index))}
    local = [json.loads(l) for l in open(ROOT / a.local_index)]
    for stem, path in sorted(by_stem.items()):
        with gzip.open(path, 'rb') as f:
            g = pickle.load(f)
        st = side_stats(g)
        for side, d in st.items():
            if stem in t7:
                r7 = corpus_idx.get(stem)
                ours = (r7 and ((r7['team_a'] == 7 and side == 'A') or (r7['team_b'] == 7 and side == 'B')))
                if not ours:
                    continue
                pop = 'team7live'
            else:
                fx = next((r for r in local if r['game'] == stem), None)
                if not fx:
                    continue
                us_a = fx['botA'] == 'yuna-v03-core'
                pop = 'yunalocal' if ((side == 'A') == us_a) else 'opplocal'
            rows.append(dict(pop=pop, map=g['map'], game=stem, side=side, **d))

    json.dump(rows, open(ROOT / a.out, 'w'))
    # medians per population
    for pop in ('team7live', 'yunalocal', 'opplocal'):
        rs = [r for r in rows if r['pop'] == pop]
        if not rs:
            continue
        tp = statistics.median(r['transits'] for r in rs)
        ep = statistics.median(r['eats'] for r in rs)
        cl = [r['child_lag_median'] for r in rs if r['child_lag_median'] is not None]
        n20 = statistics.median(r['noeat20'] for r in rs)
        cb = statistics.median(r['child_births'] for r in rs)
        print(f'{pop}: n={len(rs)} transits r<100 med {tp} (per pearl {tp / max(ep, 1):.3f}), '
              f'eats {ep}, child first-eat lag med {statistics.median(cl) if cl else None}, '
              f'children never eating >20r med {n20} of {cb} born')


if __name__ == '__main__':
    main()
