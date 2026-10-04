"""Read-only L10 paired score check, retaining the preregistered median-checkpoint estimand."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rome',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--draws',type=int,default=2000);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 cs=['pearls@50','pearls@100','pearls@150','pearls@250','units@100','total@100'];key=['seed','mapkey','opponent','side'];sources={};out={};paired=[]
 for panel,folder in [('pool','z1'),('gen','gen')]:
  refpath=a.rome/('docs/analysis/benchmarks/map_reference_medians.json' if panel=='pool' else 'tools/ra/gen_reference.json');ref=json.loads(refpath.read_text());sources[str(refpath)]=hashlib.sha256(refpath.read_bytes()).hexdigest();frames=[]
  for bot,fp in [('rome-02-far-contact','61fb6691'),('rome-01-nodevil','28132ee5')]:
   path=a.rome/f'build/zoo/{folder}-{bot}-{fp}/features/features.parquet';sources[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest();d=pd.read_parquet(path);d=d[d.bot==bot].copy();d['seed']=d.game.str.split('__').str[0].str[1:].astype(int);d['mapkey']=d.game.str.split('__').str[1];
   if panel=='gen':d['mapkey']=d['mapkey'].map(lambda k:k.replace('_','+',1))
   assert not d.duplicated(key).any()
   for c in cs:
    if panel=='gen':assert all(k in ref and c in ref[k] for k in d.mapkey), sorted(set(d.mapkey)-set(ref))
    den=d['map'].map(ref[c]) if panel=='pool' else d['mapkey'].map(lambda k:max(1.,ref[k][c]))
    d[c]=d[c]/den
   assert np.isfinite(d[cs].to_numpy()).all();d['win']=d.result.map({'win':1.,'loss':0.,'draw':.5});frames.append(d)
  c,p=frames;m=c[key+cs+['win','result']].merge(p[key+cs+['win','result']],on=key,suffixes=('_c','_p'),validate='one_to_one');assert len(m)==len(c)==len(p)==(480 if panel=='pool' else 1392)
  C=m[[x+'_c' for x in cs]].to_numpy();P=m[[x+'_p' for x in cs]].to_numpy();w=(m.win_c-m.win_p).to_numpy();names=['econ_median','econ_mean','units100_median','total100_median','win']
  def stat(ix):
   med=np.median(C[ix],axis=0)-np.median(P[ix],axis=0);return np.array([med[:4].mean(),(C[ix,:4]-P[ix,:4]).mean(),med[4],med[5],w[ix].mean()])
  point=stat(np.arange(len(m)));r={'n':len(m),'parent_wld':p.result.value_counts().to_dict(),'candidate_wld':c.result.value_counts().to_dict(),'point':dict(zip(names,map(float,point))),'cluster_intervals':{}}
  for label,cols in [('map_opponent_seat',['mapkey','opponent','side']),('seed_map',['seed','mapkey'])]:
   groups=list(m.groupby(cols).indices.values());rng=np.random.default_rng(12);samples=np.array([stat(np.concatenate([groups[i] for i in rng.integers(0,len(groups),len(groups))])) for _ in range(a.draws)]);bounds=np.percentile(samples,[5,95],axis=0);r['cluster_intervals'][label]={'clusters':len(groups),'draws':a.draws,'central90':{name:[float(bounds[0,i]),float(bounds[1,i])] for i,name in enumerate(names)}}
  out[panel]=r;m['panel']=panel;paired.extend(m.to_dict('records'))
 (a.out/'rome-paired-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in paired));(a.out/'rome-estimand-summary.json').write_text(json.dumps(out,indent=2)+'\n');(a.out/'rome-source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
