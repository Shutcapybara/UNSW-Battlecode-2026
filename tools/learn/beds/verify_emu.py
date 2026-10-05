"""Check the pure-Python bed emulator (emu.schedule: mt19937_64(seed), countdown = lo + u % (hi-lo+1), pairs drawn in
row-major order of their first cell at round -1 and on each expiry) against the official engine's countdown events.
Probe map = the template's beds, no walls, dragons vertical in bed-free columns moving N (they live 500 rounds; the
schedule does not depend on play). Run from the repo root where unswbc imports:  python tools/learn/beds/verify_emu.py"""
import os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, 'tools/learn')
import oracle, rebuild, emu

def probe_map(text, beds, dcols):
    out = []; k = 0
    for l in text.splitlines():
        p = l.split()
        if not p: continue
        if p[0] == 'EDGE': l = f'EDGE {p[1]} 0 -1'
        elif p[0] == 'TILE':
            c = (int(p[1]), int(p[2])); lo, hi = beds.get(c, (0, 0)); l = f'TILE {c[0]} {c[1]} {lo} {hi}'
        elif p[0] == 'DRAGON':
            x = dcols[k]; k += 1; n = int(p[2]); l = f'DRAGON {p[1]} {n} ' + ' '.join(f'{x} {y}' for y in range(n))
        out.append(l)
    return '\n'.join(out) + '\n'

def engine_expiries(text, seed):
    E = oracle._engine(); res = E.run(text.encode(), lambda d, raw: b'MOVE N\nENDTURN\n', debug=0, seed=seed)
    r = rebuild.reader(E.replay('A', 'B')); root = r.object(0, 0); rnd = -1; exp = collections.defaultdict(list)
    for e in root.items(3):
        k = e.num(0, 'H'); o = e.child(0)
        if k == 0: rnd = o.num()
        elif k == 2: exp[(o.child(0).num(), o.child(0).num(4))].append(rnd + o.num(0))
    return exp, res.rounds

if __name__ == '__main__':
    for f in sorted(glob.glob('maps/live/*.map')) + sorted(glob.glob('maps/live_var/*.map')):
        t = open(f).read(); m = rebuild.Map(t); beds = {c: v for c, v in m.tiles.items() if v[1] > 0}
        free = [x for x in range(m.W) if all((x, y) not in beds for y in range(m.H))]
        if not beds or len(free) < len(m.dragons):
            print(f, 'skipped (no free columns for the probe dragons)'); continue
        for s in (12345, 0xb86755d70df234ca):
            eng, rounds = engine_expiries(probe_map(t, beds, free[:len(m.dragons)]), s)
            P, out = emu.schedule(beds, m.W, m.H, m.symmetry, s)
            bad = sum(1 for c, p in P for q in (c, p) if [x for x in eng[q] if x <= rounds] != [x for x in out[c] if x <= rounds])
            print(f, hex(s), 'pairs', len(P), 'rounds', rounds, 'cells differing', bad)
