"""Summarize frozen header audits, preserving paired fixtures and missing outcomes."""
import argparse, collections, json
from pathlib import Path
import numpy as np

def key(r): return (r['map'],r['seed'],r['opp'],r['side'])
def wld(rows,col): return [sum(r[col]==x for r in rows) for x in [1,0,.5]]
def stats(values,groups):
 v=np.array(values,float); rng=np.random.default_rng(7)
 fixture=np.array([v[rng.integers(0,len(v),len(v))].mean() for _ in range(1000)])
 gs=list(groups.values()); sums=np.array([v[g].sum() for g in gs]); ns=np.array([len(g) for g in gs]);rng=np.random.default_rng(7)
 blocked=[]
 for _ in range(1000):
  ix=rng.integers(0,len(gs),len(gs)); blocked.append(sums[ix].sum()/ns[ix].sum())
 return dict(n=len(v),delta=float(v.mean()),better=int((v>0).sum()),worse=int((v<0).sum()),ties=int((v==0).sum()),fixture_ci90=np.quantile(fixture,[.05,.95]).tolist(),map_opponent_blocks=len(gs),block_ci90=np.quantile(blocked,[.05,.95]).tolist())

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--feature-winners',type=Path,required=True);a=ap.parse_args()
 manifest=json.loads((a.out/'manifest.json').read_text());rows=list(map(json.loads,(a.out/'header-rows.jsonl').read_text().splitlines())); assert len(rows)==2447
 assert all(r['terminated'] and r['runner']==r['official'] for r in rows)
 feats={(r['bot'],r['panel'],r['game'],r['side']):{'win':1,'loss':0,'draw':.5}[r['result']] for r in json.loads(a.feature_winners.read_text())}
 assert len(feats)==len(rows)
 assert all(r['old_score']==feats[r['bot'],r['panel'],r['game'],r['side']] for r in rows)
 summary=dict(header_count=len(rows),all_terminated=True,runner_agrees=len(rows),old_matches_features=len(rows),method='1000 paired fixture bootstrap and sensitivity: map-opponent blocks retaining seeds/seats; seed7, central90% intervals; local unswbc1.2.3 declared by tester, not live',panels={})
 pairs=[]
 for panel in ['pool','gen']:
  br=[r for r in rows if r['panel']==panel and r['bot']==manifest['base']]; cr=[r for r in rows if r['panel']==panel and r['bot']==manifest['candidate']]
  b={key(r):r for r in br}; c={key(r):r for r in cr}; assert len(b)==len(br) and len(c)==len(cr)
  ks=sorted(b.keys()&c.keys()); groups=collections.defaultdict(list)
  for i,k in enumerate(ks):groups[(k[0],k[2])].append(i)
  def absolute(rs): return dict(n=len(rs),official_wld=wld(rs,'official_score'),old_wld=wld(rs,'old_score'),official_share=sum(r['official_score'] for r in rs)/len(rs),old_share=sum(r['old_score'] for r in rs)/len(rs),flips=sum(r['official']!=r['old'] for r in rs),net_correction=sum(r['official_score']-r['old_score'] for r in rs))
  official=[c[k]['official_score']-b[k]['official_score'] for k in ks];old=[c[k]['old_score']-b[k]['old_score'] for k in ks]
  s=dict(base=absolute(br),candidate=absolute(cr),official=stats(official,groups),old=stats(old,groups),missing_candidate=[b[k] for k in sorted(b.keys()-c.keys())],missing_base=[c[k] for k in sorted(c.keys()-b.keys())],map_deltas={},correction_delta=float(np.mean(official)-np.mean(old)))
  for m in sorted({k[0] for k in ks}):
   ix=[i for i,k in enumerate(ks) if k[0]==m];s['map_deltas'][m]=dict(n=len(ix),official_delta=float(np.mean(np.array(official)[ix])),old_delta=float(np.mean(np.array(old)[ix])))
  if s['missing_candidate']:
   assert len(s['missing_candidate'])==1
   bm=s['missing_candidate'][0]['official_score'];s['complete_panel_point_bounds']=[(sum(official)+x-bm)/len(b) for x in [0,1]]
   s['missing_candidate_baseline_score']=bm
  summary['panels'][panel]=s
  for k in ks: pairs.append(dict(panel=panel,map=k[0],seed=k[1],opp=k[2],side=k[3],base_official=b[k]['official_score'],candidate_official=c[k]['official_score'],base_old=b[k]['old_score'],candidate_old=c[k]['old_score']))
 (a.out/'paired-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in pairs));(a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
