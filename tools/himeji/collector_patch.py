"""Prepare, do not deploy, a focused refresh-starvation fix against current collector source."""
import argparse,ast,difflib,hashlib,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
src=(a.repo/'tools/hub/corpus.py').read_text()
old="    refresh = sorted((t for t in progress.values() if t['have'] >= t['target']), key=lambda t: (t.get('checked_at') or '', t.get('rank', 10**6)))"
new="""    # Refresh is about freshness, not historical depth. Teams below a backfill
    # target still need their newest page checked (otherwise new low-depth teams
    # can indefinitely starve a leader just short of its target).
    refresh_now = datetime.now(timezone.utc)
    def refresh_key(t):
        checked = t.get('checked_at')
        try:
            age = (refresh_now - datetime.fromisoformat(checked.replace('Z', '+00:00'))).total_seconds()
        except (TypeError, ValueError, AttributeError):
            age = float('inf')
        rank = t.get('rank') or 10**6
        stale_leader = rank <= int(c.get('refresh_priority_top_n', 10)) and age >= float(c.get('refresh_priority_seconds', 900))
        return (not stale_leader, checked or '', rank)
    refresh = sorted(progress.values(), key=refresh_key)"""
assert src.count(old)==1;patched=src.replace(old,new);ast.parse(patched)
(a.out/'corpus-refresh-priority.patch').write_text(''.join(difflib.unified_diff(src.splitlines(True),patched.splitlines(True),fromfile='a/tools/hub/corpus.py',tofile='b/tools/hub/corpus.py')))
# Exercise just the pure selection block: no imports or collector writes/API calls.
block='\n'.join(line[4:] for line in new.splitlines())
from datetime import datetime,timezone,timedelta
now=datetime.now(timezone.utc)
def stamp(minutes):return (now-timedelta(minutes=minutes)).isoformat()
progress={1:dict(id=1,have=2990,target=3000,rank=2,checked_at=stamp(1800)),2:dict(id=2,have=10,target=500,rank=40,checked_at=None),3:dict(id=3,have=500,target=500,rank=3,checked_at=stamp(1)),4:dict(id=4,have=500,target=500,rank=41,checked_at=stamp(30))}
ns=dict(datetime=datetime,timezone=timezone,c={},progress=progress);exec(block,ns);order=[x['id'] for x in ns['refresh']];assert order==[1,2,4,3],order
progress[1]['checked_at']=stamp(1);ns=dict(datetime=datetime,timezone=timezone,c={},progress=progress);exec(block,ns);order2=[x['id'] for x in ns['refresh']];assert order2[0]==2
out=dict(source_sha256=hashlib.sha256(src.encode()).hexdigest(),stale_under_target_leader_first=order,fresh_leader_does_not_starve_other_teams=order2,syntax='pass',deployed=False)
(a.out/'collector-patch-check.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
