"""Kanazawa H-KZ1: sonar usage in the live field (post-m2 ranked games).
Per side: sonars cast, per 100 dragon-rounds, hit-kind mix (incl. enemy = message delivered to the opponent),
refracted share; per team aggregates. Reads the corpus via tools/analysis/features/frame.decode (read-only).
  python3 build/kanazawa/tree/tools/kanazawa/q_sonar.py --n 160 --time 150 --jobs 4   # repo root
Output: build/kanazawa/sonar/sides.csv (appends; resumable by game id)."""
import argparse, collections, csv, json, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
OUT = ROOT / 'build/kanazawa/sonar'; OUT.mkdir(parents=True, exist_ok=True)
CORPUS = ROOT / 'public_replays/corpus'
COLS = ['game','map','team','opp','side','ranked','R','win','n_sonar','dragon_rounds','refracted','first_round',
        'hit_kelp','hit_ally','hit_ally_head','hit_enemy','hit_enemy_head','hit_none','hit_other','queen_sonar']

def one(gid, meta):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay'))
    R = g['last_round']; rounds = g['rounds']
    teams = {i: t for i, (t, _) in rounds[0].items()}
    dr = collections.Counter()
    for r in rounds:
        for i, (t, _) in r.items(): dr[t] += 1
    rows = {}
    for t in 'AB':
        rows[t] = dict(game=gid, map=meta['map_name'], team=meta['team_' + t.lower()], opp=meta['team_' + ('b' if t == 'A' else 'a')],
                       side=t, ranked=int(bool(meta['ranked'])), R=R, win={'a': 1 if t == 'A' else 0, 'b': 1 if t == 'B' else 0}.get(meta['winner'], 0.5),
                       n_sonar=0, dragon_rounds=dr[t], refracted=0, first_round=-1, queen_sonar=0,
                       **{k: 0 for k in COLS if k.startswith('hit_')})
    q = {t: min((i for i, tt in teams.items() if tt == t), default=None) for t in 'AB'}
    for s in g['events']['sonar']:
        t = s['team']
        if t not in rows: continue
        r = rows[t]; r['n_sonar'] += 1; r['refracted'] += int(bool(s['refracted']))
        if r['first_round'] < 0: r['first_round'] = s['round']
        if s['id'] == q[t]: r['queen_sonar'] += 1
        hk = s['hit_kind'] or 'none'
        k = 'hit_' + hk if ('hit_' + hk) in COLS else 'hit_other'
        r[k] += 1
    return [rows['A'], rows['B']]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=160); ap.add_argument('--time', type=float, default=150)
    ap.add_argument('--jobs', type=int, default=4); ap.add_argument('--since', default='2026-10-02T03:49')
    a = ap.parse_args(); t0 = time.time()
    f = OUT / 'sides.csv'; done = set()
    if f.exists():
        done = {int(r['game']) for r in csv.DictReader(open(f))}
    metas = []
    with open(CORPUS / 'index.jsonl') as fh:
        for line in fh:
            m = json.loads(line)
            if m.get('status') == 'completed' and m.get('ranked') and (m.get('started_at') or '') >= a.since and m['game_id'] not in done \
               and (CORPUS / 'replays' / f"{m['game_id']}.replay").exists():
                metas.append(m)
    # deterministic spread sample: every k-th game
    k = max(1, len(metas) // a.n); pick = metas[::k][:a.n]
    print(f'eligible {len(metas)} picking {len(pick)}', flush=True)
    new = f.exists(); w = open(f, 'a', newline=''); cw = csv.DictWriter(w, COLS)
    if not new: cw.writeheader()
    n = 0
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(one, m['game_id'], m): m for m in pick}
        for fu in as_completed(futs):
            try:
                for r in fu.result(): cw.writerow(r)
                n += 1
            except Exception as e: print('ERR', futs[fu]['game_id'], e)
            if time.time() - t0 > a.time:
                print('time budget hit'); ex.shutdown(wait=False, cancel_futures=True); break
    w.close(); print(f'decoded {n} games in {time.time()-t0:.0f}s')
main()
