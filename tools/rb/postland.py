#!/usr/bin/env python3
"""Deaths of our dragons within 2 rounds after a portal crossing: cause, whether the dragon was doomed at the start
of its fatal turn, and the round of the crossing relative to the death.

    python tools/rb/postland.py REPLAY ... [--team-bot aline]
"""
import sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.analysis.features.frame import decode

tag = 'aline'
args = sys.argv[1:]
if '--team-bot' in args:
    i = args.index('--team-bot'); tag = args[i + 1]; del args[i:i + 2]
C = collections.Counter(); total = collections.Counter()
for p in args:
    f = decode(p); us = 'A' if tag in f['botA'] else 'B'
    W, H, nbr = f['W'], f['H'], f['nbr']
    cross = {}
    for a in f['events']['actions']:
        if a['team'] != us or a['kind'] != 'move':
            continue
        b = f['rounds'][a['round']].get(a['id'])
        if not b:
            continue
        c = b[1][0]
        for dd in a.get('dirs', ()):
            n = nbr[c][dd]
            if n is None:
                break
            if n != ((c[0] + (0, 1, 0, -1)[dd]) % W, (c[1] + (-1, 0, 1, 0)[dd]) % H):
                cross[a['id']] = a['round']
            c = n
    for d in f['events']['deaths']:
        if d['team'] != us:
            continue
        total[d['cause']] += 1
        r0 = cross.get(d['id'])
        if r0 is None or d['round'] - r0 > 2:
            continue
        snap = f['rounds'][d['round']]
        doomed = '?'
        if d['id'] in snap:
            head = snap[d['id']][1][0]
            occ = {x for i, (t, b) in snap.items() for x in b}
            doomed = 'doomed' if not [n for n in nbr[head] if n is not None and n not in occ] else 'free'
        C[(d['round'] - r0, d['cause'], doomed)] += 1
print('all our deaths by cause', dict(total))
for k, v in sorted(C.items(), key=lambda x: -x[1]):
    print(f'  +{k[0]} rounds after crossing  {k[1]:5s} {k[2]:7s} {v}')
