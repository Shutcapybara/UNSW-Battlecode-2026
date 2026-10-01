"""Verso synthetic training maps: seeded random layouts for data games only (never scored, never a panel).

    .venv/bin/python tools/verso/mapgen.py N [--start 0] [--check]   -> build/verso/maps/vt_<seed>.map

The learned heads must not learn the ten live maps (out-of-sample rule), and the generalisation panel is held out
of every training set, so the data games need layouts of their own. Each map is drawn from independent style
choices — size (16x12 .. 64x36), border (closed / torus / cylinder), walls (open, rooms with doors, maze
corridors, scattered segments), income (uniform slow background, fast clusters, remote clusters, sparse wells,
a belt), portals (0-4 pairs) and spawns (1-6 dragons a side, lengths 3-12) — and is point-symmetric
(SYMMETRY xy: (x, y) <-> (W-1-x, H-1-y)), like every map in the pool. Deterministic per seed; the maps are
regenerated, not committed. --check plays a short game on each map and drops any the engine rejects or corrects.
"""
from __future__ import annotations

import argparse, random, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build' / 'verso' / 'maps'


class Map:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.kelp = set()      # ('h', x, y) north side of tile; ('v', x, y) west side of tile
        self.portal = {}       # edge -> pid
        self.beds = {}         # (x, y) -> (min gap, max gap)
        self.dragons = []      # (team, [(x, y) head first])

    def mt(self, t):
        return (self.W - 1 - t[0], self.H - 1 - t[1])

    def me(self, e):
        k, x, y = e
        if k == 'h':   # north of (x, y) <-> south of mirror tile = north of the tile below it
            return ('h', self.W - 1 - x, (self.H - y) % self.H)
        return ('v', (self.W - x) % self.W, self.H - 1 - y)

    def wall(self, e):
        self.kelp.add(e); self.kelp.add(self.me(e))

    def unwall(self, e):
        self.kelp.discard(e); self.kelp.discard(self.me(e))

    def edge_between(self, a, b):
        """edge crossed stepping from tile a to the orthogonally adjacent tile b (torus)"""
        (ax, ay), (bx, by) = a, b
        if ax == bx:
            return ('h', ax, max(ay, by)) if abs(ay - by) == 1 else ('h', ax, 0)
        return ('v', max(ax, bx), ay) if abs(ax - bx) == 1 else ('v', 0, ay)

    def text(self, name):
        W, H = self.W, self.H
        L = [f'MAP {W} {H}', 'SYMMETRY xy', f'MAP_NAME {name}', f'TILE_COUNT {W * H}']
        for y in range(H):
            for x in range(W):
                mn, mx = self.beds.get((x, y), (0, 0))
                L.append(f'TILE {x} {y} {mn} {mx}')
        E = []
        stride = W + 1
        for (k, x, y) in sorted(self.kelp):
            E.append((((2 * y) if k == 'h' else (2 * y + 1)) * stride + x, 1, -1))
        for (k, x, y), pid in sorted(self.portal.items()):
            E.append((((2 * y) if k == 'h' else (2 * y + 1)) * stride + x, 2, pid))
        L.append(f'EDGE_COUNT {len(E)}')
        L += [f'EDGE {i} {kind} {pid}' for i, kind, pid in sorted(E)]
        L.append(f'DRAGON_COUNT {len(self.dragons)}')
        for team, cells in self.dragons:
            L.append(f'DRAGON {team} {len(cells)} ' + ' '.join(f'{x} {y}' for x, y in cells))
        L.append('END')
        return '\n'.join(L) + '\n'


