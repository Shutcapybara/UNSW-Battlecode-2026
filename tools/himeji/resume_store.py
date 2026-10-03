"""Incremental Himeji v7 store from a frozen corpus index, no API calls or legacy writes."""
import argparse,collections,fcntl,hashlib,json,sys,time
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--store',type=Path,required=True);ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--seconds',type=int,default=180);ap.add_argument('--since',default='2026-10-02T22:00');a=ap.parse_args()
 a.store.mkdir(parents=True,exist_ok=True);lock=(a.store/'writer.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 sys.path.insert(0,str(a.repo));from tools.s1 import build as B
 from tools.analysis.features import frame as F
 import pandas as pd
 assert F.FRAME_VERSION==7
 source={str(p.relative_to(a.repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.repo/'tools/s1/build.py',a.repo/'tools/s1/extras.py',a.repo/'tools/analysis/features/frame.py',a.repo/'tools/analysis/features/extract.py']}
 sourcefile=a.store/'decoder-source.json'
 if sourcefile.exists():assert json.loads(sourcefile.read_text())==source, 'Decoder changed: use a new store version'
 else:sourcefile.write_text(json.dumps(source,indent=2)+'\n')
 rows={str(r['game_id']):r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};lad=json.loads((a.snapshot/'ladder.json').read_text());tops=sorted([r for r in lad if r.get('rank') and r['rank']<=10 and not r.get('dev')],key=lambda r:r['rank']);ids=[7]+[r['id'] for r in tops]
 d=pd.DataFrame(rows.values());d['game']=d.game_id.astype(str);d['era']=d.started_at.map(lambda s:'post' if s and s>='2026-10-01T06:00' else 'pre');d.to_parquet(a.store/'.games.parquet.tmp',index=False);(a.store/'.games.parquet.tmp').replace(a.store/'games.parquet');pd.DataFrame(lad).to_parquet(a.store/'.teams.parquet.tmp',index=False);(a.store/'.teams.parquet.tmp').replace(a.store/'teams.parquet')
 done=B.done_games(a.store,clean=False);groups=collections.defaultdict(list)
 for gid,r in rows.items():
  if gid in done or (r.get('started_at') or '')<a.since or r.get('status')!='completed':continue
  for tid in ids:
   if tid in (r['team_a'],r['team_b']):groups[(tid,bool(r['ranked']),r['map_name'])].append(r)
 for rs in groups.values():rs.sort(key=lambda r:r['started_at'],reverse=True)
 keys=sorted(groups,key=lambda k:(ids.index(k[0]),not k[1],k[2]));queue=[];seen=set()
 # Map-balanced round robin across teams and modes, with us first only within each depth.
 maxmaps=max((len([k for k in keys if k[0]==tid]) for tid in ids),default=0)
 fair=[k for j in range(maxmaps) for tid in ids for kk in [[k for k in keys if k[0]==tid]] if j<len(kk) for k in [kk[j]]]
 for depth in range(max((len(v) for v in groups.values()),default=0)):
  for k in fair:
   if depth<len(groups[k]):
    r=groups[k][depth];gid=str(r['game_id'])
    if gid not in seen:seen.add(gid);queue.append(r)
 tasks=[]
 for r in queue:
  p=a.repo/'public_replays/corpus/replays'/f"{r['game_id']}.replay"
  if p.exists():tasks.append((p,str(r['game_id']),dict(team_a=str(r['team_a']),team_b=str(r['team_b']),source='corpus')))
 manifest=dict(index_sha256=hashlib.sha256((a.snapshot/'index.jsonl').read_bytes()).hexdigest(),frame_version=F.FRAME_VERSION,since=a.since,top10=[r['id'] for r in tops],done_before=len(done),queue=len(tasks),jobs=a.jobs,budget_seconds=a.seconds,selected_game_ids=[t[1] for t in tasks],selection='recent current top10 and us; balanced across team,map,mode; explicit coverage sample, not field census')
 (a.store/'last-build.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if k!='selected_game_ids'}),flush=True)
 B.run_batch(a.store,iter(tasks),a.jobs,a.seconds,flush_every=20)
 now=B.done_games(a.store,clean=False);manifest['done_after']=len(now);(a.store/'last-build.json').write_text(json.dumps(manifest,indent=2)+'\n');print('done',len(now),flush=True)
if __name__=='__main__':main()
