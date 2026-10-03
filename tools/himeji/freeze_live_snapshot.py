"""Freeze one complete-line corpus index and ladder/progress for repeatable analysis. No API calls."""
import argparse,datetime,hashlib,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 assert not (a.out/'index.jsonl').exists(), 'Choose a new output directory; freezes are immutable'
 raw=(a.corpus/'index.jsonl').read_bytes();raw=raw[:raw.rfind(b'\n')+1];rows={r['game_id']:r for r in map(json.loads,raw.splitlines())};lad=sorted((a.corpus/'ladder').glob('*.json'))[-1];lb=lad.read_bytes();ld=json.loads(lb);progress=(a.corpus/'teams.json').read_bytes();json.loads(progress)
 (a.out/'index.jsonl').write_bytes(raw);(a.out/'ladder.json').write_bytes(lb);(a.out/'collection-progress.json').write_bytes(progress)
 manifest=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),index_sha256=hashlib.sha256(raw).hexdigest(),index_games=len(rows),latest_start=max(r.get('started_at') or '' for r in rows.values()),ladder=lad.name,ladder_sha256=hashlib.sha256(lb).hexdigest(),top10=sorted([r for r in ld if r.get('rank') and r['rank']<=10 and not r.get('dev')],key=lambda r:r['rank']),collector_progress_at=json.loads(progress)['at'])
 (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
