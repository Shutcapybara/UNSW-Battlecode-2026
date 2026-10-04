from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
R=Path('/Users/alik/Documents/Projects/wt-asahi');O=Path('/tmp/tanaka-r4');out={};frozen=[]
for panel,n in [('pool',272),('gen',464)]:
 arms=[];hashes={}
 for bot,fp in [('asahi-05-kz12-k16','43bd2d4f'),('carthage-05-free-sprint','7df05a3f')]:
  p=R/'build/asahi/runs'/bot/fp/panel/'queen.parquet';hashes[bot]=hashlib.sha256(p.read_bytes()).hexdigest();q=pd.read_parquet(p,columns=['game','side','winner'])
  rr=[]
  for r in q.itertuples():
   seed,mp,a,b=r.game.split('__')
   if seed!='s1' or (a if r.side=='A' else b)!=bot:continue
   rr.append(dict(seed=1,map=mp,opp=b if r.side=='A' else a,seat=r.side,win=1.0 if r.winner==r.side else 0.5 if r.winner in ['draw','Draw'] else 0.0))
  arms.append(pd.DataFrame(rr))
 pair=arms[0].merge(arms[1],on=['seed','map','opp','seat'],suffixes=('_v','_p'),validate='one_to_one');assert len(pair)==n
 pair['d']=pair.win_v-pair.win_p;pair['panel']=panel;frozen.extend(pair.to_dict('records'))
 def interval(keys):
  g=pair.groupby(keys,sort=True).d.agg(['sum','count']);rng=np.random.default_rng(7);ix=rng.integers(0,len(g),(1000,len(g)));v=g['sum'].to_numpy()[ix].sum(1)/g['count'].to_numpy()[ix].sum(1)
  return list(np.percentile(v,[5,95]))
 per=pair.groupby('map').agg(n=('d','size'),wins=('win_v','sum'),parent_wins=('win_p','sum'),net=('d','sum')).reset_index().to_dict('records')
 out[panel]=dict(n=n,net=float(pair.d.sum()),delta=float(pair.d.mean()),clusters=pair.groupby(['map','opp']).ngroups,ci_map_opp=interval(['map','opp']),ci_directional=interval(['map','opp','seat']),ci_map=interval(['map']),per_map=per,input_hashes=hashes)
(O/'k16-seed1-audit.json').write_text(json.dumps(out,indent=2));pd.DataFrame(frozen).to_csv(O/'k16-seed1-pairs.csv',index=False)
print(json.dumps({k:{f:v for f,v in x.items() if f!='per_map'} for k,x in out.items()},indent=2));print([x for x in out['pool']['per_map'] if x['net']])
