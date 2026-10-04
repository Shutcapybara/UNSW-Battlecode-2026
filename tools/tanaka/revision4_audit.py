from pathlib import Path
import importlib.util, json, hashlib, tempfile, copy, contextlib, io, sys, types, shutil
import numpy as np
import pandas as pd
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026'); O=Path('/tmp/tanaka-r7'); O.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
for rel in ['tools/hinata/p2_confirm.py','tools/hinata/r2_bc.py']:
 shutil.copyfile(R/rel,O/Path(rel).name)
m=module('p2',O/'p2_confirm.py'); spec=m.load_spec(); checks={}
rows=[dict(population='ranked_clean',regime=reg,round=cp,status='OK',n=100,auc_v=.70,auc_phi=.68,d_auc=.02,d_auc_ci=[.01,.03],slope_v=1.,slope_phi=1.,valid_draws=1000) for _,reg,cp in m.CELLS]
checks['valid_gate']=m.gate(rows,spec,['elim/r10'])['verdict']
for value in [float('nan'),float('inf'),None]:
 for f in ['auc_v','auc_phi','d_auc','slope_v','slope_phi','d_auc_ci']:
  bad=copy.deepcopy(rows); r=next(r for r in bad if r['regime']=='rl' and r['round']==50); r[f]=[value,value] if f=='d_auc_ci' else value
  checks[f'nonfinite/{f}/{value}']=m.gate(bad,spec,['elim/r10'])['verdict']
for n in [989,990]:
 bad=copy.deepcopy(rows); bad[-1]['valid_draws']=n; checks[f'draws/{n}']=m.gate(bad,spec,['elim/r10'])['verdict']
pin=pd.DataFrame({'game':['keep','gone','gone'],'round':[50,50,100]}); got=pin[pin.game=='keep'].copy()
checks['membership']={}
for case,result in [('decisive',{'gone':1.}),('draw',{'gone':.5}),('absent',{}),('null',{'gone':None}),('nan',{'gone':float('nan')}),('invalid',{'gone':2.})]:
 checks['membership'][case]=m.membership(pin,got,result)
checks['partial']=m.membership(pin,pin.iloc[:2],{'gone':.5})['ok']
checks['duplicate']=m.membership(pin,pd.concat([pin,pin.iloc[:1]]),{})['ok']
checks['new']=m.membership(pin,pd.concat([pin,pd.DataFrame({'game':['new'],'round':[50]})]),{})['ok']
# Real store lookup and score preflight on invented data only; metric function deliberately stubbed.
m.evaluate=lambda *a:copy.deepcopy(rows)
for case in ['decisive','draw','absent','null','invalid']:
 with tempfile.TemporaryDirectory(prefix='tanaka-r6-p2-') as td:
  td=Path(td); m.P2=td/'p2';m.P2.mkdir();m.S1=td/'store';m.S1.mkdir()
  data=[dict(game='keep',result_a=1.,in_scope=False)]
  if case!='absent': data.append(dict(game='gone',result_a={'decisive':1.,'draw':.5,'null':None,'invalid':2.}[case],in_scope=False))
  pd.DataFrame(data).to_parquet(m.S1/'games.parquet')
  for sub in ['series','sides']:(m.S1/sub).mkdir()
  view=m.frozen_view(['keep','gone']); v=pd.read_parquet(view/'games.parquet'); checks[f'view/{case}']={'games':v.game.tolist(),'scope_all_true':bool(v.in_scope.all())};shutil.rmtree(view)
  res=m.store_results(['gone']);mem=m.membership(pin,got,res);ph=m.write_pin(pin)
  m._claim(m.SPEC_SHA,sha(m.SELF),['elim/r10'],{k:{'coverage':1.} for k in ['Autarky','Maze','Trauma']},{'pin_sha':ph})
  m._seal(got,mem)
  with contextlib.redirect_stdout(io.StringIO()): g=m.cmd_score(types.SimpleNamespace())
  checks[f'score/{case}']={'verdict':g['verdict'],'incomplete':g.get('incomplete'),'lookup':res}
  try:m.cmd_score(types.SimpleNamespace()); checks[f'second/{case}']='accepted'
  except SystemExit:checks[f'second/{case}']='refused'
