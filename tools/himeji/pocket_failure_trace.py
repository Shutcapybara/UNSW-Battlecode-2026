"""Explain every heldout late queen death and non-length3 survivor; replay only."""
import argparse,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
rows=list(map(json.loads,(a.snapshot/'pocket-rows.jsonl').read_text().splitlines()));targets=[]
for r in rows:
    if not r['cohort']:continue
    for s in r['sides']:
        d=s['queen_death']
        if (d and d['round']>0) or (s['final']['queen'] and s['final']['queen']!=3):targets.append((r,s))
out=[]
for gid in sorted({r['game'] for r,s in targets}):
    p=a.repo/'public_replays/corpus/replays'/f'{gid}.replay';g=F.decode(p)
    for r,s in targets:
        if r['game']!=gid:continue
        q=s['queen'];d=s['queen_death'];end=d['round'] if d else g['last_round'];splits=[e for e in g['events']['splits'] if e['parent']==q];food=[e for e in g['events']['eats'] if e['id']==q]
        checkpoints=sorted(set([max(0,end-3),max(0,end-2),max(0,end-1),end]+[e['round'] for e in splits if e['round']>0]))
        out.append({'game':gid,'team':s['team'],'side':s['side'],'queen':q,'death':d,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'food':food,'splits':splits,'charged_moves':[e for e in g['events']['actions'] if e['id']==q and e.get('paid',0)>0],'last_actions':[e for e in g['events']['actions'] if e['id']==q and e['round']>=end-4],'states':[{'round':t,'queen':g['rounds'][t].get(q),'team_units':sum(team==s['side'] for team,b in g['rounds'][t].values()),'pearls_in_spawn_component':[c for c in s['spawn_body'] if tuple(c) in g['pearls'][t]]} for t in checkpoints]})
(a.snapshot/'pocket-failure-traces.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
