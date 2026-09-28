import sys,glob,collections
sys.path.insert(0,'/root/w/tools/ouroboros')
import replaystats as R
def supply(path, team, upto=100):
    rep=R.load(path); rnd=0; tm={}; nid=0; actor=-1; indeath=False
    for line in rep.map.splitlines():
        if line.startswith('DRAGON '): tm[nid]='AB'[int(line.split()[1])]; nid+=1
    pearl={}; c=collections.Counter()
    for ev in rep.events:
        w=ev.which()
        if w=='roundStart':
            rnd=ev.roundStart.round
            if rnd>=upto: break
        elif w=='turnStart': actor=ev.turnStart.id; indeath=False
        elif w=='dragonDeath': indeath=True
        elif w=='dragonSplit':
            s=ev.dragonSplit; tm[s.childId]='A' if str(s.team)=='a' else 'B'
        elif w=='tileChange':
            t=ev.tileChange; cell=(t.tile.x,t.tile.y)
            if t.hasPearl:
                k='corpse' if indeath else 'bed'; pearl[cell]=k; c['spawn_'+k]+=1
            else:
                k=pearl.pop(cell,None)
                if k: c[('us' if tm.get(actor)==team else 'them')+'_'+k]+=1
    for k in pearl.values(): c['left_'+k]+=1
    return c
agg=collections.defaultdict(collections.Counter); n=collections.Counter()
for p in sorted(glob.glob(sys.argv[1]+'/*.replay')):
    m=p.split('/')[-1].split('_s1_')[0]; side=p[-8]
    agg[m].update(supply(p, side)); n[m]+=1
for m in sorted(agg):
    a=agg[m]; k=n[m]
    print('%-16s bed spawned %5.1f  us %5.1f them %5.1f left@r100 %5.1f | corpse us %5.1f them %5.1f' % (m, a['spawn_bed']/k, a['us_bed']/k, a['them_bed']/k, a['left_bed']/k, a['us_corpse']/k, a['them_corpse']/k))
