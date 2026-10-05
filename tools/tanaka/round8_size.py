import json
from pathlib import Path
import numpy as np
from scipy.stats import binom
from scipy.optimize import minimize
from scipy.special import expit
import pandas as pd
O=Path('/tmp/tanaka-r8');O.mkdir(exist_ok=True);R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');out=json.loads((O/'audit.json').read_text());ls=out['ls_std']
# Enumerate (+,-,zero) counts exactly at two fixed cluster looks, expected nonzero count12 at final85.
def dp_power(q,reject=False):
 d=np.zeros((86,86));d[0,0]=1.;prob=12/85
 for _ in range(51):
  e=d*(1-prob);e[1:,1:]+=d[:-1,:-1]*prob*q;e[1:,:]+=d[:-1,:]*prob*(1-q);d=e
 n,k=np.indices(d.shape);qual=(n>=4)&(binom.sf(k-1,n,.5)<=.075)&(k>n/2);early=float(d[qual].sum());d[qual]=0
 if reject:d[k<=n/2]=0
 for _ in range(34):
  e=d*(1-prob);e[1:,1:]+=d[:-1,:-1]*prob*q;e[1:,:]+=d[:-1,:]*prob*(1-q);d=e
 return early+float(d[qual].sum())
ls['random_nonzero_final_mean12']={'design':'51 then85 clusters; independent fixed per-cluster nonzero probability12/85; equipotent +/- magnitudes; bootstrap/fault guards omitted, hence sign-rule ceiling','any_look':{str(q):dp_power(q) for q in [.5,.6,.7,.75,.8]},'reject_at_first':{str(q):dp_power(q,True) for q in [.5,.6,.7,.75,.8]},'prob_final_below12':float(binom.cdf(11,85,12/85))}
# Independent likelihood optimisation of point recalibration, no new model fit or gate rerun.
pred=pd.read_parquet(R/'build/hinata/p2/predictions.parquet');res=json.loads((R/'build/hinata/p2/result.json').read_text());sl=[]
for row in res['rows']:
 if row['population']!='ranked_clean':continue
 x=pred[pred.ranked&pred.clean&(pred.regime==row['regime'])&(pred['round']==row['round'])];y=x.y.to_numpy()
 a={'regime':row['regime'],'round':row['round']}
 for key,col in [('v','p_v'),('phi','p_phi')]:
  p=np.clip(x[col].to_numpy(),1e-4,1-1e-4);z=np.log(p/(1-p));X=np.c_[np.ones(len(x)),z]
  f=lambda ab:np.logaddexp(0,X@ab).sum()-y@(X@ab)
  jac=lambda ab:X.T@(expit(X@ab)-y)
  opt=minimize(f,[0.,1.],jac=jac,method='BFGS',options={'gtol':1e-7,'maxiter':500});a[key]={'slope':float(opt.x[1]),'difference':float(opt.x[1]-row['slope_'+key]),'gradient_max':float(abs(jac(opt.x)).max())}
 sl.append(a)
out['p2']['independent_point_slopes']=sl
out['p2']['max_point_slope_difference']=max(abs(a[k]['difference']) for a in sl for k in ['v','phi'])
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'random_K':ls['random_nonzero_final_mean12'],'mean_zero_size':ls['mean_zero_asymmetric']['one_look_pass_probability'],'max_slope_difference':out['p2']['max_point_slope_difference']},indent=2))
