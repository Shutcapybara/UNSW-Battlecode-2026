"""Recover meals on selected attacks exceeding the food-free budget; read-only replay query."""
import argparse,json,sys
from pathlib import Path
main=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');sys.path.insert(0,str(main));from tools.analysis.features import frame as F
ap=argparse.ArgumentParser();ap.add_argument('--audit-dir',type=Path,required=True);args=ap.parse_args();s=args.audit_dir;rs=json.loads((s/'strike-audit.json').read_text())['rows'];extra=[]
for row in rs:
 L=row['killer_turn_start']['killer_length'];S=row['killer_action']['steps'];B=(L+3)//4+L-2
 if S<=B:continue
 g=F.decode(main/'public_replays/corpus/replays'/f"{row['game']}.replay");k=row['killer'];r=row['death']['round'];extra.append(dict(game=row['game'],killer=k,round=r,turn_start_length=L,commanded_steps=S,nofood_movement_budget=B,eats=[e for e in g['events']['eats'] if e['id']==k and e['round']==r],killer_death=next(d for d in g['events']['deaths'] if d['id']==k)))
(s/'food-extension.json').write_text(json.dumps(extra,indent=2)+'\n');print([(x['game'],x['turn_start_length'],x['commanded_steps'],len(x['eats'])) for x in extra])
