"""Dead-end branch census of a map: for each tree part hanging off the map graph, its cells, depth, beds and gaps."""
import sys, collections
sys.path.insert(0, 'tools/hub/vendor/ouroboros'); sys.path.insert(0, 'tools/analysis/features')
import frame

def branches(nbr):
    adj = {c: [n for n in nbr[c] if n is not None] for c in nbr}
    alive = set(nbr); pruned = []
    changed = True
    while changed:
        changed = False
        for c in list(alive):
            if sum(1 for n in adj[c] if n in alive) <= 1:
                alive.discard(c); pruned.append(c); changed = True
    pruned_set = set(pruned)
    # group pruned cells by the junction (alive cell) they attach to
    groups = collections.defaultdict(set)
    seen = set()
    for c in pruned:
        if c in seen: continue
        comp = set(); stack = [c]
        while stack:
            x = stack.pop()
            if x in comp: continue
            comp.add(x)
            for n in adj[x]:
                if n in pruned_set and n not in comp: stack.append(n)
        seen |= comp
        junctions = {n for x in comp for n in adj[x] if n in alive}
        groups[tuple(sorted(junctions))] |= comp
    return alive, pruned_set, groups

if __name__ == '__main__':
    for mp in sys.argv[1:]:
        m, W, H, nbr, beds, pc = frame.terrain(open(f'maps/live/{mp}.map').read())
        alive, pruned, groups = branches(nbr)
        print(f'== {mp} {W}x{H}: {len(groups)} branches, {len(pruned)} cells')
        rows = []
        for j, comp in groups.items():
            # depth = max BFS distance from the junction
            dist = {}; q = []
            for jj in j:
                for n in nbr[jj]:
                    if n in comp and n not in dist: dist[n] = 1; q.append(n)
            i = 0
            while i < len(q):
                x = q[i]; i += 1
                for n in nbr[x]:
                    if n is not None and n in comp and n not in dist: dist[n] = dist[x] + 1; q.append(n)
            bb = [(c, beds[c]) for c in comp if c in beds]
            rate = sum(2 / (g[0] + g[1]) for c, g in bb)
            rows.append((rate, j, len(comp), max(dist.values()) if dist else 0, len(bb), sorted(set(g for c, g in bb))))
        for rate, j, n, depth, nb, gaps in sorted(rows, reverse=True)[:14]:
            print(f'  junction {j}: cells {n} depth {depth} beds {nb} rate {rate:.2f}/round gaps {gaps}')
