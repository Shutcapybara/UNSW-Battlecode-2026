"""Summarize committed donor-cohort receipts without decoding or accessing a database."""
import argparse,collections,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('audit',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
rs=json.loads((a.audit/'corpse-cohort-check.json').read_text())['rows'];totals={k:collections.Counter() for k in ['all_sides','own_sides']};examples=[]
for r in rs:
 for s in r['sides']:
  f=s['fixed20'];d=dict(spawns=s['late_corpse_spawns'],loose_enemy=s['late_meals_by_eater'].get('enemy',0),cohort_enemy=s['same_spawn_cohort_meals'].get('enemy',0),loose_ally=s['late_meals_by_eater'].get('ally',0),cohort_ally=s['same_spawn_cohort_meals'].get('ally',0),carry=sum(s['pre150_carry_in_meals'].values()),fixed_eligible=f['eligible'],fixed_enemy=f['enemy'],fixed_ally=f['ally'],fixed_not=f['not_eaten_by20'])
  assert d['fixed_eligible']==d['fixed_enemy']+d['fixed_ally']+d['fixed_not']
  totals['all_sides'].update(d)
  if s['side']==r['own_side']:totals['own_sides'].update(d)
  if d['carry']:examples.append(dict(game=r['game'],map=r['map'],side=s['side'],**d,examples=s['carry_examples']))
a.out.write_text(json.dumps(dict(**totals,carry_affected_side_games=len(examples),carry_examples=examples),indent=2)+'\n')
