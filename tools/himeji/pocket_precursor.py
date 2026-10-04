"""Event-time precursor availability before selected late pocket deaths; no simulation."""
import argparse,collections,hashlib,itertools,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--prior',type=Path,required=True);ap.add_argument('--index',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
idx={r['game_id']:r for r in map(json.loads,a.index.read_text().splitlines())};old=[r for r in json.loads(a.prior.read_text()) if r['death']];rows=[]
def pt(o):return(o.num(),o.num(4))
for gid in sorted({r['game'] for r in old}):
 p=a.repo/'public_replays/corpus/replays'/f'{gid}.replay';reader=F._reader(p);root=reader.object(0,0);m,W,H,nbr,*_=F.terrain(root.text(0));body={i:collections.deque(b) for i,(s,b) in enumerate(m['dragons'])};teams={i:s for i,(s,b) in enumerate(m['dragons'])};live=set(body);pearls=set();rnd=-1;target={r['queen']:r for r in old if r['game']==gid};spawns={};assert hashlib.sha256(p.read_bytes()).hexdigest()==idx[gid]['sha256']
 for en,e in enumerate(root.items(3)):
  k=e.num(0,'H');o=e.child(0);i=o.num()
  if k==0:rnd=i
  elif k==3:
   cell=pt(o.child(0))
   if o.num(0,'B')&1:pearls.add(cell);spawns[cell]=(rnd,en)
   else:pearls.discard(cell)
  elif k==9:
   b=body[i];head,tail=pt(o.child(0)),pt(o.child(1))
   if b[0]!=head:b.appendleft(head)
   while len(b)>1 and b[-1]!=tail:b.pop()
  elif k==10:
   child=o.num(4);teams[child]=teams[i];live.add(child);body[i]=collections.deque(pt(x) for x in o.items(0));body[child]=collections.deque(pt(x) for x in o.items(1))
  elif k==11:live.remove(i)
  elif k==1 and i in target and target[i]['death']['round']-3<=rnd<=target[i]['death']['round']:
   b=tuple(body[i]);other={c for j in live if j!=i for c in body[j]};empty=[(d,c) for d,c in enumerate(nbr[b[0]]) if c is not None and c not in b and c not in other];routes=[]
   for d0,d1 in itertools.product(range(4),repeat=2):
    bb=list(b);ok=True
    for dr in [d0,d1]:
     dest=nbr[bb[0]][dr]
     if dest is None or dest in bb or dest in other or dest in pearls:ok=False;break
     bb.insert(0,dest);bb.pop()
    if ok:routes.append(F.DIRS[d0]+F.DIRS[d1])
   rows.append({'game':gid,'queen':i,'team':target[i]['team'],'side':target[i]['side'],'ranked':idx[gid]['ranked'],'series':idx[gid]['series_id'],'started_at':idx[gid]['started_at'],'round':rnd,'fatal_round':target[i]['death']['round'],'body':b,'units':sum(teams[j]==teams[i] for j in live),'first_unoccupied_steps':[{'direction':F.DIRS[d],'cell':c,'has_pearl':c in pearls,'spawn_round':spawns.get(c,[None])[0] if c in pearls else None} for d,c in empty],'food_free_two_step_routes':routes,'replay_sha256':idx[gid]['sha256']})
a.out.write_text(json.dumps({'rows':rows,'scope':'Four selected late deaths/three games; exact TurnStart omniscient reconstruction, not proof of bot observation. Food-free routes checked with conservative before-tail collision and one ordinary tail removal per empty step, ignoring beneficial second-step paid shrink. Public countdown metadata unavailable.','decoder_sha256':hashlib.sha256(Path(F.__file__).read_bytes()).hexdigest()},indent=2)+'\n');print(json.dumps(rows,indent=2))
