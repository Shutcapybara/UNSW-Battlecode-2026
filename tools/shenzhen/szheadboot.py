"""H-SZ59 robustness: one row per game (team A seat only, no symmetric duplicate), game-level bootstrap CI of the
headroom-difference coefficient, plus a leave-one-arm-out sign check. Arms = bot pair parsed from file name."""
import sys, glob, numpy as np, collections
sys.path.insert(0, '/home/claude/fr')
import frame
KS = [100, 200, 300]
rows = {k: [] for k in KS}
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        p = f.split('/')[-1].replace('.replay', '').split('_')
        arm = '-'.join(sorted([p[-3], p[-2]]))
        g = frame.decode(f)
        fin = {t: g['final'][t]['total'] for t in 'AB'}
        for K in KS:
            if K >= len(g['rounds']): continue
            snap = g['rounds'][K]
            L = {t: sum(len(b) for (tt, b) in snap.values() if tt == t) for t in 'AB'}
            U = {t: sum(1 for (tt, _) in snap.values() if tt == t) for t in 'AB'}
            s = L['A'] / max(1, L['A'] + L['B'])
            rows[K].append((arm, s, U['B'] - U['A'], fin['A'] / max(1, fin['A'] + fin['B'])))
rng = np.random.default_rng(0)
def fit(R):
    X = np.array([(1, r[1], r[2]) for r in R], float); Y = np.array([r[3] for r in R], float)
    b, *_ = np.linalg.lstsq(X, Y, rcond=None); return b[2]
for K in KS:
    R = rows[K]; b = fit(R)
    bs = [fit([R[i] for i in rng.integers(0, len(R), len(R))]) for _ in range(2000)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    arms = collections.Counter(r[0] for r in R)
    loo = [fit([r for r in R if r[0] != a]) for a in arms]
    print(f'k={K} games={len(R)} arms={len(arms)} coef={b:+.4f} CI95=[{lo:+.4f},{hi:+.4f}] '
          f'LOO-arm sign neg {sum(c<0 for c in loo)}/{len(loo)}', flush=True)
