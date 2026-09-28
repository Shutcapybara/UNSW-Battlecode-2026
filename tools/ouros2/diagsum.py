import sys,collections
sys.path.insert(0,'/root/w/tools/ouros2')
import econ2
for p in sys.argv[2:]:
    d=econ2.analyse(p); team=sys.argv[1]
    logs={}
    for i,r,t in econ2.LOGS:
        for tok in t.split():
            if tok.startswith('DG:') and not tok.startswith('DG:tb'): logs[(i,r)]=tok
    c=collections.Counter()
    for tm,i,r,key in econ2.DLIST:
        if tm!=team: continue
        rs,o,via,ab,ph,L=key.split('|')
        c[(rs,o,via,logs.get((i,r),'-'))]+=1
    print(p.split('/')[-1], 'total deaths', sum(c.values()), d['teams'][team]['bed_eaten'], d['teams'][team]['corpse_eaten'])
    for k,v in sorted(c.items(),key=lambda z:-z[1])[:10]: print('  ',v,k)
