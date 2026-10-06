"""H-SZ59 sim check: does the team unit-headroom difference at round k add to current length share in predicting the
final total share? OLS per k over simulator replays (two symmetric rows per game)."""
import sys, glob, numpy as np
sys.path.insert(0, '/home/claude/fr')
import frame

KS = [100, 200, 300]
X = {k: [] for k in KS}
Y = {k: [] for k in KS}
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        g = frame.decode(f)
        fin = {t: g['final'][t]['total'] for t in 'AB'}
        for K in KS:
            if K >= len(g['rounds']):
                continue
            snap = g['rounds'][K]
            L = {t: sum(len(b) for (tt, b) in snap.values() if tt == t) for t in 'AB'}
            U = {t: sum(1 for (tt, _) in snap.values() if tt == t) for t in 'AB'}
            for t, o in (('A', 'B'), ('B', 'A')):
                s = L[t] / max(1, L[t] + L[o])
                hd = (64 - U[t]) - (64 - U[o])
                X[K].append((1.0, s, hd))
                Y[K].append(fin[t] / max(1, fin[t] + fin[o]))
for K in KS:
    Xk = np.array(X[K], float); Yk = np.array(Y[K], float)

    def r2(cols):
        A = Xk[:, cols]
        b, *_ = np.linalg.lstsq(A, Yk, rcond=None)
        res = Yk - A @ b
        return 1 - res.var() / Yk.var(), b

    ra, _ = r2([0, 1]); rb, bb = r2([0, 1, 2])
    print(f'k={K} n={len(Yk)} R2 share-only {ra:.3f}  +headroom-diff {rb:.3f}  coef headroom {bb[2]:+.4f} per slot', flush=True)
