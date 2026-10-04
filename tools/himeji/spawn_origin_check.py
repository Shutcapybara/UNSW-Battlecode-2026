"""Raw-event negative control for the template-cell corpse-food proxy."""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
lines=[l.split() for l in (a.repo/'maps/live/slithery_fight.map').read_text().splitlines()];W=next(int(p[1]) for p in lines if p and p[0]=='MAP');beds={(int(p[1])%W,int(p[1])//W) for p in lines if p and p[0]=='TILE' and len(p)==5 and p[3]=='1'};rows=[]
for gid in [852617,887284,999613]:
 root=F._reader(a.repo/'public_replays/corpus/replays'/f'{gid}.replay').object(0,0);prev=None;r=-1;counts=collections.Counter();examples=[];last_countdown=None
 for e in root.items(3):
  k=e.num(0,'H');o=e.child(0)
  if k==0:r=o.num()
  if k==2:last_countdown=(o.child(0).num(),o.child(0).num(4),o.num())
  if k==3 and o.num(0,'B')&1 and 250<=r<400:
   c=(o.child(0).num(),o.child(0).num(4));counts[(prev,'bed' if c in beds else 'other')]+=1
   if prev==0 and c not in beds:
    if len(examples)<8:examples.append(dict(round=r,cell=c,preceding_event='RoundStart',before_any_turn=True,template_bed=False))
  prev=k
 rows.append(dict(game_id=gid,map_hash=hashlib.sha256(root.text(0).encode()).hexdigest(),spawn_previous_event=[dict(kind=k,template_cell=c,n=n) for (k,c),n in sorted(counts.items())],examples=examples))
a.out.write_text(json.dumps(dict(rows=rows,meaning='Positive pearl spawn directly follows RoundStart before any turn or death in that round; template non-bed location alone cannot classify corpse origin.'),indent=2)+'\n');print(json.dumps(rows,indent=2))
