"""Offline, source-frozen opponent curation. Does not touch the running campaign."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse
from collections import defaultdict,Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from benchmark import observed
from benchmark_data import aliases
from game_stats import ROOT,read_parquet,write_parquet


def family(name):
    return 'von_neumann' if name.startswith(('vn-','von_neumann-')) else name.split('-')[0].split('_v')[0]


def fit(data,n,m,weights,with_maps=False,start=None):
    a,b,k,y=data
    size=n+m+(n*m if with_maps else 0)
    def fg(x):
        s=x[:n];side=x[n:n+m]
        z=s[a]-s[b]+side[k]
        if with_maps:
            t=x[n+m:].reshape(n,m);z=z+t[a,k]-t[b,k]
        loss=np.sum(weights*(np.logaddexp(0,z)-y*z))+.25*np.dot(s,s)+.5*np.dot(side,side)
        e=weights*(expit(z)-y)
        g=[np.bincount(a,e,minlength=n)-np.bincount(b,e,minlength=n)+.5*s,
           np.bincount(k,e,minlength=m)+side]
        if with_maps:
            loss+=2.5*np.sum(t*t)
            g.append(np.bincount(a*m+k,e,minlength=n*m)-np.bincount(b*m+k,e,minlength=n*m)+5*t.ravel())
        return loss/len(y),np.concatenate(g)/len(y)
    result=minimize(fg,np.zeros(size) if start is None else start,jac=True,method='L-BFGS-B',
                    options=dict(maxiter=600,ftol=1e-11,gtol=1e-7))
    if not result.success:raise RuntimeError(result.message)
    return result.x


def predict(x,data,n,m):
    a,b,k,_=data
    z=x[a]-x[b]+x[n:n+m][k]
    if len(x)>n+m:
        t=x[n+m:].reshape(n,m);z+=t[a,k]-t[b,k]
    return expit(z)


def main(out):
    out.mkdir(parents=True,exist_ok=True)
    if not (out/'manifest.json').exists():
        campaign=Path(json.loads((ROOT/'experiment_data/benchmark-current.json').read_text())['directory'])
        shutil.copy2(campaign/'manifest.json',out/'manifest.json')
        (out/'aliases.json').write_text(json.dumps(aliases()|json.loads((campaign/'aliases.json').read_text())))
        write_parquet(out/'games.parquet',read_parquet(ROOT/'game_stats.parquet'))
    manifest=json.loads((out/'manifest.json').read_text())
    rows=read_parquet(out/'games.parquet')
    raw=observed(manifest,rows,json.loads((out/'aliases.json').read_text()))
    count=Counter(n for a,b,k in raw for n in (a,b))
    # Identical effective packaged sources become one competitor, even across names.
    groups=defaultdict(list)
    for name,h in manifest['effective_hashes'].items():groups[h].append(name)
    members=sorted((sorted(ns,key=lambda x:(-count[x],x)) for ns in groups.values()),key=lambda ns:ns[0])
    names=[ns[0] for ns in members];index={v:i for i,ns in enumerate(members) for v in ns}
    maps=manifest['maps'];mi={v:i for i,v in enumerate(maps)};n=len(names);m=len(maps)
    cells=defaultdict(list)
    for (a,b,k),rr in raw.items():
        if index[a]==index[b]:continue
        cells[index[a],index[b],mi[k]].append(np.mean([1 if r['outcome']=='A' else .5 if r['outcome']=='draw' else 0 for r in rr]))
    keys=sorted(cells);a,b,k=np.asarray(keys,dtype=int).T;y=np.array([np.mean(cells[f]) for f in keys])
    data=(a,b,k,y);families=sorted({family(v) for v in names});fi=np.array([families.index(family(v)) for v in names])
    f=len(families);blocks=(np.minimum(fi[a],fi[b])*f+np.maximum(fi[a],fi[b]))*m+k
    # Balance lineage-pair/map blocks, reducing redundant lineages' influence.
    sizes=Counter(blocks);w=np.array([1/sizes[z] for z in blocks]);w*=len(w)/w.sum()
    mapped=fit(data,n,m,w,True)
    strength=mapped[:n]+mapped[n+m:].reshape(n,m).mean(axis=1)
    # Cross-fit residuals by whole opponent pair (all maps and both sides held together).
    pairs=np.minimum(a,b)*n+np.maximum(a,b);unique=np.unique(pairs);rng=np.random.default_rng(20260927)
    folds={v:i%5 for i,v in enumerate(rng.permutation(unique))};fold=np.array([folds[v] for v in pairs]);oof=np.empty(len(y))
    for split in range(5):
        train=fold!=split;test=~train
        train_blocks=Counter(blocks[train]);ww=np.array([1/train_blocks[z] for z in blocks[train]]);ww*=len(ww)/ww.sum()
        x=fit(tuple(v[train] for v in data),n,m,ww,True)
        # Remove overall strength and initiative, retaining map/style differences.
        overall=x[:n]+x[n+m:].reshape(n,m).mean(axis=1)
        oof[test]=expit(overall[a[test]]-overall[b[test]]+x[n:n+m][k[test]])
    print('Fitted',n,'source-distinct bots',len(keys),'fixtures',flush=True)
    actual=np.full((n,n,m),np.nan);residual=np.full_like(actual,np.nan)
    lookup={v:i for i,v in enumerate(keys)}
    for i,(left,right,mp) in enumerate(keys):
        j=lookup.get((right,left,mp))
        if j is not None:
            actual[left,right,mp]=(y[i]+1-y[j])/2
            residual[left,right,mp]=((y[i]-oof[i])-(y[j]-oof[j]))/2
    support=[]
    for i in range(n):
        mask=(a==i)|(b==i);opponents=set(b[a==i])|set(a[b==i]);dense=(np.isfinite(actual[i]).sum(axis=0)>=3).sum()
        support.append(dict(fixtures=int(mask.sum()),opponents=len(opponents),families=len({fi[z] for z in opponents}),
            maps=len(set(k[mask])),dense_maps=int(dense)))
    broad=np.array([s['fixtures']>=200 and s['opponents']>=15 and s['families']>=6 and s['maps']>=10 and s['dense_maps']>=10 for s in support])
    # Equal-family anchor panel: strongest broadly tested member per lineage.
    anchors=[max([i for i in range(n) if broad[i] and fi[i]==j],key=lambda i:strength[i])
             for j in range(f) if any(broad[i] and fi[i]==j for i in range(n))]
    def profiles(x):
        t=x[n+m:].reshape(n,m);s=x[:n];anchor=np.array(anchors)
        return expit(s[:,None,None]+t[:,None,:]-s[anchor][None,:,None]-t[anchor][None,:,:]).mean(axis=1)
    score=profiles(mapped).mean(axis=1)
    # Bayesian cluster bootstrap: a shared random multiplier for each lineage;
    # all outcomes involving that lineage move together. Sensitivity, not calibrated CI.
    boots=[]
    for repeat in range(40):
        u=rng.exponential(size=f);ww=w*np.sqrt(u[fi[a]]*u[fi[b]]);ww*=len(w)/ww.sum()
        boots.append(profiles(fit(data,n,m,ww,True,start=mapped)).mean(axis=1))
        if repeat%10==9:print('Cluster resamples',repeat+1,flush=True)
    low,high=np.quantile(boots,[.05,.95],axis=0)
    profile=profiles(mapped)
    # Shared paired opponent/map cells compare like with like; weight each lineage equally.
    similarities=[];dominance=[]
    def compare(i,j):
        mask=np.isfinite(actual[i])&np.isfinite(actual[j]);opp,mp=np.where(mask)
        fam=fi[opp];nf=len(set(fam));nm=len(set(mp));nc=len(opp)
        if nc<40 or nf<4 or nm<6:return
        family_counts=Counter(fam)
        weight=np.array([1/family_counts[z] for z in fam]);weight/=weight.sum()
        l=residual[i][mask];r=residual[j][mask];lc=l-np.dot(l,weight);rc=r-np.dot(r,weight)
        scale=np.sqrt(np.dot(weight,lc*lc)*np.dot(weight,rc*rc))
        corr=float(np.dot(weight,lc*rc)/scale) if scale>1e-9 else None
        difference=actual[i][mask]-actual[j][mask]
        delta=float(np.dot(weight,difference))
        family_delta=np.array([difference[fam==z].mean() for z in sorted(set(fam))])
        ww=rng.exponential(size=(500,len(family_delta)));ww/=ww.sum(axis=1,keepdims=True)
        lo,hi=np.quantile(ww@family_delta,[.05,.95])
        bymap={maps[z]:float(difference[mp==z].mean()) for z in set(mp)}
        item=dict(a=i,b=j,cells=nc,families=nf,maps=nm,correlation=corr,delta=delta,low=float(lo),high=float(hi),by_map=bymap)
        similarities.append(item)
        if broad[i] and broad[j]:
            for better,worse,sign in [(i,j,1),(j,i,-1)]:
                lower=lo if sign==1 else -hi
                # Loose observed dominance: material average gain, no >10pp map sacrifice.
                if lower>.02 and min(sign*v for v in bymap.values())>=-.10 and score[better]>=score[worse]:
                    dominance.append(dict(better=better,worse=worse,cells=nc,families=nf,maps=nm,
                                          advantage=sign*delta,lower=float(lower),worst_map=min(sign*v for v in bymap.values())))
    for i in range(n):
        for j in range(i+1,n):
            if broad[i] or broad[j]:compare(i,j)
    result=dict(at=datetime.now(timezone.utc).isoformat(),ledger_games=len(rows),raw_fixtures=len(raw),fixtures=len(y),
        maps=maps,anchors=anchors,families=families,aliases=members,
        bots=[dict(id=i,name=names[i],family=families[fi[i]],broad=bool(broad[i]),**support[i],
                   score=float(score[i]),low=float(low[i]),high=float(high[i]),map_profile=profile[i].tolist()) for i in range(n)],
        similarities=similarities,dominance=dominance,
        validation=dict(oof_log_loss=float(np.mean(-y*np.log(oof)-(1-y)*np.log1p(-oof)))))
    (out/'analysis.json').write_text(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n')
    np.savez_compressed(out/'profiles.npz',actual=actual,residual=residual,bootstrap=np.array(boots),strength=strength,mapped=mapped)
    print('Broad',int(broad.sum()),'of',n,'dominance edges',len(dominance),flush=True)
    for b in sorted(result['bots'],key=lambda b:-b['score'])[:40]:print(b['name'],round(b['score'],3),b['broad'],b['fixtures'],b['families'],b['dense_maps'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output.resolve())
