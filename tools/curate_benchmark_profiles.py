"""Offline lineage/map residual correlations; no live campaign changes."""
from pathlib import Path
import sys,json,argparse
import numpy as np
root=Path.cwd();sys.path.insert(0,str(root/'tools'))
from curate_benchmarks import family
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);out=parser.parse_args().output.resolve();r=json.loads((out/'analysis.json').read_text());bs=r['bots'];z=np.load(out/'profiles.npz');res=z['residual'];actual=z['actual'];families=r['families'];f=len(families);n=len(bs);m=len(r['maps']);fi=np.array([families.index(b['family']) for b in bs]);profile=np.full((n,f,m),np.nan);count=np.zeros((n,f,m),int)
for j in range(f):
 part=res[:,fi==j,:];count[:,j,:]=np.isfinite(part).sum(axis=1)
 np.divide(np.nansum(part,axis=1),count[:,j,:],out=profile[:,j,:],where=count[:,j,:]>0)
pairs=[];rng=np.random.default_rng(783)
for i in range(n):
 for j in range(i+1,n):
  if not(bs[i]['broad'] or bs[j]['broad']):continue
  mask=np.isfinite(profile[i])&np.isfinite(profile[j]);fa,mp=np.where(mask)
  if len(fa)<50 or len(set(fa))<6 or len(set(mp))<10:continue
  l=profile[i][mask];rr=profile[j][mask];weight=np.sqrt(np.minimum(count[i][mask],3)*np.minimum(count[j][mask],3)).astype(float)
  for fam in set(fa):weight[fa==fam]/=weight[fa==fam].sum()
  weight/=weight.sum()
  def corr(w):
   w=w/w.sum(axis=-1,keepdims=True);ml=w@l;mr=w@rr
   cov=(w@(l*rr))-ml*mr;var=(w@(l*l)-ml*ml)*(w@(rr*rr)-mr*mr)
   return cov/np.sqrt(np.maximum(var,1e-20))
  c=float(corr(weight));u=rng.exponential(size=(200,f));boot=corr(u[:,fa]*weight);lo,hi=np.quantile(boot,[.05,.95])
  pairs.append(dict(a=i,b=j,correlation=c,low=float(lo),high=float(hi),cells=len(fa),families=len(set(fa)),maps=len(set(mp))))
r['family_correlations']=pairs
(out/'analysis.json').write_text(json.dumps(r,separators=(',',':'),allow_nan=False)+'\n')
np.savez_compressed(out/'family-profiles.npz',profile=profile,count=count)
for pair in sorted([p for p in pairs if bs[p['a']]['broad'] and bs[p['b']]['broad']],key=lambda p:-p['correlation'])[:25]:
 print(bs[pair['a']]['name'],bs[pair['b']]['name'],round(pair['correlation'],3),round(pair['low'],3),pair['cells'])

# High-overlap exact-opponent comparisons take precedence over coarser lineage bins.
for pair in r['similarities']:
 if pair['cells']<80 or pair['families']<6 or pair['maps']<10 or pair['correlation'] is None or pair['correlation']<.80:continue
 i,j=pair['a'],pair['b'];mask=np.isfinite(res[i])&np.isfinite(res[j]);opp,mp=np.where(mask);fa=fi[opp]
 l=res[i][mask];rr=res[j][mask];frequency=np.bincount(fa,minlength=f)
 weight=1/frequency[fa];weight/=weight.sum()
 def exact_corr(w):
  w=w/w.sum(axis=-1,keepdims=True);ml=w@l;mr=w@rr
  variance=(w@(l*l)-ml*ml)*(w@(rr*rr)-mr*mr)
  return (w@(l*rr)-ml*mr)/np.sqrt(np.maximum(variance,1e-20))
 low,high=np.quantile(exact_corr(rng.exponential(size=(200,f))[:,fa]*weight),[.05,.95])
 pair['correlation_low']=float(low);pair['correlation_high']=float(high)
(out/'analysis.json').write_text(json.dumps(r,separators=(',',':'),allow_nan=False)+'\n')
