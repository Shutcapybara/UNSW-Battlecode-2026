"""Queen turn history from replay events, without rebuilding every dragon's view.

Uses the canonical replay reader/map parser; event transitions mirror rebuild.walk.
All births/deaths update team counts, including deaths on another dragon's turn.
"""
import collections
import struct
from tools.learn.rebuild import reader,Map

def recent_queens(data):
    r=reader(data);root=r.object(0,0);m=Map(root.text(0))
    teams={i:t for i,(t,b) in enumerate(m.dragons)}
    live=set(teams);population=collections.Counter(teams.values())
    bodies={i:collections.deque(b) for i,(t,b) in enumerate(m.dragons) if i in (0,1)}
    recent={0:[],1:[]};rnd=-1;actor=None;current=None
    def flush():
        nonlocal current
        if current is not None:
            recent[actor].append(current);recent[actor]=recent[actor][-5:]
        current=None
    def point(o):return (o.num(),o.num(4))
    for event in root.items(3):
        kind=event.num(0,'H');o=event.child(0)
        if kind==0:
            flush();rnd=o.num();actor=None
        elif kind==1:
            flush();actor=o.num()
            if actor in recent:
                body=bodies[actor]
                current=dict(round=rnd,head=body[0],length=len(body),units=population[teams[actor]],action=None)
        elif kind==4 and current is not None and actor==o.num():
            if o.has(0):
                a=o.child(0);ak=a.num(0,'H')
                if ak==0:
                    segment,at,word=r.pointer(a.s,a.a+a.dw);count=word>>35
                    steps=struct.unpack_from('<'+'H'*count,r.segments[segment],at*8) if count else ()
                    current['action']=('move',''.join('NESW'[v] for v in steps))
                elif ak==1:current['action']=('split',a.num(4))
                elif ak==2:current['action']=('suicide',None)
                else:current['action']=(f'kind{ak}',None)
        elif kind==9:
            ident=o.num()
            if ident in bodies:
                body=bodies[ident];head=point(o.child(0));tail=point(o.child(1))
                if body[0]!=head:body.appendleft(head)
                while len(body)>1 and body[-1]!=tail:body.pop()
        elif kind==10:
            parent,child=o.num(),o.num(4);assert child not in live
            teams[child]=teams[parent];live.add(child);population[teams[child]]+=1
            if parent in bodies:bodies[parent]=collections.deque(point(q) for q in o.items(0))
            if child in (0,1):bodies[child]=collections.deque(point(q) for q in o.items(1))
        elif kind==11:
            ident=o.num()
            if ident in live:live.remove(ident);population[teams[ident]]-=1
    flush()
    return recent
