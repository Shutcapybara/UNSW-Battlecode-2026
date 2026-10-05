import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fit import *
import pickle, sys
part,n=int(sys.argv[1]),int(sys.argv[2])
VB={'Devil':pickle.load(open('devilB.pkl','rb')),'Queen Of Spades':pickle.load(open('qosB.pkl2','rb'))[0],
    'Schooltime':pickle.load(open('school4.pkl','rb')),'Prisoners Dilemma':pickle.load(open('dil10_B.pkl','rb')),
    'Slithery Fight':pickle.load(open('sli7.pkl','rb'))}
VN={'Devil':'devil_b','Queen Of Spades':'queen_of_spades_b','Schooltime':'schooltime_open4','Prisoners Dilemma':'dilemma_10','Slithery Fight':'slithery_fight_b'}
out=open(f'cls.{part}.jsonl','w')
for i,l in enumerate(gzip.open('build/learn/kageyama/beds/ev_all.jsonl.gz','rt')):
    if i%n!=part: continue
    d=json.loads(l)
    if 'ev' not in d: out.write(json.dumps(dict(game=d['game'],err=d.get('err')))+'\n'); continue
    m=TPL[d['map']]
    a,na=score(d,beds_of(m),m); b,nb=score(d,VB[d['map']],m)
    cls='template' if a==na else VN[d['map']] if b==nb else 'none'
    if a==na and b==nb: cls='both'
    out.write(json.dumps(dict(game=d['game'],map=d['map'],hash=d['hash'],seed=d['seed'],ranked=d['ranked'],last=d['last'],n=na,tpl=a,var=b,cls=cls))+'\n')
