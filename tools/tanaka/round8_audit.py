from pathlib import Path
import json,hashlib,math
import numpy as np,pandas as pd
from scipy.stats import rankdata,binom
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');O=Path('/tmp/tanaka-r8');O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Exact fixed-count sign-test operating characteristics. No live observations.
def pval(k,n):return float(binom.sf(k-1,n,.5))
def threshold(n):return next((k for k in range(n+1) if n>=4 and pval(k,n)<=.075),n+1)
def prob(n,q):return float(binom.sf(threshold(n)-1,n,q))
def two(n1,n2,q,stop_reject=False):
 total=0.
 for k in range(n1+1):
  pk=binom.pmf(k,n1,q)
  if k>=threshold(n1):total+=pk
  elif not stop_reject or k>n1/2:total+=pk*binom.sf(threshold(n2)-k-1,n2-n1,q)
 return float(total)
ls={'threshold_12':threshold(12),'fixed12':{str(q):prob(12,q) for q in [.5,.6,.7,.75,.8]},'two_12_20_sign_only':{str(q):two(12,20,q) for q in [.5,.6,.7,.75,.8]},'two_12_20_with_equal_magnitude_reject_at_first':{str(q):two(12,20,q,True) for q in [.5,.6,.7,.75,.8]},'critical':{str(n):threshold(n) for n in [4,5,6,7,9,12,15,20]}}
# Mean-zero, asymmetric cluster-sum counterexample: 12 nonzero of 51 fixed clusters.
# Each nonzero cluster independently +0.5 (p=.8) or -2 (p=.2), E[S]=0. Actual D056 guards at one look.
bi=np.random.default_rng(7).integers(0,51,(1000,51));cases=[]
for k in range(13):
 a=np.array([.5]*k+[-2.]*(12-k)+[0.]*39);ci=np.percentile(a[bi].sum(1)/102,[5,95]);passed=k>=threshold(12) and a.sum()>0 and ci[0]>-.02
 cases.append({'k':k,'p':pval(k,12),'mean':float(a.sum()/102),'ci':ci.tolist(),'pass':bool(passed)})
