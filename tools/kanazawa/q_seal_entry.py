"""Kanazawa unit 5 (answers Himeji H23-01). q_seal_who's '-own' kept b[1:] (= no change): the unit-4 'terrain-only 10/17'
was terrain + own body. Here, on the same 17 seal states: flood from the head with
  all   = every body blocked;   own = only the queen's full body;   neck = only the neck cell b[1] (entry edge);
  none  = no bodies (true terrain);  and the STATIC entry-conditioned region E = |component of head in G minus neck|,
uncapped (cap 5000). E is precomputable per map for every directed edge u->v. Repo root."""
import csv, sys
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
sys.path.append(str(ROOT / 'build/s1-pylib'))
from tools.analysis.features.frame import decode
CAP = 5000
def flood(nbr, head, occ):
    seen = {head}; st = [head]; n = 0
    while st and n < CAP:
        c = st.pop()
        for x in nbr.get(c, ()):
            if x is None or x in seen or x in occ: continue
            seen.add(x); st.append(x); n += 1
    return n
w = csv.writer(sys.stdout); w.writerow(['game','map','seal','death','L','all','own','neck','none','moved','neck_is_tail'])
for r in csv.DictReader(open('build/kanazawa/trap/seal.csv')):
    g = decode(f"public_replays/corpus/replays/{r['game']}.replay"); R = g['rounds']; side = r['side']
    q = min(i for i, (t, _) in R[0].items() if t == side); s = int(r['seal_start']); st = R[s]; b = st[q][1]
    allb = set(); [allb.update(bb) for _, (tm, bb) in st.items()]
    h = b[0]; nb = nbr = g['nbr']
    w.writerow([r['game'], r['map'][:10], s, r['death_round'], len(b), flood(nbr,h,allb), flood(nbr,h,set(b)),
                flood(nbr,h,set(b[1:2])), flood(nbr,h,set()), int(R[s-1][q][1][0] != h), int(len(b)==2)])
