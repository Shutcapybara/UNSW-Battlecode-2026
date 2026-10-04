"""Fill only missing confirmed-14585 games from the local corpus; no downloads or shared writes."""
import argparse,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--snapshot',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
rows=[json.loads(x) for x in (a.snapshot/'queen-rows.jsonl').read_text().splitlines()];done={str(r['game']) for r in rows if r['cohort']=='us14585'};idx={str(r['game_id']):r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};sel=[];checks=[]
for gid,m in idx.items():
 if gid in done or (m.get('started_at') or '')<'2026-10-02T03:49:00' or 7 not in (m['team_a'],m['team_b']):continue
 side='A' if m['team_a']==7 else 'B';other='B' if side=='A' else 'A'
 if str(m.get('bot_a' if side=='A' else 'bot_b'))!='14585':continue
 p=a.repo/'public_replays/corpus/replays'/f'{gid}.replay';sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==m['sha256'];g=F.decode(p);assert g['winner'].lower()==m['winner'];assert F._reader(p).object(0,0).text(1 if side=='A' else 2)=='14585'
 queens={t:min(i for i,(tt,b) in g['rounds'][0].items() if tt==t) for t in 'AB'}
 for t in 'AB':
  qb=g['rounds'][-1].get(queens[t]);assert g['final'][t]['queen']==(len(qb[1]) if qb else 0)
 cp=g['rounds'][min(490,g['last_round'])];qb=cp.get(queens[side]);qd=next((x for x in g['events']['deaths'] if x['id']==queens[side]),{});win=1 if g['winner']==side else 0 if g['winner']==other else .5
 r=dict(game=gid,side=side,team='7',opp=str(m['team_b'] if side=='A' else m['team_a']),map=('Prisoners Dilemma 10' if g['map']=='Prisoners Dilemma' and g.get('n_initial')==10 else g['map']),ranked=m['ranked'],started_at=m['started_at'],R=g['last_round'],reason=g['reason'],eng_win=win,win=win,qlen_end=g['final'][side]['queen'],opp_qlen_end=g['final'][other]['queen'],total_end=g['final'][side]['total'],opp_total_end=g['final'][other]['total'],longest_end=g['final'][side]['longest'],q_death_round=qd.get('round'),q_death_cause=qd.get('cause'),map_hash=m['map_hash'],series_id=m['series_id'] or 'game-'+gid,submission='14585',cohort='us14585')
 r['qlen@490']=len(qb[1]) if qb else 0
 for key,t in [('total@490',side),('opp_total@490',other)]:r[key]=sum(len(b) for tt,b in cp.values() if tt==t)
 r['longest@490']=max((len(b) for tt,b in cp.values() if tt==side),default=0);rows.append(r);sel.append(m);checks.append({'game':gid,'sha256':sha,'winner':g['winner'],'terminal_queens_agree':True,'header_submission':'14585'});print('done',gid,flush=True)
(a.snapshot/'complete-queen-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(a.snapshot/'own-supplement.json').write_text(json.dumps({'selection':sel,'checks':checks},indent=2)+'\n');print('supplemented',len(checks))
