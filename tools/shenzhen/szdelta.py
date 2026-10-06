"""H-SZ62: is headroom a proxy for recent losses? Compare, at k=100/200/300, OLS of final share (team A, one row/game) on
share + headroom diff vs share + recent unit-count change diff (U(k)-U(k-20)) vs both. Legal analogue: a dragon can log
get_unit_count each turn."""
import sys, glob, numpy as np
sys.path.insert(0, '/home/claude/fr')
import frame
KS = [100, 200, 300]; W = 20
rows = {k: [] for k in KS}
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        g = frame.decode(f)
        fin = {t: g['final'][t]['total'] for t in 'AB'}
        def U(k, t): return sum(1 for (tt, _) in g['rounds'][k].values() if tt == t)
        for K in KS:
            if K >= len(g['rounds']): continue
            snap = g['rounds'][K]
            L = {t: sum(len(b) for (tt, b) in snap.values() if tt == t) for t in 'AB'}
            s = L['A'] / max(1, L['A'] + L['B'])
            hd = U(K, 'B') - U(K, 'A')
            dd = (U(K, 'A') - U(K - W, 'A')) - (U(K, 'B') - U(K - W, 'B'))
            rows[K].append((s, hd, dd, fin['A'] / max(1, fin['A'] + fin['B'])))
for K in KS:
    R = np.array(rows[K], float); Y = R[:, 3]
    def r2(c):
        X = np.column_stack([np.ones(len(R))] + [R[:, i] for i in c]); b, *_ = np.linalg.lstsq(X, Y, rcond=None)
        return 1 - (Y - X @ b).var() / Y.var(), b
    a, _ = r2([0]); h, bh = r2([0, 1]); d, bd = r2([0, 2]); hdb, bb = r2([0, 1, 2])
    print(f'k={K} n={len(R)} R2 share {a:.3f} +head {h:.3f} +delta{W} {d:.3f} +both {hdb:.3f}  '
          f'coef(both) head {bb[2]:+.4f} delta {bb[3]:+.4f}  corr(head,delta) {np.corrcoef(R[:,1],R[:,2])[0,1]:+.2f}', flush=True)
