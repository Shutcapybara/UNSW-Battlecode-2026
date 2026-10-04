"""Kanazawa unit 9. H-KZ20 corpse-chain bait, with EVENT provenance (FRAME spawn origin; Himeji H27-01: template-cell
proxy is invalid). For each first queen entry u->v into a terrain tree pocket P (q_forced2 definition, both sides):
  in-pocket pearls = PR[t] & P ; origin = last spawn event at that cell with round < t ('bed' env / team-coded corpse)
  board base = all pearls PR[t] at the same round, same origin rule.  Chain = in-pocket corpse pearl whose donor's
  last body snapshot (R[death round]) intersects P (donor died in/at the pocket).
FROZEN (unit 9, 07:20Z, before running): H-KZ20 falsified if pooled in-pocket corpse share <= board corpse share;
supported (weight -> 0.5) if diff >= +0.10 AND chain share of in-pocket corpse pearls >= 0.25. In-sample stride 96 only."""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
from tools.kanazawa.q_cycle import pocket, longest_cycle, CORPUS
def one(gid, ours):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; PR = g['pearls']; out = Counter(); rows = []
    sp = {}
    for s in g['events']['spawns']: sp.setdefault(s['cell'], []).append((s['round'], s['origin'], s['donor']))
    dr = {d['id']: d['round'] for d in g['events']['deaths']}; drec = {d['id']: d for d in g['events']['deaths']}
    def org(c, t):
        best = None
        for r, o, dn in sp.get(c, ()):
            if r < t: best = (o, dn)
        return best or ('init', None)
    for side in ('A', 'B'):
        who = 'us' if side == ours else 'opp'
        q = min(i for i, (tm, _) in R[0].items() if tm == side)
        for t in range(1, len(R) - 1):
            if q not in R[t] or q not in R[t + 1]: break
            body = R[t][q][1]; u = body[0]; v = R[t + 1][q][1][0]; L = len(body)
            if v not in nbr.get(u, ()): continue
            P = pocket(nbr, u, v)
            if P is None or longest_cycle(P + [u], nbr) != 0: continue
            Ps = set(P); inp = [c for c in PR[t] if c in Ps]; nc = 0; dd = []
            for c in inp:
                o, dn = org(c, t); k = 'corpse' if o not in ('bed', 'init', 'unknown') else o
                out[(who, 'in', k)] += 1
                if k == 'corpse':
                    dt = dr.get(dn); chain = dt is not None and dn in R[min(dt, len(R) - 1)] and bool(set(R[min(dt, len(R) - 1)][dn][1]) & Ps)
                    if dt is not None and dn not in R[min(dt, len(R) - 1)] and dt - 1 >= 0 and dn in R[dt - 1]:
                        chain = bool(set(R[dt - 1][dn][1]) & Ps)
                    out[(who, 'chain', chain)] += 1; nc += 1; D = drec.get(dn, {}); dd.append(('own' if D.get('team') == side else 'foe', D.get('cause'), D.get('length'), D.get('head') in Ps, t - dt if dt is not None else None, D.get('age'))); out[(who, 'donor', 'own' if D.get('team') == side else 'foe', D.get('cause'))] += 1
            for c in PR[t]:
                o, _ = org(c, t); out[(who, 'board', 'corpse' if o not in ('bed', 'init', 'unknown') else o)] += 1
            out[(who, 'entries')] += 1; out[(who, 'entries_with_pearl')] += bool(inp)
            rows.append((gid, who, t, len(P), len(inp), nc, g['map'], sorted(set(dd))))
            break
    return out, rows
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=96); ap.add_argument('--time', type=float, default=150)
    ap.add_argument('--jobs', type=int, default=4); ap.add_argument('--new', action='store_true'); a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    new = metas[286:]; metas = metas[:286]  # unit-8 frozen eligible set; new games are reported separately
    k = max(1, len(metas) // a.n); pick = new if a.new else metas[::k][:a.n]; _ = metas[::k][:a.n]; tot = Counter(); n = 0; allrows = []
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], 'A' if m['team_a'] == 7 else 'B') for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: o, r = fu.result(); tot.update(o); allrows += r; n += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} in {time.time()-t0:.0f}s (eligible {len(metas)})')
    for kk, v in sorted(tot.items(), key=str): print(kk, v)
    for r in allrows: print('row', *r)
if __name__ == '__main__': main()
