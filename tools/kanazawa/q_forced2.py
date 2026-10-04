"""Kanazawa unit 8. Exact turn-start legality re-test of H-KZ11 (Himeji H26-05).
Occupancy at our queen's turn in round t (dragons act in ascending id; collision checked before movement):
  other dragon id < q, alive in R[t+1]: its R[t+1] cells (already acted)   | id < q, absent in R[t+1]: nothing (died)
  other dragon id > q in R[t]: its R[t] cells INCLUDING tail (not yet acted) | new ids in R[t+1]: their R[t+1] cells (conservative)
  own body: ALL cells incl. tail (own tail always fatal).  Single-step alternatives only (sprint ignored -> conservative).
Second, stricter class 'safe2': alternative w is legal AND w has >=1 onward neighbour that is legal under the same
occupancy minus our own tail (2-ply sanity, still ignores the opponents' next moves).
FROZEN (unit 8, 06:50Z, before running): exact avoidable share >= 0.7 keeps H-KZ11 falsified; <= 0.5 reverts it to open.
Sets: in-sample stride 96 (positions) and consumed holdout 192+ (replication only, not new evidence)."""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
from tools.kanazawa.q_cycle import pocket, longest_cycle, CORPUS
def one(gid, ours):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; PR = g['pearls']; memo = {}; out = Counter(); rows = []
    def cls(u, w, L):
        if (u, w) not in memo:
            P = pocket(nbr, u, w); memo[(u, w)] = None if P is None else (P, longest_cycle(P + [u], nbr))
        r = memo[(u, w)]
        if r is None: return 'open', None
        return ('tree' if r[1] == 0 else ('orbit_ok' if r[1] >= L + 1 else 'cyc_short')), r[0]
    for side in ('A', 'B'):
        who = 'us' if side == ours else 'opp'
        q = min(i for i, (t, _) in R[0].items() if t == side); done = False
        for t in range(1, len(R) - 1):
            if done or q not in R[t] or q not in R[t + 1]: break
            body = R[t][q][1]; u = body[0]; v = R[t + 1][q][1][0]; L = len(body)
            if v not in nbr.get(u, ()): continue
            if cls(u, v, L)[0] != 'tree': continue
            done = True
            occ = set(body)
            for i, (_, cells) in R[t].items():
                if i == q: continue
                if i < q:
                    if i in R[t + 1]: occ.update(R[t + 1][i][1])
                else: occ.update(cells)
            for i, (_, cells) in R[t + 1].items():
                if i not in R[t]: occ.update(cells)
            occ2 = occ - {body[-1]}
            alts = {}
            for w in nbr.get(u, ()):
                if w is None or w == v or w in occ: continue
                c = cls(u, w, L)[0]
                s2 = any(x is not None and x != u and x not in occ2 for x in nbr.get(w, ()))
                alts[w] = (c, s2)
            good = [w for w, (c, s2) in alts.items() if c in ('open', 'orbit_ok')]
            good2 = [w for w in good if alts[w][1]]
            k = 'avoid2' if good2 else ('avoid1' if good else ('other' if alts else 'nofree'))
            out[('q1', who, k)] += 1
            rows.append((gid, who, t, L, k, len(alts)))
    return out, rows
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=96); ap.add_argument('--time', type=float, default=150)
    ap.add_argument('--holdout', action='store_true'); ap.add_argument('--jobs', type=int, default=4); a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    k = max(1, len(metas) // a.n); pick = metas[192:] if a.holdout else metas[::k][:a.n]; tot = Counter(); n = 0; allrows = []
    meta = {m['game_id']: m for m in pick}
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], 'A' if m['team_a'] == 7 else 'B') for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: o, r = fu.result(); tot.update(o); allrows += r; n += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} in {time.time()-t0:.0f}s (eligible {len(metas)})')
    for k, v in sorted(tot.items(), key=str): print(k, v)
    for r in allrows:
        m = meta[r[0]]; print('row', *r, m['map_name'], 'ranked' if m['ranked'] else 'unranked', 'series' if m['series_id'] else '-')
if __name__ == '__main__': main()
