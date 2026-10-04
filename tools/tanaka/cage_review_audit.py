import hashlib, importlib.util, json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pandas as pd
import argparse
ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,required=True); ap.add_argument('--asahi',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
R=args.repo; A=args.asahi
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out={'scope':'Read-only Schooltime development outputs, map headers, synthetic rating lookup. No held-out confirmation data.'}
maps=[]
for group in ['live','new','m2tr','var']:
 for p in sorted((R/'maps'/group).glob('*.map')):
  line=p.open().readline().strip(); maps.append({'path':str(p.relative_to(R)),'header':line,'sha256':sha(p)})
out['map_headers']=maps
out['map_60x40']=[m['path'] for m in maps if m['header']=='MAP 60 40']
out['map_40x60']=[m['path'] for m in maps if m['header']=='MAP 40 60']
out['schooltime']={}
for bot,fp in [('asahi-01-cage-cd-e0','c0579163'),('carthage-05-free-sprint','7df05a3f')]:
 p=A/'build/asahi/runs'/bot/fp/'pool/queen.parquet'; b=p.read_bytes(); q=pd.read_parquet(p)
 q=q[q.game.str.contains('__live+schooltime__',regex=False)].copy()
 q=q[q.apply(lambda r:r['game'].split('__')[2 if r['side']=='A' else 3]==bot,axis=1)]
 rows=q[['game','side','queen_end','reason','winner','last_round']].to_dict('records')
 alive=q.queen_end.gt(0); rl=q.reason.ne('elimination')
 out['schooltime'][bot]={'source':str(p),'sha256':hashlib.sha256(b).hexdigest(),'n':len(q),'reached_rl':int(rl.sum()),'alive_at_rl':int((alive&rl).sum()),'alive_at_end':int(alive.sum()),'win':int((q.winner==q.side).sum()),'rows':rows}
p=R/'tools/daichi/live_monitor.py'; s=importlib.util.spec_from_file_location('monitor',p); m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
t=datetime(2026,10,1,tzinfo=timezone.utc); ls=[(t,{7:{'elo':1700}}),(t+timedelta(hours=1),{7:{'elo':1710}})];keys=[x[0] for x in ls]
probes=[('before',t-timedelta(seconds=1),None),('exact',t,1700),('between',t+timedelta(minutes=30),1700),('later',t+timedelta(hours=2),1710)]
out['rating_lookup']={'source_sha256':sha(p),'checks':[{'name':n,'expected':e,'actual':m.rating_at(ls,keys,w,7),'pass':m.rating_at(ls,keys,w,7)==e} for n,w,e in probes]}
out['p2']={'scorer_sha256':sha(R/'tools/hinata/p2_confirm.py'),'spec_sha256':sha(R/'docs/learning/proposals/P-2-gate-spec.D-052.json'),'claim_exists':(R/'build/hinata/p2/CLAIM.json').exists()}
out['proposal_sha256']=sha(R/'docs/learning/proposals/P-sugawara-01-cage-gated-reserve.md')
args.out.write_text(json.dumps(out,indent=2))
print(json.dumps({**{k:v for k,v in out.items() if k not in ['map_headers','schooltime']},'map_count':len(maps),'schooltime':{k:{a:b for a,b in v.items() if a!='rows'} for k,v in out['schooltime'].items()}},indent=2))
