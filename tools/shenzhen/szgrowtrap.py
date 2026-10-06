"""H-SZ44 growth trap: meals in the 5 rounds before a self/wall death (sealed deaths), queen vs others, vs the base rate."""
import sys, glob, collections; sys.path.insert(0, '/home/claude/fr'); import frame
c = collections.Counter()
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        g = frame.decode(f)
        eats = collections.defaultdict(list)
        for e in g['events']['eats']: eats[e['id']].append(e['round'])
        for d in g['events']['deaths']:
            k = 'queen' if d['id'] <= 1 else 'other'
            m = sum(1 for r in eats[d['id']] if d['round'] - 5 <= r <= d['round'])
            grp = 'sealed' if d['cause'] in ('self', 'wall') else ('h2h' if d['cause'] == 'h2h' else 'rest')
            c[(k, grp, 'n')] += 1; c[(k, grp, 'meals5')] += m; c[(k, grp, 'ge3')] += m >= 3
for k in ('queen', 'other'):
    for grp in ('sealed', 'h2h', 'rest'):
        n = c[(k, grp, 'n')]
        if n: print(k, grp, n, 'meals in last 5 rounds', round(c[(k, grp, 'meals5')] / n, 2), '>=3 meals', round(c[(k, grp, 'ge3')] / n, 2))
