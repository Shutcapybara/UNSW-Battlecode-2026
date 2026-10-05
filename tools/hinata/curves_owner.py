"""P-hinata-07 correction: per game, each team's queen id from the replay's map text (no round decode). Resumable.
Usage: python3 tools/hinata/curves_owner.py BUDGET_S SHARD NSHARD  -> build/hinata/curves/own_s<SHARD>.jsonl"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, '.')
from tools.analysis.features import frame
sys.path.insert(0, 'tools/hinata'); from curves_qid import queen_ids
D = Path('build/hinata/curves'); budget = float(sys.argv[1]); sh, ns = int(sys.argv[2]), int(sys.argv[3]); t0 = time.time()
gids = [json.loads(l)['gid'] for q in sorted(D.glob('g_s*.jsonl')) for l in open(q)]
gids = [g for g in gids if g % ns == sh]
op = D / f'own_s{sh}.jsonl'; done = {json.loads(l)['gid'] for l in open(op)} if op.exists() else set()
fh = open(op, 'a'); n = 0
for g in gids:
    if g in done: continue
    if time.time() - t0 > budget: break
    try: q = queen_ids(frame._reader(f'public_replays/corpus/replays/{g}.replay').object(0, 0).text(0))
    except Exception as e: q = {'err': str(e)[:80]}
    fh.write(json.dumps(dict(gid=g, q=q)) + '\n'); fh.flush(); n += 1
print('shard', sh, 'new', n, 'left', len(gids) - len(done) - n, f'{time.time()-t0:.0f}s')
