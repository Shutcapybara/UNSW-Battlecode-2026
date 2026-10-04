"""Kanazawa unit 16: H-KZ33 (tiered dodge) + H-KZ35 (pincer). FROZEN 10:47Z before running.
Opportunity definition identical to q_suff (unit 15): enemy head e, target head t, Cheb<=3 (wrap), 2<=BFS(e->t)<=B(Le)+1.
Denominators follow Himeji H34-03: flee/chase over non-hit opps with both alive at R[r+1] (joint survivors).
Tier = opponent team rank in build/s1/corpus/cohort.json top50 (snapshot 20261004T074654Z): top10 = rank<=10, rest = other.
H-KZ33 prediction: opponent-queen flee rate top10 >= 0.85 and rest <= 0.78; falsifier top10 flee <= 0.72.
  Secondary: opponent-queen strike rate (our strikers) top10 < rest.
H-KZ35 prediction: per (queen, round) event, P(hit | >=2 strikers with opp) >= 2 * P(hit | 1 striker), for opponent
  queens (our strikers). Falsifier: ratio < 2. Same table for our queen reported (descriptive).
Corpus: default in-sample first-286 stride set (consumed, descriptive); --new = eligible games after 286 (out of sample)."""
import argparse, json, sys, time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
from tools.kanazawa.q_cycle import CORPUS
from tools.kanazawa.q_avoid2 import B, bfs, cheb
TOP10 = set(json.load(open(ROOT / 'build/s1/corpus/cohort.json'))['top50'][:10])
def one(gid, ours, tier):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; W, H = g['W'], g['H']
    dd = {(d['id'], d['round']): d.get('killer') for d in g['events']['deaths'] if d['cause'] == 'h2h'}
    c = Counter()
    for r, S in enumerate(R[:-1]):
        for side in ('A', 'B'):
            who = 'us' if side == ours else 'opp|' + tier
            en = [(i, bb) for i, (tm, bb) in S.items() if tm != side]
            for i, (tm, bb) in S.items():
                if tm != side or i > 1: continue
                t = bb[0]; c[who + '|alive'] += 1; ks = []; hit = False
                for j, eb in en:
                    if cheb(t, eb[0], W, H) > 3: continue
                    cap = B(len(eb)) + 1; dist = bfs(nbr, eb[0], cap).get(t, 99)
                    if not (2 <= dist <= cap): continue
                    ks.append(j); c[who + '|opp'] += 1
                    if dd.get((i, r)) == j: c[who + '|hit'] += 1; hit = True
                    elif i in R[r + 1] and j in R[r + 1]:
                        c[who + '|js'] += 1
                        c[who + '|chase'] += bfs(nbr, R[r + 1][j][1][0], cap).get(t, 99) < dist
                        c[who + '|flee'] += bfs(nbr, eb[0], cap + 1).get(R[r + 1][i][1][0], 99) > dist
                if ks:
                    k = '1' if len(ks) == 1 else '2+'
                    c[f'{who}|ev{k}'] += 1; c[f'{who}|evhit{k}'] += hit or (dd.get((i, r)) in ks)
    return c
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--time', type=float, default=150); ap.add_argument('--new', action='store_true'); ap.add_argument('--stride', type=int, default=1)
    a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    if a.new: pick = metas[286:][::a.stride]
    else: metas = metas[:286]; k = max(1, len(metas) // 96); pick = metas[::k][:96]
    C = Counter(); n = 0; nt = Counter()
    with ProcessPoolExecutor(4) as exr:
        futs = {}
        for m in pick:
            ours = 'A' if m['team_a'] == 7 else 'B'; ot = m['team_b'] if ours == 'A' else m['team_a']
            tier = 'top10' if ot in TOP10 else 'rest'; futs[exr.submit(one, m['game_id'], ours, tier)] = tier
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: C += fu.result(); n += 1; nt[futs[fu]] += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    print(f'games {n}/{len(pick)} {dict(nt)} in {time.time()-t0:.0f}s')
    for who in ('us', 'opp|top10', 'opp|rest'):
        g = lambda s: C[f'{who}|{s}']
        print(f"== {who}: queen-rounds {g('alive')} opp {g('opp')} hit {g('hit')} rate {g('hit')/max(1,g('opp')):.4f} | "
              f"joint-surv non-hit {g('js')} flee {g('flee')/max(1,g('js')):.3f} chase {g('chase')/max(1,g('js')):.3f}")
        e1, e2, h1, h2 = g('ev1'), g('ev2+'), g('evhit1'), g('evhit2+')
        print(f"   pincer: 1-striker {h1}/{e1}={h1/max(1,e1):.4f}  2+-striker {h2}/{e2}={h2/max(1,e2):.4f}  ratio {(h2/max(1,e2))/max(1e-9,h1/max(1,e1)):.2f}")
if __name__ == '__main__': main()
