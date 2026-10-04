"""Audit raw no-static-bed pearl events; preserve decoder attribution uncertainty."""
import argparse,json,sys,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
p=a.repo/'public_replays/corpus/replays/997644.replay';root=F._reader(p).object(0,0);g=F.decode(p);m,*_=F.terrain(root.text(0));cells={(2,1),(2,2),(3,1),(3,2)}
history=[];matches=[];rnd=-1
for e in root.items(3):
    kind=e.num(0,'H');o=e.child(0)
    if kind==0:rnd=o.num()
    record={'round':rnd,'kind':kind,'value':o.num()}
    if kind in [2,3]:record['cell']=(o.child(0).num(),o.child(0).num(4))
    if kind==3:record['has_pearl']=bool(o.num(0,'B')&1)
    history.append(record)
    if kind==3 and record['has_pearl'] and record['cell']==(3,1) and rnd==267:matches.append(history[-7:])
out={'game':997644,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'static_tiles':{str(c):m['tiles'].get(c) for c in cells},'spawns':[e for e in g['events']['spawns'] if tuple(e['cell']) in cells],'countdowns':[e for e in g['events']['countdowns'] if tuple(e['cell']) in cells],'raw_event_context':matches,'limitation':'FRAME_VERSION7 assigns bed to non-adjacent-death pearl appearance by default. A bed label here is not evidence of a static bed or known spawning cause.'}
a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
