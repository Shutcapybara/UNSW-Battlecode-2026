"""Frozen ranked post-m2 queen endpoints: temporal composition and overlap audit.
Exploratory series bootstrap recomputes overlap; it is not a causal adoption test.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
p=argparse.ArgumentParser();p.add_argument('--rows',type=Path,required=True);p.add_argument('--headers',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True)
d=pd.read_json(a.rows,lines=True,convert_dates=False)
h={str(x['game']):x for x in json.loads(a.headers.read_text())['games']}
d['queen']=d.q_end
for i,r in d[d.q_end.isna()].iterrows():d.loc[i,'queen']=h[str(r.game)]['queens'][r.side]
assert d.queen.notna().all()
d['alive']=d.queen.gt(0).astype(int);d['day']=d.started_at.str[:10]
d['cohort4']=np.select([d.team.astype(str).eq('7'),d.crank.between(1,10),d.crank.between(11,50)],['us','top10','r11_50'],default='other')
compact=d[['game','side','team','opp','map','map_hash','series_id','started_at','day','crank','cohort4','q_end','queen','alive','reason','won','bot','opponent']]
compact.to_json(a.out/'terminal-rows.jsonl',orient='records',lines=True,date_format='iso')
rl=d[d.reason.isin(['queen','longest','total'])].copy()
daily=[]
for (co,day),x in rl.groupby(['cohort4','day']):
    daily.append(dict(cohort=co,day=day,n=len(x),series=x.series_id.nunique(),teams=x.team.nunique(),hashes=x.map_hash.nunique(),alive=int(x.alive.sum()),rate=float(x.alive.mean()),queen_decided=int(x.reason.eq('queen').sum()),filled=int(x.q_end.isna().sum())))
x=rl[rl.cohort4.eq('r11_50') & rl.day.isin(['2026-10-02','2026-10-04'])].copy()
x['period']=x.day.eq('2026-10-04').astype(int)
assert x.series_id.notna().all()
def summary(cols,frame=x):
    t=frame.groupby(cols+['period']).agg(n=('alive','size'),sum=('alive','sum')).unstack('period').dropna()
    n0,n1=t['n'][0],t['n'][1];w=np.minimum(n0,n1);r0=t['sum'][0]/n0;r1=t['sum'][1]/n1
    return dict(keys=cols,cells=len(t),sides0=int(n0.sum()),sides1=int(n1.sum()),overlap_weight=float(w.sum()),
                mean0=float((w*r0).sum()/w.sum()),mean1=float((w*r1).sum()/w.sum()),delta=float((w*(r1-r0)).sum()/w.sum()))
sens=[summary(cols) for cols in [['map_hash'],['team'],['team','map_hash'],['team','map_hash','side'],['team','map_hash','side','opp']]]
cols=['team','map_hash','side']
groups=x.groupby(cols+['period']).agg(n=('alive','size'),sum=('alive','sum')).unstack('period').dropna()
common=set(groups.index);matched=x[x[cols].apply(tuple,axis=1).isin(common)].copy()
cells=pd.factorize(pd.MultiIndex.from_frame(matched[cols]))[0];M=len(common)
matched.to_json(a.out/'matched-team-hash-seat.jsonl',orient='records',lines=True,date_format='iso')
# Whole-series sampling shares a weight among both focal sides of the same game.
# Re-estimate overlap support/weights each draw. Sparse support makes this exploratory.
sid=pd.factorize(x.series_id)[0];S=int(sid.max()+1);period=x.period.to_numpy();y=x.alive.to_numpy(float)
sid_m=pd.Categorical(matched.series_id,categories=list(pd.unique(x.series_id))).codes
cellperiod=cells*2+matched.period.to_numpy();ym=matched.alive.to_numpy(float)
rng=np.random.default_rng(3232);boots=[];raw=[];support=[]
length_labels={'short1to3':matched.queen.between(1,3).to_numpy(float),'long_gt3':matched.queen.gt(3).to_numpy(float),'long_ge10':matched.queen.ge(10).to_numpy(float)}
length_boots={k:[] for k in length_labels}
for _ in range(2000):
    ws=rng.multinomial(S,np.full(S,1/S));wr=ws[sid]
    raw.append(np.average(y[period==1],weights=wr[period==1])-np.average(y[period==0],weights=wr[period==0]))
    ww=ws[sid_m];n=np.bincount(cellperiod,weights=ww,minlength=2*M).reshape(M,2);z=np.bincount(cellperiod,weights=ww*ym,minlength=2*M).reshape(M,2)
    keep=(n>0).all(axis=1);w=np.minimum(n[keep,0],n[keep,1]);rates=z[keep]/n[keep]
    boots.append(float(np.average(rates[:,1]-rates[:,0],weights=w)));support.append(int(keep.sum()))
    for label,lv in length_labels.items():
        zs=np.bincount(cellperiod,weights=ww*lv,minlength=2*M).reshape(M,2)[keep]/n[keep]
        length_boots[label].append(float(np.average(zs[:,1]-zs[:,0],weights=w)))
team=[]
for tm,v in matched.groupby('team'):
    z=summary(cols,v);z['team']=str(tm);team.append(z)
maps=[]
for (mp,mh),v in matched.groupby(['map','map_hash']):
    z=summary(cols,v);z.update(map=mp,map_hash=mh);maps.append(z)
strict=groups[(groups['n'][0]>=2)&(groups['n'][1]>=2)]
strictx=x[x[cols].apply(tuple,axis=1).isin(set(strict.index))]
known_submissions=int(matched.bot.astype(str).str.len().gt(0).sum())
length_rows=[]
for label,lv in length_labels.items():
    mm=matched.copy();mm['alive']=lv;item=summary(cols,mm);item['endpoint']=label;item['series_boot95']=np.quantile(length_boots[label],[.025,.975]).tolist();length_rows.append(item)
# Descriptive top-ten control with the same match definition, not a second confirmatory test.
top=rl[rl.cohort4.eq('top10') & rl.day.isin(['2026-10-02','2026-10-04'])].copy();top['period']=top.day.eq('2026-10-04').astype(int)
top_control=summary(cols,top)
top_control['length_endpoints']=[]
for label,v in [('short1to3',top.queen.between(1,3)),('long_gt3',top.queen.gt(3))]:
    tmp=top.copy();tmp['alive']=v.astype(int);row=summary(cols,tmp);row['endpoint']=label;top_control['length_endpoints'].append(row)
output=dict(daily=daily,raw_r11_50=dict(n=len(x),series=S,teams=x.team.nunique(),days={k:dict(n=len(v),alive=int(v.alive.sum()),rate=float(v.alive.mean()),series=v.series_id.nunique()) for k,v in x.groupby('day')},delta=float(x[x.period==1].alive.mean()-x[x.period==0].alive.mean()),series_boot95=np.quantile(raw,[.025,.975]).tolist()),
    sensitivity=sens,primary=dict(**sens[3],series=matched.series_id.nunique(),teams=matched.team.nunique(),hashes=matched.map_hash.nunique(),known_bot_fields=known_submissions,series_boot95=np.quantile(boots,[.025,.975]).tolist(),bootstrap_support95=np.quantile(support,[.025,.975]).tolist()),
    repeated_cell_sensitivity=summary(cols,strictx),length_endpoints=length_rows,top10_control=top_control,team_rows=team,map_rows=maps,
    contract='Rank11–50 frozen store ranks, ranked post-m2 RL sides, Oct2 vsOct4. Same team/fullhash/seat cells present both days; min(n0,n1) weights. 2000 whole-series bootstrap seed3232 re-estimates overlap among original shared cells; support changes, interval exploratory not stable target/causal adoption. Opponent/submission/time-of-day not controlled. Terminal survival conditional on reaching RL; early games excluded, not declared dead at490.')
(a.out/'adoption-summary.json').write_text(json.dumps(output,indent=2)+'\n')
pairs=[]
trace=rl[rl.day.isin(['2026-10-02','2026-10-04']) & rl.cohort4.isin(['top10','r11_50'])]
for key,z in trace.groupby(['cohort4','team','map_hash','side']):
    early=z[z.day.eq('2026-10-02') & z.queen.between(1,3)];late=z[z.day.eq('2026-10-04') & z.queen.ge(10)]
    if len(early) and len(late):
        aa=early.sort_values('started_at').iloc[-1];bb=late.sort_values(['queen','started_at'],ascending=[False,True]).iloc[0]
        pairs.append(dict(cohort=key[0],team=int(key[1]),map_hash=key[2],side=key[3],map=aa['map'],early_game=int(aa.game),late_game=int(bb.game),early_queen=int(aa.queen),late_queen=int(bb.queen),early_opponent=int(aa.opp),late_opponent=int(bb.opp),same_opponent=bool(aa.opp==bb.opp)))
pairs=sorted(pairs,key=lambda r:(r['cohort'],r['team'],r['map_hash'],r['side']))
(a.out/'feeding-trace-candidates.json').write_text(json.dumps({'selection':'Both ranked RL; same team/fullhash/seat; day2 latest survivingq1..3 vsday4 largestq>=10 (earliest tie). Outcome-selected discovery candidates, not effect estimate; never call these a holdout.','pairs':pairs},indent=2)+'\n')
print(json.dumps({k:output[k] for k in ['daily','raw_r11_50','sensitivity','primary','repeated_cell_sensitivity']},indent=2))
