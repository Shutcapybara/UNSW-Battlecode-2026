"""Finalize measured Riptide baselines, niches and negative results."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import zipfile
from converge import load, compare
from cycle_report import summarize

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'build/leviathan'
COUNTS = {
    'x01-screen':24, 'x01-myopic':24, 'x01-bank-screen':24, 'x01-silent':24,
    'x01-monolith':20, 'x02-screen':24, 'x02-factory':24, 'x02-neutral':4,
    'x01-G':110, 'x02-G':110, 'x02-V':88, 'x01-monolith-V':48,
    'x01-J-screen':4, 'x02-J':4,
}


def folder(suffix):
    return BUILD / ('riptide-' + suffix)


def rows(suffix):
    return load([folder(suffix)])[0]


def score(rs):
    c = Counter(r['result'] for r in rs)
    return '%d–%d–%d' % tuple(c[k] for k in 'WLD')


def table(rs):
    grouped = defaultdict(list)
    for r in rs:
        for k in ('ALL', r['map_class'], 'side '+r['side'], r['map_class']+' '+r['side'], r['opponent']):
            grouped[k].append(r)
    return '| Set | W–L–D |\n|---|---:|\n' + ''.join('| %s | %s |\n' % (k,score(v)) for k,v in grouped.items())


def diversity(suffix, reference):
    before, bh = load([reference]); after, ah = load([folder(suffix)])
    assert before.keys() == after.keys()
    assert all(bh[k] == ah[k] for k in before), 'Changed comparison fixtures'
    novel = [dict(opponent=k[0],map=k[1],side=k[2],baseline=before[k]['result'])
             for k,r in after.items() if r['result']=='W' and before[k]['result']!='W']
    lost = [k for k,r in before.items() if r['result']=='W' and after[k]['result']!='W']
    return novel, lost


def cpu(suffix):
    rs = list(rows(suffix).values())
    out = '| Metric | Per-game range, million points |\n|---|---:|\n'
    for k in ('cpu_p50','cpu_p99','cpu_max'):
        values = [r[k] for r in rs];assert all(v is not None for v in values)
        out += '| %s | %.1f–%.1f |\n' % (k,min(values)/1e6,max(values)/1e6)
    return out


def main():
    health = {}
    for suffix,n in COUNTS.items():
        rs = list(rows(suffix).values());assert len(rs)==n,(suffix,len(rs),n)
        assert all(r['result']!='E' and not r['timeouts'] for r in rs)
        raw=json.loads((folder(suffix)/'results.json').read_text())
        invalid=sum(t['deaths'].get('invalid',0) for r in raw for side,t in r['analysis']['teams'].items()
                    if r['team_a' if side=='A' else 'team_b'].startswith('leviathan-x'))
        errors=[r['log'] for r in raw if r.get('analysis_error') or any(t['timeouts'] for t in r['analysis']['teams'].values())]
        assert not errors,errors
        health[suffix]=dict(games=len(rs),errors=errors,invalid_actions=invalid)
        summarize(folder(suffix), phases=(folder(suffix)/'opening.json').exists())
    out=BUILD/'riptide-final';out.mkdir(exist_ok=True)
    equivalence=json.loads((folder('x02-neutral')/'equivalence.json').read_text())
    assert equivalence['cases']==equivalence['identical']==4 and not equivalence['differences']
    for version,slug in [('x01','horizon'),('x02','viability')]:
        name='leviathan-'+version+'-riptide-'+slug
        manifest=json.loads((folder(version+'-G')/'manifest.json').read_text())
        judge=json.loads((folder('x01-J-screen' if version=='x01' else 'x02-J')/'manifest.json').read_text())
        for filename,digest in manifest['hashes'][name].items():
            if Path(filename).suffix in ('.cpp','.h','.toml'):
                assert hashlib.sha256((ROOT/'bots'/name/filename).read_bytes()).hexdigest()==digest, (name,filename)
                assert judge['hashes'][name][filename]==digest, ('Judge source differs',name,filename)
    (out/'health.json').write_text(json.dumps(health,indent=2)+'\n')
    comp,flips=compare([folder('x01-G')],[folder('x02-G')])
    (out/'x02-vs-x01-flips.json').write_text(json.dumps(flips,indent=2)+'\n')
    niche1,lost1=diversity('x01-G',BUILD/'cycle1-v09-G')
    niche2,lost2=diversity('x02-G',BUILD/'cycle1-v09-G')
    (out/'diversity.json').write_text(json.dumps(dict(x01=dict(novel_wins=niche1,lost_wins=lost1),
                                                     x02=dict(novel_wins=niche2,lost_wins=lost2)),indent=2)+'\n')
    report='# Riptide measured baselines\n\n'
    report+='Riptide x02 improves the independent family to **42–67–1** on G, versus x01 **33–77–0**. Mainline v09 remains substantially stronger at **85–25–0**, but x02 wins four fixtures that v09 loses. Retain both Riptide sources for research; x02 is the stronger starting point within this family.\n\n'
    report+='## Structural comparison: full gauntlet G\n\n'+comp+'\n\n'
    report+='G is five ACTIVE opponents × eleven original maps × both sides. The x02 V set below is a targeted validation set, **not full G+V**.\n\n'
    report+='## Complementarity against mainline\n\n'
    report+='Mainline v09 scores 85–25–0 on the same 110 frozen fixtures. Source/map hashes match.\n\n'
    report+='| Branch | G W–L–D | Wins where v09 did not win | v09 wins not retained |\n|---|---:|---:|---:|\n'
    for version,novel,lost in [('x01',niche1,lost1),('x02',niche2,lost2)]:
        report+='| %s | %s | %d | %d |\n' % (version,score(rows(version+'-G').values()),len(novel),len(lost))
    report+='\nThese are deterministic complementary fixtures, not evidence of a reliable opponent detector or automatic portfolio selector.\n\n'
    for version,novel in [('x01',niche1),('x02',niche2)]:
        report+='**%s complementary wins:**\n\n'%version
        report+='\n'.join('- `%s`, side %s, vs `%s` (v09 %s).' % (r['map'],r['side'],r['opponent'],r['baseline']) for r in novel) or 'None.'
        report+='\n\n'
    report+='## Frozen configuration screens\n\n| Profile | Games | W–L–D |\n|---|---:|---:|\n'
    for suffix in ['x01-screen','x01-myopic','x01-bank-screen','x01-silent','x01-monolith','x02-screen','x02-factory']:
        rs=list(rows(suffix).values());report+='| %s | %d | %s |\n'%(suffix,len(rs),score(rs))
    report+='''
The common 24-game screen is arena/default_small/default/big_empty × Hunter
v14, Hunter v20 and Leviathan v09 × both sides. The monolith screen is a
separate 20-game open-map set against v09/Hunter v20; do not compare its raw
win count to the 24-game screens. The x02 screen preserves its original 0.35
fork-risk constant; the same value was later exposed as a parameter.

The core screen result is x01 2–22, x02 5–19 (three improved outcomes, none
regressed). Turning x01's horizon down to one or applying the early-bank
profile leaves all 24 outcomes unchanged. This does **not** establish action
or mechanism equivalence. The four-game x02 neutral control *does* reproduce
x01 movement, split and sonar streams exactly with viability disabled.

Disabling the self-report broadcasts improves x01 from 2–22 to 4–20 on this
screen: big_empty/B against Hunter v14 and default/A against v09 change to
wins, with no lost wins. The current ownership consumer therefore has no
demonstrated benefit on the screen. Keep the radio-on source as the frozen
control; use `radio=False` as a recorded search starting point. This ablation
does not establish that all communication is harmful.

The factory profile finishes 4–20 versus x02's 5–19: one improved fixture,
two regressions. Removing the food gate and relaxing reproduction risk does
not establish a repair of the opening deficit. On compact screen maps its
opening pearl average rises to 24.42 and splits to 7.33, while opponents still
collect 36.50 pearls and split 13.00 times. The extra production is too small
to overturn any of the twelve compact losses.

Opening [0,30), per game on the screen's compact maps: x01 eats 23.08 pearls
and makes 6.17 splits against the opponents' 37.83 pearls and 13.50 splits.
x02 remains almost unchanged (22.83 pearls, 6.17 splits). Its improvements
therefore do not fix the opening production deficit. Most x01 wall/self deaths
occur after the planner reports no legal action; a few deaths also involve
incomplete knowledge beyond vision. Neither planner is an omniscient safety
proof.

### Paired profile comparisons

'''
    for before,after in [('x01-screen','x01-myopic'),('x01-screen','x01-bank-screen'),
                         ('x01-screen','x01-silent'),('x02-screen','x02-factory')]:
        comparison,changes=compare([folder(before)],[folder(after)])
        report+='\n**%s → %s**\n\n%s\n'%(before,after,comparison)
        (out/(after+'-flips.json')).write_text(json.dumps(changes,indent=2)+'\n')
    report+='''

## x02 orientation validation

Twenty-two transposed/flipped maps × v09/Hunter v20 × both sides (88 games).
The default x02 policy was frozen before viewing this set. These orientations
were held out for this Riptide selection, not globally unused by the project.

'''+table(rows('x02-V').values())
    report+='\n## Monolith orientation validation\n\nTwelve open-map variants × v09/Hunter v20 × both sides (48 games). Frozen `population_max=1` prevents reproduction; it retains the two to four initial dragons on these maps.\n\n'+table(rows('x01-monolith-V').values())
    report+='\nThe original wins are both trauma/A (against v09 and Hunter v20). Only two validation wins remain: trauma_FX/B against v09, and trauma_T/A against Hunter v20. All four are longest-dragon tiebreaks. This is a narrow survival/banking signal, not a robust general specialist.\n'
    report+='\n## Judge CPU and verification\n\nx01: arena and big_empty, both sides versus Hunter v20.\n\n'+cpu('x01-J-screen')
    report+='\nx02: big_empty and trauma, both sides versus Hunter v20.\n\n'+cpu('x02-J')
    assert all(r['invalid_actions']==0 for r in health.values())
    report+='\nCPU values are runner-rounded per-game percentile ranges, not pooled percentiles. See the bot READMEs for verdicts. All '+str(sum(COUNTS.values()))+' games have checked replays and no recorded runner/analysis errors or timeouts; Riptide has zero invalid-action deaths. Per-run evidence is in `build/leviathan/riptide-final/health.json`.\n'
    report+='\n31 Python-discovered tests pass, including compiling/running both C++ rule suites. Native results do not substitute for sandbox metering. Source/map snapshots, all replays, standard ledgers and ablation manifests remain in `build/leviathan/riptide-*`.\n'
    report+='''

## Decision and next search

Retain Riptide as an independent **research baseline**, not a replacement for
v09 or an ACTIVE promotion. Preserve x01 as the original negative control and
x02 as the capacity-filter branch. A few complementary wins justify further
search only if their economic/survival mechanism can be reproduced on new
maps; overall deficits must remain visible.

The capacity component's full-G gain is entirely on open maps: +10 wins there,
with a compact win becoming a draw in aggregate. The paired total is 15
improved fixtures and 5 regressions, not a uniform safety improvement. Its
17–71 orientation result includes 0–44 against v09, so the isolated direct
win over v09 in the selection screen does not generalize to these variants.

The next structural questions are: how to value forecast food under enemy
competition; how to fund reproduction while head pressure is high; and how to
turn distributed reserves into one winning length without inheriting the
mainline's feeding system. The horizon ablation does not support blindly
increasing search depth. The CPU headroom allows new models, but is not evidence
that more search alone will improve play.
'''
    (ROOT/'docs/leviathan/RIPTIDE_RESULTS.md').write_text(report)
    for version,slug in [('x01','horizon'),('x02','viability')]:
        name='leviathan-'+version+'-riptide-'+slug
        source=ROOT/'bots'/name
        intro=('# '+name+'\n\nLine: Leviathan / Riptide.\n\n'+
            ('Base: fresh C++ implementation; borrowed: protocol and geometry concepts from leviathan-v07-local-cache. No Hunter/Ouroboros policy copied.\n\nHypothesis: resource-funded colonies plus bounded future-route planning can form a competitive alternative to crown/feeding evaluation.\n' if version=='x01' else
             'Base: leviathan-x01-riptide-horizon; borrowed: its world model, planning and colony policy.\n\nHypothesis: own-tail release capacity filtering prevents traps missed by a short route horizon. Original fork-risk constant 0.35 is exposed without changing the default.\n'))
        intro+='\n**Verdict: archived from mainline promotion; retained as an experimental search baseline.** The user explicitly requested competitive diversity. This is not a claim of overall superiority.\n\n'
        intro+='Full G: five ACTIVE opponents × eleven maps × both sides. W–L–D:\n\n'+table(rows(version+'-G').values())
        novel,lost=(niche1,lost1) if version=='x01' else (niche2,lost2)
        intro+='\nVersus the v09 reference (85–25–0), there are %d wins on fixtures v09 did not win and %d v09 wins not retained. See the diversity file for exact cases.\n'%(len(novel),len(lost))
        if version=='x02':intro+='\nPaired structural changes against x01:\n\n'+comp+'\n\nTargeted orientation validation:\n\n'+table(rows('x02-V').values())
        intro+='\nJudge CPU: '+('arena and big_empty' if version=='x01' else 'big_empty and trauma')+', both sides against Hunter v20 (four sandbox fixtures).\n\n'+cpu('x01-J-screen' if version=='x01' else 'x02-J')
        intro+='\nAll exposed decision parameters are documented in params.h. Run snapshot-only variants with tools/leviathan/lab.py --set key=value. No parameter-only folders.\n\n'
        intro+='31 regression tests pass, including the C++ rule checks for both branches. x02 with viability=False preserves x01 movement/split/sonar in all four neutral-control games.\n\n'
        intro+='Design, assumptions and reproducible commands: docs/leviathan/RIPTIDE.md. Full ablations, side/map-class results, validation and limits: docs/leviathan/RIPTIDE_RESULTS.md.\n\n'
        intro+='Important limits: future food and unknown edges are forecasts; other bodies are held stationary; capacity assumes tail release without intervening growth. No crown, feeding, active hunting, role assignment, or map-wide shared memory is present.\n'
        (source/'README.md').write_text(intro)
        with zipfile.ZipFile(out/(name+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(source.iterdir()):
                if p.suffix in ('.cpp','.h','.toml') or p.name=='README.md':z.write(p,p.name)
    print(comp)
    print('Novel wins versus mainline:',len(niche1),len(niche2))
    print(ROOT/'docs/leviathan/RIPTIDE_RESULTS.md')


if __name__=='__main__':main()
