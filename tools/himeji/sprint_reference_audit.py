"""Read-only re-cut of a frozen Shenzhen sprint sample; no norm/store writes."""
import argparse,hashlib,json,sys
from pathlib import Path
import duckdb,numpy as np,pandas as pd
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--frozen-rows',type=Path);a=ap.parse_args();c=duckdb.connect();c.execute('set threads=1')
a.snapshot.mkdir(parents=True,exist_ok=True)
if a.frozen_rows:
 d=pd.read_json(a.frozen_rows,lines=True,convert_dates=False);files=[]
else:
 files=sorted((a.repo/'build/shenzhen/qpay').glob('part-*.parquet'));d=c.execute('select distinct on (game,side) * from read_parquet(?)',[list(map(str,files))]).df()
 lean=c.execute("select distinct on (game,side) game,side,reason from read_parquet(?,union_by_name=true)",[list(map(str,sorted((a.repo/'build/shenzhen/lean').glob('part-*.parquet'))))]).df();d=d.merge(lean,on=['game','side'],validate='one_to_one')
 idx={str(x['game_id']):x for x in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};ld=json.loads((a.snapshot/'ladder.json').read_text());top={str(x['id']) for x in ld if x.get('rank') and x['rank']<=10 and not x.get('dev')}
 for k in ['ranked','series_id','started_at','map_name','map_hash']:d[k]=d.game.map(lambda g:idx[str(g)].get(k))
 d['block']=d.series_id.fillna(d.game).astype(str);d['cohort']=d.team.map(lambda x:'us' if str(x)=='7' else 'top10' if str(x) in top else 'other');d['q_paid']=d.q_paid.fillna(0);d['q_multi']=d.q_multi.fillna(0);d['q_moves']=d.q_moves.fillna(0)
d.to_json(a.snapshot/'sprint-rows.jsonl',orient='records',lines=True)
res=[]
for (ranked,cohort),g in d.groupby(['ranked','cohort']):
 for alive in [False,True]:
  z=g[g.q_alive_end] if alive else g
  if not len(z):continue
  blocks=list(z.groupby('block'));rng=np.random.default_rng(1919);boot=[]
  for _ in range(1000):
   bs=[blocks[i][1] for i in rng.integers(len(blocks),size=len(blocks))];p=pd.concat(bs);boot.append([p.q_paid.mean(),(p.q_paid>0).mean()])
  ci=np.quantile(boot,[.025,.975],axis=0)
  res.append(dict(ranked=bool(ranked),cohort=cohort,condition='terminal queen alive' if alive else 'all selected sides',sides=len(z),games=z.game.nunique(),series=z.block.nunique(),q_paid_mean=z.q_paid.mean(),q_paid_mean_ci95=ci[:,0].tolist(),ever_pay_share=(z.q_paid>0).mean(),ever_pay_ci95=ci[:,1].tolist(),q_multi_share=z.q_multi.sum()/z.q_moves.sum() if z.q_moves.sum() else None))
summary={'games':int(d.game.nunique()),'sides':len(d),'reason_counts':d.groupby('reason').size().to_dict(),'mode_games':d.groupby('ranked').game.nunique().to_dict(),'started_min':d.started_at.min(),'started_max':d.started_at.max(),'results':res,'free_steps':{str(L):(L+3)//4 for L in range(2,22)},'frozen_input_sha256':hashlib.sha256(a.frozen_rows.read_bytes()).hexdigest() if a.frozen_rows else None,'source_parts':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'method':'Selected qpay sample; frozen current ladder and index; series bootstrap1000 seed1919, descriptive selection-conditional CI; no causal inference. Queen survival condition is post-outcome selection. Modes separated; reasons enumerated, not inferred from R.'}
(a.snapshot/'sprint-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
