"""P-hinata-06 stage 1: select games, attach opponent elo, decode replays -> build/hinata/p06/rows.csv (resumable)."""
import json, gzip, csv, sys, os, time, bisect, tempfile
from pathlib import Path
sys.path.insert(0, '.')
from tools.analysis.features import frame
SUBS = {'14585', '16979', '17388', '17530'}
MAP_SWITCH = '2026-10-02T03:49:00'
OUT = Path('build/hinata/p06'); OUT.mkdir(parents=True, exist_ok=True)
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 140
shard, nshard = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
t0 = time.time()
sel_p = OUT / 'sel.json'
if not sel_p.exists():
    sel = []
    for l in open('public_replays/corpus/index.jsonl'):
        if '"team_a": 7,' not in l and '"team_b": 7,' not in l: continue
        r = json.loads(l)
        if not (r.get('ranked') and r.get('status') == 'completed' and (r.get('started_at') or '') >= MAP_SWITCH): continue
        us = 'A' if r['team_a'] == 7 else 'B'
        sub = str(r['bot_a'] if us == 'A' else r['bot_b'])
        if sub not in SUBS: continue
        sel.append(dict(gid=r['game_id'], series=r['series_id'], start=r['started_at'], map=r['map_name'], us=us, sub=sub,
                        opp=r['team_b'] if us == 'A' else r['team_a'], winner=r['winner']))
    snaps = sorted(Path('public_replays/corpus/ladder').glob('*.json'))
    keys = [p.stem for p in snaps]  # 20261005T093546Z
    cache = {}
    for s in sel:
        k = s['start'][:19].replace('-', '').replace(':', '') + 'Z'
        i = bisect.bisect_right(keys, k) - 1
        if i < 0: s['opp_elo'] = ''; continue
        if i not in cache: cache[i] = {t['id']: t['elo'] for t in json.load(open(snaps[i]))}
        s['opp_elo'] = cache[i].get(s['opp'], ''); s['snap'] = keys[i]
    json.dump(sel, open(sel_p, 'w'))
sel = json.load(open(sel_p))
# priority (P-06 matched design): all trial-sub games, then 14585 games against opponents any trial sub met
trial_opps = {x['opp'] for x in sel if x['sub'] != '14585'}
sel = [x for x in sel if x['sub'] != '14585' or x['opp'] in trial_opps]
sel = [x for x in sel if x['gid'] % nshard == shard]
rows_p = OUT / f'rows_s{shard}.csv'
done = set()
for q in OUT.glob('rows*.csv'):
    done |= {r['gid'] for r in csv.DictReader(open(q))}
F = ['gid', 'series', 'start', 'map', 'sub', 'opp', 'opp_elo', 'us', 'won', 'reason', 'last_round', 'q_us', 'q_them', 'L_us', 'L_them',
     'u100_us', 'u100_them', 'len100_us', 'len100_them', 'lng100_us', 'lng100_them']
new = not rows_p.exists()
fh = open(rows_p, 'a', newline=''); w = csv.DictWriter(fh, F)
if new: w.writeheader()
n = 0
for s in sel:
    if str(s['gid']) in done: continue
    if time.time() - t0 > budget: break
    p = Path(f"public_replays/corpus/replays/{s['gid']}.replay")
    row = {k: s.get(k, '') for k in F}
    if not p.exists():
        row['reason'] = 'MISSING'; w.writerow(row); continue
    with tempfile.NamedTemporaryFile(suffix='.replay', dir='/tmp', delete=False) as tf:
        tf.write(gzip.decompress(p.read_bytes())); tn = tf.name
    try:
        fr = frame.decode(tn)
    except Exception as e:
        row['reason'] = 'DECODE_ERR'; w.writerow(row); os.unlink(tn); continue
    os.unlink(tn)
    us = s['us']; them = 'B' if us == 'A' else 'A'; f = fr['final']
    row.update(won=int(fr['winner'] == us), reason=fr['reason'], last_round=fr['last_round'], q_us=f[us]['queen'], q_them=f[them]['queen'],
               L_us=f[us]['longest'], L_them=f[them]['longest'])
    R = fr['rounds']; rr = R[min(100, len(R) - 1)]
    for side, tag in ((us, 'us'), (them, 'them')):
        tm = 0 if side == 'A' else 1
        bodies = [b for (t, b) in rr.values() if t in (side, tm)]
        row[f'u100_{tag}'] = len(bodies); row[f'len100_{tag}'] = sum(map(len, bodies)); row[f'lng100_{tag}'] = max(map(len, bodies), default=0)
    w.writerow(row); n += 1
fh.close()
print('decoded', n, 'total', len(done) + n, 'of', len(sel), f'{time.time()-t0:.0f}s')
