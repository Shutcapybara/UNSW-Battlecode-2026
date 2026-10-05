"""per-game pearl/death events for the bed-variant maps (kageyama, D-072 §E). resumable; part i of n; time budget"""
import sys, json, gzip, os, time
sys.path.insert(0, 'tools/learn')
import rebuild
MAPS={'Devil','Queen Of Spades','Slithery Fight','Schooltime','Prisoners Dilemma'}
OUT='build/learn/kageyama/beds/ev'
def events(data):
    r=rebuild.reader(data); root=r.object(0,0); txt=root.text(0)
    rnd=-1; ev=[]; deaths=[]
    for e in root.items(3):
        k=e.num(0,'H'); o=e.child(0)
        if k==0: rnd=o.num()
        elif k==3: ev.append((rnd,o.child(0).num(),o.child(0).num(4),o.num(0,'B')&1))
        elif k==11: deaths.append(rnd)
    return txt, ev, deaths, rnd
i,n,budget=int(sys.argv[1]),int(sys.argv[2]),float(sys.argv[3])
t0=time.time()
games=[]
for l in open('public_replays/corpus/index.jsonl'):
    d=json.loads(l)
    if (d.get('started_at') or '')<'2026-10-02T03:49' or d.get('status')!='completed' or d['map_name'] not in MAPS: continue
    if d['game_id']%n!=i: continue
    games.append(d)
fn=f'{OUT}/part{i}.jsonl'
done=set()
if os.path.exists(fn):
    for l in open(fn):
        try: done.add(json.loads(l)['game'])
        except Exception: pass
f=open(fn,'a'); k=0
for d in games:
    if d['game_id'] in done: continue
    if time.time()-t0>budget: break
    p=f"public_replays/corpus/replays/{d['game_id']}.replay"
    if not os.path.exists(p): continue
    try: txt,ev,de,last=events(open(p,'rb').read())
    except Exception as e: 
        f.write(json.dumps(dict(game=d['game_id'],err=str(e)[:100]))+'\n'); continue
    f.write(json.dumps(dict(game=d['game_id'],map=d['map_name'],hash=d['map_hash'][:6],seed=d['seed'],ranked=d['ranked'],last=last,deaths=de,ev=ev,txt=txt if d['game_id']%50==0 else None))+'\n'); k+=1
f.close()
print(i, 'new', k, 'done', len(done)+k, 'of', len(games))
