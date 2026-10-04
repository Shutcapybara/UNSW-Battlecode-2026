"""Kanazawa H-KZ6: are our wall deaths deliberate culls or trapped dragons?
For each wall death of a team-T dragon (post-m2), look at the start-of-round state rounds[r] (head first, nbr N,E,S,W):
free = neighbours of the head that are not kelp and not occupied by any body cell (strict); lenient also treats
any dragon's tail tip as free. Also the move direction and whether the dragon split in the last 5 rounds.
  python3 build/kanazawa/tree/tools/kanazawa/q_trap.py --team 7 --n 60 --time 150   # repo root
Output: build/kanazawa/trap/deaths.csv"""
import argparse, csv, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
CORPUS = ROOT / 'public_replays/corpus'; OUT = ROOT / 'build/kanazawa/trap'; OUT.mkdir(parents=True, exist_ok=True)
COLS = ['game', 'map', 'team', 'side', 'round', 'id', 'queen', 'length', 'age', 'dir', 'free_strict', 'free_lenient',
        'split_recent', 'cause']

def one(gid, mapname, side, team):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay'))
    acts = {(a['round'], a['id']): a for a in g['events']['actions']}
    splits = {}
    for s in g['events']['splits']:
        splits.setdefault(s['parent'], []).append(s['round'])
    queen = min(i for i, (t, _) in g['rounds'][0].items() if t == side)
    out = []
    for d in g['events']['deaths']:
        if d['team'] != side or d['cause'] not in ('wall',): continue
        r = d['round']
        if r >= len(g['rounds']): continue
        st = g['rounds'][r]
        if d['id'] not in st: continue
        body = st[d['id']][1]; head = body[0]
        occ = set(); tails = set()
        for i, (t, b) in st.items():
            occ.update(b); tails.add(b[-1])
        nb = g['nbr'].get(head, (None,) * 4)
        fs = sum(1 for c in nb if c is not None and c not in occ)
        fl = sum(1 for c in nb if c is not None and (c not in occ or (c in tails and c != body[1] if len(body) > 1 else True)))
        a = acts.get((r, d['id']), {})
        dirs = a.get('dirs') or ()
        out.append(dict(game=gid, map=mapname, team=team, side=side, round=r, id=d['id'], queen=int(d['id'] == queen),
                        length=d['length'], age=d['age'], dir=dirs[0] if dirs else a.get('kind', '?'), free_strict=fs,
                        free_lenient=fl, split_recent=int(any(0 <= r - s <= 5 for s in splits.get(d['id'], []))),
                        cause=d['cause']))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--team', type=int, default=7); ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--time', type=float, default=150); ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--since', default='2026-10-02T03:49'); ap.add_argument('--out', default='deaths.csv')
    a = ap.parse_args(); t0 = time.time()
    metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < a.since: continue
        if a.team not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    k = max(1, len(metas) // a.n); pick = metas[::k][:a.n]
    print(f'eligible {len(metas)} picking {len(pick)}', flush=True)
    f = open(OUT / a.out, 'w', newline=''); cw = csv.DictWriter(f, COLS); cw.writeheader(); n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], m['map_name'], 'A' if m['team_a'] == a.team else 'B', a.team) for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: rows = fu.result()
            except Exception as e: print('err', e); continue
            cw.writerows(rows); n += 1
        for fu in futs: fu.cancel()
    f.close(); print(f'games {n} in {time.time()-t0:.0f}s')
main()
