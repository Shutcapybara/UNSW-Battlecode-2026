import sys, collections
sys.path.insert(0,'/root/w/tools/ouroboros')
import replaystats as R
def early(path, team, upto=40):
    rep=R.load(path); rnd=0; tm={}; out=[]; nid=0
    for line in rep.map.splitlines():
        if line.startswith('DRAGON '):
            tm[nid]='AB'[int(line.split()[1])]; nid+=1
    for ev in rep.events:
        w=ev.which()
        if w=='roundStart':
            rnd=ev.roundStart.round
            if rnd>upto: break
        elif w=='dragonSplit':
            s=ev.dragonSplit; tm[s.childId]='A' if str(s.team)=='a' else 'B'
            if tm[s.childId]==team: out.append((rnd,'split',s.parentId,len(s.parentBody),len(s.childBody)))
        elif w=='tileChange' and not ev.tileChange.hasPearl: pass
        elif w=='dragonDeath':
            d=ev.dragonDeath
            if tm.get(d.id)==team: out.append((rnd,'death',d.id,str(d.reason)))
        elif w=='dragonLog':
            if tm.get(ev.dragonLog.id)==team and 'DG:' in ev.dragonLog.text: out.append((rnd,'log',ev.dragonLog.id,ev.dragonLog.text[:60]))
    return out
for p in sys.argv[2:]:
    print(p.split('/')[-1]); [print('  ',x) for x in early(p, sys.argv[1])]
