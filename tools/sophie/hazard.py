"""K-1 hazard signatures: per-cell structural features, fitted hazard models, and per-map hazard profiles.

    python tools/sophie/hazard.py features <map file or map_hash> [...]      # print the per-cell feature summary
    python tools/sophie/hazard.py profile <map file> [...]                   # score every signature on a map
    python tools/sophie/hazard.py profile-all --out docs/.../profiles.csv    # pool + gen maps (39)

Everything here is local structure computed from the map text alone (never the map's name, hash or dimensions as
a key); the signatures in SIGNATURES are fitted on the corpus (see docs/findings/*-K1-hazard-signatures.md).
Kelp in this game lives on edges between cells, so 'degree' is the number of open sides of a cell (0-4).
"""
import collections, json, math, os, sys
from pathlib import Path

REPO = Path(os.environ.get('K1_REPO', Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(REPO))
from tools.analysis.features.frame import terrain  # noqa: E402

BED_R = (3, 6)


def bfs(nbr, sources, limit=None):
    dist, q = {}, collections.deque()
    for s in sources:
        if s not in dist:
            dist[s] = 0
            q.append(s)
    while q:
        c = q.popleft()
        d = dist[c]
        if limit is not None and d >= limit:
            continue
        for n in nbr[c]:
            if n is not None and n not in dist:
                dist[n] = d + 1
                q.append(n)
    return dist


def load_map(arg):
    """returns (name, text, W, H, nbr, beds{cell: rate}, portal_cells, spawns{team: [cells]})"""
    p = Path(arg)
    if not p.exists():
        p = REPO / 'build/sophie/maps' / f'{arg}.map'
    text = p.read_text()
    m, W, H, nbr, beds, portal_cells = terrain(text)
    name = next((l[9:] for l in text.splitlines() if l.startswith('MAP_NAME ')), p.stem)
    if not beds:
        from tools.analysis.features.beds import resolve
        beds, _ = resolve(dict(beds={}, W=W, H=H, nbr=nbr, map=name))
    rate = {c: 2.0 / (lo + hi) for c, (lo, hi) in beds.items() if lo + hi > 0}
    spawns = collections.defaultdict(list)
    for t, body in m['dragons']:
        spawns[t].append(tuple(body[0]))
    return name, text, W, H, nbr, rate, portal_cells, dict(spawns)


def cell_features(arg):
    name, text, W, H, nbr, rate, portal_cells, spawns = load_map(arg)
    cells = list(nbr)
    deg = {c: sum(n is not None for n in nbr[c]) for c in cells}
    # distance to kelp: 0 if the cell has a kelp side
    kd = bfs(nbr, [c for c in cells if deg[c] < 4])
    # dead-end depth: peel cells of remaining degree <= 1; depth = peel round (0 = in the cyclic core)
    rem = {c: set(n for n in nbr[c] if n is not None and n != c) for c in cells}
    depth, frontier, k = {}, [c for c in cells if len(rem[c]) <= 1], 0
    while frontier:
        k += 1
        nxt = []
        for c in frontier:
            if c in depth:
                continue
            depth[c] = k
            for n in rem[c]:
                rem[n].discard(c)
                if n not in depth and len(rem[n]) <= 1:
                    nxt.append(n)
        frontier = nxt
    # portals: terrain distance to nearest portal cell; landing openness of that portal's exit
    pd_ = bfs(nbr, list(portal_cells)) if portal_cells else {}
    # landing degree: for each portal-side cell, the degree of the cell reached through the portal
    land = {}
    for c in portal_cells:
        for d, n in enumerate(nbr[c]):
            if n is None:
                continue
            x, y = c
            g = ((x + (0, 1, 0, -1)[d]) % W, (y + (-1, 0, 1, 0)[d]) % H)
            if n != g:
                land[c] = min(land.get(c, 9), deg[n] + min(kd.get(n, 9), 3))
    near_portal_land = {}
    if land:
        # multi-source bfs carrying the landing value of the nearest portal cell
        q = collections.deque()
        for c, v in land.items():
            near_portal_land[c] = v
            q.append(c)
        seen = set(land)
        while q:
            c = q.popleft()
            for n in nbr[c]:
                if n is not None and n not in seen:
                    seen.add(n)
                    near_portal_land[n] = near_portal_land[c]
                    q.append(n)
    # bed density within r (terrain distance), per cell
    bed_d = {r: collections.Counter() for r in BED_R}
    for b, lam in rate.items():
        dd = bfs(nbr, [b], max(BED_R))
        for c, dist in dd.items():
            for r in BED_R:
                if dist <= r:
                    bed_d[r][c] += lam
    # bed clusters: beds joined when within 2 steps
    beds = list(rate)
    comp, cid = {}, 0
    for b in beds:
        if b in comp:
            continue
        cid += 1
        stack = [b]
        comp[b] = cid
        while stack:
            u = stack.pop()
            for v, dist in bfs(nbr, [u], 2).items():
                if v in rate and v not in comp:
                    comp[v] = cid
                    stack.append(v)
    csize = collections.Counter(comp.values())
    bdist = bfs(nbr, beds) if beds else {}
    near_cluster = {}
    if beds:
        q = collections.deque()
        for b in beds:
            near_cluster[b] = csize[comp[b]]
            q.append(b)
        seen = set(beds)
        while q:
            c = q.popleft()
            for n in nbr[c]:
                if n is not None and n not in seen:
                    seen.add(n)
                    near_cluster[n] = near_cluster[c]
                    q.append(n)
    # spawn distance (any team) and region size of the open area (cells of degree >= 3, 4-connected via open sides)
    all_sp = [c for v in spawns.values() for c in v]
    sd = bfs(nbr, all_sp)
    region, rsize = {}, collections.Counter()
    rid = 0
    for c in cells:
        if deg[c] < 3 or c in region:
            continue
        rid += 1
        stack = [c]
        region[c] = rid
        while stack:
            u = stack.pop()
            rsize[rid] += 1
            for n in nbr[u]:
                if n is not None and deg[n] >= 3 and n not in region:
                    region[n] = rid
                    stack.append(n)
    reach5 = {c: len(bfs(nbr, [c], 5)) for c in cells}
    wrap = {}
    for (x, y) in cells:
        w = 0
        for d, n in enumerate(nbr[(x, y)]):
            if n is None:
                continue
            if (d == 0 and y == 0) or (d == 2 and y == H - 1) or (d == 1 and x == W - 1) or (d == 3 and x == 0):
                w = 1
        wrap[(x, y)] = w
    # map scalars
    n_edges = 2 * W * H
    kelp = sum(1 for c in cells for d in (1, 2) if nbr[c][d] is None)
    teams = sorted(spawns)
    contact = None
    if len(teams) == 2:
        d0 = bfs(nbr, spawns[teams[0]])
        contact = min(d0.get(c, 999) for c in spawns[teams[1]])   # 999 = the sides never meet by terrain
    scal = dict(tiles=W * H, kelp_share=kelp / n_edges, portal_cells=len(portal_cells), beds=len(rate),
                bed_capacity=sum(rate.values()), contact=contact, core_share=sum(1 for c in cells if c not in depth) / len(cells),
                dead_share=sum(1 for c in cells if c in depth) / len(cells),
                deg2_share=sum(1 for c in cells if deg[c] <= 2) / len(cells))
    rows = {}
    for c in cells:
        rows[c] = dict(deg=deg[c], kelp_d=kd.get(c, 99), dead=depth.get(c, 0), portal_d=pd_.get(c, 99),
                       land=near_portal_land.get(c, 9), bed3=bed_d[3][c], bed6=bed_d[6][c],
                       bed_d=bdist.get(c, 99), cluster=near_cluster.get(c, 0) if bdist.get(c, 99) <= 2 else 0,
                       spawn_d=sd.get(c, 99), wrap=wrap[c], region=rsize[region[c]] if c in region else 0,
                       reach5=reach5[c], is_bed=int(c in rate))
    return dict(name=name, W=W, H=H, scalars=scal, cells=rows)

# ---------------------------------------------------------------- signatures (K-1 Part 2)
# Each is a rule on the per-cell features above. Chosen from Poisson trees fitted on the field's cells (10 pool
# terrains, 4,563 games) and kept only if the rate ratio is > 1 on most terrains for both the field and us.
SIGNATURES = {
    'H1_dead_end':       ('cell with one open side (cul-de-sac tip)', lambda r: r['deg'] <= 1),
    'H2_bed_corridor':   ('two-sided corridor cell with beds within 6 steps (bed6 > 0.36)', lambda r: r['deg'] == 2 and r['bed6'] > 0.36),
    'H3_bare_corridor':  ('two-sided corridor cell without beds nearby', lambda r: r['deg'] == 2 and r['bed6'] <= 0.36),
    'H4_portal_mouth':   ('cell adjacent through a portal edge', lambda r: r['portal_d'] == 0),
    'H5_portal_approach_beds': ('one step from a portal mouth, inside a bed cluster of >= 3', lambda r: r['portal_d'] == 1 and r['cluster'] >= 3),
    'H6_bed_pocket':     ('three-sided cell (one kelp side) with bed3 > 0.28', lambda r: r['deg'] == 3 and r['bed3'] > 0.28),
    'H7_dense_open_cluster': ('fully open cell inside a dense bed cluster (bed3 > 0.44, bed6 > 0.63)', lambda r: r['deg'] == 4 and r['bed3'] > 0.44 and r['bed6'] > 0.63),
    'H8_small_room':     ('open cell (>= 3 sides) with <= 25 cells reachable in 5 steps', lambda r: r['deg'] >= 3 and r['reach5'] <= 25),
}


def signature_of(row):
    return [k for k, (_, f) in SIGNATURES.items() if f(row)]


def profile(arg, ratios=None):
    """share of cells carrying each signature; with ratios {sig: {class: field_ratio}} also a hazard index per
    class = mean over cells of the product-free max ratio of the signatures the cell carries (1 = benign)"""
    f = cell_features(arg)
    n = len(f['cells'])
    share = {k: 0 for k in SIGNATURES}
    idx = collections.defaultdict(float)
    for c, r in f['cells'].items():
        sigs = signature_of(r)
        for k in sigs:
            share[k] += 1 / n
        if ratios:
            for cls in next(iter(ratios.values())):
                vals = [ratios[k][cls] for k in sigs if cls in ratios[k]]
                idx[cls] += (max(vals) if vals else ratios.get('_rest', {}).get(cls, 1.0)) / n
    return dict(name=f['name'], W=f['W'], H=f['H'], scalars=f['scalars'], share=share, index=dict(idx))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'features':
        import statistics
        for a in sys.argv[2:]:
            f = cell_features(a)
            print(f['name'], f['W'], f['H'], json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in f['scalars'].items()}))
            keys = next(iter(f['cells'].values())).keys()
            for k in keys:
                vs = [r[k] for r in f['cells'].values()]
                print(f'   {k:9s} mean {statistics.mean(vs):7.2f}  max {max(vs):7.2f}')
    elif cmd == 'profile':
        rp = REPO / 'docs/findings/data/sophie-K1-signature-ratios.json'
        ratios = json.load(open(rp)) if rp.exists() else None
        for a in sys.argv[2:]:
            p = profile(a, ratios)
            print(p['name'], json.dumps({k: round(v, 3) for k, v in p['share'].items()}))
            if p['index']:
                print('   hazard index (x field-average rate at uniform exposure):', json.dumps({k: round(v, 2) for k, v in p['index'].items()}))
