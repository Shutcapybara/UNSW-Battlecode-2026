"""Two scripted engine edge cases: pearl on first step versus empty route; no bot experiments."""
import argparse,dataclasses,hashlib,json,sys
from pathlib import Path
from importlib.metadata import version
from unswbc.engine import EngineModule,WASM_PATH
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--tools',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert version('unswbc')=='1.2.3';sys.path[:0]=[str(a.repo),str(a.tools)];from pocket_legality_check import fixture
from tools.analysis.features import frame as F
a.out.mkdir(exist_ok=True);rows=[]
for food in [False,True]:
 m,n=fixture(64,3)
 if food:m=m.replace(b'TILE 2 2 0 0',b'TILE 2 2 1 1').replace(b'TILE 61 2 0 0',b'TILE 61 2 1 1')
 eng=EngineModule();turns=[]
 def reply(i,raw):
  lines=raw.decode().splitlines();rnd=int(lines[0].split()[1]);act='MOVE WN' if i==0 and rnd==0 else 'MOVE W' if i==1 and rnd<3 else 'SPLIT 0'
  if i==0:turns.append({'round':rnd,'action':act,'raw_observation':raw.decode()})
  return (act+'\nPROTOCOL 3\nENDTURN\n').encode()
 result=eng.run(m,reply,debug=0,seed=117);payload=eng.replay('fixture_A','fixture_B');p=a.out/('food.replay' if food else 'empty.replay');p.write_bytes(payload);g=F.decode(p);rows.append({'food_bed_enabled':food,'map_sha256':hashlib.sha256(m).hexdigest(),'replay_sha256':hashlib.sha256(payload).hexdigest(),'queen_turns':turns,'queen_actions':[e for e in g['events']['actions'] if e['id']==0],'queen_eats':[e for e in g['events']['eats'] if e['id']==0],'queen_deaths':[e for e in g['events']['deaths'] if e['id']==0],'spawns_before2':[e for e in g['events']['spawns'] if e['round']<2 and e['cell']==(2,2)],'result':dataclasses.asdict(result)})
(a.out/'food-step-check.json').write_text(json.dumps({'runtime':version('unswbc'),'engine_wasm_sha256':hashlib.sha256(WASM_PATH.read_bytes()).hexdigest(),'rows':rows,'limitation':'Two deterministic legality fixtures only. Queen deliberately terminates at round1 if alive. The bed is placed on first W step; inspect actual spawn/eat before claiming food exposure.'},indent=2)+'\n')
for r in rows:print(r['food_bed_enabled'],r['queen_actions'],r['queen_eats'],r['queen_deaths'],[(t['round'],t['raw_observation'].splitlines()[2]) for t in r['queen_turns']])
