#!/usr/bin/env python3
"""Read-only replay review. Uses the existing dependency-free v0/1/2 decoder.

Usage: python3 tools/public_replay_review.py [replay ...] --out DIRECTORY
Round curves are start-of-round snapshots; pearl sources track the most recent
spawn at a cell (overwrites are ambiguous). No opponent identity is inferred.
"""
import argparse, collections, concurrent.futures, hashlib, json, struct, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent.parent / 'hub' / 'vendor'               # frozen helper copies live beside this file (byte-identical to tools/leviathan and tools/ouroboros)
sys.path.insert(0, str(_HERE / 'leviathan'))
from replay import Reader
sys.path.insert(0, str(_HERE / 'ouroboros'))
from mapview import load_map

def analyse(path):
    r=Reader(path); root=r.object(0,0); version=root.num(0,'I')
    if version not in (0,1,2): raise ValueError(f'Unsupported version {version}')
    maptext=root.text(0); m=load_map(maptext); W,H=m['W'],m['H']
    edges={}; ports=collections.defaultdict(list)
    for line in maptext.splitlines():
        p=line.split()
        if p and p[0]=='EDGE':
            idx,k,pid=map(int,p[1:]); col,row=idx%(W+1),idx//(W+1)
            if col>=W or row>=2*H:continue
            key=(row%2,col,row//2);edges[key]=(k,pid)
            if k==2:ports[pid].append(key)
    def dest(c,d):
        x,y=c; key=((0,x,y),(1,(x+1)%W,y),(0,x,(y+1)%H),(1,x,y))[d]
        k,pid=edges.get(key,(0,-1))
        if k==1:return None
        if k==2:
            other=next(e for e in ports[pid] if e!=key); ori,x,y=other
            return ((x if ori==0 or d==1 else x-1)%W,(y if ori==1 or d==2 else y-1)%H)
        return ((x+(0,1,0,-1)[d])%W,(y+(-1,0,1,0)[d])%H)
    teams={i:t for i,(t,b) in enumerate(m['dragons'])};body={i:collections.deque(b) for i,(t,b) in enumerate(m['dragons'])};live=set(body)
    born={i:0 for i in live}; initial=set(live); visited={t:set() for t in 'AB'}
    st={t:collections.Counter() for t in 'AB'}; split_sizes={t:collections.Counter() for t in 'AB'};actions={t:collections.Counter() for t in 'AB'}
    curve=[]; deaths=[]; splits=[]; logs=collections.Counter(); indicators=collections.Counter(); pearl_origin={}; pearl_age={}; first_crown={}; transfers=[]; action_kind=None; bed_resets=collections.Counter()
    acts={t:collections.Counter() for t in 'AB'};rnd=-1;actor=None;steps=[];update_count=0;drop_team=None;drop_id=None;pair=None
    def point(o):return (o.num(),o.num(4))
    def sample(rr):
        row={'round':rr}
        for t in 'AB':
            ids=sorted((i for i in live if teams[i]==t),key=lambda i:(-len(body[i]),i)); lens=[len(body[i]) for i in ids]
            row[t]=dict(units=len(ids),total=sum(lens),longest=lens[0] if lens else 0,leader=ids[0] if ids else None,top5=lens[:5],**st[t])
            st[t]['peak_units']=max(st[t]['peak_units'],len(ids))
            for threshold in (10,20,30,40,50):
                if lens and lens[0]>=threshold:first_crown.setdefault(t+str(threshold),rr)
        curve.append(row)
    for e in root.items(3):
        kind=e.num(0,'H');o=e.child(0);i=o.num()
        if kind not in (3,11):drop_team=None;drop_id=None
        if kind==0:
            rnd=i;sample(rnd)
        elif kind==1:actor=i;steps=[];update_count=0;pair=None;action_kind=None
        elif kind==2 and rnd>=0:
            c=point(o.child(0));bed_resets['scheduled']+=1
            if c not in pearl_origin:
                owner=next((j for j in live if c in body[j]),None)
                if owner is not None:bed_resets['blocked_by_'+teams[owner]]+=1
                else:bed_resets['unexplained_empty']+=1
            elif pearl_origin[c][0]=='bed' and pearl_age.get(c)==rnd:bed_resets['spawned']+=1
            else:bed_resets['already_pearl']+=1
        elif kind==3:
            c=point(o.child(0))
            if o.num(0,'B'):
                pearl_origin[c]=(drop_team,drop_id) if drop_team else ('bed',None);pearl_age[c]=rnd
            elif actor in live:
                t=teams[actor];st[t]['pearls']+=1
                origin,donor=pearl_origin.pop(c,('unknown',None));age=rnd-pearl_age.pop(c,rnd)
                label='ally_corpse' if origin==t else ('enemy_corpse' if origin in 'AB' else origin)
                st[t]['pearls_'+label]+=1
                if age<=1:st[t]['fresh_'+label]+=1
                if donor is not None:transfers.append(dict(round=rnd,collector=actor,team=t,donor=donor,donor_team=origin,age=age,at=c))
        elif kind==4:
            t=teams[i];st[t]['turns']+=1
            if o.num(4,'B')&1:st[t]['tle']+=1
            if o.has(1):
                usage=o.child(1);st[t]['cpu_max']=max(st[t]['cpu_max'],usage.num(0,'Q'));st[t]['cpu_recorded']+=1
            if o.has(0):
                a=o.child(0);ak=a.num(0,'H');action_kind=('move','split','suicide')[ak]
                if ak==0:
                    s,at,word=r.pointer(a.s,a.a+a.dw);count=word>>35
                    steps=list(struct.unpack_from('<'+'H'*count,r.segments[s],at*8)) if count else []
                    actions[t]['move'+str(count)]+=1
                    if count>1:st[t]['sprints']+=1
                elif ak==1:actions[t]['split']+=1
                else:actions[t]['suicide']+=1;st[t]['suicides']+=1
        elif kind in (5,6):
            txt=o.text(0)
            if txt.startswith('ACT:') and i in teams:
                tag=txt.split()[0];acts[teams[i]][tag]+=1
                if rnd<=100:acts[teams[i]][tag+'@100']+=1
            if len(logs)<100 or txt[:100] in logs:logs[txt[:100]]+=1
        elif kind==7:
            txt=o.text(0)
            if len(indicators)<25:indicators[txt[:120]]+=1
        elif kind==9:
            b=body[i];head,tail=point(o.child(0)),point(o.child(1))
            if b[0]!=head:
                before=b[0];b.appendleft(head)
                if i==actor:
                    if update_count:st[teams[i]]['extra_steps']+=1
                    if update_count<len(steps):
                        d=steps[update_count];normal=((before[0]+(0,1,0,-1)[d])%W,(before[1]+(-1,0,1,0)[d])%H)
                        if head!=normal:st[teams[i]]['portal_steps']+=1
                    update_count+=1
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail,(path,rnd,i,tail)
            visited[teams[i]].add(head)
        elif kind==10:
            child=o.num(4);t=teams[i];oldlen=len(body[i]);teams[child]=t;born[child]=rnd;live.add(child)
            body[i]=collections.deque(point(p) for p in o.items(0));body[child]=collections.deque(point(p) for p in o.items(1))
            assert oldlen==len(body[i])+len(body[child])
            st[t]['splits']+=1;split_sizes[t][len(body[child])]+=1
            splits.append(dict(round=rnd,team=t,parent=i,child=child,before=oldlen,parent_len=len(body[i]),child_len=len(body[child])))
        elif kind==11:
            t=teams[i];cause=('wall','self','body','h2h','invalid')[o.num(4,'H')];ln=len(body[i]);st[t]['deaths']+=1;st[t]['death_'+cause]+=1;st[t]['length_lost']+=ln
            age=rnd-born[i]
            if i not in initial and age<=10:st[t]['newborn_deaths_10']+=1
            record=dict(round=rnd,id=i,team=t,cause=cause,length=ln,actor=actor,age=age,head=body[i][0],step=update_count,move=steps,action=action_kind)
            if cause=='h2h':
                if i!=actor:
                    pair=(i,t,ln);record['attacker_length']=len(body[actor]);record['attacker_team']=teams[actor]
                else:
                    st[t]['initiated_h2h']+=1
                    if pair:
                        record['victim_id'],record['victim_team'],record['victim_length']=pair
                        st[t]['friendly_h2h' if pair[1]==t else 'enemy_h2h']+=1
            if i==actor and cause!='h2h':
                occ={c:j for j in live for c in body[j]};neigh=[dest(body[i][0],d) for d in range(4)]
                record['free_exits']=sum(c is not None and c not in occ for c in neigh)
                if cause=='body' and update_count<len(steps):
                    hit=occ.get(dest(body[i][0],steps[update_count]));record['hit_id']=hit;record['hit_team']=teams.get(hit)
                    st[t]['body_'+('ally' if teams.get(hit)==t else 'enemy' if hit is not None else 'unknown')]+=1
            deaths.append(record);live.remove(i);drop_team=t;drop_id=i
        elif kind==12:
            if i in teams:st[teams[i]]['sonar']+=1
    sample(rnd+1);res=root.child(4);final={}
    for n,t in enumerate('AB'):
        q=res.child(n);final[t]=dict(units=q.num(),longest=q.num(4),total=q.num(8))
        assert all(curve[-1][t][k]==v for k,v in final[t].items()),(path,t,curve[-1][t],final[t])
        st[t]['visited_cells']=len(visited[t])
    return dict(acts=acts,file=str(path),id=Path(path).stem,battle=Path(path).parent.name,version=version,botA=root.text(1),botB=root.text(2),map=next((l[9:] for l in maptext.splitlines() if l.startswith('MAP_NAME ')),'unknown'),map_hash=hashlib.sha256(maptext.encode()).hexdigest(),width=W,height=H,beds=sum(v[1]>0 for v in m['tiles'].values()),rounds=rnd+1,winner='AB'[res.num(6,'H')] if res.num(4,'H')==1 else 'draw',reason=('elimination','roundLimit')[res.num(2,'H')],final=final,bed_resets=bed_resets,stats=st,actions=actions,split_sizes=split_sizes,first_length=first_crown,curve=curve,deaths=deaths,splits=splits,transfers=transfers,log_samples=dict(logs),indicator_samples=dict(indicators))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('files',nargs='*');ap.add_argument('--out',default='build/public-replay-review');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    files=a.files or sorted(map(str,Path('public_replays').glob('*/*.replay')))
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.jobs) as pool:
        futures={pool.submit(analyse,p):p for p in files if not (out/(Path(p).stem+'.json')).exists()}
        for f in concurrent.futures.as_completed(futures):
            result=f.result();(out/(result['id']+'.json')).write_text(json.dumps(result,separators=(',',':'))+'\n');print(result['id'],result['map'],result['rounds'],result['winner'],flush=True)
    print('Complete',len(files))
if __name__=='__main__':main()
