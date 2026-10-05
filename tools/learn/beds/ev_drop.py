"""pearl events with death-drop flags (body cells of dragons dying that round) for one map; kageyama D-072 §E"""
import sys, json, os, time, collections
sys.path.insert(0, 'tools/learn')
import rebuild
def events(data):
    r=rebuild.reader(data); root=r.object(0,0); txt=root.text(0); m=rebuild.Map(txt)
    B={i:collections.deque(b) for i,(t,b) in enumerate(m.dragons)}
    pt=lambda o:(o.num(),o.num(4))
    rnd=-1; ev=[]; dropc=collections.defaultdict(set)
    for e in root.items(3):
        k=e.num(0,'H'); o=e.child(0)
        if k==0: rnd=o.num()
        elif k==9:
            i=o.num(); d=B[i]; head,tail=pt(o.child(0)),pt(o.child(1))
            if d[0]!=head: d.appendleft(head)
            while len(d)>1 and d[-1]!=tail: d.pop()
        elif k==10:
            pid,cid=o.num(),o.num(4)
            B[pid]=collections.deque(pt(q) for q in o.items(0)); B[cid]=collections.deque(pt(q) for q in o.items(1))
        elif k==11:
            i=o.num(); dropc[rnd]|=set(B.get(i,()))
        elif k==3:
            c=pt(o.child(0)); ev.append((rnd,c[0],c[1],o.num(0,'B')&1))
    out=[]
    for rr,x,y,v in ev:
        drop=int(v and ((x,y) in dropc.get(rr,()) or (x,y) in dropc.get(rr-1,())))
        out.append((rr,x,y,v,drop))
    return out, rnd
mapname=sys.argv[1]; i,n,budget,cap=int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]),int(sys.argv[5])
t0=time.time(); OUT='build/learn/kageyama/beds/evd'; os.makedirs(OUT,exist_ok=True)
games=[]
for l in open('public_replays/corpus/index.jsonl'):
    d=json.loads(l)
    if (d.get('started_at') or '')<'2026-10-02T03:49' or d.get('status')!='completed' or d['map_name']!=mapname: continue
    if d['game_id']%n==i: games.append(d)
games=games[:cap]
fn=f"{OUT}/{mapname.replace(' ','_')}_{i}.jsonl"; done=set()
if os.path.exists(fn): done={json.loads(l)['game'] for l in open(fn)}
f=open(fn,'a'); k=0
for d in games:
    if d['game_id'] in done: continue
    if time.time()-t0>budget: break
    try: ev,last=events(open(f"public_replays/corpus/replays/{d['game_id']}.replay",'rb').read())
    except Exception as e: f.write(json.dumps(dict(game=d['game_id'],err=str(e)[:100]))+'\n'); continue
    f.write(json.dumps(dict(game=d['game_id'],map=mapname,hash=d['map_hash'][:6],seed=d['seed'],ranked=d['ranked'],last=last,ev=ev))+'\n'); k+=1
print(i,'new',k,'done',len(done)+k,'of',len(games))
