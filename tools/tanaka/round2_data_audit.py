from pathlib import Path
import hashlib,importlib.util,json,tempfile
import numpy as np,pandas as pd,pyarrow.parquet as pq
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');O=Path('/tmp/tanaka-r5');O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tp=R/'build/learn/kageyama/teachers_v1.parquet';sp=R/'build/learn/splits/games_split_v2.parquet';sm=R/'build/learn/kageyama/smoke.parquet'
t=pd.read_parquet(tp,columns=['game','side','team','map','series_key','split','weight']);d=pd.read_parquet(sp,columns=['game','map','series_key','split','map_era','ranked','in_scope','team_a','team_b'])
teams=set(t.team.astype(str));trainseries=set(t.series_key.astype(str));h=d[(d.split=='heldout_map')&(d.map_era=='post-m2')&d.ranked&d.in_scope&((d.team_a.astype(str).isin(teams))|(d.team_b.astype(str).isin(teams)))].copy();h['overlap']=h.series_key.astype(str).isin(trainseries)
per=[]
for mp,x in t.groupby('map'):
 te=set(x.series_key);tr=set(t.loc[t['map']!=mp,'series_key']);per.append({'map':mp,'test_sides':len(x),'test_series':len(te),'overlap_series':len(te&tr),'overlap_sides':int(x.series_key.isin(tr).sum())})
out={'teacher_file_sha':sha(tp),'split_file_sha':sha(sp),'teacher_sides':len(t),'teacher_games':int(t.game.nunique()),'teacher_series':int(t.series_key.nunique()),'duplicate_teacher_keys':int(t.duplicated(['game','side']).sum()),'teacher_split_counts':t.split.value_counts().to_dict(),'maps':int(t['map'].nunique()),'variant_named_sides':int(t['map'].isin(['Schooltime','Prisoners Dilemma']).sum()),'heldout_metadata':{'games':len(h),'series':int(h.series_key.nunique()),'games_sharing_training_series':int(h.overlap.sum()),'series_sharing_training':int(h.loc[h.overlap,'series_key'].nunique()),'side_count':int(h.team_a.astype(str).isin(teams).sum()+h.team_b.astype(str).isin(teams).sum()),'by_map':h.groupby(['map','overlap']).size().rename('n').reset_index().to_dict('records'),'scope':'Frozen metadata only; top-ten teacher-team membership, ranked/post-m2/in_scope. No action or winner labels, no decisive-only filter. Not a proposed replacement holdout draw.'},'lomo_series_overlap':per}
cols=['game','side','dragon','round','series_key','map','split','y_kind','y_first','x_cd_known','blocks_src','x_is_queen','x_length'];q=pd.read_parquet(sm,columns=cols);qm=q[(q.y_kind==0)&q.y_first.between(0,3)]
out['smoke']={'sha':sha(sm),'rows':len(q),'move_rows':len(qm),'class_counts':qm.y_first.value_counts().sort_index().to_dict(),'cd_known_counts':q.x_cd_known.value_counts().to_dict(),'blocks_src':q.blocks_src.value_counts().to_dict()}
src=R/'tools/hinata/r2_bc.py';s=importlib.util.spec_from_file_location('r2',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
# Read-only load on the existing smoke, never fit. Checks prototype's real feature/row selection.
loaded,X=m.load([sm],tp)
out['prototype']={'source_sha':sha(src),'loaded_smoke_move_rows':len(loaded),'retained_cd_unknown':int((loaded.x_cd_known==0).sum()),'n_features':len(X)}
with tempfile.TemporaryDirectory(prefix='tanaka-r2-') as td:
 td=Path(td);base=dict(game='fake',side='A',series_key='s',map='Dev',split='train',y_kind=0,y_first=0,x_is_queen=1,x_cd_known=0,x_length=3)
 pd.DataFrame([base]).to_parquet(td/'rows.parquet');pd.DataFrame([dict(game='fake',side='A',team='7',weight=1.)]*2).to_parquet(td/'teachers.parquet')
 z,_=m.load([td/'rows.parquet'],td/'teachers.parquet');out['prototype']['synthetic_duplicate_teacher_join_rows']=len(z)
 # Deterministic fold masks: same series on two maps must stay together in series5 but not LOMO.
 fd=pd.DataFrame({'game':['1','2','3','4'],'series_key':['s','s','t','u'],'map':['A','B','A','B']})
 out['prototype']['synthetic_series5_keeps_pair']=all(bool(v[0])==bool(v[1]) for v in m.folds(fd,'series5').values())
 out['prototype']['synthetic_lomo_splits_pair']=any(bool(v[0])!=bool(v[1]) for v in m.folds(fd,'lomo').values())
p=R/'build/hinata/v0/fit-lq/train_rows.parquet';v=pd.read_parquet(p,columns=['game','side','round','series_id']);out['p6_rows']={'sha':sha(p),'rows':len(v),'games':int(v.game.nunique()),'side_a_rows':int((v.side=='A').sum()),'game_side_round_duplicates':int(v.duplicated(['game','side','round']).sum())}
out['memory_float32_bytes']=3_000_000*len(X)*4;out['scope']='Teacher/split metadata, development smoke and frozen P2 training row IDs only; no new fit, bot run, or confirmation data.'
# Supplementary row-key alignment and schema guard probes, still no new labels or fit.
oofp=R/'build/hinata/v0/fit-lq/oof.parquet';qq=pd.read_parquet(oofp,columns=['game','round'])
aa=v[v.side=='A'];ak=set(zip(aa.game.astype(str),aa['round'].astype(int)));qk=set(zip(qq.game.astype(str),qq['round'].astype(int)))
out['p6_oof']={'sha':sha(oofp),'rows':len(qq),'unique_keys':len(qk),'games':int(qq.game.nunique()),'train_side_a_keys_without_oof':len(ak-qk),'oof_keys_not_in_train':len(qk-ak)}
sc=pd.read_parquet(sm,columns=['x_cd_known','x_n_beds'])
out['smoke']['cd_known_true_with_n_beds_zero']=int(((sc.x_cd_known==1)&(sc.x_n_beds==0)).sum())
out['smoke']['cd_known_true_with_visible_beds']=int(((sc.x_cd_known==1)&(sc.x_n_beds>0)).sum())
with tempfile.TemporaryDirectory(prefix='tanaka-columns-') as td:
 td=Path(td);pd.DataFrame([dict(game='fake',side='A',team='7',weight=1.)]).to_parquet(td/'t.parquet');res={}
 for name in ['x_W','x_H','x_x','x_y','x_xn','x_yn','x_width','x_facing_abs']:
  row=dict(game='fake',side='A',map='Dev',split='train',y_kind=0,y_first=0,x_is_queen=1);row[name]=60;pd.DataFrame([row]).to_parquet(td/'r.parquet')
  try:m.load([td/'r.parquet'],td/'t.parquet');res[name]='accepted'
  except AssertionError:res[name]='rejected'
 out['prototype']['identity_guard_tests']=res
out['hb1_features_source_sha']=sha(R/'bots/carthage-05-free-sprint/hb1_features.hpp')
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
