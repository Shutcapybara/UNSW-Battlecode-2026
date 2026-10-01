"""Verify the peer artifact's termination labels, without changing it."""
import json,sys
from pathlib import Path
sys.path.insert(0,'/Users/alik/Documents/Projects/wt-himeji')
from tools.antioch.era import header
w=Path(sys.argv[1]);rs=[json.loads(l) for l in (w/'cutlery-source-rows.jsonl').read_text().splitlines()];out=[]
for n,r in enumerate(rs,1):
 h=header(Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026/public_replays/corpus/replays')/f"{r['game']}.replay")
 out.append(dict(game=r['game'],ranked=r['ranked'],started=r['started'],side=r['side'],peer_rl=r['round_limit'],official_rl=h['res_reason']==1,peer_won=r['won'],official_won=h['res_winner']==r['side'],q490=r['q_len@490'],queen_final=h['queen_'+r['side'].lower()]))
 if n%25==0:print(n,flush=True)
(w/'cutlery-header-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in out));s=dict(n=len(out),rl_disagreements=sum(r['peer_rl']!=r['official_rl'] for r in out),winner_disagreements=sum(r['peer_won']!=r['official_won'] for r in out),groups=[])
for ranked in [False,True]:
 for after in [False,True]:
  r=[x for x in out if x['ranked']==ranked and (x['started']>='2026-10-01T13:00')==after];rl=[x for x in r if x['official_rl']]
  s['groups'].append(dict(ranked=ranked,after13=after,n=len(r),rl_n=len(rl),q490_positive_in_rl=sum(x['q490']>0 for x in rl),final_positive_in_rl=sum(x['queen_final']>0 for x in rl)))
(w/'cutlery-header-summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s),flush=True)
