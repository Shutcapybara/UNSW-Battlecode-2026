#!/usr/bin/env python3
"""Queen columns by round (D-080 §B), for a candidate and a parent on one panel, seed 1:
our queen alive at rounds 100, 200, 300 (death round from the replay death events, frame cache; among sides whose game reached that round)
and at the end (engine result block, round-limit games); both queens' length at the end (engine `queen`, median and
mean over round-limit games, 0 = dead); results of round-limit games in which both queens are alive.
Appends a markdown block to --out (creates it if missing).

    python tools/asahi/queencols.py CAND --parent PARENT --panel pool --out docs/learning/results/asahi/X-queen.md
"""
import argparse, glob, json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asahi'))
import panel as P  # noqa: E402


def table(bot, pnl):
    """Per game, our side: queen (team's starting dragon, id 0 or 1) death round from the replay's death events (frame
    cache), lengths at the end from the engine result block. (The features dragons table is not used: its lowest-id
    initial dragon does not always match the engine's queen.)"""
    import gzip, pickle
    root = P.run_root(bot, pnl)
    rows = []
    for l in open(root / 'index.jsonl'):
        r = json.loads(l)
        if r.get('rc') != 0 or r['seed'] != 1:
            continue
        hits = glob.glob(str(root / 'frames' / (r['game'] + '.*.pkl.gz')))
        if not hits:
            continue
        g = pickle.load(gzip.open(max(hits, key=lambda h: Path(h).stat().st_mtime)))
        me, op = r['seat'], ('B' if r['seat'] == 'A' else 'A')
        qd = [d for d in g['events']['deaths'] if d['id'] in (0, 1) and d['team'] == me]
        rows.append(dict(game=r['game'], win=r['winner'] == me, last=int(g['last_round']), limit=int(g['last_round']) >= 499,
                         died=qd[0]['round'] if qd else None, cause=qd[0]['cause'] if qd else None, q_me=int(g['final'][me]['queen']), q_op=int(g['final'][op]['queen'])))
    return rows


def summary(rows):
    out = {}
    for R in (100, 200, 300):
        s = [x for x in rows if x['last'] >= R]
        a = [x for x in s if x['died'] is None or x['died'] > R]
        out[f'alive@r{R}'] = (len(a), len(s))
    lim = [x for x in rows if x['limit']]
    out['alive@end'] = (sum(x['q_me'] > 0 for x in lim), len(lim))
    out['our len@end med/mean'] = (statistics.median([x['q_me'] for x in lim]) if lim else 0,
                                   round(sum(x['q_me'] for x in lim) / len(lim), 1) if lim else 0)
    out['opp len@end med/mean'] = (statistics.median([x['q_op'] for x in lim]) if lim else 0,
                                   round(sum(x['q_op'] for x in lim) / len(lim), 1) if lim else 0)
    import collections
    cz = collections.Counter(x['cause'] for x in rows if x['cause'])
    out['queen deaths: wall / other'] = (cz.get('wall', 0), sum(cz.values()) - cz.get('wall', 0))
    out['queen deaths by cause'] = (', '.join(f'{k} {v}' for k, v in cz.most_common()), len(rows))
    both = [x for x in lim if x['q_me'] > 0 and x['q_op'] > 0]
    out['both alive@end W-L'] = (sum(x['win'] for x in both), len(both) - sum(x['win'] for x in both))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cand'); ap.add_argument('--parent', required=True)
    ap.add_argument('--panel', default='pool'); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    c, p = summary(table(a.cand, a.panel)), summary(table(a.parent, a.panel))
    L = ['', f'## Queen by round ({a.panel}, seed 1; D-080 §B) — {a.cand} vs {a.parent}', '',
         'Alive at r100/200/300: death round from the death events, among sides whose game reached the round. End: engine '
         'result block, round-limit games. Lengths: engine queen length at the end, 0 = dead.', '',
         '| column | cand | parent |', '|---|---|---|']
    def f(v):
        return (f'{v[0]}–{v[1]}' if 'W-L' in k else f'{v[0]}/{v[1]}' if 'alive' in k else f'{v[0]} / {v[1]}')
    for k in c:
        L.append(f'| {k} | {f(c[k])} | {f(p[k])} |')
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'a') as fh:
        fh.write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
