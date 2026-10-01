"""Summarize a frozen first-live extract; a single series yields no resampled CI.
python summarize_live.py AUDIT_DIR
"""
import csv
import json
from pathlib import Path
import statistics
import sys

w=Path(sys.argv[1]);rows=[json.loads(l) for l in (w/'sides.jsonl').read_text().splitlines()]
games=[json.loads(l) for l in (w/'games.jsonl').read_text().splitlines()]
assert len(rows)==2*len(games)
assert len({(r['game'],r['side']) for r in rows})==len(rows)
us=[r for r in rows if r['team']=='7']
assert all(r['submission']=='14265' for r in us)
assert len(us)==len(games)
paired=[];summ=[]
# Published Esquie groupings only. Unspecified pool memberships remain map singletons.
cluster={'Devil':'corridor/kelp','Trauma':'corridor/kelp',
         'Portals':'portal-heavy','Default':'default/trophy','Trophy':'default/trophy',
         'Queen Of Spades':'QoS','Schooltime':'Schooltime singleton'}
for r in us:
    o=next(z for z in rows if z['game']==r['game'] and z['team']!='7')
    for cp in (25,50,100,150,250):
        for metric in ('bed_eats','bed_capture','splits','transits','territory','units','total'):
            a,b=r[f'{metric}@{cp}'],o[f'{metric}@{cp}']
            paired.append(dict(game=r['game'],map=r['map'],cluster=cluster.get(r['map'],r['map']+' singleton'),
                               ranked=r['ranked'],series_id=r['series_id'],opponent=r['opp'],
                               round=cp,metric=metric,us=a,opponent_value=b,
                               opponent_minus_us=b-a if a is not None and b is not None else None,
                               checkpoint_played=r['last_round']>=cp,
                               era='post',population='ranked' if r['ranked'] else 'unranked',
                               stability='insufficient: one series, one opponent; not a percentile'))
for ranked in (True,False):
    x=[r for r in us if r['ranked']==ranked];reach=[r for r in x if r['reached490']]
    rl=[r for r in x if r['round_limit']];loss=[r for r in rl if r['won']==0]
    leads490=[r for r in rl if r['total490']>next(z['total490'] for z in rows if z['game']==r['game'] and z['team']!='7')]
    leadsend=[r for r in rl if r['total_end']>r['opp_total_end']]
    lostlead490=[r for r in leads490 if r['won']==0];lostleadend=[r for r in leadsend if r['won']==0]
    lost=[r for r in x if r['won']==0]
    behind=lambda cp:sum(r[f'total@{cp}']<next(z[f'total@{cp}'] for z in rows if z['game']==r['game'] and z['team']!='7') for r in lost)
    summ.append(dict(ranked=ranked,n=len(x),series=len({r['series_id'] for r in x}),
                     opponents=sorted({r['opp'] for r in x}),wins=sum(r['won']==1 for r in x),
                     losses=len(lost),draws=sum(r['won']==.5 for r in x),
                     last_round_min=min(r['last_round'] for r in x),
                     queen_deaths=sum(r['queen_death_round'] is not None for r in x),
                     queen_death_round_median=statistics.median(r['queen_death_round'] for r in x),
                     reached490=len(reach),queen_alive490=sum(r['queen_alive490'] for r in reach),
                     queen_length490_median=statistics.median(r['queen_length490'] for r in reach) if reach else None,
                     round_limit=len(rl),rl_losses=len(loss),rl_material_leads490=len(leads490),
                     rl_losses_with_lead490=len(lostlead490),rl_material_leads_end=len(leadsend),
                     rl_losses_with_lead_end=len(lostleadend),
                     lost_and_material_behind25=behind(25),lost_and_material_behind50=behind(50),
                     old_decoder_disagreements=sum(r['old_decoder_disagrees'] for r in x),
                     uncertainty='No generalization CI: one independent series per population; maps and opponents unbalanced.',
                     stability='first-live diagnostic only; not a field percentile or gate reference'))
(w/'summary.json').write_text(json.dumps(summ,indent=2)+'\n')
with (w/'opening-paired.csv').open('w') as f:
    wr=csv.DictWriter(f,fieldnames=list(paired[0]));wr.writeheader();wr.writerows(paired)
groups=[]
for ranked in (True,False):
    for cl in sorted({r['cluster'] for r in paired}):
        for cp in (25,50,100,150,250):
            for metric in ('bed_eats','bed_capture','splits','transits','territory','units','total'):
                x=[r for r in paired if r['ranked']==ranked and r['cluster']==cl and r['round']==cp and r['metric']==metric]
                if not x:continue
                v=[r['opponent_minus_us'] for r in x if r['opponent_minus_us'] is not None]
                groups.append(dict(ranked=ranked,cluster=cl,round=cp,metric=metric,games=len(x),
                                   series=len({r['series_id'] for r in x}),
                                   mean_opponent_minus_us=statistics.mean(v) if v else None,
                                   checkpoint_played=sum(r['checkpoint_played'] for r in x),
                                   field_percentile=None,uncertainty='not estimable from one series',stability='insufficient'))
(w/'cluster-diagnostics.json').write_text(json.dumps(groups,indent=2)+'\n')
print(json.dumps(summ,indent=2))
