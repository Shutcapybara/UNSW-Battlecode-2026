"""H-SZ68: how deterministic is the teacher (carthage-05 family) given only its local view? For every single-step move
by a dragon of length >= 2, build an egocentric key (rotated so heading = up) from the (2r+1)^2 window around the
head: per cell {empty, own body, ally body, ally head, enemy body, enemy head} x pearl, plus passability of F/R/L and
a length bucket. Report, for keys seen >= 5 times, the share of rows whose action equals the key's majority action
(an upper bound on any local-view classifier's accuracy on those states, up to sampling)."""
import sys, glob, collections
sys.path.insert(0, '/home/claude/fr')
import frame
DX, DY = (0, 1, 0, -1), (-1, 0, 1, 0)
cnt = {r: collections.defaultdict(collections.Counter) for r in (1, 2, 3)}
test = []
gi = 0
lab = collections.Counter()
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        gi += 1; tr = gi % 2 == 1
        g = frame.decode(f); W, H, nbr, R, P = g['W'], g['H'], g['nbr'], g['rounds'], g['pearls']
        for e in g['events']['actions']:
            if e['kind'] != 'move' or e['steps'] != 1: continue
            r, i = e['round'], e['id']
            if r + 1 >= len(R) or i not in R[r]: continue
            t, b = R[r][i]
            if len(b) < 2: continue
            (hx, hy), (nx, ny) = b[0], b[1]
            ddx, ddy = (hx - nx + 1) % W - 1, (hy - ny + 1) % H - 1
            if (ddx, ddy) not in list(zip(DX, DY)): continue
            h = list(zip(DX, DY)).index((ddx, ddy)); d = e['dirs'][0]
            rel = (d - h) % 4
            if rel == 2: continue
            a = 'FRxL'[rel]
            occ = {}
            for j, (tt, bb) in R[r].items():
                for k, c in enumerate(bb):
                    occ[c] = 1 if j == i else (2 if tt == t else 4) + (k == 0)
            pear = P[r] if r < len(P) else frozenset()
            pas = tuple(nbr[b[0]][(h + q) % 4] is not None for q in (0, 1, 3))
            lb = min(len(b), 12) // 3
            keys = {}
            for rad in (1, 2, 3):
                key = []
                for u in range(-rad, rad + 1):          # u: forward/back, v: right/left in egocentric frame
                    for v in range(-rad, rad + 1):
                        fx, fy = DX[h], DY[h]; rx, ry = DX[(h + 1) % 4], DY[(h + 1) % 4]
                        c = ((hx - u * fx + v * rx) % W, (hy - u * fy + v * ry) % H)
                        key.append(occ.get(c, 0) * 2 + (c in pear))
                keys[rad] = (tuple(key), pas, lb)
                if tr: cnt[rad][keys[rad]][a] += 1
            if tr: lab[a] += 1
            else: test.append((keys, a))
n = sum(lab.values())
print('train rows', n, 'test rows', len(test), 'label shares', {k: round(v / n, 3) for k, v in lab.items()})
for MIN in (5, 20):
    for rad in (1, 2, 3):
        hit = cov = 0
        for keys, a in test:
            c = cnt[rad].get(keys[rad])
            if c and sum(c.values()) >= MIN:
                cov += 1; hit += c.most_common(1)[0][0] == a
        print(f'min{MIN} window {2*rad+1}: test coverage {cov/len(test):.1%}, held-out lookup accuracy on covered {hit/max(1,cov):.3f}')
    hit = 0; used = collections.Counter()
    for keys, a in test:
        p = 'F'
        for rad in (3, 2, 1):
            c = cnt[rad].get(keys[rad])
            if c and sum(c.values()) >= MIN: p = c.most_common(1)[0][0]; used[rad] += 1; break
        hit += p == a
    print(f'min{MIN} backoff 7->5->3->F held-out accuracy on ALL test rows: {hit/len(test):.3f}  levels used {dict(used)}')
