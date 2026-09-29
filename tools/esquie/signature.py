"""Structural signature of a map: the observable geometry that makes it what it
is, independent of its name (M-1 Part 1).

    python -m tools.esquie.signature maps/devil.map          # one vector
    python -m tools.esquie.signature --all                   # table over pool+gen
    python -m tools.esquie.signature --all --cluster 6       # + average-linkage clusters
    python -m tools.esquie.signature --all --annotate CSV    # join a perf csv (map,brick)
                                                            # to annotate cluster members

Topology follows tools/analysis/features/frame.py:terrain(): square grid, 4
directions (N/E/S/W), torus; EDGE key (0,x,y) is the north edge of cell (x,y),
(1,x,y) its east edge; kind 0 open, 1 kelp, 2 portal (id pairs the two ends);
TILE x y minGap maxGap is a bed iff maxGap > 0; DRAGON team n x0 y0 ... is an
initial body, head first.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
POOL = ['devil', 'dilemma', 'portals', 'schooltime', 'slithery_fight', 'queen_of_spades',
        'default', 'trophy', 'autarky', 'trauma']
GEN = [f'var/{p.stem}' for p in sorted((ROOT / 'maps/var').glob('*_tr.map'))] \
      + [f'new/{p.stem}' for p in sorted((ROOT / 'maps/new').glob('*.map'))]

FEATURES = [
    'tile_count', 'open_share', 'kelp_density', 'deg_le2_share', 'deg1_share', 'mean_deg',
    'portal_pairs', 'portals_per100', 'portal_pair_dist',
    'bed_count', 'bed_density', 'bed_gap_mean', 'bed_gap_fast_share', 'bed_ripe50', 'bed_nnd',
    'spawn_bed_path', 'bed_detour_ratio', 'spawn_bed_supply', 'spawn_supply50',
    'spawn_bed_dist', 'spawn_contact',
    'wrap_open_share', 'wrap_edge_use',
]


def parse_map(path):
    """-> dict with W, H, edges {(ori,x,y): kind}, portal pairs, beds, dragons."""
    text = pathlib.Path(path).read_text()
    W = H = None
    edges = {}
    ports = collections.defaultdict(list)
    beds = {}
    dragons = []
    for line in text.splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == 'MAP':
            W, H = int(p[1]), int(p[2])
        elif p[0] == 'EDGE':
            idx, k, pid = int(p[1]), int(p[2]), int(p[3])
            col, row = idx % (W + 1), idx // (W + 1)
            if col >= W or row >= 2 * H:
                continue
            key = (row % 2, col, row // 2)
            edges[key] = k
            if k == 2:
                ports[pid].append(key)
        elif p[0] == 'TILE':
            x, y, mn, mx = map(int, p[1:])
            if mx > 0:
                beds[(x, y)] = (mn, mx)
        elif p[0] == 'DRAGON':
            team, n = int(p[1]), int(p[2])
            segs = [(int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n)]
            dragons.append((team, segs))
    pairs = []
    for pid, keys in ports.items():
        if len(keys) != 2:
            continue
        # edge (0,x,y) is the north edge of (x,y): touches (x,y),(x,y-1);
        # edge (1,x,y) is the east edge of (x,y): touches (x,y),(x+1,y)
        touching = []
        for ori, x, y in keys:
            touching.append([(x % W, y % H),
                             ((x + 1) % W, y % H) if ori == 1 else (x % W, (y + 1) % H)])
        pairs.append((pid, touching))
    return dict(W=W, H=H, edges=edges, pairs=pairs, beds=beds, dragons=dragons)


def tdist(a, b, W, H):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


def signature(path):
    m = parse_map(path)
    W, H, edges = m['W'], m['H'], m['edges']
    n_cells = W * H

    # neighbour function that walks through portals (pairs table has both ends)
    pair_of = {}
    for pid, (side_a, side_b) in m['pairs']:
        for a in side_a:
            for b in side_b:
                pair_of.setdefault(a, set()).add(b)
                pair_of.setdefault(b, set()).add(a)

    def nbrs(c):
        x, y = c
        out = []
        for d in range(4):
            key = ((0, x, y), (1, (x + 1) % W, y), (0, x, (y + 1) % H), (1, x, y))[d]
            k = edges.get(key, 0)
            if k == 1:
                continue
            out.append(((x + (0, 1, 0, -1)[d]) % W, (y + (-1, 0, 1, 0)[d]) % H))
            if k == 2:
                out.extend(q for q in pair_of.get(c, ()) if q not in out)
        return out

    degs, deg1 = collections.Counter(), 0
    cells = [(x, y) for y in range(H) for x in range(W)]
    for c in cells:
        d = len(nbrs(c))
        degs[d] += 1
        if d == 1:
            deg1 += 1
    open_cells = n_cells - degs[0]
    kelp_edges = sum(1 for k in edges.values() if k == 1)
    total_edges = 2 * n_cells

    # seam (wrap) edges: north of row 0, west of column 0
    seam = [(0, x, 0) for x in range(W)] + [(1, 0, y) for y in range(H)]
    seam_open = sum(1 for k in seam if edges.get(k, 0) != 1)
    all_open = total_edges - kelp_edges
    seam_edge_open = sum(1 for k in seam if edges.get(k, 0) != 1)

    pairs = m['pairs']
    pdist = [float(np.mean([tdist(a, b, W, H) for a in side_a for b in side_b]))
             for _, (side_a, side_b) in pairs]
    beds = m['beds']
    bed_cells = list(beds)
    if len(bed_cells) > 1:
        nn = []
        for i, a in enumerate(bed_cells):
            nn.append(min(tdist(a, b, W, H) for j, b in enumerate(bed_cells) if j != i))
        bed_nnd = float(np.mean(nn))
    else:
        bed_nnd = 0.0
    heads0 = [segs[0] for t, segs in m['dragons'] if t == 0]
    heads1 = [segs[0] for t, segs in m['dragons'] if t == 1]
    spawn_bed = float(np.mean([min(tdist(h, b, W, H) for b in bed_cells)
                               for h in heads0 + heads1])) if bed_cells else float('nan')
    contact = min((tdist(a, b, W, H) for a in heads0 for b in heads1), default=float('nan'))

    # BFS through open edges (portals crossed): true walking distance from each
    # initial head to the nearest bed, and the detour ratio over torus manhattan
    def bfs_to_bed(start):
        if not bed_cells:
            return float('nan')
        seen = {start: 0}
        frontier = [start]
        for depth in range(1, 4 * max(W, H)):
            nxt = []
            for c in frontier:
                for q in nbrs(c):
                    if q not in seen:
                        seen[q] = depth
                        nxt.append(q)
            frontier = nxt
            if any(c in bed_set for c in frontier):
                return float(depth)
            if not frontier:
                break
        return float('nan')

    bed_set = set(bed_cells)
    paths = [bfs_to_bed(h) for h in heads0 + heads1]
    spawn_bed_path = float(np.nanmean(paths))
    detour = [p / max(tdist(h, min(bed_cells, key=lambda b: tdist(h, b, W, H)), W, H), 1)
              for h, p in zip(heads0 + heads1, paths)]
    bed_detour_ratio = float(np.nanmean(detour))

    # local supply at the opening: beds within BFS distance 8 of each spawn
    # head, raw and expected-ripe-by-r50 (uniform gap draw); per head
    p_ripe = {c: min(max((50 - mn + 1) / (mx - mn + 1), 0.0), 1.0) for c, (mn, mx) in beds.items()}

    def bfs_ball(start, radius):
        seen = {start}
        frontier = [start]
        for _ in range(radius):
            nxt = []
            for c in frontier:
                for q in nbrs(c):
                    if q not in seen:
                        seen.add(q)
                        nxt.append(q)
            frontier = nxt
        return seen

    balls = [bfs_ball(h, 8) for h in heads0 + heads1]
    supply = [sum(1 for c in b if c in bed_set) for b in balls]
    supply50 = [sum(p_ripe[c] for c in b if c in bed_set) for b in balls]
    spawn_bed_supply = float(np.mean(supply))
    spawn_supply50 = float(np.mean(supply50))
    gaps = [mx for mn, mx in beds.values()]
    mins = [mn for mn, mx in beds.values()]
    # expected share of beds holding a pearl at round 50, if each bed's initial
    # countdown is drawn uniformly from [minGap, maxGap]: E[countdown <= 50]
    ripe50 = float(np.mean([min(max((50 - mn + 1) / (mx - mn + 1), 0.0), 1.0)
                            for mn, mx in beds.values()])) if beds else float('nan')

    try:
        rel = pathlib.Path(path).resolve().relative_to(ROOT)
        name = str(rel.with_suffix(''))
        if name.startswith('maps/'):
            name = name[len('maps/'):]
    except ValueError:
        name = pathlib.Path(path).stem

    return {
        'map': name,
        'W': W, 'H': H,
        'tile_count': n_cells,
        'open_share': open_cells / n_cells,
        'kelp_density': kelp_edges / total_edges,
        'deg_le2_share': (degs[1] + degs[2]) / max(open_cells, 1),
        'deg1_share': deg1 / max(open_cells, 1),
        'mean_deg': sum(k * n for k, n in degs.items()) / n_cells,
        'portal_pairs': len(pairs),
        'portals_per100': 2 * len(pairs) / n_cells * 100,
        'portal_pair_dist': float(np.mean(pdist)) if pdist else 0.0,
        'bed_count': len(beds),
        'bed_density': len(beds) / max(open_cells, 1),
        'bed_gap_mean': float(np.mean(gaps)) if gaps else float('nan'),
        'bed_gap_fast_share': float(np.mean([g <= 10 for g in gaps])) if gaps else float('nan'),
        'bed_ripe50': ripe50,
        'bed_nnd': bed_nnd,
        'spawn_bed_dist': spawn_bed,
        'spawn_bed_path': spawn_bed_path,
        'spawn_bed_supply': spawn_bed_supply,
        'spawn_supply50': spawn_supply50,
        'bed_detour_ratio': bed_detour_ratio,
        'spawn_contact': contact,
        'wrap_open_share': seam_edge_open / len(seam),
        'wrap_edge_use': seam_edge_open / max(all_open, 1),
    }


# ---------------------------------------------------------------- clustering
def cluster(rows, k):
    """Average-linkage agglomerative clustering on z-scored FEATURES (pure numpy,
    deterministic). Returns list of cluster ids aligned with rows."""
    X = np.array([[float(r[f]) for f in FEATURES] for r in rows], dtype=float)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    groups = [[i] for i in range(len(rows))]
    cents = [Z[i] for i in range(len(rows))]
    while len(groups) > k:
        best = None
        for a in range(len(groups)):
            for b in range(a + 1, len(groups)):
                d = float(np.linalg.norm(cents[a] - cents[b]))
                if best is None or d < best[0]:
                    best = (d, a, b)
        _, a, b = best
        groups[a] = groups[a] + groups[b]
        cents[a] = Z[groups[a]].mean(axis=0)
        del groups[b]
        del cents[b]
    return groups


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('map', nargs='?')
    ap.add_argument('--all', action='store_true', help='pool (10) + gen (29) table')
    ap.add_argument('--cluster', type=int, default=0, help='number of clusters with --all')
    ap.add_argument('--annotate', default=None, help='csv with map,brick to annotate members')
    ap.add_argument('--json', default=None, help='write the table as json')
    a = ap.parse_args(argv)

    if not a.all and not a.map:
        ap.error('give a map file or --all')

    names = POOL + GEN if a.all else [a.map]
    rows = []
    for n in names:
        p = pathlib.Path(n) if a.map and not a.all else ROOT / 'maps' / f'{n}.map'
        r = signature(p)
        r['panel'] = 'pool' if r['map'] in POOL else 'gen'
        rows.append(r)

    if not a.all:
        print(json.dumps(rows[0], indent=1, default=str))
        return 0

    hdr = ['panel', 'map'] + FEATURES
    print('\t'.join(hdr))
    for r in rows:
        print('\t'.join([r['panel'], r['map']] + [
            f'{r[f]:.3f}' if isinstance(r[f], float) else str(r[f]) for f in FEATURES]))

    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(rows, indent=1, default=str))

    if a.cluster:
        groups = cluster(rows, a.cluster)
        ann = {}
        if a.annotate:
            for line in pathlib.Path(a.annotate).read_text().splitlines()[1:]:
                p = line.split(',')
                if len(p) >= 2:
                    ann[p[0]] = p[1]
        print(f'\n{len(groups)} clusters (average linkage over z-scored features):')
        for gi, g in enumerate(groups):
            mem = sorted((rows[i]['panel'], rows[i]['map'],
                          ann.get(rows[i]['map'], '')) for i in g)
            print(f'  c{gi}: ' + ', '.join(f'{m[1]}{"*" if m[0] == "pool" else ""}[{m[2]}]'
                                           for m in mem))
    return 0


if __name__ == '__main__':
    sys.exit(main())
