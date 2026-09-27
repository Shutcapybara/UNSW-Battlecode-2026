"""Finalize Charybdis's frozen experiments without promoting it to ACTIVE."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import zipfile
from converge import load, compare
from cycle_report import summarize

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'build/leviathan'
BOT='leviathan-x04-charybdis-replies'
COUNTS={'screen':24,'myopic':24,'G':110,'V':24,'J':6,
        'bounded-screen':24,'bounded-G':110,'bounded-V':24,'bounded-J':6,
        'final-screen':24,'final-G':110,'final-V':24,'final-J':6,'final-neutral':4}

def folder(suffix):return BUILD/('charybdis-'+suffix)
def rows(suffix):return list(load([folder(suffix)])[0].values())
def score(rs):
    c=Counter(r['result'] for r in rs)
    return '–'.join(str(c[k]) for k in 'WLD')
def table(rs):
    groups=defaultdict(list)
    for r in rs:
        for k in ('ALL',r['map_class'],'side '+r['side'],r['map_class']+' '+r['side'],r['opponent']):groups[k].append(r)
    return '| Set | W–L–D |\n|---|---:|\n'+''.join('| %s | %s |\n'%(k,score(v)) for k,v in groups.items())
def cpu(suffix):
    return '| Metric | Per-game range, million points |\n|---|---:|\n'+''.join(
        '| %s | %.1f–%.1f |\n'%(k,min(r[k] for r in rows(suffix))/1e6,max(r[k] for r in rows(suffix))/1e6)
        for k in ('cpu_p50','cpu_p99','cpu_max'))
def trace(suffix):
    rs=json.loads((folder(suffix)/'decision-trace.json').read_text());c=Counter()
    for r in rs:
        for k,v in r.items():
            if isinstance(v,int):c[k]=max(c[k],v) if k=='nodes_max' else c[k]+v
    return c
def mechanics(suffix):
    raw=json.loads((folder(suffix)/'results.json').read_text())
    focus=json.loads((folder(suffix)/'manifest.json').read_text())['focus'];c=Counter()
    for r in raw:
        side='A' if r['team_a']==focus else 'B';t=r['analysis']['teams'][side]
        c.update(t['deaths']);c.update({k:t[k] for k in ('turns','pearls','splits','initiated_trades')})
    return c

def main():
    health={}
    for suffix,n in COUNTS.items():
        rs=rows(suffix);assert len(rs)==n,(suffix,len(rs),n)
        assert all(r['result']!='E' and not r['timeouts'] for r in rs)
        raw=json.loads((folder(suffix)/'results.json').read_text())
        assert all(not r.get('analysis_error') and not any(t['timeouts'] for t in r['analysis']['teams'].values()) for r in raw)
        invalid=mechanics(suffix)['invalid'];assert not invalid
        health[suffix]=dict(games=n,invalid_actions=invalid,errors=0,timeouts=0)
        summarize(folder(suffix),phases=(folder(suffix)/'opening.json').exists())
    equivalence=json.loads((folder('final-neutral')/'equivalence.json').read_text())
    assert equivalence['cases']==equivalence['identical']==4 and not equivalence['differences']
    manifests={s:json.loads((folder(s)/'manifest.json').read_text()) for s in ['final-G','final-J','final-screen','final-V']}
    for s,m in manifests.items():
        for filename,digest in m['hashes'][BOT].items():
            if Path(filename).suffix in ('.cpp','.h','.toml'):
                assert hashlib.sha256((ROOT/'bots'/BOT/filename).read_bytes()).hexdigest()==digest,(s,filename)
    current,ch=load([folder('final-G')])
    primary,ph=load([BUILD/'cycle1-v09-G']);riptide,rh=load([BUILD/'riptide-x02-G'])
    assert current.keys()==primary.keys()==riptide.keys()
    assert all(ch[k]==ph[k]==rh[k] for k in current),'Different opponent/map/mode snapshots'
    novel=[dict(opponent=k[0],map=k[1],side=k[2],riptide=riptide[k]['result']) for k,r in current.items()
           if r['result']=='W' and primary[k]['result']!='W']
    unique=[r for r in novel if r['riptide']!='W']
    lost=sum(primary[k]['result']=='W' and r['result']!='W' for k,r in current.items())
    out=BUILD/'charybdis-final';out.mkdir(exist_ok=True)
    (out/'health.json').write_text(json.dumps(health,indent=2)+'\n')
    (out/'diversity.json').write_text(json.dumps(dict(v09_novel_wins=novel,novel_vs_v09_and_riptide=unique,v09_wins_lost=lost),indent=2)+'\n')
    paired,flips=compare([folder('myopic')],[folder('final-screen')])
    (out/'reply-search-flips.json').write_text(json.dumps(flips,indent=2)+'\n')
    report='# Charybdis: exploration results\n\n'
    report+='New family: **%s**. The experiment changes the decision model to adversarial local-game search; it does not train an actor-critic. The tested default uses a 450-node nominal budget with leaf accounting fixed.\n\n'%BOT
    report+='## Full gauntlet and competitive diversity\n\n'+table(current.values())
    report+='\nOn these identical 110 fixtures, v09 scores 85–25–0 and Riptide x02 scores 42–67–1. Charybdis scores **%s**, adding **%d** wins where v09 loses, of which **%d** also lose for Riptide x02. It fails to retain %d of v09\'s wins. Opponent sources, map hashes and execution modes match.\n\n'%(score(current.values()),len(novel),len(unique),lost)
    for r in novel:report+='- `%s`, side %s, vs `%s`; Riptide result %s.\n'%(r['map'],r['side'],r['opponent'],r['riptide'])
    if not novel:report+='No complementary wins against v09.\n'
    report+='\nThese are fixture-specific niches, not a validated rule for selecting which bot to deploy.\n\n'
    report+='## Causal screen: reply search versus no search\n\n'
    report+='Base is `reply_plies=0`; candidate is the final default. Same evaluator, routing, production policy and root actions. Four control games reproduce the old no-search movement/split/sonar streams after the budget fix.\n\n'+paired+'\n\n'
    report+='The screen contains three compact maps and one open map against Hunter v14, Hunter v20 and v09, both sides. Read the per-class splits; totals are not population-wide estimates.\n\n'
    report+='| Profile | Logged / total decisions | Searched | Changed from immediate choice | Changed / searched | Max visited nodes |\n|---|---:|---:|---:|---:|---:|\n'
    for suffix in ['screen','myopic','final-screen']:
        c=trace(suffix);rate=100*c['changed_decisions']/max(1,c['searched_decisions'])
        report+='| %s | %d / %d | %d | %d | %.1f%% | %d |\n'%(suffix,c['logged_decisions'],c['turns'],c['searched_decisions'],c['changed_decisions'],rate,c['nodes_max'])
    report+='\nOnly recorded indicators contribute to the usage rates. These counts establish that the solver changes decisions, not that the changed actions are correct. Dead newborns may never produce an indicator.\n\n'
    report+='| Profile | Pearls | Splits | Head deaths | Initiated head trades / 1,000 turns | Wall / self / body deaths |\n|---|---:|---:|---:|---:|---|\n'
    for suffix in ['screen','myopic','final-screen']:
        c=mechanics(suffix);report+='| %s | %d | %d | %d | %.2f | %d / %d / %d |\n'%(suffix,c['pearls'],c['splits'],c['head-to-head'],1000*c['initiated_trades']/c['turns'],c['wall'],c['self'],c['body'])
    report+='\nRaw totals depend on game duration and population. The deeper prototype makes more head trades while losing more screen games than the no-search control. This is evidence against this particular model/evaluator pairing, not against adversarial search in general.\n\n'
    report+='### Opening economy\n\n'
    for suffix in ['myopic','final-screen']:
        summary=summarize(folder(suffix),phases=True)
        report+='**%s**\n\n%s\n\n'%(suffix,summary[summary.index('Rounds [0,30)'):])
    report+='## Orientation validation\n\nSix transformed open maps × Hunter v20/v09 × both sides (24); this is not full G+V or a globally unused holdout.\n\n'+table(rows('final-V'))
    report+='\n## Compute and engineering history\n\n'
    report+='The deeper 1800-budget prototype reached 99.8M CPU points. Reducing its nominal budget to 450 still reached 94.9M: leaf evaluations were bypassing the budget decrement. The final implementation charges leaves too. Evaluation weights and strategic rules were not tuned during this repair.\n\n'
    report+='| Implementation snapshot | Screen W–L–D | G W–L–D | Orientation W–L–D | Judge max, M |\n|---|---:|---:|---:|---:|\n'
    for prefix,label in [('', '1800, expansion-only'),('bounded-','450, expansion-only'),('final-','450, leaf-accounted')]:
        report+='| %s | %s | %s | %s | %.1f |\n'%(label,score(rows(prefix+'screen')),score(rows(prefix+'G')),score(rows(prefix+'V')),max(r['cpu_max'] for r in rows(prefix+'J'))/1e6)
    report+='\nFinal judge sample: arena, big_empty, trauma, both sides against Hunter v20.\n\n'+cpu('final-J')
    gate=max(r['cpu_p99'] for r in rows('final-J'))<60e6 and max(r['cpu_max'] for r in rows('final-J'))<80e6
    report+='\nSampled CPU gate: **%s** (p99 <60M; max <80M). Ranges are runner-rounded per-game statistics, not pooled percentiles or a worst-case proof.\n'%('pass' if gate else 'fail')
    report+='\nAll **%d executions** have checked replays, no runner/analysis errors or recorded timeouts, and zero Charybdis invalid-action deaths. These include repeated deterministic fixtures under different implementations/configurations and are not %d independent samples. The archive contains one final source family; earlier implementations remain in frozen run snapshots.\n'%(sum(COUNTS.values()),sum(COUNTS.values()))
    report+='\nThe regression suite passes, including focused local-game tests for turn order, same-round births, collision/carcass rules, sprint funding, bed timing, incomplete observation, a forced-reply tactic and leaf-budget accounting.\n'
    report+='''
## Exploration verdict

Retain Charybdis and its no-search control as distinct experimental baselines
for phase-end selection. This exploration does not change ACTIVE or replace
the stronger Leviathan v09 reference. The value of reply search remains a
measured question; resemblance to a chess engine is not evidence of strength.

The new reusable component is the local multi-actor transition model and its
opponent-reply solver. The evidence motivates different experiments at phase
end: multi-opponent interaction instead of a single duel; opponent-policy
sampling instead of a worst-case reply; and a value function that distinguishes
locally favorable exchanges from team-level winning chances. Each would be a
new hypothesis, not a reason to keep tuning this branch's current weights.

The existing approximation can value a local sacrifice incorrectly because it
omits the rest of the team's future. Away from a fully observed duel the policy
is a greedy economic evaluator, and it has no long-route trap solver. Those are
explicit model limits; the match totals alone do not isolate their individual
contributions. Unknown edges are blocked for both players, so a predicted trap
can be false when an opponent can escape into unseen terrain. No trained-network
or online-learning claim is made.

Design, assumptions and commands: [CHARYBDIS.md](CHARYBDIS.md).
Raw evidence: `build/leviathan/charybdis-*`.
'''
    (ROOT/'docs/leviathan/CHARYBDIS_RESULTS.md').write_text(report)
    readme='# '+BOT+'\n\nLine: Leviathan / Charybdis.\n\n'
    readme+='Base: fresh decision policy; borrowed: input parsing, terrain/portal geometry, own-body history and food-memory helpers from leviathan-x01-riptide-horizon. Its planner, reproduction rule and communications are replaced.\n\n'
    readme+='Hypothesis: explicitly minimizing over opponent replies enables useful blocking, forced trades and sacrifices. The local game models ID order, same-round newborn turns, movement, sprinting, splitting, food and deaths. Three half-turns, width six, and a leaf-accounted nominal budget of 450 bound search.\n\n'
    readme+='Production has per-unit value; a deterministic subset of IDs banks growth after maturity. There is no elected crown, feeding, sonar, trained network or online learning.\n\n'
    readme+='**Verdict: retained for phase-end comparison; mixed evidence for the reply-search hypothesis.**\n\nFull G, five ACTIVE opponents × eleven maps × both sides:\n\n'+table(current.values())
    readme+='\nComplementarity: %d wins where v09 loses; %d also lose for Riptide x02. V09 scores 85–25–0 and remains stronger overall.\n\n'%(len(novel),len(unique))
    readme+='Paired final screen, base=no-search, candidate=reply search:\n\n'+paired+'\n\n'
    readme+='Targeted open-orientation validation (24 games, not full G+V):\n\n'+table(rows('final-V'))
    readme+='\nJudge CPU: arena, big_empty and trauma, both sides against Hunter v20 (six games):\n\n'+cpu('final-J')
    readme+='\nKnown limits: only one fully observed enemy is dynamic; other bodies are frozen, hidden information is unresolved, enemy population is unknown, and width/budget limits omit replies. Local material value is not a learned estimate of winning probability.\n\n'
    readme+='Design: docs/leviathan/CHARYBDIS.md. Full controls, traces, historical compute failures and results: docs/leviathan/CHARYBDIS_RESULTS.md. Parameters live in params.h; lab overrides only private snapshots.\n'
    source=ROOT/'bots'/BOT;(source/'README.md').write_text(readme)
    with zipfile.ZipFile(out/(BOT+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(source.iterdir()):
            if p.suffix in ('.cpp','.h','.toml') or p.name=='README.md':z.write(p,p.name)
    print('Final G',score(current.values()),'novel vs v09',len(novel),'novel vs both',len(unique),'CPU gate',gate)
    print(ROOT/'docs/leviathan/CHARYBDIS_RESULTS.md')

if __name__=='__main__':main()
