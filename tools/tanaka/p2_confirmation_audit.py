"""Synthetic confirmation safeguards and metadata-only split checks; never calls cmd_run."""
import argparse,copy,hashlib,importlib.util,json,tempfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np,pandas as pd
ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
R=args.repo; O=args.out; O.mkdir(parents=True,exist_ok=True)
source=R/'tools/hinata/p2_confirm.py'; source_bytes=source.read_bytes();snapshot=O/'p2_confirm_snapshot.py';snapshot.write_bytes(source_bytes)
spec=importlib.util.spec_from_file_location('audit_confirm',snapshot);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=m.DEFAULT_SPEC.copy();rows=[dict(population='all',regime=reg,round=cp,status='OK',d_auc_ci=[.02,.04],slope_v=1.,slope_phi=1.,auc_v=.70,auc_phi=.68) for _,reg,cp in m.CELLS]
checks={'valid_control':m.gate(rows,s)}
for field in ['slope_v','slope_phi','auc_v','auc_phi','d_auc_ci']:
    bad=copy.deepcopy(rows);i=next(i for i,r in enumerate(bad) if r['regime']=='rl' and r['round']==50)
    bad[i][field]=[float('nan'),float('nan')] if field=='d_auc_ci' else float('nan')
    checks['nan_'+field]=m.gate(bad,s)
proposal=json.loads((R/'docs/learning/proposals/P-hinata-02-gate-spec.PROPOSED.json').read_text())
checks['proposed_record_passes_run_record_predicate']=proposal['record'].startswith('D-')
# Use isolated synthetic files, not the real one-shot directory; don't call cmd_run.
with tempfile.TemporaryDirectory(prefix='tanaka-claim-') as tmp:
    m.P2=Path(tmp);pf=m.P2/'predictions.parquet';pd.DataFrame({'fake':[1]}).to_parquet(pf)
    claim=m.P2/'CLAIM.json';claim.write_text(json.dumps({'spec':{'min_lb_all':1.0},'missing_cells':[]}));original=m.sha(claim)
    (m.P2/'RECEIPT.json').write_text(json.dumps({'stages':[{'stage':'claimed','claim_sha':original},{'stage':'sealed','predictions_sha':m.sha(pf)}]}))
    claim.write_text(json.dumps({'spec':{'min_lb_all':-.01},'missing_cells':[]}))
    m.evaluate=lambda pred,spec:([],{'verdict':'PASS' if spec['min_lb_all']<0 else 'FAIL','incomplete':[],'reasons':[]})
    m.cmd_score(SimpleNamespace())
    checks['changed_claim_accepted']={'claim_changed':m.sha(claim)!=original,'scored':json.loads((m.P2/'result.json').read_text())['gate']}
    pf.write_bytes(pf.read_bytes()+b'x')
    try:
        m.cmd_score(SimpleNamespace()); checks['changed_predictions_rejected']=False
    except AssertionError:
        checks['changed_predictions_rejected']=True
# Metadata-only split check. Do not load any held-out labels or checkpoint state.
tr=pd.read_parquet(R/'build/hinata/v0/fit-lq/train_rows.parquet',columns=['game','series_id']).drop_duplicates('game')
split=R/'build/learn/splits/games_split_v2.parquet'
d=pd.read_parquet(split,columns=['game','series_key','split','map','map_era','ranked','in_scope','consumed_by'])
cons=set(tr.series_id.astype(str));expected=d.series_key.astype(str).isin(cons);actual=d.consumed_by.fillna('').str.contains('P-2',regex=False)
mapset=set(d.loc[d['split']=='heldout_map','map']);h=d[(d['split']=='heldout_map')&(d.map_era=='post-m2')&d.in_scope&~expected]
# No outcome label is in this projection; counts are all in-scope, not decisive-only.
counts=h.groupby(['map','ranked']).size().to_dict()
res={'source_sha256':hashlib.sha256(source_bytes).hexdigest(),'source':str(source),'checks':checks,'split_sha256':m.sha(split),'split_rows':len(d),'consumed_series':len(cons),'consumed_flag_mismatches':int((expected!=actual).sum()),'heldout_maps':sorted(mapset),'clean_in_scope_post_m2_counts':{f'{k[0]}/{"ranked" if k[1] else "unranked"}':int(v) for k,v in counts.items()},'scope':'Synthetic scorer probes plus metadata-only manifest validation; no held-out labels or predictions read; no real confirmation claim made.'}
(O/'audit.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
