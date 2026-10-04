"""Kanazawa H-KZ2: are sonar echoes a radar beyond 7x7 vision? For rays that end on an enemy head (or the enemy queen),
torus distance origin->end along the ray, and whether the hit dragon is the enemy queen (lowest id of its team).
  python3 build/kanazawa/tree/tools/kanazawa/q_radar.py --n 60 --time 140   # repo root; prints a summary"""
import argparse, collections, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT)]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
CORPUS = ROOT / 'public_replays/corpus'

def one(gid):
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay'))
    W, H = g['W'], g['H']; teams = {i: t for i, (t, _) in g['rounds'][0].items()}
    q = {t: min(i for i, tt in teams.items() if tt == t) for t in 'AB'}
    out = collections.Counter(); dist = []
    for s in g['events']['sonar']:
        hk = s['hit_kind']; o, e = s['origin'], s['end']
        if o is None or e is None: continue
        (ox, oy), (ex, ey) = o, e
        dx = min((ex - ox) % W, (ox - ex) % W); dy = min((ey - oy) % H, (oy - ey) % H)
        d = max(dx, dy)
        out['rays'] += 1; out[f'k_{hk}'] += 1
        if hk in ('enemy_head', 'enemy'):
            beyond = d > 3
            out[f'{hk}_n'] += 1; out[f'{hk}_beyond'] += beyond
            if s.get('hit') == q.get('B' if s['team'] == 'A' else 'A'):
                out[f'{hk}_queen'] += 1; out[f'{hk}_queen_beyond'] += beyond
            dist.append(d)
        if s['team'] == 'A' or s['team'] == 'B':
            out['ray_len_sum'] += d
    return out, dist

ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=60); ap.add_argument('--time', type=float, default=140)
a = ap.parse_args(); t0 = time.time()
ids = []
for line in open(CORPUS / 'index.jsonl'):
    m = json.loads(line)
    if m.get('status') == 'completed' and m.get('ranked') and (m.get('started_at') or '') >= '2026-10-02T03:49' and (CORPUS / 'replays' / f"{m['game_id']}.replay").exists():
        ids.append(m['game_id'])
ids = ids[7::max(1, len(ids) // a.n)][:a.n]
tot = collections.Counter(); D = []
with ProcessPoolExecutor(4) as ex:
    fs = [ex.submit(one, i) for i in ids]
    n = 0
    for f in as_completed(fs):
        try: c, d = f.result(); tot += c; D += d; n += 1
        except Exception as e: print('ERR', e)
        if time.time() - t0 > a.time: ex.shutdown(wait=False, cancel_futures=True); break
print('games', n, dict(tot))
import statistics
if D: print('enemy-hit ray Chebyshev length: median', statistics.median(D), 'p90', sorted(D)[int(.9 * len(D))], 'share>3', sum(x > 3 for x in D) / len(D))
