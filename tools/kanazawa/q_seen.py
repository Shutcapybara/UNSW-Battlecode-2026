"""Kanazawa unit 12, blue-sky H-KZ28 (frozen 08:58Z): strikers act on their own vision (Chebyshev 3 from head).
For the 24 unit-11 strike cases: Chebyshev distance killer head -> queen head at R[dr-2], R[dr-1], R[dr]; and whether
ANY enemy head saw the queen head at R[dr-1]. Supported (0.5) if the killer saw the queen at R[dr] in >= 16/20 and
first saw it within <= 2 rounds of the strike in >= 10/20; refuted (0.1) if the killer could not see the queen at R[dr]
in >= 6/20 (then strikers use shared info: sonar or other)."""
import json, sys
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
from tools.kanazawa.q_cycle import CORPUS
from tools.kanazawa.q_avoid import cheb
from tools.analysis.features.frame import decode
from collections import Counter
src = ROOT / 'build/kanazawa/tree/docs/findings/kanazawa-data/unit11-q_h2h.txt'; c = Counter()
for line in open(src):
    if not line.startswith('{'): continue
    r = json.loads(line)
    if not ((r.get('kdist') or 0) >= 2 and r.get('kdied')): continue
    g = decode(str(CORPUS / 'replays' / f"{r['gid']}.replay")); R = g['rounds']; dr = r['r']; W, H = g['W'], g['H']
    qs = [e for e in g['events']['deaths'] if e['round'] == dr and e['cause'] == 'h2h' and e['id'] <= 1]
    for d in qs:
        q, k = d['id'], d.get('killer'); side = R[0][q][0]
        if k not in R[dr]: continue
        seq = []
        for t in range(max(0, dr - 6), dr + 1):
            seq.append(cheb(R[t][k][1][0], R[t][q][1][0], W, H) if (k in R[t] and q in R[t]) else None)
        anyE = int(any(cheb(bb[0], R[dr-1][q][1][0], W, H) <= 3 for i, (tm, bb) in R[dr-1].items() if tm != side)) if q in R[dr-1] else None
        first = None
        for j in range(len(seq) - 1, -1, -1):
            if seq[j] is not None and seq[j] <= 3: first = len(seq) - 1 - j
            else: break
        print(json.dumps(dict(who=r['who'], gid=r['gid'], r=dr, cheb_seq=seq, killer_sees_now=int(seq[-1] is not None and seq[-1] <= 3), seen_run=first, anyE_prev=anyE)))
        if r['who'] == 'us':
            c['n'] += 1; c['sees_now'] += seq[-1] is not None and seq[-1] <= 3; c['seen<=2rounds'] += first is not None and first <= 2
            c['anyE_prev'] += bool(anyE)
        break
print(dict(c))
