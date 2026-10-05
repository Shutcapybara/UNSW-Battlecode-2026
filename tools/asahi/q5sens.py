#!/usr/bin/env python3
"""Sensitivity of the paired 5th percentile to the bootstrap seed (seeds 1-40; card convention is seed 7). Sensitivity only.
    python tools/asahi/q5sens.py <cand> <base> <panel>   (cwd = wt-asahi)
"""
import json,glob,random,sys
def load(bot,panel):
    f=glob.glob(f'build/asahi/runs/{bot}/*/{panel}/index.jsonl')
    best=max(f,key=lambda p:sum(json.loads(l).get("rc")==0 for l in open(p)))
    d={}
    for l in open(best):
        r=json.loads(l)
        if r.get("rc")!=0 or r["seed"]!=1: continue
        d[(r['seed'],r['map'],r['opp'],r['seat'])]=1.0 if r['winner']==r['seat'] else (0.5 if r['winner'] in (None,'draw','D') else 0.0)
    return d
a=load(sys.argv[1],sys.argv[3]); b=load(sys.argv[2],sys.argv[3])
keys=sorted(set(a)&set(b)); cl={}
for k in keys: cl.setdefault((k[1],k[2]),[]).append(a[k]-b[k])
C=list(cl.values()); n=len(keys); pt=sum(map(sum,C))/n*100
def q5(seed):
    rng=random.Random(seed); bs=[]
    for _ in range(1000):
        s=[C[rng.randrange(len(C))] for _ in C]; bs.append(sum(map(sum,s))/sum(map(len,s))*100)
    bs.sort(); x=.05*999; i=int(x); return bs[i]+(bs[i+1]-bs[i])*(x-i)
v=sorted(q5(s) for s in range(1,41))
print(f'{sys.argv[1]} vs {sys.argv[2]} {sys.argv[3]}: n {n} miss {len(set(a)^set(b))} pt {pt:+.2f} seed7 q5 {q5(7):+.2f}; 40 seeds q5 min {v[0]:+.2f} median {(v[19]+v[20])/2:+.2f} max {v[-1]:+.2f}; share <= -5: {sum(x<=-5 for x in v)}/40')
