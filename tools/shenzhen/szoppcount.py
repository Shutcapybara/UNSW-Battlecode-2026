"""H-SZ60: union of enemy heads visible to a team (7x7 views around own heads, torus Chebyshev <= 3) vs the opponent's
true unit count, rounds 150..R step 10, simulator replays. Pearson rho pooled and within-game."""
import sys, glob, numpy as np; sys.path.insert(0, '/home/claude/fr'); import frame
xs, ys, within = [], [], []
for f in sorted(glob.glob(sys.argv[1]))[:int(sys.argv[2])]:
    g = frame.decode(f); W, H = g['W'], g['H']; R = len(g['rounds']) - 1
    cd = lambda p, q: max(min(abs(p[0]-q[0]), W-abs(p[0]-q[0])), min(abs(p[1]-q[1]), H-abs(p[1]-q[1])))
    gx, gy = [], []
    for r in range(150, R, 10):
        snap = g['rounds'][r]
        for t, o in (('A', 'B'), ('B', 'A')):
            own = [b[0] for (tt, b) in snap.values() if tt == t]
            enemy = [b[0] for (tt, b) in snap.values() if tt == o]
            seen = sum(1 for e in enemy if any(cd(e, h) <= 3 for h in own))
            gx.append(seen); gy.append(len(enemy))
    if len(gx) > 5 and np.std(gx) > 0 and np.std(gy) > 0: within.append(np.corrcoef(gx, gy)[0, 1])
    xs += gx; ys += gy
xs, ys = np.array(xs), np.array(ys)
print('rows', len(xs), 'pooled rho', round(np.corrcoef(xs, ys)[0, 1], 3), 'median within-game rho', round(float(np.median(within)), 3),
      'mean seen', round(xs.mean(), 1), 'mean true', round(ys.mean(), 1), 'share at true>=60', round(float((ys >= 60).mean()), 2))
