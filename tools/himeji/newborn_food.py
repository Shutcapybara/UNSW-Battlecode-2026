"""New endpoint on frozen unit25 selection: child-age food capture and template-cell/provenance confusion.
No simulator, shared cache writes, or API calls. One resumable query worker.
"""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--index',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
sel=json.loads(a.selection.read_text());index={m['game_id']:m for m in map(json.loads,a.index.read_text().splitlines()) if m['game_id'] in sel['games']}
template=a.repo/'maps/live/slithery_fight.map';lines=[l.split() for l in template.read_text().splitlines()];W=next(int(p[1]) for p in lines if p and p[0]=='MAP');beds={(int(p[1])%W,int(p[1])//W) for p in lines if p and p[0]=='TILE' and len(p)==5 and p[3]=='1'}
path=a.out/'newborn-food.jsonl';done={r['game_id'] for r in map(json.loads,path.read_text().splitlines())} if path.exists() else set()
for gid in sel['games']:
 if gid in done:continue
 m=index[gid];p=a.repo/'public_replays/corpus/replays'/f'{gid}.replay';assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];g=F.decode(p);root=F._reader(p).object(0,0);assert hashlib.sha256(root.text(0).encode()).hexdigest()==m['map_hash'];assert g['winner'].lower()==m['winner'];assert g['last_round']>=399
 births={e['child']:e['round'] for e in g['events']['splits']};rows=[]
 for side in 'AB':
  if m['team_a' if side=='A' else 'team_b']==7:assert g['bot'+side]=='14585'
  for start,end in [(0,250),(250,400)]:
   count=collections.Counter();cross=collections.Counter();perchild=collections.Counter();actions=collections.Counter()
   for e in g['events']['eats']:
    if e['team']!=side or not start<=e['round']<end:continue
    born=births.get(e['id']);kind='initial' if born is None else ('child_age0_9' if e['round']-born<10 else 'child_age10plus')
    assert born is None or e['round']>=born
    count[(kind,e['origin'])]+=1;cross[('template_bed' if tuple(e['cell']) in beds else 'template_other',e['origin'])]+=1
    if born is not None and start<=born<end:perchild[(e['id'],e['origin'])]+=1
   for e in g['events']['actions']:
    if e['team']!=side or not start<=e['round']<end:continue
    born=births.get(e['id']);kind='initial' if born is None else ('child_age0_9' if e['round']-born<10 else 'child_age10plus');actions[kind]+=1
   rows.append(dict(side=side,start=start,end=end,food=[dict(age_group=k,origin=o,n=n) for (k,o),n in sorted(count.items())],template_cross=[dict(cell_type=k,origin=o,n=n) for (k,o),n in sorted(cross.items())],action_turns=dict(actions),born_in_window=sum(e['team']==side and start<=e['round']<end for e in g['events']['splits']),born_in_window_bed_eaters=len({i for (i,o),n in perchild.items() if o=='bed'}),born_in_window_bed_meals=sum(n for (i,o),n in perchild.items() if o=='bed'),born_in_window_all_meals=sum(perchild.values())))
 rec=dict(game_id=gid,series_id=m['series_id'],map_hash=m['map_hash'],ranked=m['ranked'],team_a=m['team_a'],team_b=m['team_b'],bot_a=g['botA'],bot_b=g['botB'],last_round=g['last_round'],winner=g['winner'],source_sha256=m['sha256'],rows=rows)
 with path.open('a') as f:f.write(json.dumps(rec,separators=(',',':'))+'\n')
 print(gid,'complete',flush=True)
(a.out/'query-contract.json').write_text(json.dumps(dict(selection_sha256=hashlib.sha256(a.selection.read_bytes()).hexdigest(),decoder_sha256=hashlib.sha256((a.repo/'tools/analysis/features/frame.py').read_bytes()).hexdigest(),template_sha256=hashlib.sha256(template.read_bytes()).hexdigest(),template_beds=len(beds),windows='start-inclusive/end-exclusive; round-start checkpoints',young='new child IDs only, age round-birth 0..9; parents do not become young on split',origin='FRAME7 event provenance, not meal coordinate; no simulator or policy counterfactual',cohort=sel['cohort'],deaths_censoring='All games reach399; child capture only within window, no full-lifetime claim'),indent=2)+'\n')
