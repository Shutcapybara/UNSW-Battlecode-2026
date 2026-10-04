"""Kanazawa unit 5, H-KZ12 (corrected) / H-KZ13. Static entry-conditioned dead-end size E(u->v) = |component of v in
G minus u| (terrain only, wrap/portals via nbr, capped at 17). For every queen move u->v (queen = lowest id of a side at
round 0) in post-m2 games with team T, record E bucket and whether the queen died by wall within 6 rounds.
Rows per side: ours (team T) vs opponent. Repo root.  python3 .../q_deadend.py --n 48 --time 150"""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
CORPUS = ROOT / 'public_replays/corpus'; CAP = 17
def E(nbr, u, v, memo):
    k = (u, v)
    if k in memo: return memo[k]
    seen = {u, v}; st = [v]; n = 0
    while st and n < CAP:
        c = st.pop()
        for x in nbr.get(c, ()):
            if x is None or x in seen: continue
            seen.add(x); st.append(x); n += 1
    memo[k] = n; return n
def bucket(e): return '0-4' if e <= 4 else '5-8' if e <= 8 else '9-16' if e <= 16 else '17+'
def one(gid, ours, mp=''):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; memo = {}
    out = Counter()
    for side in ('A', 'B'):
        who = 'us' if side == ours else 'opp'
        q = min(i for i, (t, _) in R[0].items() if t == side)
        d = next((d for d in g['events']['deaths'] if d['id'] == q), None)
        dr = d['round'] if d else 10**9; wall = bool(d and d['cause'] == 'wall')
        for t in range(1, len(R) - 1):
            if q not in R[t] or q not in R[t + 1]: break
            u, v = R[t][q][1][0], R[t + 1][q][1][0]
            if u == v or v not in nbr.get(u, ()): continue   # no move, sprint or teleport: skip
            e = E(nbr, u, v, memo); b = bucket(e)
            if e <= 4: out[('ent', who, g.get('map_name', mp), e, len(R[t+1][q][1]), int(wall and 0 <= dr-(t+1) <= 6))] += 1
            out[(who, b, 'n')] += 1
            if wall and 0 <= dr - (t + 1) <= 6: out[(who, b, 'wall6')] += 1
        ent6 = [t for t in range(1, len(R)-1) if q in R[t] and q in R[t+1] and R[t][q][1][0] != R[t+1][q][1][0] and R[t+1][q][1][0] in nbr.get(R[t][q][1][0], ()) and 0 <= dr-(t+1) <= 6 and E(nbr, R[t][q][1][0], R[t+1][q][1][0], memo) <= 4]
        if ent6 and wall:
            out[(who, 'queens', 'deadend_wall')] += 1
            Ls = [len(R[t+1][q][1]) for t in ent6]; out[(who, 'queens', 'grew_inside')] += int(max(Ls) > min(Ls)) ; out[(who,'queens','grew_or_ate')] += int(len(R[min(ent6)][q][1]) < len(R[min(dr, len(R)-1)][q][1]) if q in R[min(dr,len(R)-1)] else 0)
        out[(who, 'queens', 'n')] += 1; out[(who, 'queens', 'wall')] += int(wall)
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--team', type=int, default=7); ap.add_argument('--n', type=int, default=48)
    ap.add_argument('--time', type=float, default=150); ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--since', default='2026-10-02T03:49')
    a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < a.since: continue
        if a.team not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    k = max(1, len(metas) // a.n); pick = metas[::k][:a.n]; tot = Counter(); n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], 'A' if m['team_a'] == a.team else 'B', m['map_name']) for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: tot.update(fu.result()); n += 1
            except Exception as e: print('err', e)
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} eligible {len(metas)} in {time.time()-t0:.0f}s')
    for who in ('us', 'opp'):
        print(who, 'queens', tot[(who,'queens','n')], 'wall deaths', tot[(who,'queens','wall')], 'after E<=4 entry', tot[(who,'queens','deadend_wall')], 'grew inside', tot[(who,'queens','grew_inside')])
        for b in ('0-4', '5-8', '9-16', '17+'):
            nn = tot[(who,b,'n')]; w = tot[(who,b,'wall6')]
            print(f'  E {b:5s} moves {nn:6d}  wall<=6r {w:3d}  rate {w/max(nn,1):.4f}')
    ent = Counter()
    for k, v in tot.items():
        if k[0] == 'ent': ent[k[1:]] += v
    for k, v in sorted(ent.items(), key=lambda kv: -kv[1])[:40]: print('entry', k, v)
    json.dump({'|'.join(map(str,k)): v for k, v in tot.items()}, open(ROOT/'build/kanazawa/trap/deadend.json','w'))
main()
