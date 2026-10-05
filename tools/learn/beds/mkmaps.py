import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fit import *
import pickle, json, gzip
G=load()
def nontile(t): return [l for l in t.splitlines() if not l.startswith('TILE ')]
def build_text(name, beds, newname, hashes):
    m=TPL[name]; tt=open([f for f in glob.glob('maps/live/*.map') if rebuild.Map(open(f).read()).name==name][0]).read()
    # a server text of this variant: prefer one whose non-TILE lines equal the template's (same seats)
    cands=[d['txt'] for d in G if d['map']==name and d.get('txt') and d['hash'] in hashes]
    pick=None
    for t in cands:
        if nontile(t)==nontile(tt): pick=t; break
    src = pick or (cands[0] if cands else tt)
    out=[]
    for l in src.splitlines():
        p=l.split()
        if p and p[0]=='TILE':
            c=(int(p[1]),int(p[2])); lo,hi=beds.get(c,(0,0)); l=f'TILE {c[0]} {c[1]} {lo} {hi}'
        elif p and p[0]=='MAP_NAME': l='MAP_NAME '+newname
        out.append(l)
    return '\n'.join(out)+'\n', pick is not None, len(cands)
V={}
V['devil_b']=('Devil', pickle.load(open('devilB.pkl','rb')), 'Devil B', ('cb4efb','da98e1'))
V['queen_of_spades_b']=('Queen Of Spades', pickle.load(open('qosB.pkl2','rb'))[0], 'Queen Of Spades B', ('3ffe4a','ea5704'))
V['schooltime_open4']=('Schooltime', pickle.load(open('school4.pkl','rb')), 'Schooltime Open4', ('23fa2e','85635a'))
V['dilemma_10']=('Prisoners Dilemma', pickle.load(open('dil10_B.pkl','rb')), 'Prisoners Dilemma 10', ('a9a230','aebe7f'))
for k,(name,beds,newname,hs) in []:
    t,same,nc=build_text(name,beds,newname,hs)
    open(f'live_var/{k}.map','w').write(t)
    json.dump({f'{x},{y}':v for (x,y),v in beds.items()}, open(f'live_var/{k}.beds.json','w'))
    print(k, 'template seats' if same else 'server seats', nc, len(beds), collections.Counter(beds.values()).most_common(6))
t,same,nc=build_text('Slithery Fight', pickle.load(open('sli7.pkl','rb')), 'Slithery Fight B', ('2b2eaa','c8e8fa'))
open('live_var/slithery_fight_b.map','w').write(t); print('slithery', same, nc)
