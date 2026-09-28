"""Paired crown-margin comparison (longest own - longest enemy) at given rounds for two arms."""
import json, sys, statistics as st
path, a1, a2 = sys.argv[1], sys.argv[2], sys.argv[3]
R = {}
for f in path.split(','):
    for l in open(f):
        r = json.loads(l)
        if 'score' in r and 'me' in r: R[r['key']] = r
def at(c, rnd):
    v = [x for x in c if x[0] <= rnd]; return v[-1]
rows = []
for k, r in R.items():
    if r['arm'] != a1: continue
    o = R.get(k.replace(a1 + '|', a2 + '|', 1))
    if not o: continue
    row = dict(opp=r['opp'], seat=r['seat'], s1=r['score'], s2=o['score'], t1=r.get('timeouts'), t2=o.get('timeouts'))
    for rnd in (400, 450, 500):
        row[f'm1_{rnd}'] = at(r['me']['curve'], rnd)[3] - at(r['them']['curve'], rnd)[3]
        row[f'm2_{rnd}'] = at(o['me']['curve'], rnd)[3] - at(o['them']['curve'], rnd)[3]
    row['long1'] = at(r['me']['curve'], 500)[3]; row['long2'] = at(o['me']['curve'], 500)[3]
    row['tot1'] = at(r['me']['curve'], 500)[2]; row['tot2'] = at(o['me']['curve'], 500)[2]
    rows.append(row)
print(f'pairs {len(rows)}  W {a1} {sum(r["s1"] for r in rows)}  {a2} {sum(r["s2"] for r in rows)}  flips {sum(r["s1"]!=r["s2"] for r in rows)}')
for rnd in (400, 450, 500):
    d = [r[f'm1_{rnd}'] - r[f'm2_{rnd}'] for r in rows]
    if d: print(f'r{rnd} crown margin {a1[:12]} mean {st.mean(r[f"m1_{rnd}"] for r in rows):+.1f}  {a2[:12]} mean {st.mean(r[f"m2_{rnd}"] for r in rows):+.1f}  paired diff mean {st.mean(d):+.2f} sd {st.pstdev(d):.1f} n {len(d)}')
if rows:
    print('own longest r500 mean', st.mean(r['long1'] for r in rows), st.mean(r['long2'] for r in rows), ' total', st.mean(r['tot1'] for r in rows), st.mean(r['tot2'] for r in rows))
for r in sorted(rows, key=lambda r: (r['opp'], r['seat'])):
    print(f"  {r['opp'][:26]:26s} {r['seat']} W {r['s1']}/{r['s2']} m500 {r['m1_500']:+d}/{r['m2_500']:+d} long {r['long1']}/{r['long2']} tmo {r['t1']}/{r['t2']}")
