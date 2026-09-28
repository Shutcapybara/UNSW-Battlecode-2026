"""Produce a frozen strength/profile/progress snapshot for an interactive view."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sqlite3
import numpy as np
from scipy.special import expit
from filelock import FileLock,Timeout
from benchmark import observed
from benchmark_data import aliases,with_rating_context
from game_stats import ROOT,read_parquet,write_parquet
from performance_model import fit,unpack,predictions,metrics,subset
from benchmark_weights import normalized_weights


def main(out):
    out.mkdir(parents=True,exist_ok=True)
    campaign=Path(json.loads((ROOT/'experiment_data/benchmark-current.json').read_text())['directory'])
    manifest=json.loads((campaign/'manifest.json').read_text())
    active_names=set(manifest['bots'])
    manifest=with_rating_context(manifest)
    data_at=datetime.now(timezone.utc).isoformat()
    rows=read_parquet(ROOT/'game_stats.parquet');write_parquet(out/'games.parquet',rows)
    games=observed(manifest,rows,aliases()|json.loads((campaign/'aliases.json').read_text()))
    names,maps=manifest['bots'],manifest['maps'];n,m=len(names),len(maps)
    distribution=normalized_weights(manifest)
    map_weights=np.array([distribution[name] for name in maps])
    ni={name:i for i,name in enumerate(names)};mi={name:i for i,name in enumerate(maps)}
    fs=sorted(games)
    data=tuple(np.asarray(v) for v in zip(*[(ni[a],ni[b],mi[board],np.mean([
        1 if r['outcome']=='A' else .5 if r['outcome']=='draw' else 0 for r in games[a,b,board]])) for a,b,board in fs]))
    data=tuple(x.astype(int) if k<3 else x for k,x in enumerate(data));a,b,board,y=data
    groups=np.minimum(a,b)*n+np.maximum(a,b);unique=np.unique(groups)
    rng=np.random.default_rng(260926);shuffled=rng.permutation(unique)
    hold=np.isin(groups,shuffled[:len(unique)//5]);train=~hold
    base=fit(subset(data,train),n,m)
    cycle=fit(subset(data,train),n,m,q=2,start=base)
    if not base['success'] or not cycle['success']:
        raise RuntimeError('Validation fit did not converge; retain the previous ranking')
    validation={name:metrics(y[hold],predictions(model,subset(data,hold),n,m))
                for name,model in [('map',base),('cycle',cycle)]}
    chosen=cycle if validation['cycle']['log_loss']<validation['map']['log_loss'] else base
    model=fit(data,n,m,q=chosen['q'],start=chosen)
    if not model['success']:
        raise RuntimeError('Ranking fit did not converge; retain the previous ranking')
    print('Fit',model['q'],model['success'],validation,flush=True)
    panel=np.array([ni[name] for name in manifest['references']])
    def profiles(fitted):
        s,t,initiative,u,v=unpack(fitted['x'],n,m,fitted['q'])
        c=u@v.T-v@u.T
        z=s[:,None,None]-s[panel][None,:,None]+t[:,None,:]-t[panel][None,:,:]+c[:,panel,None]
        p=(expit(z+initiative[None,None,:])+expit(z-initiative[None,None,:]))/2
        per_map=p.mean(axis=1)
        return per_map@map_weights,per_map
    scores,map_scores=profiles(model)
    index={g:np.flatnonzero(groups==g) for g in unique};boot=[];boot_maps=[];success=[]
    for k in range(24):
        sample=np.concatenate([index[g] for g in rng.choice(unique,len(unique),replace=True)])
        fitted=fit(subset(data,sample),n,m,q=model['q'],start=model)
        success.append(fitted['success'])
        if fitted['success']:
            s,ms=profiles(fitted);boot.append(s);boot_maps.append(ms)
        print('Resample',k+1,flush=True)
    if len(boot)<20:
        raise RuntimeError('Too few converged resamples; retain the previous ranking')
    lo,hi=np.quantile(boot,[.1,.9],axis=0)
    # Ranges enclose the point estimate as well as the resample spread.
    lo=np.minimum(lo,scores);hi=np.maximum(hi,scores)
    delta=map_scores-scores[:,None]
    boot_delta=np.asarray(boot_maps)-np.asarray(boot)[:,:,None]
    dlo,dhi=np.quantile(boot_delta,[.1,.9],axis=0)
    empirical=np.full((n,n,m),np.nan);lookup={f:float(v) for f,v in zip(fs,y)}
    for left,right,mp in fs:
        if (right,left,mp) in lookup:
            empirical[ni[left],ni[right],mi[mp]]=(lookup[left,right,mp]+1-lookup[right,left,mp])/2
    support=[]
    for i in range(n):
        mask=(a==i)|(b==i)
        seen_maps=set(board[mask])
        support.append(dict(games=int(mask.sum()),opponents=len(set(b[a==i])|set(a[b==i])),
            maps=len(seen_maps),map_weight_coverage=float(sum(map_weights[k] for k in seen_maps))))
    profile_supported=np.array([r['games']>=60 and r['opponents']>=5 and r['maps']>=8 for r in support])
    established=profile_supported & np.array([r['map_weight_coverage']>=.8 for r in support])
    bots=[]
    for i,name in enumerate(names):
        if name not in active_names:continue
        neighbors=[]
        for j in range(n):
            if i==j or not profile_supported[j] or names[j] not in active_names:continue
            left,right=empirical[i].ravel(),empirical[j].ravel();shared=np.isfinite(left)&np.isfinite(right)
            count=int(shared.sum())
            if count<30:continue
            ll,rr=left[shared],right[shared]
            correlation=float(np.corrcoef(ll,rr)[0,1]) if ll.std()>0 and rr.std()>0 else None
            neighbors.append(dict(id=j,shared=count,correlation=correlation,difference=float(np.mean(abs(ll-rr)))))
        neighbors.sort(key=lambda r:r['difference'])
        heads=[]
        for j in range(n):
            if i==j or names[j] not in active_names:continue
            paired=empirical[i,j];valid=np.isfinite(paired)
            if valid.sum()>=3:
                heads.append(dict(id=j,paired_maps=int(valid.sum()),observed_score=float(paired[valid].mean())))
        heads.sort(key=lambda r:(-support[r['id']]['games'],-r['paired_maps']))
        refs={x['id'] for x in heads if x['id'] in panel}
        heads=[x for x in heads if x['id'] in refs]+[x for x in heads if x['id'] not in refs]
        short=re.sub(r'-(v|x|s)(\d+).*',lambda z:' '+z[1]+z[2],name).replace('monte_christo','Monte Christo')
        short=short[0].upper()+short[1:]
        bymap=[]
        for k,mp in enumerate(maps):
            observed_count=int((((a==i)|(b==i))&(board==k)).sum())
            bymap.append(dict(name=mp,score=float(map_scores[i,k]),delta=float(delta[i,k]),
                low=float(min(dlo[i,k],delta[i,k])),high=float(max(dhi[i,k],delta[i,k])),games=observed_count))
        bots.append(dict(id=i,name=name,short=short,score=float(scores[i]),low=float(lo[i]),high=float(hi[i]),
            established=bool(established[i]),**support[i],map_profile=bymap,similar=neighbors[:3],head_to_head=heads[:6]))
    progress=json.loads((campaign/'progress.json').read_text())
    with sqlite3.connect((campaign/'results.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        journal=[json.loads(x[0]) for x in db.execute('SELECT data FROM games')]
    started=datetime.fromisoformat(json.loads((campaign/'launch.json').read_text())['started']).timestamp()
    timeline=[dict(time=started,games=0)];errors=[];finished=[]
    for game in journal:
        if game['outcome']=='error':
            errors.append({k:game.get(k) for k in ('team_a','team_b','map','error')});continue
        path=campaign/'games'/game['log']
        if path.exists():finished.append(path.stat().st_mtime)
    for k,timestamp in enumerate(sorted(finished),1):timeline.append(dict(time=timestamp,games=k))
    # Keep no more than ~150 points, including the newest completion.
    step=max(1,len(timeline)//150);timeline=timeline[::step]+[timeline[-1]]
    try:
        with FileLock(str(campaign/'.run.lock'),timeout=0):running=False
    except Timeout:running=True
    matching=[r for records in games.values() for r in records]
    payload=dict(at=datetime.now(timezone.utc).isoformat(),data_at=data_at,campaign=str(campaign),running=running,
        model_q=model['q'],matching_records=len(matching),
        source_counts=dict(Counter(r['source'] for r in matching)),
        source_hashes=manifest['effective_hashes'],map_hashes=manifest['map_hashes'],
        native=True,bots=bots,maps=maps,map_weights=distribution,
        map_weight_policy=manifest.get('map_weight_policy',dict(kind='uniform')),
        reference_ids=panel.tolist(),fixtures=len(y),ledger_games=len(rows),
        rating_context_bots=n-len(active_names),
        established=sum(b['established'] for b in bots),provisional=sum(not b['established'] for b in bots),
        adaptive_completed=len(finished),errors=errors,blocked=progress['blocked_bots'],timeline=timeline,
        validation=validation,fit_converged=model['success'],bootstrap_converged=sum(success),bootstrap_count=24)
    (out/'dashboard.json').write_text(json.dumps(payload,separators=(',',':'),allow_nan=False)+'\n')
    np.savez_compressed(out/'fit.npz',parameters=model['x'],bootstrap=np.asarray(boot))
    print('Leaders',[(x['short'],round(x['score'],3),x['games']) for x in sorted(bots,key=lambda b:-b['score'])[:15]],flush=True)
    return payload


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output.resolve())
