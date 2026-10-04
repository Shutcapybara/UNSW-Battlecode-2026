"""Verify the peer's24 distance-selected head collisions against actions and TurnStart states.
Read-only replay inspection, not a counterfactual avoidance test.
"""
import argparse,collections,hashlib,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--index',type=Path,required=True);p.add_argument('--selected',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
idx={x['game_id']:x for x in map(json.loads,a.index.read_text().splitlines())};selected=json.loads(a.selected.read_text());groups=collections.defaultdict(list)
for r in selected:groups[r['gid']].append(r)
rows=[]
def distance(nbr,u,v):
    seen={u};todo=collections.deque([(u,0)])
    while todo:
        x,d=todo.popleft()
        if x==v:return d
        for y in nbr[x]:
            if y is not None and y not in seen:seen.add(y);todo.append((y,d+1))
    return None
for gid,cases in groups.items():
    meta=idx[gid];path=a.repo/'public_replays/corpus/replays'/f'{gid}.replay';assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256'];g=F.decode(path);root=F._reader(path).object(0,0);assert hashlib.sha256(root.text(0).encode()).hexdigest()==meta['map_hash'];assert g['winner'].lower()==meta['winner'];ours='A' if meta['team_a']==7 else 'B'
    for peer in cases:
        side=ours if peer['who']=='us' else ('B' if ours=='A' else 'A');q=min(i for i,(t,b) in g['rounds'][0].items() if t==side);death=next(d for d in g['events']['deaths'] if d['id']==q);r=death['round'];killer=death['killer'];assert r==peer['r'] and death['cause']=='h2h' and death['actor']==killer
        action=next(x for x in g['events']['actions'] if x['round']==r and x['id']==killer)
        terrain=F.terrain(root.text(0))[0];bodies={i:collections.deque(b) for i,(tm,b) in enumerate(terrain['dragons'])};live=set(bodies);rnd=-1;actor=None;start=None;head_updates=[];q_last_turn=None
        point=lambda o:(o.num(),o.num(4))
        for e in root.items(3):
            kind=e.num(0,'H');o=e.child(0);i=o.num()
            if kind==0:rnd=i
            elif kind==1:
                actor=i
                if i==q:q_last_turn=dict(round=rnd,head=list(bodies[q][0]),length=len(bodies[q]))
                if rnd==r and i==killer:
                    start=dict(killer_head=list(bodies[killer][0]),killer_length=len(bodies[killer]),queen_head=list(bodies[q][0]),queen_length=len(bodies[q]),distance=distance(g['nbr'],bodies[killer][0],bodies[q][0]))
            elif kind==9:
                head,tail=point(o.child(0)),point(o.child(1));b=bodies[i]
                if b[0]!=head:
                    b.appendleft(head)
                    if rnd==r and i==killer:head_updates.append(list(head))
                while len(b)>1 and b[-1]!=tail:b.pop()
            elif kind==10:
                child=o.num(4);bodies[i]=collections.deque(point(x) for x in o.items(0));bodies[child]=collections.deque(point(x) for x in o.items(1));live.add(child)
            elif kind==11:
                if rnd==r and i==q:break
                live.discard(i)
        assert start is not None
        rows.append(dict(game=gid,series=meta['series_id'],ranked=meta['ranked'],map=g['map'],map_hash=meta['map_hash'],replay_sha256=meta['sha256'],own_submission=g['bot'+ours],opponent_submission=g['bot'+('B' if ours=='A' else 'A')],peer=peer,queen=q,killer=killer,death=death,killer_action=action,killer_turn_start=start,killer_head_updates_before_queen_death=head_updates,queen_last_turn_start=q_last_turn))
    print(gid,'complete',flush=True)
a.out.write_text(json.dumps(dict(rows=rows,scope='24 selected collision cases from the same consumed96 sample; command length and event states only. No causal avoidance, policy-visibility or enemy-intent claim.'),indent=2)+'\n')
