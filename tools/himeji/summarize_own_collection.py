"""Reproduce coverage only from cache evidence observed before the frozen index."""
import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--rows',type=Path,required=True);ap.add_argument('--progress',type=Path,required=True);ap.add_argument('--observed-before',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
rows=list(map(json.loads,a.rows.read_text().splitlines()));eligible=[r for r in rows if r['fetched_at']<=a.observed_before and r['status']=='completed' and r['has_replay'] is True];watch=set(map(int,json.loads(a.progress.read_text())['teams']));result=[]
for label,since in [('post_m2_time_window','2026-10-02T04:31'),('oct4','2026-10-04'),('after_unit21','2026-10-04T03:26')]:
 for mode in [True,False]:
  rs=[r for r in eligible if (r['series_requested_at'] or '')>=since and r['ranked'] is mode];missing=[r for r in rs if not(r['in_index'] and r['corpus_payload'])]
  result.append(dict(window=label,ranked=mode,games=len(rs),series=len({r['series_id'] for r in rs}),missing=len(missing),missing_series=len({r['series_id'] for r in missing}),hub_recoverable=sum(r['hub_raw'] for r in missing),unknown_submission=sum(r['api_own_submission'] is None for r in rs),missing_ids=[r['game_id'] for r in missing]))
groups=[]
for mode in [True,False]:
 for watched in [True,False]:
  rs=[r for r in eligible if (r['series_requested_at'] or '')>='2026-10-04' and r['ranked'] is mode and (r['opponent_team'] in watch)==watched];groups.append(dict(ranked=mode,opponent_watched=watched,games=len(rs),missing=sum(not(r['in_index'] and r['corpus_payload']) for r in rs)))
obj=dict(observed_before=a.observed_before,excluded_later_cache_rows=len(rows)-sum(r['fetched_at']<=a.observed_before for r in rows),own_watched=7 in watch,coverage=result,watch_strata=groups,limitations='Cache subset, not census; payload paths checked at audit time. Watch membership only at freeze. Map era and bot identity not inferred from timestamps. No statistical CI for a deterministic missingness count.');a.out.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(dict(coverage=[{k:v for k,v in r.items() if k!='missing_ids'} for r in result],watch_strata=groups),indent=2))
