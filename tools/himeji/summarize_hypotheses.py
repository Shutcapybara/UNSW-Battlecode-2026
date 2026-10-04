"""Summarize frozen hypothesis evidence; all rates retain their selection denominator."""
import argparse,collections,json,math
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,required=True);a=ap.parse_args();rows=list(map(json.loads,(a.snapshot/'hypothesis-rows.jsonl').read_text().splitlines()));selection=json.loads((a.snapshot/'hypothesis-selection.json').read_text());assert len(rows)==len(set(selection['cases']+selection['controls']+selection['growth_games']))
cases=[];controls=[];growth=[]
for r in rows:
 own=next((s for s in r['sides'] if s['team']==7),None)
 if r['case'] and own:
  op=next(s for s in r['sides'] if s['team']!=7);cases.append(dict(game=r['game'],map=r['map'],hash=r['map_hash'],series=r['series'],ranked=r['ranked'],submission=own['submission'],cause=own['death']['cause'],round=own['death']['round'],q=own['queen'],empty=len(own['initial_empty_one_step_directions']),opponent=op['team'],opponent_first_split=any(e['kind']=='split' for e in op['initial_actions']),opponent_q_alive25=op['checkpoints']['25']['alive'],opponent_q_alive490=op['checkpoints']['490']['alive'],opponent_q_end=op['final']['queen']))
 if r['control'] and own:controls.append(dict(game=r['game'],ranked=r['ranked'],submission=own['submission'],hash=r['map_hash'],empty=len(own['initial_empty_one_step_directions']),first_split=any(e['kind']=='split' for e in own['initial_actions']),q_alive25=own['checkpoints']['25']['alive']))
 if r['growth']:
  for s in r['sides']:
   if s['team'] not in [306,91]:continue
   c=s['checkpoints'];growth.append(dict(game=r['game'],team=s['team'],map=r['map'],series=r['series'],winner=r['winner']==s['side'],reason=r['reason'],queen100=c['100']['length'],queen300=c['300']['length'],queen400=c['400']['length'],reached490=c['490']['reached'],queen490=c['490']['length'],queen_end=s['final']['queen'],splits_before100=s['queen_splits_before100'],ally_food_late=s['queen_food_after300'].get('ally_corpse',0),bed_food_late=s['queen_food_after300'].get('bed',0),death=s['death']))
selfs=[r for r in cases if r['cause']=='self'];out={'case_self':len(selfs),'case_other':len(cases)-len(selfs),'self_empty_zero':sum(r['empty']==0 for r in selfs),'self_series':len({r['series'] for r in selfs}),'opponent_split':sum(r['opponent_first_split'] for r in selfs),'opponent_split_alive25':sum(r['opponent_first_split'] and r['opponent_q_alive25'] for r in selfs),'opponent_split_alive490':sum(r['opponent_first_split'] and bool(r['opponent_q_alive490']) for r in selfs),'cases':cases,'controls':controls,'growth':growth,'growth_counts':{'n':len(growth),'series':len({r['series'] for r in growth}),'reach490':sum(r['reached490'] for r in growth),'alive490':sum(bool(r['queen490']) for r in growth),'before100_split':sum(r['splits_before100']>0 for r in growth),'late_ally_food':sum(r['ally_food_late']>0 for r in growth)},'sizes':{str(d):math.ceil((1.96+.84)**2*(d-.1**2)/.1**2) for d in [.2,.4,.6]}}
(a.snapshot/'hypothesis-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['cases','growth']},indent=2));print(json.dumps(growth,indent=2))
