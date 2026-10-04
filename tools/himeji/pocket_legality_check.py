"""Small fixed-action engine fixtures only: split legality at population cap and sprint space.
No repository bot is loaded, built, modified or compared; no tournament or policy experiment.
Run only with Himeji's isolated unswbc1.2.3 Python.
"""
import argparse,dataclasses,hashlib,json,sys
from pathlib import Path
from importlib.metadata import version
from unswbc.engine import EngineModule,WASM_PATH

def fixture(units, qlen):
    W,H=64,8
    lines=[f'MAP {W} {H}','SYMMETRY y','MAP_NAME Himeji legality fixture',f'TILE_COUNT {W*H}']
    lines += [f'TILE {x} {y} 0 0' for y in range(H) for x in range(W)]
    walls={(2*y, x) for y in [1,3] for x in [2,3]} | {(2*y+1,x) for y in [1,2] for x in [2,4]}
    lines.append(f'EDGE_COUNT {2*W*H}')
    lines += [f'EDGE {r*(W+1)+x} {int((r,x) in walls)} 0' for r in range(2*H) for x in range(W)]
    bodies=[(0,[(3,2),(3,1),(2,1),(2,2)][:qlen]),(1,[(60,1),(61,1)])]
    for j in range(units-1):
        y=4+j//32;x=2*(j%32);bodies.append((0,[(x,y),(x+1,y)]));bodies.append((1,[(x,y+2),(x+1,y+2)]))
    lines.append(f'DRAGON_COUNT {len(bodies)}')
    lines += ['DRAGON '+str(t)+' '+str(len(b))+' '+' '.join(f'{x} {y}' for x,y in b) for t,b in bodies]
    return ('\n'.join(lines+['END'])+'\n').encode(),len(bodies)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert version('unswbc')=='1.2.3';sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
    a.out.mkdir(exist_ok=True);engine=EngineModule();rows=[]
    cases=[(63,4,'SPLIT 2'),(64,4,'SPLIT 2')]+[(64,4,'MOVE '+d) for d in ['N','E','S','W','WN']]+[(64,3,'MOVE WN')]
    for n,(units,qlen,first) in enumerate(cases):
        m,ninitial=fixture(units,qlen);spawn=[];turns=[]
        def reply(i,raw):
            ls=[s for s in raw.decode().splitlines() if s];rnd=int(ls[0].split()[1]);length=int(ls[2].split()[1]);count=int(ls[3].split()[1])
            if i==0:
                if rnd==0:action=first
                elif first=='SPLIT 2':action='MOVE '+['W','N','E','S'][(rnd-1)%4]
                else:action='SPLIT 0'
                turns.append({'round':rnd,'length':length,'units':count,'action':action})
            elif i==1:action='MOVE W' if rnd<4 else 'SPLIT 0'
            elif i>=ninitial:action='MOVE N'
            else:action='SPLIT 0'
            return (action+'\nPROTOCOL 3\nENDTURN\n').encode()
        result=engine.run(m,reply,bot_spawn=lambda i,b:spawn.append({'id':i,'init':b.decode()}),debug=0,seed=116)
        payload=engine.replay('fixture_A','fixture_B');p=a.out/f'fixture-{n}.replay';p.write_bytes(payload);g=F.decode(p)
        qdeath=next((d for d in g['events']['deaths'] if d['id']==0),None)
        row={'case':n,'units':units,'queen_length':qlen,'first_action':first,'map_sha256':hashlib.sha256(m).hexdigest(),'replay_sha256':hashlib.sha256(payload).hexdigest(),'initial_queen_block':spawn[0]['init'],'queen_turns':turns,'queen_death':qdeath,'queen_splits':[s for s in g['events']['splits'] if s['parent']==0],'result':dataclasses.asdict(result)}
        if units==63 and first=='SPLIT 2':assert qdeath is None and row['queen_splits'] and turns[1]['length']==2 and turns[2]['length']==3
        elif first=='SPLIT 2':assert qdeath['round']==0 and qdeath['cause']=='invalid'
        elif qlen==4:assert qdeath['round']==0 and qdeath['cause'] in ['wall','self']
        else:assert turns[1]['length']==2
        rows.append(row);print(n,units,qlen,first,'death',None if qdeath is None else (qdeath['round'],qdeath['cause']),flush=True)
    (a.out/'legality-summary.json').write_text(json.dumps({'runtime':version('unswbc'),'engine_wasm_sha256':hashlib.sha256(WASM_PATH.read_bytes()).hexdigest(),'seed':116,'cases':rows,'limitation':'Eight deterministic legal-action fixtures, not independent games or a strategy win-rate test. Other units use fixed terminating actions; no population-level survival estimate.'},indent=2)+'\n')
if __name__=='__main__':main()