def gen(seed):
    r = random.Random(1000003 * seed + 17)
    W = r.choice([16, 20, 24, 24, 28, 32, 32, 36, 40, 48, 56, 64])
    H = r.choice([12, 16, 16, 20, 24, 24, 28, 32, 36])
    m = Map(W, H)
    # ---- border
    border = r.choice(['closed', 'closed', 'torus', 'cyl_x', 'cyl_y'])
    if border in ('closed', 'cyl_x'):      # closed top/bottom
        for x in range(W):
            m.wall(('h', x, 0))
    if border in ('closed', 'cyl_y'):
        for y in range(H):
            m.wall(('v', 0, y))
    # ---- walls
    style = r.choice(['open', 'open', 'rooms', 'rooms', 'maze', 'scatter', 'scatter', 'bands'])
    if style == 'rooms':
        rw, rh = r.randint(5, 10), r.randint(4, 8)
        for gx in range(rw, W // 2 + rw, rw):
            for y in range(H):
                if r.random() > 0.22:
                    m.wall(('v', gx % W, y))
        for gy in range(rh, H, rh):
            for x in range(W // 2 + 1):
                if r.random() > 0.22:
                    m.wall(('h', x, gy))
    elif style == 'maze':
        cw = r.choice([2, 3, 3, 4])
        nx, ny = W // cw, H // cw
        seen, stack, open_ = {(0, 0)}, [(0, 0)], set()
        while stack:
            c = stack[-1]
            nb = [(c[0] + dx, c[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= c[0] + dx < nx and 0 <= c[1] + dy < ny and (c[0] + dx, c[1] + dy) not in seen]
            if not nb:
                stack.pop(); continue
            n = r.choice(nb)
            seen.add(n); open_.add((c, n)); open_.add((n, c)); stack.append(n)
        for cx in range(nx):
            for cy in range(ny):
                for (dx, dy) in ((1, 0), (0, 1)):
                    n = (cx + dx, cy + dy)
                    if n[0] >= nx or n[1] >= ny or ((cx, cy), n) in open_ or r.random() < 0.25:
                        continue
                    for i in range(cw):
                        if dx:
                            m.wall(('v', (cx + 1) * cw, cy * cw + i))
                        else:
                            m.wall(('h', cx * cw + i, (cy + 1) * cw))
    elif style == 'scatter':
        for _ in range(r.randint(W * H // 60, W * H // 18)):
            x, y, k, n = r.randrange(W), r.randrange(H), r.choice('hv'), r.randint(2, 7)
            for i in range(n):
                m.wall((k, (x + i) % W, y) if k == 'h' else (k, x, (y + i) % H))
    elif style == 'bands':
        for gy in range(r.randint(3, 6), H, r.randint(4, 8)):
            gaps = {r.randrange(W) for _ in range(r.randint(2, 5))}
            for x in range(W):
                if not any(abs(x - g) <= 1 for g in gaps):
                    m.wall(('h', x, gy))
    # ---- spawns (team 0, mirrored for team 1)
    n_dr = r.choice([1, 2, 2, 3, 3, 4, 6])
    occupied = set()
    for i in range(n_dr):
        ln = r.choice([3, 3, 3, 3, 4, 4, 6, 8, 12]) if i == 0 else r.choice([2, 3, 3, 3, 4])
        for _ in range(400):
            hx, hy = r.randrange(W), r.randrange(H)
            dx, dy = r.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
            cells = [(hx - dx * j, hy - dy * j) for j in range(ln)]   # head first, body trailing behind
            if any(not (0 <= x < W and 0 <= y < H) for x, y in cells):
                continue
            mirror = [m.mt(c) for c in cells]
            if set(cells) & occupied or set(mirror) & occupied or set(cells) & set(mirror):
                continue
            if any(m.edge_between(a, b) in m.kelp for a, b in zip(cells, cells[1:])):
                continue
            if abs(hx - (W - 1 - hx)) + abs(hy - (H - 1 - hy)) < 6:   # not on top of its mirror image
                continue
            occupied |= set(cells) | set(mirror)
            m.dragons.append((0, cells)); m.dragons.append((1, mirror))
            break
    if not m.dragons:
        return None
    heads = [c[0] for t, c in m.dragons if t == 0]
    # ---- income
    def bed(t, gap):
        m.beds[t] = gap; m.beds[m.mt(t)] = gap
    income = r.choice(['uniform', 'clusters', 'clusters', 'remote', 'wells', 'belt', 'mixed', 'mixed'])
    if income in ('uniform', 'mixed'):
        slow = r.choice([(1, 1000), (1, 3849), (1, 769), (1, 2000)])
        for y in range(H):
            for x in range(W):
                if r.random() < r.choice([1.0, 1.0, 0.5]):
                    m.beds[(x, y)] = slow
        for t in list(m.beds):
            m.beds[m.mt(t)] = m.beds[t]
    fast = lambda: r.choice([(1, 50), (1, 255), (10, 34), (10, 30), (25, 50), (5, 20), (1, 385), (40, 80)])
    def cluster(cx, cy, rad, gap, dens=0.8):
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                if r.random() < dens:
                    bed(((cx + dx) % W, (cy + dy) % H), gap)
    if income in ('clusters', 'mixed'):
        for _ in range(r.randint(2, 7)):
            cluster(r.randrange(W), r.randrange(H), r.randint(0, 2), fast())
    if income == 'remote':   # income far from the spawns
        far = sorted(((min(abs(x - hx) + abs(y - hy) for hx, hy in heads), x, y) for x in range(W) for y in range(H)),
                     reverse=True)
        for _ in range(r.randint(2, 5)):
            _, x, y = far[r.randrange(max(1, len(far) // 6))]
            cluster(x, y, r.randint(1, 2), fast())
    if income == 'wells':
        for _ in range(r.randint(3, 10)):
            bed((r.randrange(W), r.randrange(H)), r.choice([(3, 8), (5, 12), (5, 20)]))
    if income == 'belt':
        y0, th = r.randrange(H), r.randint(1, 3)
        for x in range(W):
            for dy in range(th):
                if r.random() < 0.7:
                    bed((x, (y0 + dy) % H), fast())
    if not m.beds:
        cluster(W // 3, H // 3, 1, fast())
    # ---- portals: same-orientation edge pairs, each mirrored to a second pair
    pid = 0
    for _ in range(r.choice([0, 0, 0, 1, 2, 3, 4])):
        k = r.choice('hv')
        e1 = (k, r.randrange(W), r.randrange(H)); e2 = (k, r.randrange(W), r.randrange(H))
        es = [e1, e2, m.me(e1), m.me(e2)]
        if len(set(es)) < 4 or any(e in m.kelp or e in m.portal for e in es):
            continue
        m.portal[e1] = pid; m.portal[e2] = pid
        m.portal[m.me(e1)] = pid + 1; m.portal[m.me(e2)] = pid + 1
        pid += 2
    desc = f'{W}x{H} {border} {style} {income} dragons={n_dr} portals={pid}'
    return m, desc


def check(path):
    """a short real game; reject on any engine error or map correction"""
    exe = str(Path(sys.executable).parent / 'unswbc')
    p = subprocess.run([exe, 'run', '--seed', '1', '--no-logs', '--no-indicator', '--no-draw', '--no-replay', '-v',
                        str(path), 'bots/verso-00-base', 'bots/verso-00-base'],
                       capture_output=True, text=True, cwd=ROOT, timeout=900)
    out = p.stdout + p.stderr
    bad = p.returncode != 0 or 'defect' in out or 'error' in out.lower()
    return not bad, out[-300:] if bad else ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('n', type=int); ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    made, seed = 0, a.start
    while made < a.n and seed < a.start + 20 * a.n:
        g = gen(seed)
        seed += 1
        if g is None:
            continue
        m, desc = g
        name = f'vt_{seed - 1}'
        path = OUT / f'{name}.map'
        path.write_text(m.text(name))
        if a.check:
            ok, why = check(path)
            if not ok:
                print(name, 'REJECTED', desc, '|', why.replace('\n', ' / ')[-200:], flush=True)
                path.unlink()
                continue
        made += 1
        print(name, desc, flush=True)


if __name__ == '__main__':
    main()
