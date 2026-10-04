"""Audit frozen development predictions; never loads held-out data or fits a model."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
R=args.repo; out=args.out; out.mkdir(parents=True,exist_ok=True); src=R/'build/hinata/v0/fit-lq'
hashfile=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert hashfile(src/'train_rows.parquet') == 'c958e8c7f830c4c5d1b5e322adc44f16152d2a4c4c96714d5d1c30eb091cae76', 'Frozen input changed'
d=pd.read_parquet(src/'train_rows.parquet'); o=pd.read_parquet(src/'oof.parquet'); old=pd.read_csv(src/'lomo.csv')
g=d.drop_duplicates('game').copy(); g['bucket']=g.series_id.astype(str).map(lambda s:int(hashlib.sha256(('D-046/'+s).encode()).hexdigest(),16)%10)
# Weighted rank AUC, with half credit for ties. Sorting is frozen across bootstrap samples.
def auc_setup(y,p):
    order=np.argsort(p,kind='stable'); y=np.asarray(y)[order]; p=np.asarray(p)[order]; starts=np.r_[0,np.flatnonzero(p[1:]!=p[:-1])+1]
    def calc(w):
        w=w[order]; pos=np.add.reduceat(w*y,starts); neg=np.add.reduceat(w*(1-y),starts)
        return float(np.sum(pos*(np.cumsum(neg)-neg/2))/(pos.sum()*neg.sum())) if pos.sum()*neg.sum() else np.nan
    return calc

def slope(y,p):
    z=np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4))); X=np.column_stack([np.ones(len(z)),z])
    def obj(b):
        v=X@b; return np.logaddexp(0,v).sum()-y@v+0.5e-6*b[1]**2, X.T@(expit(v)-y)+np.array([0,1e-6*b[1]])
    f=minimize(obj,np.array([0.,1.]),jac=True,method='BFGS',options={'gtol':1e-7})
    return float(f.x[1])
rows=[]; rng=np.random.default_rng(7); rngs=np.random.default_rng(7)
for key,x in o.groupby(['map_era','regime','round']):
    y=x.y.to_numpy(); a=x.p_v0.to_numpy(); b=x.p_phi.to_numpy(); n=len(x); A=auc_setup(y,a); B=auc_setup(y,b); ones=np.ones(n)
    boot=[]
    for _ in range(1000):
        w=np.bincount(rng.integers(0,n,n),minlength=n); boot.append(A(w)-B(w))
    sx=x.merge(g[['game','series_id','ranked','bucket']],on='game',validate='many_to_one'); ids,inv=np.unique(sx.series_id.astype(str),return_inverse=True); ns=len(ids)
    sb=[]
    for _ in range(1000):
        weights=np.bincount(rngs.integers(0,ns,ns),minlength=ns)[inv]; sb.append(A(weights)-B(weights))
    ref=old[(old.regime==key[1])&(old['round']==key[2])].iloc[0]
    row=dict(map_era=key[0],regime=key[1],round=int(key[2]),n=n,series=ns,maps=int(x['map'].nunique()),auc_v0=A(ones),auc_phi=B(ones),d_auc=A(ones)-B(ones),d_lo=float(np.nanpercentile(boot,5)),d_hi=float(np.nanpercentile(boot,95)),series_lo=float(np.nanpercentile(sb,5)),series_hi=float(np.nanpercentile(sb,95)),slope_v0=slope(y,a),slope_phi=slope(y,b),ranked=int(sx.ranked.sum()))
    row['max_auc_interval_difference']=max(abs(row[k]-ref[k]) for k in ['auc_v0','auc_phi','d_auc','d_lo','d_hi']); row['max_slope_difference']=max(abs(row[k]-ref[k]) for k in ['slope_v0','slope_phi'])
    rows.append(row)
    print(key,n,'d=',round(row['d_auc'],6),'seriesCI=',round(row['series_lo'],6),round(row['series_hi'],6),flush=True)
res={'scope':'Frozen development predictions only; held-out maps not loaded; no fitting or confirmation run.','hashes':{p.name:hashfile(p) for p in [src/'train_rows.parquet',src/'oof.parquet',src/'lomo.csv',src/'registry.json',R/'tools/hinata/v0.py']},'games':len(g),'rows':len(d),'game_modes':{str(k):int(v) for k,v in g.groupby('ranked').size().items()},'bucket_games':{str(k):int(v) for k,v in g.groupby('bucket').size().items()},'bucket_series':{str(k):int(v) for k,v in g.groupby('bucket').series_id.nunique().items()},'heldout_overlap':sorted(set(d['map'])&{'Autarky','Maze','Trauma'}),'rows_duplicate_keys':int(d.duplicated(['game','side','round']).sum()),'table':rows,'baseline_export_files':sorted(p.name for p in src.glob('*phi*'))}
# Count LOMO train-test series overlaps without fitting or reading held-out rows.
folds=[]
for (reg,cp),x in d.groupby(['regime','round']):
    for m in sorted(x['map'].unique()):
        te=x[(x['map']==m)&(x.side=='A')]; tr=x[x['map']!=m]
        if len(te)<20 or tr.game.nunique()<100: continue
        overlap=set(te.series_id)&set(tr.series_id)
        folds.append({'regime':reg,'round':int(cp),'map':m,'test_games':len(te),'test_games_with_series_in_training':int(te.series_id.isin(overlap).sum())})
res['lomo_series_overlap']=folds
(out/'p2-audit.json').write_text(json.dumps(res,indent=2));pd.DataFrame(rows).to_csv(out/'p2-table.csv',index=False)
print('SUMMARY',json.dumps({k:v for k,v in res.items() if k not in ['table','lomo_series_overlap']}))
