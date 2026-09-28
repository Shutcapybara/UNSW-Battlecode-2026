"""Paired seat-B comparison: jet-fw-<host> vs its host on identical fixtures.
usage: wrap_eval.py RESULTS[,RESULTS...]"""
import collections, json, sys
rows = {}
for f in sys.argv[1].split(','):
    for l in open(f):
        r = json.loads(l)
        if 'score' in r: rows[r['key']] = r
HOSTS = {'jet-fw-tidus-t02': 'tidus-t02-spread-only', 'jet-fw-yuna-v02': 'yuna-v02-core', 'jet-fw-bifrost-v29': 'bifrost-v29-tuned-net-growth-farms', 'jet-fw-gavroche-v32': 'gavroche-v32-supported-divecap'}
tot = [0, 0, 0]
for w, h in HOSTS.items():
    per = collections.defaultdict(lambda: [0, 0, 0]); up = dn = 0
    for k, r in rows.items():
        if r['arm'] != w: continue
        c = rows.get(k.replace(w + '|', h + '|', 1))
        if not c: continue
        per[r['map']][0] += r['score']; per[r['map']][1] += c['score']; per[r['map']][2] += 1
        up += r['score'] > c['score']; dn += r['score'] < c['score']
    n = sum(v[2] for v in per.values())
    if not n: continue
    a = sum(v[0] for v in per.values()); b = sum(v[1] for v in per.values())
    tot[0] += a; tot[1] += b; tot[2] += n
    print(f"{w}: wrapped {a:.0f} vs host {b:.0f} of {n} seat-B fixtures (up {up} / down {dn})  " + ', '.join(f"{m} {v[0]:.0f}/{v[1]:.0f}" for m, v in sorted(per.items())))
print('pooled', tot)
