"""Kanazawa: for each queen wall death in build/kanazawa/trap/seal.csv, who sealed the pocket at seal_start?
Flood at seal_start-1 (all bodies) and at seal_start with all bodies / without enemy bodies / without ally (non-queen) bodies /
without the queen's own body (head excluded). Prints a table; repo root."""
import csv, sys
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
sys.path.append(str(ROOT / 'build/s1-pylib'))
sys.path.insert(0, str(ROOT / 'build/kanazawa/tree/tools/kanazawa'))
from tools.analysis.features.frame import decode
CAP = 60
def flood(nbr, head, occ):
    seen = {head}; st = [head]; n = 0
    while st and n < CAP:
        c = st.pop()
        for x in nbr.get(c, ()):
            if x is None or x in seen or x in occ: continue
            seen.add(x); st.append(x); n += 1
    return n
for r in csv.DictReader(open('build/kanazawa/trap/seal.csv')):
    g = decode(f"public_replays/corpus/replays/{r['game']}.replay"); R = g['rounds']; side = r['side']
    q = min(i for i, (t, _) in R[0].items() if t == side); s = int(r['seal_start'])
    def fl(t, skip):
        st = R[t]; occ = set()
        for i, (tm, b) in st.items():
            if i == q: occ.update(b[1:] if 'own' in skip else b)
            elif tm == side and 'ally' not in skip: occ.update(b)
            elif tm != side and 'enemy' not in skip: occ.update(b)
        return flood(g['nbr'], st[q][1][0], occ)
    moved = R[s][q][1][0] != R[s-1][q][1][0]
    print(r['game'], r['map'][:10], 'seal', s, 'death', r['death_round'], 'L', r['length'], '| pre', fl(s-1, ()), 'all', fl(s, ()),
          '-enemy', fl(s, ('enemy',)), '-ally', fl(s, ('ally',)), '-own', fl(s, ('own',)), 'moved', int(moved),
          'nearest_enemy_dist?', sum(1 for i,(tm,b) in R[s].items() if tm!=side))
