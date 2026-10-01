"""Frozen Cutlery audit summaries, ranked/unranked and map separated.
python summarize_cutlery.py AUDIT_DIR
"""
import collections
import json
from pathlib import Path
import sys
import numpy as np

w = Path(sys.argv[1])
rs = [json.loads(l) for l in (w/'action-rows.jsonl').read_text().splitlines()]
assert len(rs) == json.loads((w/'manifest.json').read_text())['selected']
assert len({r['game'] for r in rs}) == len(rs)
POCKET = {'Autarky','Slithery Fight','Prisoners Dilemma'}
for r in rs:
    r['after13'] = r['started'] >= '2026-10-01T13:00'
    r['pocket'] = r['map'] in POCKET
    r['invalid'] = r['q_death_cause'] == 'invalid'


def stats(x):
    rl = [r for r in x if r['official_rl']]
    return dict(n=len(x), series=len({r['series_id'] for r in x}),
                maps=dict(collections.Counter(r['map'] for r in x)),
                deaths=sum(r['q_death_cause'] is not None for r in x),
                causes=dict(collections.Counter(r['q_death_cause'] or 'survived_end' for r in x)),
                invalid_actions=dict(collections.Counter(str((r['death_action']or{}).get('kind')) for r in x if r['invalid'])),
                invalid_tle=sum(bool(r['death_action']['tle']) for r in x if r['invalid']),
                invalid_same_round=sum(r['death_action']['round']==r['q_death_round'] for r in x if r['invalid']),
                reach490=sum(r['reached490'] for r in x), alive490=sum(r['alive490'] for r in x),
                clipped_positive=sum(r['q_len490']>0 for r in x),
                positive_early_end=sum(r['q_len490']>0 and not r['reached490'] for r in x),
                rl_n=len(rl), rl_final_alive=sum(r['queen_final']>0 for r in rl),
                wins=sum(r['official_won'] for r in x))


out = dict(n=len(rs), groups=[], map_groups=[])
for ranked in (True,False):
    for after in (False,True):
        x=[r for r in rs if r['ranked']==ranked and r['after13']==after]
        out['groups'].append(dict(ranked=ranked,after13=after,**stats(x)))
        for m in sorted({r['map'] for r in x}):
            out['map_groups'].append(dict(ranked=ranked,after13=after,map=m,**stats([r for r in x if r['map']==m])))

ranked=[r for r in rs if r['ranked']]
periods=[[r for r in ranked if r['after13']==a] for a in (False,True)]
series=[collections.defaultdict(list) for _ in periods]
for d,x in zip(series,periods):
    for r in x:
        d[r['series_id']].append(r)
assert not (set(series[0]) & set(series[1])), 'Series crosses cutoff: paired block design required'
rng=np.random.default_rng(6123)


def rate(x,metric,nonpocket=False):
    x=[r for r in x if not (nonpocket and r['pocket'])]
    if metric=='rl_final_alive':
        x=[r for r in x if r['official_rl']]
        return np.mean([r['queen_final']>0 for r in x]) if x else float('nan')
    return np.mean([r[metric] for r in x]) if x else float('nan')


def resample(d):
    keys=list(d)
    return [r for i in rng.integers(0,len(keys),len(keys)) for r in d[keys[i]]]

out['contrasts']=[]
for metric,npocket in [('invalid',False),('invalid',True),('rl_final_alive',False)]:
    boot=[]
    for _ in range(2000):
        a,b=[resample(d) for d in series]
        boot.append(rate(b,metric,npocket)-rate(a,metric,npocket))
    out['contrasts'].append(dict(metric=metric,nonpocket=npocket,
                               before=rate(periods[0],metric,npocket),after=rate(periods[1],metric,npocket),
                               difference=rate(periods[1],metric,npocket)-rate(periods[0],metric,npocket),
                               ci95=np.nanquantile(boot,[.025,.975]).tolist(),
                               independent_series=[len(d) for d in series],replicates=2000))
out['uncertainty']='Independent series-block percentile bootstrap within before/after windows; descriptive temporal association, no map/opponent randomization or deployment fingerprint.'
(w/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='map_groups'},indent=2))
