"""Small queen-only action clone; legal HB-1 inputs, keeper teachers, series-held-out check.
Seven classes: F, R, B, L, split-2, retain-2, split-half. No identity or map inputs.
Fixed budget: 128 rounds x 15 leaves, one thread, to fit beside the deployed prior.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import threading

ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(Path(__file__).parent))
from panel import check_space, monitor, STOP


def main():
    assert os.getpriority(os.PRIO_PROCESS,0)>=15
    check_space()
    threading.Thread(target=monitor,daemon=True).start()
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import lightgbm as lgb
    pa.set_cpu_count(1); pa.set_io_thread_count(1)
    out=MAIN/'build/kenma/queen-action-v1'; out.mkdir(parents=True,exist_ok=True)
    features=(MAIN/'build/kenma/a1/features.txt').read_text().splitlines()
    meta=['game','side','series_key','map','split','x_is_queen','blocks_src','y_kind','y_first','y_child','y_parent','y_nsteps','hb_pF','hb_pR','hb_pL']
    teachers=pd.read_parquet(MAIN/'build/learn/kageyama/teachers_v1.parquet',columns=['game','side','team'])
    teachers['game']=teachers.game.astype(str); teachers['team']=teachers.team.astype(str)
    keepers=['91','213','507','842','55']
    teachers=teachers[teachers.team.isin(keepers)]
    assert not teachers.duplicated(['game','side']).any()
    games=set(teachers.game)
    parts=[]; used=[]; t0=time.time()
    for i,p in enumerate(sorted((MAIN/'build/learn/kageyama/teachers_v1').glob('*.parquet'))):
        if STOP.is_set(): raise RuntimeError('Resource or user stop')
        if p.stem not in games: continue
        d=pq.read_table(p,columns=meta+features,filters=[('x_is_queen','=',1),('blocks_src','=','oracle'),('y_kind','in',[0,1])],use_threads=False).to_pandas()
        if len(d)==0:continue
        d['game']=d.game.astype(str)
        d=d.merge(teachers,on=['game','side'],how='inner')
        if len(d): parts.append(d); used.append(p.name)
        if len(used)%25==0: print('loaded',len(used),'shards',sum(map(len,parts)),'queen turns',flush=True)
    d=pd.concat(parts,ignore_index=True); del parts
    assert d.split.eq('train').all()
    heldout=json.loads((ROOT/'docs/learning/splits/heldout-maps.json').read_text())['heldout_maps']
    assert not d['map'].isin(heldout).any()
    move=(d.y_kind==0)&d.y_first.between(0,3)
    split=(d.y_kind==1)&(d.y_child>=2)&(d.y_parent>=2)
    d=d[move|split].reset_index(drop=True)
    y=np.where(d.y_kind==0,d.y_first,np.where(d.y_child==2,4,np.where(d.y_parent==2,5,6))).astype(np.int32)
    val=d.series_key.map(lambda s:int(hashlib.sha256(('kenma-queen-v1/'+str(s)).encode()).hexdigest(),16)%5==0).to_numpy()
    X=d[features].to_numpy(np.float32)
    params=dict(objective='multiclass',num_class=7,learning_rate=0.06,num_leaves=15,min_data_in_leaf=40,
                feature_fraction=0.8,bagging_fraction=0.8,bagging_freq=1,lambda_l2=2.0,verbosity=-1,num_threads=1,seed=73)
    print('fit',len(d),'rows','validation',int(val.sum()),flush=True)
    train=lgb.Dataset(X[~val],label=y[~val],free_raw_data=True)
    model=lgb.train(params,train,num_boost_round=128)
    pred=model.predict(X[val],num_threads=1).argmax(axis=1)
    eval_y=y[val]
    counts=np.bincount(y[~val],minlength=7)
    result=dict(teachers=keepers,rows=len(d),train_rows=int((~val).sum()),validation_rows=int(val.sum()),
        train_series=int(d.loc[~val,'series_key'].nunique()),validation_series=int(d.loc[val,'series_key'].nunique()),
        validation_accuracy=float((pred==eval_y).mean()),majority_accuracy=float((eval_y==counts.argmax()).mean()),
        classes={str(k):int(v) for k,v in enumerate(np.bincount(y,minlength=7))},params=params,rounds=128,
        per_class={str(k):dict(n=int((eval_y==k).sum()),recall=float((pred[eval_y==k]==k).mean()) if (eval_y==k).any() else None) for k in range(7)},
        phases={str(lo):dict(n=int(((d.loc[val,'hb_f_round']>=lo)&(d.loc[val,'hb_f_round']<hi)).sum()),accuracy=float((pred[((d.loc[val,'hb_f_round']>=lo)&(d.loc[val,'hb_f_round']<hi)).to_numpy()]==eval_y[((d.loc[val,'hb_f_round']>=lo)&(d.loc[val,'hb_f_round']<hi)).to_numpy()]).mean())) for lo,hi in [(0,100),(100,250),(250,500)]},
        source_shards=used,feature_order=features,seconds=round(time.time()-t0,1))
    model.save_model(str(out/'validation-model.txt'))
    del train
    # Refit the fixed configuration for deployment; validation metric above remains untouched.
    model=lgb.train(params,lgb.Dataset(X,label=y,free_raw_data=True),num_boost_round=128)
    model.save_model(str(out/'model.txt'))
    d.iloc[:min(20000,len(d))].to_parquet(out/'parity_rows.parquet',index=False)
    (out/'features.txt').write_text('\n'.join(features)+'\n')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_shards','feature_order']}),flush=True)
    STOP.set()

if __name__=='__main__':main()
