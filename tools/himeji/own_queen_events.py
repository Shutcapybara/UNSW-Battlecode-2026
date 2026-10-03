"""Inspect original-queen death and actions in named own losses; read-only replay decoding."""
import argparse,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--games',required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
idx={r['game_id']:r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};out=[]
for gid in map(int,a.games.split(',')):
 m=idx[gid];p=a.repo/'public_replays/corpus/replays'/f'{gid}.replay';assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];g=F.decode(p);s='A' if m['team_a']==7 else 'B';q=min(i for i,(t,b) in g['rounds'][0].items() if t==s);death=next((d for d in g['events']['deaths'] if d['id']==q),None);r=death['round'] if death else None
 out.append(dict(game=gid,side=s,queen=q,spawn_body=g['rounds'][0][q][1],death=death,nearby_actions=[e for e in g['events']['actions'] if e['id']==q and r-2<=e['round']<=r],nearby_splits=[e for e in g['events']['splits'] if e['parent']==q and r-2<=e['round']<=r],before_death_body=g['rounds'][r].get(q),sha256=m['sha256']))
(a.snapshot/'own-queen-events.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
