"""Additional event-level metrics for lineage review; no changes to bots."""
from collections import Counter
import json
from pathlib import Path
import sys
from replay import Reader


def detailed(path):
    r = Reader(path)
    root = r.object(0,0)
    teams, live, born = {}, set(), {}
    for line in root.text(0).splitlines():
        p=line.split()
        if p and p[0]=='DRAGON':
            i=len(teams);teams[i]='AB'[int(p[1])];live.add(i)
    stats={s:Counter() for s in 'AB'}
    last_action, last_round = {}, {}
    rnd, actor, updates = -1,None,0
    for e in root.items(3):
        kind,o=e.num(0,'H'),e.child(0)
        i=o.num()
        if kind==0:
            rnd=i
            for team in 'AB':
                ids=[i for i in live if teams[i]==team]
                stats[team]['peak_population']=max(stats[team]['peak_population'],len(ids))
                for bits in (6,8):
                    duplicate=len(ids)-len({i % (1 << bits) for i in ids})
                    stats[team]['peak_live_aliases_%dbit'%bits]=max(stats[team]['peak_live_aliases_%dbit'%bits],duplicate)
        elif kind==1:
            actor,updates=i,0
        elif kind==4:
            action=o.child(0)
            last_action[i]=action.num(0,'H') if o.has(0) else -1
            last_round[i]=rnd
        elif kind==9 and i==actor:
            updates+=1
            if updates>1:
                stats[teams[i]]['successful_extra_steps']+=1
        elif kind==10:
            child=o.num(4);teams[child]=teams[i];born[child]=rnd;live.add(child)
            stats[teams[i]]['births']+=1
            if rnd<100:stats[teams[i]]['births_before_100']+=1
            if rnd>=380:stats[teams[i]]['births_after_380']+=1
        elif kind==11:
            team=teams[i];cause=o.num(4,'H')
            if i in born:
                age=rnd-born[i]
                for cutoff in (0,1,3,10):
                    if age<=cutoff:stats[team]['newborn_deaths_within_%d_rounds'%cutoff]+=1
            if cause==3 and actor in teams and teams[actor]==team:
                stats[team]['friendly_head_collisions']+=1 if actor!=i else 0
                # Only the victim is counted here, so this is collision count.
            if last_action.get(i)==1 and last_round.get(i)==rnd:
                stats[team]['death_on_split_round']+=1
            live.discard(i)
    return {s:dict(st) for s,st in stats.items()}


if __name__=='__main__':
    folder=Path(sys.argv[1])
    rows=json.loads((folder/'results.json').read_text())
    output=[]
    for row in rows:
        if row.get('replay'):
            output.append(dict(map=row['map'],team_a=row['team_a'],team_b=row['team_b'],
                               replay=row['replay'],teams=detailed(folder/row['replay'])))
    (folder/'event-metrics.json').write_text(json.dumps(output,indent=2)+'\n')
    print('Analysed',len(output),'replays in',folder)
