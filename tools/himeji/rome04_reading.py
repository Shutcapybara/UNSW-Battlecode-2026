"""Independent paired Rome04 feature/outcome audit; read-only cached features and official headers."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np,pandas as pd
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--rome',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
out={'sources':{},'panels':{}};allpairs=[]
for panel,prefix,n in [('pool','z1',480),('gen','gen',1392)]:
 ds=[]
 for bot,fp in [('rome-01-nodevil','28132ee5'),('rome-04-queen-head-tie','8304fb79')]:
  root=a.rome/'build/zoo'/f'{prefix}-{bot}-{fp}';p=root/'features/features.parquet';out['sources'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();d=pd.read_parquet(p);d=d[d.bot==bot].copy();dr=pd.read_parquet(root/'features/dragons.parquet');q=dr[dr.initial].sort_values('id').drop_duplicates(['game','side'])[['game','side','id','died']];d=d.merge(q,on=['game','side'],validate='one_to_one');d['queen_alive150_reached']=(d['rounds']>=150)&(d.died.isna()|(d.died>=150));d['reach150']=d['rounds']>=150;d['mapkey']=d.game.str.split('__').str[1];d['seedkey']=d.game.str.split('__').str[0];d['score']=d.result.map({'win':1.,'loss':0.,'draw':.5});assert len(d)==n
  # Header reads only; no decoder/store cache write, no replay download.
  out['sources'][str(root/'index.jsonl')]=hashlib.sha256((root/'index.jsonl').read_bytes()).hexdigest();out['sources'][str(root/'features/dragons.parquet')]=hashlib.sha256((root/'features/dragons.parquet').read_bytes()).hexdigest();ix={r['game']:r for r in map(json.loads,(root/'index.jsonl').read_text().splitlines())};audit=0
  for row in d.head(8).itertuples():
   path=root/ix[row.game]['replay'];res=F._reader(path).object(0,0).child(4);winner=('A','B')[res.num(6,'H')] if res.num(4,'H')==1 else 'draw';score=.5 if winner=='draw' else float(winner==row.side);assert res.num(0,'B')&1 and score==row.score;audit+=1
  d['header_verified']=d.game.isin(d.head(8).game);ds.append(d);print(panel,bot,'headers',audit,flush=True)
 key=['seedkey','mapkey','opponent','side'];p,c=ds;cols=['score','queen_alive150_reached','reach150','rounds','died']+[f'{metric}@{r}' for r in [50,100,150] for metric in ['pearls','units','total','births']];m=p[key+cols].merge(c[key+cols],on=key,suffixes=('_p','_c'),validate='one_to_one');assert len(m)==n;delta=m.score_c-m.score_p;clusters=list(m.groupby(['mapkey','opponent','side']).indices.values());rng=np.random.default_rng(417);boots=[]
 for _ in range(5000):
  ii=np.concatenate([clusters[j] for j in rng.integers(0,len(clusters),len(clusters))]);boots.append(float(delta.iloc[ii].mean()))
 checks={col:int((m[col+'_p'].fillna(-999)!=m[col+'_c'].fillna(-999)).sum()) for col in cols if '@' in col};out['panels'][panel]={'pairs':n,'official_headers_verified':16,'parent_wld':p.result.value_counts().to_dict(),'candidate_wld':c.result.value_counts().to_dict(),'score_delta':delta.mean(),'score95_map_opponent_seat':np.quantile(boots,[.025,.975]).tolist(),'clusters':len(clusters),'changed_scores':int((delta!=0).sum()),'queen_alive150_p':int(m.queen_alive150_reached_p.sum()),'queen_alive150_c':int(m.queen_alive150_reached_c.sum()),'queen150_discordant_pairs':int((m.queen_alive150_reached_p!=m.queen_alive150_reached_c).sum()),'reached150_p':int(m.reach150_p.sum()),'reached150_c':int(m.reach150_c.sum()),'early_fixture_metric_mismatches':checks,'per_map':[{'map':k,'pairs':len(x),'score_delta':float((x.score_c-x.score_p).mean()),'changed_scores':int((x.score_c!=x.score_p).sum())} for k,x in m.groupby('mapkey')]};allpairs+=m[key+['score_p','score_c','queen_alive150_reached_p','queen_alive150_reached_c']].assign(panel=panel).to_dict('records')
for bot in ['rome-01-nodevil','rome-04-queen-head-tie']:
 p=a.rome/'bots'/bot/'policy.hpp';out['sources'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
out['limitation']='Local1.2.3 panels only. Official header preflight is first8 cached rows per arm/panel (32 total), not complete census; all outcomes otherwise from FRAME7 features. First-stage survival uses feature reach>=150 and queen death>=150 or none; no future terminal survival imputation. r150 is pre-treatment because role_crown cannot become true before250. Block bootstrap descriptive fixed-panel uncertainty.'
a.out.write_text(json.dumps(out,indent=2)+'\n');a.out.with_name('rome04-pairs.json').write_text(json.dumps(allpairs,indent=2)+'\n');print(json.dumps(out['panels'],indent=2))
