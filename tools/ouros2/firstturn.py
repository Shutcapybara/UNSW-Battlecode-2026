import re,sys,collections
def ft(f,team):
    first={}; F=[]; L=[]; tle=collections.Counter()
    for line in open(f,errors='replace'):
        m=re.match(r"round (\d+): bot (\d+) \(team ([AB])\) (points (\d+)|exceeded)",line)
        if not m or m.group(3)!=team: continue
        r,b=int(m.group(1)),int(m.group(2))
        if b not in first: first[b]=r
        isf=first[b]==r
        if m.group(4)=='exceeded': tle['first' if isf else 'later']+=1; continue
        (F if isf else L).append(int(m.group(5))/1e6)
    F.sort(); L.sort()
    q=lambda x,p: round(x[min(len(x)-1,int(len(x)*p))],1) if x else None
    return dict(rounds=max(first.values()) if first else 0, first_n=len(F), first_p50=q(F,.5), first_p90=q(F,.9), first_max=q(F,1), later_n=len(L), later_p50=q(L,.5), later_p99=q(L,.99), later_max=q(L,1), tle=dict(tle))
for f in sys.argv[2:]:
    print(f, ft(f, sys.argv[1]))
