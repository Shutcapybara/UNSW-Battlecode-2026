"""Make an offline comparison-pool decision; --apply-default changes future TOMLs only."""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tomllib
import numpy as np
from game_stats import ROOT


def choose(r,blocked,limit=24):
    bs=r['bots'];profile=np.array([b['map_profile'] for b in bs])
    eligible=[b['id'] for b in bs if b['broad'] and b['name'] not in blocked]
    correlations={(s['a'],s['b']):s for s in r['family_correlations']}
    exact={ (s['a'],s['b']):s for s in r['similarities'] if 'correlation_low' in s }
    def near(i,j):
        key=tuple(sorted((i,j)));s=exact.get(key)
        if s and s['correlation']>=.85 and s['correlation_low']>=.65:
            return s|dict(low=s['correlation_low'],high=s['correlation_high'],basis='exact shared opponent/map cells')
        s=correlations.get(key)
        return s|dict(basis='opponent-lineage/map averages') if s else None
    selected=[];why={}
    def add(i,reason):
        if i not in selected:selected.append(i);why[i]=reason
        elif reason not in why[i]:why[i]+='; '+reason
    for i in sorted(eligible,key=lambda i:-bs[i]['score'])[:5]:add(i,'broad overall leader')
    for k,name in enumerate(r['maps']):add(max(eligible,key=lambda i:profile[i,k]),'map leader: '+name)
    best_map=profile[eligible].max(axis=0)
    candidates=[i for i in eligible if bs[i]['score']>=.50 or np.any(profile[i]>=best_map-.06)]
    while len(selected)<limit:
        available=[i for i in candidates if i not in selected]
        if not available:break
        def utility(i):
            ss=[near(i,j) for j in selected]
            if any(s and s['correlation']>=.85 and s['low']>=.65 for s in ss):return -100
            mx=max([s['correlation'] for s in ss if s],default=.8)
            return bs[i]['score']+.12*(1-max(0,mx))
        i=max(available,key=utility)
        if utility(i)<0:break
        add(i,'strong and distinct strength-adjusted profile')
    decisions=[]
    for b in bs:
        i=b['id'];replacement=None;evidence=None
        if i in selected:status='primary';reason=why[i]
        elif b['name'] in blocked:
            status='runtime_hold';reason='Inherited campaign timeout hold; does not establish which participant caused the failure.'
        elif not b['broad']:
            status='needs_evidence';reason='Insufficient broad coverage; no weakness or dominance judgement.'
        elif b['high']<.40 and max(b['map_profile'])<.60:
            status='deprecated_weak';reason='Well-tested: upper strength sensitivity bound below 40%, with no map profile above 60% against the balanced anchor panel.'
        else:
            dominators=[d for d in r['dominance'] if d['worse']==i and d['families']>=6 and d['maps']>=10
                        and bs[d['better']]['name'] not in blocked]
            if dominators:
                evidence=max(dominators,key=lambda d:(d['better'] in selected,bs[d['better']]['score']))
                replacement=bs[evidence['better']]['name'];status='deprecated_dominated'
                reason='Observed loose dominance on shared fixtures: >2pp lower-bound mean gain, no tested map more than 10pp worse; >=6 families and >=10 maps.'
            else:
                redundant=[(j,near(i,j)) for j in selected if near(i,j) and near(i,j)['correlation']>=.85
                           and near(i,j)['low']>=.65 and bs[j]['score']>=b['score']-.02
                           and max(profile[i]-profile[j])<=.10]
                if redundant:
                    j,evidence=max(redundant,key=lambda js:js[1]['correlation']);replacement=bs[j]['name']
                    status='deprecated_redundant';reason='Strong residual-profile correlation with a primary bot of comparable or better strength, without a >10pp modeled map niche.'
                else:
                    status='reserve';reason='Broad evidence but not selected for the 24-bot routine budget; retain for targeted or extended tests.'
        decisions.append(dict(name=b['name'],canonical=b['name'],status=status,reason=reason,replacement=replacement,evidence=evidence))
        for alias in r['aliases'][i][1:]:
            decisions.append(dict(name=alias,canonical=b['name'],status='duplicate_alias',replacement=b['name'],
                reason='Identical effective packaged source; retain history but use one competitor in routine comparisons.',evidence=None))
    return selected,why,decisions


