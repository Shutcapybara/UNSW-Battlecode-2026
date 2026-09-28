"""Reports for bot_similarity.py; observed correlations and fitted style clusters."""
import csv
import html
import json
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, leaves_list, dendrogram
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.special import expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from performance_model import fit, unpack, subset
from bot_field_report import correlations


def table(path, rows):
    with path.open('w', newline='') as file:
        writer=csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def matrix_csv(path, labels, matrix):
    with path.open('w', newline='') as file:
        writer=csv.writer(file); writer.writerow(['bot']+labels)
        for label,row in zip(labels,matrix):
            writer.writerow([label]+[float(v) if np.isfinite(v) else '' for v in row])


def components(model,n,m,core):
    s,t,b,u,v=unpack(model['x'],n,m,model['q'],model['maps'])
    c=u@v.T-v@u.T
    # Remove the transitive component hidden in the factorization; absorb it
    # into s so the full fitted prediction is unchanged.
    mean=c.mean(axis=1); tm=t.mean(axis=1)
    c=c-mean[:,None]+mean[None,:]
    s=s+mean+tm
    t=t-tm[:,None]; t=t-t.mean(axis=0)
    features=(t[:,None,:]-t[core][None,:,:]+c[:,core,None]).reshape(n,-1)
    return s,t,b,c,features


def silhouette(x, assignments):
    d=squareform(pdist(x)); result=[]
    for i in range(len(x)):
        same=np.flatnonzero(assignments==assignments[i])
        if len(same)==1:
            result.append(0.);continue
        a=d[i,same].sum()/(len(same)-1)
        b=min(d[i,assignments==k].mean() for k in set(assignments) if k!=assignments[i])
        result.append((b-a)/max(a,b))
    return float(np.mean(result))


