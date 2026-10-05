import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gens import mt64
def partner(c,W,H,sym):
    x,y=c; return {'y':(W-1-x,y),'x':(x,H-1-y),'xy':(W-1-x,H-1-y)}.get(sym,c)
def pair_order(cells,W,H,sym):
    seen=set(); out=[]
    for c in sorted(cells,key=lambda c:(c[1],c[0])):
        if c in seen: continue
        p=partner(c,W,H,sym); seen|={c,p}; out.append((c,p))
    return out
def schedule(beds,W,H,sym,seed,rounds=500):
    """{pair first cell: [expiry rounds]} emulating the engine: mt19937_64(seed), draw = lo + u % span"""
    g=mt64(seed); P=pair_order(beds,W,H,sym)
    exp={}; out={c:[] for c,p in P}
    for c,p in P:
        lo,hi=beds[c]; exp[c]=-1+lo+next(g)%(hi-lo+1); out[c].append(exp[c])
    for r in range(rounds):
        for c,p in P:
            if exp[c]==r:
                lo,hi=beds[c]; exp[c]=r+lo+next(g)%(hi-lo+1); out[c].append(exp[c])
    return P,out
