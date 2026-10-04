"""Summarize heldout pocket sides, separating modes and resampling whole series."""
import argparse,collections,json
from pathlib import Path
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,required=True);a=ap.parse_args()
rows=list(map(json.loads,(a.snapshot/'pocket-rows.jsonl').read_text().splitlines()));held=[r for r in rows if r['cohort']];out={'games':len(held),'distinct_series':len({r['series'] for r in held}),'map_hashes':dict(collections.Counter(r['map_hash'] for r in held)),'rows':[],'bootstrap':'5000 whole-series draws seed114, ratio of reached sides; exploratory percentile95 CI; 4 geometry hashes only; not a causal effect or stable field target.'}
for mode in [True,False]:
    rr=[r for r in held if r['ranked']==mode];ss=[s for r in rr for s in r['sides']];groups=collections.defaultdict(list)
    for r in rr:groups[r['series']].extend(r['sides'])
    counts=np.array([[sum(s['checkpoints']['490']['alive'] is True for s in group),sum(s['checkpoints']['490']['reached'] for s in group)] for group in groups.values()]);rng=np.random.default_rng(114);boot=[]
    for _ in range(5000):
        draw=counts[rng.integers(0,len(counts),len(counts))].sum(axis=0);boot.append(draw[0]/draw[1])
    out['rows'].append({'mode':'ranked' if mode else 'unranked','games':len(rr),'series':len(groups),'sides':len(ss),'eligible':sum(s['trigger'] for s in ss),'first_split':sum(bool(s['initial_splits']) for s in ss),'alive25':sum(s['checkpoints']['25']['alive'] is True for s in ss),'reached490':sum(s['checkpoints']['490']['reached'] for s in ss),'alive490':sum(s['checkpoints']['490']['alive'] is True for s in ss),'survival490_ci95':np.quantile(boot,[.025,.975]).tolist(),'r0deaths':sum(s['queen_death'] is not None and s['queen_death']['round']==0 for s in ss),'late_deaths':sum(s['queen_death'] is not None and s['queen_death']['round']>0 for s in ss)})
(a.snapshot/'pocket-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