def report(out,data,meta,model):
    n,m=len(meta['labels']),len(meta['maps']);labels=meta['labels'];core=np.array(meta['core'])
    s,t,b,c,F=components(model,n,m,core)
    X=F[core]; center=X.mean(axis=0); xc=X-center
    _,sv,vt=np.linalg.svd(xc,full_matrices=False)
    embedding=(F-center)@vt[:2].T
    explained=sv**2/np.sum(sv**2)
    z=linkage(X,method='ward',optimal_ordering=True)
    assignments=fcluster(z,5,criterion='maxclust')
    broad=fcluster(z,2,criterion='maxclust')
    order=leaves_list(z)
    sils={str(k):silhouette(X,fcluster(z,k,criterion='maxclust')) for k in range(2,9)}
    centers=np.stack([X[assignments==k].mean(axis=0) for k in range(1,6)])
    all_assign=np.argmin(cdist(F,centers),axis=1)+1;all_assign[core]=assignments
    core_distance=squareform(pdist(X))
    medoids={k:int(core[np.flatnonzero(assignments==k)[np.argmin(
        core_distance[np.ix_(assignments==k,assignments==k)].sum(axis=1))]]) for k in range(1,6)}

    # Resample whole unordered pairs, retaining all maps and both sides together.
    # This measures sensitivity to observed-pair sampling, not tournament-completion certainty.
    a,d,board,y=data; group=np.minimum(a,d)*n+np.maximum(a,d)
    unique=np.unique(group); index={g:np.flatnonzero(group==g) for g in unique}
    rng=np.random.default_rng(724);coassign=np.zeros((len(core),len(core)))
    bootfile=out/'bootstrap_coassignment.npy'
    if bootfile.exists():
        coassign=np.load(bootfile)
    else:
        for repeat in range(20):
            sampled=np.concatenate([index[g] for g in rng.choice(unique,len(unique),replace=True)])
            fitted=fit(subset(data,sampled),n,m,model['q'],model['maps'],model['ridge'],start=model)
            _,_,_,_,bf=components(fitted,n,m,core)
            bz=linkage(bf[core],method='ward');bc=fcluster(bz,5,criterion='maxclust')
            coassign+=(bc[:,None]==bc[None,:])/20
            print('Cluster stability',repeat+1,'/ 20',flush=True)
        np.save(bootfile,coassign)
    stability=np.array([np.mean(coassign[i,(assignments==assignments[i]) & (np.arange(len(core))!=i)])
                        for i in range(len(core))])

    # Observable check: only paired sides enter a bot/opponent/map profile.
    total=np.zeros((n,n,m)); count=np.zeros((n,n,m),int)
    np.add.at(total,(a,d,board),y); np.add.at(total,(d,a,board),1-y)
    np.add.at(count,(a,d,board),1); np.add.at(count,(d,a,board),1)
    observed=np.full_like(total,np.nan);paired=count==2
    observed[paired]=total[paired]/2
    corr,shared=correlations(observed,minimum=30)
    matrix_csv(out/'observed_correlation.csv',labels,corr)
    matrix_csv(out/'observed_shared_counts.csv',labels,shared)
    table(out/'map_affinities.csv',[dict(bot=labels[i],**{meta['maps'][j][0]:t[i,j] for j in range(m)}) for i in range(n)])
    matrix_csv(out/'cyclic_matchup_logits.csv',labels,c)
    matrix_csv(out/'style_distances.csv',labels,cdist(F,F)/np.sqrt(F.shape[1]))
    matrix_csv(out/'bootstrap_coassignment.csv',[labels[i] for i in core],coassign)

    # Equal-map, equal-original-opponent expected score, with both initiatives.
    margin=s[:,None,None]-s[core][None,:,None]+t[:,None,:]-t[core][None,:,:]+c[:,core,None]
    fair=(expit(margin+b[None,None,:])+expit(margin-b[None,None,:]))/2
    for j,i in enumerate(core):fair[i,j]=np.nan
    fair_score=np.nanmean(fair,axis=(1,2))
    rows=[]
    for i in range(n):
        mask=(a==i)|(d==i);opponents=set(d[a==i])|set(a[d==i])
        nearest=sorted((np.linalg.norm(F[i]-F[j])/np.sqrt(F.shape[1]),j) for j in core if j!=i)[:3]
        valid=[j for j in range(n) if j!=i and np.isfinite(corr[i,j])]
        best=max(valid,key=lambda j:corr[i,j]) if valid else None
        where=np.flatnonzero(core==i)
        original_hashes=sorted({v['source_sha256'] for v in meta['source_aliases'] if
                               (v['name'],v['analysis_sha256'])==tuple(meta['identities'][i])})
        rows.append(dict(bot=labels[i],name=meta['identities'][i][0],analysis_sha256=meta['identities'][i][1],
                         original_source_hashes=';'.join(original_hashes),
                         cluster=int(all_assign[i]),original=bool(len(where)),unique_games=int(mask.sum()),
                         opponents=len(opponents),maps=len(set(board[mask])),general_strength=float(s[i]),
                         equal_field_expected_score=float(fair_score[i]),pc1=float(embedding[i,0]),pc2=float(embedding[i,1]),
                         within_cluster_bootstrap=float(stability[where[0]]) if len(where) else '',
                         nearest_model_profile=labels[nearest[0][1]],nearest_model_distance=float(nearest[0][0]),
                         nearest_observed_profile=labels[best] if best is not None else '',
                         observed_correlation=float(corr[i,best]) if best is not None else '',
                         observed_shared_cells=int(shared[i,best]) if best is not None else 0,
                         support='field coverage' if len(where) else 'sparse projection; cluster provisional'))
    table(out/'bots.csv',rows)
    top_pairs=sorted([(float(corr[i,j]),int(shared[i,j]),labels[i],labels[j]) for i in core for j in core
                       if i<j and np.isfinite(corr[i,j]) and shared[i,j]>=40],reverse=True)
    table(out/'closest_observed_pairs.csv',[dict(bot_a=x,bot_b=y,correlation=r,shared_cells=k) for r,k,x,y in top_pairs])
    newcomer_pairs=sorted([(float(corr[i,j]),int(shared[i,j]),labels[i],labels[j]) for i in range(n) for j in range(i+1,n)
                           if (i not in core or j not in core) and np.isfinite(corr[i,j])],reverse=True)
    table(out/'newer_observed_pairs.csv',[dict(bot_a=x,bot_b=y,correlation=r,shared_cells=k) for r,k,x,y in newcomer_pairs])
    groups=[]
    for k in range(1,6):
        selected=core[assignments==k];aff=t[selected].mean(axis=0)
        groups.append(dict(cluster=k,size=len(selected),medoid=labels[medoids[k]],
                           members=[labels[i] for i in selected],
                           mean_expected_score=float(fair_score[selected].mean()),
                           bootstrap=float(stability[assignments==k].mean()),
                           map_affinity={meta['maps'][j][0]:float(aff[j]) for j in range(m)},
                           projections=[labels[i] for i in range(n) if i not in core and all_assign[i]==k]))
    original_shared=shared[np.ix_(core,core)][np.triu_indices(len(core),1)]
    facts=dict(explained_variance=explained.tolist(),silhouette=sils,groups=groups,
               empirical_pair_support=dict(min=int(original_shared.min()),median=float(np.median(original_shared)),
                                           max=int(original_shared.max())),
               original_paired_map_cells=int(paired[np.ix_(core,core,np.arange(m))].sum()//2),
               original_possible_pair_maps=len(core)*(len(core)-1)//2*m,
               broad_groups=[[labels[i] for i in core[broad==k]] for k in (1,2)],
               initiative={meta['maps'][j][0]:float(b[j]) for j in range(m)},
               cyclic_singular_values=np.linalg.svd(c,compute_uv=False).tolist())
    (out/'clusters.json').write_text(json.dumps(facts,indent=2)+'\n')

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    colors=['#176a87','#b06024','#737886','#569252','#925b9a']
    fig,ax=plt.subplots(figsize=(12,8))
    for k in range(1,6):
        selected=core[assignments==k]
        ax.scatter(*embedding[selected].T,s=55,c=colors[k-1],label=f'Group {k} · {len(selected)} original bots',alpha=.85)
        i=medoids[k]
        ax.annotate(labels[i],embedding[i],xytext=(7,10),textcoords='offset points',fontsize=9,
                    bbox=dict(facecolor='white',alpha=.8,edgecolor='none'))
    newcomers=np.array([i for i in range(n) if i not in core])
    ax.scatter(*embedding[newcomers].T,s=45,facecolors='none',edgecolors='#272f36',marker='^',alpha=.65,
               label=f'{len(newcomers)} newer source versions · provisional')
    ax.axhline(0,color='#ddd',lw=.6);ax.axvline(0,color='#ddd',lw=.6)
    ax.set(xlabel=f'Style PC1 ({explained[0]:.1%})',ylabel=f'Style PC2 ({explained[1]:.1%})')
    ax.set_title('Performance style after removing overall strength\nMap preferences + cyclic matchups; proximity is model-based.',pad=14)
    ax.legend(loc='best',fontsize=9);fig.tight_layout();fig.savefig(out/'style_embedding.png',dpi=170);plt.close(fig)

    fig,ax=plt.subplots(figsize=(12,4.8))
    aff=np.stack([t[core[assignments==k]].mean(axis=0) for k in range(1,6)])
    limit=max(abs(aff.min()),abs(aff.max()));im=ax.imshow(aff,cmap='RdBu',vmin=-limit,vmax=limit,aspect='auto')
    ax.set_xticks(range(m),[v[0] for v in meta['maps']],rotation=35,ha='right')
    ax.set_yticks(range(5),[f'Group {k} · n={len(core[assignments==k])}' for k in range(1,6)])
    ax.set_title('Map affinities: relative strengths after removing overall skill')
    fig.colorbar(im,ax=ax,label='Centered logit-score effect (blue = relative advantage)')
    fig.tight_layout();fig.savefig(out/'map_affinities.png',dpi=170);plt.close(fig)

    ordered=core[order];names=[labels[i] for i in ordered]
    fig,ax=plt.subplots(figsize=(19,18))
    cmap=plt.get_cmap('RdBu').copy();cmap.set_bad('#d9dce0')
    im=ax.imshow(corr[np.ix_(ordered,ordered)],cmap=cmap,vmin=-1,vmax=1)
    ax.set_xticks(range(len(core)),names,rotation=90,fontsize=5.5);ax.set_yticks(range(len(core)),names,fontsize=5.5)
    ax.set_title('Observed common-opponent × map correlation · original 85 bots\nBoth sides required; ≥30 shared cells; ordered by fitted style',fontsize=16,pad=18)
    fig.colorbar(im,ax=ax,shrink=.45,label='Pearson r; grey = insufficient or constant data')
    fig.tight_layout();fig.savefig(out/'observed_correlation.png',dpi=170);plt.close(fig)

    fig,ax=plt.subplots(figsize=(13,17))
    dendrogram(z,labels=[labels[i] for i in core],orientation='right',leaf_font_size=7,ax=ax,color_threshold=0,above_threshold_color='#486581')
    ax.set_title('Hierarchical style similarity · all fitted dimensions');ax.set_xlabel('Ward linkage distance')
    fig.tight_layout();fig.savefig(out/'dendrogram.png',dpi=140);plt.close(fig)

    validation=json.loads((out/'validation.json').read_text())
    text=[f'# Bot performance similarity — {meta["snapshot_at"]}\n',
          f'{meta["snapshot_games"]:,} ledger games; {meta["unique_fixtures"]:,} unique native fixtures; '
          f'{n} source versions; {len(core)} original bots. Frozen input: `games.parquet`.\n',
          '## Model and validation\n',
          'Expected game score (win=1, draw=0.5, loss=0) uses logistic strength differences, '
          'map-specific strength differences, map-specific side bias, and a low-rank skew-symmetric interaction. '
          'Missing fixtures are omitted from the loss, never filled with draws. Genuine code/config revisions remain distinct; '
          'Markdown-only changes excluded by the frozen packaging config are combined in this analysis. '
          'The shared ledger retains every original source hash; snapshot.json records the identity mapping. '
          'Repeated identical analysis fixtures receive one vote. Only native unswbc 1.0.0 is analyzed.\n',
          'Entire unordered bot pairs (all maps and both sides) were partitioned into training/validation/test. '
          'Model choice used validation only; test results are held-out pair predictions, not a claim about unseen lineages.\n',
          '| Model | Validation log loss | Test log loss | Test score MSE |\n|---|---:|---:|---:|']
    for result in validation['models']:
        text.append(f'| {result["name"]} | {result["validation"]["log_loss"]:.5f} | {result["test"]["log_loss"]:.5f} | {result["test"]["brier"]:.5f} |')
    text += [f'\nSelected: **{validation["selected"]}**. Test log-loss improvement over map strength: '
             f'{validation["test_cycle_improvement"]:.5f}; pair-block bootstrap 95% interval '
             f'{validation["test_cycle_improvement_pair_bootstrap_95"]}. This interval is conditional on the available snapshot.\n',
             '## Similarity and clusters\n',
             'Remove fitted general strength. Compare each bot\'s map-affinity plus cyclic-interaction profile '
             'against the same 85 original opponents on the same 11 maps. Cluster the 85 originals using Ward '
             'linkage in the full profile space. Project newer bots to the nearest centroid, explicitly provisionally. '
             'PCA is used only to display those profiles; its first two axes retain '
             f'{explained[:2].sum():.1%} of their variance. Clustering does not use just those two axes.\n',
             f'**{max(sils,key=sils.get)} broad groups have the best silhouette** in the tested 2–8 range. '
             'The five-group cut below is an exploratory finer description, not five proven natural strategy classes. '
             'Scores below average equally over the original opponent pool and maps; they are fitted estimates.\n',
             '| Group | Bots | Representative (medoid) | Mean estimated score | Within-group bootstrap |\n|---|---:|---|---:|---:|']
    for group in groups:
        text.append(f'| {group["cluster"]} | {group["size"]} | {group["medoid"]} | {group["mean_expected_score"]:.1%} | {group["bootstrap"]:.1%} |')
    text += ['\nBootstrap values are mean pair co-memberships within each fitted group across 20 unordered-pair '
             'resamples and model refits. They measure partition sensitivity, not a probability of a true strategy.\n',
             '## Coverage and limits\n',
             f'Original bot pairs share a median {np.median(original_shared):.0f} observed, side-balanced opponent–map cells '
             f'(range {original_shared.min()}–{original_shared.max()}). The empirical correlation matrix uses these common cells only. '
             'It is a separate observational check, not the input to the fitted-model clustering.\n',
             'The run is incomplete; completed fixtures and team-selected new-bot matchups need not represent all future games. '
             'New bots usually have only a few reference opponents: their extrapolated placement is less reliable. '
             'Regularization pulls weakly identified map/cycle effects toward zero, so sparse bots can land near '
             'the mixed central group even if their overall strength is high. This is not evidence they share its tactics. '
             'Use newer_observed_pairs.csv for supported direct comparisons of newer profiles. '
             'Low-signal weak bots may cluster together without sharing a tactic. Outcome similarity alone does not prove behaviour. '
             'Runtime faults remain engine-scored outcomes; none occur in this snapshot. Native results do not validate judge CPU safety.\n',
             '## Files\n',
             '- `bots.csv`: every source version, coverage, cluster, strength, neighbours and embedding.\n'
             '- `clusters.json`: all memberships, bootstrap stability, spectra and map effects.\n'
             '- `observed_correlation.csv` / `observed_shared_counts.csv`: empirical similarity and support.\n'
             '- `style_distances.csv` / `cyclic_matchup_logits.csv`: fitted profiles and cyclic effects.\n'
             '- `snapshot.json`, `validation.json`, `model.json`, `fit.npz`: reproducibility and held-out evaluation.\n',
             '## Mathematical references\n',
             'The ranking-versus-cycle distinction is motivated by '
             '[Hodge ranking](https://arxiv.org/abs/0811.1067); this implementation uses regularized fractional logistic fitting, '
             'not an exact Hodge decomposition. Missing skew-symmetric comparisons can be completed with '
             '[low-rank methods](https://arxiv.org/abs/1102.4821). A recent '
             '[non-transitive pairwise model](https://www.jmlr.org/papers/v27/25-0217.html) develops this approach further; '
             'our small implementation is not a reproduction of that paper.\n']
    for group in groups:
        text += [f'\n## Group {group["cluster"]} members\n', '\n'.join('- '+v for v in group['members'])]
    text += ['\n## Newer source versions (provisional projections)\n',
             '| Bot | Group | Unique games | Opponents | Closest model profile |\n|---|---:|---:|---:|---|']
    text += [f'| {r["bot"]} | {r["cluster"]} | {r["unique_games"]} | {r["opponents"]} | {r["nearest_model_profile"]} |' for r in rows if not r['original']]
    (out/'README.md').write_text('\n'.join(text)+'\n')
    page=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
          '<title>Bot performance similarity</title><style>body{font:16px system-ui;max-width:1250px;margin:32px auto;padding:0 24px;color:#23313f;background:#fafbf9}img{max-width:100%;background:white}p{line-height:1.55}td,th{padding:6px 12px;border-bottom:1px solid #ddd;text-align:left}table{border-collapse:collapse;font-size:13px}a{color:#176a87}.scroll{overflow:auto}</style>',
          '<h1>Bot performance similarity</h1>',
          f'<p>Frozen snapshot: {html.escape(meta["snapshot_at"])} · {meta["snapshot_games"]:,} games · {n} source versions. '
          'Tournament remains incomplete. Two broad families; five groups shown for exploratory detail.</p>',
          '<p>General strength is removed before clustering. Newer bots are provisional projections from limited reference matches. '
          'The two-dimensional picture omits some fitted structure; clustering uses every fitted dimension.</p>',
          '<p><a href="README.md">Methods, validation and memberships</a> · <a href="bots.csv">Bot data</a> · '
          '<a href="observed_correlation.csv">Observed correlations</a> · <a href="observed_shared_counts.csv">Shared evidence counts</a> · '
          '<a href="dendrogram.png">Full hierarchy</a></p>',
          '<img src="style_embedding.png" alt="PCA of fitted performance styles"><img src="map_affinities.png" alt="Cluster map affinities">',
          '<h2>All source versions</h2><input id="search" placeholder="Filter bots" style="padding:8px;font:inherit;width:320px">',
          '<div class="scroll"><table id="bots"><thead><tr><th>Bot</th><th>Group</th><th>Games</th><th>Opponents</th><th>Estimated score</th><th>Closest fitted profile</th><th>Support</th></tr></thead><tbody>']
    for r in sorted(rows,key=lambda r:(r['cluster'],-r['equal_field_expected_score'])):
        page.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in (r['bot'],r['cluster'],r['unique_games'],r['opponents'],
                     f'{r["equal_field_expected_score"]:.1%}',r['nearest_model_profile'],r['support']))+'</tr>')
    page += ['</tbody></table></div><h2>Observed common-opponent correlations</h2><p>This matrix uses only observed, side-balanced common opponents and maps. Click for full resolution.</p>',
             '<a href="observed_correlation.png"><img src="observed_correlation.png" alt="Observed correlation matrix"></a>',
             '<script>document.getElementById("search").oninput=function(){const q=this.value.toLowerCase();document.querySelectorAll("#bots tbody tr").forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))}</script></html>']
    (out/'index.html').write_text('\n'.join(page))
    print('Report:',out/'index.html',flush=True)
