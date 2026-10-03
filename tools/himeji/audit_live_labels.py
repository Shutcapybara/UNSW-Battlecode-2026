"""Official terminal audit of Nara's exact team7 sample; no API or cached-frame assumptions."""
import argparse,collections,hashlib,json,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

def one(arg):
 repo,m,n=arg;sys.path.insert(0,repo)
 from tools.analysis.features import frame as F
 p=Path(repo)/'public_replays/corpus/replays'/f"{m['game_id']}.replay";assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];root=F._reader(p).object(0,0);res=root.child(4);assert res.num(0,'B')&1
 si=0 if m['team_a']==7 else 1;oth=1-si;win=('a','b')[res.num(6,'H')] if res.num(4,'H')==1 else 'draw';assert win==m['winner'];final=[dict(units=res.child(k).num(),longest=res.child(k).num(4),total=res.child(k).num(8),queen=res.child(k).num(12)) for k in [0,1]]
 rl=res.num(2,'H')==1;level=next((key for key in ['queen','longest','total'] if final[0][key]!=final[1][key]),'tie') if rl else 'elimination'
 return dict(game=m['game_id'],series=m['series_id'],map=m['map_name'],ranked=m['ranked'],started_at=m['started_at'],side='ab'[si],opponent=m['team_b' if si==0 else 'team_a'],submission=root.text(1+si),official_winner=win,won=win=='ab'[si],lost=win=='ab'[oth],round_limit=rl,level=level,queen=final[si]['queen'],opponent_queen=final[oth]['queen'],total=final[si]['total'],opponent_total=final[oth]['total'],nara_round_limit=n['round_limit'],nara_q_len490=n['q_len490'],nara_last_round=n['last_round'],nara_death=n.get('q_death_round'),sha256=m['sha256'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--index',type=Path,required=True);ap.add_argument('--nara',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(exist_ok=True,parents=True)
 raw=a.nara.read_bytes();nr=[r for r in map(json.loads,raw.splitlines()) if r.get('team')==7];assert len(nr)==len({int(r['game']) for r in nr})==737
 idx={r['game_id']:r for r in map(json.loads,a.index.read_text().splitlines())};manifest=dict(nara_sha256=hashlib.sha256(raw).hexdigest(),index_sha256=hashlib.sha256(a.index.read_bytes()).hexdigest(),games=len(nr));mp=a.out/'live-manifest.json'
 if mp.exists():assert json.loads(mp.read_text())==manifest
 else:mp.write_text(json.dumps(manifest,indent=2)+'\n');(a.out/'nara-own-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in nr))
 p=a.out/'live-header-rows.jsonl';done={r['game'] for r in map(json.loads,p.read_text().splitlines())} if p.exists() else set();todo=[(a.repo,idx[int(r['game'])],r) for r in nr if int(r['game']) not in done]
 with ProcessPoolExecutor(max_workers=2) as pool,p.open('a') as f:
  for i,r in enumerate(pool.map(one,todo,chunksize=1),len(done)+1):
   f.write(json.dumps(r)+'\n');f.flush()
   if i%100==0:print(i,flush=True)
 print('complete',len(nr),flush=True)
if __name__=='__main__':main()