# Metadata-only real preclaim evidence. Never invoke real run, counts or score.
pop=pd.read_parquet(R/'build/hinata/p2/population.parquet'); pinreal=pd.read_parquet(R/'build/hinata/p2/membership-pin.parquet'); cc=json.loads((R/'build/hinata/p2/cell-counts.json').read_text())
joined=pinreal.merge(pop[['game','map','ranked','clean']],on='game',validate='many_to_one'); bind=joined[joined.ranked & joined.clean].copy();bind['regime']=np.where(bind['map']=='Autarky','elim','rl')
counts={f'{reg}/r{cp}':len(x) for (reg,cp),x in bind.groupby(['regime','round'])}
checks['preclaim']={'claim_exists':(R/'build/hinata/p2/CLAIM.json').exists(),'coverage':m.coverage(pop,spec),'pin_rows':len(pinreal),'pin_games':int(pinreal.game.nunique()),'pin_duplicates':int(pinreal.duplicated().sum()),'counts_match':counts==cc['counts']['ranked_clean'],'pin_hash_matches':sha(R/'build/hinata/p2/membership-pin.parquet')==cc['pin_sha'],'counts':counts}
# Final immutable-receipt mutations on invented data, with a passing metric stub.
checks['receipt']={}
for case in ['valid','claim','scorer','spec','prediction','pin','membership','coverage','missing_model']:
 with tempfile.TemporaryDirectory(prefix='tanaka-r7-receipt-') as td:
  m.P2=Path(td);ph=m.write_pin(pin);cov={k:{'coverage':1.} for k in ['Autarky','Maze','Trauma']}
  if case=='coverage':cov['Maze']['coverage']=.94
  extra={'pin_sha':ph}
  if case=='missing_model':extra['missing_cells']=[['post-m2','rl',50]]
  cf=m._claim(m.SPEC_SHA,'bad' if case=='scorer' else sha(m.SELF),['elim/r10'],cov,extra)
  pf=m._seal(pin,m.membership(pin,pin,{}));sp=m.SPEC_PATH
  if case=='claim':cf.write_text(cf.read_text()+' ')
  if case=='spec':sp=Path(td)/'spec.json';sp.write_text(m.SPEC_PATH.read_text()+' ')
  if case in ['prediction','pin','membership']:
   f={'prediction':pf,'pin':Path(td)/'membership-pin.parquet','membership':Path(td)/'membership.json'}[case];f.chmod(0o644);f.write_bytes(f.read_bytes()+b' ')
  try:
   with contextlib.redirect_stdout(io.StringIO()):g=m.cmd_score(types.SimpleNamespace(),spec_path=sp,results={})
   checks['receipt'][case]=g['verdict']
  except Exception as e:
   checks['receipt'][case]='REFUSED_EXCEPTION'
   checks['receipt_exception_'+case]=type(e).__name__
# Gate threshold boundary and incomplete cases, no real metrics/data.
checks['gate_boundaries']={}
for case in ['missing','one_class','all_lb_equal','late_lb_equal','slope_equal','slope_over','rl50_lower','absolute_floor_report']:
 rr=copy.deepcopy(rows);target=next(x for x in rr if x['regime']=='rl' and x['round']==50)
 if case=='missing':rr.remove(target)
 if case=='one_class':target['status']='UNDEFINED'
 if case=='all_lb_equal':target['d_auc_ci'][0]=-.01
 if case=='late_lb_equal':rr[-1]['d_auc_ci'][0]=0.
 if case=='slope_equal':target['slope_v']=1.;target['slope_phi']=1.05
 if case=='slope_over':target['slope_v']=1.051
 if case=='rl50_lower':target['auc_v']=.67
 if case=='absolute_floor_report':target['auc_v']=.64;target['auc_phi']=.62
 checks['gate_boundaries'][case]=m.gate(rr,spec,['elim/r10'])['verdict']
