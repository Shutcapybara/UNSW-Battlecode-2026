#!/usr/bin/env python3
"""C1-E follow-up (a): the Schooltime opening of the top ten, described from ten ranked wins.

Reads the cached corpus frames (tools/analysis/features; no new decoding) and prints the
anatomy the C1-B spec is written from: split timing and sizes, child routing, portal pair
coverage and transits, and swarm structure at r100.

  python tools/analysis/c1e_schooltime.py            # pandas venv not required
"""
import collections, json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.analysis.features.frame import load

# ten top-ten Schooltime wins, spread over teams (rank at game time): 70x3, 306x2, 213x2, 264, 91, 20
GAMES = [(497728, 'B', 70, 2), (516797, 'B', 70, 2), (517364, 'B', 70, 2),
         (512028, 'A', 306, 1), (510667, 'A', 306, 1),
         (499524, 'B', 213, 10), (514740, 'B', 213, 10),
         (517328, 'B', 264, 3), (510684, 'A', 91, 6), (518224, 'A', 20, 5)]
CACHE = ROOT / 'build/c1e/frames'
DECODED = ROOT / 'build/c1e/decoded'


def wrapd(a, b, n):
    d = abs(a - b) % n
    return min(d, n - d)


def cdist(a, b, W, H):
    return max(wrapd(a[0], b[0], W), wrapd(a[1], b[1], H))


def portal_pairs(maptext, W, H):
    """pid -> list of the 2-4 cells bounding its two edges (same math as frame.terrain)."""
    ports = collections.defaultdict(set)
    for line in maptext.splitlines():
        p = line.split()
        if p and p[0] == 'EDGE':
            idx, k, pid = map(int, p[1:])
            if k != 2:
                continue
            col, row = idx % (W + 1), idx // (W + 1)
            if col >= W or row >= 2 * H:
                continue
            ori, x, y = row % 2, col, row // 2
            ports[pid].add((x % W, y % H))
            ports[pid].add(((x - 1) % W, y % H) if ori == 1 else (x % W, (y - 1) % H))
    return {pid: sorted(cs) for pid, cs in ports.items()}


def head_series(g, team, r0, r1):
    """{dragon: [head per round r0..r1]} for dragons of `team` alive at each round."""
    out = collections.defaultdict(list)
    for r in range(r0, r1 + 1):
        if r >= len(g['rounds']):
            break
        for i, (t, b) in g['rounds'][r].items():
            if t == team:
                out[i].append((r, b[0]))
    return out


LIVE_BEDS = None


def live_beds_for(g):
    global LIVE_BEDS
    if LIVE_BEDS is None:
        LIVE_BEDS = json.load(open(ROOT / 'game_stats/live_beds.json'))['maps']
    lay = LIVE_BEDS.get(g['map'], {})
    d = lay.get(g['map_hash'][:16])
    return {tuple(int(x) for x in c.split(',')) for c in d['beds']} if d else set()


