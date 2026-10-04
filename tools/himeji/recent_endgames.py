"""Official terminal queen anatomy on the freshly decoded coverage sample."""
import argparse,hashlib,json,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

def one(arg):
 repo,r=arg;sys.path.insert(0,repo)
 from tools.analysis.features import frame as F
 p=Path(repo)/'public_replays/corpus/replays'/f"{r['game_id']}.replay";assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 root=F._reader(p).object(0,0);res=root.child(4);assert res.num(0,'B')&1
 winner=('a','b')[res.num(6,'H')] if res.num(4,'H')==1 else 'draw';assert winner==r['winner']
 final=[dict(units=res.child(k).num(),longest=res.child(k).num(4),total=res.child(k).num(8),queen=res.child(k).num(12)) for k in [0,1]]
 return dict(game=r['game_id'],ranked=r['ranked'],map=r['map_name'],series=r['series_id'],started_at=r['started_at'],teams=[r['team_a'],r['team_b']],winner=winner,round_limit=res.num(2,'H')==1,final=final)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--store',type=Path,required=True);a=ap.parse_args()
 import pandas as pd
 ids=set(pd.concat([pd.read_parquet(f,columns=['game']) for f in (a.store/'sides').glob('part*')]).game.astype(str));idx={str(r['game_id']):r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};p=a.snapshot/'endgame-rows.jsonl'
 with ProcessPoolExecutor(max_workers=2) as pool, p.open('w') as f:
  for r in pool.map(one,[(a.repo,idx[i]) for i in sorted(ids)],chunksize=1):f.write(json.dumps(r)+'\n');f.flush()
 print('audited',len(ids),flush=True)
if __name__=='__main__':main()
