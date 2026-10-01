"""Attach frozen structural clusters and observed live percentiles, with missing gaps explicit.
python annotate_ranked_refs.py AUDIT_DIR LIVE_SIDES CLUSTER_MAP
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

w=Path(sys.argv[1]);livepath=Path(sys.argv[2]);clusterpath=Path(sys.argv[3])
r=pd.read_csv(w/'ranked-references.csv');d=pd.read_csv(w/'opening-rows.csv',dtype={'game':str,'team':str})
live=[x for x in map(json.loads,livepath.read_text().splitlines()) if x['team']=='7' and x['ranked']]
clusters=dict(pd.read_csv(clusterpath)[['map','cluster']].values)
out=[]
for row in r.to_dict('records'):
    m,cp,metric=row['map'],int(row['round']),row['metric']
    x=[z for z in live if z['map']==m]
    field=d[d.ranked & (d['map']==m) & (d['round']==cp)][metric].dropna().to_numpy(float)
    v=[z[f'{metric}@{cp}'] for z in x if z[f'{metric}@{cp}'] is not None]
    us=float(np.median(v)) if v else None
    pct=float(np.mean(field<us)+.5*np.mean(field==us)) if us is not None else None
    row.update(cluster=clusters.get(m,'unassigned replay-label variant'),us_sides=len(v),
               live_series=len({z['series_id'] for z in x}),us_median=us,us_field_percentile=pct,
               descriptive_top10_minus_us=float(row['top10_median']-us) if us is not None else None,
               top10_minus_us=None,contrast_ci=None,
               comparison_label='unmatched earlier-field vs one later live series; no inferential gap')
    out.append(row)
pd.DataFrame(out).to_csv(w/'annotated-references.csv',index=False)
meta=dict(live_source=str(livepath),live_sha256=hashlib.sha256(livepath.read_bytes()).hexdigest(),
          clusters_source=str(clusterpath),clusters_sha256=hashlib.sha256(clusterpath.read_bytes()).hexdigest(),
          live_ranked_games=len(live),live_series=len({z['series_id'] for z in live}),
          description='Unit1 frozen computed signature clusters, not unit7 prose groupings. PD10 has no verified assignment.')
(w/'annotation-provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
print(pd.DataFrame(out).query('round == 50 and metric == "total"')[['map','cluster','top10_median','us_sides','us_median','us_field_percentile','descriptive_top10_minus_us']].to_string(index=False))