# File-integrity and source presence metadata only. No held-out results read.
import duckdb
p2=R/'build/hinata/p2'; realpin=pd.read_parquet(p2/'membership-pin.parquet');s1=R/'build/s1/corpus'
ids=duckdb.sql(f"select cast(game as varchar) game,count(*) n from read_parquet('{s1}/games.parquet') group by 1").df()
j=realpin[['game']].drop_duplicates().merge(ids,on='game',how='left')
checks['source_game_metadata']={'missing':int(j.n.isna().sum()),'nonunique':int((j.n>1).sum())}
manifest=json.loads((m.PHI/'MANIFEST.sha256.json').read_text());checks['phi_hashes_match']=all(sha(m.PHI/f)==h for f,h in manifest.items())
ww,wh=m.weights();checks['weights_finite_complete']=all(a is not None and b is not None and m.fin(*a.values(),*b.values()) for a,b in ww.values());checks['weight_hashes']=wh
checks['archive_matches']=sha(m.SRC)==m.SRC_SHA
checks['unchanged_numerics']={}
old=module('oldp2',R/'docs/learning/reviews/tanaka-round4/p2_confirm.py')
import inspect
fresh=module('freshp2',O/'p2_confirm.py')
for f in ['wauc','wslope','evaluate','gate']:
 checks['unchanged_numerics'][f]=inspect.getsource(getattr(fresh,f))==inspect.getsource(getattr(old,f))
