"""Matched fixed-fixture reading of the completed Portals mechanism audit."""
import argparse,collections,json
from pathlib import Path
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
rows=list(map(json.loads,(a.out/'rome-trigger-rows.jsonl').read_text().splitlines()))
assert len(rows)==192==len({(r['panel'],r['bot'],r['game']) for r in rows})
result={'method':'Portals selected after reported loss. Fixed matched fixture expected-score deltas; 5000 opponent-seat block bootstrap draws preserving 3 seeds, central95%, seed115. Descriptive diagnostics only, not heldout confirmation or field targets.','panels':[]}
pairs=[]
for panel in ['z1','gen']:
    rr=[r for r in rows if r['panel']==panel]
    by={bot:{tuple(r['fixture']):r for r in rr if r['bot']==bot} for bot in ['rome-01-nodevil','rome-03-queen-state-convert']}
    pa=by['rome-01-nodevil'];ca=by['rome-03-queen-state-convert'];assert set(pa)==set(ca) and len(pa)==48
    arms=[]
    for bot in by:
        rs=list(by[bot].values());tr=[r for r in rs if r['first_trigger']]
        arms.append({'bot':bot,'games':len(rs),'triggered':len(tr),'live_queen_first_trigger':sum(r['first_trigger']['queen_alive'] for r in tr),'dead_queen_first_trigger':sum(not r['first_trigger']['queen_alive'] for r in tr),'never_triggered':len(rs)-len(tr),'eligible_actions':sum(r['eligible_actions'] for r in rs),'dead_queen_eligible_actions':sum(r['dead_queen_eligible_actions'] for r in rs),'score_points':sum(r['score'] for r in rs),'queen490_alive':sum((r['queen490'] or 0)>0 for r in rs),'reached490':sum(r['reached490'] for r in rs),'final_longest_mean':float(np.mean([r['final']['longest'] for r in rs]))})
    block=collections.defaultdict(list);deltas=[];dead_deltas=[];mismatch=[]
    for key in sorted(pa):
        p,c=pa[key],ca[key];d=c['score']-p['score'];deltas.append(d);block[(key[2],key[3])].append(d)
        if p['first_trigger']!=c['first_trigger']:mismatch.append(key)
        pred=bool(p['first_trigger'] and not p['first_trigger']['queen_alive'])
        if pred:dead_deltas.append(d)
        pairs.append({'panel':panel,'fixture':key,'parent_first_trigger':p['first_trigger'],'candidate_first_trigger':c['first_trigger'],'parent_dead_queen_trigger':pred,'d_score':d,'parent_score':p['score'],'candidate_score':c['score'],'parent_final_longest':p['final']['longest'],'candidate_final_longest':c['final']['longest'],'parent_queen490':p['queen490'],'candidate_queen490':c['queen490'],'parent_reason':p['reason'],'candidate_reason':c['reason']})
    values=list(block.values());assert len(values)==16 and all(len(v)==3 for v in values);rng=np.random.default_rng(115);means=np.array([sum(v)/len(v) for v in values]);boot=means[rng.integers(0,len(means),(5000,len(means)))].mean(axis=1)
    result['panels'].append({'panel':panel,'paired_games':48,'blocks':16,'arms':arms,'trigger_mismatches':mismatch,'d_score':float(np.mean(deltas)),'d_score_ci95_opponent_seat':np.quantile(boot,[.025,.975]).tolist(),'parent_dead_queen_trigger_pairs':len(dead_deltas),'dead_queen_pairs_d_score':float(np.mean(dead_deltas)) if dead_deltas else None,'queen_alive_at_first_trigger_pairs':sum(p['first_trigger'] is not None and p['first_trigger']['queen_alive'] for p in pa.values()),'index_winner_disagreements':sum(r['index_winner']!=r['winner'] for r in rr)})
(a.out/'rome-trigger-summary.json').write_text(json.dumps(result,indent=2)+'\n');(a.out/'rome-trigger-pairs.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in pairs));print(json.dumps(result,indent=2))
