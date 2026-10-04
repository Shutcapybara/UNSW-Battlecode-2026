"""Prepare and verify opt-in own-team collection in the sole hub; never deploy or call APIs."""
import argparse,ast,difflib,hashlib,json
from datetime import datetime,timezone,timedelta
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
src=(a.repo/'tools/hub/corpus.py').read_text()
old='    out.pop(me, None)'
new='''    if c.get('include_own_team', False) and me is not None:
        me = int(me)
        out.setdefault(me, dict(id=me, target=int(c.get('own_team_games', c.get('per_team', 60))), why='own team'))
    else:
        out.pop(me, None)'''
assert src.count(old)==1;patched=src.replace(old,new)
old_refresh="    refresh = sorted((t for t in progress.values() if t['have'] >= t['target']), key=lambda t: (t.get('checked_at') or '', t.get('rank', 10**6)))"
new_refresh='''    # Freshness is independent of backfill depth. Keep the existing pass budget,
    # download cap, refresh reserve, per-team cap and executor-yield checks.
    refresh_now = datetime.now(timezone.utc)
    own_id = (cfg.get('team') or {}).get('id')
    def refresh_key(t):
        checked = t.get('checked_at')
        try:
            age = (refresh_now - datetime.fromisoformat(checked.replace('Z', '+00:00'))).total_seconds()
        except (TypeError, ValueError, AttributeError):
            age = float('inf')
        rank = t.get('rank') or 10**6
        own = c.get('include_own_team', False) and own_id is not None and t['id'] == int(own_id)
        stale_own = own and age >= float(c.get('own_refresh_priority_seconds', 900))
        stale_leader = rank <= int(c.get('refresh_priority_top_n', 10)) and age >= float(c.get('refresh_priority_seconds', 900))
        return (not stale_own, not stale_leader, checked or '', rank)
    refresh = sorted(progress.values(), key=refresh_key)'''
assert patched.count(old_refresh)==1;patched=patched.replace(old_refresh,new_refresh);ast.parse(patched)
# Extract only pure selection functions: no hub import, DB, filesystem or network side effects.
fn=next(n for n in ast.parse(patched).body if isinstance(n,ast.FunctionDef) and n.name=='watch_list');ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<watch_list>','exec'),ns);watch=ns['watch_list']
ladder=[dict(id=7,rank=80),dict(id=264,rank=1)]
base=dict(team=dict(id=7),corpus=dict(teams=[dict(id=7,games=300),dict(id=264,games=500)],top_n=1))
assert 7 not in watch(base,ladder)
cfg=dict(team=dict(id=7),corpus=dict(base['corpus'],include_own_team=True));assert set(watch(cfg,ladder))=={7,264};assert watch(cfg,ladder)[7]['target']==300
cfg2=dict(team=dict(id=7),corpus=dict(include_own_team=True,own_team_games=100));assert watch(cfg2,[])[7]['target']==100
assert watch(dict(corpus=dict(include_own_team=True)),[])=={}
block='\n'.join(line[4:] for line in new_refresh.splitlines());now=datetime.now(timezone.utc)
def stamp(m):return (now-timedelta(minutes=m)).isoformat()
progress={7:dict(id=7,have=1,target=100,rank=80,checked_at=stamp(20)),264:dict(id=264,have=499,target=500,rank=1,checked_at=stamp(25)),300:dict(id=300,have=0,target=60,rank=40,checked_at=None)}
def order():
 n=dict(datetime=datetime,timezone=timezone,c=cfg['corpus'],cfg=cfg,progress=progress);exec(block,n);return [t['id'] for t in n['refresh']]
assert order()==[7,264,300];progress[7]['checked_at']=stamp(1);assert order()==[264,300,7]
patch=''.join(difflib.unified_diff(src.splitlines(True),patched.splitlines(True),fromfile='a/tools/hub/corpus.py',tofile='b/tools/hub/corpus.py'));(a.out/'corpus-own-team.patch').write_text(patch)
result=dict(source_sha256=hashlib.sha256(src.encode()).hexdigest(),patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),checks=['default excludes own','opt-in includes own preserving explicit target','empty ladder own enabled','missing own ID safe','stale under-target own then leader','fresh own yields priority'],deployed=False,activation={'corpus.include_own_team':True},limits='Existing reserve/cap/budget/should_yield unchanged. Finite cadence priority; public discovery may lag and must be verified. Known historical missing IDs need separate bounded backfill through sole collector.')
(a.out/'collector-repair-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
