"""Compare fertility metadata in public replay headers, local replays and authored maps."""
import argparse,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--rome',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
items=[]
for gid in [997644,995611,996984,998186,992701,999614,999613,999610,999612,999611]:items.append(('public',str(gid),a.repo/'public_replays/corpus/replays'/f'{gid}.replay'))
for mapname in ['portals','schooltime','trauma','autarky']:
 root=a.rome/'build/zoo/z1-rome-01-nodevil-28132ee5';idx=[json.loads(s) for s in (root/'index.jsonl').read_text().splitlines()];r=next(r for r in idx if r['map']==mapname);items.append(('local',r['game'],root/r['replay']))
rows=[]
for population,label,p in items:
 raw=F._reader(p).object(0,0).text(0);m=F.terrain(raw)[0];vals=list(m['tiles'].values());rows.append({'population':population,'game':label,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'map_header_sha256':hashlib.sha256(raw.encode()).hexdigest(),'tiles':len(vals),'positive_max_gap':sum(v[1]>0 for v in vals),'nonzero_gap_pair':sum(v!=(0,0) for v in vals)})
maps=[]
for name in ['portals','schooltime','trauma','autarky']:
 p=a.repo/'maps'/f'{name}.map';text=p.read_text();m=F.terrain(text)[0];maps.append({'map':name,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tiles':len(m['tiles']),'positive_max_gap':sum(v[1]>0 for v in m['tiles'].values())})
a.out.write_text(json.dumps({'replays':rows,'authored_maps':maps,'limitation':'Authored map fertility is not substituted into transformed live headers; comparison diagnoses metadata availability, not exact live bed placement.'},indent=2)+'\n');print(json.dumps({'replays':rows,'maps':maps},indent=2))
