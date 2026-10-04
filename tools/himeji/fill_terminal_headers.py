"""Fill only missing analytical terminal queen values from existing official headers.
Preserve store columns and historical parts; no simulator or API calls.
"""
import argparse,hashlib,json,sys
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('repo','rows','index','out'):p.add_argument('--'+k,type=Path,required=True)
a=p.parse_args();sys.path.insert(0,str(a.repo))
from tools.analysis.features import frame as F
rows=[json.loads(s) for s in a.rows.read_text().splitlines()]
idx={str(m['game_id']):m for m in map(json.loads,a.index.read_text().splitlines())}
missing={r['game'] for r in rows if r['q_end'] is None};out=[]
for gid in sorted(missing):
    m=idx[gid];path=a.repo/'public_replays/corpus/replays'/f'{gid}.replay'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==m['sha256']
    root=F._reader(path).object(0,0);res=root.child(4)
    assert root.num(0,'I')==2 and res.num(0,'B')&1
    winner=('a','b')[res.num(6,'H')] if res.num(4,'H')==1 else 'draw'
    assert winner==m['winner'];assert hashlib.sha256(root.text(0).encode()).hexdigest()==m['map_hash']
    out.append(dict(game=gid,sha256=m['sha256'],map_hash=m['map_hash'],official_winner=winner,queens={s:res.child(k).num(12) for k,s in enumerate('AB')},bots={s:root.text(k+1) for k,s in enumerate('AB')}))
a.out.write_text(json.dumps({'games':out,'scope':'Only missing canonical terminal columns filled from verified official replay headers; no checkpoint inference or store edits.'},indent=2)+'\n');print('Verified missing headers',len(out))
