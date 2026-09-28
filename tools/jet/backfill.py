"""Recompute replay metrics for results rows lacking them."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ouroboros'))
import replaystats
out = Path(sys.argv[1]).resolve(); rows = [json.loads(l) for l in open(out / 'results.jsonl')]
n = 0
for r in rows:
    if 'me' in r or 'error' in r: continue
    rp = out / 'replays' / (r['key'].replace('|', '__').replace('/', '_') + '.replay')
    if not rp.exists(): continue
    s = replaystats.analyse(str(rp))
    me, th = (s['teams']['A'], s['teams']['B']) if r['seat'] == 'A' else (s['teams']['B'], s['teams']['A'])
    comp = lambda t: {k: t[k] for k in ('deaths', 'len_lost', 'splits', 'pearls', 'h2h_up', 'h2h_even', 'h2h_down', 'peak_units', 'curve')}
    r['me'], r['them'] = comp(me), comp(th); n += 1
with open(out / 'results.jsonl', 'w') as f:
    for r in rows: f.write(json.dumps(r) + '\n')
print('backfilled', n)
