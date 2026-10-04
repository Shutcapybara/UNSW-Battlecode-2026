from pathlib import Path
import json,hashlib,sys,shutil,contextlib,io,tempfile,argparse
from types import SimpleNamespace
import numpy as np,pandas as pd
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026'); O=Path('/tmp/tanaka-r11');O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HERE=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,default=HERE/'docs/learning/reviews/tanaka-round11');opts=ap.parse_args()
for f in ['r2_bc.py','r2_battery.py','r2_cnn_b.py']:shutil.copyfile(opts.sources/f,O/f)
# Reuse independent round-10 toys with only rev6's required A0 metadata and waiver argument added.
s=(HERE/'tools/tanaka/battery_repair_audit.py').read_text();s=s[s.index('checks={};'):s.index('# Independently reproduce')]
s=s.replace("'model_bytes':{name:1 if name.startswith('A10') else 100}","'model_bytes':{name:1 if name.startswith('A10') else 100},'teams_by_rating':['1','2','3','4']")
s=s.replace('out=str(f)))','out=str(f),waive_ts=None))');s=s.replace("'missing_teacher_inventory','complete']", "'missing_teacher_inventory','complete','A10b_perfect']")
s=s.replace("if name in ['missing_teacher_inventory','complete']:","if name in ['missing_teacher_inventory','complete','A10b_perfect']:")
s=s.replace("for ar in B.PLANNED:\n", "if name=='A10b_perfect':\n     write(root,'A10b',pp,dd);pp=pp.copy();pp[80:]=pbad[80:]\n    for ar in B.PLANNED:\n")
s=s.replace("'vs_A0':r['vs_A0']", "'vs_A0':r['vs_A0'],'pooled':r['pooled']")
sys.path.insert(0,str(O));import r2_battery as B
exec(s)
assert all(not checks[k]['accepted'] for k in ['nan','inf','bad_sum','negative_sum_one','pooled_subset','duplicate','labels','folds','series','A6_wrong_team','A7_partial','A2_nan'])
assert not checks['A7_full_only']['result']['teacher']['goes_forward']
assert checks['complete']['result']['teacher']['goes_forward']
assert any(r['arm']=='A10b' and not r['pooled'] for r in checks['A10b_perfect']['result']['rows'])
# Supported exclusion positive control and one-extra-row negative control, independently constructed.
with tempfile.TemporaryDirectory(prefix='tanaka-a2valid-') as tt:
 root=Path(tt); dd=d.copy();dd.loc[dd.team.eq('4'),'fold']='f0';a0=write(root,'A0',pbad,dd);good=dd.team.ne('4').to_numpy();write(root,'A2-400',pgood[good],dd[good]);t=table(root,a0)
 checks['a2_structural_exclusion']={'accepted':True,'rows':t['rows'][0]['rows'],'inventory_blocks':not t['teacher_specific']['selection']['goes_forward']}
 pp=root/'A2-400'/'rows.parquet';bb=pd.read_parquet(pp);bb.iloc[1:].to_parquet(pp);np.save(root/'A2-400'/'p_A2-400.npy',pgood[good][1:]);checks['a2_one_extra_missing']=attempt(lambda:table(root,a0));assert not checks['a2_one_extra_missing']['accepted']
# Official published local gate: read frozen local run outputs, never live indexes.
W=Path('/Users/alik/Documents/Projects/wt-asahi/build/asahi/runs');pairrows=[];gates={}
for panel,n in [('pool',544),('gen',928)]:
 arms=[];hashes={}
 for bot,fp in [('asahi-05-kz12-k16','43bd2d4f'),('carthage-05-free-sprint','7df05a3f')]:
  p=W/bot/fp/panel/'queen.parquet';q=pd.read_parquet(p,columns=['game','side','winner']);hashes[bot]=sha(p);rr=[]
  records={v['game']:v for v in map(json.loads,(p.parent/'index.jsonl').read_text().splitlines())}
  for x in q.itertuples():
   seed,mp,aa,bb=x.game.split('__');ss=int(seed[1:])
   if ss not in [1,2,3] or (aa if x.side=='A' else bb)!=bot:continue
   assert records[x.game]['rc']==0 and records[x.game]['winner']==x.winner
   assert x.winner in ['A','B','draw','Draw']
   rr.append(dict(seed=ss,map=mp,opp=bb if x.side=='A' else aa,seat=x.side,win=float(x.winner==x.side) if x.winner in ['A','B'] else .5))
  arms.append(pd.DataFrame(rr))
 p=arms[0].merge(arms[1],on=['seed','map','opp','seat'],suffixes=('_c','_p'),validate='one_to_one');p['d']=p.win_c-p.win_p;p['panel']=panel;pairrows.extend(p.to_dict('records'))
 def calc(z):
  g=z.groupby(['map','opp'],sort=True).d.agg(['sum','count']);ix=np.random.default_rng(7).integers(0,len(g),(1000,len(g)));bs=g['sum'].to_numpy()[ix].sum(1)/g['count'].to_numpy()[ix].sum(1)
  return {'n':len(z),'clusters':len(g),'candidate_score_total':float(z.win_c.sum()),'parent_score_total':float(z.win_p.sum()),'delta':float(z.d.mean()),'ci90':np.percentile(bs,[5,95]).tolist()}
 gate=p[p.seed.isin([2,3])];assert len(gate)==n;gates[panel]={'s23':calc(gate),'hashes':hashes}
 if panel=='pool':
  weak=gate['map'].eq('live+weakhold');gates[panel]['weakhold_s23']=calc(gate[weak]);gates[panel]['other_s23']=calc(gate[~weak]);gates[panel]['weakhold_seeds']={str(ss):calc(p[p.seed.eq(ss)&p['map'].eq('live+weakhold')]) for ss in [1,2,3]};a=gates[panel]['weakhold_s23']['delta'];b=gates[panel]['other_s23']['delta'];gates[panel]['break_even_weakhold_weight']=-b/(a-b)
