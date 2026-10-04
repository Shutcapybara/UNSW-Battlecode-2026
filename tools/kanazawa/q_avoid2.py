"""Kanazawa unit 13 (q_avoid2 = q_avoid with the BFS cap lifted, answering Himeji H31-02).
FROZEN 09:20Z before running: primary = safe1 on OUR 20 with cap 60 (was 11). Expected: unchanged 15/20 (all killers
L<=5; B>=12 needs an enemy L>=10 within distance 12-13 of the queen). If safe1 drops by >=2 -> H-KZ26 back to 0.5 and
the tester spec must use uncapped reach. Secondary (spec dose m=1): safe1m1 = safe at B+1. Exploratory H-KZ30 (bodyguard):
guard = some ally non-queen head with dist(ally head, killer head) <= B(len ally) at R[dr] (could have struck the striker).
Original unit-12 docstring follows.
Kanazawa unit 12. H-KZ26 avoidability + visibility pass (owned per Himeji H30-03), with Himeji H30-01 reach
B(L) = ceil(L/4) + L - 2 (food-free; distance >= enemy L is NOT safe for L>=5).
Cases: the 24 kdist>=2 & kdied queen h2h deaths of unit 11 (20 ours, 4 opp), in-sample stride-96 set (consumed; descriptive).
Decision state D = R[dr] (queen id 0/1 acts before any child id in round dr; the killer struck from its TurnStart after).
Per case at D:
  w legal-ish: nbr neighbour of queen head u, not kelp, not neck, not in occupied(R[dr]) (tails exempt: approximate, H29-02).
  thr(w): some enemy head e with BFS(nbr, ignoring bodies) dist(e, w) <= B(len e). Food-free (H-H8 food cases flagged).
  safe1: some w with not thr(w) and Cb(u->w) >= 4 (inclusive, cap 16, R[dr] bodies).
  safeK: same but only the killer's reach counted (queen knows who strikes).
  safeQ: queen multistep within its own B(len q) over free cells, endpoint safe as above (optimistic: food-free, no
         intermediate collision model).
  vis: killer head within Chebyshev 3 (wrap) of the queen head at D; visA: within 3 of any ally head (shareable).
  d1: dist(killer head, queen head) at R[dr-1] and B(kl) then (warning one round earlier).
FROZEN 08:50Z before running: primary = safe1 on OUR 20.  >= 10/20 -> H-KZ26 0.6 (send spec to testers);
  <= 4/20 -> 0.2 (strikes unavoidable at the last turn: lever moves earlier, to standoff at R[dr-1] or screening);
  else 0.4. Visibility: if vis < 10/20, the rule needs shared threat info (sonar/broadcast) - recorded as dependency.
EXPLORATORY (H-KZ27, not a test; Himeji H30-04 wants matched exposure): per-round exposure of our queen vs our
  length-2..3 non-queens = rounds with an enemy head at dist 2..B(Le); strike = h2h death by enemy with kdist>=2 that
  round. Rates descriptive only."""
import argparse, json, math, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
from tools.kanazawa.q_cycle import CORPUS
from tools.kanazawa.q_dose import reach, occupied
B = lambda L: math.ceil(L / 4) + L - 2
def bfs(nbr, s, cap=60):
    d = {s: 0}; fr = [s]
    for k in range(1, cap + 1):
        nf = []
        for c in fr:
            for x in nbr.get(c, ()):
                if x is not None and x not in d: d[x] = k; nf.append(x)
        fr = nf
    return d
