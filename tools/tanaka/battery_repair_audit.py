from pathlib import Path
import hashlib,json,sys,shutil,tempfile,contextlib,io,argparse
from types import SimpleNamespace
import numpy as np,pandas as pd
from scipy.stats import binom,beta
ROOT=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026'); OUT=Path('/tmp/tanaka-r10'); OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser(); ap.add_argument('--sources',type=Path,default=Path(__file__).resolve().parents[2]/'docs/learning/reviews/tanaka-round10'); opts=ap.parse_args()
for f in ['r2_bc.py','r2_battery.py','r2_cnn.py']:shutil.copyfile(opts.sources/f,OUT/f)
sys.path.insert(0,str(OUT));import r2_battery as B
checks={};a=SimpleNamespace(weighted=False)
d=pd.DataFrame([dict(game=str(i),side='A',dragon=0,round=1,turn=1,map='Dev',team=str(i%4+1),series_key=str(i//10),x_is_queen=1,y_first=0,fold='f'+str(i%5)) for i in range(100)])
pbad=np.tile([.01,.97,.01,.01],(100,1));pgood=np.tile([.97,.01,.01,.01],(100,1))
def write(root,name,P,dd=d):
 run=root/name;run.mkdir(parents=True)
 with contextlib.redirect_stdout(io.StringIO()):B.write(a,run,dd,None,dd.fold.to_numpy(),{name:P},{'arm':name.split('-')[0],'model_bytes':{name:1 if name.startswith('A10') else 100}},[],{},['x_is_queen'])
 (run/'manifest.json').write_text(json.dumps({'teams_top3':['1','2','3']}));return run
def table(root,a0):
 f=root/'table.json'
 with contextlib.redirect_stdout(io.StringIO()):B.table(SimpleNamespace(a0=str(a0),runs=str(root),out=str(f)))
 return json.loads(f.read_text())
def attempt(fn):
 try:return {'accepted':True,'result':fn()}
 except (SystemExit,AssertionError,ValueError,IndexError) as e:return {'accepted':False,'reason':str(e)}
with tempfile.TemporaryDirectory(prefix='tanaka-selector-') as td:
 td=Path(td)
 for name in ['nan','inf','bad_sum','negative_sum_one','pooled_subset','duplicate','labels','folds','series','A6_wrong_team','A7_partial','A7_full_only','A2_nan','missing_teacher_inventory','complete']:
  root=td/name;root.mkdir();a0=write(root,'A0',pbad)
  def probe():
   pp=pgood.copy();dd=d.copy();arm='A3-400'
   if name=='nan':pp[0]=np.nan
   if name=='inf':pp[0,0]=np.inf
   if name=='bad_sum':pp[0]=1
   if name=='negative_sum_one':pp[0]=[2,-1,0,0]
   if name=='pooled_subset':dd=dd.iloc[:80];pp=pp[:80]
   if name=='duplicate':dd.iloc[0]=dd.iloc[1]
   if name=='labels':dd.loc[0,'y_first']=1
   if name=='folds':dd.loc[0,'fold']='wrong'
   if name=='series':dd['series_key']='merged'
   if name=='A6_wrong_team':arm='A6-400';m=dd.team.eq('4').to_numpy();dd=dd[m];pp=pp[m]
   if name=='A7_full_only':arm='A7fix-400'
   if name=='A7_partial':arm='A7fix-400';dd=dd.iloc[:20];pp=pp[:20]
   if name=='A2_nan':arm='A2-400';pp[:80]=np.nan
   if name in ['missing_teacher_inventory','complete']:
    for ar in B.PLANNED:
     if name=='missing_teacher_inventory' and ar.split('-')[0] not in B.POOLED:continue
     mask=dd.team.isin(['1','2','3']).to_numpy() if ar.startswith('A6') else np.ones(100,bool)
     write(root,ar,pp[mask],dd[mask])
   else:write(root,arm,pp,dd)
   t=table(root,a0)
   return {'pooled':t['selection'],'teacher':t['teacher_specific']['selection'],'missing':t['missing_planned'],'rows':[{'arm':r['arm'],'rows':r['rows'],'vs_A0':r['vs_A0']} for r in t['rows']]}
  checks[name]=attempt(probe)
 # A lone A7 arm must not advance while other declared teacher arms are absent.
 checks['missing_teacher_inventory_with_A7']=checks['A7_full_only']
# Independently reproduce published development predictions only.
key=['game','side','dragon','round','turn'];frl=np.array([0,1,3]);runs={};base=None;hits={}
for dirname in ['A3-u','A10-u']:
 p=ROOT/'build/hinata/r2/battery'/dirname;dd=pd.read_parquet(p/'rows.parquet');kk=pd.MultiIndex.from_frame(dd[key]);assert kk.is_unique
 if base is None:base=dd;bk=kk
 assert set(kk)==set(bk);order=pd.Series(np.arange(len(dd)),index=kk).loc[bk].to_numpy();dd=dd.iloc[order].reset_index(drop=True)
 assert np.array_equal(base.y_first,dd.y_first) and np.array_equal(base.fold,dd.fold) and np.array_equal(base.series_key,dd.series_key)
 reg=json.loads((p/'registry.json').read_text());met={};m=base.y_first.isin(frl).to_numpy();s=base.series_key
 for arm in reg['arms']:
  P=np.load(p/f'p_{arm}.npy')[order];assert np.isfinite(P).all() and (P>=0).all() and np.allclose(P.sum(1),1,atol=1e-3);h=frl[P[:,frl].argmax(1)]==base.y_first.to_numpy();hits[arm]=h
  g=pd.DataFrame({'s':s,'h':h&m,'n':m}).groupby('s')[['h','n']].sum();ix=np.random.default_rng(7).integers(0,len(g),(1000,len(g)));bs=g.h.to_numpy()[ix].sum(1)/g.n.to_numpy()[ix].sum(1)
  met[arm]={'accuracy':float(h[m].mean()),'ci90':np.percentile(bs,[5,95]).tolist(),'published':reg['arms'][arm]['frl_all'],'pred_sha':sha(p/f'p_{arm}.npy')}
 runs[dirname]={'rows':len(dd),'frl':int(m.sum()),'games':int(dd.game.nunique()),'series':int(dd.series_key.nunique()),'teachers':int(dd.team.nunique()),'maps':int(dd['map'].nunique()),'registry_sha':sha(p/'registry.json'),'rows_sha':sha(p/'rows.parquet'),'metrics':met}
diff={}
for aa,bb in [('A3-400','A10-e4'),('A3-800','A3-400')]:
 g=pd.DataFrame({'s':s,'d':(hits[aa].astype(float)-hits[bb].astype(float))*m,'n':m}).groupby('s')[['d','n']].sum();ix=np.random.default_rng(7).integers(0,len(g),(1000,len(g)));bs=g.d.to_numpy()[ix].sum(1)/g.n.to_numpy()[ix].sum(1)
 diff[f'{aa} minus {bb}']={'delta':float(g.d.sum()/g.n.sum()),'ci90':np.percentile(bs,[5,95]).tolist()}
# Analytic sizing only; no bot run or throughput benchmark.
p7={'source_G1_cpu_us_per_decision':3.05*62.57/497642*1e6,'decisions_per_game_G1':497642/698,'rollout_hours_at_E2':120e6/1e7,'four_epoch_update_hours_at_8000_samples_s_core_8cores':4*120e6/(8000*8*3600),'h2h_200_independent_decisive_games_P_atleast_110':{str(p):float(binom.sf(109,200,p)) for p in [.5,.55,.6]},'exact_central90_at_110_of_200':[float(beta.ppf(.05,110,91)),float(beta.ppf(.95,111,90))]}
out={'scope':'Synthetic selector probes; published A3/A10 development predictions; analytic P7 arithmetic only. No real selection, fitting, bot runs, or confirmation/LS1 outcome reads.','source_sha':{f:sha(OUT/f) for f in ['r2_bc.py','r2_battery.py','r2_cnn.py']},'checks':checks,'development':runs,'paired':diff,'p7':p7}
assert all(not checks[k]['accepted'] for k in ['nan','inf','bad_sum','pooled_subset','duplicate','labels','folds'])
assert checks['complete']['result']['pooled']['selected']=='A10-e4'
assert all(checks[k]['result']['teacher']['goes_forward'] for k in ['A6_wrong_team','A7_partial','A2_nan','A7_full_only'])
(OUT/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
