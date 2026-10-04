"""Read initial topology of the specifically cited Autarky counterexample; no simulation."""
import argparse,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
p=a.repo/'public_replays/corpus/replays/992701.replay';root=F._reader(p).object(0,0);m,W,H,nbr,beds,ports=F.terrain(root.text(0));out=[];occupied={tuple(c) for team,b in m['dragons'] for c in b}
for side in ['A','B']:
 q=min(i for i,(s,b) in enumerate(m['dragons']) if s==side);body=m['dragons'][q][1];seen={body[0]};queue=list(seen)
 while queue:
  for c in nbr[queue.pop()]:
   if c is not None and c not in seen:seen.add(c);queue.append(c)
 acts=[];rnd=-1
 for e in root.items(3):
  k=e.num(0,'H');o=e.child(0)
  if k==0:rnd=o.num()
  if rnd>0:break
  if k==4 and o.num()==q:acts.append({'round':rnd,'kind':o.child(0).num(0,'H') if o.has(0) else None})
 out.append({'side':side,'queen':q,'body':body,'component_size':len(seen),'component_beds':len(seen & set(beds)),'empty_adjacent':sum(c is not None and c not in occupied for c in nbr[body[0]]),'initial_actions':acts})
a.out.write_text(json.dumps({'game':992701,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sides':out,'limitation':'Initial structural audit only; terminal queen41/winner from unit12 official evidence. No mechanism inferred from map name.'},indent=2)+'\n');print(out)
