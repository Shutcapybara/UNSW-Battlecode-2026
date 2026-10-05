import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, gzip, collections, sys, glob
sys.path.insert(0,'tools/learn')
import rebuild, emu
TPL={}
for f in glob.glob('maps/live/*.map'):
    t=open(f).read(); m=rebuild.Map(t); TPL[m.name]=m
def load(fn='build/learn/kageyama/beds/ev_all.jsonl.gz'):
    G=[]
    for l in gzip.open(fn,'rt'):
        d=json.loads(l)
        if 'ev' in d: G.append(d)
    return G
def obs(d):
    """non-death appearances [(round,cell)], presence timeline"""
    dr=set(d['deaths'])|{x+1 for x in d['deaths']}
    return [(r,(x,y)) for r,x,y,v in d['ev'] if v and r not in dr]
def beds_of(m): return {c:v for c,v in m.tiles.items() if v[1]>0}
def score(d, beds, m):
    P,out=emu.schedule(beds,m.W,m.H,m.symmetry,int(d['seed'],16),rounds=d['last']+1)
    ex=set()
    for c,p in P:
        for r in out[c]: ex.add((r,c)); ex.add((r,p))
    a=obs(d); ok=sum(1 for x in a if x in ex)
    return ok, len(a)
import numpy as np
from gens import mt64
_U={}
def U(seed_hex, n):
    k=seed_hex
    if k not in _U or len(_U[k])<n:
        g=mt64(int(seed_hex,16)); _U[k]=np.array([next(g) for _ in range(n)],dtype=np.uint64)
    return _U[k][:n]
def group(G, mapname, fail=True):
    m=TPL[mapname]; out=[]
    for d in G:
        if d['map']!=mapname: continue
        ok,n=score(d,beds_of(m),m)
        if (ok<n) == fail: out.append(d)
    return out
def candidates(Gs, W,H,sym, minfrac=0.02):
    cnt=collections.Counter()
    for d in Gs: cnt.update({c for r,c in obs(d)})
    cells={c for c,n in cnt.items() if n>=minfrac*len(Gs)}
    cells|={emu.partner(c,W,H,sym) for c in cells}
    return cells, cnt
def first_app(d, c, p):
    a=[r for r,x in obs(d) if x in (c,p)]
    return min(a) if a else None
def fit_pairs(Gs, P, W,H,sym, maxspan=700, maxlo=60):
    n=len(P)
    res=[]
    Us=[U(d['seed'],n) for d in Gs]
    for j,(c,p) in enumerate(P):
        f=np.array([ (first_app(d,c,p) if first_app(d,c,p) is not None else -9) for d in Gs]); seen=f>=0
        u=np.array([x[j] for x in Us],dtype=np.uint64)
        best=(-1,)
        for s in range(1,maxspan+1):
            lo=f+1-(u%np.uint64(s)).astype(np.int64)
            v=lo[seen]; v=v[(v>=1)&(v<=maxlo)]
            if len(v)==0: continue
            vals,cn=np.unique(v,return_counts=True); k=cn.argmax()
            if cn[k]>best[0]: best=(cn[k],int(vals[k]),s)
        res.append(dict(j=j,pair=(c,p),nseen=int(seen.sum()),hits=best[0],lo=best[1],span=best[2]))
    return res
def build(res, W,H,sym):
    beds={}
    for r in res:
        c,p=r['pair']; v=(r['lo'],r['lo']+r['span']-1); beds[c]=v; beds[p]=v
    return beds
def evaluate(Gs, beds, m):
    fr=[]; 
    for d in Gs:
        ok,n=score(d,beds,m); fr.append(ok/max(n,1))
    fr=np.array(fr); return dict(n=len(fr), full=int((fr==1).sum()), ge99=int((fr>=.99).sum()), q=[round(float(x),3) for x in np.quantile(fr,[0,.05,.25,.5])])
