"""Read one observed split-and-child-death sequence; no simulation or behavioral intervention."""
import argparse,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--game',type=int,default=995611);ap.add_argument('--side',choices=['A','B'],default='A');a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
p=a.repo/'public_replays/corpus/replays'/f'{a.game}.replay';g=F.decode(p);q=min(i for i,(s,b) in g['rounds'][0].items() if s==a.side);sp=next(e for e in g['events']['splits'] if e['parent']==q and e['round']==0);ids=[q,sp['child']]
out={'game':a.game,'queen':q,'split':sp,'replay_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actions':[e for e in g['events']['actions'] if e['id'] in ids and e['round']<=4],'deaths':[e for e in g['events']['deaths'] if e['id'] in ids],'food':[e for e in g['events']['eats'] if e['id']==q],'queen_head_cells':sorted({g['rounds'][r][q][1][0] for r in range(len(g['rounds'])) if q in g['rounds'][r]}),'lengths_seen':sorted({len(s[q][1]) for s in g['rounds'] if q in s}),'states':[{str(i):g['rounds'][r].get(i) for i in ids} for r in range(5)]};
seen={tuple(out['queen_head_cells'][0])};queue=list(seen)
while queue:
 for x in g['nbr'][queue.pop()]:
  if x is not None and x not in seen:seen.add(x);queue.append(x)
out['terrain_component_size']=len(seen);out['terrain_component_cells']=sorted(seen);out['component_beds']=[list(x) for x in seen if x in g['beds']]
a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['actions','states']},indent=2))
