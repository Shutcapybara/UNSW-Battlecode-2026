"""Conditional whole-series interval on the peer's frozen h2h diagnostic, no replay decoding."""
import argparse,collections,hashlib,json,random
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--peer',type=Path,required=True);p.add_argument('--index',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
rows=[json.loads(x) for x in a.peer.read_text().splitlines() if x.startswith('{')];rows=[r for r in rows if r['who']=='us' and not r.get('bad')];ids={r['gid'] for r in rows};idx={m['game_id']:m for m in map(json.loads,a.index.read_text().splitlines()) if m['game_id'] in ids};blocks=collections.defaultdict(list)
for r in rows:blocks[idx[r['gid']]['series_id']].append(r)
z=[(sum(bool(r['fore'] and r['alt4']) for r in b),len(b)) for b in blocks.values()];rng=random.Random(3030);boot=[]
for _ in range(4000):
    b=[rng.choice(z) for j in range(len(z))];boot.append(sum(x for x,n in b)/sum(n for x,n in b))
boot.sort();out=dict(n=len(rows),positive=sum(x for x,n in z),series=len(z),ci95=[boot[int(.025*len(boot))],boot[int(.975*len(boot))]],replicates=4000,seed=3030,ranked_cases=sum(idx[r['gid']]['ranked'] for r in rows),blocks=[dict(series=k,positive=sum(bool(r['fore'] and r['alt4']) for r in v),n=len(v)) for k,v in blocks.items()],source_sha256=hashlib.sha256(a.peer.read_bytes()).hexdigest(),scope='Descriptive interval conditional on selected96 sample and approximate labels; series resampling does not correct selection/measurement bias. Frozen point-threshold decision is distinct from population falsification.')
a.out.write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='blocks'})
