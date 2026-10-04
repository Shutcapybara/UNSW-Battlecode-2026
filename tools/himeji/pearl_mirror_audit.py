"""Read map symmetry, declared fertility and pearl appearances in one saved replay."""
import argparse,json,sys,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();repo=a.repo;sys.path.insert(0,str(repo));from tools.analysis.features import frame as F
p=repo/'public_replays/corpus/replays/997644.replay';root=F._reader(p).object(0,0);text=root.text(0);g=F.decode(p);m,W,H,*_=F.terrain(text);c=(3,1);mirrors=[c,(W-1-c[0],c[1]),(c[0],H-1-c[1]),(W-1-c[0],H-1-c[1])]
o={'game':997644,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'map_metadata':[s for s in text.splitlines() if not s.startswith(('TILE ','EDGE ','DRAGON '))],'mirror_tiles':{str(x):m['tiles'][x] for x in mirrors},'countdowns_total':len(g['events']['countdowns']),'round267_countdowns':[e for e in g['events']['countdowns'] if e['round']==267],'round267_spawns':[dict(e,static_tile=m['tiles'].get(e['cell'])) for e in g['events']['spawns'] if e['round']==267],'noncorpse_spawn_counts':{}}
from collections import Counter
canonical=F.terrain((repo/'maps/schooltime.map').read_text())
o['canonical_geometry_matches']=g['nbr']==canonical[3]
o['canonical_pocket_tiles']={str(x):canonical[0]['tiles'][x] for x in [(2,1),(2,2),(3,1),(3,2),(56,1),(56,2),(57,1),(57,2)]}
o['spawns_on_canonical_beds']=dict(Counter('on_bed' if e['cell'] in canonical[4] else 'off_bed' for e in g['events']['spawns'] if e['origin']=='bed'))
o['noncorpse_spawn_counts']=dict(Counter('static_bed' if e['cell'] in g['beds'] else 'header_zero_gap_pair' for e in g['events']['spawns'] if e['origin']=='bed'))
a.out.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o,indent=2))
