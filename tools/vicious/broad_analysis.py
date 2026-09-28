"""Paired frozen-map summary and publication-friendly campaign figures."""
import argparse,json,os,sys
from pathlib import Path
from collections import defaultdict
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/vicious-matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
C=Path(json.loads((ROOT/'tools/vicious/current.json').read_text())['directory'])
ap=argparse.ArgumentParser();ap.add_argument('--panel',default='cycle_04/broad');ap.add_argument('--controls');ap.add_argument('--candidate');ap.add_argument('--out',default='cycle_04/BROAD_RESULTS.json');ap.add_argument('--figure-prefix',default='');args=ap.parse_args()
P=C/args.panel
rows=[]
for folder in [P]+([C/args.controls] if args.controls else []):
 rows += [dict(r,directory=str(folder)) for r in json.loads((folder/'results.json').read_text())]
manifest=json.loads((P/'manifest.json').read_text())
if args.controls:
 control_manifest=json.loads((C/args.controls/'manifest.json').read_text())
 assert manifest['seed']==control_manifest['seed']
 for opponent in manifest['opponents']:
  assert manifest['source_hashes'][opponent]==control_manifest['source_hashes'][opponent]
 for name in manifest['maps']:
  assert manifest['map_hashes'][name]==control_manifest['map_hashes'][name]
weights=json.loads((C/'baseline/experiment_data__bot-ratings__latest.json').read_text())['map_weights']
parent='vicious-v01-frozen';candidate=args.candidate or json.loads((C/'release/SELECTION.json').read_text())['candidate']
by=defaultdict(dict)
for r in rows:
 if r['outcome']=='error':continue
 r['score']=.5 if r['outcome']=='draw' else float(r['outcome']==r['side'])
 by[r['arm']][r['opponent'],r['map'],r['side']]=r
keys=sorted(set(by[parent])&set(by[candidate]));maps=sorted(set(k[1] for k in keys))
expected=len(manifest['maps'])*len(manifest['opponents'])*2
assert len(keys)==expected,("Incomplete paired panel",len(keys),expected)
permap={m:{a:float(np.mean([by[a][k]['score'] for k in keys if k[1]==m])) for a in [parent,candidate]} for m in maps}
for m in maps:permap[m]['delta']=permap[m][candidate]-permap[m][parent];permap[m]['paired_games']=sum(k[1]==m for k in keys)
coverage=sum(weights[m] for m in maps)
orig=[m for m in maps if not m.startswith(('mc26','md26'))];synth=[m for m in maps if m not in orig]
def weighted(ms,a):return sum(weights[m]*permap[m][a] for m in ms)/sum(weights[m] for m in ms) if ms else None
summary={'candidate':candidate,'pairs':len(keys),'target_map_mass_observed':coverage,'missing_target_map_mass':1-coverage,'comparison_opponents':manifest['opponents'],'target_opponent_caveat':'These two frozen controls, not an estimate against the full24-reference field.','per_map':permap,'arms':{}}
for a in [parent,candidate]:
 rs=[by[a][k] for k in keys]
 summary['arms'][a]={'wins':sum(r['score']==1 for r in rs),'draws':sum(r['score']==.5 for r in rs),'losses':sum(r['score']==0 for r in rs),'weighted':weighted(maps,a),'original':weighted(orig,a),'synthetic':weighted(synth,a),'by_opponent':{o:sum(weights[m]*np.mean([by[a][k]['score'] for k in keys if k[0]==o and k[1]==m]) for m in maps)/coverage for o in manifest['opponents']}}
summary['mixture_sensitivity']={str(alpha):{a:alpha*weighted(orig,a)+(1-alpha)*weighted(synth,a) for a in [parent,candidate]} for alpha in (.25,.5,.75)}
exposure=json.loads((C/'RESERVE_LEDGER.json').read_text())
fresh=[m for m in maps if m in exposure['new_map_set_at_primary_freeze']]
reserve=[m for m in maps if m in exposure['family_confirmation_reserved']]
summary['fresh_at_freeze']={'maps':fresh,'mass':sum(weights[m] for m in fresh),
                          'weighted':{a:weighted(fresh,a) for a in [parent,candidate]}}
summary['reserved_maps']={'maps':reserve,'mass':sum(weights[m] for m in reserve),
                         'weighted':{a:weighted(reserve,a) for a in [parent,candidate]}}
