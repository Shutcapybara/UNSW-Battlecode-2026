"""Fixed-action head-collision fixtures at the food-free movement budget boundary, 1.2.3 only."""
import argparse,hashlib,json,sys
from pathlib import Path
from importlib.metadata import version
from unswbc.engine import EngineModule,WASM_PATH
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert version('unswbc')=='1.2.3';sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
a.out.mkdir(parents=True,exist_ok=True);rows=[];engine=EngineModule()
for length in [2,3,4,5,6,9]:
    budget=(length+3)//4+length-2
    for excess in [0,1,2]:
        steps=budget+excess;W,H=64,8;ls=[f'MAP {W} {H}','SYMMETRY y','MAP_NAME Himeji collision boundary',f'TILE_COUNT {W*H}']+[f'TILE {x} {y} 0 0' for y in range(H) for x in range(W)];ls += [f'EDGE_COUNT {2*W*H}']+[f'EDGE {r*(W+1)+x} 0 0' for r in range(2*H) for x in range(W)];b=[(15-i,2) for i in range(length)];ls+=['DRAGON_COUNT 2','DRAGON 0 '+str(length)+' '+' '.join(f'{x} {y}' for x,y in b),f'DRAGON 1 2 {15+steps} 2 {15+steps} 3','END'];m=('\n'.join(ls)+'\n').encode()
        def reply(i,raw):
            r=int(raw.decode().splitlines()[0].split()[1]);action='MOVE '+('E'*steps) if i==0 and r==0 else 'SPLIT 0';return(action+'\nPROTOCOL 3\nENDTURN\n').encode()
        engine.run(m,reply,debug=0,seed=131);payload=engine.replay('fixed_A','fixed_B');path=a.out/f'L{length}-d{steps}.replay';path.write_bytes(payload);g=F.decode(path);deaths=g['events']['deaths'];struck=any(d['id']==1 and d['cause']=='h2h' for d in deaths);rows.append(dict(length=length,clear_path_budget=budget,target_distance=steps,struck=struck,deaths=deaths,actions=g['events']['actions'],map_sha256=hashlib.sha256(m).hexdigest(),replay_sha256=hashlib.sha256(payload).hexdigest()));print(length,steps,struck,[(d['id'],d['cause']) for d in deaths],flush=True)
(a.out/'summary.json').write_text(json.dumps(dict(runtime=version('unswbc'),engine_sha256=hashlib.sha256(WASM_PATH.read_bytes()).hexdigest(),rows=rows,scope='18 fixed collision fixtures, no food; no bot policy or performance test.'),indent=2)+'\n')
