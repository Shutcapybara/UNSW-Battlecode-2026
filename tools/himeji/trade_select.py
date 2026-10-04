"""Freeze a small ranked fullhash/seat/time-matched trade cohort, without outcomes."""
import argparse,collections,datetime,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);a=p.parse_args();p=a.snapshot
idx=[json.loads(x) for x in (p/'index.jsonl').read_text().splitlines()];lad=json.loads((p/'ladder.json').read_text());top={t['id'] for t in lad if t.get('rank') is not None and 1<=t['rank']<=10};maps={'Around UNSW','Australia','Islands'}
rows=[m for m in idx if m['ranked'] and m['started_at']>='2026-10-04T00:00:00' and m.get('header_map_name',m['map_name']) in maps]
def ts(m):return datetime.datetime.fromisoformat(m['started_at'].replace('Z','+00:00')).timestamp()
fields=collections.defaultdict(list)
for m in rows:
    if 7 in (m['team_a'],m['team_b']):continue
    for side in 'AB':
        if m['team_'+side.lower()] in top:fields[(m['map_hash'],side)].append(m)
pairs=[];missing=[];used=set()
for name in sorted(maps):
    n=0;ser=set()
    own=[m for m in rows if m.get('header_map_name',m['map_name'])==name and 7 in (m['team_a'],m['team_b'])]
    for m in sorted(own,key=lambda m:m['started_at'],reverse=True):
        side='A' if m['team_a']==7 else 'B'
        if m['series_id'] in ser:continue
        cand=[x for x in fields[(m['map_hash'],side)] if abs(ts(x)-ts(m))<=7200 and x['game_id'] not in used]
        if not cand:missing.append(m['game_id']);continue
        f=min(cand,key=lambda x:(abs(ts(x)-ts(m)),x['game_id']))
        pairs.append(dict(pair=len(pairs),map=name,map_hash=m['map_hash'],side=side,us=m,field=f,field_team=f['team_'+side.lower()],delta_minutes=abs(ts(f)-ts(m))/60));used.add(f['game_id']);ser.add(m['series_id']);n+=1
        if n==12:break
out=dict(contract='Ranked4Oct00Z onwards; latest12 own series/map with a unique non-own field game from frozen top10 within120min at identical fullmaphash and seat, nearest time then ID tie break; no outcome filter. Opponents unmatched.',ladder_top10=sorted(top),pairs=pairs,unmatched_considered_own=missing)
(p/'trade-selection.json').write_text(json.dumps(out,indent=2)+'\n')
print('top',sorted(top),'pairs',collections.Counter(x['map'] for x in pairs),'missing',len(missing),'maxmin',max(x['delta_minutes'] for x in pairs))
