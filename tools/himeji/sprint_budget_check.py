"""Fixed-action 1.2.3 engine checks of food-free sprint budgets; no bot/policy experiment."""
import argparse,hashlib,json,sys
from pathlib import Path
from importlib.metadata import version
from unswbc.engine import EngineModule,WASM_PATH
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert version('unswbc')=='1.2.3';sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
a.out.mkdir(parents=True,exist_ok=True);rows=[];engine=EngineModule()
for length in [2,3,4,5,6,9]:
    budget=(length+3)//4+length-2
    for steps in [budget,budget+1]:
        W,H=64,8;ls=[f'MAP {W} {H}','SYMMETRY y','MAP_NAME Himeji sprint budget fixture',f'TILE_COUNT {W*H}']
        ls += [f'TILE {x} {y} 0 0' for y in range(H) for x in range(W)]
        ls += [f'EDGE_COUNT {2*W*H}']+[f'EDGE {r*(W+1)+x} 0 0' for r in range(2*H) for x in range(W)]
        b=[(15-i,2) for i in range(length)];ls+=['DRAGON_COUNT 2','DRAGON 0 '+str(length)+' '+' '.join(f'{x} {y}' for x,y in b),'DRAGON 1 2 45 6 44 6','END'];m=('\n'.join(ls)+'\n').encode();turns=[]
        def reply(i,raw):
            lines=raw.decode().splitlines();r=int(lines[0].split()[1]);L=int(lines[2].split()[1])
            if i==0:turns.append(dict(round=r,length=L));action='MOVE '+('E'*steps) if r==0 else 'SPLIT 0'
            else:action='MOVE N' if r<2 else 'SPLIT 0'
            return (action+'\nPROTOCOL 3\nENDTURN\n').encode()
        engine.run(m,reply,debug=0,seed=130);payload=engine.replay('fixed_A','fixed_B');path=a.out/f'L{length}-s{steps}.replay';path.write_bytes(payload);g=F.decode(path)
        death=next(d for d in g['events']['deaths'] if d['id']==0);r1=next((x for x in turns if x['round']==1),None)
        rows.append(dict(length=length,steps=steps,formula_budget=budget,reached_round1=r1,death=death,first_action=next(x for x in g['events']['actions'] if x['id']==0),map_sha256=hashlib.sha256(m).hexdigest(),replay_sha256=hashlib.sha256(payload).hexdigest()))
        print(length,steps,r1,death['round'],death['cause'],flush=True)
(a.out/'summary.json').write_text(json.dumps(dict(runtime=version('unswbc'),engine_sha256=hashlib.sha256(WASM_PATH.read_bytes()).hexdigest(),rows=rows,scope='12 deterministic no-food open-path checks. A terminates deliberately at round1 if alive; not game performance or population evidence.'),indent=2)+'\n')
