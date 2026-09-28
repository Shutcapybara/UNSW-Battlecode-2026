#!/usr/bin/env python3
"""Aggregate the seeded panel and fit ridge logistic regression."""
import collections, json, math, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=Path(__file__).resolve().parent
ALL_ROWS=[json.loads(x) for x in (RUN/"results.jsonl").read_text().splitlines() if x.strip()]
ERRORS=sum(r.get("winner")=="error" for r in ALL_ROWS)
ROWS=[r for r in ALL_ROWS if r.get("winner") in ("A","B","draw")]
TARGET={"compact":{"units_r25":6,"units_r50":9,"units_r100":13,"total_r250":0},
        "open":{"units_r25":6,"units_r50":9,"units_r100":15,"total_r250":54.5}}
MC={}
for p in (ROOT/"maps").glob("*.map"):
    with p.open() as f: _, dims=f.readline().split(maxsplit=1); w,h=map(int,dims.split()[:2])
    MC[p.stem]="compact" if w*h<=625 else "open"
def q(a,p):
    if not a: return float("nan")
    z=sorted(a); return z[min(len(z)-1,round(p*(len(z)-1)))]
def med(a): return statistics.median(a) if a else float("nan")
def stat(r,k): return r.get("stats",{}).get(k,0)
def cp(r,stage,k): return r.get("checkpoints",{}).get(str(stage),{}).get(k,0)
def sign_p(b,w):
    n=min(b,w)
    return 1.0 if b+w==0 else min(1.0,2*sum(math.comb(b+w,k) for k in range(n+1))/2**(b+w))
def auc(y,p):
    pos=[v for a,v in zip(y,p) if a==1]; neg=[v for a,v in zip(y,p) if a==0]
    return float("nan") if not pos or not neg else sum(1 if a>b else .5 if a==b else 0 for a in pos for b in neg)/(len(pos)*len(neg))
NAMES=["units_r25","units_r50","units_r100","total_r250","longest_r400","wall_deaths_k","self_deaths_k","body_deaths_k","h2h_deaths_k","splits_100turns","newborn_deaths_100births","portal_steps_k","sonar_rays_turn"]
def features(r):
    t=max(1,stat(r,"turns")); b=max(1,stat(r,"splits"))
    v=[cp(r,25,"units"),cp(r,50,"units"),cp(r,100,"units"),cp(r,250,"total"),cp(r,400,"longest")]
    v += [1000*stat(r,k)/t for k in ("death_wall","death_self","death_body","death_h2h")]
    v += [100*stat(r,"splits")/t,100*stat(r,"newborn_deaths_10")/b,1000*stat(r,"portal_steps")/t,stat(r,"sonar")/t]
    return v
def fit(rows):
    X=[features(r) for r in rows]; y=[float(r["score"]) for r in rows]
    means=[statistics.mean(c) for c in zip(*X)]; stds=[statistics.pstdev(c) or 1 for c in zip(*X)]
    Z=[[(v-m)/s for v,m,s in zip(x,means,stds)] for x in X]
    beta=[0.]*(len(NAMES)+1); rate=.18; ridge=1.
    for _ in range(1800):
        g=[0.] * len(beta)
        for x,y0 in zip(Z,y):
            z=max(-30,min(30,beta[0]+sum(a*b for a,b in zip(x,beta[1:])))); e=1/(1+math.exp(-z))-y0
            g[0]+=e
            for j,v in enumerate(x,1): g[j]+=e*v
        n=max(1,len(Z)); beta[0]-=rate*g[0]/n
        for j in range(1,len(beta)): beta[j]-=rate*(g[j]/n+ridge*beta[j]/n)
    return beta,means,stds
print("usable games=%d errors=%d" % (len(ROWS),ERRORS))
for arm in sorted({r["arm"] for r in ROWS}):
  for cls in ("compact","open"):
    rr=[r for r in ROWS if r["arm"]==arm and MC.get(r["map"])==cls]
    if not rr: continue
    print("%s %s n=%d" % (arm,cls,len(rr)))
    for st,key in ((25,"units"),(50,"units"),(100,"units"),(250,"total")):
      vs=[cp(r,st,key) for r in rr]; target=TARGET[cls]["total_r250" if st==250 else "units_r%d"%st]
      print("  r%d %s q25=%.2f median=%.2f target=%.2f%s" % (st,key,q(vs,.25),med(vs),target,(" on_pace=%.3f"%(sum(v>=target for v in vs)/len(vs))) if st==100 else ""))
    for st in (25,50,100,250,400):
      print("  survive r%d %.3f" % (st,sum(cp(r,st,"units")>0 for r in rr)/len(rr)))
