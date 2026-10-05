#!/usr/bin/env python3
"""Paired pool difference between two Asahi runs (seed 1): candidate wins minus base wins per fixture (seed, map, opp,
seat), cluster bootstrap over map x opp, 1,000 resamples, seed 7, linear 5th-95th. Reproduces card.py Δwin.
    python tools/asahi/pairdiff.py <bot_a> <bot_b>   (cwd = wt-asahi)
"""
import json,glob,random,sys
def load(bot):
    f=[p for p in glob.glob(f'build/asahi/runs/{bot}/*/pool/index.jsonl')]
    best=max(f,key=lambda p:sum(json.loads(l).get("rc")==0 for l in open(p)))
    d={}
    for l in open(best):
        r=json.loads(l)
        if r.get("rc")!=0 or r["seed"]!=1: continue
        d[(r['seed'],r['map'],r['opp'],r['seat'])]=1.0 if r['winner']==r['seat'] else (0.5 if r['winner'] in (None,'draw','D') else 0.0)
    return d,best
a,pa=load(sys.argv[1]); b,pb=load(sys.argv[2]); print(pa,pb)
keys=sorted(set(a)&set(b)); print('pairs',len(keys),'missing',len(set(a)^set(b)))
cl={}
for k in keys: cl.setdefault((k[1],k[2]),[]).append(a[k]-b[k])
C=list(cl.values()); n=len(keys)
pt=sum(sum(c) for c in C)/n*100
rng=random.Random(7); bs=[]
for _ in range(1000):
    s=[C[rng.randrange(len(C))] for _ in C]; bs.append(sum(sum(c) for c in s)/sum(len(c) for c in s)*100)
bs.sort()
import statistics
def q(p):
    x=p*(len(bs)-1); i=int(x); return bs[i]+(bs[min(i+1,len(bs)-1)]-bs[i])*(x-i)
print(f'{sys.argv[1]} - {sys.argv[2]}: {pt:+.2f} [{q(.05):+.2f}, {q(.95):+.2f}] clusters {len(C)}; W {sum(a[k] for k in keys)} vs {sum(b[k] for k in keys)}')
