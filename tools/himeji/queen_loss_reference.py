"""Post-m2 queen reference cut from existing lean parts. No API, simulator or shared writes."""
import argparse,hashlib,json
from pathlib import Path
import duckdb,numpy as np,pandas as pd
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--frozen-rows',type=Path);a=ap.parse_args();a.snapshot.mkdir(exist_ok=True,parents=True)
if a.frozen_rows:
 d=pd.read_json(a.frozen_rows,lines=True,convert_dates=False,dtype={'game':str,'team':str,'opp':str});source={'frozen_rows_sha256':hashlib.sha256(a.frozen_rows.read_bytes()).hexdigest()}
else:
 files=sorted((a.repo/'build/shenzhen/lean').glob('part-*.parquet'));c=duckdb.connect();c.execute('set threads=1')
 cols=['game','side','team','opp','map','ranked','started_at','R','reason','eng_win','win','qlen@490','qlen_end','opp_qlen_end','total@490','opp_total@490','total_end','opp_total_end','longest@490','longest_end','q_death_round','q_death_cause']
 expr=','.join('"'+x+'"' for x in cols)
 d=c.execute(f'select distinct on (game,side) {expr} from read_parquet(?,union_by_name=true) order by game,side',[list(map(str,files))]).df();d.game=d.game.astype(str);d.team=d.team.astype(str);d.opp=d.opp.astype(str)
 idx={str(r['game_id']):r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};lad=json.loads((a.snapshot/'ladder.json').read_text());top={str(r['id']) for r in lad if r.get('rank') and r['rank']<=10 and not r.get('dev')}
 d=d[d.game.isin(idx)].copy();d=d[pd.to_datetime(d.started_at,utc=True,format='mixed')>=pd.Timestamp('2026-10-02T03:49:00Z')].copy()
 for row in d.itertuples():
  m=idx[row.game];assert row.ranked==m['ranked'];assert pd.Timestamp(row.started_at)==pd.Timestamp(m['started_at']),(row.game,row.started_at,m['started_at']);assert str(m['team_a'] if row.side=='A' else m['team_b'])==row.team
  assert row.win==(1 if m['winner']==row.side.lower() else 0 if m['winner'] in ['a','b'] else .5),(row.game,row.side,m['winner'],row.win)
  assert row.eng_win==row.win,(row.game,row.side,row.eng_win,row.win)
 d['started_at']=d.game.map(lambda g:idx[g]['started_at']);d['map_hash']=d.game.map(lambda g:idx[g]['map_hash']);d['series_id']=d.game.map(lambda g:idx[g].get('series_id') or 'game-'+g);d['submission']=[str(idx[g].get('bot_a' if s=='A' else 'bot_b') or '') for g,s in zip(d.game,d.side)]
 d['cohort']=d.team.map(lambda x:'us14585' if x=='7' else 'top10' if x in top else 'other')
 excluded=d[(d.team=='7') & (d.submission!='14585')].groupby('submission').size().to_dict()
 allgames=d.game.nunique();allchecks=len(d)
 d=d[(d.cohort=='top10') | ((d.cohort=='us14585') & (d.submission=='14585'))].copy()
 available=[m for m in idx.values() if (m.get('started_at') or '')>='2026-10-02T03:49:00' and 7 in (m['team_a'],m['team_b']) and str(m.get('bot_a' if m['team_a']==7 else 'bot_b'))=='14585']
 source={'parts':[{'file':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'post_m2_lean_games':int(allgames),'all_side_winner_checks':allchecks,'excluded_own_submission_sides':excluded,'top10':sorted(top),'own14585_index_by_mode':{str(k):sum(m['ranked']==k for m in available) for k in [False,True]},'rule_era':'post123','map_era':'post-m2','cutoff':'2026-10-02T03:49Z'}
 (a.snapshot/'source-selection.json').write_text(json.dumps(source,indent=2)+'\n')
 assert not (a.snapshot/'queen-rows.jsonl').exists(),'Freeze already exists; use --frozen-rows for reproduction'
 d.to_json(a.snapshot/'queen-rows.jsonl',orient='records',lines=True,double_precision=15)
assert not d.duplicated(['game','side']).any()
q=d[d.reason.eq('queen')];assert (q.qlen_end.ne(q.opp_qlen_end)).all();assert (q.win.eq(1)==q.qlen_end.gt(q.opp_qlen_end)).all()
def ratio(z,num,den):
 num=np.asarray(num,dtype=int);den=np.asarray(den,dtype=int);assert (num<=den).all()
 g=pd.DataFrame({'block':z.series_id.to_numpy(),'num':num,'den':den}).groupby('block')[['num','den']].sum();n=int(num.sum());N=int(den.sum());S=len(g);eligibleS=int((g.den>0).sum())
 if not N:return {'n':n,'N':N,'series':eligibleS,'value':None,'ci95':None}
 rng=np.random.default_rng(2020);v=g.to_numpy();chosen=rng.integers(S,size=(2000,S));b=v[chosen].sum(axis=1);b=b[b[:,1]>0];boot=b[:,0]/b[:,1];ci=np.quantile(boot,[.025,.975]).tolist()
 o={'n':n,'N':N,'series':eligibleS,'resampled_blocks':S,'value':n/N,'ci95':ci,'bootstrap':2000}
 if n==0 or n==N:
  o['ci95']=None;o['note']='Boundary sample: percentile bootstrap degenerates; no game-rate confidence claim.'
  o['series_any_failure_upper95' if n==N else 'series_any_event_upper95']=1-.05**(1/eligibleS)
 return o
def metrics(z):
 loss=z.win.eq(0);rl=z.reason.isin(['queen','longest','total','tie']);reach=z.R.ge(490);qa=z['qlen@490'].gt(0)&reach;qe=z.qlen_end.gt(0);qv=z.reason.eq('queen');lead490=z['total@490'].gt(z['opp_total@490'])&reach;leadend=z.total_end.gt(z.opp_total_end);ones=np.ones(len(z),bool)
 defs={'queen_loss_among_losses':(qv&loss,loss),'queen_loss_among_games':(qv&loss,ones),'loss_among_queen_verdicts':(qv&loss,qv),'queen_verdict_share':(qv,ones),'queen_alive_actual490':(qa,reach),'queen_alive490_joint':(qa,ones),'queen_alive_RL_terminal':(qe&rl,rl),'lead490_loss_among_RL_losses':(lead490&loss&rl,loss&rl&reach),'loss_among_RL_lead490':(lead490&loss&rl,lead490&rl),'leadend_loss_among_RL_losses':(leadend&loss&rl,loss&rl),'loss_among_RL_leadend':(leadend&loss&rl,leadend&rl)}
 return {'games':int(z.game.nunique()),'sides':len(z),'series':int(z.series_id.nunique()),'hashes':int(z.map_hash.nunique()),'wins':int(z.win.eq(1).sum()),'losses':int(loss.sum()),'early_before490':int((~reach).sum()),'metrics':{k:ratio(z,*v) for k,v in defs.items()},'r490_queen_dead_zero_percentiles':np.quantile(z.loc[reach,'qlen@490'],[.25,.5,.75,.9]).tolist() if reach.any() else None,'terminal_queen_checks':int((qv & z.qlen_end.eq(z.opp_qlen_end)).sum())}
res=[]
for (mode,cohort),g in d.groupby(['ranked','cohort']):
 for label,z in [('ALL',g)]+list(g.groupby('map')):
  res.append(dict(ranked=bool(mode),cohort=cohort,map=label,**metrics(z)))
(a.snapshot/'queen-reference.json').write_text(json.dumps({'rows':res,'method':'2000 whole-series bootstrap seed2020; coverage sample, intervals conditional on selected rows; ranked/unranked separate; no matched-us gap; actualR>=490, terminalRL reason explicit','source':source},indent=2)+'\n')
byhash=[dict(ranked=bool(mode),cohort=cohort,map=m,map_hash=h,sides=len(z),series=int(z.series_id.nunique()),reached490=int(z.R.ge(490).sum()),alive490=int((z.R.ge(490)&z['qlen@490'].gt(0)).sum()),queen_losses=int((z.reason.eq('queen')&z.win.eq(0)).sum()),losses=int(z.win.eq(0).sum())) for (mode,cohort,m,h),z in d.groupby(['ranked','cohort','map','map_hash'])]
(a.snapshot/'hash-counts.json').write_text(json.dumps(byhash,indent=2)+'\n')
for r in res:
 if r['map']=='ALL' or (r['cohort']=='us14585' and r['ranked']):print(r['ranked'],r['cohort'],r['map'],r['sides'],r['metrics']['queen_loss_among_losses'],r['metrics']['queen_alive_actual490'])
