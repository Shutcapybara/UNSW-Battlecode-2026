"""Measurement audit on newly arrived own replays: align corpse creation and consumption cohorts.
No API, simulator, store or main-checkout writes. Preserve unknowns; never infer submission identity.
"""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--metadata',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
rows=[]
for m in json.loads(a.metadata.read_text()):
 p=a.repo/'public_replays/corpus/replays'/f"{m['game_id']}.replay";assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];g=F.decode(p);root=F._reader(p).object(0,0);assert hashlib.sha256(root.text(0).encode()).hexdigest()==m['map_hash'];assert g['winner'].lower()==m['winner'];assert root.num(0,'I')==2
 own='A' if m['team_a']==7 else 'B';assert g['bot'+own]=='14585';record=dict(game=m['game_id'],series=m['series_id'],ranked=m['ranked'],map=g['map'],map_hash=m['map_hash'],own_side=own,submission=g['bot'+own],opponent_submission=g['bot'+('B' if own=='A' else 'A')],last_round=g['last_round'],winner=g['winner'],sides=[])
 spawns=[s for s in g['events']['spawns'] if s['origin'] in ('A','B')];keys=collections.Counter((s['round'],tuple(s['cell']),s['donor']) for s in spawns);duplicates=sum(n-1 for n in keys.values() if n>1);record['duplicate_spawn_keys']=duplicates
 assert not duplicates,'Need event-level identity for repeated spawn keys'
 for side in 'AB':
  made=[s for s in spawns if s['origin']==side and s['round']>=150];loose=collections.Counter();same=collections.Counter();carry=collections.Counter();examples=[];fixed=collections.Counter();eligible=[s for s in made if s['round']<=min(399,g['last_round']-20)];eligiblekeys={(s['round'],tuple(s['cell']),s['donor']) for s in eligible};consumedkeys=set()
  for e in g['events']['eats']:
   if e['origin'] not in ('ally_corpse','enemy_corpse'):continue
   donor_side=e['team'] if e['origin']=='ally_corpse' else ('B' if e['team']=='A' else 'A')
   if donor_side!=side or e['round']<150:continue
   who='ally' if e['team']==side else 'enemy';born=e['round']-e['age'];loose[who]+=1
   if born>=150:same[who]+=1
   else:
    carry[who]+=1
    if len(examples)<4:examples.append(dict(consumer_team=e['team'],donor=e['donor'],born=born,eaten=e['round'],age=e['age'],cell=e['cell']))
   key=(born,tuple(e['cell']),e['donor'])
   if key in eligiblekeys and e['age']<=20:
    assert key not in consumedkeys;consumedkeys.add(key);fixed[who]+=1
  record['sides'].append(dict(side=side,late_corpse_spawns=len(made),late_meals_by_eater=dict(loose),same_spawn_cohort_meals=dict(same),pre150_carry_in_meals=dict(carry),carry_examples=examples,unconsumed_by_end=len(made)-sum(same.values()),fixed20=dict(born_from=150,born_through=min(399,g['last_round']-20),eligible=len(eligible),ally=fixed['ally'],enemy=fixed['enemy'],not_eaten_by20=len(eligible)-sum(fixed.values())),reached150=g['last_round']>=150))
  assert sum(same.values())<=len(made)
 rows.append(record);print(m['game_id'],'complete',flush=True)
a.out.write_text(json.dumps(dict(rows=rows,contract='Donor cohort born>=150; consumer born=meal round-age. Fixed20 includes births150..min399,R-20, event age<=20. No terminal carry; early endings have no eligible late pearls. Current10game/2series audit, not the peer463-game population. Unconsumed is an accounting residual, not a claim of physically remaining pearls.'),indent=2)+'\n')
