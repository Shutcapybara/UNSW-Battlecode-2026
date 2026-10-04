"""Simulator analogue of corpse2: per bot, share of its corpse pearls (born r150..R-50) eaten by the enemy within 50 rounds;
contact share; wins; total."""
import sys, glob, bisect, collections; sys.path.insert(0, '/home/claude/fr')
import frame
agg = collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(sys.argv[1])):
    parts = f.split('/')[-1][:-7].split('_'); a, b = parts[2], parts[3]
    g = frame.decode(f); W, H, R = g['W'], g['H'], g['last_round']
    cd = lambda p, q: max(min(abs(p[0]-q[0]), W-abs(p[0]-q[0])), min(abs(p[1]-q[1]), H-abs(p[1]-q[1])))
    death = {d['id']: d for d in g['events']['deaths']}
    ctx = {}
    for i, d in death.items():
        r = max(0, min(d['round'], R)); heads = [bb[0] for (tt, bb) in g['rounds'][r].values() if tt != d['team']]
        h = d.get('head'); ctx[i] = h is not None and any(cd(h, x) <= 3 for x in heads)
    ebc = collections.defaultdict(list)
    for e in g['events']['eats']: ebc[tuple(e['cell'])].append((e['round'], e['team']))
    for v in ebc.values(): v.sort()
    for t, bot in (('A', a), ('B', b)):
        c = agg[bot]; c['n'] += 1; c['win'] += g['winner'] == t; c['total'] += g['final'][t]['total']
    for s in g['events']['spawns']:
        side = s['origin']
        if side not in ('A', 'B') or not (150 <= s['round'] <= R - 50): continue
        bot = a if side == 'A' else b; c = agg[bot]; c['born'] += 1; c['contact'] += ctx.get(s.get('donor'), False)
        lst = ebc.get(tuple(s['cell']), []); j = bisect.bisect_left(lst, (s['round'], ''))
        if j < len(lst) and lst[j][0] <= s['round'] + 50 and lst[j][1] != side: c['enemy'] += 1
for k, c in agg.items():
    print(k, dict(n=c['n'], win=c['win'], total=c['total'], born=c['born'], enemy_share=round(c['enemy']/max(1,c['born']),3), contact_share=round(c['contact']/max(1,c['born']),3)))
