"""Read-only checkpoint audit of explicitly selected new live-own metadata rows."""
import argparse,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--rows',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
out=[]
for meta in json.loads(a.rows.read_text()):
 p=a.repo/'public_replays/corpus/replays'/f"{meta['game_id']}.replay";assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256'];g=F.decode(p);assert g['winner'].lower()==meta['winner'];side='A' if meta['team_a']==7 else 'B';other='B' if side=='A' else 'A';q=min(i for i,(s,b) in g['rounds'][0].items() if s==side);reached=g['last_round']>=490;cp={}
 for s in ['A','B']:
  qi=min(i for i,(t,b) in g['rounds'][0].items() if t==s);b=g['rounds'][-1].get(qi);assert g['final'][s]['queen']==(len(b[1]) if b else 0)
  cp[s]={'total490':sum(len(b) for t,b in g['rounds'][490].values() if t==s) if reached else None,'queen490':len(g['rounds'][490][qi][1]) if reached and qi in g['rounds'][490] else 0 if reached else None,'final':g['final'][s]}
 out.append({'game':meta['game_id'],'series':meta['series_id'],'ranked':meta['ranked'],'started_at':meta['started_at'],'map':g['map'],'map_hash':g['map_hash'],'side':side,'opponent':meta['team_b'] if side=='A' else meta['team_a'],'submission':F._reader(p).object(0,0).text(1 if side=='A' else 2),'sha256':meta['sha256'],'winner':g['winner'],'won':g['winner']==side,'reason':g['reason'],'reached490':reached,'checkpoint':cp,'queen_death':next((d for d in g['events']['deaths'] if d['id']==q),None)})
a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
