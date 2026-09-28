import sys,collections
sys.path.insert(0,'.')
from s2report import load, med, score, at
rows=load(sys.argv[1].split(','))
arms=sys.argv[2].split(',')
maps=sorted({k[1] for k in rows})
for m in maps:
    for c in arms:
        rs=[r for k,r in rows.items() if k[0]==c and k[1]==m]
        if not rs: continue
        me=[r['me'] for r in rs]
        print('%-15s %-28s n=%2d sc %.2f u50 %4.1f u100 %4.1f t100 %5.1f t250 %5.1f l400 %4.1f pearls %5.0f p100 %4.0f d100 %4.0f pd %4.0f ws1k %5.1f res_end %s' % (m,c[:28],len(rs),sum(map(score,rs))/len(rs),
          med([at(x,'50',0) for x in me]),med([at(x,'100',0) for x in me]),med([at(x,'100',1) for x in me]),med([at(x,'250',1) for x in me]),med([at(x,'400',2) for x in me]),
          med([x['pearls'] for x in me]),med([x.get('pearls_r100') for x in me]),med([x.get('deaths_r100') for x in me]),med([x['portal_deaths'] for x in me]),
          1000*sum(x['deaths'].get('wall',0)+x['deaths'].get('self',0) for x in me)/sum(x['turns'] for x in me),
          collections.Counter((r['res'],'elim' if r['rounds']<500 else 'r500') for r in rs).most_common()))