ix={(r["arm"],r["map"],r["side"],r["seed"],r["opponent"]):r for r in ROWS}
for arm in ("pace","pace-nolimit"):
    b=w=t=0; ds=[]; clsds=collections.defaultdict(list)
    mat={k:[] for k in ("units_r25","units_r50","units_r100","total_r250")}
    mk={"units_r25":(25,"units"),"units_r50":(50,"units"),"units_r100":(100,"units"),"total_r250":(250,"total")}
    for r in ROWS:
      if r["arm"]!="host": continue
      a=ix.get((arm,r["map"],r["side"],r["seed"],r["opponent"]))
      if not a: continue
      d=a["score"]-r["score"]; ds.append(d); clsds[MC[r["map"]]].append(d)
      for k,(stage,key) in mk.items(): mat[k].append(cp(a,stage,key)-cp(r,stage,key))
      if d>0:b+=1
      elif d<0:w+=1
      else:t+=1
    print("paired %s vs host n=%d delta=%.4f better=%d worse=%d tied=%d sign_p=%.5g"%(arm,len(ds),statistics.mean(ds) if ds else float("nan"),b,w,t,sign_p(b,w)))
    for cls,vals in clsds.items(): print("  %s delta=%.4f n=%d"%(cls,statistics.mean(vals),len(vals)))
    print("  paired material deltas: "+", ".join("%s %.2f"%(k,med(v)) for k,v in mat.items()))
    fired=sum(any("ACT:pace+" in k or "ACT:pace-" in k for k in r.get("activation",{})) for r in ROWS if r["arm"]==arm)
    narm=sum(r["arm"]==arm for r in ROWS)
    print("  marker games %d/%d"%(fired,narm))
# The contrast between the constrained and no-limit arms estimates the
# outcome cost of the survival guards on exact shared fixtures.
b=w=t=0; ds=[]; diffs=collections.defaultdict(list)
for r in ROWS:
  if r["arm"]!="pace": continue
  a=ix.get(("pace-nolimit",r["map"],r["side"],r["seed"],r["opponent"]))
  if not a: continue
  d=r["score"]-a["score"]; ds.append(d); diffs[MC[r["map"]]].append(d)
  if d>0:b+=1
  elif d<0:w+=1
  else:t+=1
print("paired pace minus nolimit n=%d delta=%.4f better=%d worse=%d tied=%d sign_p=%.5g"%(len(ds),statistics.mean(ds) if ds else float("nan"),b,w,t,sign_p(b,w)))
for cls,vals in diffs.items(): print("  %s delta=%.4f n=%d"%(cls,statistics.mean(vals),len(vals)))
for arm in ("pace","pace-nolimit"):
  rr=[r for r in ROWS if r["arm"]==arm]
  wallself=[1000*(stat(r,"death_wall")+stat(r,"death_self"))/max(1,stat(r,"turns")) for r in rr]
  nb=[100*stat(r,"newborn_deaths_10")/max(1,stat(r,"splits")) for r in rr]
  print("safety %s median wall+self/1k turns %.3f newborn_deaths/100 births %.2f"%(arm,med(wallself),med(nb)))
beta,means,stds=fit(ROWS)
print("ridge logistic coefficients (standardized):")
for n,c in sorted(zip(NAMES,beta[1:]),key=lambda z:-abs(z[1])): print("  %s %.5f"%(n,c))
valid=[r for r in ROWS if r["score"] in (0,1)]
def predict(rows,b,means,stds):
    out=[]
    for r in rows:
      z=max(-30,min(30,b[0]+sum(c*(x-m)/s for c,x,m,s in zip(b[1:],features(r),means,stds))))
      out.append(1/(1+math.exp(-z)))
    return out
print("overall AUC %.4f"%auc([int(r["score"]==1) for r in valid],predict(valid,beta,means,stds)))
fold=[]
for held in sorted({r["map"] for r in valid}):
    train=[r for r in valid if r["map"]!=held]; test=[r for r in valid if r["map"]==held]
    if len(test)<2: continue
    b,m,s=fit(train); fold.append(auc([int(r["score"]==1) for r in test],predict(test,b,m,s)))
print("leave-one-map-out AUC mean %.4f folds %d"%(statistics.mean([x for x in fold if not math.isnan(x)]),len(fold)))
