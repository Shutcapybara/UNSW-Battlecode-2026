"""End-to-end parity of the slot bot (kageyama-01-p1-slot built with a debug writer to /tmp/p1dbg/<id>.txt): the
bot's in-play P(F,R,B,L) against the Python encoder + LightGBM on the replay of the same game.
    python slot_e2e_parity.py REPLAY TEAM [MODEL.txt]"""
import sys, collections, numpy as np, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rebuild, block as B, encode as E, labels as LB, lightgbm as lgb
data=open(sys.argv[1],'rb').read(); team=sys.argv[2]
turns=collections.defaultdict(list)
rebuild.walk(data, lambda i,sp,txt,ctx: turns[i].append((sp,txt,ctx)))
X=[]; keys=[]
for did,seq in turns.items():
    sp=seq[0][0]
    if sp['team']!=team: continue
    enc=E.Encoder(B.Spawn(sp['id'],sp['team'],sp['W'],sp['H'],sp['unit_limit']))
    for k,(sp_,txt,ctx) in enumerate(seq):
        b=B.parse_block(txt); X.append(enc.observe(b)); keys.append((did,k,ctx['round']))
        y=LB.label(ctx,b,did,sp['team'])
        if y['y_kind']==0: enc.act('move',list(y['y_seq']))
        elif y['y_kind']==1: enc.act('split',child=y['y_child'],rnd=ctx['round'])
        elif y['y_kind']==2: enc.act('invalid')
        else: enc.act('none')
P=lgb.Booster(model_file=sys.argv[3] if len(sys.argv) > 3 else 'build/hinata/r2/placeholder/A3-400-f0.txt').predict(np.asarray(X,dtype=np.float32))
C={}
for f in os.listdir('/tmp/p1dbg'):
    C[int(f[:-4])]=[list(map(float,l.split())) for l in open('/tmp/p1dbg/'+f)]
n=bad=miss=0; mx=0; am=0
for (did,k,r),p in zip(keys,P):
    if did not in C or k>=len(C[did]): miss+=1; continue
    c=C[did][k]; assert int(c[0])==r,(did,k,r,c[0])
    d=np.abs(np.array(c[1:])-p).max(); mx=max(mx,d); n+=1; bad+=d>1e-6; am+=np.argmax(c[1:])==np.argmax(p)
print('team',team,'turns',len(keys),'compared',n,'missing',miss,'max|dp|',mx,'>1e-6',bad,'argmax agree',am,'/',n, 'dbg files',len(C))
