"""Kanazawa unit 6, cycle bit for low-capacity entries. C(u->v) = cells reachable from v in terrain minus u, INCLUSIVE of v
(Himeji H24-01 contract; q_deadend's E = C-1). For each single-step queen move with C<=5 classify the pocket P:
  tree  : P+{u} acyclic (no orbit possible)
  cyc   : P+{u} has a simple cycle; orbit_ok if its longest simple cycle >= L+1 (L = queen length after move)
Label wall6 = queen died by wall with 0 <= death-(t+1) <= 6 (peer label, 7 integer rounds). Reports move-level and
first-entry-per-queen tallies for us vs opponents, opponents split by team id. Same selection as q_deadend (96, since m2).
Repo root: python3 build/kanazawa/tree/tools/kanazawa/q_cycle.py --time 150"""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
CORPUS = ROOT / 'public_replays/corpus'; CAPC = 5
def pocket(nbr, u, v):
    seen = {u, v}; st = [v]; P = [v]
    while st:
        c = st.pop()
        for x in nbr.get(c, ()):
            if x is None or x in seen: continue
            seen.add(x); st.append(x); P.append(x)
            if len(P) > CAPC: return None
    return P
def longest_cycle(nodes, nbr):
    S = set(nodes); adj = {a: [x for x in nbr.get(a, ()) if x in S and x != a] for a in S}
    best = 0
    for s in S:
        def dfs(c, path, vis):
            nonlocal best
            for x in adj[c]:
                if x == s and len(path) >= 3: best = max(best, len(path))
                elif x not in vis: vis.add(x); path.append(x); dfs(x, path, vis); path.pop(); vis.discard(x)
        dfs(s, [s], {s})
    return best
def one(gid, ours, opp_team):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; memo = {}; out = Counter()
    for side in ('A', 'B'):
        who = 'us' if side == ours else f'opp{opp_team}'
        q = min(i for i, (t, _) in R[0].items() if t == side)
        d = next((d for d in g['events']['deaths'] if d['id'] == q), None)
        dr = d['round'] if d else 10**9; wall = bool(d and d['cause'] == 'wall'); first = True
        for t in range(1, len(R) - 1):
            if q not in R[t] or q not in R[t + 1]: break
            u, v = R[t][q][1][0], R[t + 1][q][1][0]
            if u == v or v not in nbr.get(u, ()): continue
            if (u, v) not in memo:
                P = pocket(nbr, u, v)
                memo[(u, v)] = None if P is None else (len(P), longest_cycle(P + [u], nbr))
            r = memo[(u, v)]
            if r is None: continue
            C, lc = r; L = len(R[t + 1][q][1])
            cls = 'tree' if lc == 0 else ('orbit_ok' if lc >= L + 1 else 'cyc_short')
            w6 = int(wall and 0 <= dr - (t + 1) <= 6)
            out[('mv', who, cls, 'n')] += 1; out[('mv', who, cls, 'w6')] += w6
            if first:
                first = False; out[('q1', who, cls, 'n')] += 1; out[('q1', who, cls, 'w6')] += w6
                out[('q1L', who, cls, min(L, 9))] += 1
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--team', type=int, default=7); ap.add_argument('--n', type=int, default=96)
    ap.add_argument('--time', type=float, default=150); ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--since', default='2026-10-02T03:49'); ap.add_argument('--holdout', action='store_true', help='index positions >= 192 (outside q_deadend selection)'); ap.add_argument('--out', default='cycle.json'); a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < a.since: continue
        if a.team not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    k = max(1, len(metas) // a.n); pick = metas[192:] if a.holdout else metas[::k][:a.n]; tot = Counter(); n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], 'A' if m['team_a'] == a.team else 'B',
                          m['team_b'] if m['team_a'] == a.team else m['team_a']) for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: tot.update(fu.result()); n += 1
            except Exception as e: print('err', e)
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} eligible {len(metas)} in {time.time()-t0:.0f}s')
    for lvl in ('mv', 'q1'):
        whos = sorted({k[1] for k in tot if k[0] == lvl})
        for who in whos:
            row = ' | '.join(f"{c} {tot[(lvl,who,c,'w6')]}/{tot[(lvl,who,c,'n')]}" for c in ('tree','cyc_short','orbit_ok'))
            print(lvl, who, row)
    for k, v in sorted(tot.items(), key=str):
        if k[0] == 'q1L': print(k, v)
    json.dump({'|'.join(map(str, k)): v for k, v in tot.items()}, open(ROOT / 'build/kanazawa/trap' / a.out, 'w'))
if __name__ == '__main__': main()