def cheb(a, b, W, H):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1]); return max(min(dx, W - dx), min(dy, H - dy))
def one(gid, ours, cases):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; W, H = g['W'], g['H']
    rows = []; deaths = g['events']['deaths']
    for side, who in (('A', 'us' if ours == 'A' else 'opp'), ('B', 'us' if ours == 'B' else 'opp')):
        q = min(i for i, (tm, _) in R[0].items() if tm == side)
        d = next((d for d in deaths if d['id'] == q), None)
        if not d or d['cause'] != 'h2h' or (gid, d['round']) not in cases: continue
        dr = d['round']; S = R[dr]; k = d.get('killer'); b = S[q][1]; u = b[0]; neck = b[1] if len(b) > 1 else None
        en = {i: bb for i, (tm, bb) in S.items() if tm != side}
        ed = {i: bfs(nbr, bb[0]) for i, bb in en.items()}
        occ = occupied(S)
        def thr(w, only=None):
            return any(ed[i].get(w, 99) <= B(len(en[i])) for i in en if only is None or i == only)
        cand = [w for w in nbr.get(u, ()) if w is not None and w != neck and w not in occ]
        cb = {w: len(reach(nbr, u, w, occ - {w})) for w in cand}
        safe1 = [w for w in cand if not thr(w) and cb[w] >= 4]
        thr1 = lambda w: any(ed[i].get(w, 99) <= B(len(en[i])) + 1 for i in en)
        safe1m1 = [w for w in cand if not thr1(w) and cb[w] >= 4]
        maxLe = max((len(bb) for bb in en.values()), default=0)
        guard = 0
        if k in en:
            kd_ = bfs(nbr, en[k][0])
            guard = int(any(kd_.get(bb[0], 99) <= B(len(bb)) for i, (tm, bb) in S.items() if tm == side and i > 1))
        safeK = [w for w in cand if not thr(w, k) and cb[w] >= 4]
        # queen multistep within its own budget over free cells
        bq = B(len(b)); fr = {u}; seen = {u}; ends = set()
        for _ in range(bq):
            fr = {x for c in fr for x in nbr.get(c, ()) if x is not None and x not in occ and x not in seen and x != neck}
            seen |= fr; ends |= fr
        safeQ = [w for w in ends if not thr(w) and len(reach(nbr, u, w, occ - {w})) >= 4]
        kh = en[k][0] if k in en else None
        vis = int(kh is not None and cheb(u, kh, W, H) <= 3)
        visA = int(kh is not None and any(cheb(bb[0], kh, W, H) <= 3 for i, (tm, bb) in S.items() if tm == side))
        d1 = None; B1 = None
        if dr >= 1 and k in R[dr - 1] and q in R[dr - 1]:
            P = R[dr - 1]; d1 = bfs(nbr, P[k][1][0]).get(P[q][1][0]); B1 = B(len(P[k][1]))
        rows.append(dict(kind='case', who=who, gid=gid, map=g['map'], r=dr, ql=len(b), kl=len(en[k]) if k in en else None,
                         Bk=B(len(en[k])) if k in en else None, kd=ed[k].get(d['head']) if k in ed else None,
                         ncand=len(cand), safe1=len(safe1), safe1m1=len(safe1m1), maxLe=maxLe, guard=guard, safeK=len(safeK), safeQ=len(safeQ), vis=vis, visA=visA, d1=d1, B1=B1))
    return rows
    # exploratory exposure (ours only)
    ex = Counter(); dset = {(e['id'], e['round']): e for e in deaths}
    for r, S in enumerate(R[:-1]):
        en = [bb for tm, bb in S.values() if tm != ours]
        if not en: continue
        for i, (tm, bb) in S.items():
            if tm != ours: continue
            isq = i <= 1
            if not isq and not (2 <= len(bb) <= 3): continue
            h = bb[0]; near = [e for e in en if cheb(h, e[0], W, H) <= 11]
            if not near: continue
            dd = bfs(nbr, h); exp = any(2 <= dd.get(e[0], 99) <= B(len(e)) for e in near)
            if not exp: continue
            key = 'q' if isq else 'c'; ex[key + '_exp'] += 1
            e = dset.get((i, r))
            if e and e['cause'] == 'h2h' and e.get('killer_team') != tm and e.get('killer') in S:
                kh = S[e['killer']][1][0]
                if dd.get(kh, 99) >= 2 or bfs(nbr, kh).get(e['head'], 99) >= 2: ex[key + '_strike'] += 1
    rows.append(dict(kind='exp', gid=gid, **ex))
    return rows
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--time', type=float, default=150); ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args(); t0 = time.time()
    src = ROOT / 'build/kanazawa/tree/docs/findings/kanazawa-data/unit11-q_h2h.txt'; cases = set()
    for line in open(src):
        if not line.startswith('{'): continue
        r = json.loads(line)
        if (r.get('kdist') or 0) >= 2 and r.get('kdied'): cases.add((r['gid'], r['r']))
    metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    metas = metas[:286]; k = max(1, len(metas) // 96); pick = metas[::k][:96]
    print('cases', len(cases)); rows = []; n = 0
    with ProcessPoolExecutor(a.jobs) as exr:
        futs = [exr.submit(one, m['game_id'], 'A' if m['team_a'] == 7 else 'B', cases) for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: rows += fu.result(); n += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} in {time.time()-t0:.0f}s')
    C = [r for r in rows if r['kind'] == 'case']
    for r in sorted(C, key=lambda r: (r['who'], r['r'])): print(json.dumps(r))
    for who in ('us', 'opp'):
        R_ = [r for r in C if r['who'] == who]; c = Counter(n=len(R_))
        for r in R_:
            c['safe1'] += r['safe1'] > 0; c['safe1m1'] += r['safe1m1'] > 0; c['guard'] += r['guard']; c['maxLe>=10'] += r['maxLe'] >= 10; c['safeK'] += r['safeK'] > 0; c['safeQ'] += r['safeQ'] > 0; c['vis'] += r['vis']; c['visA'] += r['visA']
            c['nocand'] += r['ncand'] == 0; c['kd>Bk(food)'] += (r['kd'] or 0) > (r['Bk'] or 99)
            c['d1<=B1'] += r['d1'] is not None and r['d1'] <= r['B1']; c['d1<=B1+1'] += r['d1'] is not None and r['d1'] <= r['B1'] + 1
        print(who, dict(c))
    E = Counter()
    for r in rows:
        if r['kind'] == 'exp': E.update({k: v for k, v in r.items() if k not in ('kind', 'gid')})
    print('exposure', dict(E))
if __name__ == '__main__': main()
