"""Read-only narrow weakhold routing and fixed-cohort RL reconciliation."""
import argparse,hashlib,json,sys
from pathlib import Path
import duckdb
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--lineage',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
idx={str(r['game_id']):r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};oldpath=a.lineage/'tools/himeji/unit11_audit/audit/live-header-rows.jsonl';old={str(r['game']):r for r in map(json.loads,oldpath.read_text().splitlines())}
c=duckdb.connect();c.execute('set threads=1');parts=sorted((a.repo/'build/shenzhen/lean').glob('*.parquet'));lean=c.execute("select distinct on (game) game,R,reason,started_at from read_parquet(?,union_by_name=true) where team='7'",[list(map(str,parts))]).df().to_dict('records');(a.snapshot/'lean-own-rows.json').write_text(json.dumps(lean,indent=2)+'\n');(a.snapshot/'lean-source-hashes.json').write_text(json.dumps({str(p.relative_to(a.repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in parts},indent=2)+'\n');known=[r for r in lean if str(r['game']) in old];extra=[r for r in lean if str(r['game']) not in old];miss=[g for g in old if g not in {str(r['game']) for r in lean}]
res={'fixed_cohort_games':len(old),'old_source_sha256':hashlib.sha256(oldpath.read_bytes()).hexdigest(),'fixed_official_RL':sum(r['round_limit'] for r in old.values()),'fixed_nara_R499':sum(r['nara_last_round']>=499 for r in old.values()),'lean_overlap':len(known),'lean_overlap_R499':sum(r['R']>=499 for r in known),'lean_overlap_official_RL':sum(r['reason'] in ['queen','longest','total','tie'] for r in known),'lean_overlap_disagreements':[r for r in known if (r['R']>=499)!=old[str(r['game'])]['round_limit']],'lean_missing_old_ids':miss,'lean_current_own_games':len(lean),'lean_current_R499':sum(r['R']>=499 for r in lean),'lean_extra_rows':extra,'limitation':'401 is a peer historical aggregate with no frozen id manifest attached here. Do not attribute a three-game cause unless the identical selection can be recovered.'}
(a.snapshot/'rl-reconciliation.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ['lean_extra_rows','lean_missing_old_ids']},flush=True)
def norm(t):
 out=[]
 for line in t.strip().splitlines():
  p=line.split()
  if not p or p==['END']:continue
  if p[0]=='TILE' and len(p)==5:p=p[:3]+['_','_']
  out.append(' '.join(p))
 return out
def swap(ls):
 out=[]
 for l in ls:
  p=l.split()
  if p[0]=='DRAGON':p[1]=str(1-int(p[1]))
  out.append(' '.join(p))
 return out
maps=[];groups={}
for r in idx.values():
 if r['map_name']=='weakhold' and (r.get('started_at') or '')>='2026-10-02T04:31:00':groups.setdefault(r['map_hash'],[]).append(r)
for h,rs in sorted(groups.items()):
 r=max(rs,key=lambda r:r['started_at']);p=a.repo/'public_replays/corpus/replays'/f"{r['game_id']}.replay";payload=p.read_bytes();assert hashlib.sha256(payload).hexdigest()==r['sha256'];mt=F._reader(p).object(0,0).text(0);assert hashlib.sha256(mt.encode()).hexdigest()==h;live=norm(mt);z={'map_hash':h,'game':r['game_id'],'population_games':len(rs),'ranked_games':sum(x['ranked'] for x in rs),'source_sha256':r['sha256'],'lines':len(mt.splitlines()),'map_header':mt.splitlines()[0],'templates':[]}
 for name in ['weakhold','stronghold']:
  tp=a.repo/'maps/live'/f'{name}.map';tt=tp.read_text();n=norm(tt);z['templates'].append({'name':name,'sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),'byte_equal':mt==tt,'normalized_equal':live==n,'normalized_seat_swapped_equal':live==swap(n),'lines':len(tt.splitlines()),'map_header':tt.splitlines()[0]})
 maps.append(z)
route=(a.repo/'tools/analysis/features/run_panel.py').read_text();assert "'weakhold'" in route and "'stronghold'" not in route.split('LIVE_MAPS_M2 =',1)[1].split('GEN_MAPS',1)[0]
(a.snapshot/'weakhold-routing.json').write_text(json.dumps({'rows':maps,'run_panel_sha256':hashlib.sha256(route.encode()).hexdigest(),'selected_pool_path':'maps/live/weakhold.map','mask':'TILE final2 fields; optionalEND; compare both team assignments. Fertility values remain unverified.'},indent=2)+'\n');print('weakhold',maps,flush=True)
