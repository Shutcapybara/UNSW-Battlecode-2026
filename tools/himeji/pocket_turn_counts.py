"""Exact TurnStart own-unit counts for the four previously observed late pocket deaths."""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--prior',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
prior=[r for r in json.loads(a.prior.read_text()) if r['death']];out=[]
for gid in sorted({r['game'] for r in prior}):
 p=a.repo/'public_replays/corpus/replays'/f'{gid}.replay';root=F._reader(p).object(0,0);m=F.terrain(root.text(0))[0];teams={i:s for i,(s,b) in enumerate(m['dragons'])};live=set(teams);counts=collections.Counter(teams.values());targets={(r['queen'],r['death']['round']):r for r in prior if r['game']==gid};rnd=-1
 for e in root.items(3):
  k=e.num(0,'H');o=e.child(0);i=o.num()
  if k==0:rnd=i
  elif k==10:child=o.num(4);teams[child]=teams[i];live.add(child);counts[teams[i]]+=1
  elif k==11:live.remove(i);counts[teams[i]]-=1
  elif k==1 and (i,rnd) in targets:out.append({'game':gid,'queen':i,'team':targets[(i,rnd)]['team'],'round':rnd,'units_at_turn_start':counts[teams[i]],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert len(out)==4;a.out.write_text(json.dumps(out,indent=2)+'\n');print(out)
