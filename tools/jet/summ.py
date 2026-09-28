"""Summarise a panel: per-arm score, per map/opp, paired flips vs a control arm."""
import json, sys, collections
out = sys.argv[1]; ctrl = sys.argv[2] if len(sys.argv) > 2 else None
R = [json.loads(l) for l in open(f'{out}/results.jsonl')]
R = {r['key']: r for r in R}
arms = sorted({r['arm'] for r in R.values()})
err = [k for k, r in R.items() if 'error' in r]
print('errors', len(err), err[:5])
for arm in arms:
    rs = [r for r in R.values() if r['arm'] == arm and 'score' in r]
    s = sum(r['score'] for r in rs)
    print(f'{arm:40s} {s:5.1f}/{len(rs):3d} = {s/max(1,len(rs)):.3f}  mean_secs {sum(r["secs"] for r in rs)/max(1,len(rs)):.0f}')
for dim in ('map', 'opp', 'seat'):
    print('--', dim)
    vals = sorted({r[dim] for r in R.values()})
    for v in vals:
        row = []
        for arm in arms:
            rs = [r for r in R.values() if r['arm'] == arm and r[dim] == v and 'score' in r]
            row.append(f'{sum(r["score"] for r in rs):4.1f}/{len(rs):<3d}')
        print(f'{v[:28]:28s}', '  '.join(row))
if ctrl:
    for arm in arms:
        if arm == ctrl: continue
        up = dn = same = 0; lst = []
        for k, r in R.items():
            if r['arm'] != arm or 'score' not in r: continue
            c = R.get(k.replace(arm + '|', ctrl + '|', 1))
            if not c or 'score' not in c: continue
            d = r['score'] - c['score']
            if d > 0: up += 1; lst.append('+' + k)
            elif d < 0: dn += 1; lst.append('-' + k)
            else: same += 1
        print(f'paired {arm} vs {ctrl}: up {up} down {dn} same {same}')
        for x in lst: print('   ', x)
