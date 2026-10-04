"""Summarize event-verified attack cases and deterministic engine boundary checks."""
import argparse,collections,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=a.directory
rs=json.loads((d/'strike-audit.json').read_text())['rows'];food=json.loads((d/'food-extension.json').read_text());summary={}
for who in ['us','opp']:
    z=[r for r in rs if r['peer']['who']==who]
    assert all(r['killer_action']['kind']=='move' and r['killer_action']['steps']>=2 for r in z)
    assert all(r['killer_turn_start']['distance']==r['killer_action']['steps'] for r in z)
    assert all(len(r['killer_head_updates_before_queen_death'])==r['killer_action']['steps']-1 for r in z)
    summary[who]=dict(cases=len(z),games=len({r['game'] for r in z}),series=len({r['series'] for r in z}),
        commands=dict(collections.Counter(r['killer_action']['steps'] for r in z)),
        modes=dict(collections.Counter(str(r['ranked']) for r in z)),
        own_submissions=dict(collections.Counter(r['own_submission'] for r in z)),
        map_counts=dict(collections.Counter(r['map'] for r in z)),
        beyond_nofood=sum(r['killer_action']['steps']>((r['killer_turn_start']['killer_length']+3)//4+r['killer_turn_start']['killer_length']-2) for r in z))
for r in json.loads((d/'budget-summary.json').read_text())['rows']:
    assert bool(r['reached_round1'])==(r['steps']==r['formula_budget'])
for r in json.loads((d/'collision-summary.json').read_text())['rows']:
    assert r['struck']==(r['target_distance']==r['clear_path_budget'])
assert len(food)==4 and all(r['eats'] for r in food)
summary.update(unique_games=len({r['game'] for r in rs}),food_extended_cases=[dict(game=r['game'],length=r['turn_start_length'],steps=r['commanded_steps'],food=len(r['eats'])) for r in food],scope='Selected same96-game case audit; no incidence, targeting intent, avoidability or win estimate. Two ranked own cases,18unranked; exact hashes retained.')
a.out.write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