def analyse(gid, side, team, rank):
    from tools.hub.vendor.leviathan import replay as replaymod  # noqa: F401 (path set by frame import)
    g = load(str(DECODED / f'{gid}.replay'), str(CACHE))
    t = side
    W, H = g['W'], g['H']
    heads = head_series(g, t, 0, 200)
    sp = [s for s in g['events']['splits'] if s['team'] == t and s['round'] < 100]
    deaths = [d for d in g['events']['deaths'] if d['team'] == t and d['round'] < 100]
    eats = [e for e in g['events']['eats'] if e['team'] == t]
    snap = lambda r: g['rounds'][min(r, g['last_round'])]
    lens = lambda r: sorted((len(b) for i, (tt, b) in snap(r).items() if tt == t), reverse=True)
    # ---- split anatomy ----
    bins = collections.Counter(s['round'] // 10 * 10 for s in sp)
    child_len = collections.Counter(s['child_len'] for s in sp)
    before = collections.Counter(s['before'] for s in sp)
    # ---- portal usage ----
    pairs = portal_pairs(_maptext(DECODED / f'{gid}.replay'), W, H)
    transits = collections.Counter()          # round bin -> transits (head jump >= 3)
    jump2 = 0
    for i, path in heads.items():
        for (r1, a), (r2, b) in zip(path, path[1:]):
            if r2 != r1 + 1 or r1 >= 100:
                continue
            d = cdist(a, b, W, H)
            if d == 2:
                jump2 += 1
            elif d >= 3:
                transits[r1 // 10 * 10] += 1
    # pair coverage at checkpoints: min over our heads of distance to the pair's cells
    cov = {}
    for r in (25, 50, 100):
        hs = [b[0] for i, (tt, b) in snap(r).items() if tt == t]
        ds = []
        for pid, cs in pairs.items():
            best = min((cdist(h, c, W, H) for h in hs for c in cs), default=99)
            ds.append(best)
        ds.sort()
        cov[r] = (ds[len(ds) // 2], ds[0], sum(1 for d in ds if d <= 3), len(ds))
    # ---- child routing: displacement from birthplace, portal crossing in first 40 rounds ----
    homes, crossed, still = [], 0, 0
    born = {s['child']: s['round'] for s in g['events']['splits'] if s['team'] == t}
    for i, path in heads.items():
        if i not in born or i not in g['rounds'][min(100, g['last_round'])]:
            continue
        b0 = born[i]
        p0 = next((h for r, h in path if r >= b0), None)
        p_end = next((h for r, h in path if r >= min(b0 + 60, 100)), None)
        if p0 and p_end:
            homes.append(cdist(p0, p_end, W, H))
        seg = [(r, h) for r, h in path if b0 <= r <= b0 + 40]
        if any(cdist(a, b, W, H) >= 3 for (_, a), (_, b) in zip(seg, seg[1:])):
            crossed += 1
        if i in snap(100):
            still += 1
    # ---- swarm structure at r100 ----
    l100 = lens(100)
    hs100 = [b[0] for i, (tt, b) in snap(100).items() if tt == t]
    nn = []
    for i, a in enumerate(hs100):
        nn.append(min((cdist(a, b, W, H) for j, b in enumerate(hs100) if j != i), default=99))
    bodies = sum(len(b) for i, (tt, b) in snap(100).items() if tt == t)
    beds = live_beds_for(g) or set(g['beds'])
    pcells = [c for cs in pairs.values() for c in cs]
    bed_to_pair = [min(cdist(c, pc, W, H) for pc in pcells) for c in beds]
    all_to_pair = []
    pcells = [c for cs in pairs.values() for c in cs]
    for x in range(0, W, 3):
        for y in range(0, H, 3):
            all_to_pair.append(min(cdist((x, y), pc, W, H) for pc in pcells))
    return dict(gid=gid, side=t, team=team, rank=rank, winner=g['winner'], reason=g['reason'],
                final=g['final'][t], opp=g['final']['A' if t == 'B' else 'B'],
                units={r: len(lens(r)) for r in (0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 200)},
                total={r: sum(lens(r)) for r in (25, 50, 100, 200)},
                first_spawn=next((sp2['round'] for sp2 in g['events']['spawns'] if sp2['origin'] == 'bed'), None),
                death_bins=dict(sorted(collections.Counter(d['round'] // 10 * 10 for d in deaths).items())),
                splits_n=len(sp), split_bins=dict(sorted(bins.items())),
                child_len=dict(sorted(child_len.items())), split_before=dict(sorted(before.items())),
                deaths_by_cause=dict(collections.Counter(d['cause'] for d in deaths)),
                newborn_deaths10=sum(1 for d in deaths if not d['initial'] and d['age'] <= 10),
                first_pearl=next((e['round'] for e in eats), None),
                pearls_r100=sum(1 for e in eats if e['round'] < 100),
                pearls_50_100=sum(1 for e in eats if 50 <= e['round'] < 100),
                pairs=len(pairs), transits=dict(sorted(transits.items())), jump2=jump2,
                pair_cov={r: dict(median=v[0], nearest=v[1], within3=v[2], n=v[3]) for r, v in cov.items()},
                child_displacement_med=sorted(homes)[len(homes) // 2] if homes else None,
                children_crossed_portal=crossed, children_alive_r100=still,
                len100=dict(n=len(l100), len2=sum(1 for x in l100 if x <= 2), len3_5=sum(1 for x in l100 if 3 <= x <= 5),
                            big=max(l100) if l100 else 0, crown=sum(1 for x in l100 if x >= 8)),
                bed_portal_dist_med=sorted(bed_to_pair)[len(bed_to_pair) // 2] if bed_to_pair else None,
                beds_n=len(beds),
                heads_on_bed=sum(1 for h in hs100 if any(cdist(h, c, W, H) <= 2 for c in beds)) / len(hs100) if hs100 and beds else None,
                beds_covered=sum(1 for c in beds if any(cdist(h, c, W, H) <= 2 for h in hs100)) / len(beds) if hs100 and beds else None,
                grid_portal_dist_med=sorted(all_to_pair)[len(all_to_pair) // 2] if all_to_pair else None,
                nearest_ally_med=sorted(nn)[len(nn) // 2] if nn else None,
                nearest_ally_within1=sum(1 for x in nn if x <= 1) / len(nn) if nn else None,
                body_cell_share=bodies / (W * H))


def _maptext(path):
    import sys as _s
    _s.path.insert(0, str(ROOT / 'tools/hub/vendor/leviathan'))
    from replay import Reader
    return Reader(str(path)).object(0, 0).text(0)


def main():
    rows = [analyse(*g) for g in GAMES]
    for r in rows:
        r['swarm'] = r['units'][100] >= 40
        print(json.dumps(r))
    # pooled summary
    pooled = dict(
        games=len(rows),
        units_r100=[r['units'][100] for r in rows], total_r100=[r['total'][100] for r in rows],
        total_r200=[r['total'][200] for r in rows],
        splits=[r['splits_n'] for r in rows], first_pearl=[r['first_pearl'] for r in rows],
        pearls_r100=[r['pearls_r100'] for r in rows],
        split_bins_med={b: statistics.median([r['split_bins'].get(b, 0) for r in rows]) for b in range(0, 100, 10)},
        len2_med=statistics.median([r['len100']['len2'] for r in rows]),
        crown_med=statistics.median([r['len100']['crown'] for r in rows]),
        nearest_ally_med=statistics.median([r['nearest_ally_med'] for r in rows]),
        pair_within3={rr: statistics.median([row['pair_cov'][rr]['within3'] for row in rows]) for rr in (25, 50, 100)},
        transits_med=statistics.median([sum(r['transits'].values()) for r in rows]),
        child_disp_med=statistics.median([r['child_displacement_med'] for r in rows]),
        newborn_deaths10_med=statistics.median([r['newborn_deaths10'] for r in rows]))
    print('POOLED ' + json.dumps(pooled))
    for name, sel in (('SWARM(>=40 units r100)', [r for r in rows if r['swarm']]),
                      ('NON-SWARM', [r for r in rows if not r['swarm']])):
        if not sel:
            continue
        print(name + ' ' + json.dumps(dict(
            games=len(sel), teams=sorted({r['team'] for r in sel}),
            units_r100=[r['units'][100] for r in sel], splits=[r['splits_n'] for r in sel],
            pearls_r100=[r['pearls_r100'] for r in sel], pearls_50_100=[r['pearls_50_100'] for r in sel],
            first_pearl=[r['first_pearl'] for r in sel], first_spawn=[r['first_spawn'] for r in sel],
            split_bins={b: statistics.median([r['split_bins'].get(b, 0) for r in sel]) for b in range(0, 100, 10)},
            units_curve={rr: statistics.median([r['units'][rr] for r in sel]) for rr in (0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)},
            child_disp=[r['child_displacement_med'] for r in sel],
            children_crossed=[r['children_crossed_portal'] for r in sel],
            newborn_deaths10=[r['newborn_deaths10'] for r in sel],
            pair_within3={rr: statistics.median([r['pair_cov'][rr]['within3'] for r in sel]) for rr in (25, 50, 100)},
            transits=[sum(r['transits'].values()) for r in sel],
            nearest_ally_med=[r['nearest_ally_med'] for r in sel],
            len2=[r['len100']['len2'] for r in sel], crown=[r['len100']['crown'] for r in sel],
            heads_on_bed=[r['heads_on_bed'] for r in sel], beds_covered=[r['beds_covered'] for r in sel],
            beds_n=[r['beds_n'] for r in sel], deaths=[sum(r['deaths_by_cause'].values()) for r in sel])))


if __name__ == '__main__':
    main()
