import json,glob,random,collections,sys
G=[json.loads(l) for f in sorted(glob.glob('build/hinata/curves2/g_s*.jsonl')) for l in open(f)]
def band(e): return 'na' if e is None else '<1725' if e<1725 else '1725-1900' if e<=1900 else '>1900'
cells=collections.defaultdict(list)
for g in G:
    if g['pop']=='top10': continue
    us=g['us']; th='B' if us=='A' else 'A'; b=band(g['elo_'+th.lower()])
    for bb in {b,'all',('>=1725' if b in('1725-1900','>1900') else None)}:
        if bb: cells[(g['pop'],bb)].append(g)
print('pop,band,round,n_games,n_series,us,opp,diff,lo5,hi95,win_rate')
for (p,b),gs in sorted(cells.items()):
    for r in ('100','200','300'):
        rows=[(g['series'],g['c'+g['us']][r][3],g['c'+('B' if g['us']=='A' else 'A')][r][3],g['winner']==g['us']) for g in gs if r in g['c'+g['us']] and g['last_round']>=int(r)]
        if not rows: continue
        S=collections.defaultdict(list)
        for s,x,y,w in rows: S[s].append((x,y))
        keys=list(S); rng=random.Random(7); ds=[]
        for _ in range(1000):
            xs=[t for k in (rng.choice(keys) for _ in keys) for t in S[k]]
            ds.append(sum(x-y for x,y in xs)/len(xs))
        ds.sort(); n=len(rows)
        u=sum(x for _,x,_,_ in rows)/n; o=sum(y for _,_,y,_ in rows)/n
        print(f"{p},{b},{r},{n},{len(keys)},{u:.2f},{o:.2f},{u-o:+.2f},{ds[49]:+.2f},{ds[949]:+.2f},{sum(w for *_,w in rows)/n:.2f}")
