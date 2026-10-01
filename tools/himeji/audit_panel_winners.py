"""Read official headers; compare old longest/total outcome without decoding or cache writes."""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--panel',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo))
from tools.antioch.era import header
raw=(a.panel/'index.jsonl').read_bytes();idx={r['game']:r for r in map(json.loads,raw.splitlines())};rows=[]
for p in sorted((a.panel/'replays').glob('*.replay')):
 h=header(p);i=idx[p.stem];side='A' if i['botA']=='rome-01-nodevil' else 'B';assert i['bot'+side]=='rome-01-nodevil'
 if bool(h['units_a'])!=bool(h['units_b']):old='A' if h['units_a'] else 'B'
 else:
  ka=(h['longest_a'],h['total_a']);kb=(h['longest_b'],h['total_b']);old='A' if ka>kb else 'B' if kb>ka else 'draw'
 actual=h['res_winner'];runner=i.get('winner');assert runner==actual,(p,runner,actual)
 rows.append(dict(game=p.stem,map=i['map'],seed=i['seed'],side=side,old=old,official=actual,runner=runner,queen_a=h['queen_a'],queen_b=h['queen_b'],end_reason=h['res_reason'],old_score=1 if old==side else .5 if old=='draw' else 0,official_score=1 if actual==side else .5 if actual=='draw' else 0))
assert len(rows)==480
summary=dict(n=len(rows),index_sha256=hashlib.sha256(raw).hexdigest(),old_wld=[sum(r['old_score']==v for r in rows) for v in [1,0,.5]],official_wld=[sum(r['official_score']==v for r in rows) for v in [1,0,.5]],old_share=sum(r['old_score'] for r in rows)/len(rows),official_share=sum(r['official_score'] for r in rows)/len(rows),changed=sum(r['old']!=r['official'] for r in rows),runner_agrees=len(rows),flips=[r for r in rows if r['old']!=r['official']])
a.out.mkdir(parents=True,exist_ok=True);(a.out/'winner-audit.json').write_text(json.dumps(summary,indent=2)+'\n');(a.out/'winner-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));print(json.dumps(summary,indent=2))
