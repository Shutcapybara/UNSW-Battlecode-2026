"""Read-only case-control event evidence for queen-safety and delayed-growth hypotheses."""
import argparse,collections,hashlib,json,sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--audit',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
 idx={r['game_id']:r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};nr={int(r['game']):r for r in map(json.loads,(a.audit/'audit/nara-own-rows.jsonl').read_text().splitlines())};hdr={r['game']:r for r in map(json.loads,(a.audit/'audit/live-header-rows.jsonl').read_text().splitlines())}
 candidates=[gid for gid,r in nr.items() if r['q_death_round']==0];candidates.append(995611)
 controls=[]
 for sub in ['14265','14585']:
  for mode in [True,False]:
   rr=[gid for gid,r in hdr.items() if r['submission']==sub and r['ranked']==mode and r['map']=='Schooltime' and nr[gid]['q_death_round']!=0]
   controls.extend(sorted(rr,key=lambda g:hashlib.sha256(str(g).encode()).hexdigest())[:2])
 growth=[r for r in idx.values() if r['ranked'] and r['started_at']>='2026-10-03T00:00' and r['map_name'] in ['Maze','Slithery Fight'] and {306,91}&{r['team_a'],r['team_b']}]
 selected=sorted(set(candidates+controls+[r['game_id'] for r in growth]));manifest={'index_sha256':hashlib.sha256((a.snapshot/'index.jsonl').read_bytes()).hexdigest(),'cases':candidates,'controls':controls,'growth_games':[r['game_id'] for r in growth],'growth_selection':'All collected ranked 306/91 Maze/Slithery games started >=2026-10-03T00:00 in this immutable snapshot, without outcome selection','control_selection':'Two smallest SHA256(game_id) per submission/mode among prior-audited Schooltime games with queen death !=0','source_prior_headers_sha256':hashlib.sha256((a.audit/'audit/live-header-rows.jsonl').read_bytes()).hexdigest()}
 (a.snapshot/'hypothesis-selection.json').write_text(json.dumps(manifest,indent=2)+'\n');outfile=a.snapshot/'hypothesis-rows.jsonl';done={r['game'] for r in map(json.loads,outfile.read_text().splitlines())} if outfile.exists() else set()
 for i,gid in enumerate(selected):
  if gid in done:continue
  meta=idx[gid];path=a.repo/'public_replays/corpus/replays'/f'{gid}.replay';assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256'];g=F.decode(path);assert g['winner'].lower()==meta['winner'];root=F._reader(path).object(0,0);ev=g['events'];R=g['rounds'];sides=[]
  for side,tid in [('A',meta['team_a']),('B',meta['team_b'])]:
   q=min(i for i,(s,b) in R[0].items() if s==side);acts=[e for e in ev['actions'] if e['id']==q];death=next((d for d in ev['deaths'] if d['id']==q),None);splits=[s for s in ev['splits'] if s['parent']==q];eats=[e for e in ev['eats'] if e['id']==q];head=R[0][q][1][0];occ={pos for _,body in R[0].values() for pos in body};dest=[g['nbr'][head][d] for d in range(4)];empty=[d for d,to in enumerate(dest) if to is not None and to not in occ];cp={}
   for t in [0,25,50,100,200,250,300,400,490]:
    reach=g['last_round']>=t;body=R[t].get(q) if reach else None;cp[str(t)]={'reached':reach,'alive':body is not None if reach else None,'length':len(body[1]) if body else 0 if reach else None}
   assert g['final'][side]['queen']==(len(R[-1][q][1]) if q in R[-1] else 0)
   sides.append(dict(team=tid,side=side,queen=q,submission=root.text(1 if side=='A' else 2),spawn_body=R[0][q][1],spawn_destinations=dest,initial_empty_one_step_directions=empty,initial_actions=[e for e in acts if e['round']==0],death=death,checkpoints=cp,final=g['final'][side],queen_splits_before100=sum(e['round']<100 for e in splits),queen_splits_after300=sum(e['round']>=300 for e in splits),queen_splits=splits,queen_food_before300=dict(collections.Counter(e['origin'] for e in eats if e['round']<300)),queen_food_after300=dict(collections.Counter(e['origin'] for e in eats if e['round']>=300)),queen_moves_after300=sum(e['kind']=='move' and e['round']>=300 for e in acts)))
  out=dict(game=gid,map=g['map'],map_hash=g['map_hash'],started_at=meta['started_at'],ranked=meta['ranked'],series=meta['series_id'],winner=g['winner'],reason=g['reason'],last_round=g['last_round'],sha256=meta['sha256'],case=gid in candidates,control=gid in controls,growth=gid in manifest['growth_games'],sides=sides)
  with outfile.open('a') as f:f.write(json.dumps(out)+'\n')
  print(i+1,len(selected),gid,flush=True)
if __name__=='__main__':main()
