"""Kanazawa unit 14: H-KZ31 (invisibility rule) on the same 20+4 queen sprint-strike cases as q_avoid2 (cap 60).
FROZEN 09:43Z before running. inv(w): every enemy head at Chebyshev >= 4 (wrap) of w at R[dr] (enemy TurnStart vision
is Cheb <= 3 from its head, H31-01). Primary = invsafe: some cand w with inv(w) and Cb(u->w) >= 4, on OUR 20.
Expected: <= 6/20 (15/20 killers already within Cheb 3 of the queen; one step can lift Cheb by at most 1).
Falsifier from unit 13: < 10/20 -> H-KZ31 to 0.1 (a vision-hiding rule cannot replace the reach veto at the last turn).
Secondary: invK (only the killer counted); inv_and_safe1 (inv and outside every enemy reach B(Le)).
Cross-lane (Shenzhen H-SZ34 reach = min(L-1,3)): computed from unit-13 rows, not here."""
import json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
from tools.kanazawa.q_cycle import CORPUS
from tools.kanazawa.q_dose import reach, occupied
from tools.kanazawa.q_avoid2 import B, bfs, cheb
def one(gid, ours, cases):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; W, H = g['W'], g['H']
    rows = []
    for side in ('A', 'B'):
        who = 'us' if ours == side else 'opp'
        q = min(i for i, (tm, _) in R[0].items() if tm == side)
        d = next((d for d in g['events']['deaths'] if d['id'] == q), None)
        if not d or d['cause'] != 'h2h' or (gid, d['round']) not in cases: continue
        dr = d['round']; S = R[dr]; k = d.get('killer'); b = S[q][1]; u = b[0]; neck = b[1] if len(b) > 1 else None
        en = {i: bb for i, (tm, bb) in S.items() if tm != side}
        ed = {i: bfs(nbr, bb[0]) for i, bb in en.items()}; occ = occupied(S)
        cand = [w for w in nbr.get(u, ()) if w is not None and w != neck and w not in occ]
        cb = {w: len(reach(nbr, u, w, occ - {w})) for w in cand}
        inv = lambda w, only=None: all(cheb(w, bb[0], W, H) >= 4 for i, bb in en.items() if only is None or i == only)
        thr = lambda w: any(ed[i].get(w, 99) <= B(len(en[i])) for i in en)
        cu = min((cheb(u, bb[0], W, H) for bb in en.values()), default=99)
        ck = cheb(u, en[k][0], W, H) if k in en else None
        rows.append(dict(who=who, gid=gid, r=dr, ncand=len(cand), cu=cu, ck=ck,
            invsafe=sum(inv(w) and cb[w] >= 4 for w in cand), invK=sum(inv(w, k) and cb[w] >= 4 for w in cand),
            inv_safe1=sum(inv(w) and not thr(w) and cb[w] >= 4 for w in cand),
            safe1=sum((not thr(w)) and cb[w] >= 4 for w in cand)))
    return rows
def main():
    t0 = time.time(); src = ROOT / 'build/kanazawa/tree/docs/findings/kanazawa-data/unit11-q_h2h.txt'; cases = set()
    for line in open(src):
        if line.startswith('{'):
            r = json.loads(line)
            if (r.get('kdist') or 0) >= 2 and r.get('kdied'): cases.add((r['gid'], r['r']))
    gids = {g for g, _ in cases}; metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m['game_id'] in gids: metas.append(m)
    rows = []
    with ProcessPoolExecutor(4) as exr:
        futs = [exr.submit(one, m['game_id'], 'A' if m['team_a'] == 7 else 'B', cases) for m in metas]
        for fu in as_completed(futs):
            if time.time() - t0 > 150: print('time budget hit'); break
            try: rows += fu.result()
            except Exception as e: print('err', repr(e))
    for r in sorted(rows, key=lambda r: (r['who'], r['r'])): print(json.dumps(r))
    for who in ('us', 'opp'):
        X = [r for r in rows if r['who'] == who]; c = Counter(n=len(X))
        for r in X:
            for kk in ('invsafe', 'invK', 'inv_safe1', 'safe1'): c[kk] += r[kk] > 0
            c['cu>=4'] += r['cu'] >= 4; c['ck==3'] += r['ck'] == 3
        print(who, dict(c))
    print(f'{time.time()-t0:.0f}s')
if __name__ == '__main__': main()
