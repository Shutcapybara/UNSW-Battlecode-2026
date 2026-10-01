"""Read-only official replay outcome audit for two already completed local panels.
Outputs are checkpointed; source indexes must match on resume. No feature rebuilds.
"""
import argparse, collections, hashlib, json, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def one(arg):
 repo, path, bot, panel, row = arg
 sys.path.insert(0, repo)
 from tools.analysis.features import frame as F
 p=Path(path); root=F._reader(p).object(0,0); res=root.child(4)
 final=[dict(units=res.child(k).num(),longest=res.child(k).num(4),total=res.child(k).num(8),queen=res.child(k).num(12)) for k in [0,1]]
 fa,fb=final
 if bool(fa['units']) != bool(fb['units']): old='A' if fa['units'] else 'B'
 else:
  ka=(fa['longest'],fa['total']); kb=(fb['longest'],fb['total']); old='A' if ka>kb else 'B' if kb>ka else 'draw'
 official=('A','B')[res.num(6,'H')] if res.num(4,'H')==1 else 'draw'
 side=row['seat']; assert row['bot'+side]==bot
 def score(w): return .5 if w=='draw' else float(w==side)
 return dict(bot=bot,panel=panel,game=row['game'],map=row['map'],seed=row['seed'],opp=row['opp'],side=side,terminated=bool(res.num(0,'B')&1),end_reason=res.num(2,'H'),official=official,old=old,runner=row['winner'],official_score=score(official),old_score=score(old),final=final,replay_sha256=sha(p))

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True); ap.add_argument('--runs',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--base',default='kyoto-01-nodevil'); ap.add_argument('--candidate',default='kyoto-03-latecap'); ap.add_argument('--jobs',type=int,default=2); a=ap.parse_args()
 a.out.mkdir(parents=True,exist_ok=True); manifest={'base':a.base,'candidate':a.candidate,'source_indexes':{},'failures':[]}; tasks=[]
 for bot in [a.base,a.candidate]:
  for panel in ['pool','gen']:
   root=a.runs/bot/panel; files=sorted(p for p in root.glob('index-*.jsonl') if p.name!='index-all.tmp.jsonl')
   rows=[json.loads(l) for p in files for l in p.read_text().splitlines()]; assert len(rows)==len({r['game'] for r in rows}), 'Retry duplicates require explicit resolution'
   for p in files: manifest['source_indexes'][str(p)]=sha(p)
   assert len(rows)==(480 if panel=='pool' else 744)
   for r in rows:
    if r['rc']!=0: manifest['failures'].append(dict(bot=bot,**r)); continue
    path=root/r['replay']; assert path.is_file(); tasks.append((a.repo,str(path),bot,panel,r))
 mp=a.out/'manifest.json'
 if mp.exists(): assert json.loads(mp.read_text())==manifest, 'Source changed since checkpoint'
 else: mp.write_text(json.dumps(manifest,indent=2)+'\n')
 rp=a.out/'header-rows.jsonl'; done={ (r['bot'],r['panel'],r['game']) for r in map(json.loads,rp.read_text().splitlines())} if rp.exists() else set()
 todo=[t for t in tasks if (t[2],t[3],t[4]['game']) not in done]
 with rp.open('a') as out, ProcessPoolExecutor(max_workers=a.jobs) as pool:
  for n,row in enumerate(pool.map(one,todo,chunksize=1),len(done)+1):
   out.write(json.dumps(row)+'\n');out.flush()
   if n%100==0: print(n,flush=True)
 assert all(sha(Path(p))==s for p,s in manifest['source_indexes'].items())
 rows=list(map(json.loads,rp.read_text().splitlines())); assert len(rows)==len(tasks)==len({(r['bot'],r['panel'],r['game']) for r in rows})
 assert all(r['terminated'] and r['runner']==r['official'] for r in rows)
 print('COMPLETE',len(rows),flush=True)
if __name__=='__main__': main()
