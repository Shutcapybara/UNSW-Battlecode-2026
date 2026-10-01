"""Read-only S-1 opening references; never imports q.py or writes shared norms.

python ranked_store_refs.py --store MAIN/build/s1/corpus --ladder SNAPSHOT --out SCRATCH
Re-run with the same out directory to summarize frozen extracted rows only.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--store',type=Path,required=True)
    ap.add_argument('--ladder',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--boot',type=int,default=1000);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    frozen=a.out/'opening-rows.csv'
    if not frozen.exists():
        c=duckdb.connect();c.execute('set threads=1');c.execute("set memory_limit='700MB'")
        c.execute("set temp_directory='"+str(a.out.resolve()/'spill').replace("'","''")+"'")
        c.execute('create table g as select * from read_parquet(?)',[str(a.store/'games.parquet')])
        inv=c.execute("select era,ranked,count(*) n,cast(min(started_at) as varchar) first_start,cast(max(started_at) as varchar) last_start from g group by all").df().to_dict('records')
        c.execute('create table canon as select s.game,min(filename) part from read_parquet(?,union_by_name=true,filename=true) s join g using(game) where g.era=\'post\' group by s.game',[str(a.store/'sides/part-*.parquet')])
        files=[r[0].replace('/sides/','/series/') for r in c.execute('select distinct part from canon').fetchall()]
        before={p:dict(size=Path(p).stat().st_size,mtime_ns=Path(p).stat().st_mtime_ns) for p in files}
        sql="""select s.game,s.side,s.team,s.map,s.round,s.ended,g.ranked,g.series_id,
          cast(g.started_at as varchar) started_at,
          coalesce(s.c_eats_bed,0) bed_eats,coalesce(s.c_splits,0) splits,
          coalesce(s.c_transits,0) transits,s.territory,s.units,s.total,
          coalesce(s.c_eats_bed,0)/nullif(s.c_bed_spawns,0) bed_capture
          from read_parquet(?,union_by_name=true,filename=true) s
          join canon k on k.game=s.game and replace(s.filename,'/series/','/sides/')=k.part
          join g on g.game=s.game where s.round in (25,50)"""
        d=c.execute(sql,[files]).df()
        assert not d.duplicated(['game','side','round']).any()
        assert (d.groupby(['game','round']).size()==2).all()
        assert d.series_id.notna().all()
        assert before=={p:dict(size=Path(p).stat().st_size,mtime_ns=Path(p).stat().st_mtime_ns) for p in files}
        ladderraw=a.ladder.read_bytes();lad=json.loads(ladderraw)
        top=[str(r['id']) for r in lad if not r.get('dev') and r.get('rank') is not None and r['rank']<=10]
        assert len(top)==10
        d['top10']=d.team.astype(str).isin(top);d.to_csv(frozen,index=False)
        manifest=dict(store=str(a.store),games_sha256=hashlib.sha256((a.store/'games.parquet').read_bytes()).hexdigest(),
          ladder=a.ladder.name,ladder_sha256=hashlib.sha256(ladderraw).hexdigest(),top10_ids=top,
          indexed_eras=inv,canonical_post_games=int(d.game.nunique()),post_series_files=before,
          cohorts=d[d['round']==50].groupby('ranked').agg(games=('game','nunique'),sides=('side','size'),series=('series_id','nunique'),top10_sides=('top10','sum')).reset_index().to_dict('records'),
          first_start=d.started_at.min(),last_start=d.started_at.max(),
          opening_rows_sha256=hashlib.sha256(frozen.read_bytes()).hexdigest(),
          method='earliest filename per game; both sides; post-era; separate ranked/unranked; terminal state carry included and counted')
        (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        (a.out/'source-query.sql').write_text(sql+'\n')
        print(json.dumps({k:v for k,v in manifest.items() if k!='post_series_files'}),flush=True)
    d=pd.read_csv(frozen,dtype={'game':str,'team':str});d=d[d.ranked].copy()
    metrics=['bed_eats','bed_capture','splits','transits','territory','units','total']
    rng=np.random.default_rng(8123);out=[]
    for (m,cp),x in d.groupby(['map','round']):
        x=x.reset_index(drop=True);groups=[v.index.to_numpy() for _,v in x.groupby('series_id')]
        samples=[np.concatenate([groups[i] for i in rng.integers(0,len(groups),len(groups))]) for _ in range(a.boot)]
        for metric in metrics:
            values=x[metric].to_numpy(float);top=x.top10.to_numpy(bool)
            def measure(ix):
                f=values[ix];t=f[top[ix]];f=f[np.isfinite(f)];t=t[np.isfinite(t)]
                if len(t)==0:return (np.nan,np.nan)
                med=float(np.median(t));return med,float(np.mean(f<med)+.5*np.mean(f==med))
            med,pct=measure(np.arange(len(x)));boots=np.array([measure(ix) for ix in samples])
            valid=np.isfinite(boots[:,1]);nvalid=int(valid.sum())
            ci=np.quantile(boots[valid,1],[.025,.975]).tolist() if nvalid else [None,None]
            out.append(dict(era='post',population='ranked',map=m,round=int(cp),metric=metric,
              field_games=x.game.nunique(),field_sides=len(x),field_series=len(groups),
              field_finite=int(np.isfinite(values).sum()),ended_sides=int(x.ended.sum()),
              top10_sides=int(top.sum()),top10_series=x.loc[top,'series_id'].nunique(),top10_teams=x.loc[top,'team'].nunique(),
              field_median=float(np.nanmedian(values)),top10_median=med,top10_field_mid_percentile=pct,
              percentile_ci95_low=ci[0],percentile_ci95_high=ci[1],bootstrap_valid=nvalid,bootstrap_total=a.boot,
              stability='provisional; historical post window, current cohort; time stability not checked',
              us_sides=0,top10_minus_us=None))
        print('summarized',m,int(cp),'field',len(x),'top10',int(x.top10.sum()),flush=True)
    pd.DataFrame(out).to_csv(a.out/'ranked-references.csv',index=False)
    (a.out/'reference-method.json').write_text(json.dumps(dict(seed=8123,replicates=a.boot,confidence=.95,
      bootstrap='whole series within map, both sides retained; same draw defines field and its top10 subset',
      percentile='midrank: mean(field < top10 median) + 0.5*mean(field == top10 median)',
      caveats=['current top10 membership applied retrospectively','collector/in-scope selection','terminal carry counted','no live-us rows in store','no temporal validation']),indent=2)+'\n')


if __name__=='__main__':main()
