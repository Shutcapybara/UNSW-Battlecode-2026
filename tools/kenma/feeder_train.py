"""Fit a bounded donor-action clone on legal oracle observations from teacher 306."""
from pathlib import Path
import hashlib,json,os,sys,threading,time
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(Path(__file__).parent))
from panel import check_space,monitor,STOP

def main():
    assert os.getpriority(os.PRIO_PROCESS,0)>=15
    check_space();threading.Thread(target=monitor,daemon=True).start()
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import lightgbm as lgb
    pa.set_cpu_count(1);pa.set_io_thread_count(1)
    start=time.time();out=MAIN/'build/kenma/feeder-v1';out.mkdir(exist_ok=True)
    features=(MAIN/'build/kenma/queen-action-v1/features.txt').read_text().splitlines()
    meta=['game','side','series_key','map','split','y_kind','y_death']
    t=pq.read_table(MAIN/'build/learn/kageyama/teachers_v1.parquet',columns=['game','side','team'],use_threads=False).to_pandas()
    t['team']=t.team.astype(str);t['game']=t.game.astype(str);t=t[t.team.eq('306')]
    heldout=json.loads((ROOT/'docs/learning/splits/heldout-maps.json').read_text())['heldout_maps']
    parts=[];sources=[]
    for game,g in t.groupby('game',sort=True):
        if STOP.is_set():raise RuntimeError('Resource guard stopped training')
        p=MAIN/'build/learn/kageyama/teachers_v1'/f'{game}.parquet'
        if not p.exists():continue
        d=pq.read_table(p,columns=meta+features,filters=[('x_is_queen','=',0),('blocks_src','=','oracle'),('hb_f_length','<=',8),('hb_f_vis_ally_heads','>=',1)],use_threads=False).to_pandas()
        d=d[d.side.isin(g.side)&d.split.eq('train')&d.y_kind.ne(3)]
        assert not d['map'].isin(heldout).any()
        if len(d):parts.append(d);sources.append(p.name)
    d=pd.concat(parts,ignore_index=True);del parts
    assert len(d)<=250000, 'Reassess memory budget if the source corpus changes'
    y=(d.y_kind.eq(2)|d.y_death.eq('invalid')).to_numpy(dtype=np.int32)
    val=d.series_key.map(lambda s:int(hashlib.sha256(('kenma-feeder-v1/'+str(s)).encode()).hexdigest(),16)%5==0).to_numpy()
    X=d[features].to_numpy(dtype=np.float32)
    params=dict(objective='binary',learning_rate=0.05,num_leaves=31,min_data_in_leaf=60,feature_fraction=0.8,bagging_fraction=0.8,bagging_freq=1,lambda_l2=3.0,verbosity=-1,num_threads=1,seed=73)
    def resource_callback(env):
        if STOP.is_set():raise RuntimeError('Resource guard stopped training')
    def fit(x,label):return lgb.train(params,lgb.Dataset(x,label=label,free_raw_data=True),num_boost_round=160,callbacks=[resource_callback])
    print('fit',len(d),'rows',int(y.sum()),'culls; validation',int(val.sum()),flush=True)
    model=fit(X[~val],y[~val]);p=model.predict(X[val],num_threads=1)
    thresholds={}
    for threshold in (0.5,0.9):
        pred=p>=threshold;actual=y[val].astype(bool)
        tp=int((pred&actual).sum());fp=int((pred&~actual).sum());fn=int((~pred&actual).sum());tn=int((~pred&~actual).sum())
        thresholds[str(threshold)]=dict(tp=tp,fp=fp,fn=fn,tn=tn,precision=tp/max(1,tp+fp),recall=tp/max(1,tp+fn),false_positive_rate=fp/max(1,fp+tn))
    report=dict(teacher='306',rows=len(d),culls=int(y.sum()),train_rows=int((~val).sum()),validation_rows=int(val.sum()),train_series=int(d.loc[~val,'series_key'].nunique()),validation_series=int(d.loc[val,'series_key'].nunique()),fixed_play_threshold=0.9,validation=thresholds,params=params,rounds=160,source_shards=sources,eligibility='nonqueen, length <= 8, visible allied head, oracle, original train split, no timeout action')
    model.save_model(str(out/'validation-model.txt'))
    pd.DataFrame({'series_key':d.loc[val,'series_key'],'label':y[val],'probability':p}).to_parquet(out/'validation.parquet',index=False)
    model=fit(X,y);model.save_model(str(out/'model.txt'))
    idx=np.random.default_rng(73).choice(len(d),min(20000,len(d)),replace=False)
    d.iloc[idx].to_parquet(out/'parity_rows.parquet',index=False)
    (out/'features.txt').write_text('\n'.join(features)+'\n')
    report['seconds']=round(time.time()-start,2);report['model_sha256']=hashlib.sha256((out/'model.txt').read_bytes()).hexdigest()
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='source_shards'}),flush=True);STOP.set()

if __name__=='__main__':main()
