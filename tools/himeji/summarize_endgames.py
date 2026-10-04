import argparse,collections,json
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser();ap.add_argument('snapshot',type=Path);a=ap.parse_args();m=json.loads((a.snapshot/'manifest.json').read_text());top={r['id'] for r in m['top10']};rows=list(map(json.loads,(a.snapshot/'endgame-rows.jsonl').read_text().splitlines()));sides=[];rulesbad=[]
 for r in rows:
  aa,bb=r['final']
  if r['round_limit']:
   ka=(aa['queen'],aa['longest'],aa['total']);kb=(bb['queen'],bb['longest'],bb['total']);expected='a' if ka>kb else 'b' if kb>ka else 'draw'
   if expected!=r['winner']:rulesbad.append(r['game'])
  for i in [0,1]:
   if r['teams'][i] not in top:continue
   f=r['final'][i];o=r['final'][1-i]
   sides.append(dict(game=r['game'],team=r['teams'][i],ranked=r['ranked'],map=r['map'],series=r['series'],round_limit=r['round_limit'],won=r['winner']=='ab'[i],lost=r['winner']=='ab'[1-i],queen=f['queen'],queen_opp=o['queen'],longest=f['longest'],total=f['total'],material_lead=f['total']>o['total']))
 out=dict(audited_games=len(rows),round_limit_games=sum(r['round_limit'] for r in rows),queen_then_longest_then_total_mismatches=rulesbad,cohorts=[],teams=[])
 for mode in [True,False]:
  rr=[r for r in sides if r['ranked']==mode and r['round_limit']];alone=[r for r in rr if r['queen']>0 and r['queen_opp']==0];los=[r for r in rr if r['lost']];leads=[r for r in rr if r['material_lead']]
  groups=collections.defaultdict(list)
  for r in rr:groups[r['series']].append(r)
  blocks=list(groups.values());rng=np.random.default_rng(104);boots=[]
  if len(blocks)>=2:
   for _ in range(1000):
    sample=[r for j in rng.integers(0,len(blocks),len(blocks)) for r in blocks[j]];boots.append(sum(r['queen']>0 for r in sample)/len(sample))
  ci=np.quantile(boots,[.025,.975]).tolist() if boots else None
  out['cohorts'].append(dict(queen_alive_ci95=ci,ranked=mode,rl_sides=len(rr),series=len({r['series'] for r in rr}),queen_alive=sum(r['queen']>0 for r in rr),sole_queen=len(alone),sole_queen_wins=sum(r['won'] for r in alone),losses=len(los),losses_with_final_total_lead=sum(r['material_lead'] for r in los),final_total_leads=len(leads),losses_given_final_total_lead=sum(r['lost'] for r in leads)))
 for tid in sorted(top):
  for mode in [True,False]:
   rr=[r for r in sides if r['team']==tid and r['ranked']==mode and r['round_limit']]
   out['teams'].append(dict(team=tid,ranked=mode,rl_n=len(rr),queen_alive=sum(r['queen']>0 for r in rr),positive_queen_lengths=[r['queen'] for r in rr if r['queen']>0]))
 (a.snapshot/'endgame-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
