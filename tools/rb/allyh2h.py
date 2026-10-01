#!/usr/bin/env python3
"""Count our ally head-on collisions (both dragons ours) and portal crossings per replay.

    python tools/rb/allyh2h.py REPLAY ... [--team-bot aline]
"""
import sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.analysis.features.frame import decode

tag = 'aline'
args = sys.argv[1:]
if '--team-bot' in args:
    i = args.index('--team-bot'); tag = args[i + 1]; del args[i:i + 2]
tot = collections.Counter()
for p in args:
    f = decode(p); us = 'A' if tag in f['botA'] else 'B'
    W, H, nbr = f['W'], f['H'], f['nbr']
    by = collections.defaultdict(list)
    for d in f['events']['deaths']:
        if d['cause'] == 'h2h':
            by[(d['round'], d['actor'])].append(d)
    ally = sum(1 for ds in by.values() if len(ds) >= 2 and all(d['team'] == us for d in ds))
    cross = 0
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
                cross += 1
            c = n
    tot['ally_h2h'] += ally; tot['crossings'] += cross; tot['games'] += 1
print(dict(tot), f"collisions per 100 crossings {100 * tot['ally_h2h'] / max(1, tot['crossings']):.2f}")