ls['mean_zero_asymmetric']={'distribution':'+.5 with probability .8; -2 with probability .2; 12 independent nonzero clusters + 39 fixed zero clusters','cases':cases,'one_look_pass_probability':float(sum(binom.pmf(c['k'],12,.8) for c in cases if c['pass'])),'limitation':'sorted hypothetical cluster order; demonstrates that sign symmetry is stronger than zero mean, not a prediction for LS1'}
# P2: read the already published sealed predictions, independently reproduce ranks and shared-series intervals.
b=R/'build/hinata/p2';rec=json.loads((b/'RECEIPT.json').read_text());claim=json.loads((b/'CLAIM.json').read_text());result=json.loads((b/'result.json').read_text());pred=pd.read_parquet(b/'predictions.parquet');pin=pd.read_parquet(b/'membership-pin.parquet')
hashes={name:sha(b/name) for name in ['CLAIM.json','RECEIPT.json','predictions.parquet','result.json','membership-pin.parquet','membership.json']}
st=rec['stages'];integrity={'claim':hashes['CLAIM.json']==st[0]['claim_sha'],'predictions':hashes['predictions.parquet']==st[1]['predictions_sha'],'result':hashes['result.json']==st[2]['result_sha'],'membership':hashes['membership.json']==st[1]['membership_sha'],'pin':hashes['membership-pin.parquet']==claim['pin_sha'],'source':sha(R/'tools/hinata/p2_confirm.py')==claim['scorer_sha'],'one_claim_one_score':[x['stage'] for x in st]==['claimed','sealed','scored']}
assert all(integrity.values())
sk=sorted(pred.series_key.astype(str).unique());index={s:i for i,s in enumerate(sk)};rg=np.random.default_rng(7);C=np.array([np.bincount(rg.integers(0,len(sk),len(sk)),minlength=len(sk)) for _ in range(1000)])
def auc(y,p):
 ranks=rankdata(p,method='average');n1=sum(y);n0=len(y)-n1;return float((ranks[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def bootauc(y,p,w):
 order=np.argsort(p);p=p[order];y=y[order];w=w[:,order];starts=np.r_[0,1+np.flatnonzero(np.diff(p))]
 pos=np.add.reduceat(w*(y==1),starts,axis=1);neg=np.add.reduceat(w*(y==0),starts,axis=1)
 return (pos*(np.cumsum(neg,axis=1)-neg/2)).sum(1)/(pos.sum(1)*neg.sum(1))
table=[]
for row in result['rows']:
 if row['population']!='ranked_clean':continue
 x=pred[pred.ranked & pred.clean & (pred.regime==row['regime']) & (pred['round']==row['round'])];y=x.y.to_numpy();v=x.p_v.to_numpy();phi=x.p_phi.to_numpy();W=C[:,[index[s] for s in x.series_key.astype(str)]]
 a=auc(y,v);ap=auc(y,phi);d=bootauc(y,v,W)-bootauc(y,phi,W);ci=np.percentile(d,[5,95]);table.append({'regime':row['regime'],'round':row['round'],'n':len(x),'series':int(x.series_key.nunique()),'auc_v':a,'auc_phi':ap,'delta':a-ap,'ci':ci.tolist(),'max_difference':float(max(abs(a-row['auc_v']),abs(ap-row['auc_phi']),max(abs(ci-np.array(row['d_auc_ci']))))),'valid_draws':int(np.isfinite(d).sum())})
p2={'hashes':hashes,'integrity':integrity,'keys_match':set(zip(pred.game,pred['round']))==set(zip(pin.game,pin['round'])),'duplicate_keys':int(pred.duplicated(['game','round']).sum()),'rows':len(pred),'games':int(pred.game.nunique()),'binding_table':table,'published_gate':result['gate'],'brier_forecast_040':.4**2,'bootstrap':'all prediction series sorted;1000 seed7 common draws; independent rank formula and tie-group weighted pair counts; linear5/95'}
assert p2['keys_match'] and p2['duplicate_keys']==0 and max(x['max_difference'] for x in table)<1e-12
# R2: frozen out-of-fold predictions only, no fit. Verify full support and compute exact accuracy, clustered interval.
r=R/'build/hinata/r2/dev120-enc-s5';d=pd.read_parquet(r/'oof.parquet');met=json.loads((r/'metrics.json').read_text());man=json.loads((r/'manifest.json').read_text());support=json.loads((r/'support.json').read_text());reg=json.loads((r/'registry.json').read_text())
mask=d.y_first.isin([0,1,3]);frl=np.array([0,1,3]);guess=frl[d[['p_F','p_R','p_L']].to_numpy().argmax(1)];hit=guess==d.y_first.to_numpy();g=pd.DataFrame({'series':d.series_key,'hit':hit & mask,'n':mask}).groupby('series')[['hit','n']].sum();z=np.random.default_rng(7).integers(0,len(g),(1000,len(g)));v=g.hit.to_numpy()[z].sum(1)/g.n.to_numpy()[z].sum(1)
fold=d.series_key.map(lambda s:'f'+str(int(hashlib.sha256(f'hinata-r2/{s}'.encode()).hexdigest(),16)%5));r2={'hashes':{name:sha(r/name) for name in ['oof.parquet','manifest.json','support.json','metrics.json','registry.json']},'source_recorded':man['code_sha'],'manifest_matches_registry':sha(r/'manifest.json')==reg['manifest_sha'],'rows':len(d),'frl_rows':int(mask.sum()),'games':int(d.game.nunique()),'series':int(d.series_key.nunique()),'frl_accuracy':float(hit[mask].mean()),'queen_accuracy':float(hit[mask&(d.x_is_queen==1)].mean()),'ci':np.percentile(v,[5,95]).tolist(),'folds':{k:{'rows':int((fold==k).sum()),'frl':int((mask & (fold==k)).sum()),'accuracy':float(hit[mask & (fold==k)].mean())} for k in sorted(fold.unique())},'five_models_present':all((r/f'model_f{k}.txt').exists() for k in range(5))}
assert r2['rows']==support['rows']==met['scored'] and r2['frl_rows']==support['frl_rows'] and r2['manifest_matches_registry'] and r2['five_models_present']
assert round(r2['frl_accuracy'],4)==met['frl_all']['acc'] and np.allclose(np.round(r2['ci'],4),[met['frl_boot']['p05'],met['frl_boot']['p95']])
# Data code/future cohort metadata will be audited separately when accessible. No live LS1 index or outcomes opened.
out={'scope':'Published P2 confirmation and R2 development frozen outputs; independent diagnostic replication, no rerun of run/score/fit, no live LS1 outcomes. Exact LS sizing probabilities on invented distributions.','ls_std':ls,'p2':p2,'r2':r2}
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'ls':ls,'p2':p2,'r2':r2},indent=2))
