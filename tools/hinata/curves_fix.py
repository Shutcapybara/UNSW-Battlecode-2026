"""P-hinata-07 correction: rewrite queen fields (idx 3 alive, 4 length) of build/hinata/curves/g_s*.jsonl using own_s*.jsonl
-> build/hinata/curves2/g_s*.jsonl, and run the engine guard (end queen alive vs final[t]['queen'] > 0)."""
import json
from pathlib import Path
D, O = Path('build/hinata/curves'), Path('build/hinata/curves2'); O.mkdir(exist_ok=True)
own = {r['gid']: r['q'] for q in D.glob('own_s*.jsonl') for r in map(json.loads, open(q))}
stat = dict(games=0, swapped=0, odd=0, guard_n=0, guard_fixed=0, guard_orig=0)
for q in sorted(D.glob('g_s*.jsonl')):
    out = open(O / q.name, 'w')
    for g in map(json.loads, open(q)):
        if 'err' in g: out.write(json.dumps(g) + '\n'); continue
        stat['games'] += 1; Q = own[g['gid']]
        orig = {t: g['c' + t]['end'][3] for t in 'AB'}
        if Q == {'A': 0, 'B': 1}: pass
        elif Q == {'A': 1, 'B': 0}:
            stat['swapped'] += 1
            for r in g['cA']:
                a, b = g['cA'][r], g['cB'].get(r)
                if b is None: continue
                a[3], a[4], b[3], b[4] = b[3], b[4], a[3], a[4]
        else: stat['odd'] += 1; g['queen_err'] = Q
        g['queen_owner'] = Q
        for t in 'AB':
            fq = g['final'][t].get('queen')
            if fq is None: continue
            stat['guard_n'] += 1; e = int(fq > 0)
            stat['guard_fixed'] += (g['c' + t]['end'][3] == e); stat['guard_orig'] += (orig[t] == e)
        out.write(json.dumps(g) + '\n')
print(json.dumps(stat))
