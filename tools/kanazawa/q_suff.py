"""Kanazawa unit 15: H-KZ28 sufficiency / H-KZ26 veto precision (Himeji H32-03, Nara veto-firings column).
FROZEN 10:13Z before running. In-sample stride-96 set (first 286 eligible, consumed; descriptive).
Opportunity at state S=R[r] (same indexing as q_avoid2: death round dr has pre-move state R[dr]):
  enemy head e (team != target team), target head t, Cheb(e,t) <= 3 (wrap; target in e's TurnStart vision),
  2 <= BFS(nbr, e->t) <= B(Le)+1 (B = ceil(L/4)+L-2; +1 because the queen moves first).
  struck = target dies cause h2h in round r with killer == e.
Classes of target: Q = queen (id<=1); CL = non-queen child with L > Le (longer than striker, like 19/20 queen strikes);
  CS = non-queen child with L <= Le.
Primary: per-opportunity strike rate P(struck | opp) for our Q vs our CL.
Prediction: Q rate <= 0.05 (in-vision is not sufficient, Himeji) and Q/CL ratio >= 2 (enemies single out queens, H-KZ27).
  If Q/CL < 1.5 -> H-KZ27 to 0.1 (queen strikes are ordinary length-trade opportunism, no targeting).
  If Q rate >= 0.15 -> H-KZ28 sufficiency up to 0.6 (vision + reach nearly determines a strike).
Follow-up added 10:15Z after the primary (exploratory): for non-hit Q/CL opps with both alive at R[r+1], chase = striker
  head moved closer to the target's old head; flee = target head moved farther from the striker's old head.
Secondary: veto firing rate = queen-rounds with >=1 opportunity / queen-rounds alive (H-KZ26 firings per 1k moves);
  by striker length Le 2-3 / 4-5 / 6+; same numbers for opponent queens (our strikers)."""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
from tools.kanazawa.q_cycle import CORPUS
from tools.kanazawa.q_avoid2 import B, bfs, cheb
def lb(L): return '2-3' if L <= 3 else ('4-5' if L <= 5 else '6+')
def one(gid, ours):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; W, H = g['W'], g['H']
    dd = {}
    for d in g['events']['deaths']:
        if d['cause'] == 'h2h': dd[(d['id'], d['round'])] = d.get('killer')
    c = Counter()
    for r, S in enumerate(R[:-1]):
        for side in ('A', 'B'):
            who = 'us' if side == ours else 'opp'
            en = [(i, bb) for i, (tm, bb) in S.items() if tm != side]
            for i, (tm, bb) in S.items():
                if tm != side: continue
                t = bb[0]; isq = i <= 1
                if isq: c[f'{who}|Q|alive'] += 1
                near = [(j, eb) for j, eb in en if cheb(t, eb[0], W, H) <= 3]
                if not near: continue
                anyopp = False
                for j, eb in near:
                    Le = len(eb); cap = B(Le) + 1
                    dist = bfs(nbr, eb[0], cap).get(t, 99)
                    if not (2 <= dist <= cap): continue
                    cls = 'Q' if isq else ('CL' if len(bb) > Le else 'CS')
                    k = f'{who}|{cls}|{lb(Le)}'; c[k + '|opp'] += 1; anyopp = True
                    if dd.get((i, r)) == j: c[k + '|hit'] += 1
                    elif cls != 'CS' and i in R[r + 1] and j in R[r + 1]:
                        ne = R[r + 1][j][1][0]; nt = R[r + 1][i][1][0]
                        c[k + '|chase'] += bfs(nbr, ne, cap).get(t, 99) < dist
                        c[k + '|flee'] += bfs(nbr, eb[0], cap + 1).get(nt, 99) > dist
                if isq and anyopp: c[f'{who}|Q|fire'] += 1
    return c
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--time', type=float, default=150); a = ap.parse_args(); t0 = time.time()
    metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    metas = metas[:286]; k = max(1, len(metas) // 96); pick = metas[::k][:96]
    C = Counter(); n = 0
    with ProcessPoolExecutor(4) as exr:
        futs = [exr.submit(one, m['game_id'], 'A' if m['team_a'] == 7 else 'B') for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: C += fu.result(); n += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} in {time.time()-t0:.0f}s')
    for who in ('us', 'opp'):
        print('==', who, 'queen-rounds', C[f'{who}|Q|alive'], 'fire', C[f'{who}|Q|fire'],
              'fire/1k', round(1000 * C[f'{who}|Q|fire'] / max(1, C[f'{who}|Q|alive']), 1))
        for cls in ('Q', 'CL', 'CS'):
            O = sum(C[f'{who}|{cls}|{l}|opp'] for l in ('2-3', '4-5', '6+')); Hh = sum(C[f'{who}|{cls}|{l}|hit'] for l in ('2-3', '4-5', '6+'))
            parts = ' '.join(f"{l}:{C[f'{who}|{cls}|{l}|hit']}/{C[f'{who}|{cls}|{l}|opp']}" for l in ('2-3', '4-5', '6+'))
            ch = sum(C[f'{who}|{cls}|{l}|chase'] for l in ('2-3', '4-5', '6+')); fl = sum(C[f'{who}|{cls}|{l}|flee'] for l in ('2-3', '4-5', '6+'))
            print(f'  {cls} chase {ch} flee {fl} (of non-hit opps)')
            print(f'  {cls} hit/opp {Hh}/{O} = {Hh/max(1,O):.4f}   by Le {parts}')
if __name__ == '__main__': main()
