"""Kanazawa unit 11. H-KZ24: anatomy of queen head-to-head (h2h) deaths, with Himeji H29-04's separations.
Unit: queen h2h deaths (us = team 7, and opponents), in-sample stride 96 of the first 286 eligible post-m2 games
  (same selection as q_dose). Pre-move state = R[dr] (start of death round; checked on game 1: R[dr] heads are pre-move).
Per death: killer relation (ally/enemy), mover (event actor == queen) vs victim, mutual flag, queen and killer lengths at R[dr].
Foreseeable: the queen's death cell (event head) equals or is 4-adjacent to the killer's head at R[dr].
Alternative: a neighbour w of the queen head u at R[dr], not the neck, not kelp, not occupied at R[dr] (tails exempt:
  optimistic, NOT legality - H29-02), not equal/adjacent to any other dragon head at R[dr] (uncontested), with
  Cb(u->w) >= 4 (inclusive, cap 16, R[dr] bodies; no future snapshot). Approximate; event-time TurnStart is not modelled.
FROZEN 08:20Z before running: H-KZ24 supported (weight >= 0.55) if >= 1/3 of OUR queen h2h deaths are foreseeable AND have an
  uncontested alternative; refuted (<= 0.2) if < 1/3. Secondary (frozen): if ally killers >= 50 % of our queen h2h, the lever
  is the known ally head-on guard (P-04), not enemy contests - redirect.
POST HOC (08:27Z, after first run): kdist = BFS steps (nbr graph, ignoring bodies, cap 9) from killer head at R[dr] to the death
  cell; kdied = killer dies in the same round (the event 'mutual' flag is set on one record only, so it undercounts)."""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
from tools.kanazawa.q_cycle import CORPUS
from tools.kanazawa.q_dose import reach, occupied
def one(gid, ours):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; rows = []
    for side in ('A', 'B'):
        who = 'us' if side == ours else 'opp'
        q = min(i for i, (tm, _) in R[0].items() if tm == side)
        d = next((d for d in g['events']['deaths'] if d['id'] == q), None)
        if not d or d['cause'] != 'h2h': continue
        dr = d['round']; S = R[dr] if dr < len(R) else None
        if S is None or q not in S: rows.append(dict(who=who, gid=gid, bad=1)); continue
        b = S[q][1]; u = b[0]; neck = b[1] if len(b) > 1 else None; k = d.get('killer')
        kb = S[k][1] if k in S else None
        rel = 'ally' if d.get('killer_team') == side else 'enemy'
        heads = {i: bb[0] for i, (tm, bb) in S.items() if i != q}
        adj = lambda c, h: c == h or h in nbr.get(c, ())
        fore = kb is not None and adj(d['head'], kb[0])
        kdist = None
        if kb is not None:
            fr = {kb[0]}; seen = set(fr)
            for dd in range(10):
                if d['head'] in fr: kdist = dd; break
                fr = {x for c in fr for x in nbr.get(c, ()) if x is not None and x not in seen}; seen |= fr
        kdied = int(any(e['id'] == k and e['round'] == dr for e in g['events']['deaths']))
        occ = occupied(S); alts = []
        for w in nbr.get(u, ()):
            if w is None or w == neck or w in occ: continue
            if any(adj(w, h) for h in heads.values()): continue
            alts.append(len(reach(nbr, u, w, occ - {w})))
        rows.append(dict(who=who, gid=gid, map=g['map'], r=dr, rel=rel, mover=int(d.get('actor') == q), mutual=int(bool(d.get('mutual'))),
                         ql=len(b), kl=len(kb) if kb else None, fore=int(fore), kdist=kdist, kdied=kdied, alt4=int(any(a >= 4 for a in alts)), nalt=len(alts)))
    return rows
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=96); ap.add_argument('--time', type=float, default=150)
    ap.add_argument('--jobs', type=int, default=4); a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    metas = metas[:286]; k = max(1, len(metas) // a.n); pick = metas[::k][:a.n]; rows = []; n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], 'A' if m['team_a'] == 7 else 'B') for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: rows += fu.result(); n += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} in {time.time()-t0:.0f}s')
    for r in sorted(rows, key=lambda r: (r['who'], r.get('rel', ''), r.get('r', 0))): print(json.dumps(r))
    for who in ('us', 'opp'):
        R_ = [r for r in rows if r['who'] == who and not r.get('bad')]; c = Counter()
        for r in R_:
            c['n'] += 1; c[r['rel']] += 1; c['mover'] += r['mover']; c['mutual'] += r['mutual']; c['fore'] += r['fore']
            c['fore&alt4'] += r['fore'] and r['alt4']; c['alt4'] += r['alt4']
            if r['kl'] is not None: c['q_shorter'] += r['ql'] < r['kl']; c['q_equal'] += r['ql'] == r['kl']; c['q_longer'] += r['ql'] > r['kl']
            c[f"{r['rel']}_fore&alt4"] += r['fore'] and r['alt4']; c[f"kdist{r['kdist']}"] += 1; c['kdied'] += r['kdied']
            c['range2+&kdied'] += (r['kdist'] or 0) >= 2 and r['kdied']
        print(who, dict(c))
if __name__ == '__main__': main()
