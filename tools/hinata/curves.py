"""P-hinata-07 stage 1: select populations (frozen in the card), decode replays -> per-team per-round rows (resumable).
Usage: python3 tools/hinata/curves.py BUDGET_S SHARD NSHARD"""
import json, gzip, sys, os, time, bisect, tempfile
from pathlib import Path
sys.path.insert(0, '.')
from tools.analysis.features import frame
POST, CUT, REF_END = '2026-10-02T03:49:00', '2026-10-05T11:24:00', '2026-10-05T02:13:00'
OUT = Path('build/hinata/curves'); OUT.mkdir(parents=True, exist_ok=True)
GRID = list(range(0, 500, 25))
budget = float(sys.argv[1]); sh, ns = int(sys.argv[2]), int(sys.argv[3]); t0 = time.time()
sel_p = OUT / 'sel.json'
if not sel_p.exists():
    snaps = sorted(Path('public_replays/corpus/ladder').glob('*.json')); keys = [p.stem for p in snaps]; cache = {}
    def snap(start):
        i = bisect.bisect_right(keys, start[:19].replace('-', '').replace(':', '') + 'Z') - 1
        if i not in cache:
            d = json.load(open(snaps[i])); nd = sorted([t for t in d if not t.get('dev')], key=lambda t: -t['elo'])
            cache[i] = ({t['id'] for t in nd[:10]}, {t['id']: t['elo'] for t in d}, keys[i])
        return cache[i]
    ours = {'14585': [], '17388': [], '17530': []}; top = []
    for l in open('public_replays/corpus/index.jsonl'):
        r = json.loads(l)
        st = r.get('started_at') or ''
        if not (r.get('ranked') and r.get('status') == 'completed' and POST <= st < CUT): continue
        t10, elo, k = snap(st)
        base = dict(gid=r['game_id'], series=r['series_id'], start=st, snap=k, elo_a=elo.get(r['team_a']), elo_b=elo.get(r['team_b']),
                    team_a=r['team_a'], team_b=r['team_b'])
        if 7 in (r['team_a'], r['team_b']):
            us = 'A' if r['team_a'] == 7 else 'B'; sub = str(r['bot_a'] if us == 'A' else r['bot_b'])
            if sub in ours and (sub != '14585' or st < REF_END): ours[sub].append(dict(base, pop=sub, us=us))
        elif r['team_a'] in t10 and r['team_b'] in t10:
            top.append(dict(base, pop='top10', us=''))
    ours['14585'] = sorted(ours['14585'], key=lambda s: s['start'])[-300:]
    sel = sum(ours.values(), []) + top
    json.dump(sel, open(sel_p, 'w'))
sel = [s for s in json.load(open(sel_p)) if s['gid'] % ns == sh]
done = set()
for q in OUT.glob('g_s*.jsonl'):
    done |= {json.loads(l)['gid'] for l in open(q)}
fh = open(OUT / f'g_s{sh}.jsonl', 'a'); n = 0
def queen_ids(maptext):
    """Each team's queen = its lowest initial dragon id (ids follow the map's DRAGON lines; frame.decode builds teams the same way)."""
    q = {}
    for i, (t, b) in enumerate(frame.terrain(maptext)[0]['dragons']): q.setdefault(t, i)
    return q
def side(R, t, q):
    bodies = [b for (tt, b) in R.values() if tt == t]
    return [len(bodies), sum(map(len, bodies)), max(map(len, bodies), default=0), int(q in R), len(R[q][1]) if q in R else 0]
for s in sel:
    if s['gid'] in done: continue
    if time.time() - t0 > budget: break
    p = Path(f"public_replays/corpus/replays/{s['gid']}.replay")
    if not p.exists(): fh.write(json.dumps(dict(s, err='MISSING')) + '\n'); continue
    with tempfile.NamedTemporaryFile(suffix='.replay', dir='/tmp', delete=False) as tf:
        tf.write(gzip.decompress(p.read_bytes())); tn = tf.name
    try: fr = frame.decode(tn)
    except Exception: fh.write(json.dumps(dict(s, err='DECODE')) + '\n'); os.unlink(tn); continue
    try: QID = queen_ids(frame._reader(tn).object(0, 0).text(0))
    finally: os.unlink(tn)
    R = fr['rounds']; out = dict(s, winner=fr['winner'], reason=fr['reason'], last_round=fr['last_round'], final=fr['final'], map=fr['map'])
    for t in 'AB':
        q = QID.get(t, -1)  # fix 2026-10-05 (Sugawara review): ids follow the map's DRAGON lines, not the seat
        out['c' + t] = {str(r): side(R[r], t, q) for r in GRID if r < len(R) - 1}
        out['c' + t]['end'] = side(R[-1], t, q)
    fh.write(json.dumps(out) + '\n'); fh.flush(); n += 1
print('shard', sh, 'decoded', n, 'done_before', len(done), 'of_all', len(json.load(open(sel_p))), f'{time.time()-t0:.0f}s')
