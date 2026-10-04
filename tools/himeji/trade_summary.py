"""Summarize a frozen matched trade audit; exploratory connected-series uncertainty."""
import argparse,collections,json
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
sides=[json.loads(x) for x in (a.data/'trade-sides.jsonl').read_text().splitlines()]
paths=sorted(a.data.glob('trade-events-*.jsonl')) or [a.data/'trade-events.jsonl']
trades=[json.loads(x) for f in paths for x in f.read_text().splitlines()]
rng=np.random.default_rng(3434);result=[];cohort=[]
for name in sorted({r['map'] for r in sides}):
    ss=[r for r in sides if r['map']==name];parents={r['series_id']:r['series_id'] for r in ss}
    def find(k):
        while parents[k]!=k:k=parents[k]
        return k
    for pair in {r['pair'] for r in ss}:
        x,y=[r['series_id'] for r in ss if r['pair']==pair];parents[find(y)]=find(x)
    blocks=sorted({find(k) for k in parents});bid={s:i for i,s in enumerate(blocks)}
    groups={co:[r for r in ss if r['cohort']==co] for co in ('us','field')}
    data={co:np.array([[bid[find(r['series_id'])],r['counts'].get('mover',0),r['counts'].get('enemy_h2h',0)] for r in group],float) for co,group in groups.items()}
    def delta(w):
        rates=[]
        for co in ('us','field'):
            z=data[co];weights=w[z[:,0].astype(int)];rates.append(float(np.sum(weights*z[:,1])/np.sum(weights*z[:,2])))
        return rates[1]-rates[0]
    boot=[]
    for _ in range(4000):
        w=rng.multinomial(len(blocks),np.full(len(blocks),1/len(blocks)));boot.append(delta(w))
    result.append(dict(map=name,pairs=len(groups['us']),fullhashes=len({r['map_hash'] for r in ss}),connected_series_blocks=len(blocks),field_minus_us_mover_share=delta(np.ones(len(blocks))),bootstrap95=np.quantile(boot,[.025,.975]).tolist()))
    for co,gg in groups.items():
        tt=[t for t in trades if t['map']==name and t['cohort']==co];cc=collections.Counter()
        for r in gg:cc.update(r['counts'])
        def stats(v):return dict(n=len(v),**{k:float(np.mean([t[k] for t in v])) if v else None for k in ['mover_length','partner_length','length_advantage','capture_advantage','material_advantage','mover_net','partner_net']})
        eq=[t for t in tt if t['mover_length']==t['partner_length']]
        # Descriptive payoff CI, series resampling in each cohort; no causal interpretation.
        sids=sorted({r['series_id'] for r in gg});sums=np.array([[sum(t['capture_advantage'] for t in eq if t['series_id']==s),sum(t['series_id']==s for t in eq)] for s in sids],float)
        bs=[]
        for _ in range(4000):
            w=rng.multinomial(len(sids),np.full(len(sids),1/len(sids)));n=np.sum(w*sums[:,1])
            if n:bs.append(float(np.sum(w*sums[:,0])/n))
        cohort.append(dict(map=name,cohort=co,games=len(gg),series=len(sids),counts=dict(cc),dragon_turns=sum(r['dragon_turns'] for r in gg),mover_share=cc['mover']/cc['enemy_h2h'],trade_payoff=stats(tt),equal_length_payoff=stats(eq),equal_capture_series95=np.quantile(bs,[.025,.975]).tolist()))
assert all(t['material_advantage']==t['length_advantage']+t['capture_advantage'] for t in trades)
out=dict(contract='All counts r>=150; payoffs require death<=actual last round-50, donor+birth+cell identity and at most50round capture. Death-role fraction conditions on enemy h2h, not contact opportunity/causal initiation rate. Samehash/seat time matching, opponents not matched. 4000 connected-series cluster bootstrap for per-map field-us share; payoff equal-length CI ordinary whole-series bootstrap; seed3434. Small samples, exploratory.',games=len(sides),trades=len(trades),matched_map_differences=result,cohorts=cohort)
a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(result,indent=2));print([(r['map'],r['cohort'],r['equal_capture_series95']) for r in cohort])
