import importlib.util,json,copy
from pathlib import Path
import numpy as np,pandas as pd
s=importlib.util.spec_from_file_location('audit','/tmp/tanaka-r4/p2_confirm.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.CELLS=[('post-m2','rl',50)];spec=dict(m.DEFAULT_SPEC,reported_populations=['all'])
r=np.random.default_rng(919);n=200;z=r.normal(size=n);y=(r.random(n)<1/(1+np.exp(-z))).astype(int)
p=pd.DataFrame(dict(game=np.arange(n).astype(str),series_key=(np.arange(n)//4).astype(str),map='synthetic',map_era='post-m2',regime='rl',round=50,ranked=True,clean=True,y=y,p_v=1/(1+np.exp(-z)),p_phi=1/(1+np.exp(-.8*z))))
out={};row=m.evaluate(p,spec)[0];pos=p.loc[p.y==1,'p_v'].to_numpy();neg=p.loc[p.y==0,'p_v'].to_numpy();auc=((pos[:,None]>neg).mean()+.5*(pos[:,None]==neg).mean());out['control']={'status':row['status'],'valid_draws':row['valid_draws'],'auc':row['auc_v'],'independent_pair_auc':float(auc),'error':float(row['auc_v']-auc)}
for name,v in [('nan',np.nan),('inf',np.inf)]:
 bad=p.copy();bad.loc[0,'p_v']=v;out[name]=m.evaluate(bad,spec)[0]['status']
bad=p.copy();bad.y=1;out['oneclass']=m.evaluate(bad,spec)[0]['status']
bad=p.copy();bad.y=(bad.series_key=='0').astype(int);row=m.evaluate(bad,spec)[0];out['one_positive_series_valid_draws']=row['valid_draws']
Path('/tmp/tanaka-r4/evaluate-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
