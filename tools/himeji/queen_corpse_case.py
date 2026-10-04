"""Single fresh weakhold mechanism receipt, exact event-time queen entry and corpse donor birth.
No inference of counterfactual survival, policy observations, or causal pearl attraction.
"""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
p=a.repo/'public_replays/corpus/replays/1021321.replay';g=F.decode(p);root=F._reader(p).object(0,0);m,W,H,nbr,*_=F.terrain(root.text(0));q=min(i for i,(t,b) in g['rounds'][0].items() if t=='A')
def pocket(u,v):
 seen={u,v};todo=[v];P=[v]
 while todo:
  for x in nbr[todo.pop()]:
   if x is None or x in seen:continue
   seen.add(x);todo.append(x);P.append(x)
   if len(P)>5:return None
 return P
entry=None
for t in range(1,len(g['rounds'])-1):
 R=g['rounds'];
 if q not in R[t] or q not in R[t+1]:break
 u,v=R[t][q][1][0],R[t+1][q][1][0]
 if v not in nbr[u]:continue
 P=pocket(u,v)
 if P is not None:entry=(t,u,v,P);break
assert entry;t,u,v,P=entry;S=set(P);pearls=g['pearls'][t]&S;orig={}
for e in g['events']['spawns']:
 if e['round']<t and tuple(e['cell']) in pearls:orig[tuple(e['cell'])]=e
donors={e['donor'] for e in orig.values() if e['origin'] in ('A','B')};births={};deaths={e['id']:e for e in g['events']['deaths'] if e['id'] in donors or e['id']==q};bodies={i:collections.deque(b) for i,(tm,b) in enumerate(m['dragons'])};teams={i:tm for i,(tm,b) in enumerate(m['dragons'])};live=set(bodies);r=-1;turn=None
pt=lambda o:(o.num(),o.num(4))
for event in root.items(3):
 k=event.num(0,'H');o=event.child(0);i=o.num()
 if k==0:r=i
 elif k==9:
  head,tail=pt(o.child(0)),pt(o.child(1));b=bodies[i]
  if b[0]!=head:b.appendleft(head)
  while len(b)>1 and b[-1]!=tail:b.pop()
 elif k==10:
  child=o.num(4);teams[child]=teams[i];live.add(child);bodies[i]=collections.deque(pt(x) for x in o.items(0));bodies[child]=collections.deque(pt(x) for x in o.items(1))
  if child in donors:births[child]=dict(round=r,parent=i,child_body=list(bodies[child]),head_in_pocket=bodies[child][0] in S,any_body_in_pocket=bool(set(bodies[child])&S))
 elif k==11:live.discard(i)
 elif k==1 and i==q and r==t:
  occupied={c:j for j in live for c in bodies[j]};turn=dict(round=r,queen_body=list(bodies[q]),directions=[dict(direction=d,cell=c,occupant=occupied.get(c),empty=c is not None and c not in occupied) for d,c in enumerate(nbr[bodies[q][0]])]);break
queen_near_donor_death=[dict(donor=i,death_round=d['round'],queen_head_at_round_start=g['rounds'][d['round']][q][1][0] if q in g['rounds'][d['round']] else None,donor_head=d['head']) for i,d in deaths.items() if i!=q]
out=dict(queen_death_proximity=queen_near_donor_death,game=1021321,map_hash=hashlib.sha256(root.text(0).encode()).hexdigest(),own_submission=g['botA'],queen=q,entry=dict(round=t,from_cell=u,to_cell=v,pocket=P,pearls_at_round_start=list(pearls),pearl_origins=list(orig.values())),exact_turn_start=turn,donor_births=births,donor_deaths=deaths,scope='One new ranked14585 case; starts from peer narrow-pocket selection; actualTurnStart emptiness only, not survival or observations. Corpse snapshots at round-start are not claimed to include same-round pre-queen changes.')
a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
