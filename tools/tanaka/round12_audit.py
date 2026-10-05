from pathlib import Path,PurePosixPath
import json,hashlib,sys,shutil,tempfile,contextlib,io,zipfile,argparse
from types import SimpleNamespace
import numpy as np,pandas as pd
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');O=Path('/tmp/tanaka-r12');O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,default=Path(__file__).resolve().parents[2]/'docs/learning/reviews/tanaka-round12');args=ap.parse_args()
for f in ['r2_bc.py','r2_battery.py']:shutil.copyfile(args.sources/f,O/f)
sys.path.insert(0,str(O));import r2_battery as B
D=pd.DataFrame([dict(game=str(i),side='A',dragon=0,round=1,turn=1,map='Dev',team=str(i%4+1),series_key=str(i//10),x_is_queen=1,y_first=0,fold='f'+str(i%5)) for i in range(100)])
base=np.tile([.01,.97,.01,.01],(100,1));perfect=np.tile([.97,.01,.01,.01],(100,1));p80=perfect.copy();p80[80:]=base[80:]
def write(root,name,P,d=D):
 p=root/name;p.mkdir();info={'arm':name.split('-')[0],'model_bytes':{name:1 if name.startswith('A10') else 100},'teams_by_rating':['1','2','3','4']}
 with contextlib.redirect_stdout(io.StringIO()):B.write(SimpleNamespace(weighted=False),p,d,None,d.fold.to_numpy(),{name:P},info,[],{},[])
 (p/'manifest.json').write_text(json.dumps({'teams_top3':['1','2','3']}));return p
checks={}
with tempfile.TemporaryDirectory(prefix='tanaka-r12-') as td:
 td=Path(td)
 for case in ['complete','missing_A10b','curve25','curve50','unknown75','unknownsize','A7only','A2six','A2ten','A2twelve','counts_missing']:
  root=td/case;root.mkdir();a0=write(root,'A0',base)
  counts=root/'counts.json';counts.write_text(json.dumps({'1':12,'2':12,'3':12,'4':6 if case=='A2six' else 10 if case=='A2ten' else 12}))
  if case=='A7only':write(root,'A7fix-400',perfect)
  elif case.startswith('A2') or case=='counts_missing':
   p=p80.copy();p[D.team.eq('4')]=perfect[D.team.eq('4')]
   for name in B.TS_PLANNED:
    m=D.team.isin(['1','2','3']).to_numpy() if name.startswith('A6') else np.ones(100,bool)
    write(root,name,(p80 if name.startswith('A6') else p)[m],D[m])
  else:
   for name in B.POOLED_NAMES:
    if name=='A10b' and case in ['missing_A10b','curve25','curve50']:continue
    write(root,name,perfect if name=='A10b' else p80)
   extra={'curve25':'A10b-f25','curve50':'A10b-f50','unknown75':'A10b-f75','unknownsize':'A3-200'}.get(case)
   if extra:write(root,extra,perfect)
  try:
   with contextlib.redirect_stdout(io.StringIO()):B.table(SimpleNamespace(a0=str(a0),runs=str(root),out=str(root/'out.json'),waive_ts=None,cohort_series=None if case=='counts_missing' else str(counts)))
   t=json.loads((root/'out.json').read_text());checks[case]={'accepted':True,'pooled':t['selection'],'ts':t['teacher_specific']['selection'],'roles':{r['arm']:r['role'] for r in t['rows']}}
  except SystemExit as e:checks[case]={'accepted':False,'reason':str(e)}
assert checks['complete']['pooled']['selected']=='A10b' and checks['complete']['pooled']['passes']
for c in ['missing_A10b','curve25','curve50']:assert not checks[c]['pooled']['passes'] and 'A10b' in checks[c]['pooled']['pooled_missing']
assert checks['curve25']['roles']['A10b-f25']=='descriptive' and checks['curve50']['roles']['A10b-f50']=='descriptive'
assert not checks['unknown75']['accepted'] and not checks['unknownsize']['accepted']
assert checks['A7only']['ts'] is None
assert 'team 4' not in checks['A2six']['ts']['best']['cand']
for c in ['A2ten','A2twelve']:assert 'team 4' in checks[c]['ts']['best']['cand'] and checks[c]['ts']['goes_forward']
assert not checks['counts_missing']['ts']['goes_forward']
# Metadata projection only: no confirmation action/outcome/encoder values.
cf=R/'build/learn/kageyama/r2_confirm_cohort_v1.parquet';C=pd.read_parquet(cf,columns=['game','series_key','teacher_sides','team_a','team_b']);sets={};games={};top=set();topg=set()
for r in C.itertuples():
 for side in r.teacher_sides.split(','):
  team=str(getattr(r,'team_a' if side=='A' else 'team_b'));sets.setdefault(team,set()).add(r.series_key);games.setdefault(team,set()).add(r.game)
  if team in ['91','306','264']:top.add(r.series_key);topg.add(r.game)
counts={t:len(v) for t,v in sorted(sets.items())};eligible=sorted(t for t,n in counts.items() if n>=10)
assert counts=={'19':6,'213':14,'264':11,'306':8,'507':9,'55':10,'566':7,'842':6,'91':6,'952':16}
(O/'cohort-series.json').write_text(json.dumps(counts,indent=2))
# Independently reproduce published runtime source fingerprint directly from zip members.
zp=R/'build/daichi/ls1/16979-asahi-05-kz12-k16.zip';suffixes={'.cpp','.hpp','.h','.c','.cc','.cxx','.rs','.py','.toml'}
# Read exact suffix constant without executing the runner.
import ast
module=ast.parse((R/'tools/analysis/features/run_panel.py').read_text())
for node in module.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FP_SUFFIXES' for t in node.targets):suffixes=ast.literal_eval(node.value)
with zipfile.ZipFile(zp) as z:
 names=sorted(n for n in z.namelist() if not n.endswith('/') and (PurePosixPath(n).suffix in suffixes or PurePosixPath(n).name=='bot.toml') and '.unswbc-build' not in PurePosixPath(n).parts)
 h=hashlib.sha256();members={}
 for n in names:
  data=z.read(n);h.update(n.encode()+b'\0'+data+b'\0');members[n]=hashlib.sha256(data).hexdigest();assert data==(R/'bots/asahi-05-kz12-k16'/n).read_bytes()
 fp=h.hexdigest()
assert fp=='43bd2d4fc7a8baac6d8f14d22a6a0a8eb9c33cc2ca85ee12cce5b770a3eff1ad'
runmetas={}
for panel in ['pool','gen']:
 p=Path('/Users/alik/Documents/Projects/wt-asahi/build/asahi/runs/asahi-05-kz12-k16/43bd2d4f')/panel/'run.json';m=json.loads(p.read_text());runmetas[panel]=m;assert m['fingerprint']==fp
out={'source_sha':{f:sha(O/f) for f in ['r2_bc.py','r2_battery.py']},'checks':checks,'cohort_metadata':{'sha':sha(cf),'columns':['game','series_key','teacher_sides','team_a','team_b'],'counts':counts,'A2_eligible_teams':eligible,'A6_games':len(topg),'A6_series':len(top)},'archive':{'sha256':sha(zp),'bytes':zp.stat().st_size,'runtime_fingerprint':fp,'members':members,'gate_run_metadata':runmetas}}
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'checks':{c:{'accepted':v['accepted'],'pooled':v.get('pooled'),'ts':v.get('ts')} for c,v in checks.items()},'cohort':out['cohort_metadata'],'archive':{k:v for k,v in out['archive'].items() if k not in ['members','gate_run_metadata']}},indent=2))
