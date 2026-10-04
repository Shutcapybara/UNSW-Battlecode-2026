from pathlib import Path
import gzip,json,hashlib,importlib.util,sys
import numpy as np
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');p=R/'docs/learning/live-inputs/20261004T1353Z-6578d155.json.gz';j=json.loads(gzip.decompress(p.read_bytes()));g=[dict(zip(j['columns'],r)) for r in j['games']];g=[r for r in g if r['ranked'] and str(r['bot'])=='14585' and r['exp'] is not None];ss=[r['series'] for r in sorted(g,key=lambda r:(r['start'],r['game_id']))];runs=[s for i,s in enumerate(ss) if i==0 or s!=ss[i-1]]
src=R/'tools/daichi/rollback_d052.py';sys.path.insert(0,str(src.parent));s=importlib.util.spec_from_file_location('rb',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=[];rng=np.random.default_rng(103)
for i in range(8):
 new=[rng.normal(-.1,.2,rng.integers(2,7)).tolist() for _ in range(9)];ref=[rng.normal(0,.2,rng.integers(2,7)).tolist() for _ in range(26)]
 got=m.decide(new,ref,np.random.default_rng(7));r=np.random.default_rng(7);ni=r.integers(0,len(new),(1000,len(new)));ri=r.integers(0,len(ref),(1000,len(ref)))
 vals=[]
 for a,b in zip(ni,ri):
  n=[v for ix in a for v in new[ix]];p_=[v for ix in b for v in ref[ix]];vals.append(np.mean(n)-np.mean(p_))
 diff=np.mean([v for a in new for v in a])-np.mean([v for a in ref for v in a]);hi=float(np.percentile(vals,95,method='linear'));checks.append({'diff_error':float(abs(diff-got[0])),'hi_error':abs(hi-got[1]),'decision_agrees':bool(got[2]==(diff<-.08 and hi<0))})
out={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'frozen_input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frozen_ranked_games':len(g),'unique_series':len(set(ss)),'series_runs':len(runs),'synthetic_independent_flattened_bootstrap':checks,'scope':'No operational rule change or new full simulation. Frozen monitor input differs from simulation corpus snapshot; published operating rates not replicated.'}
Path('/tmp/tanaka-r4/rollback-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