info=json.loads((C/'baseline/maps__new__manifest.json').read_text())['maps'];family={r['name']:r['family_id'] for r in info}
groups=[]
for ms in [orig,synth]:
 gg=defaultdict(list)
 for m in ms:gg[family.get(m,m)].append(m)
 groups.append(list(gg.values()))
rng=np.random.default_rng(20260928);samples=[]
for _ in range(10000):
 v=0.
 for gs in groups:
  drawn=[gs[i] for i in rng.integers(0,len(gs),len(gs))];ms=[m for g in drawn for m in g]
  v+=.5*sum(weights[m]*permap[m]['delta'] for m in ms)/sum(weights[m] for m in ms)
 samples.append(v)
summary['descriptive_family_bootstrap']={'draws':10000,'groups':[len(g) for g in groups],'delta_90pct':np.quantile(samples,[.05,.95]).tolist(),'caveat':'Paired sides/opponents retained together; map siblings grouped; original/synthetic strata retained. Describes sensitivity of this finite selected panel, not a confirmatory significance test or new independent games.'}
summary['paired_flips']=[{'opponent':k[0],'map':k[1],'side':k[2],'delta':by[candidate][k]['score']-by[parent][k]['score']} for k in keys if by[candidate][k]['score']!=by[parent][k]['score']]
figs=C/'figures';figs.mkdir(exist_ok=True)
def figure(name):return figs/(args.figure_prefix+name)
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'font.size':10})
ordered=orig+synth;delta=[100*permap[m]['delta'] for m in ordered]
fig,ax=plt.subplots(figsize=(10,11));ax.barh(range(len(ordered)),delta,color=['#247b77' if x>=0 else '#bb4a45' for x in delta]);ax.set_yticks(range(len(ordered)),ordered);ax.invert_yaxis();ax.axvline(0,color='#555',lw=.8);ax.axhline(len(orig)-.5,color='#999',lw=.8);ax.set_xlabel('Candidate minus parent · win-rate percentage points');ax.set_title(candidate+' — paired map effects\nTwo frozen opponents × both sides; 50/50 original/synthetic target');fig.tight_layout();fig.savefig(figure('map_effects.png'),dpi=160);fig.savefig(figure('map_effects.svg'));plt.close(fig)
curves={a:{k:np.zeros(501) for k in ('units','total','longest')} for a in [parent,candidate]}
for a in curves:
 for key in keys:
  r=by[a][key];s=json.loads((Path(r['directory'])/'games'/r['stats']).read_text());points=s['curve'];lookup={p['round']:p[r['side']] for p in points};last=points[-1][r['side']]
  # Each map gets declared target mass, split equally over its paired fixtures.
  mass=weights[r['map']]/permap[r['map']]['paired_games']/coverage
  for turn in range(501):
   pt=lookup.get(turn,last)
   for metric in curves[a]:curves[a][metric][turn]+=mass*pt.get(metric,0)
fig,axs=plt.subplots(3,1,figsize=(10,9),sharex=True)
for ax,metric,label in zip(axs,('units','total','longest'),('Live dragons','Team material','Longest dragon')):
 for a,color,name in [(parent,'#8d9299','Frozen parent'),(candidate,'#176f83','Vicious candidate')]:ax.plot(range(501),curves[a][metric],color=color,label=name,lw=2)
 for boundary in ([340,400] if candidate=='vicious-x15-late-time' else [250,380]):ax.axvline(boundary,color='#aaa',ls=':',lw=1)
 ax.set_ylabel(label);ax.grid(alpha=.15)
axs[0].legend();axs[0].set_title(candidate+' · weighted phase trajectories\nAll paired games; terminal state carried forward after early elimination');axs[-1].set_xlabel('Global game round');fig.tight_layout();fig.savefig(figure('phase_trajectories.png'),dpi=160);fig.savefig(figure('phase_trajectories.svg'));plt.close(fig)
summary['weighted_phase_points']={a:{str(r):{k:float(v[r]) for k,v in curves[a].items()} for r in (30,80,250,380,400,500)} for a in curves}
(C/args.out).write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:summary[k] for k in ('candidate','pairs','arms','descriptive_family_bootstrap')},indent=2))
