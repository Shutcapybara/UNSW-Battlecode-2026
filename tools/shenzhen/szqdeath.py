"""Queen (ids 0/1) death causes in simulator replays, per bot name from the file name."""
import sys, glob, collections; sys.path.insert(0, '/home/claude/fr'); import frame
c = collections.Counter(); per = collections.defaultdict(collections.Counter)
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        p = f.split('/')[-1][:-7].split('_'); bots = {'A': p[2], 'B': p[3]}
        g = frame.decode(f); r0 = g['rounds'][0]
        dead = {d['id']: d for d in g['events']['deaths']}
        for i in (0, 1):
            if i not in r0: continue
            t = r0[i][0]; b = bots[t]; per[b]['n'] += 1
            d = dead.get(i)
            if d is None: per[b]['alive'] += 1; continue
            kt = 'enemy' if d['killer_team'] and d['killer_team'] != t else ('ally' if d['killer_team'] == t and d['killer'] != i else 'none')
            per[b][f"{d['cause']}/{kt}"] += 1; c[(d['cause'], kt)] += 1
            per[b]['len_at_death'] += d['length']; per[b]['round_at_death'] += d['round']
for b, x in per.items(): print(b, dict(x))
print(c.most_common())
