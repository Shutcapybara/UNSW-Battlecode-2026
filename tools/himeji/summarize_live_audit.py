import argparse,collections,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);a=ap.parse_args();rows=list(map(json.loads,(a.out/'live-header-rows.jsonl').read_text().splitlines()));assert len(rows)==737
 out=dict(games=len(rows),official_round_limit=sum(r['round_limit'] for r in rows),nara_round_limit=sum(r['nara_round_limit'] for r in rows),levels=dict(collections.Counter(r['level'] for r in rows)),queen_alive_end_rl=sum(r['queen']>0 for r in rows if r['round_limit']),queen_decided_losses=sum(r['lost'] and r['level']=='queen' for r in rows),groups=[],ranked_maps=dict(collections.Counter(r['map'] for r in rows if r['ranked'])),first_start=min(r['started_at'] for r in rows),last_start=max(r['started_at'] for r in rows))
 groups=collections.defaultdict(list)
 for r in rows:groups[(r['submission'],r['ranked'])].append(r)
 for (sub,mode),rr in sorted(groups.items()):
  rl=[r for r in rr if r['round_limit']];loss=[r for r in rl if r['lost']];lead=[r for r in rl if r['total']>r['opponent_total']]
  out['groups'].append(dict(submission=sub,ranked=mode,n=len(rr),series=len({r['series'] for r in rr}),wins=sum(r['won'] for r in rr),losses=sum(r['lost'] for r in rr),rl=len(rl),queen_alive=sum(r['queen']>0 for r in rl),queen_losses=sum(r['level']=='queen' and r['lost'] for r in rr),rl_losses=len(loss),losses_with_final_total_lead=sum(r['total']>r['opponent_total'] for r in loss),final_total_leads=len(lead),losses_given_final_total_lead=sum(r['lost'] for r in lead),first_start=min(r['started_at'] for r in rr),last_start=max(r['started_at'] for r in rr)))
 assert all(r['round_limit']==(r['nara_round_limit'] or r['level']=='queen') for r in rows)
 (a.out/'live-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