def fit_pairs2(Gs, P, maxspan=1100, maxlo=60, tol=0.97):
    """like fit_pairs but returns, per pair, all (lo,hi) with hits >= tol*best"""
    n=len(P); res=[]
    Us=[U(d['seed'],n) for d in Gs]
    for j,(c,p) in enumerate(P):
        f=np.array([ (first_app(d,c,p) if first_app(d,c,p) is not None else -9) for d in Gs]); seen=f>=0
        last=np.array([d['last'] for d in Gs])
        u=np.array([x[j] for x in Us],dtype=np.uint64)
        cand=[]
        for s in range(1,maxspan+1):
            um=(u%np.uint64(s)).astype(np.int64)
            lo=f+1-um
            v=lo[seen]; v=v[(v>=1)&(v<=maxlo)]
            if len(v)==0: continue
            vals,cn=np.unique(v,return_counts=True); k=cn.argmax(); L=int(vals[k])
            # penalty: unseen games whose predicted first appearance falls inside the game
            pen=int(((~seen)&(L-1+um<last-5)).sum())
            cand.append((int(cn[k])-pen,L,s))
        if not cand: res.append(dict(j=j,pair=(c,p),nseen=0,best=0,cands=[])); continue
        b=max(x[0] for x in cand)
        res.append(dict(j=j,pair=(c,p),nseen=int(seen.sum()),best=b,cands=[(L,L+s-1,h) for h,L,s in cand if h>=b-max(1,(1-tol)*abs(b))]))
    return res
def fit_free(Gs, pairs, kmax=80, spans=range(1,1101), maxlo=60):
    Us=[U(d['seed'],kmax) for d in Gs]; out=[]
    UU=np.array(Us,dtype=np.uint64)  # games x k
    for (c,p) in pairs:
        f=np.array([ (first_app(d,c,p) if first_app(d,c,p) is not None else -9) for d in Gs]); seen=f>=0
        best=(-1,)
        for k in range(kmax):
            u=UU[:,k]
            for s in spans:
                lo=f[seen]+1-(u[seen]%np.uint64(s)).astype(np.int64)
                v=lo[(lo>=1)&(lo<=maxlo)]
                if len(v)==0: continue
                vals,cn=np.unique(v,return_counts=True); i=cn.argmax()
                if cn[i]>best[0]: best=(int(cn[i]),k,int(vals[i]),s)
        out.append(dict(pair=(c,p),nseen=int(seen.sum()),best=best))
    return out
def fit_seq(Gs, pairs, window=12, spans=range(1,2701), maxlo=60, kmax=400):
    """sequential: pair i gets stream index k in (prev, prev+window]; best (lo,span) by hits - early*2"""
    UU=np.array([U(d['seed'],kmax) for d in Gs],dtype=np.uint64)
    last=np.array([d['last'] for d in Gs])
    out=[]; prev=-1
    for (c,p) in pairs:
        f=np.array([ (first_app(d,c,p) if first_app(d,c,p) is not None else -9) for d in Gs]); seen=f>=0
        best=(-10**9,)
        for k in range(prev+1, min(prev+1+window,kmax)):
            u=UU[:,k]
            for s in spans:
                um=(u%np.uint64(s)).astype(np.int64)
                lo=f[seen]+1-um[seen]
                v=lo[(lo>=1)&(lo<=maxlo)]
                if len(v)==0: continue
                vals,cn=np.unique(v,return_counts=True); i=cn.argmax(); L=int(vals[i])
                early=int((seen&(f<L-1+um)).sum())
                sc=int(cn[i])-2*early
                if sc>best[0]: best=(sc,k,L,s,int(cn[i]),early)
        if best[0]>-10**9 and best[0]>0: prev=best[1]
        out.append(dict(pair=(c,p),nseen=int(seen.sum()),best=best))
        print(c,p,int(seen.sum()),best,flush=True)
    return out
def fit_rank(Gs, P, spans=range(1,2701), maxlo=60, wl=0.5, we=2.0):
    n=len(P); UU=np.array([U(d['seed'],n) for d in Gs],dtype=np.uint64)
    last=np.array([d['last'] for d in Gs]); out=[]
    for j,(c,p) in enumerate(P):
        f=np.array([ (first_app(d,c,p) if first_app(d,c,p) is not None else -9) for d in Gs]); seen=f>=0
        u=UU[:,j]; cands=[]
        for s in spans:
            um=(u%np.uint64(s)).astype(np.int64)
            lo=f[seen]+1-um[seen]; v=lo[(lo>=1)&(lo<=maxlo)]
            if not len(v): continue
            vals,cn=np.unique(v,return_counts=True); Ls={int(x) for x in vals[np.argsort(-cn)[:2]]}
            for L in Ls:
                pr=L-1+um
                hit=int((seen&(f==pr)).sum()); early=int((seen&(f<pr)).sum()); late=int((seen&(f>pr)).sum())
                due=int(((~seen)&(pr<last-3)).sum())
                cands.append((hit-we*early-wl*late-wl*due,L,L+s-1,hit,early,late,due))
        cands.sort(reverse=True)
        out.append(dict(j=j,pair=(c,p),nseen=int(seen.sum()),cands=cands[:5]))
    return out
