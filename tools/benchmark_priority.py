"""Bounded, adaptive batches: optimistic contenders versus informative opponents.

This is a scheduling heuristic, not a calibrated ranking/confidence service.
The cheap map-aware Bradley–Terry fit is refreshed between batches. Approximate
diagonal information ignores parameter covariances and matchup cycles.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
from collections import Counter
import re

import numpy as np
from scipy.special import expit
from performance_model import fit, unpack
from benchmark_weights import normalized_weights
from benchmark_data import with_rating_context


def lineage(name):
    return re.split(r'-[vxs]\d+', name, maxsplit=1)[0]


def adaptive_batch(manifest, games, excluded=(), blocked=(), size=128):
    """Return missing ordered fixtures plus a compact, reviewable decision trace."""
    active = set(manifest['bots'])
    context_manifest = with_rating_context(manifest) if 'rating_context' in manifest else manifest
    names, maps = context_manifest['bots'], manifest['maps']
    n, m = len(names), len(maps)
    distribution = normalized_weights(manifest)
    map_weights = np.array([distribution[name] for name in maps])
    ni = {name:i for i,name in enumerate(names)}
    mi = {name:i for i,name in enumerate(maps)}
    data = [(ni[a], ni[b], mi[board], np.mean([
        1 if r['outcome']=='A' else .5 if r['outcome']=='draw' else 0 for r in rs]))
        for (a,b,board),rs in sorted(games.items())]
    if data:
        a,b,board,y = [np.asarray(x) for x in zip(*data)]
        a,b,board = [v.astype(int) for v in (a,b,board)]
        model = fit((a,b,board,y),n,m,q=0)
        s,t,initiative,_,_ = unpack(model['x'],n,m,0)
        converged = model['success']
        # Non-convergence should not quietly make an arbitrary fit authoritative.
        if not converged:
            s,t,initiative = np.zeros(n),np.zeros((n,m)),np.zeros(m)
        probability = expit(s[a]-s[b]+t[a,board]-t[b,board]+initiative[board])
        information = probability*(1-probability)
    else:
        a=b=board=np.array([],dtype=int); information=np.array([])
        s,t,initiative=np.zeros(n),np.zeros((n,m)),np.zeros(m)
        converged=True
    counts=np.bincount(np.r_[a,b],minlength=n).astype(float)
    info=(np.bincount(a,information,minlength=n)+np.bincount(b,information,minlength=n)).astype(float)
    map_info=np.zeros((n,m)); np.add.at(map_info,(a,board),information); np.add.at(map_info,(b,board),information)
    pair_count=np.zeros((n,n)); np.add.at(pair_count,(a,b),1); np.add.at(pair_count,(b,a),1)
    family_ids={f:i for i,f in enumerate(sorted({lineage(name) for name in names}))}
    family=np.array([family_ids[lineage(name)] for name in names])
    family_count=np.zeros((n,len(family_ids)))
    np.add.at(family_count,(a,family[b]),1); np.add.at(family_count,(b,family[a]),1)
    rating=s+t@map_weights
    # Target the upper fifth. A sparse bot's optimistic rating keeps it eligible.
    active_ids=np.array([i for i,name in enumerate(names) if name in active])
    cutoff=float(np.quantile(rating[active_ids],.8))
    left,right=np.triu_indices(len(active_ids),1)
    left,right=active_ids[left],active_ids[right]
    aa=np.repeat(left,m); bb=np.repeat(right,m); mm=np.tile(np.arange(m),len(left))
    keys=[(names[i],names[j],maps[k]) for i,j,k in zip(aa,bb,mm)]
    unavailable=set(games)|set(excluded)
    missing=np.array([[f not in unavailable,(f[1],f[0],f[2]) not in unavailable] for f in keys],dtype=bool)
    blocked=set(blocked)
    valid=missing.any(axis=1)&np.array([x not in blocked and z not in blocked for x,z,_ in keys])
    margin=s[aa]-s[bb]+t[aa,mm]-t[bb,mm]
    p1,p2=expit(margin+initiative[mm]),expit(margin-initiative[mm])
    fisher=(p1*(1-p1)+p2*(1-p2))/2
    queue=[];trace=[];reason_counts=Counter()
    # A fixed tie order is reproducible; it is unrelated to the engine's seed.
    tie=np.random.default_rng(260926).random(len(keys))*1e-10
    while valid.any() and len(queue)<size:
        variance=1/(.2+info)
        optimistic=rating+1.5*np.sqrt(variance)
        promise=.1+.9*expit((optimistic-cutoff)/.4)
        # Known, diverse opponents anchor new bots better than two unknowns.
        support=.25+.75*np.minimum((pair_count>0).sum(axis=1)/8,1)
        va=variance[aa]+1/(5+map_info[aa,mm])
        vb=variance[bb]+1/(5+map_info[bb,mm])
        novelty=1/np.sqrt(1+pair_count[aa,bb]/4)
        diversity_a=1/np.sqrt(1+family_count[aa,family[bb]]/20)
        diversity_b=1/np.sqrt(1+family_count[bb,family[aa]]/20)
        gain_a=fisher*va*support[bb]*novelty*diversity_a
        gain_b=fisher*vb*support[aa]*novelty*diversity_b
        reason='contender'
        if len(trace)%5==0:
            # Reserve 20% of blocks for exploration; weak/unknown bots aren't discarded.
            eligible=np.unique(np.r_[aa[valid],bb[valid]])
            focal=min(eligible,key=lambda i:(counts[i],names[i]))
            utility=np.where(aa==focal,gain_a,0)+np.where(bb==focal,gain_b,0)
            allowed=valid&((aa==focal)|(bb==focal)); reason='coverage'
        else:
            utility=promise[aa]*gain_a+promise[bb]*gain_b
            allowed=valid
        # Complete a half-observed side pair, without allowing that to dominate.
        utility*=np.where(missing.sum(axis=1)==1,1.15,1)
        # Weight information gain by the target distribution, not map-file count.
        # Coverage and diminishing map information still allow every positive map.
        utility*=map_weights[mm]*m
        j=int(np.argmax(np.where(allowed,utility+tie,-np.inf)))
        x,z,k=int(aa[j]),int(bb[j]),int(mm[j])
        f=keys[j];block=[]
        if missing[j,0]:block.append(f)
        if missing[j,1]:block.append((f[1],f[0],f[2]))
        queue.extend(block);valid[j]=False
        trace.append(dict(bot_a=f[0],bot_b=f[1],map=f[2],reason=reason,
            predicted_a_score=float((p1[j]+p2[j])/2),priority=float(utility[j]),
            map_weight=float(map_weights[k])))
        reason_counts[reason]+=1
        # Account for planned work before selecting the next block in this batch.
        increment=len(block)*fisher[j]
        info[[x,z]]+=increment;map_info[[x,z],k]+=increment;counts[[x,z]]+=len(block)
        pair_count[x,z]+=len(block);pair_count[z,x]+=len(block)
        family_count[x,family[z]]+=len(block);family_count[z,family[x]]+=len(block)
    return queue,dict(model='map-aware Bradley-Terry; heuristic uncertainty',fit_converged=converged,
        observed_fixtures=len(data),batch_games=len(queue),map_weights=distribution,
        active_bots=len(active),rating_context_bots=n-len(active),
        reason_counts=dict(reason_counts),selections=trace)
