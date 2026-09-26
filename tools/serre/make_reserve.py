"""Two fresh Serre reserve map families, generated and frozen BEFORE any
serre screen/gauntlet outcome is read. Serre studies grafted mechanisms on a
sinbad-e23 foundation, so the reserve targets the foundation's measured leaks
rather than one combat surface:

twinlakes (30x22, seed 6209): open water with two mirrored rich bed clusters
off-centre and sparse slow beds elsewhere; no walls, no portals. Tests
sustained resource acquisition, spatial distribution of collectors, and the
expansion -> longest-dragon endgame transition without terrain excuses.

crossfire (26x26, seed 8864): a central horizontal band of fast beds
(every-round and 30-round) flanked by two staggered kelp walls, plus one
portal pair whose two ends are mutual 180-degree mirrors (a dive near home
lands near the enemy spawn). Tests the foundation's documented devil leak
(contested central fast beds), choke-point survival, and portal-exit risk.

Both rotationally mirrored (SYMMETRY xy). Map format follows
tools/godel/make_reserve.py: TILE x y countdown period; EDGE kind 0 open,
1 wall, 2 portal with p = pair id.
"""
from pathlib import Path
import random, json, hashlib

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'configs/serre/reserve_maps'
out.mkdir(parents=True, exist_ok=True)
rows = []

for family, W, H, seed in [('twinlakes', 30, 22, 6209), ('crossfire', 26, 26, 8864)]:
    rng = random.Random(seed)
    mirror = lambda x, y: (W - 1 - x, H - 1 - y)

    def mirrored(k):
        o, x, y = k
        return (0, W - 1 - x, (-y) % H) if o == 0 else (1, (-x) % W, H - 1 - y)

    starts = [[(3, 3), (2, 3), (1, 3)], [(3, H - 4), (2, H - 4), (1, H - 4)]]
    dragons = [(0, starts[0]), (1, [mirror(x, y) for x, y in starts[0]]),
               (0, starts[1]), (1, [mirror(x, y) for x, y in starts[1]])]

    tiles = {}
    overrides = {}
    if family == 'twinlakes':
        # two mirrored lakes of mixed-period beds; sparse slow beds elsewhere
        cx, cy = W // 4, H // 2
        for y in range(H):
            for x in range(W):
                d = max(abs(x - cx), abs(y - cy))
                if d <= 2:
                    period = 30 if d <= 1 else 150
                    tiles[x, y] = tiles[mirror(x, y)] = (1, period)
                elif rng.random() < 0.03:
                    tiles[x, y] = tiles[mirror(x, y)] = (600, 600)
                else:
                    tiles[x, y] = tiles[mirror(x, y)] = (0, 0)
    else:
        # central fast-bed band (devil-style leak surface)
        band = range(H // 2 - 2, H // 2 + 2)
        for y in range(H):
            for x in range(W):
                if y in band and x % 3 != 2:
                    period = 1 if y in (H // 2 - 1, H // 2) else 30
                    tiles[x, y] = tiles[mirror(x, y)] = (1, period)
                elif rng.random() < 0.04:
                    tiles[x, y] = tiles[mirror(x, y)] = (300, 300)
                else:
                    tiles[x, y] = tiles[mirror(x, y)] = (0, 0)
        # two staggered kelp walls above/below the band, gates offset
        for row, par in ((H // 2 - 3, 0), (H // 2 + 2, 1)):
            for x in range(1, W - 1):
                if x % 6 in ((3, 4) if par == 0 else (0, 1)):
                    continue  # gates
                k = (0, x, row)
                overrides.setdefault(k, (1, -1))
                overrides.setdefault(mirrored(k), (1, -1))
        # one portal pair: left flank <-> its 180-degree mirror (right flank)
        k = (1, 2, H // 2 - 1)
        overrides[k] = (2, 0)
        overrides[mirrored(k)] = (2, 0)

    edges = {}
    for o in (0, 1):
        for y in range(H):
            for x in range(W):
                k = (o, x, y)
                if k in edges:
                    continue
                kind = overrides.get(k, (0, -1))
                edges[k] = edges[mirrored(k)] = kind

    name = 'serre_reserve_' + family
    lines = [f'MAP {W} {H}', 'SYMMETRY xy', f'MAP_NAME {name}', f'TILE_COUNT {W*H}']
    lines += [f'TILE {x} {y} {a} {b}' for (x, y), (a, b) in sorted(tiles.items())]
    lines += [f'EDGE_COUNT {2*W*H}']
    lines += [f'EDGE {(2*y+o)*(W+1)+x} {kind} {p}' for (o, x, y), (kind, p) in sorted(edges.items())]
    lines += ['DRAGON_COUNT 4'] + ['DRAGON ' + str(team) + ' 3 ' + ' '.join(f'{x} {y}' for x, y in body)
                                   for team, body in dragons] + ['END']
    p = out / (name + '.map')
    p.write_text('\n'.join(lines) + '\n')
    rows.append(dict(name=name, family=family, seed=seed, size=[W, H],
                     sha256=hashlib.sha256(p.read_bytes()).hexdigest()))

(ROOT / 'tools/serre/reserve_frozen.json').write_text(json.dumps(
    dict(maps=rows,
         note='Frozen 2026-09-26 before any Serre screen/gauntlet outcome was read; '
              'no result-driven adaptation. Roster spans four styles (compact production '
              'ladder, arrival economy, crown-race banker, French density radio).'), indent=2) + '\n')
print(json.dumps(rows, indent=2))
