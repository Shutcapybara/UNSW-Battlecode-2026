#!/usr/bin/env python3
"""Classify our deaths: doomed at the start of the round (no neighbour free of kelp and bodies) or not, and what the
dragon did the round before (split / tsplit child / move into pocket). Aggregates over replays.

    python tools/rb/doom.py REPLAY ... [--team-bot aline]
"""
import sys, glob, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.analysis.features.frame import decode

def main():
    tag = 'aline'
    args = [a for a in sys.argv[1:]]
    if '--team-bot' in args:
        i = args.index('--team-bot'); tag = args[i + 1]; del args[i:i + 2]
    C = collections.Counter(); ML = collections.Counter()
    for p in args:
        f = decode(p); us = 'A' if tag in f['botA'] else 'B'
        nbr = f['nbr']
        acts = {(e['round'], e['id']): e for e in f['events']['actions']}
        splits = {(s['round'], s['parent']): s for s in f['events']['splits']}
        born_by = {s['child']: s for s in f['events']['splits']}
        for d in f['events']['deaths']:
            if d['team'] != us or d['actor'] != d['id']:
                continue
            r = d['round']; snap = f['rounds'][r]
            if d['id'] not in snap:
                continue
            body = snap[d['id']][1]; head = body[0]
            occ = {c for i, (t, b) in snap.items() for c in b}
            tail = body[-1]
            free = [n for n in nbr[head] if n is not None and (n not in occ)]
            doomed = not free
            prev = acts.get((r - 1, d['id']), {}).get('kind')
            sp = (r - 1, d['id']) in splits
            key = ('doomed' if doomed else 'free', d['cause'], 'after_split' if sp else ('newborn' if d['age'] <= 1 else 'other'))
            C[key] += 1; ML[key] += d['length']
    tot = sum(C.values())
    for k, v in sorted(C.items(), key=lambda x: -x[1]):
        print(f'{k[0]:7s} {k[1]:6s} {k[2]:12s} {v:6d} ({100*v/tot:4.1f}%)  mean len {ML[k]/v:.2f}')

main()
