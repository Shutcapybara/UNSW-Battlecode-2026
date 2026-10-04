"""Kanazawa unit 7. H-KZ11 (were tree-pocket entries forced?) and H-KZ17 (do pearls lure queens into tree pockets?).
Pocket/cycle as q_cycle (terrain-only C<=5, inclusive of v; tree = P+{u} acyclic). Body occupancy at round t = all dragon
cells at R[t] minus each dragon's tail (approximation: ignores same-round head moves and growth).
FROZEN before running (unit 7, 06:20Z):
 H-KZ11: first tree entry per queen is AVOIDABLE if u had another terrain neighbour w (not v, not the neck, not body-
   occupied) whose pocket is open (C>5) or orbit_ok. Forced share >= 0.5 supports H-KZ11; avoidable share >= 0.7 falsifies.
 H-KZ17: exposure = queen head adjacent to a free tree-pocket cell w (w != neck). Lure if P(enter | pearl in P) >=
   2x P(enter | no pearl in P), per side; falsified if ratio <= 1.
Primary set: in-sample stride 96 (holdout already consumed, Himeji H25-04)."""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
from tools.kanazawa.q_cycle import pocket, longest_cycle, CORPUS
def one(gid, ours):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; PR = g['pearls']; memo = {}; out = Counter()
    def cls(u, w, L):
        if (u, w) not in memo:
            P = pocket(nbr, u, w); memo[(u, w)] = None if P is None else (P, longest_cycle(P + [u], nbr))
        r = memo[(u, w)]
        if r is None: return 'open', None
        return ('tree' if r[1] == 0 else ('orbit_ok' if r[1] >= L + 1 else 'cyc_short')), r[0]
    for side in ('A', 'B'):
        who = 'us' if side == ours else 'opp'
        q = min(i for i, (t, _) in R[0].items() if t == side); first = True; uq = {}
        for t in range(1, len(R) - 1):
            if q not in R[t] or q not in R[t + 1]: break
            body = R[t][q][1]; u = body[0]; neck = body[1] if len(body) > 1 else None; v = R[t + 1][q][1][0]; L = len(body)
            if v not in nbr.get(u, ()): continue
            occ = set()
            for i, (_, cells) in R[t].items(): occ.update(cells[:-1] if len(cells) > 1 else cells)
            opts = {}
            for w in nbr.get(u, ()):
                if w is None or w == neck or w in occ and w != v: continue
                opts[w] = cls(u, w, L)
            for w, (c, P) in opts.items():
                if c != 'tree' or not first: continue
                pe = int(any(p in PR[t] for p in P)); ent = int(w == v)
                out[('exp', who, pe, 'n')] += 1; out[('exp', who, pe, 'in')] += ent
                key = (w, pe); uq[key] = max(uq.get(key, 0), ent)
            if v in opts and opts[v][0] == 'tree' and first:
                first = False
                alts = [c for w, (c, _) in opts.items() if w != v]
                k = 'avoid' if any(c in ('open', 'orbit_ok') for c in alts) else ('other' if alts else 'nofree')
                out[('q1', who, k)] += 1
                out[('q1pearl', who, int(any(p in PR[t] for p in opts[v][1])))] += 1
        for (w, pe), ent in uq.items(): out[('uexp', who, pe, 'n')] += 1; out[('uexp', who, pe, 'in')] += ent
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=96); ap.add_argument('--time', type=float, default=150)
    ap.add_argument('--holdout', action='store_true'); ap.add_argument('--jobs', type=int, default=4); a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    k = max(1, len(metas) // a.n); pick = metas[192:] if a.holdout else metas[::k][:a.n]; tot = Counter(); n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], 'A' if m['team_a'] == 7 else 'B') for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: tot.update(fu.result()); n += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} in {time.time()-t0:.0f}s')
    for k, v in sorted(tot.items(), key=str): print(k, v)
if __name__ == '__main__': main()
