"""A6 + A7 — runtime table and sonar audit (handoff §3.6, §3.7).

A6: distribution of cpu_max / p99-ish stage cpu by source, map and round window; near-cap turns
(> NEAR_CAP points) and what precedes them (units, sonar at the previous stage). Cross-checked
with cpu_recorded == turns coverage.

A7: within-source correlation of sonar rate (per turn) with outcome controlling for map class;
sonar cost per ray in points (stage deltas between adjacent stages).

Unit of independence: the game (verified, controlled; field+dev stated per table). Side A only.
"""
import statistics
from collections import defaultdict

from live_load import STAGES, load, map_class, per_1k, stage

NEAR_CAP = 90_000_000
CAP = 100_000_000


def q(vs, p):
    vs = sorted(v for v in vs if v is not None)
    if not vs:
        return None
    i = min(len(vs) - 1, max(0, int(round(p * (len(vs) - 1)))))
    return vs[i]


def main():
    games = [g for g in load() if g.get('origin') == 'controlled']
    print(f"# A6 runtime — verified controlled games (field+dev), n={len(games)}\n")
    print("| submission | pool | n | cpu_max med | cpu_max p95 | cpu_max max | cap games | >90M games | cpu_recorded==turns |")
    print("|---|---|---|---|---|---|---|---|---|")
    cells = defaultdict(list)
    for g in games:
        cells[(g['submission'], g['pool'])].append(g)
    for (s, pool), rows in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        cm = [g.get('cpu_max') for g in rows]
        cov = sum(1 for g in rows if g.get('cpu_recorded') == g.get('turns'))
        print(f"| {s} | {pool} | {len(rows)} | {q(cm,.5)/1e6:.1f}M | {q(cm,.95)/1e6:.1f}M | {max(cm)/1e6:.1f}M | "
              f"{sum(1 for v in cm if v>=CAP)} | {sum(1 for v in cm if v>NEAR_CAP)} | {cov}/{len(rows)} |")

    # stage-window cpu for the two hot sources
    print("\nstage cpu_max medians (M) by window — sources with any stage cpu > 80M:")
    hot = defaultdict(list)
    for g in games:
        for r in STAGES:
            v = stage(g, r, 'cpu_max')
            if v is not None:
                hot[(g['submission'], r)].append(v)
    srcs = {s for (s, r), v in hot.items() if q(v, .5) and q(v, .5) > 80e6}
    for s in sorted(srcs):
        line = [f"{s}: "]
        for r in STAGES:
            m = q(hot.get((s, r), []), .5)
            line.append(f"r{r}={m/1e6:.0f}" if m else f"r{r}=—")
        print("  " + " ".join(line))

    # what precedes near-cap turns: compare stage context at the stage BEFORE first >90M stage
    pre = defaultdict(list)
    for g in games:
        first = None
        for r in STAGES:
            v = stage(g, r, 'cpu_max')
            if v is not None and v > NEAR_CAP:
                first = r
                break
        if first:
            idx = STAGES.index(first)
            prev = STAGES[idx - 1] if idx else None
            pre[g['submission']].append(dict(first=first, prev_r=prev,
                                             units=stage(g, prev, 'units') if prev else None,
                                             sonar=stage(g, prev, 'sonar') if prev else None,
                                             turns=stage(g, prev, 'turns') if prev else None,
                                             map=g['map_name']))
    for s, rows in sorted(pre.items()):
        firsts = statistics.median([r['first'] for r in rows])
        def m(key):
            vs = [r[key] for r in rows if r.get(key) is not None]
            return statistics.median(vs) if vs else None
        us, son = m('units'), m('sonar')
        maps = defaultdict(int)
        for r in rows:
            maps[r['map']] += 1
        print(f"  {s}: n={len(rows)} first>90M at r{firsts:.0f} median; prev-stage units med {us}, sonar med {son}; maps {dict(maps)}")

    # ---- A7 sonar
    print(f"\n# A7 sonar — verified controlled games\n")
    print("| submission | pool | n | sonar/turn med (wins) | sonar/turn med (losses) | sonar/turn med (compact) | (open) | cpu_max med |")
    print("|---|---|---|---|---|---|---|---|")
    for (s, pool), rows in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        def rate(g):
            so, t = stage(g, 499, 'sonar'), stage(g, 499, 'turns')
            return so / t if so is not None and t else None
        w = [rate(g) for g in rows if (g.get('score') or 0) == 1]
        l = [rate(g) for g in rows if (g.get('score') or 0) == 0]
        c = [rate(g) for g in rows if map_class(g) == 'compact']
        o = [rate(g) for g in rows if map_class(g) == 'open']
        cm = [g.get('cpu_max') for g in rows]
        fmt = lambda v: f"{statistics.median(v):.2f}" if v else "—"
        print(f"| {s} | {pool} | {len(rows)} | {fmt(w)} | {fmt(l)} | {fmt(c)} | {fmt(o)} | {q(cm,.5)/1e6:.0f}M |")

    # within-source, within-map-class: does higher sonar rate predict winning? (median split)
    print("\nwithin source x map class: share when sonar/turn above vs below its own median")
    for (s, pool), rows in sorted(cells.items()):
        rr = [(rate(g), (g.get('score') or 0), map_class(g)) for g in rows]
        rr = [x for x in rr if x[0]]
        for cls in ('compact', 'open'):
            sub = [x for x in rr if x[2] == cls]
            if len(sub) < 8:
                continue
            m = statistics.median([x[0] for x in sub])
            hi = [sc for r, sc, _ in sub if r > m]
            lo = [sc for r, sc, _ in sub if r <= m]
            if hi and lo:
                print(f"  {s} {pool} {cls}: share hi {sum(hi)/len(hi):.2f} (n={len(hi)}) vs lo {sum(lo)/len(lo):.2f} (n={len(lo)}) [split {m:.2f}]")

    # opponent sonar (what we face) for context
    print("\nopponent sonar/turn medians (from opponent_stages):")
    opc = defaultdict(list)
    for g in games:
        so, t = stage(g, 499, 'sonar', 'opp'), stage(g, 499, 'turns', 'opp')
        if so is not None and t:
            opc[g['opponent']].append(so / t)
    for o, v in sorted(opc.items()):
        print(f"  opp {o}: {statistics.median(v):.2f} (n={len(v)})")


if __name__ == '__main__':
    main()
