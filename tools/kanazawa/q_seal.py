"""Kanazawa H-KZ6 vs Himeji H22-01/H-H6: was a wall-dying queen already sealed before its last split, or did the split seal it?
For each queen (lowest id of the side at round 0) wall death, compute the static flood region of the head (cells reachable
through non-kelp cells not occupied by any body at round start; wrap/portals via nbr; capped at 60) for every round of the
last 60 before death. Report: last split round of the queen before death, flood at split-1 and split+1, and the first round
of the final sealed run (flood < length+2 continuously until death).
  python3 build/kanazawa/tree/tools/kanazawa/q_seal.py --team 7 --n 60 --time 150   # repo root
Output: build/kanazawa/trap/seal.csv"""
import argparse, csv, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
CORPUS = ROOT / 'public_replays/corpus'; OUT = ROOT / 'build/kanazawa/trap'; OUT.mkdir(parents=True, exist_ok=True)
COLS = ['game', 'map', 'side', 'death_round', 'length', 'last_split', 'flood_pre', 'flood_post', 'seal_start',
        'sealed_before_split', 'split_sealed', 'never_sealed', 'units_at_split']
CAP = 60

def flood(nbr, head, occ):
    seen = {head}; st = [head]; n = 0
    while st and n < CAP:
        c = st.pop()
        for x in nbr.get(c, ()):
            if x is None or x in seen or x in occ: continue
            seen.add(x); st.append(x); n += 1
    return n

def one(gid, mapname, side):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay'))
    R = g['rounds']; nbr = g['nbr']
    queen = min(i for i, (t, _) in R[0].items() if t == side)
    d = next((d for d in g['events']['deaths'] if d['id'] == queen), None)
    if not d or d['cause'] != 'wall': return []
    r = d['round']
    if r >= len(R) or queen not in R[r]: return []
    L = len(R[r][queen][1])
    fl = {}
    for t in range(max(1, r - 60), r + 1):
        st = R[t]
        if queen not in st: continue
        occ = set()
        for i, (tm, b) in st.items(): occ.update(b)
        fl[t] = flood(nbr, st[queen][1][0], occ)
    seal = r
    while seal - 1 in fl and fl[seal - 1] < L + 2: seal -= 1
    sp = [s['round'] for s in g['events']['splits'] if s['parent'] == queen and s['round'] <= r]
    ls = max(sp) if sp else None
    pre = fl.get(ls - 1) if ls else None; post = fl.get(ls + 1) if ls else None
    units = sum(1 for i, (tm, b) in R[ls].items() if tm == side) if ls and ls < len(R) else None
    never = int(fl.get(r, 0) >= L + 2)
    return [dict(game=gid, map=mapname, side=side, death_round=r, length=L, last_split=ls, flood_pre=pre, flood_post=post,
                 seal_start=seal, sealed_before_split=int(ls is not None and seal < ls), split_sealed=int(ls is not None and seal >= ls and r - ls <= 15 and (pre or 0) >= L + 2),
                 never_sealed=never, units_at_split=units)]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--team', type=int, default=7); ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--time', type=float, default=150); ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--since', default='2026-10-02T03:49'); ap.add_argument('--out', default='seal.csv')
    a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < a.since: continue
        if a.team not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    k = max(1, len(metas) // a.n); pick = metas[::k][:a.n]
    print(f'eligible {len(metas)} picking {len(pick)}', flush=True)
    f = open(OUT / a.out, 'w', newline=''); cw = csv.DictWriter(f, COLS); cw.writeheader(); n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], m['map_name'], 'A' if m['team_a'] == a.team else 'B') for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: cw.writerows(fu.result()); n += 1
            except Exception as e: print('err', e)
        for fu in futs: fu.cancel()
    f.close(); print(f'games {n} in {time.time()-t0:.0f}s')
main()
