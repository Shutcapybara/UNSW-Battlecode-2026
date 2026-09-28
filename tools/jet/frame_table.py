"""Wins per (map, seat, frame) from panel results; v32 rows count as frame id.
usage: frame_table.py RESULTS[,RESULTS...]"""
import collections, json, sys
T = collections.defaultdict(lambda: collections.defaultdict(float)); N = collections.defaultdict(lambda: collections.defaultdict(int))
for f in sys.argv[1].split(','):
    for l in open(f):
        r = json.loads(l)
        if 'score' not in r: continue
        a = r['arm']
        fr = 'id' if a.startswith('gavroche-v32') else (a.split('jet-f32-')[1] if a.startswith('jet-f32-') else None)
        if fr is None: continue
        T[(r['map'], r['seat'])][fr] += r['score']; N[(r['map'], r['seat'])][fr] += 1
F = ['id', 'fx', 'fy', 'r']
print('map seat ' + ' '.join(F) + '  (n per cell)')
tot = collections.Counter(); best = collections.Counter()
for k in sorted(T):
    row = T[k]; print(f"{k[0][:14]:14s} {k[1]} " + ' '.join(f"{row.get(f, float('nan')):4.1f}" for f in F) + '  ' + ' '.join(str(N[k].get(f, 0)) for f in F))
    for f in F: tot[f] += row.get(f, 0)
    best['max'] += max(row.get(f, 0) for f in F)
print('total', dict(tot), 'oracle', best['max'])
