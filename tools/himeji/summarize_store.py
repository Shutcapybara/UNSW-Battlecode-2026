"""Validate fresh labels and summarize recent opening observations by team/map/mode."""
import argparse,json
from pathlib import Path
import pandas as pd

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--store',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);a=ap.parse_args()
 g=pd.read_parquet(a.store/'games.parquet');g['game']=g.game.astype(str)
 fs=sorted((a.store/'sides').glob('part-*.parquet'));d=pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True);d.game=d.game.astype(str);assert not d.duplicated(['game','side']).any()
 d=d.merge(g[['game','ranked','winner','started_at','series_id']],on='game',validate='many_to_one')
 expected=d.apply(lambda r:'win' if r.winner==r.side.lower() else 'loss' if r.winner in ['a','b'] else 'draw' if r.winner in ['draw','tie'] else None,axis=1)
 assert (expected==d.result).all(),d[expected!=d.result][['game','side','winner','result']]
 meta=json.loads((a.snapshot/'manifest.json').read_text());top=[str(t['id']) for t in meta['top10']];chosen=d[d.team.isin(top+['7'])].copy()
 columns=['game','team','map','side','ranked','series_id','started_at','result','R','bed_pearls@50','births@50','total@50','units@50']
 chosen[columns].to_json(a.snapshot/'opening-observations.json',orient='records',indent=2)
 summary=dict(decoded_games=int(d.game.nunique()),decoded_sides=len(d),official_index_winner_matches=len(d),first_start=d.started_at.min(),last_start=d.started_at.max(),maps=sorted(d['map'].unique()),top10_sides=int(chosen.team.isin(top).sum()),own_sides=int((chosen.team=='7').sum()),per_team_map=[])
 for (team,mapname,ranked),x in chosen.groupby(['team','map','ranked']):
  summary['per_team_map'].append(dict(team=team,map=mapname,ranked=bool(ranked),games=len(x),series=x.series_id.nunique(),ended_before50=int((x.R<50).sum()),bed_pearls50_median=float(x['bed_pearls@50'].median()),births50_median=float(x['births@50'].median()),total50_median=float(x['total@50'].median()),stability='descriptive coverage sample, no stable targets'))
 (a.snapshot/'store-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='per_team_map'},indent=2))
 print(chosen[chosen['map']=='Around UNSW'][columns].to_string(index=False))
if __name__=='__main__':main()
