"""Read-only canonical S-1 endpoint extract; no q.py imports, norms or store builds.
Freeze selected terminal queen rows for temporal composition checks, not causal adoption inference.
"""
import argparse, hashlib, json
from pathlib import Path
import duckdb
p=argparse.ArgumentParser();p.add_argument('--store',type=Path,required=True);p.add_argument('--index',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=True)
files=sorted((a.store/'sides').glob('part-202610*.parquet'))
con=duckdb.connect();con.execute('set threads=1');con.execute("set memory_limit='1200MB'")
con.read_parquet([str(f) for f in files],union_by_name=True,filename=True).create_view('raw')
con.read_parquet(str(a.store/'games.parquet')).create_view('games')
con.read_parquet(str(a.store/'teams.parquet')).create_view('teams')
sql="""WITH canon AS (SELECT game,min(filename) part FROM raw GROUP BY game)
SELECT s.game,s.side,s.team,s.opp,s.map,s.bot,s.opponent,s.R,s.reason,s.won,
       s.q_alive_end,s.q_end,s.q_header,g.ranked,g.series_id,g.started_at,g.map_hash,g.map_era,g.era,
       t.crank,t.cohort,ot.crank AS opp_crank,s.filename
FROM raw s JOIN canon c ON c.game=s.game AND c.part=s.filename
JOIN games g ON g.game=s.game LEFT JOIN teams t ON t.team=s.team LEFT JOIN teams ot ON ot.team=s.opp
WHERE g.map_era='post-m2' AND g.era='post' AND g.ranked
ORDER BY g.started_at,s.game,s.side"""
df=con.execute(sql).df();assert not df.duplicated(['game','side']).any()
idx={str(r['game_id']):r for r in map(json.loads,a.index.read_text().splitlines())}
checks={'rows':len(df),'games':int(df.game.nunique()),'missing_index':0,'winner_mismatch':0,'queen_header_mismatch':0,'missing_queen':0,'hash_mismatch':0,'resolved_hash_prefix':0}
for r in df.itertuples():
    m=idx.get(r.game)
    if m is None:checks['missing_index']+=1;continue
    checks['winner_mismatch']+=r.won != (0.5 if m['winner']=='draw' else float(m['winner'].upper()==r.side))
    checks['hash_mismatch']+=not m['map_hash'].startswith(r.map_hash)
    checks['resolved_hash_prefix']+=r.map_hash != m['map_hash']
    if r.q_end!=r.q_end or r.q_header!=r.q_header:checks['missing_queen']+=1
    else:checks['queen_header_mismatch']+=r.q_end!=r.q_header
assert checks['winner_mismatch']==checks['hash_mismatch']==checks['queen_header_mismatch']==0,checks
df['store_map_hash']=df.map_hash
df['map_hash']=df.game.map(lambda gid:idx[gid]['map_hash'])
df.to_json(a.out/'ranked-endpoints.jsonl',orient='records',lines=True,date_format='iso')
manifest={'sql':sql,'checks':checks,'files':[dict(name=f.name,size=f.stat().st_size,mtime_ns=f.stat().st_mtime_ns) for f in files],
          'metadata_sha256':{n:hashlib.sha256((a.store/n).read_bytes()).hexdigest() for n in ['games.parquet','teams.parquet']},
          'rows_sha256':hashlib.sha256((a.out/'ranked-endpoints.jsonl').read_bytes()).hexdigest(),
          'contract':'Earliest canonical part per game, as peer qq.py; ranked/post-m2 only. Official index winner comparison and stored header equality, not full raw replay census. No local/unranked rows.'}
(a.out/'store-extract.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(checks))
