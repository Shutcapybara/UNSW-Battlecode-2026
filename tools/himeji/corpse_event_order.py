"""Audit round-only corpse fate matching against FRAME event provenance on fresh games.
Reads corpus only. Fully followed births150..R-50, age<=50; no store writes.
"""
import argparse, bisect, collections, hashlib, json, sys
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('repo','metadata','out'): p.add_argument('--'+k, type=Path, required=True)
a=p.parse_args();sys.path.insert(0,str(a.repo))
from tools.analysis.features import frame as F
rows=[]
for m in json.loads(a.metadata.read_text()):
    path=a.repo/'public_replays/corpus/replays'/f"{m['game_id']}.replay"
    assert hashlib.sha256(path.read_bytes()).hexdigest()==m['sha256']
    g=F.decode(path);root=F._reader(path).object(0,0)
    assert hashlib.sha256(root.text(0).encode()).hexdigest()==m['map_hash']
    assert g['winner'].lower()==m['winner']
    sp=[s for s in g['events']['spawns'] if s['origin'] in ('A','B') and 150<=s['round']<=g['last_round']-50]
    key=lambda s:(s['round'],tuple(s['cell']),s['donor'])
    assert len({key(s) for s in sp})==len(sp)
    bycell=collections.defaultdict(list); actual={}
    for e in g['events']['eats']:
        bycell[tuple(e['cell'])].append((e['round'],e['team']))
        if e['origin'] in ('ally_corpse','enemy_corpse'):
            k=(e['round']-e['age'],tuple(e['cell']),e['donor'])
            assert k not in actual
            actual[k]=e
    for lst in bycell.values():lst.sort()
    totals={side:collections.Counter() for side in 'AB'}; examples=[]; changed=[]
    for s in sp:
        side=s['origin'];lst=bycell[tuple(s['cell'])];j=bisect.bisect_left(lst,(s['round'],''))
        old='not_by50'
        if j<len(lst) and lst[j][0]<=s['round']+50:old='ally' if lst[j][1]==side else 'enemy'
        e=actual.get(key(s));new='not_by50'
        if e and e['age']<=50:new='ally' if e['team']==side else 'enemy'
        c=totals[side];c['born']+=1;c['round_only_'+old]+=1;c['event_'+new]+=1
        if old!=new:
            c['mismatches']+=1
            changed.append(dict(birth=s,round_only=old,event_fate=new,first_round_match=lst[j] if j<len(lst) else None,actual_eat=e))
    for side,c in totals.items():
        assert sum(c['event_'+k] for k in ('ally','enemy','not_by50'))==c['born']
    trace=[]; cells={(x['birth']['round'],tuple(x['birth']['cell'])) for x in changed}
    rnd=-1;actor=None
    for pos,ev in enumerate(root.items(3)):
        kind=ev.num(0,'H');o=ev.child(0)
        if kind==0:rnd=o.num()
        elif kind==1:actor=o.num()
        elif kind==3:
            cell=(o.child(0).num(),o.child(0).num(4))
            if (rnd,cell) in cells:trace.append(dict(event=pos,round=rnd,actor=actor,cell=cell,spawn=bool(o.num(0,'B')&1)))
    rows.append(dict(game=m['game_id'],series=m['series_id'],ranked=m['ranked'],map=g['map'],map_hash=m['map_hash'],sha256=m['sha256'],own_side='A' if m['team_a']==7 else 'B',bots=[g['botA'],g['botB']],R=g['last_round'],winner=g['winner'],counts={s:dict(c) for s,c in totals.items()},mismatches=changed,raw_same_round_trace=trace))
    print(m['game_id'],len(sp),len(changed),flush=True)
a.out.write_text(json.dumps(dict(rows=rows,contract='Round-only first eat sorted (round,team) versus donor+birth-round+cell event identity, fully followed50round cohort. Residual not_by50 is not a physical remaining-food claim. Fresh audit population, not peer349 recut.'),indent=2)+'\n')
