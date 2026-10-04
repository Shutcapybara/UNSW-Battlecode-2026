from pathlib import Path
import json,hashlib,importlib.util,sys,tempfile,contextlib,io,shutil
from types import SimpleNamespace
import numpy as np,pandas as pd
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');O=Path('/tmp/tanaka-r9');O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for f in ['r2_bc.py','r2_battery.py','r2_cnn.py']:shutil.copyfile(R/'tools/hinata'/f,O/f)
sys.path.insert(0,str(O));import r2_battery as B;import r2_cnn as CNN
checks={};a=SimpleNamespace(weighted=False)
with tempfile.TemporaryDirectory(prefix='tanaka-battery-') as td:
 td=Path(td);d=pd.DataFrame([dict(game=str(i),side='A',dragon=0,round=1,turn=1,map='Dev',team='7',series_key=str(i//10),x_is_queen=1,y_first=0,split='train',blocks_src='oracle',y_kind=0,weight=1.) for i in range(100)]);fk=np.array(['f'+str(i%5) for i in range(100)])
 def write(root,name,p,dd=d):
  run=root/name;run.mkdir(parents=True);P=np.asarray(p)
  with contextlib.redirect_stdout(io.StringIO()):B.write(a,run,dd,None,fk[:len(dd)],{name:P},{'arm':name.split('-')[0],'model_bytes':{name:100}},[],{},['x_is_queen'])
  return run
 def table(root,a0):
  f=root/'table.json'
  with contextlib.redirect_stdout(io.StringIO()):B.table(SimpleNamespace(a0=str(a0),runs=str(root),out=str(f)))
  return json.loads(f.read_text())
 base=np.tile([.01,.97,.01,.01],(100,1));perfect=np.tile([.97,.01,.01,.01],(100,1));p80=perfect.copy();p80[80:]=base[80:]
 root=td/'candidates';root.mkdir();a0=write(root,'A0',base);write(root,'A3-400',p80);write(root,'A10-e4',perfect);write(root,'A7fix-400',perfect)
 tab=table(root,a0);checks['candidate_inventory']={'pooled_constant':list(B.POOLED),'selection':tab['selection'],'rows':[{k:r[k] for k in ['arm','pooled','acc']} for r in tab['rows']],'output_fields':list(tab)}
 root=td/'nan';root.mkdir();a0=write(root,'A0',base);write(root,'A3-400',np.full((100,4),np.nan));checks['nan_predictions']=table(root,a0)['selection']
 root=td/'subset';root.mkdir();a0=write(root,'A0',base);write(root,'A3-400',perfect[:80],d.iloc[:80]);tab=table(root,a0);checks['subset_predictions']={'selection':tab['selection'],'selected_rows':tab['rows'][0]['n'],'baseline_rows':100}
 # Loader negative tests on invented rows only; track every file read.
 fp=td/'features.txt';fp.write_text('x_is_queen\n');tp=td/'teachers.parquet';pd.DataFrame([dict(game='0',side='A',team='7',weight=1.,crank=1,elo=2000)]).to_parquet(tp);rp=td/'rows.parquet';calls=[];read=pd.read_parquet
 def audited_read(p,*args,**kw):calls.append(str(p));return read(p,*args,**kw)
 pd.read_parquet=audited_read
 checks['load_refusal']={}
 for case in ['valid','test','val','heldout']:
  dd=d.iloc[:1].copy()
  if case in ['test','val']:dd['split']=case
  if case=='heldout':dd['map']='Autarky'
  dd.to_parquet(rp)
  try:B.get(SimpleNamespace(rows=str(rp),teachers=str(tp),features=str(fp),side=None,hb_prefix='hb_f_'));result='accepted'
  except (AssertionError,SystemExit) as e:result='refused: '+str(e)
  checks['load_refusal'][case]=result
 pd.read_parquet=read;checks['loader_reads']={'only_invented_paths':all(Path(p).parent==td for p in calls),'paths':sorted(set(calls))}
# Independent learning-curve metric and fixed-key check from published development outputs only.
basep=R/'build/hinata/r2/dev120-enc-s5';base=pd.read_parquet(basep/'oof.parquet');m0=json.loads((basep/'manifest.json').read_text());frl=np.array([0,1,3]);key=['game','side','dragon','round'];bk=pd.MultiIndex.from_frame(base[key]);assert bk.is_unique
hit=lambda d:frl[d[['p_F','p_R','p_L']].to_numpy().argmax(1)]==d.y_first.to_numpy()
bh=hit(base);mask=base.y_first.isin(frl).to_numpy();curve=[];half=None
for frac,name in [(0.1,'lc-f10'),(.25,'lc-f25'),(.5,'lc-f50'),(1.,'dev120-enc-s5')]:
 p=R/'build/hinata/r2'/name;d=pd.read_parquet(p/'oof.parquet');man=json.loads((p/'manifest.json').read_text());idx=pd.MultiIndex.from_frame(d[key]);assert idx.is_unique and set(idx)==set(bk)
 d=d.set_index(key).loc[bk].reset_index();assert np.array_equal(d.y_first,base.y_first);h=hit(d);c={'fraction':frac,'accuracy':float(h[mask].mean()),'rows':len(d),'frl_rows':int(mask.sum()),'same_fold_hashes':man['folds']==m0['folds'],'oof_sha':sha(p/'oof.parquet'),'manifest_sha':sha(p/'manifest.json'),'weighted':man['weighted']};curve.append(c)
 if frac==.5:half=h
v=pd.DataFrame({'s':base.series_key,'d':(bh.astype(float)-half.astype(float))*mask,'n':mask}).groupby('s')[['d','n']].sum();i=np.random.default_rng(7).integers(0,len(v),(1000,len(v)));dd=v.d.to_numpy()[i].sum(1)/v.n.to_numpy()[i].sum(1)
features=(R/'tools/hinata/r2_features_enc_v1.txt').read_text().splitlines();ch,flat,sc=CNN.layout(features)
out={'scope':'Invented battery/loader probes; published development learning-curve OOF only. No fit, real battery selection, frozen confirmation action/winner read, or live outcomes.','hashes':{f:sha(O/f) for f in ['r2_bc.py','r2_battery.py','r2_cnn.py']},'battery':checks,'curve':curve,'curve_full_minus_half':{'delta':float(v.d.sum()/v.n.sum()),'ci':np.percentile(dd,[5,95]).tolist(),'series_positive':int((v.d>0).sum()),'series':len(v)},'cnn_layout':{'channels':len(ch),'planes':len(flat),'scalars':len(sc),'unique_columns':len(set(flat+sc))==len(features)}}
assert checks['nan_predictions']['passes'] and checks['subset_predictions']['selection']['passes']
assert checks['load_refusal']['valid']=='accepted' and all(checks['load_refusal'][x].startswith('refused') for x in ['test','val','heldout'])
assert all(c['same_fold_hashes'] for c in curve)
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
