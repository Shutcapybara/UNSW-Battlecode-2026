"""Checkpointed event anatomy for named examples; decode only, no simulation or cache writes."""
import argparse,collections,hashlib,json,sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--index',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--games',required=True);a=ap.parse_args();sys.path.insert(0,a.repo)
 from tools.analysis.features import frame as F
 idx={r['game_id']:r for r in map(json.loads,a.index.read_text().splitlines())};a.out.mkdir(exist_ok=True,parents=True)
 for gid in map(int,a.games.split(',')):
  target=a.out/f'{gid}.json'
  if target.exists():continue
  meta=idx[gid];p=Path(a.repo)/'public_replays/corpus/replays'/f'{gid}.replay';assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256'];g=F.decode(p);R=g['rounds'];ev=g['events'];out=dict(game=gid,map=g['map'],map_hash=g['map_hash'],initial_dragons=len(R[0]),reason=g['reason'],winner=g['winner'],last_round=g['last_round'],final=g['final'],source_sha256=meta['sha256'],ranked=meta['ranked'],started_at=meta['started_at'],sides=[])
  for t,tid in [('A',meta['team_a']),('B',meta['team_b'])]:
   q=min(i for i,(tm,b) in R[0].items() if tm==t);actions=[x for x in ev['actions'] if x['id']==q];eats=[x for x in ev['eats'] if x['id']==q];splits=[x for x in ev['splits'] if x['parent']==q];death=[x for x in ev['deaths'] if x['id']==q];donors={x['donor'] for x in eats if x['origin']=='ally_corpse'};finalbody=len(R[-1][q][1]) if q in R[-1] else 0
   checkpoints={str(cp):dict(reached=cp<=g['last_round'],length=(len(R[cp][q][1]) if q in R[cp] else 0) if cp<=g['last_round'] else None) for cp in [0,25,50,100,200,300,400,490]}
   out['sides'].append(dict(team=tid,side=t,original_queen=q,final_body_length=finalbody,checkpoints=checkpoints,move_rounds=len({x['round'] for x in actions if x['kind']=='move'}),multistep_moves=sum(x['kind']=='move' and x['steps']>1 for x in actions),sprint_paid=sum(x.get('paid',0) for x in actions if x['kind']=='move'),eats_by_source=dict(collections.Counter(x['origin'] for x in eats)),splits=splits,death=death,ally_donor_deaths=[x for x in ev['deaths'] if x['id'] in donors],ally_donor_suicides=[x for x in ev['actions'] if x['id'] in donors and x['kind']=='suicide'],queen_corpse_eats=[x for x in eats if x['origin']=='ally_corpse']))
  target.write_text(json.dumps(out,indent=2)+'\n');print(gid,[(r['team'],r['final_body_length'],r['eats_by_source']) for r in out['sides']],flush=True)
if __name__=='__main__':main()
