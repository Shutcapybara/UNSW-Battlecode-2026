from pathlib import Path
import importlib.util, json, hashlib, tempfile, copy, contextlib, io, sys, types, shutil
import numpy as np
import pandas as pd
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026'); O=Path('/tmp/tanaka-r6')
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
# R2 invented rows, fake backend, zero actual learning.
r=module('r2',O/'r2_bc.py'); calls={'train':0,'loaded':0}; stub=types.ModuleType('lightgbm')
class Booster:
 def __init__(self,model_file=None):calls['loaded']+=int(model_file is not None)
 def predict(self,x):return np.tile([.7,.1,.1,.1],(len(x),1))
 def save_model(self,p):Path(p).write_text('fake backend, no fitted model')
stub.Booster=Booster;stub.Dataset=lambda *a,**kw:None
def train(*a,**kw):calls['train']+=1;return Booster()
stub.train=train;sys.modules['lightgbm']=stub
rc={}
with tempfile.TemporaryDirectory(prefix='tanaka-r6-r2-') as td:
 td=Path(td); d=pd.DataFrame([dict(game=str(i),side='A',dragon=0,round=1,turn=1,series_key=str(i),map='Dev',split='train',blocks_src='oracle' if i<2 else 'rebuild_redacted',y_kind=0,y_first=0,x_is_queen=1,x_cd_known=1,x_length=3,x_W=99) for i in range(3)])
 rp=td/'rows.parquet';tp=td/'teachers.parquet';fp=td/'features.txt';d.to_parquet(rp);pd.DataFrame([dict(game=str(i),side='A',team='7',weight=1.) for i in range(3)]).to_parquet(tp);fp.write_text('x_is_queen\nx_length\n')
 loaded,feats,drops=r.load([rp],tp,fp);rc['oracle_filter']={'games':loaded.game.tolist(),'features':feats,'drops':drops,'unlisted_identity_ignored':'x_W' not in feats}
 for col in ['x_W','x_H','x_x','x_y','x_xn','x_yn','x_width','x_facing_abs','x_map_id','x_abs_pos','x_missing']:
  fp.write_text(col+'\n')
  try:r.load([rp],tp,fp);rc[col]='accepted'
  except SystemExit as e:rc[col]=str(e)
 fp.write_text('x_is_queen\nx_length\n');argv=['r2_bc.py','fit','--rows',str(rp),'--teachers',str(tp),'--features',str(fp),'--cv','game','--run',str(td/'run'),'--rounds','400']
 def run(args):
  sys.argv=args
  try:
   with contextlib.redirect_stdout(io.StringIO()):r.main()
   return 'accepted'
  except SystemExit as e:return str(e)
 rc['first']=run(argv);first=calls.copy();rc['identical_resume']=run(argv);rc['identical_extra_fake_train_calls']=calls['train']-first['train']
 d.x_length=99;d.to_parquet(rp);rc['changed_rows']=run(argv);d.x_length=3;d.to_parquet(rp);rc['changed_rounds']=run(argv[:-1]+['800']);rc['calls']=calls
 # Deployed FRL normalization can disagree with raw four-class argmax.
 prob=np.array([[.3,.2,.4,.1]]);rc['support_example']={'label':'F','raw_four_class_accuracy':r.acc(np.array([0]),prob)['acc'],'deployed_frl_accuracy':float(np.argmax(prob[:,[0,1,3]],axis=1)[0]==0)}
# Development provenance read only selected metadata/feature flags, no action/outcome labels.
files=[R/f'build/learn/kageyama/teachers_dev120.p{i}.parquet' for i in [0,1]]
dev=pd.concat([pd.read_parquet(p,columns=['game','series_key','map','blocks_src','x_cd_known']) for p in files]); held=json.loads((R/'docs/learning/splits/heldout-maps.json').read_text())['heldout_maps']
dc={'rows':len(dev),'games':int(dev.game.nunique()),'series':int(dev.series_key.nunique()),'maps':sorted(dev['map'].unique()),'heldout_rows':int(dev['map'].isin(held).sum()),'by_source':{k:{'rows':len(v),'games':int(v.game.nunique()),'cd_known_1':int((v.x_cd_known==1).sum())} for k,v in dev.groupby('blocks_src')}}
out={'scope':'Synthetic probes only, mocked numerical score and fake learning backend; real reads limited to frozen membership and development provenance metadata. No real claim, score, heldout outcomes or actions.','hashes':{str(p.relative_to(R)) if p.is_relative_to(R) else p.name:sha(p) for p in [O/'p2_confirm.py',O/'r2_bc.py',m.SPEC_PATH,R/'build/hinata/p2/cell-counts.json',R/'build/hinata/p2/membership-pin.parquet',*files]},'p2':checks,'r2':rc,'dev':dc}
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
