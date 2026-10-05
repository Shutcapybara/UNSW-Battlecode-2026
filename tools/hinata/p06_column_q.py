"""Secondary of the standing column: decode the window games -> loss reasons and our queen alive at the end. Usage: COLJSON SHARD NSHARD"""
import json, gzip, sys, os, tempfile
from pathlib import Path
sys.path.insert(0, '.')
from tools.analysis.features import frame
col = json.load(open(sys.argv[1])); sh, ns = int(sys.argv[2]), int(sys.argv[3])
idx = {}
want = set(col['gids'])
for l in open('public_replays/corpus/index.jsonl'):
    if '"team_a": 7,' not in l and '"team_b": 7,' not in l: continue
    r = json.loads(l)
    if r['game_id'] in want: idx[r['game_id']] = 'A' if r['team_a'] == 7 else 'B'
out = open(sys.argv[1].replace('.json', f'.q{sh}.jsonl'), 'w')
for gid in sorted(want):
    if gid % ns != sh: continue
    p = Path(f'public_replays/corpus/replays/{gid}.replay')
    if not p.exists(): out.write(json.dumps(dict(gid=gid, err='MISSING')) + '\n'); continue
    with tempfile.NamedTemporaryFile(suffix='.replay', dir='/tmp', delete=False) as tf:
        tf.write(gzip.decompress(p.read_bytes())); tn = tf.name
    try: fr = frame.decode(tn)
    except Exception as e: out.write(json.dumps(dict(gid=gid, err='DECODE')) + '\n'); os.unlink(tn); continue
    os.unlink(tn); us = idx[gid]; them = 'B' if us == 'A' else 'A'
    out.write(json.dumps(dict(gid=gid, won=int(fr['winner'] == us), reason=fr['reason'], last_round=fr['last_round'],
                              q_us=fr['final'][us]['queen'], q_them=fr['final'][them]['queen'])) + '\n')
