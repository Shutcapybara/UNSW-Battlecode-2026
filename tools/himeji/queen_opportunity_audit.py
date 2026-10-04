"""Audit KZ15 queen-only opportunity denominators and collision roles on the same96.
Round-start geometry is not attacker TurnStart visibility. No causal rescue estimate.
"""
import argparse,collections,hashlib,json,math,sys
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('repo','selection','out'):p.add_argument('--'+k,type=Path,required=True)
a=p.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
B=lambda L:math.ceil(L/4)+L-2
def bfs(nbr,s,cap):
    ds={s:0};todo=collections.deque([s])
    while todo:
        c=todo.popleft()
        if ds[c]>=cap:continue
        for n in nbr[c]:
            if n is not None and n not in ds:ds[n]=ds[c]+1;todo.append(n)
    return ds
def cheb(a,b,W,H):
    dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return max(min(dx,W-dx),min(dy,H-dy))
rows=[];games=[]
for m in json.loads(a.selection.read_text()):
    gid=str(m['game_id']);path=a.repo/'public_replays/corpus/replays'/f'{gid}.replay'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==m['sha256']
    root=F._reader(path).object(0,0);assert hashlib.sha256(root.text(0).encode()).hexdigest()==m['map_hash']
    assert root.num(0,'I')==2 and root.child(4).num(0,'B')&1
    g=F.decode(path);assert g['winner'].lower()==m['winner'];R=g['rounds'];nbr=g['nbr'];ours='A' if m['team_a']==7 else 'B'
    dd={(d['id'],d['round']):d for d in g['events']['deaths'] if d['cause']=='h2h'}
    qs={side:min(i for i,(t,b) in R[0].items() if t==side) for side in 'AB'}
    c=collections.Counter()
    for rnd,S in enumerate(R[:-1]):
        for side,q in qs.items():
            who='us' if side==ours else 'opp'
            if q not in S:continue
            c[who+'_alive']+=1;t=S[q][1][0];anyopp=False
            for j,(tm,eb) in S.items():
                if tm==side or cheb(t,eb[0],g['W'],g['H'])>3:continue
                Le=len(eb);cap=B(Le)+1;dist=bfs(nbr,eb[0],cap).get(t,99)
                if not 2<=dist<=cap:continue
                anyopp=True;d=dd.get((q,rnd));hit=bool(d and d['killer']==j)
                both=q in R[rnd+1] and j in R[rnd+1]
                chase=flee=None
                if not hit and both:
                    ne=R[rnd+1][j][1][0];nt=R[rnd+1][q][1][0]
                    chase=bfs(nbr,ne,cap).get(t,99)<dist
                    flee=bfs(nbr,eb[0],cap+1).get(nt,99)>dist
                rows.append(dict(game=gid,series_id=m['series_id'],map=m['map_name'],map_hash=m['map_hash'],ranked=m['ranked'],own_submission=root.text(1 if ours=='A' else 2),who=who,round=rnd,queen=q,enemy=j,enemy_length=Le,queen_length=len(S[q][1]),distance=dist,hit=hit,queen_mover=bool(hit and d['actor']==q),queen_partner=bool(hit and d['actor']!=q),nonhit_both_survive=bool(not hit and both),chase=chase,flee=flee,enemy_acts_first=j<q))
            c[who+'_fire']+=int(anyopp)
    games.append(dict(game=gid,ranked=m['ranked'],series_id=m['series_id'],counts=dict(c),sha256=m['sha256'],map_hash=m['map_hash']))
    if len(games)%12==0:print('decoded',len(games),flush=True)
a.out.mkdir(exist_ok=True,parents=True)
(a.out/'queen-opportunities.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
summary=[]
for who in ('us','opp'):
    rr=[r for r in rows if r['who']==who];nh=[r for r in rr if not r['hit']];eligible=[r for r in nh if r['nonhit_both_survive']]
    summary.append(dict(who=who,opportunities=len(rr),hits=sum(r['hit'] for r in rr),queen_mover_hits=sum(r['queen_mover'] for r in rr),queen_partner_hits=sum(r['queen_partner'] for r in rr),nonhits=len(nh),nonhit_both_survive=len(eligible),flee=sum(r['flee'] for r in eligible),chase=sum(r['chase'] for r in eligible),enemy_acts_first=sum(r['enemy_acts_first'] for r in rr),alive=sum(g['counts'].get(who+'_alive',0) for g in games),fire=sum(g['counts'].get(who+'_fire',0) for g in games)))
assert [(r['opportunities'],r['hits']) for r in summary]==[(264,25),(586,18)], 'Selection/measurement differs: do not silently call this the same KZ sample'
(a.out/'queen-opportunity-summary.json').write_text(json.dumps(dict(summary=summary,games=games,contract='Exact KZ15 queen subset reproduced; same96 consumed games, mixedmode; opportunity uses round-start S, ignoring bodies/food, B+1. Flee/chase only on nonhits with both alive next round; not causal conditioning.'),indent=2)+'\n');print(json.dumps(summary,indent=2))