# New HB side export: join metadata checks, no engine rerun.
H=R/'build/learn/kageyama/hb1_dev120';man=json.loads((H/'_manifest.json').read_text());assert all(sha(H/f)==v for f,v in man['shards'].items())
key=['game','side','dragon','round','turn'];meta=['blocks_src','y_kind','y_first'];paths=[R/'build/learn/kageyama'/f'teachers_dev120.p{i}.parquet' for i in [0,1]]
# Locate source shards by their explicit manifest basename if stored under another subdirectory.
for i,p in enumerate(paths):
 if not p.exists():paths[i]=next((R/'build/learn/kageyama').rglob(p.name))
orig=pd.concat([pd.read_parquet(p,columns=key+meta) for p in paths],ignore_index=True);hb=pd.read_parquet(H);assert not hb.duplicated(key).any() and not orig.duplicated(key).any()
idx=pd.MultiIndex.from_frame(orig[key]);hidx=pd.MultiIndex.from_frame(hb[key]);assert set(idx)==set(hidx);hb=hb.set_index(key).loc[idx].reset_index();assert all(np.array_equal(orig[c],hb[c]) for c in meta)
m=orig.blocks_src.eq('oracle')&orig.y_kind.eq(0);fr=m&orig.y_first.isin([0,1,3]);cols=[c for c in hb if c.startswith('hb_f_')];assert not any(B.R.banned(c[5:]) for c in cols);assert len(cols)==270 and np.isfinite(hb.loc[m,cols].to_numpy()).all();probs=hb.loc[m,['hb_pF','hb_pR','hb_pL']].to_numpy();assert (probs>=0).all() and np.allclose(probs.sum(1),1,atol=2e-6)
pred=np.array([0,1,3])[hb[['hb_pF','hb_pR','hb_pL']].to_numpy().argmax(1)];hbcheck={'manifest_sha':sha(H/'_manifest.json'),'verified_shards':len(man['shards']),'exact_keys':len(orig),'oracle_moves':int(m.sum()),'frl':int(fr.sum()),'features':len(cols),'A0_accuracy':float((pred[fr]==orig.loc[fr,'y_first']).mean()),'sources':[{'path':str(p),'sha':sha(p)} for p in paths]}
# Independently reproduce A10b and its fixed-support curve from published predictions only.
base=pd.read_parquet(R/'build/hinata/r2/battery/A3-u/rows.parquet');bk=pd.MultiIndex.from_frame(base[key]);frl=np.array([0,1,3]);mask=base.y_first.isin(frl).to_numpy();hits={};curves={}
for dr in ['A3-u','A10-u','A10b-u','A10b-f25','A10b-f50']:
 p=R/'build/hinata/r2/battery'/dr;dd=pd.read_parquet(p/'rows.parquet');kk=pd.MultiIndex.from_frame(dd[key]);assert kk.is_unique and set(kk)==set(bk);ix=pd.Series(np.arange(len(dd)),index=kk).loc[bk].to_numpy();dd=dd.iloc[ix].reset_index(drop=True);assert all(np.array_equal(dd[c],base[c]) for c in ['y_first','series_key','fold'])
 reg=json.loads((p/'registry.json').read_text());curves[dr]={'registry_sha':sha(p/'registry.json'),'metrics':{}}
 for arm in reg['arms']:
  P=np.load(p/f'p_{arm}.npy')[ix];hits[arm]=frl[P[:,frl].argmax(1)]==base.y_first.to_numpy();h=hits[arm]
  g=pd.DataFrame({'s':base.series_key,'h':h&mask,'n':mask}).groupby('s')[['h','n']].sum();ii=np.random.default_rng(7).integers(0,len(g),(1000,len(g)));bs=g.h.to_numpy()[ii].sum(1)/g.n.to_numpy()[ii].sum(1);curves[dr]['metrics'][arm]={'acc':float(h[mask].mean()),'ci90':np.percentile(bs,[5,95]).tolist(),'p_sha':sha(p/f'p_{arm}.npy')}
diffs={}
for aa,bb in [('A10b','A10-e4'),('A3-400','A10b'),('A10b','A10b-f50')]:
 g=pd.DataFrame({'s':base.series_key,'d':(hits[aa].astype(float)-hits[bb].astype(float))*mask,'n':mask}).groupby('s')[['d','n']].sum();ix=np.random.default_rng(7).integers(0,len(g),(1000,len(g)));bs=g.d.to_numpy()[ix].sum(1)/g.n.to_numpy()[ix].sum(1);diffs[aa+' minus '+bb]={'delta':float(g.d.sum()/g.n.sum()),'ci90':np.percentile(bs,[5,95]).tolist()}
pd.DataFrame(pairrows).to_csv(O/'k16-pairs.csv',index=False)
out={'source_sha':{f:sha(O/f) for f in ['r2_bc.py','r2_battery.py','r2_cnn_b.py']},'selector':checks,'k16':gates,'hb':hbcheck,'curves':curves,'curve_diffs':diffs}
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='selector'},indent=2));print('Selector regressions passed; full-data A10b remains excluded:',checks['A10b_perfect']['result']['pooled']['selected'])