def main(out,apply=False):
    r=json.loads((out/'analysis.json').read_text());manifest=json.loads((out/'manifest.json').read_text())
    pointer=json.loads((out/'campaign-pointer.json').read_text());campaign=Path(pointer['directory'])
    blockfile=out/'blocked-bots.json'
    if not blockfile.exists():shutil.copy2(campaign/'blocked-bots.json',blockfile)
    blocked=set(json.loads(blockfile.read_text()));bs=r['bots']
    selected,why,decisions=choose(r,blocked);names=[bs[i]['name'] for i in selected]
    result=dict(snapshot=r['at'],campaign=str(campaign),primary=names,counts=dict(Counter(d['status'] for d in decisions)),decisions=decisions)
    (out/'decisions.json').write_text(json.dumps(result,indent=2)+'\n')
    oldconfig=out/'benchmark-all.toml'
    if not oldconfig.exists():shutil.copy2(ROOT/'benchmark.toml',oldconfig)
    def config(base):
        def relative(p):
            import os
            return os.path.relpath(p,base)
        values=dict(pairing='adaptive',references=names,
            maps=[relative(campaign/'sources/maps')],bots=[relative(campaign/'sources/bots'/n) for n in names])
        text='# Curated, measured frozen sources; historical pool and rationale: docs/benchmark-pool-20260927.md\n'
        text+='\n'.join(f'{k} = {json.dumps(v,indent=2)}' for k,v in values.items())
        text+='\n\n[run]\n'+'\n'.join(f'{k} = {json.dumps(v)}' for k,v in manifest['settings'].items())+'\n'
        return text
    (out/'benchmark-curated.toml').write_text(config(out))
    if apply:
        archive=ROOT/'benchmark-all-20260927.toml'
        if not archive.exists():shutil.copy2(oldconfig,archive)
        (ROOT/'benchmark.toml').write_text(config(ROOT))
        comparison=ROOT/'comparison.toml'
        archive=ROOT/'comparison-before-curation-20260927.toml'
        if not archive.exists():shutil.copy2(comparison,archive)
        settings=tomllib.loads(archive.read_text())['run']
        frozen=tomllib.loads(config(ROOT))
        text='# Curated routine opponents; see docs/benchmark-pool-20260927.md.\n'
        text+='\n'.join(f'{k} = {json.dumps(frozen[k],indent=2)}' for k in ['bots','maps'])
        text+='\n\n[run]\n'+'\n'.join(f'{k} = {json.dumps(v)}' for k,v in settings.items())+'\n'
        comparison.write_text(text)
        portable=result|dict(source_hashes=manifest['effective_hashes'],map_hashes=manifest['map_hashes'])
        (ROOT/'docs/benchmark-pool-status.json').write_text(json.dumps(portable,indent=2)+'\n')
    counts=result['counts']
    lines=['# Comparison-pool decision — 27 September 2026','',
        f"Use **{len(names)} primary opponents** for routine comparisons, down from {sum(counts.values())} names. "
        'The running collector, its frozen manifest, the rating worker and the shared ledger were not changed. '
        'The central `benchmark.toml` and `comparison.toml` now apply this decision to future runs; previous defaults are archived in '
        '`benchmark-all-20260927.toml` and `comparison-before-curation-20260927.toml`. All 24 are the new reference panel. '
        '`docs/benchmark-pool-status.json` records every roster decision and source identity for sharing.', '',
        f"Snapshot: {r['ledger_games']:,} ledger games; {r['raw_fixtures']:,} matching named fixtures; "
        f"{r['fixtures']:,} distinct directional fixtures after exact-source alias pooling; {len(bs)} source versions. "
        f"{sum(b['broad'] for b in bs)} meet broad-evidence requirements.", '',
        '## Decision','', '| Status | Names |','|---|---:|']
    lines += [f'| {status} | {number} |' for status,number in counts.items()]
    lines+=['','Deprecated means removed from routine comparisons, not deleted or excluded from historical analysis. '
        'Reserve bots remain available for targeted regression tests; needs-evidence bots remain eligible for screening. '
        'Neither category is labelled weak. Runtime holds inherit prior timeouts involving the named bot; they are not proof of a defective bot.','',
        '## Primary pool','',
        '| Bot | Distinct fixtures | Opponents / lineages | Maps with ≥3 paired opponents | Selection reason |',
        '|---|---:|---:|---:|---|']
    for i in selected:
        b=bs[i];lines.append(f"| {b['name']} | {b['fixtures']} | {b['opponents']} / {b['families']} | {b['dense_maps']} | {why[i]} |")
    lines+=['','## Method and limits','',
        '- Broad evidence requires ≥200 distinct directional fixtures, ≥15 distinct source opponents, ≥6 opponent lineages, ≥10 maps, and ≥10 maps with at least three fully side-paired opponents. This is an executive coverage rule, not a formal confidence guarantee.',
        '- Pool exact effective packaged-source identities, even across different names. Repeated directional fixtures contribute their mean once; games, bot revisions and runtime identities remain intact in the ledger.',
        '- Fit a regularized paired-comparison model with bot strength, bot-by-map effects and starting-side effects. Each unordered lineage-pair/map block receives equal total fitting weight. Lineages are a coarse proxy: shared ancestry across names can remain correlated.',
        '- General-strength estimates include average map affinity. For residual profiles, fit five folds holding out whole opponent pairs (all maps and both sides); subtract expected outcomes from general strength and initiative, retaining map preferences and matchup differences.',
        '- Exact common-opponent/map residual correlations take precedence when ≥80 shared paired cells span ≥6 lineages and ≥10 maps, with correlation ≥0.85 and lower cluster-sensitivity bound ≥0.65. Also average residuals within opponent-lineage/map cells; correlate these with equal lineage weight and capped cell-support weights. Require ≥50 shared cells, ≥6 lineages and ≥10 maps. The latter pools different opponents within a lineage: it is approximate strategic similarity, not a causal or code-level classification.',
        '- Strength sensitivity uses 40 lineage-cluster reweightings; similarity uses 200 lineage-cluster reweightings. These ranges reflect sensitivity to opponent mix, not calibrated confidence intervals. Anchor choice, regularization, lineage boundaries and adaptive sampling remain limitations.',
        '- Anchor panel: strongest broadly measured source per lineage, weighted equally across lineages and maps. These scores are not comparable to the live six-reference percentages. Sparse bots can have extreme fitted scores and are excluded from primary selection regardless.',
        '- Seed the primary pool with the five broad overall leaders and each map leader. Fill to 24 using strength plus residual diversity, avoiding correlations ≥0.85 with lower sensitivity bound ≥0.65. This is a loose empirical frontier: it deliberately retains alternatives and map specialists rather than claiming exact mathematical Pareto optimality.',
        '- Weak retirement requires broad evidence, upper strength sensitivity bound <40%, and no modeled map score >60%. Observed dominance requires shared fixtures spanning ≥6 lineages and ≥10 maps: mean advantage lower sensitivity bound >2pp, with no shared map more than 10pp worse. It is conditional on observed coverage, not proof against every possible opponent.',
        '- Redundancy retirement requires correlation ≥0.85, lower sensitivity bound ≥0.65, a primary representative within 2pp of strength or better, and no modeled map advantage >10pp. Conservative reserves retain cases that do not satisfy these conditions.', '',
        '## Visuals','',
        f"[Map profiles]({out/'map-profiles.png'}) · [Strength-adjusted correlation matrix]({out/'residual-correlations.png'})", '',
        'The matrix shows the coarser lineage/map correlations; exact shared-opponent comparisons also inform deprecation when sufficiently supported.', '',
        '## Reproduction and artifacts','',
        'All analysis artifacts are in `experiment_data/curation-20260927/`: frozen `games.parquet`, `manifest.json`, aliases, '
        '`analysis.json` (pair evidence), `profiles.npz`, `family-profiles.npz`, `decisions.json` (every name and reason), '
        '`decisions.md`, and `benchmark-curated.toml`. The working bots may have changed; the TOML points to the measured frozen sources. '
        'Those local snapshots must be copied with the TOML when sharing, or source fingerprints verified against a teammate’s checkout.', '',
        '```sh', '.venv/bin/python tools/curate_benchmarks.py --output experiment_data/curation-20260927',
        '.venv/bin/python tools/curate_benchmark_profiles.py --output experiment_data/curation-20260927',
        '.venv/bin/python tools/select_benchmark_pool.py --output experiment_data/curation-20260927',
        '.venv/bin/python experiment_data/curation-20260927/plot.py',
        '```','', 'Only add `--apply-default` to the last command when intentionally updating the future default roster. '
        'No command here restarts or changes the live campaign. The next actual campaign still requires the normal explicit plan/run step.','',
        '## Collector health discovered during verification','',
        'The original 286-bot collector had already failed at 2026-09-26 22:47 UTC with a readonly SQLite error. '
        'The saved database passed its integrity and write-lock checks. The same campaign and command were resumed, '
        'and subsequent games completed successfully. Its roster, scheduling code and campaign pointer were unchanged; '
        'the 24-opponent defaults have not been applied to that live campaign.','']
    text='\n'.join(lines);(out/'report.md').write_text(text)
    if apply:(ROOT/'docs/benchmark-pool-20260927.md').write_text(text)
    detail=['# Per-bot comparison status','','| Bot | Status | Representative / dominator | Reason |','|---|---|---|---|']
    detail += [f"| {d['name']} | {d['status']} | {d['replacement'] or '—'} | {d['reason']} |" for d in sorted(decisions,key=lambda d:(d['status'],d['name']))]
    (out/'decisions.md').write_text('\n'.join(detail)+'\n')
    print(json.dumps(dict(primary=names,counts=counts),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--apply-default',action='store_true');a=p.parse_args()
    main(a.output.resolve(),a.apply_default)
