"""Summarize a frozen Himeji sample; per-map percentiles before cluster pooling."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--repo',required=True)
    a=p.parse_args();base=Path(a.input);sys.path.insert(0,a.repo)
    from tools.esquie.signature import cluster
    from tools.himeji.post_refs import percentile
    manifest=json.loads((base/'manifest.json').read_text())
    top={str(t['id']) for t in manifest['top10']}
    rows=[json.loads(l) for l in (base/'sides.jsonl').read_text().splitlines()]
    d=pd.DataFrame([r for r in rows if 'error' not in r]);d['team']=d.team.astype(str);d['top10']=d.team.isin(top)
    assert d.game.nunique()==manifest['sample_games'] and len(d)==2*manifest['sample_games']
    refs=pd.read_csv(base/'references.csv')
    signatures=json.loads((base/'signatures.json').read_text());groups=cluster(signatures,8)
    lookup={signatures[i]['map']:f'c{k}' for k,ids in enumerate(groups) for i in ids}
    names={'Autarky':'autarky','Default':'default','Devil':'devil','Portals':'portals',
           'Prisoners Dilemma':'dilemma','Prisoners Dilemma 10':'dilemma','Queen Of Spades':'queen_of_spades',
           'Schooltime':'schooltime','Slithery Fight':'slithery_fight','Trauma':'trauma','Trophy':'trophy'}
    refs['cluster']=refs['map'].map(lambda m:lookup[names[m]])
    refs.to_csv(base/'references.csv',index=False)
    mapping=[dict(map=m,signature_map=names[m],cluster=lookup[names[m]]) for m in sorted(d['map'].unique())]
    pd.DataFrame(mapping).to_csv(base/'cluster_map.csv',index=False)
    # Every cluster is the equal-map average of its top-ten median field percentile.
    # Do not pool raw scales or count repeated teams as independent teams.
    agg=refs.groupby(['cluster','metric']).agg(maps=('map','nunique'),top10_field_pct=('top10_field_pct','mean'),
        field_sides=('field_sides','sum'),top10_sides=('top10_sides','sum'),us_sides=('us_sides','sum')).reset_index()
    agg['era']='post';agg['top10_minus_us']=np.nan;agg['status']='provisional; no post-era us comparator'
    agg.to_csv(base/'cluster_references.csv',index=False)
    dist={metric:{m:sorted(pd.to_numeric(g[metric],errors='coerce').dropna().tolist()) for m,g in d.groupby('map')}
          for metric in refs.metric.unique()}
    (base/'distributions.json').write_text(json.dumps(dist,indent=1,allow_nan=False))
    # Game/series-cluster bootstrap of both field ECDF and top-ten median.
    rng=np.random.default_rng(20261001);unc=[]
    metrics=['bed_eats@50','bed_capture@50','splits@50','transits@50','territory@50','queen_alive490','queen_length490']
    for m,g in d.groupby('map'):
        for metric in metrics:
            z=g[['game','series_id','team','top10',metric]].dropna(subset=[metric]).copy()
            z['block']=z.series_id.fillna(z.game)
            blocks=[gg for _,gg in z.groupby('block')];values=[]
            xs=[b[metric].to_numpy(float) for b in blocks]
            ys=[b.loc[b.top10,metric].to_numpy(float) for b in blocks]
            for _ in range(500):
                if not blocks:break
                chosen=rng.integers(len(blocks),size=len(blocks))
                x=np.concatenate([xs[i] for i in chosen])
                y=np.concatenate([ys[i] for i in chosen])
                if len(y):values.append(percentile(x,float(np.median(y)),'up'))
            unc.append(dict(map=m,metric=metric,blocks=len(blocks),valid_bootstraps=len(values),
                pct_lo=float(np.quantile(values,.025)) if values else None,
                pct_hi=float(np.quantile(values,.975)) if values else None,status='provisional'))
    pd.DataFrame(unc).to_csv(base/'uncertainty.csv',index=False)
    q=d[d.reached490]
    print('sample',len(d),'sides; top10',int(d.top10.sum()),'teams',d.loc[d.top10,'team'].nunique())
    print('queen alive r490',int(q.queen_alive490.sum()),'/',len(q),'median length',q.queen_length490.median())
    print('queen alive END',int(d.loc[d.round_limit,'queen_alive_end'].sum()),'/',int(d.round_limit.sum()))
    print('r490 top10',q.loc[q.top10,'queen_alive490'].sum(),'/',int(q.top10.sum()))
    print('sprint commands',int(d.sprint_commands.sum()),'deaths on sprint round',int(d.deaths_on_sprint_round.sum()),
          'steps per move',d.commanded_steps.sum()/d.move_commands.sum())
    opening=refs[refs.metric.isin(metrics[:5])].pivot(index='map',columns='metric',values='top10_field_pct').round(3).to_string()
    print('OPENING');print('\n'.join(line.rstrip() for line in opening.splitlines()))
    print('ENDGAME');print(pd.read_csv(base/'endgame.csv').query("map=='ALL'").to_string(index=False))


if __name__=='__main__':main()
