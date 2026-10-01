#!/usr/bin/env python3
"""Render a board window from a replay with kelp edges, for reading individual incidents.

    python tools/rb/show.py REPLAY --round R --at X,Y [--r 5]
    python tools/rb/show.py REPLAY --deaths [--team-bot aline] [--cause wall] [--max-age 10] [--limit 5] [--r 4]

Cells: our head H / body h (the dying dragon's head is *), enemy head E / body e, pearl o, bed tile ',' (spawning
tile), empty '.'. Edges: '|' / '-' kelp, 'P' portal (a neighbour that is not the adjacent cell).
The board shown is the start-of-round snapshot (before any dragon moves in that round).
"""
from __future__ import annotations

import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.analysis.features.frame import decode  # noqa: E402

DIRC = 'NESW'


def render(f, rnd, center, rad, us, mark=None):
    W, H, nbr = f['W'], f['H'], f['nbr']
    snap = f['rounds'][rnd]
    occ = {}
    for i, (t, b) in snap.items():
        for k, c in enumerate(b):
            ch = ('H' if t == us else 'E') if k == 0 else ('h' if t == us else 'e')
            if i == mark and k == 0:
                ch = '*'
            occ[c] = ch
    pearls = f['pearls'][rnd]
    cx, cy = center
    out = []
    for dy in range(-rad, rad + 1):
        row, edge = [], []
        for dx in range(-rad, rad + 1):
            c = ((cx + dx) % W, (cy + dy) % H)
            ch = occ.get(c) or ('o' if c in pearls else (',' if c in f['beds'] else '.'))
            e = nbr[c][1]
            adj = ((c[0] + 1) % W, c[1])
            sep = '|' if e is None else ('P' if e != adj else ' ')
            row.append(ch + sep)
            s = nbr[c][2]
            adj = (c[0], (c[1] + 1) % H)
            edge.append(('-' if s is None else 'P' if s != adj else ' ') + ' ')
        out.append(''.join(row)); out.append(''.join(edge))
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('replay'); ap.add_argument('--round', type=int); ap.add_argument('--at')
    ap.add_argument('--r', type=int, default=4); ap.add_argument('--deaths', action='store_true')
    ap.add_argument('--team-bot', default='aline'); ap.add_argument('--cause'); ap.add_argument('--max-age', type=int, default=999)
    ap.add_argument('--min-round', type=int, default=0)
    ap.add_argument('--limit', type=int, default=5); ap.add_argument('--skip', type=int, default=0)
    a = ap.parse_args()
    f = decode(a.replay)
    us = 'A' if a.team_bot in f['botA'] else 'B'
    if not a.deaths:
        x, y = map(int, a.at.split(','))
        print(render(f, a.round, (x, y), a.r, us)); return
    acts = {(e['round'], e['id']): e for e in f['events']['actions']}
    n = 0
    for d in f['events']['deaths']:
        if d['team'] != us or d['age'] > a.max_age or d['round'] < a.min_round or (a.cause and d['cause'] != a.cause) or d['actor'] != d['id']:
            continue
        n += 1
        if n <= a.skip:
            continue
        if n > a.skip + a.limit:
            break
        r = d['round']
        body = f['rounds'][r].get(d['id'], (None, (d['head'],)))[1]
        act = acts.get((r, d['id']), {})
        prev = acts.get((r - 1, d['id']), {})
        print(f"--- round {r} id {d['id']} cause {d['cause']} len {d['length']} age {d['age']} "
              f"act {act.get('kind')} {''.join(DIRC[x] for x in act.get('dirs', ()))}  prev {prev.get('kind')} "
              f"{''.join(DIRC[x] for x in prev.get('dirs', ()))} head {body[0]}")
        for rr in (r - 1, r):
            if rr >= 0 and d['id'] in f['rounds'][rr]:
                print(f'[start of round {rr}]')
                print(render(f, rr, body[0], a.r, us, mark=d['id']))


if __name__ == '__main__':
    main()
