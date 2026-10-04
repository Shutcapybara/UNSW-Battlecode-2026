"""Read-only checkpoint audit. Series sibling IDs are availability, never copied winners/maps."""
import argparse, collections, hashlib, json, sqlite3
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--hub',type=Path,required=True);ap.add_argument('--index',type=Path,required=True);ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
index={int(r['game_id']):r for r in map(json.loads,a.index.read_text().splitlines())}
c=sqlite3.connect(f'file:{a.hub / "hub.sqlite"}?mode=ro&immutable=1',uri=True);c.execute('pragma query_only=on')
rows=c.execute('select series_id,payload,fetched_at from series order by fetched_at').fetchall(); games={}; conflicts=[]
for key,payload,fetched in rows:
 p=json.loads(payload);m=p.get('match') or p
 if 7 not in (m.get('teamAId'),m.get('teamBId')): continue
 for g in p.get('games') or []:
  if not isinstance(g,dict) or not g.get('id'):continue
  gid=int(g['id']); mode=m.get('ranked');sid=m.get('seriesId')
  row=dict(game_id=gid,series_id=sid,ranked=mode,opponent_team=m.get('teamBId') if m.get('teamAId')==7 else m.get('teamAId'),series_requested_at=m.get('requestedAt'),snapshot_game_id=m.get('id'),status=g.get('status'),has_replay=g.get('hasReplay'),fetched_at=fetched,api_own_submission=m.get('submissionAId') if m.get('teamAId')==7 else m.get('submissionBId'),in_index=gid in index,corpus_payload=(a.corpus/'replays'/f'{gid}.replay').exists(),hub_raw=(a.hub/'replays/raw'/f'{gid}.replay').exists())
  if gid in games and (games[gid]['series_id'],games[gid]['ranked'])!=(sid,mode):conflicts.append(gid)
  games[gid]=row
outrows=sorted((r for r in games.values() if (r['series_requested_at'] or '')>='2026-10-02T04:31'),key=lambda r:r['game_id']); (a.out/'cached-own-games.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in outrows))
summaries=[]
for label,since in [('post_m2_time_window','2026-10-02T04:31'),('oct4','2026-10-04'),('after_unit21','2026-10-04T03:26')]:
 for mode in [True,False,None]:
  selected=[r for r in outrows if (r['series_requested_at'] or '')>=since and r['ranked'] is mode and r['status']=='completed' and r['has_replay'] is True]
  missing=[r for r in selected if not(r['in_index'] and r['corpus_payload'])]
  summaries.append(dict(window=label,ranked=mode,listed_completed_replays=len(selected),series=len({r['series_id'] for r in selected}),missing_index_or_payload=len(missing),missing_series=len({r['series_id'] for r in missing}),recoverable_hub_raw=sum(r['hub_raw'] for r in missing),missing_api_own_submission=sum(r['api_own_submission'] is None for r in selected),latest_series_requested=max((r['series_requested_at'] for r in selected),default=None),missing_ids=[r['game_id'] for r in missing]))
summary=dict(index_sha256=hashlib.sha256(a.index.read_bytes()).hexdigest(),index_games=len(index),index_own=sum(7 in (r.get('team_a'),r.get('team_b')) for r in index.values()),latest_index_own=max((r.get('started_at') or '' for r in index.values() if 7 in (r.get('team_a'),r.get('team_b')))),db_series_rows=len(rows),db_series_latest=max(r[2] for r in rows),db_games=c.execute('select count(*),max(requested_at),max(ingested_at) from games').fetchone(),submissions=c.execute('select id,status,last_seen from submissions where id in (14585,14265)').fetchall(),conflicts=conflicts,coverage=summaries,limitations='Immutable read-only DB checkpoint excludes WAL; cached listing is not a server census. Time windows do not certify replay map era. Sibling maps, winners and submission identities remain unknown. Counts are observed missingness, no binomial sampling interval.')
(a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='coverage'},indent=2))
