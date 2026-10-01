"""Descriptive incidence rates; stratified fixture-block bootstrap, not causal effects."""
import collections,json,sys
from pathlib import Path
import numpy as np
p=Path(sys.argv[1]); rows=[json.loads(l) for l in (p/'exposure-rows.jsonl').read_text().splitlines()]; assert len(rows)==160
pockets={'Autarky','Prisoners Dilemma','Slithery Fight'}
rr=[r for r in rows if r['map'] not in pockets]; assert len(rr)==112
maps=collections.defaultdict(lambda:collections.Counter());tot=collections.Counter()
for r in rr:
    for c in r['cells']:
        for k in ['risk','deaths']:maps[r['map']][c['band']+'_'+k]+=c[k];tot[c['band']+'_'+k]+=c[k]
assert sum(sum(r['deaths'].values()) for r in rows)==sum(r['queen_death'] is not None for r in rows)
# Both seats resampled together, within map. One seed; no between-seed uncertainty measured.
blocks=sorted({(r['map'],r['opponent']) for r in rr}); bi={b:i for i,b in enumerate(blocks)}
rng=np.random.default_rng(20261002)
boot=[]
for _ in range(1000):
    weights=np.zeros(len(blocks),dtype=int)
    for m in sorted(maps):
        inds=[i for i,b in enumerate(blocks) if b[0]==m];chosen=rng.choice(inds,len(inds),replace=True)
        np.add.at(weights,chosen,1)
    boot.append(weights)

def calc(keys):
    strata=sorted({tuple([r['map']]+[c[k] for k in keys]) for r in rr for c in r['cells'] if c['band'] in ['after1-3','other']})
    si={x:i for i,x in enumerate(strata)};a=np.zeros((len(blocks),len(strata),4))
    for r in rr:
        for c in r['cells']:
            if c['band'] not in ['after1-3','other']:continue
            j=si[tuple([r['map']]+[c[k] for k in keys])];b=bi[(r['map'],r['opponent'])];k=0 if c['band']=='after1-3' else 2
            a[b,j,k]+=c['deaths'];a[b,j,k+1]+=c['risk']
    def est(x):
        d1,t1,d0,t0=x.T;ok=(t1>0)&(t0>0);den=t1[ok]+t0[ok]
        nu=np.sum(d1[ok]*t0[ok]/den);de=np.sum(d0[ok]*t1[ok]/den)
        return float(nu/de) if de>0 else None
    point=est(a.sum(axis=0));samples=[est(np.tensordot(w,a,axes=(0,0))) for w in boot];samples=[x for x in samples if x is not None]
    x=a.sum(axis=0);ok=(x[:,1]>0)&(x[:,3]>0)
    return dict(strata=['map']+keys,rate_ratio=point,ci95=np.quantile(samples,[.025,.975]).tolist(),bootstrap_valid=len(samples),common_strata=int(ok.sum()),all_strata=len(strata),common_after_risk=int(x[ok,1].sum()),all_after_risk=int(x[:,1].sum()),common_other_risk=int(x[ok,3].sum()),all_other_risk=int(x[:,3].sum()))
# Crude ratio and its same fixture-block bootstrap.
a=np.zeros((len(blocks),4))
for r in rr:
    for c in r['cells']:
        if c['band'] not in ['after1-3','other']:continue
        k=0 if c['band']=='after1-3' else 2;a[bi[(r['map'],r['opponent'])],k]+=c['deaths'];a[bi[(r['map'],r['opponent'])],k+1]+=c['risk']
def crude(x):return (x[0]/x[1])/(x[2]/x[3])
crudes=[crude(w@a) for w in boot]
s=dict(n_games=160,nonpocket_games=112,fixture_blocks=len(blocks),pocket_games=48,seed=1,cache_sources=dict(collections.Counter(r['source'] for r in rows)),all_queen_deaths=sum(r['queen_death'] is not None for r in rows),nonpocket_queen_deaths=sum(r['queen_death'] is not None for r in rr),total=dict(tot),per_map={m:dict(v) for m,v in sorted(maps.items())},crude_rr=float(crude(a.sum(axis=0))),crude_ci95=np.quantile(crudes,[.025,.975]).tolist(),adjusted=[calc(['phase']),calc(['phase','length']),calc(['phase','length','ally2','enemy3'])])
(p/'exposure-summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
