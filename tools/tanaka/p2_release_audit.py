import copy,hashlib,importlib.util,json,os,tempfile,contextlib,io
from pathlib import Path
from types import SimpleNamespace
import numpy as np,pandas as pd
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');O=Path('/tmp/tanaka-r4');O.mkdir(exist_ok=True)
source=R/'tools/hinata/p2_confirm.py';snap=O/'p2_confirm.py';snap.write_bytes(source.read_bytes())
s=importlib.util.spec_from_file_location('p2audit',snap);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
spec=m.load_spec();checks={};rows=[dict(population='ranked_clean',regime=reg,round=cp,status='OK',n=100,auc_v=.70,auc_phi=.68,d_auc=.02,d_auc_ci=[.01,.03],slope_v=1.,slope_phi=1.,valid_draws=1000) for _,reg,cp in m.CELLS]
checks['valid_control']=m.gate(rows,spec,['elim/r10'])
for value in [float('nan'),float('inf'),None]:
 for f in ['auc_v','auc_phi','d_auc','slope_v','slope_phi','d_auc_ci']:
  bad=copy.deepcopy(rows);r=next(r for r in bad if r['regime']=='rl' and r['round']==50);r[f]=[value,value] if f=='d_auc_ci' else value
  checks[f'{f}/{str(value)}']=m.gate(bad,spec,['elim/r10'])['verdict']
for n in [989,990]:
 bad=copy.deepcopy(rows);bad[-1]['valid_draws']=n;checks[f'valid_draws_{n}']=m.gate(bad,spec,['elim/r10'])['verdict']
bad=copy.deepcopy(rows);r=next(r for r in bad if r['regime']=='rl' and r['round']==50);r['auc_v']=.64;r['auc_phi']=.62
checks['absolute_floor_report_only']=m.gate(bad,spec,['elim/r10'])['verdict']
for p in [R/'docs/learning/proposals/P-hinata-02-gate-spec.PROPOSED.json',m.SPEC_PATH]:
 try:m.load_spec(p);v='accepted'
 except SystemExit:v='refused'
 checks[p.name]=v
# Isolated receipt mutation probes: evaluator stub, real receipt/hash checks. Never real P2 directory.
original_eval=m.evaluate;m.evaluate=lambda pred,sp:copy.deepcopy(rows)
for case in ['valid','claim','scorer','spec','prediction','coverage']:
 with tempfile.TemporaryDirectory(prefix='tanaka-score-') as td:
  m.P2=Path(td);cov={x:{'coverage':1.0} for x in ['Autarky','Maze','Trauma']}
  if case=='coverage':cov['Maze']['coverage']=.94
  c=m._claim(m.SPEC_SHA,'0'*64 if case=='scorer' else m.sha(m.SELF),['elim/r10'],cov)
  pf=m._seal(pd.DataFrame({'game':['synthetic']}))
  if case in ['claim','spec']:
   j=json.loads(c.read_text());j['report_only_cells']=[] if case=='claim' else j['report_only_cells'];j['spec_sha']='wrong' if case=='spec' else j['spec_sha'];c.write_text(json.dumps(j))
  if case=='prediction':os.chmod(pf,0o644);pf.write_bytes(pf.read_bytes()+b'x')
  with contextlib.redirect_stdout(io.StringIO()):g=m.cmd_score(SimpleNamespace())
  checks['score_'+case]=g
  try:m.cmd_score(SimpleNamespace());v='accepted'
  except SystemExit:v='refused'
  checks['second_score_'+case]=v
m.evaluate=original_eval
# Isolated run with only invented rows. All IO-bearing data loaders overridden. Tests frozen exclusion.
with tempfile.TemporaryDirectory(prefix='tanaka-run-') as td:
 m.P2=Path(td)
 pop=pd.DataFrame([dict(game=f'{mp}{i}',map=mp,series_key=f'{mp}{i}',ranked=True,clean=True,decoded=True,store_in_scope=(mp!='Autarky' or i!=0)) for mp in ['Autarky','Maze','Trauma'] for i in range(100)])
 meta={'sha256':'synthetic'};m.load_pop=lambda _: (pop,meta)
 (m.P2/'cell-counts.json').write_text(json.dumps(dict(spec_sha=m.SPEC_SHA,population_sha='synthetic',scorer_sha=m.sha(m.SELF),report_only_cells=['elim/r10'])))
 # Loader models a changing store: previously excluded Autarky0 becomes in-scope.
 d=pd.DataFrame([dict(game=mp+str(i),map=mp,map_era='post-m2',regime='elim' if mp=='Autarky' else 'rl',side='A',round=50,ranked=True,y=i%2) for mp in ['Autarky','Maze','Trauma'] for i in [0,1]])
 m.v0mod=lambda:SimpleNamespace(load=lambda *a,**kw:d.copy())
 m.weights=lambda:({c:({'a':1.},{'b':1.}) for c in m.CELLS},{})
 m.predict=lambda _m,x,wv,wp:(np.full(len(x),.6),np.full(len(x),.5))
 with contextlib.redirect_stdout(io.StringIO()):m.cmd_run(SimpleNamespace(audited_scorer_sha=m.sha(m.SELF),population='synthetic'))
 pred=pd.read_parquet(m.P2/'predictions.parquet');claim=json.loads((m.P2/'CLAIM.json').read_text())
 checks['frozen_exclusion']={'listed_missing':claim['missing_games'],'predicted_games':pred.game.tolist(),'excluded_game_predicted':bool((pred.game=='Autarky0').any()),'preclaim_coverage':claim['coverage']}
 # Scorer also does not reconcile actual game coverage against receipt; this remains code evidence, not metric test.
cc=R/'build/hinata/p2/cell-counts.json';popf=R/'build/hinata/p2/population.parquet'
out={'source_sha256':m.sha(snap),'spec_sha256':m.sha(m.SPEC_PATH),'checks':checks,'counts_sha256':m.sha(cc),'population_sha256':m.sha(popf),'scope':'synthetic only, no real run/claim or held-out labels/states/predictions read'}
(O/'p2-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
