import re,collections,sys
first={}; by=collections.defaultdict(list)
team=sys.argv[1]
for line in open(sys.argv[2],errors='replace'):
    m=re.match(r"round (\d+): bot (\d+) \(team "+team+r"\) points (\d+)",line)
    if not m: continue
    r,b,p=int(m.group(1)),int(m.group(2)),int(m.group(3))/1e6
    first.setdefault(b,r); age=r-first[b]
    by[min(age,5)].append(p)
for a in sorted(by):
    v=sorted(by[a]); print(a,len(v),'p50 %.1f p99 %.1f max %.1f >60: %d'%(v[len(v)//2],v[int(len(v)*.99)],v[-1],sum(x>60 for x in v)))
