#!/usr/bin/env python3
"""Harvest audit: per dead-end branch, how each team used it (visits, pearls eaten, deaths, idle rounds with pearls)."""
import sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/analysis/features'))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/hub/vendor/ouroboros'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bokuto'))
import frame
from branches import branches

def main(bot, files):
    tot = collections.defaultdict(lambda: collections.defaultdict(float)); n = 0
    for f in files:
        g = frame.decode(f)
        us = 'A' if bot in g['botA'] else 'B'
        alive, pruned, groups = branches(g['nbr'])
        cell2b = {}
        for bi, (j, comp) in enumerate(groups.items()):
            for c in comp: cell2b[c] = bi
        nb = len(groups)
        if not nb: continue
        n += 1
        # per round: which team occupies each branch; pearls present
        occ_rounds = collections.Counter(); pearl_idle = collections.Counter()
        for r, snap in enumerate(g['rounds'][:-1]):
            inb = collections.defaultdict(set)
            for i, (t, b) in snap.items():
                for c in b:
                    if c in cell2b: inb[cell2b[c]].add(t)
            for bi in range(nb):
                teams = inb.get(bi, set())
                for t in teams: occ_rounds[(bi, t)] += 1
                if not teams:
                    p = sum(1 for c in g['pearls'][r] if cell2b.get(c) == bi)
                    if p >= 3: pearl_idle[bi] += 1
        eats = collections.Counter(); deaths = collections.Counter()
        for e in g['events']['eats']:
            if e['cell'] in cell2b: eats[(cell2b[e['cell']], e['team'])] += 1
        for d in g['events']['deaths']:
            if d['head'] in cell2b: deaths[(cell2b[d['head']], d['team'])] += 1
        them = 'B' if us == 'A' else 'A'
        rows = []
        for bi, (j, comp) in enumerate(groups.items()):
            rows.append((len(comp), bi, j))
        rows.sort(reverse=True)
        print(f"== {Path(f).stem[:60]} {'W' if g['winner']==us else 'L'}")
        for size, bi, j in rows[:6]:
            print(f"   branch@{j} cells {size:>2}: occupied us {occ_rounds[(bi,us)]:>3} them {occ_rounds[(bi,them)]:>3} | eats us {eats[(bi,us)]:>3} them {eats[(bi,them)]:>3} | deaths us {deaths[(bi,us)]:>2} them {deaths[(bi,them)]:>2} | idle with >=3 pearls {pearl_idle[bi]:>3}")
            tot['occ']['us'] += occ_rounds[(bi,us)]; tot['occ']['them'] += occ_rounds[(bi,them)]
            tot['eats']['us'] += eats[(bi,us)]; tot['eats']['them'] += eats[(bi,them)]
            tot['idle']['x'] += pearl_idle[bi]
    print('totals', {k: dict(v) for k, v in tot.items()})

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
