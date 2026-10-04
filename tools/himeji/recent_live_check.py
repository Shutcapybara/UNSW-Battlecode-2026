"""Audit new own games from a frozen index against a prior audited ID set; no API/store writes."""
import argparse,collections,hashlib,importlib.util,json,sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--himeji',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--prior',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo))
 from tools.analysis.features import frame as F
 spec=importlib.util.spec_from_file_location('himeji_post_refs',a.himeji/'tools/himeji/post_refs.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P);P.init(a.repo)
 idx={r['game_id']:r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};old={int(r['game']) for r in map(json.loads,a.prior.read_text().splitlines())};own=[r for r in idx.values() if 7 in (r['team_a'],r['team_b']) and r['started_at']>='2026-10-01T06:00'];new=sorted([r for r in own if r['game_id'] not in old],key=lambda r:r['game_id']);out=[]
 for m in new:
  path=a.repo/'public_replays/corpus/replays'/f"{m['game_id']}.replay";assert hashlib.sha256(path.read_bytes()).hexdigest()==m['sha256'];root=F._reader(path).object(0,0);rows=P.one((m,str(a.repo/'public_replays/corpus')));assert len(rows)==2 and not any('error' in r for r in rows)
  for r in rows:
   assert r['queen_field_matches'];assert r['official_winner'].lower()==m['winner'];r['submission']=root.text(1 if r['side']=='A' else 2);r['replay_sha256']=m['sha256']
  out.extend(rows)
 (a.snapshot/'recent-live-sides.jsonl').write_text(''.join(json.dumps(r,default=float)+'\n' for r in out));ours=[r for r in out if r['team']=='7'];summary={'post_games':len(own),'post_ranked':sum(r['ranked'] for r in own),'new_games':len(new),'latest_started_at':max(r['started_at'] for r in own),'source_prior_sha256':hashlib.sha256(a.prior.read_bytes()).hexdigest(),'series':[]}
 for sid in sorted({r['series_id'] for r in ours}):
  rs=[r for r in ours if r['series_id']==sid];reached=[r for r in rs if r['reached490']];rl=[r for r in rs if r['round_limit']];summary['series'].append(dict(series=sid,opponent=rs[0]['opp'],ranked=rs[0]['ranked'],submission=rs[0]['submission'],n=len(rs),wins=sum(r['won'] for r in rs),first_start=min(r['started_at'] for r in rs),reached490=len(reached),queen_alive490=sum(r['queen_alive490'] for r in reached),round_limit=len(rl),queen_alive_end_rl=sum(r['queen_alive_end'] for r in rl),games=[dict(game=r['game'],map=r['map'],side=r['side'],won=r['won'],last_round=r['last_round'],reason=r['reason'],queen_length490=r['queen_length490'],queen_length_end=r['queen_length_end'],total_end=r['total_end'],opp_total_end=r['opp_total_end'],q3_r50={k:r[k+'@50'] for k in ['bed_eats','splits','transits','territory']}) for r in rs]))
 (a.snapshot/'recent-live-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
