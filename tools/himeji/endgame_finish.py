"""Inspect an existing replay's final snapshots/events; official header is outcome truth.
python endgame_finish.py REPLAY HIMEJI_CHECKOUT OUTPUT_JSON
"""
import json
from pathlib import Path
import sys

sys.path.insert(0,sys.argv[2])
from tools.analysis.features import frame as F
from tools.antioch.era import header

p=Path(sys.argv[1]);g=F.decode(p)
out=dict(game=int(p.stem),header=header(p),snapshots=[],events={})
for rnd in range(490,len(g['rounds'])):
    snap=g['rounds'][rnd]
    out['snapshots'].append(dict(round=rnd,teams={t:dict(
        total=sum(len(b) for tm,b in snap.values() if tm==t),
        leaders=sorted([(i,len(b)) for i,(tm,b) in snap.items() if tm==t],key=lambda v:-v[1])[:3])
        for t in ['A','B']}))
for k in ['splits','deaths','actions','eats']:
    out['events'][k]=[r for r in g['events'][k] if r['round']>=490 and
                      (k!='actions' or r['kind']=='split' or r.get('steps',0)>1)]
Path(sys.argv[3]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out['header']))
