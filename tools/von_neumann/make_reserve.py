"""Two fresh Von Neumann reserve map families, generated and frozen BEFORE any
screen/sweep outcome is read. Combat-focused topologies:

corridor_clash (26x26, seed 4242): two horizontal kelp bands and one vertical
band with staggered gates funnel movement through shared choke points into an
open central plaza; beds line the corridors. Exercises contact frequency,
trade admission at choke points and push/withdraw through gates.

open_field (32x20, seed 9090): near-open water with small kelp clumps and a
rich contested bed band along the mid-line. Exercises long chases, sprint
trades and centre contesting on open ground.

Both rotationally mirrored (SYMMETRY xy), no portals (the combat mechanism
under study is independent of portal connectivity).
"""
from pathlib import Path
import random, json, hashlib

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'configs/von_neumann/reserve_maps'
out.mkdir(parents=True, exist_ok=True)
rows = []

for family, W, H, seed in [('corridor_clash', 26, 26, 4242), ('open_field', 32, 20, 9090)]:
    rng = random.Random(seed)
    mirror = lambda x, y: (W - 1 - x, H - 1 - y)

    def mirrored(k):
        o, x, y = k
        return (0, W - 1 - x, (-y) % H) if o == 0 else (1, (-x) % W, H - 1 - y)

    starts = [[(3, 3), (2, 3), (1, 3)], [(3, H - 4), (2, H - 4), (1, H - 4)]]
    dragons = [(0, starts[0]), (1, [mirror(x, y) for x, y in starts[0]]),
               (0, starts[1]), (1, [mirror(x, y) for x, y in starts[1]])]

    # beds: corridor_clash lines the corridors; open_field concentrates a
    # contested mid band, sparse elsewhere
    tiles = {}
    for y in range(H):
        for x in range(W):
            if (x, y) in tiles:
                continue
            if family == 'corridor_clash':
                plaza = W // 3 <= x < 2 * W // 3 and H // 3 <= y < 2 * H // 3
                gap = 60 if (plaza and rng.random() < 0.10) else (110 if rng.random() < 0.06 else 0)
            else:
                mid = abs(((y + H // 2) % H) - H // 2) <= 1
                gap = (90 if rng.random() < 0.16 else 140 if rng.random() < 0.05 else 0) if mid \
                    else (130 if rng.random() < 0.04 else 0)
            tiles[x, y] = tiles[mirror(x, y)] = (gap, gap)

    overrides = {}
    if family == 'corridor_clash':
        bands = [H // 3, 2 * H // 3]
        for line in bands:
            for o in (0, 1):
                n = (W if o == 0 else H)
                for i in range(n):
                    # staggered gates: horizontal bands gate every 5, the
                    # vertical band every 6, offsets differ so paths cross
                    if i % 5 in (2, 3):
                        continue
                    k = (o, i, line) if o == 0 else (o, line, i)
                    overrides.setdefault(k, (1, -1))
                    overrides.setdefault(mirrored(k), (1, -1))
        vline = W // 2
        for i in range(H):
            if i % 6 in (2, 3):
                continue
            k = (1, vline, i)
            overrides.setdefault(k, (1, -1))
            overrides.setdefault(mirrored(k), (1, -1))
    else:  # open_field: four small clumps of kelp, mirrored
        for cx, cy in [(6, 5), (W - 7, H - 6)]:
            for _ in range(6):
                x, y = cx + rng.randrange(3), cy + rng.randrange(3)
                for o in (0, 1):
                    overrides.setdefault((o, x, y), (1, -1))
                    overrides.setdefault(mirrored((o, x, y)), (1, -1))

    edges = {}
    for o in (0, 1):
        for y in range(H):
            for x in range(W):
                k = (o, x, y)
                if k in edges:
                    continue
                kind = overrides.get(k, (0, -1))
                edges[k] = edges[mirrored(k)] = kind

    name = 'vn_reserve_' + family
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

(ROOT / 'tools/von_neumann/reserve_frozen.json').write_text(json.dumps(
    dict(maps=rows,
         note='Frozen 2026-09-26 before any screen/sweep outcome of this study was read; '
              'no result-driven adaptation. Roster spans four styles to break the '
              'sinbad/hunter/drake trio correlation.'), indent=2) + '\n')
(ROOT / 'configs/von_neumann/reserve.toml').write_text(
    '# Fresh reserve: two combat-focused families vs four stylistically varied\n'
    '# references, both sides = 16 games. Maps frozen before outcomes were read.\n'
    'bots = ["../../bots/hunter-v20-portal-scouts", "../../bots/ouroboros-v13-ladder",\n'
    '        "../../bots/avery-v08-crown-race", "../../bots/sinbad-v06-arrival"]\n'
    'maps = ["reserve_maps"]\n[run]\nsides = ["A", "B"]\njobs = 2\ntimeout_seconds = 600\n'
    'sandbox = false\ncontrol_every = 25\n')
print(json.dumps(rows, indent=2))
