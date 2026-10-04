"""Kanazawa H-KZ7: id-ordered in-round re-sim of wall deaths.
Dragons act in id order. At dragon i's move, the board is rounds[r+1] bodies for ids < i (already moved; dead ones removed)
and rounds[r] bodies for ids > i. Count free (non-kelp, unoccupied) neighbours of the death head under that board
(free_sim) and under the start-of-round board (free_sor). Also: was the fatal target cell kelp (nbr None)?
  python3 build/kanazawa/tree/tools/kanazawa/q_trap2.py --team 7 --n 60 --time 150   # repo root
Output: build/kanazawa/trap/resim.csv"""
import argparse, csv, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
CORPUS = ROOT / 'public_replays/corpus'; OUT = ROOT / 'build/kanazawa/trap'; OUT.mkdir(parents=True, exist_ok=True)
COLS = ['game', 'map', 'round', 'id', 'queen', 'length', 'steps', 'step_at_death', 'target_kelp', 'free_sor', 'free_sim',
        'own_free', 'n_lower_moved', 'dir0']

def one(gid, mapname, side):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay'))
    R = g['rounds']; nbr = g['nbr']
    acts = {(a['round'], a['id']): a for a in g['events']['actions']}
    queen = min(i for i, (t, _) in R[0].items() if t == side)
    out = []
    for d in g['events']['deaths']:
        if d['team'] != side or d['cause'] != 'wall': continue
        r, i = d['round'], d['id']
        if r + 1 >= len(R) or i not in R[r]: continue
        own = R[r][i][1]; head = d['head']
        a = acts.get((r, i), {}); dirs = a.get('dirs') or ()
        # which step died: own head moved k steps from start
        k = 0
        if head != own[0]:
            k = own.index(head) if head in own else -1
        occ_sor = set(); occ_sim = set(); lower = 0
        for j, (t, b) in R[r].items():
            if j == i: continue
            occ_sor.update(b)
            if j < i:
                lower += 1
                if j in R[r + 1]: occ_sim.update(R[r + 1][j][1])
            else:
                occ_sim.update(b)
        for j, (t, b) in R[r + 1].items():   # children born this round to lower ids
            if j not in R[r] and j != i: occ_sim.update(b)
        nb = nbr.get(head, (None,) * 4)
        ownset = set(own) if len(own) <= 2 else set(own[:-1])   # neck counts as blocked; len-2 neck is the tail
        fsor = sum(1 for c in nb if c is not None and c not in occ_sor and c not in ownset)
        fsim = sum(1 for c in nb if c is not None and c not in occ_sim and c not in ownset)
        tk = ''
        if dirs:
            s = dirs[0] if k <= 0 else (dirs[k] if k < len(dirs) else dirs[-1])
            if s < 4: tk = int(nb[s] is None)
        out.append(dict(game=gid, map=mapname, round=r, id=i, queen=int(i == queen), length=d['length'], steps=len(dirs),
                        step_at_death=k, target_kelp=tk, free_sor=fsor, free_sim=fsim,
                        own_free=sum(1 for c in nb if c is not None and c not in ownset), n_lower_moved=lower, dir0=dirs[0] if dirs else ''))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--team', type=int, default=7); ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--time', type=float, default=150); ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--since', default='2026-10-02T03:49')
    a = ap.parse_args(); t0 = time.time(); metas = []
    for line in open(CORPUS / 'index.jsonl'):
        m = json.loads(line)
        if m.get('status') != 'completed' or (m.get('started_at') or '') < a.since: continue
        if a.team not in (m.get('team_a'), m.get('team_b')): continue
        if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append(m)
    k = max(1, len(metas) // a.n); pick = metas[::k][:a.n]
    print(f'eligible {len(metas)} picking {len(pick)}', flush=True)
    f = open(OUT / 'resim.csv', 'w', newline=''); cw = csv.DictWriter(f, COLS); cw.writeheader(); n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(one, m['game_id'], m['map_name'], 'A' if m['team_a'] == a.team else 'B') for m in pick]
        for fu in as_completed(futs):
            if time.time() - t0 > a.time: print('time budget hit'); break
            try: cw.writerows(fu.result()); n += 1
            except Exception as e: print('err', repr(e))
        for fu in futs: fu.cancel()
    f.close(); print(f'games {n} in {time.time()-t0:.0f}s')
main()
