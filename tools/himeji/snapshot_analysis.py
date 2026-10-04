"""Recent top-team mode/identity coverage, with series-bootstrap uncertainty; no API."""
import argparse,collections,datetime,hashlib,json
from pathlib import Path
import numpy as np

def parse(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('snapshot',type=Path);a=ap.parse_args();m=json.loads((a.snapshot/'manifest.json').read_text());idx={r['game_id']:r for r in map(json.loads,(a.snapshot/'index.jsonl').read_text().splitlines())};end=parse(m['at']);start=end-datetime.timedelta(hours=24);top=m['top10'];ids=[t['id'] for t in top]+[7];rows=[];audit=[]
 for tid in ids:
  rr=[]
  for r in idx.values():
   if tid not in (r.get('team_a'),r.get('team_b')) or not r.get('started_at') or not start<=parse(r['started_at'])<=end or r.get('status')!='completed':continue
   s='a' if tid==r['team_a'] else 'b';w=r.get('winner');score=1 if w==s else 0 if w in ['a','b'] else .5 if w in ['draw','tie'] else None
   rr.append(dict(team=tid,game=r['game_id'],series=r['series_id'],map=r['map_name'],map_hash=r['map_hash'],ranked=r['ranked'],side=s,opponent=r['team_b' if s=='a' else 'team_a'],started_at=r['started_at'],score=score,submission=r.get('sub_'+s),header=r.get('bot_'+s),sha256=r['sha256']))
  audit+=rr
  for mode in [True,False]:
   x=[r for r in rr if r['ranked']==mode];groups=collections.defaultdict(list)
   for r in x:
    if r['score'] is not None:groups[r['series'] or 'game:'+str(r['game'])].append(r['score'])
   vals=list(groups.values());rng=np.random.default_rng(104);boot=[]
   if len(vals)>=2:
    sums=np.array([sum(v) for v in vals]);ns=np.array([len(v) for v in vals])
    for _ in range(1000):
     ix=rng.integers(0,len(vals),len(vals));boot.append(float(sums[ix].sum()/ns[ix].sum()))
   scores=[r['score'] for r in x if r['score'] is not None]
   rows.append(dict(team=tid,mode='ranked' if mode else 'unranked',games=len(x),series=len(groups),wins=sum(s==1 for s in scores),losses=sum(s==0 for s in scores),draws=sum(s==.5 for s in scores),unknown_winner=len(x)-len(scores),score=float(np.mean(scores)) if scores else None,score_ci95=np.quantile(boot,[.025,.975]).tolist() if boot else None,maps=len({r['map'] for r in x}),opponents=len({r['opponent'] for r in x}),known_submission=sum(r['submission'] is not None for r in x),nonempty_header=sum(bool(r['header']) for r in x),stability='insufficient: stale selective collection and few series'))
  # Matched map/seat/opponent/UTC-day support only, never a causal mode effect.
  sets={mode:{(r['map_hash'],r['side'],r['opponent'],r['started_at'][:10]) for r in rr if r['ranked']==mode} for mode in [True,False]}
  for x in rows[-2:]:x['matched_mode_strata']=len(sets[True]&sets[False])
 summary=dict(window_start=start.isoformat(),window_end=end.isoformat(),cohort='current ladder top10 plus us; retrospectively selected',era='post123 by accepted 2026-10-01T06:00Z cut; renewed pricing audit pending',rows=rows,method='1000 whole-series bootstrap draws, seed104; descriptive collected games, not population census; no interval with fewer than2series',warning='A ranked-unranked gap is not evidence of spoofing; unknown IDs and unequal opponent/map/time mixtures retained')
 (a.snapshot/'mode-coverage.json').write_text(json.dumps(summary,indent=2)+'\n');(a.snapshot/'recent-side-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in audit))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
