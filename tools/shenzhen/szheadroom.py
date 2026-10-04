"""H-SZ54: children born at small unit headroom (64 - team units at birth) live shorter / eat less? Simulator replays."""
import sys, glob, collections, statistics; sys.path.insert(0, '/home/claude/fr'); import frame
LO, HI = int(sys.argv[1]), int(sys.argv[2]); sys.argv = sys.argv[2:]
rows = []
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        g = frame.decode(f); R = g['last_round']
        death = {d['id']: d['round'] for d in g['events']['deaths']}
        meals = collections.defaultdict(list)
        for e in g['events']['eats']: meals[e['id']].append(e['round'])
        for s in g['events']['splits']:
            r = s['round']; t = s['team']; c = s['child']
            if r < LO or r > min(HI, R - 100): continue
            units = sum(1 for (tt, _) in g['rounds'][max(0, r - 1)].values() if tt == t)
            life = min(death.get(c, R), r + 100) - r
            m = sum(1 for x in meals[c] if r < x <= r + 100)
            rows.append((64 - units, life, m))
bins = [(0, 1), (2, 4), (5, 9), (10, 19), (20, 64)]
for lo, hi in bins:
    v = [(l, m) for h, l, m in rows if lo <= h <= hi]
    if not v: continue
    ls = sorted(l for l, _ in v); ms = [m for _, m in v]
    print(f'headroom {lo:>2}-{hi:<2} n {len(v):>6}  median life (cap 100) {ls[len(ls)//2]:>3}  died<100 {sum(l < 100 for l in ls)/len(ls):.2f}  meals/100r {sum(ms)/len(ms):.2f}')
