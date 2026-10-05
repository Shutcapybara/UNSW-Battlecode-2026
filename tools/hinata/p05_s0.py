"""P-hinata-05 (P-9) S0, amended 2026-10-05 08:37Z: spell-level rows from bokuto-13-cull pool frames.
Cull signature: own self-death, length 2, id>1, round 60-340, team units >= limit-1, round = 3*id (mod 8).
Unit = per-dragon eligibility spell on the turn-start-legal superset; instrument D = (3*id - r0) mod 8.
Training maps only (Autarky, Maze, Trauma dropped by file name). Stdlib only. Usage: p05_s0.py FRAMES_DIR OUT_CSV"""
import csv, gzip, os, pickle, sys
HELD = ('autarky', 'maze', 'trauma'); LIMIT = 64; VR = 3; BOT = 'bokuto-13-cull'

def rows_for(path):
    fr = pickle.load(gzip.open(path)); W, H = fr['W'], fr['H']
    me = 'A' if BOT in fr['botA'] else 'B'
    opp = (fr['botB'] if me == 'A' else fr['botA']).split('/')[-1]
    rs, pe = fr['rounds'], fr['pearls']; last = len(rs) - 1
    U = [sum(1 for t, b in s.values() if t == me) if s else 0 for s in rs]
    L = [sum(len(b) for t, b in s.values() if t == me) if s else 0 for s in rs]
    death = {}
    for d in fr['events']['deaths']:
        if d['team'] == me: death[d['id']] = d
    def wd(a, b, n): a = abs(a - b); return min(a, n - a)
    def elig(r, i, body):
        if i <= 1 or len(body) != 2 or U[r] < LIMIT - 1 or not 60 <= r <= 340: return False
        hx, hy = body[0]
        for (px, py) in pe[r]:
            if wd(px, hx, W) <= VR and wd(py, hy, H) <= VR: return False
        return True
    def enemy_near(r, body, R=20):
        hx, hy = body[0]
        return int(any(t != me and wd(b[0][0], hx, W) + wd(b[0][1], hy, H) <= R for t, b in rs[r].values()))
    out, open_ = [], {}
    for r in range(60, min(341, last + 1)):
        s = rs[r]
        for i, (t, body) in s.items():
            if t != me: continue
            e = elig(r, i, body)
            if e and i not in open_: open_[i] = [r, r, body]
            elif e: open_[i][1] = r
        for i in list(open_):
            r0, r1, b0 = open_[i]
            if r1 == r and r < min(340, last) and i in rs[r + 1] and r + 1 <= 340: continue
            del open_[i]
            d = death.get(i); culled = int(d is not None and d['cause'] == 'self' and r0 <= d['round'] <= r1 + 0 and (d['round'] - 3 * i) % 8 == 0)
            g = lambda k: L[min(r0 + k, last)] - L[r0]
            h = lambda k: U[min(r0 + k, last)] - U[r0]
            out.append(dict(game=os.path.basename(path).split('.')[0], map=fr['map'], opp=opp, seat=me, id=i, r0=r0, r1=r1,
                            spell=r1 - r0 + 1, D=(3 * i - r0) % 8, culled=culled, cull_round=d['round'] if culled else -1,
                            died_other=int(d is not None and not culled and r0 <= d['round'] <= r1),
                            enemy20=enemy_near(r0, b0), L0=L[r0], U0=U[r0], dL20=g(20), dL50=g(50), dU20=h(20), dU50=h(50),
                            win=int(fr['winner'] == me)))
    return out

if __name__ == '__main__':
    D, out = sys.argv[1], sys.argv[2]
    fs = sorted(f for f in os.listdir(D) if f.endswith('.pkl.gz') and not any(m in f.lower() for m in HELD))
    rows = []
    for f in fs: rows += rows_for(os.path.join(D, f))
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(len(fs), 'games', len(rows), 'spells')
