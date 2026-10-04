"""Equal-own-block summaries on the frozen unit25 matched selection; no causal or population rate claim."""
import argparse,collections,json,statistics
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--rows',type=Path,required=True);ap.add_argument('--flow-rows',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sel=json.loads(a.selection.read_text());gs={x['game_id']:x for x in map(json.loads,a.rows.read_text().splitlines())};old={x['game_id']:x for x in map(json.loads,a.flow_rows.read_text().splitlines())};assert set(gs)==set(sel['games']);verification=0

def metrics(gid,side,start):
 global verification
 r=next(r for r in gs[gid]['rows'] if r['side']==side and r['start']==start);food=collections.Counter({(x['age_group'],x['origin']):x['n'] for x in r['food']});origins=collections.Counter()
 for (age,o),n in food.items():origins[o]+=n
 if start==250:
  ref=next(x for x in old[gid]['sides'] if x['side']==side);assert dict(origins)==ref['eats'];verification+=1
 young=lambda origin:food['child_age0_9',origin]
 bed=origins['bed'];corpse=origins['ally_corpse']+origins['enemy_corpse'];total=sum(origins.values());youngall=sum(n for (age,o),n in food.items() if age=='child_age0_9');turns=sum(r['action_turns'].values());yt=r['action_turns'].get('child_age0_9',0)
 cross=collections.Counter({(x['cell_type'],x['origin']):x['n'] for x in r['template_cross']});proxy=sum(n for (cell,o),n in cross.items() if cell=='template_other');falsecorpse=cross['template_other','bed'];corpseonbed=cross['template_bed','ally_corpse']+cross['template_bed','enemy_corpse']
 return dict(bed=bed,corpse=corpse,total_meals=total,young_bed=young('bed'),young_bed_share=young('bed')/bed if bed else 0,young_meals=youngall,young_meal_share=youngall/total,young_turn_share=yt/turns,young_bed_per_turn=young('bed')/yt if yt else 0,older_bed_per_turn=(bed-young('bed'))/(turns-yt) if turns>yt else 0,born_in_window=r['born_in_window'],born_window_bed_eaters=r['born_in_window_bed_eaters'],born_window_bed_meals=r['born_in_window_bed_meals'],corpse_share=corpse/total,template_other_share=proxy/total,bed_at_template_other=falsecorpse,corpse_at_template_bed=corpseonbed,unknown=origins['unknown'])
blocks=[]
for start in [0,250]:
 for b in sel['blocks']:
  own=metrics(b['own_game'],b['side'],start);fs=[metrics(m['game'],b['side'],start) for m in b['matches']];field={k:statistics.mean(f[k] for f in fs) for k in own};blocks.append(dict(start=start,own_game=b['own_game'],map_hash=b['map_hash'],side=b['side'],own=own,field=field,difference={k:field[k]-own[k] for k in own}))
windows=[]
for start in [0,250]:
 bs=[b for b in blocks if b['start']==start];windows.append(dict(start=start,end=250 if start==0 else 400,means={group:{k:statistics.mean(b[group][k] for b in bs) for k in bs[0][group]} for group in ['own','field','difference']},ranges={k:[min(b['difference'][k] for b in bs),max(b['difference'][k] for b in bs)] for k in bs[0]['own']}))
# Unique side-window totals for deterministic provenance classification diagnostics.
cross=collections.Counter()
for g in gs.values():
 for r in g['rows']:
  if r['start']==250:
   for x in r['template_cross']:cross[x['cell_type'],x['origin']]+=x['n']
result=dict(blocks=blocks,windows=windows,provenance_cross_late=[dict(cell=k,origin=o,n=n) for (k,o),n in sorted(cross.items())],verified_matched_late_side_slots=verification,unique_games=len(gs),uncertainty='Same6own/18field slots/17unique fieldgames and5connectedseriesgroups as unit25. New endpoints, no independent replication; ranges only, no stable target or causal replacement benefit. Exposure/food shares are each-game ratios averaged equally by own block.')
a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(windows=windows,provenance_cross_late=result['provenance_cross_late']),indent=2))
