import json,sys,collections
import econ2
for p in sys.argv[2:]:
    d=econ2.analyse(p); t=sys.argv[1]
    x=d['teams'][t]; dd=x.pop('deaths'); x.pop('bed_latency_r100',None)
    print(p.split('/')[-1], d['spawned'], x)
    agg=collections.Counter()
    for k,v in dd.items():
        r,o,via,ab,ph,L=k.split('|'); agg[(r,o,via)]+=v
    print('  ',sorted(agg.items(),key=lambda z:-z[1])[:12])
    agg=collections.Counter()
    for k,v in dd.items():
        r,o,via,ab,ph,L=k.split('|'); agg[(ab,ph)]+=v
    print('  ',dict(agg))
