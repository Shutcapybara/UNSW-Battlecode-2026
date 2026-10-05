from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');W=Path('/Users/alik/Documents/Projects/wt-asahi');O=Path('/tmp/tanaka-r13');O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
key=['game','side','dragon','round','turn'];base=None;hits={};metrics={};files={};frl=np.array([0,1,3])
for dr in ['A0-u','A1-u','A3-u']:
 p=R/'build/hinata/r2/battery'/dr;d=pd.read_parquet(p/'rows.parquet');idx=pd.MultiIndex.from_frame(d[key]);assert idx.is_unique
 if base is None:base=d;bi=idx
 assert set(idx)==set(bi);order=pd.Series(np.arange(len(d)),index=idx).loc[bi].to_numpy();d=d.iloc[order].reset_index(drop=True)
 assert all(np.array_equal(d[c],base[c]) for c in ['y_first','fold','series_key'])
 mask=d.y_first.isin(frl).to_numpy();reg=json.loads((p/'registry.json').read_text());files[dr]={'rows':sha(p/'rows.parquet'),'registry':sha(p/'registry.json')}
 for arm in reg['arms']:
  P=np.load(p/f'p_{arm}.npy')[order];assert np.isfinite(P).all() and (P>=0).all() and np.allclose(P.sum(1),1,atol=1e-3)
  hit=frl[P[:,frl].argmax(1)]==d.y_first.to_numpy();hits[arm]=hit
  g=pd.DataFrame({'s':d.series_key,'h':hit&mask,'n':mask}).groupby('s')[['h','n']].sum();ix=np.random.default_rng(7).integers(0,len(g),(1000,len(g)));bs=g.h.to_numpy()[ix].sum(1)/g.n.to_numpy()[ix].sum(1)
  metrics[arm]={'accuracy':float(hit[mask].mean()),'ci90':np.percentile(bs,[5,95]).tolist(),'sha':sha(p/f'p_{arm}.npy')}
diffs={}
for a,b in [('A1-400','A0'),('A1-400','A3-400'),('A1-800','A1-400')]:
 g=pd.DataFrame({'s':base.series_key,'d':(hits[a].astype(float)-hits[b].astype(float))*mask,'n':mask}).groupby('s')[['d','n']].sum();ix=np.random.default_rng(7).integers(0,len(g),(1000,len(g)));bs=g.d.to_numpy()[ix].sum(1)/g.n.to_numpy()[ix].sum(1);diffs[f'{a} minus {b}']={'delta':float(g.d.sum()/g.n.sum()),'ci90':np.percentile(bs,[5,95]).tolist()}
# Published development fold manifest: source metadata and pinned shard-manifest counts only.
fp=R/'docs/learning/splits/PROPOSED-hinata-full-rows-folds.json';f=json.loads(fp.read_text());sp=R/f['source']['shards'];assert sha(sp)==f['source']['shards_manifest_sha256'];sm=json.loads(sp.read_text())
T=pd.read_parquet(R/'build/learn/kageyama/teachers_v1.parquet',columns=['game','series_key']);assert T.groupby('game').series_key.nunique().max()==1;gs=T.drop_duplicates('game').set_index('game').series_key.to_dict();gs={str(k):str(v) for k,v in gs.items()}
seriesfold=f['series_to_fold'];assert all(v=='f'+str(int(hashlib.sha256(('hinata-r2/'+s).encode()).hexdigest(),16)%5) for s,v in seriesfold.items())
per={k:{'series':set(),'games':0,'rows_all':0} for k in f['per_fold']}
for name,info in sm['shard_detail'].items():
 s=gs[Path(name).stem];k=seriesfold[s];per[k]['series'].add(s);per[k]['games']+=1;per[k]['rows_all']+=info['rows']
for k,v in per.items():v['series']=len(v['series'])
assert all(per[k]['series']==f['per_fold'][k]['series'] and per[k]['games']==f['per_fold'][k]['games'] for k in per)
assert all(int(v)==int(f['per_fold'][k].get('rows_all',f['per_fold'][k].get('rows'))) for k,dct in per.items() for v in [dct['rows_all']])
assert all(seriesfold[str(s)]==fold for s,fold in zip(base.series_key,base.fold))
C=pd.read_parquet(R/'build/learn/kageyama/r2_confirm_cohort_v1.parquet',columns=['game','series_key']);assert not(set(gs.values())&set(C.series_key.astype(str)))
# Independent summation and timing arithmetic of the completed Asahi benchmark; no re-execution.
SNAP=Path(__file__).resolve().parents[2]/'docs/learning/reviews/tanaka-round13'
p=SNAP/'throughput-d061c.json';j=json.loads(p.read_text());modes={}
for mode in ['engine','encode','net']:
 m=j[mode];rr=m['rows'];assert len(rr)==m['tasks']==80 and len({v['worker'] for v in rr})==80 and not any(v.get('error') for v in rr)
 sums={k:sum(v[k] for v in rr) for k in ['decisions','games','rounds','seconds','t_enc','t_net']};assert sums['decisions']==m['decisions'] and sums['games']==m['games']
 rate=sums['decisions']/m['wall_seconds']*3600
 # Raw aggregate wall is rounded to 0.1s; reported rate is calculated before rounding.
 implied=sums['decisions']/m['per_hour']*3600;assert abs(implied-m['wall_seconds'])<=.05
 modes[mode]={'tasks':len(rr),'sum':sums,'rounded_wall_seconds':m['wall_seconds'],'per_hour_from_rounded_wall':rate,'reported_per_hour':m['per_hour'],'implied_unrounded_wall':implied,'mean_rounds':sums['rounds']/sums['games'],'decisions_per_round':sums['decisions']/sums['rounds'],'time_us':{'busy':sums['seconds']/sums['decisions']*1e6,'encoder':sums['t_enc']/sums['decisions']*1e6,'net':sums['t_net']/sums['decisions']*1e6}}
out={'scope':'Published A1/A0/A3 development outputs; full-fold source metadata; completed throughput row summaries. No fit, bot execution, real selection or live/confirmation outcome read.','support':{'moves':len(base),'FRL':int(mask.sum()),'games':int(base.game.nunique()),'series':int(base.series_key.nunique()),'teams':int(base.team.nunique()),'maps':int(base['map'].nunique())},'metrics':metrics,'paired':diffs,'files':files,'folds':{'sha':sha(fp),'source_manifest_sha':sha(sp),'per_fold':per,'series':len(seriesfold),'dev_series_keep_fold':True,'cohort_series_overlap':0},'throughput':{'source_sha':sha(SNAP/'throughput.py'),'result_sha':sha(p),'modes':modes,'recorded_worker_processes':8,'recorded_host_logical_cpus':j['host']['cpus'],'historical_blas_thread_limit_or_process_cpu_time_in_receipt':False}}
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
