"""Kanazawa unit 10. H-KZ12 FROZEN CONTRACT (adopts Himeji D-044 semantics) -> per-dose exposure for the Seoul screen.
Feature Cb(u->v): cells reachable from v, INCLUSIVE of v, cap 16, through non-kelp edges, excluding u and every cell that
  is occupied at R[t+1] (post-move start-of-round snapshot) by any dragon body EXCEPT each dragon's tail cell (vacates
  next move). Unknown terrain (bot only) = passable. Orbit escape: no veto if the reach set + {u} (terrain graph) has a
  simple cycle >= L+1, L = queen length at R[t+1]. Veto at dose k if Cb < k (strict), k in {0,4,8,16}; k=0 disabled.
Label (Himeji six-round landmark): queen death with t+1 <= death_round <= t+6, reported by cause (wall/self/body/h2h/invalid).
Alternative: another neighbour w of u (not the neck, not occupied at R[t] except tails, not kelp) with Cb(u->w) >= k
  (approximate legality; H27-05).
Unit: our queen (team 7) single-step moves, in-sample stride 96 of the first 286 eligible post-m2 games. Opponents too.
POST HOC (added after first run, 07:42Z): first_in_window_alt / any_in_window_alt per death.
FROZEN before running (07:41Z): contract adequate for the screen if at k=8 (a) >= 50 % of our queen deaths-by-wall are
  preceded within six rounds by >= 1 vetoed move, and (b) >= 50 % of our vetoed moves have an alternative. Either fails ->
  report the dose that does satisfy them or that the veto is mostly forced (H-KZ12 down to 0.6)."""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
from tools.kanazawa.q_cycle import longest_cycle, CORPUS
DOSES = (4, 8, 16); CAP = 16
def reach(nbr, u, v, occ):
    if v in occ: return [v]
    seen = {u, v}; st = [v]; P = [v]
    while st and len(P) < CAP:
        c = st.pop()
        for x in nbr.get(c, ()):
            if x is None or x in seen or x in occ: continue
            seen.add(x); st.append(x); P.append(x)
            if len(P) >= CAP: break
    return P
def occupied(snap):
    o = set()
    for i, (tm, b) in snap.items(): o.update(b[:-1] if len(b) > 1 else b)
    return o
def one(gid, ours):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; out = Counter()
    for side in ('A', 'B'):
        who = 'us' if side == ours else 'opp'
        q = min(i for i, (tm, _) in R[0].items() if tm == side)
        d = next((d for d in g['events']['deaths'] if d['id'] == q), None)
        dr = d['round'] if d else None; cause = d['cause'] if d else None
        vet_rounds = {k: [] for k in DOSES}
        for t in range(0, len(R) - 1):
            if q not in R[t] or q not in R[t + 1]: break
            b0 = R[t][q][1]; b1 = R[t + 1][q][1]; u, v = b0[0], b1[0]
            if u == v or v not in nbr.get(u, ()): continue
            L = len(b1); occ1 = occupied(R[t + 1]) - {v}; P = reach(nbr, u, v, occ1); C = len(P)
            if C >= CAP: continue
            orb = C >= 3 and longest_cycle(P + [u], nbr) >= L + 1
            if orb: continue
            occ0 = occupied(R[t]); neck = b0[1] if len(b0) > 1 else None
            alts = []
            for w in nbr.get(u, ()):
                if w is None or w == v or w == neck or w in occ0: continue
                alts.append(len(reach(nbr, u, w, occ1 - {w})))
            lab = cause if (dr is not None and t + 1 <= dr <= t + 6) else 'none'
            for k in DOSES:
                if C < k:
                    out[(who, k, 'veto')] += 1; out[(who, k, 'lab', lab)] += 1
                    ok = any(a >= k for a in alts); out[(who, k, 'alt')] += ok; vet_rounds[k].append((t, ok))
        if d is not None:
            out[(who, 'deaths', cause)] += 1
            for k in DOSES:
                w = [x for x in vet_rounds[k] if dr - 6 <= x[0] <= dr - 1]; out[(who, k, 'death_preceded', cause)] += bool(w)
                if w: out[(who, k, 'first_in_window_alt', cause)] += w[0][1]; out[(who, k, 'any_in_window_alt', cause)] += any(x[1] for x in w)
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=96); ap.add_argument('--time', type=float, default=150)
    ap.add_argument('--jobs', type=int, default=4); a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    metas = metas[:286]; k = max(1, len(metas) // a.n); pick = metas[::k][:a.n]; tot = Counter(); n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], 'A' if m['team_a'] == 7 else 'B') for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: tot.update(fu.result()); n += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} in {time.time()-t0:.0f}s (eligible {len(metas)})')
    for kk, v in sorted(tot.items(), key=str): print(kk, v)
if __name__ == '__main__': main()
