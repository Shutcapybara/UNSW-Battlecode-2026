"""Read-only audit of frozen peer rows; only top-ten rows need full decoding."""
import argparse, collections, hashlib, json, sys
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,required=True); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--peer-rows',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
sys.path.insert(0,str(a.repo))
from tools.analysis.features.frame import decode
from tools.antioch.era import header
raw=a.peer_rows.read_bytes(); peer=[json.loads(x) for x in raw.splitlines()]
idxraw=(a.corpus/'index.jsonl').read_bytes(); idx={r['game_id']:r for r in map(json.loads,idxraw.splitlines())}
rows=[]
for r in peer:
    if r.get('cohort')!='top10': continue
    m=idx[int(r['game'])]; p=a.corpus/'replays'/f"{r['game']}.replay"; g=decode(p); h=header(p)
    side=r['side']; q=r['q0']; reach=g['last_round']>=490
    snap=g['rounds'][490] if reach else {}; qlen=len(snap[q][1]) if q in snap else None if not reach else 0
    rows.append(dict(game=int(r['game']),team=r['team'],side=side,map=r['map'],ranked=m.get('ranked'),series_id=m.get('series_id'),started=m['started_at'],last_round=g['last_round'],reached490=reach,peer_q490=r['q_len@490'],q490=qlen,peer_won=r['won'],official_won=h['res_winner']==side,official_end=h['res_reason'],q_eats=r['q_eats'],q_moves=r['q_head_moves'],queen_final=h['queen_'+side.lower()]))
    print(f"{len(rows)} {r['game']}",file=sys.stderr,flush=True)
cut=[r for r in rows if r['team']==306]
summary=dict(peer_sha256=hashlib.sha256(raw).hexdigest(),index_sha256=hashlib.sha256(idxraw).hexdigest(),index_unique=len(idx),latest_start=max(r.get('started_at') or '' for r in idx.values()),post_us_games=sum(r.get('started_at','')>='2026-10-01T06:00' and 7 in (r['team_a'],r['team_b']) for r in idx.values()),gap_games=sum('2026-10-01T06:00'<=r.get('started_at','')<'2026-10-01T09:00' for r in idx.values()),peer_side_rows=len(peer),top10_rows=len(rows),top10_peer_positive=sum(r['peer_q490']>0 for r in rows),top10_reached=sum(r['reached490'] for r in rows),top10_actual_positive=sum((r['q490'] or 0)>0 for r in rows),top10_false_checkpoint=sum(r['peer_q490']>0 and not r['reached490'] for r in rows),top10_winner_errors=sum(r['peer_won']!=r['official_won'] for r in rows),cutlery_rows=cut)
a.out.mkdir(parents=True,exist_ok=True)
(a.out/'peer-queen-audit.json').write_text(json.dumps(summary,indent=2)+'\n'); (a.out/'peer-queen-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); print(json.dumps(summary,indent=2))
