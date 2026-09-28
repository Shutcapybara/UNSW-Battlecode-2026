#!/usr/bin/env python3
"""Map transforms for extra independent fixtures: mx (mirror x), my (mirror y), tr (transpose).
python3 transform_map.py IN OUT mx|my|tr[,..]
Edge index: stride W+1; row 2y = north edge of (col, y); row 2y+1 = west edge of (col, y)."""
import sys


def parse(text):
    lines = text.splitlines()
    W, H = map(int, lines[0].split()[1:3])
    return lines, W, H


def apply(text, op):
    lines, W, H = parse(text)
    nW, nH = (H, W) if op == 'tr' else (W, H)

    def cell(x, y):
        if op == 'mx': return (W - 1 - x, y)
        if op == 'my': return (x, H - 1 - y)
        return (y, x)

    def edge(kind, x, y):  # kind 'n' north of (x,y) / 'w' west of (x,y) -> new (kind, x, y)
        if op == 'mx':
            return ('n', W - 1 - x, y) if kind == 'n' else ('w', (W - x) % W, y)
        if op == 'my':
            return ('n', x, (H - y) % H) if kind == 'n' else ('w', x, H - 1 - y)
        return ('w', y, x) if kind == 'n' else ('n', y, x)

    out = []
    edges = {}
    for l in lines:
        p = l.split()
        if not p:
            continue
        if p[0] == 'MAP':
            out.append(f'MAP {nW} {nH}')
        elif p[0] == 'SYMMETRY' and op == 'tr':
            out.append('SYMMETRY ' + ''.join(sorted(p[1].translate(str.maketrans('xy', 'yx')))))
        elif p[0] == 'MAP_NAME':
            out.append(l + ' ' + op)
        elif p[0] == 'TILE':
            x, y = cell(int(p[1]), int(p[2]))
            out.append(f'TILE {x} {y} ' + ' '.join(p[3:]))
        elif p[0] == 'EDGE':
            idx = int(p[1]); col, row = idx % (W + 1), idx // (W + 1)
            kind = 'n' if row % 2 == 0 else 'w'
            k, x, y = edge(kind, col, row // 2)
            nidx = (2 * y + (0 if k == 'n' else 1)) * (nW + 1) + x
            edges[nidx] = f'EDGE {nidx} {p[2]} {p[3]}'
        elif p[0] == 'DRAGON':
            team, n = p[1], int(p[2])
            pts = [cell(int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n)]
            out.append(f'DRAGON {team} {n} ' + ' '.join(f'{a} {b}' for a, b in pts))
        elif p[0] == 'EDGE_COUNT':
            out.append('__EDGES__')
        else:
            out.append(l)
    i = out.index('__EDGES__')
    out[i:i + 1] = [f'EDGE_COUNT {len(edges)}'] + [edges[k] for k in sorted(edges)]
    tiles = [l for l in out if l.startswith('TILE ')]
    rest = [l for l in out if not l.startswith('TILE ')]
    tiles.sort(key=lambda l: (int(l.split()[2]), int(l.split()[1])))
    j = next(k for k, l in enumerate(rest) if l.startswith('TILE_COUNT'))
    return '\n'.join(rest[:j + 1] + tiles + rest[j + 1:]) + '\n'


if __name__ == '__main__':
    t = open(sys.argv[1]).read()
    for op in sys.argv[3].split(','):
        t = apply(t, op)
    open(sys.argv[2], 'w').write(t)
