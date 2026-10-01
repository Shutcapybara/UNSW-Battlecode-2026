"""Checkpointed official-header audit, read-only with respect to the source panel."""
import argparse,collections,hashlib,json,sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def one(arg):
 path,repo,i=arg;sys.path.insert(0,repo)
 from tools.analysis.features import frame as F
 root=F._reader(path).object(0,0);res=root.child(4)
 terminated=bool(res.num(0,'B')&1)
 final=[dict(units=res.child(k).num(),longest=res.child(k).num(4),total=res.child(k).num(8),queen=res.child(k).num(12)) for k in [0,1]]
 fa,fb=final
 if bool(fa['units'])!=bool(fb['units']):old='A' if fa['units'] else 'B'
 else:
  ka=(fa['longest'],fa['total']);kb=(fb['longest'],fb['total']);old='A' if ka>kb else 'B' if kb>ka else 'draw'
 actual=('A','B')[res.num(6,'H')] if res.num(4,'H')==1 else 'draw'
 side='A' if i['botA']=='rome-01-nodevil' else 'B';assert i['bot'+side]=='rome-01-nodevil'
 def score(win):return 1 if win==side else .5 if win=='draw' else 0
 return dict(game=Path(path).stem,map=i['map'],seed=i['seed'],side=side,terminated=terminated,old=old,official=actual,runner=i.get('winner'),queen_a=fa['queen'],queen_b=fb['queen'],end_reason=res.num(2,'H'),old_score=score(old),official_score=score(actual) if terminated else None,toolkit=i['toolkit'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--panel',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--expected-games',type=int,default=480);ap.add_argument('--jobs',type=int,default=2);a=ap.parse_args()
 raw=(a.panel/'index.jsonl').read_bytes();idx={r['game']:r for r in map(json.loads,raw.splitlines())};paths=sorted((a.panel/'replays').glob('*.replay'));assert len(paths)==a.expected_games
 a.out.mkdir(parents=True,exist_ok=True);rp=a.out/'winner-rows.jsonl';done={r['game']:r for r in map(json.loads,rp.read_text().splitlines())} if rp.exists() else {}
 with rp.open('a') as f,ProcessPoolExecutor(max_workers=a.jobs) as pool:
  for n,row in enumerate(pool.map(one,[(str(p),str(a.repo),idx[p.stem]) for p in paths if p.stem not in done],chunksize=1),len(done)+1):
   f.write(json.dumps(row)+'\n');f.flush()
   if n%50==0:print(n,flush=True)
 rows=[json.loads(l) for l in rp.read_text().splitlines()];assert len(rows)==len({r['game'] for r in rows})==a.expected_games
 assert all(r['terminated'] and r['toolkit']=='unswbc 1.2.3' for r in rows)
 summary=dict(n=len(rows),index_sha256=hashlib.sha256(raw).hexdigest(),old_wld=[sum(r['old_score']==v for r in rows) for v in [1,0,.5]],official_wld=[sum(r['official_score']==v for r in rows) for v in [1,0,.5]],old_share=sum(r['old_score'] for r in rows)/len(rows),official_share=sum(r['official_score'] for r in rows)/len(rows),changed=sum(r['old']!=r['official'] for r in rows),runner_agrees=sum(r['runner']==r['official'] for r in rows),flips=[r for r in rows if r['old']!=r['official']],per_map={m:dict(n=len(rr),wins=sum(r['official_score']==1 for r in rr),losses=sum(r['official_score']==0 for r in rr),draws=sum(r['official_score']==.5 for r in rr),rl=sum(r['end_reason']==1 for r in rr),old_score=sum(r['old_score'] for r in rr),official_score=sum(r['official_score'] for r in rr)) for m in sorted({r['map'] for r in rows}) for rr in [[r for r in rows if r['map']==m]]})
 (a.out/'winner-audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ['flips','per_map']}),flush=True)
if __name__=='__main__':main()