# New R2 projection against an independent common-support argmax; development support only.
r=module('r2',O/'r2_bc.py');rng=np.random.default_rng(987);p=rng.dirichlet(np.ones(4),size=1000);y=rng.integers(0,4,size=1000);idx=np.flatnonzero(y!=2);normalized=p[idx][:,[0,1,3]];normalized/=normalized.sum(1)[:,None];expected=np.mean(np.array([0,1,3])[normalized.argmax(1)]==y[idx]);rc={'frl':r.frl(y,p),'independent_accuracy':round(float(expected),4)}
files=[R/f'build/learn/kageyama/teachers_dev120.p{i}.parquet' for i in [0,1]];cols=['game','side','series_key','map','split','blocks_src','y_kind','y_first','x_is_queen']
dev=pd.concat([pd.read_parquet(p,columns=cols) for p in files]);teachers=R/'build/learn/kageyama/teachers_dev120.parquet';t=pd.read_parquet(teachers,columns=['game','side','team']);dev=dev.merge(t,on=['game','side'],validate='many_to_one');dev=dev[(dev.blocks_src=='oracle') & (dev.y_kind==0) & dev.y_first.isin([0,1,2,3])].reset_index(drop=True);mask=dev.y_first!=2;F=r.folds(dev,'series5');support={'rows':len(dev),'frl_rows':int(mask.sum()),'reverse_rows':int((~mask).sum()),'games':int(dev.game.nunique()),'series':int(dev.series_key.nunique()),'teams':int(dev.team.nunique()),'maps':int(dev['map'].nunique()),'queen_frl_rows':int((mask & (dev.x_is_queen==1)).sum()),'per_fold':{k:{'rows':int(te.sum()),'frl_rows':int((te&mask).sum()),'games':int(dev.game[te].nunique()),'series':int(dev.series_key[te].nunique())} for k,te in F.items()}}
owner=json.loads((R/'build/hinata/r2/dev120-enc-s5/support.json').read_text());rc['support']=support;rc['support_matches']=all(owner[k]==v for k,v in support.items());rc['series_overlap']=any(set(dev.series_key[te])&set(dev.series_key[~te]) for te in F.values())
# LS-1: exact arithmetic and frozen seed-1 derived winner rows only. Never live outcomes.
from math import comb
signp=lambda plus,minus:sum(comb(plus+minus,k) for k in range(plus,plus+minus+1))/2**(plus+minus)
ls={'sign_probabilities':{f'{a}-{b}':signp(a,b) for a,b in [(4,0),(5,1),(6,1),(7,2),(8,2),(9,3),(9,4)]}}
pairs=pd.read_csv(R/'docs/learning/reviews/tanaka-round4/k16-seed1-pairs.csv');pool=pairs[pairs.panel=='pool'];ls['local_pool']={'pairs':len(pool),'positive':int((pool.d>0).sum()),'negative':int((pool.d<0).sum()),'zero':int((pool.d==0).sum()),'net':float(pool.d.sum()),'nonzero_clusters':int(pool[pool.d!=0].groupby(['map','opp']).ngroups)}
# Two seats move together within each of two clusters: naive pair sign test rejects with 25% null probability.
ls['dependent_pair_counterexample']={'clusters':2,'perfectly_correlated_seats_per_cluster':2,'naive_p_if_both_positive':signp(4,0),'probability_both_positive_under_independent_cluster_signs':.25,'cluster_flip_p_both_positive':.25}
# Frozen bootstrap counterexample: one positive pair, 101 ties, 51 clusters.
a=np.zeros(51);a[0]=1.;boot=np.random.default_rng(7).integers(0,51,(1000,51));b=a[boot].sum(1)/102;ls['one_positive_101_ties']={'mean':1/102,'interval':np.percentile(b,[5,95]).tolist(),'D055_pass':bool(1/102>0 and np.percentile(b,5)>-.02)}
# Exhaustive sign tests at fixed K under symmetric independent pair signs: single look only.
ls['exact_independent_pair_size']={str(k):sum(comb(k,a) for a in range(k+1) if k>=4 and signp(a,k-a)<=.15)/2**k for k in [2,4,6,10,20]}
out={'scope':'P2 synthetic only and real metadata/file integrity; R2 training-support labels permitted, no training; LS1 arithmetic and already-frozen local seed1 derived outcomes only, no live outcomes.','hashes':{str(p.relative_to(R)) if p.is_relative_to(R) else p.name:sha(p) for p in [O/'p2_confirm.py',O/'r2_bc.py',m.SPEC_PATH,p2/'cell-counts.json',p2/'population.parquet',p2/'membership-pin.parquet',m.PHI/'MANIFEST.sha256.json',*files,teachers]},'p2':checks,'r2':rc,'ls1':ls}
assert checks['score/absent']['verdict']=='INCOMPLETE' and checks['score/null']['verdict']=='INCOMPLETE' and checks['score/invalid']['verdict']=='INCOMPLETE'
assert checks['score/draw']['verdict']=='PASS' and checks['preclaim']['counts_match']
assert all(v in (['PASS'] if k=='valid' else ['INCOMPLETE','REFUSED_EXCEPTION']) for k,v in checks['receipt'].items())
assert checks['phi_hashes_match'] and checks['weights_finite_complete'] and checks['archive_matches']
assert all(checks['unchanged_numerics'].values()) and checks['source_game_metadata']=={'missing':0,'nonunique':0}
assert rc['support_matches'] and rc['frl']['acc']==rc['independent_accuracy'] and not rc['series_overlap']
def clean(v):
 if isinstance(v,float) and not np.isfinite(v):return str(v)
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
 if isinstance(v,list):return [clean(x) for x in v]
 return v
(O/'audit.json').write_text(json.dumps(clean(out),indent=2,allow_nan=False));print(json.dumps({'p2_receipt':checks['receipt'],'missing_fix':{k:v for k,v in checks.items() if k.startswith('score/')},'source_metadata':checks['source_game_metadata'],'r2':rc,'ls1':ls},indent=2))
