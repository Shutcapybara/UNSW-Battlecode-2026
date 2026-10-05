"""H-SZ65: does a 4-ray sonar echo (legal: counts per kind, no distance) add threat information beyond the 7x7 view?
For each alive dragon every 5 rounds (r>=30): view features (enemy heads / enemy body cells within Chebyshev 3, wrap)
and a virtual N/E/S/W cast from the head over the round snapshot (stops at kelp/wall edge or a dragon cell, max W+H,
own-body first-step skipped). Label: the dragon dies within the next 10 rounds (any cause) / by h2h or body."""
import sys, glob, numpy as np, collections
sys.path.insert(0, '/home/claude/fr')
import frame
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
rows = []
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        g = frame.decode(f); W, H, nbr = g['W'], g['H'], g['nbr']
        death = {}
        for d in g['events']['deaths']:
            death[d['id']] = (d['round'], d['cause'])
        R = g['rounds']
        for r in range(30, len(R) - 10, 5):
            snap = R[r]
            occ = {}
            for i, (t, b) in snap.items():
                for j, c in enumerate(b):
                    occ[c] = (i, t, j == 0)
            for i, (t, b) in snap.items():
                hx, hy = b[0]
                eh = eb = 0
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        o = occ.get(((hx + dx) % W, (hy + dy) % H))
                        if o and o[1] != t:
                            if o[2]: eh += 1
                            else: eb += 1
                ray = collections.Counter(); dmin = 99
                for d in range(4):
                    c = b[0]
                    for step in range(W + H):
                        c = nbr[c][d]
                        if c is None: ray['kelp'] += 1; break
                        o = occ.get(c)
                        if o:
                            if o[0] == i and step == 0: break
                            k = ('enemy' if o[1] != t else 'ally') + ('_head' if o[2] else '')
                            ray[k] += 1
                            if k == 'enemy_head': dmin = min(dmin, step + 1)
                            break
                dr = death.get(i)
                y = int(dr is not None and r < dr[0] <= r + 10)
                yc = int(y and dr[1] in ('h2h', 'body'))
                rows.append((eh, eb, ray['enemy_head'], ray['enemy'], ray['ally_head'] + ray['ally'], ray['kelp'],
                             len(b), dmin, y, yc, len(rows) and hash(f) % 100000))
A = np.array(rows, float)
print('rows', len(A), 'death10 rate', A[:, 8].mean().round(4), 'contact', A[:, 9].mean().round(4))
for lab, col in (('any', 8), ('contact', 9)):
    y = A[:, col]
    sets = {'len': [6], 'view': [0, 1, 6], 'view+echo': [0, 1, 2, 3, 4, 5, 6], 'echo only': [2, 3, 4, 5, 6]}
    for name, c in sets.items():
        X = A[:, c]; ntr = int(len(X) * 0.6)
        m = LogisticRegression(max_iter=500).fit(X[:ntr], y[:ntr])
        print(f'{lab:8s} {name:10s} AUC(test) {roc_auc_score(y[ntr:], m.predict_proba(X[ntr:])[:, 1]):.4f}')
blind = A[A[:, 0] == 0]
for k in (0, 1, 2):
    s = blind[np.minimum(blind[:, 2], 2) == k]
    print(f'no enemy head in view, echo enemy_head={k}{"+" if k==2 else ""}: n={len(s)} death10 {s[:,8].mean():.4f} contact {s[:,9].mean():.4f}')
