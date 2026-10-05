#!/usr/bin/env python3
"""Paired h2h difference (102 games, seeds 1-3) between two Asahi runs: map x seed cluster bootstrap, 1,000 x seed 7, linear 5-95 %.
    python tools/asahi/h2hpd.py <cand> <base>   (cwd = wt-asahi)
"""
import json,glob,random,sys
def load(bot):
    f=glob.glob(f'build/asahi/runs/{bot}/*/h2h/index.jsonl')
    best=max(f,key=lambda p:sum(json.loads(l).get("rc")==0 for l in open(p)))
    d={}
    for l in open(best):
        r=json.loads(l)
        if r.get("rc")!=0: continue
        d[(r['seed'],r['map'],r['opp'],r['seat'])]=1.0 if r['winner']==r['seat'] else (0.5 if r['winner'] in (None,'draw','D') else 0.0)
    return d
a=load(sys.argv[1]); b=load(sys.argv[2])
keys=sorted(set(a)&set(b))
cl={}
for k in keys: cl.setdefault((k[0],k[1]),[]).append(a[k]-b[k])
C=list(cl.values()); n=len(keys); pt=sum(map(sum,C))/n*100
rng=random.Random(7); bs=[]
for _ in range(1000):
    s=[C[rng.randrange(len(C))] for _ in C]; bs.append(sum(map(sum,s))/sum(map(len,s))*100)
bs.sort()
def q(p):
    x=p*(len(bs)-1); i=int(x); return bs[i]+(bs[min(i+1,len(bs)-1)]-bs[i])*(x-i)
wa=sum(a[k] for k in keys); wb=sum(b[k] for k in keys)
print(f'{sys.argv[1]} {wa:g}-{n-wa:g} vs {sys.argv[2]} {wb:g}-{n-wb:g}; n {n} miss {len(set(a)^set(b))}; diff {pt:+.2f} [{q(.05):+.2f},{q(.95):+.2f}] cl {len(C)}')
