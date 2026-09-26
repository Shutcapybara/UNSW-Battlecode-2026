"""Two fresh Godel reserve map families, generated and frozen BEFORE any
screen/sweep outcome is read. Combat-focused topologies distinct from the
Von Neumann reserve:

pincer (28x24, seed 7701): two diagonal kelp walls from opposite corners with
staggered gates; attacks arrive along two lanes at once, so local support and
trade admission decide who gets flanked. Beds trace the diagonals.

fourgates (24x24, seed 5150): a kelp ring around a rich central bed cluster
with four gates; whoever holds the ring interior owns the economy, so
engagements concentrate at the gates. Exercises choke-point trades and the
decision to contest or concede the centre.

Both rotationally mirrored (SYMMETRY xy), no portals (the combat mechanism
under study is independent of portal connectivity).
"""
from pathlib import Path
import random, json, hashlib

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'configs/godel/reserve_maps'
out.mkdir(parents=True, exist_ok=True)
rows = []

for family, W, H, seed in [('pincer', 28, 24, 7701), ('fourgates', 24, 24, 5150)]:
    rng = random.Random(seed)
    mirror = lambda x, y: (W - 1 - x, H - 1 - y)

    def mirrored(k):
        o, x, y = k
        return (0, W - 1 - x, (-y) % H) if o == 0 else (1, (-x) % W, H - 1 - y)

    starts = [[(3, 3), (2, 3), (1, 3)], [(3, H - 4), (2, H - 4), (1, H - 4)]]
    dragons = [(0, starts[0]), (1, [mirror(x, y) for x, y in starts[0]]),
               (0, starts[1]), (1, [mirror(x, y) for x, y in starts[1]])]

    # beds: pincer traces the diagonals; fourgates concentrates in the ring
    tiles = {}
    for y in range(H):
        for x in range(W):
            if family == 'pincer':
                diag = min(abs(x - y * W // H), abs((W - 1 - x) - y * W // H)) <= 2
                gap = (80 if rng.random() < 0.12 else 0) if diag \
                    else (120 if rng.random() < 0.04 else 0)
            else:
                cx, cy = W / 2 - 0.5, H / 2 - 0.5
                r = max(abs(x - cx), abs(y - cy))
                inner = r < W / 4 - 2
                gap = (70 if rng.random() < 0.20 else 0) if inner \
                    else (130 if rng.random() < 0.03 else 0)
            tiles[x, y] = tiles[mirror(x, y)] = (gap, gap)

    overrides = {}
    if family == 'pincer':
        # two diagonal walls, each with two staggered gates
        for wall, off in ((0, 0), (1, 0)):
            for i in range(H):
                x = (i * W // H + off) if wall == 0 else (W - 1 - (i * W // H + off))
                if i % 7 in (3, 4):
                    continue  # gates
                k = (0, x, i)
                overrides.setdefault(k, (1, -1))
                overrides.setdefault(mirrored(k), (1, -1))
    else:
        # square ring with four gates (one per side)
        cx, cy = W / 2 - 0.5, H / 2 - 0.5
        R = W / 4
        for y in range(H):
            for x in range(W):
                if abs(max(abs(x - cx), abs(y - cy)) - R) > 0.6:
                    continue
                gate = (min(abs(x - cx), abs(y - cy)) <= 1.6)
                if gate:
                    continue
                k = (0, x, y)
                overrides.setdefault(k, (1, -1))
                overrides.setdefault(mirrored(k), (1, -1))

    edges = {}
    for o in (0, 1):
        for y in range(H):
            for x in range(W):
                k = (o, x, y)
                if k in edges:
                    continue
                kind = overrides.get(k, (0, -1))
                edges[k] = edges[mirrored(k)] = kind

    name = 'godel_reserve_' + family
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

(ROOT / 'tools/godel/reserve_frozen.json').write_text(json.dumps(
    dict(maps=rows,
         note='Frozen 2026-09-26 before any Godel screen/sweep outcome was read; '
              'no result-driven adaptation. Roster spans four styles (C++ swarm+traps, '
              'French aggression policy, crown-race banker, length banker).'), indent=2) + '\n')
print(json.dumps(rows, indent=2))
