"""Who wins a freed slot? For splits at headroom 0-1 vs >=10: the parent's meals in the previous 20 rounds and length,
against the mean over other allied dragons of length >= 4 alive that round. Simulator replays."""
import sys, glob, collections, bisect; sys.path.insert(0, '/home/claude/fr'); import frame
acc = collections.defaultdict(lambda: collections.Counter())
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        g = frame.decode(f); R = g['last_round']
        meals = collections.defaultdict(list)
        for e in g['events']['eats']: meals[e['id']].append(e['round'])
        for v in meals.values(): v.sort()
        m20 = lambda i, r: bisect.bisect_right(meals[i], r) - bisect.bisect_left(meals[i], r - 20)
        for s in g['events']['splits']:
            r, t, p = s['round'], s['team'], s['parent']
            if r < 50 or r > R - 50: continue
            snap = g['rounds'][max(0, r - 1)]
            units = sum(1 for (tt, _) in snap.values() if tt == t)
            h = 64 - units; k = '0-1' if h <= 1 else ('10+' if h >= 10 else None)
            if k is None: continue
            others = [i for i, (tt, b) in snap.items() if tt == t and i != p and len(b) >= 4]
            if not others: continue
            c = acc[k]; c['n'] += 1
            c['par_m'] += m20(p, r); c['oth_m'] += sum(m20(i, r) for i in others) / len(others)
            c['par_len'] += s['before']; c['oth_len'] += sum(len(snap[i][1]) for i in others) / len(others)
            c['par_top'] += m20(p, r) >= max(m20(i, r) for i in others)
for k, c in acc.items():
    n = c['n']; print(k, 'n', n, 'parent meals/20r', round(c['par_m']/n, 2), 'other eligible', round(c['oth_m']/n, 2),
                      'parent len', round(c['par_len']/n, 1), 'others', round(c['oth_len']/n, 1), 'parent is top eater', round(c['par_top']/n, 2))
