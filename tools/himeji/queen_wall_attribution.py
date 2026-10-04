"""Selected live-queen wall deaths: exact TurnStart occupancy; read-only, no bot execution."""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--rows',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
out=[]
def pt(o):return(o.num(),o.num(4))
for meta in json.loads(a.rows.read_text()):
 p=a.repo/'public_replays/corpus/replays'/f"{meta['game_id']}.replay";assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256'];root=F._reader(p).object(0,0);mt=root.text(0);assert hashlib.sha256(mt.encode()).hexdigest()==meta['map_hash'];g=F.decode(p);assert g['winner'].lower()==meta['winner'];side='A' if meta['team_a']==7 else 'B';q=min(i for i,(t,b) in g['rounds'][0].items() if t==side);death=next(x for x in g['events']['deaths'] if x['id']==q);splits=[x for x in g['events']['splits'] if x['parent']==q and x['round']<=death['round']];actions=[x for x in g['events']['actions'] if x['id']==q and death['round']-8<=x['round']<=death['round']];m,W,H,nbr,*_=F.terrain(mt);body={i:collections.deque(b) for i,(t,b) in enumerate(m['dragons'])};teams={i:t for i,(t,b) in enumerate(m['dragons'])};live=set(body);rnd=-1;turns=[]
 for e in root.items(3):
  k=e.num(0,'H');o=e.child(0);i=o.num()
  if k==0:
   rnd=i
   if rnd>death['round']:break
  elif k==9:
   b=body[i];head,tail=pt(o.child(0)),pt(o.child(1))
   if b[0]!=head:b.appendleft(head)
   while len(b)>1 and b[-1]!=tail:b.pop()
  elif k==10:
   child=o.num(4);teams[child]=teams[i];live.add(child);body[i]=collections.deque(pt(x) for x in o.items(0));body[child]=collections.deque(pt(x) for x in o.items(1))
  elif k==11:live.discard(i)
  elif k==1 and i==q and death['round']-8<=rnd<=death['round']:
   b=tuple(body[q]);occ={c:j for j in live if j!=q for c in body[j]};ds=[]
   for dr,dest in enumerate(nbr[b[0]]):
    j=occ.get(dest);kind='wall' if dest is None else 'own_body' if dest in b else ('ally_head' if dest==body[j][0] else 'ally_body') if j is not None and teams[j]==side else ('enemy_head' if dest==body[j][0] else 'enemy_body') if j is not None else 'empty'
    ds.append({'dir':F.DIRS[dr],'dest':dest,'occupancy':kind,'occupant':j})
   turns.append({'round':rnd,'queen_body_head_first':b,'own_units':sum(teams[j]==side for j in live),'directions':ds})
 rec={'game':meta['game_id'],'series':meta['series_id'],'ranked':meta['ranked'],'started_at':meta['started_at'],'map':g['map'],'map_hash':meta['map_hash'],'submission':root.text(1 if side=='A' else 2),'own_side':side,'queen_id':q,'W':W,'H':H,'feed_from_source':500-40-int((W+H)*.6),'death':death,'last_splits':splits[-3:],'actions':actions,'turns':turns,'replay_sha256':meta['sha256'],'official_winner':g['winner']};out.append(rec);print(meta['game_id'],rec['submission'],death['round'],death['cause'],turns[-1] if turns else None,flush=True)
a.out.write_text(json.dumps({'rows':out,'scope':'Purposive four-case attribution check; not prevalence or causal bot-policy effect. Occupancy is omniscient exact TurnStart, not proof of observed state. Empty first step is not proof of a safe multi-step future.'},indent=2)+'\n')
