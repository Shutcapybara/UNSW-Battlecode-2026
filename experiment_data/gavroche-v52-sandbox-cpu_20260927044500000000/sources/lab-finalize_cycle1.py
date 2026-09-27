"""Publish the completed cycle-1 evidence into Leviathan-owned documentation.

Requires all 660 native and eight sandbox fixtures. Never changes ACTIVE.
"""
import json
from pathlib import Path
import zipfile

from converge import compare, load
from cycle_report import summarize

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'build/leviathan'
BASE = 'leviathan-v08-core'
CANDIDATE = 'leviathan-v09-arrival'


def dirs(version):
    return [BUILD / ('cycle1-' + version + '-' + s) for s in ('G', 'V')]


def cpu(version):
    folder = BUILD / ('cycle1-' + version + '-J')
    rows, _ = load([folder])
    assert len(rows) == 4 and all(r['result'] != 'E' and r['timeouts'] == 0 for r in rows.values())
    values = {k: [r[k] for r in rows.values()] for k in ('cpu_p50', 'cpu_p99', 'cpu_max')}
    assert all(v is not None for vs in values.values() for v in vs)
    table = '| Metric | Per-game range (million points) |\n|---|---:|\n'
    for k, vs in values.items():
        table += '| %s | %.1f–%.1f |\n' % (k, min(vs) / 1e6, max(vs) / 1e6)
    return table, max(values['cpu_p99']) < 60e6 and max(values['cpu_max']) < 80e6


def main():
    before, _ = load(dirs('v08'))
    after, _ = load(dirs('v09'))
    assert len(before) == len(after) == 330, 'Wait for the complete native matrices'
    table, flips = compare(dirs('v08'), dirs('v09'))
    gtable, _ = compare(dirs('v08')[:1], dirs('v09')[:1])
    vtable, _ = compare(dirs('v08')[1:], dirs('v09')[1:])
    bcpu, bok = cpu('v08')
    ccpu, cok = cpu('v09')
    points = {'W': 1, 'D': .5, 'L': 0}
    deltas = {}
    sets = ['compact', 'open'] + sorted({r['opponent'] for r in before.values()})
    for name in sets:
        keys = [k for k, r in before.items() if r['map_class'] == name or r['opponent'] == name]
        deltas[name] = sum(2 * (points[after[k]['result']] - points[before[k]['result']]) for k in keys)
    passed = deltas['compact'] >= 4 and min(deltas.values()) >= -3 and cok
    verdict = ('Promoted as the Leviathan working candidate for the next convergence; '
               'ACTIVE promotion remains with the unifier.' if passed else
               'Archived as a whole-bot promotion under the declared gate. '
               'Retain the arrival feature and its ablation evidence for component convergence.')
    decision = ('Gate: compact net W–L gain ≥4, no compact/open/opponent set below −3, '
                'sandbox p99 <60M and max <80M. Observed net deltas: `' + repr(deltas) + '`. '
                'CPU gate: ' + ('pass' if cok else 'fail') + '.\n\n**Verdict: ' + verdict + '**\n')
    out = BUILD / 'cycle1-final'
    out.mkdir(exist_ok=True)
    health = {}
    for version in ('v08', 'v09'):
        for suffix, expected in (('G', 110), ('V', 220), ('J', 4)):
            folder = BUILD / ('cycle1-' + version + '-' + suffix)
            rows = json.loads((folder / 'results.json').read_text())
            assert len(rows) == expected
            problems = [r['log'] for r in rows if r['outcome'] == 'error' or
                        r.get('analysis_error') or any(t['timeouts'] for t in
                        r.get('analysis', {}).get('teams', {}).values())]
            assert not problems, problems
            health[folder.name] = dict(completed=len(rows), problems=problems)
    (out / 'health-summary.json').write_text(json.dumps(health, indent=2) + '\n')
    (out / 'comparison.md').write_text(table + '\n\n' + decision)
    (out / 'flips.json').write_text(json.dumps(flips, indent=2) + '\n')
    for version in ('v08', 'v09'):
        for folder in dirs(version) + [BUILD / ('cycle1-' + version + '-J')]:
            summarize(folder)
    common = '''
Sets: G = five gauntlet opponents × 11 maps × both sides (110); V = the same
opponents on 22 transpose/flip variants (220). G+V = 330. Variants were held
out until the candidate profile was frozen; no tuning used their outcomes.
These are deterministic fixtures, not independent random samples. Source/map
hashes and native/sandbox modes are checked by tools/leviathan/converge.py.
Raw evidence lives in build/leviathan/cycle1-*; tables here are durable.
'''
    baseline = '''# leviathan-v08-core

Line: Leviathan (GPT). Base: ouroboros-v10-beacon; borrowed: complete evaluator,
terrain, safety, targeting, production, roles, crown/feeding and sonar from
ouroboros-v10-beacon. Standalone Python, no runtime dependency on another bot.

Hypothesis: adopting the measured survival/crown reference provides a stronger
convergence base than maintaining v07's missing components. The only refactor
extracts the unchanged P/RP table to config.py; policy functions remain identical.

**Verdict: null result in behavior, retained as the equivalence baseline.**
All 18 reference matchups have identical movement, split and sonar streams
(arena, default_small, default; Hunter v14/v20 and Kraken v04; both sides).
AST and parameter tests independently verify the extraction. This does not
claim native/sandbox stream equivalence or promote a duplicate into ACTIVE.
'''
    baseline += common + '\n## Paired G+V results (base column is v08)\n\n' + table
    baseline += '\n\n## Judge CPU\n\nFour sandbox games: big_empty and trauma, both sides vs Hunter v20.\n\n' + bcpu
    baseline += '\nZero sampled timeouts. Feeding intentionally records no-action deaths.\n'
    baseline += '\nComponent boundaries and inherited limitations: docs/leviathan/CONVERGENCE.md.\n'
    (ROOT / 'bots' / BASE / 'README.md').write_text(baseline)
    candidate = '''# leviathan-v09-arrival

Line: Leviathan (GPT). Base: leviathan-v08-core; borrowed: full evaluator and
crown pipeline from ouroboros-v10-beacon; arrival predicate inspired by
hunter-v15. The pearl component is new standalone Python, not a ladder port.

Hypothesis: valuing beds due before arrival improves compact opening production.
The new feature approximates V's material/control term, through the existing
route-distance and ownership target selector. It does not bypass safety filters.

Changes: `pearl_model.arrival_value` values a bed when due ≤ now + ETA − 1,
decays overdue predictions, and runs only on compact maps in the tested profile.
A separately ablated correction requires current observation for simulated
pearl growth. Neither predictions nor remembered pearls fund simulated growth
in the selected profile. Core config defaults are neutral; params.py explicitly
enables `pearl.prepos=1` and `pearl.confirmed_only=1`. The source files match
the frozen benchmark snapshots exactly.

## Verdict

'''
    candidate += decision + common
    candidate += '\n## G+V paired results\n\n' + table
    candidate += '\n\n## Original 11 maps (G)\n\n' + gtable
    candidate += '\n\n## Frozen transpose/flip validation (V)\n\n' + vtable
    candidate += '''

## Ablation and loss autopsy

Thirty compact fixtures versus Hunter v14, Hunter v20 and Kraken v04:

| Arrival | Confirmed simulation | W–L–D |
|---|---|---:|
| off | off | 15–14–1 |
| on | off | 22–8–0 |
| off | on | 15–14–1 |
| on | on | 22–8–0 |

Arrival alone gives eight improved outcomes and one regression. Confirmed-only
changes three action streams but no outcomes in this screen. Opening [0,30)
pearls rise 16.23→23.07, splits 6.27→8.63, units 6.27→8.40. Deaths rise
1.80→2.03, so the supported mechanism is collection and production.

The two open-map G regressions belong to confirmed simulation (arrival is off
on open maps): default/A vs Hunter v14, longest 22→7; queen_of_spades/B vs
Kraken v04, longest 29→13. Both lose the round-500 comparison; first action
divergences are rounds 90 and 64. Do not conflate targeting gains with a
uniform strength gain from the correctness change.

## Verification and CPU

29 regression tests pass. With both options off, all six neutral comparison
games preserve movement, splits and sonar exactly (Hunter v20 on arena,
default_small and default, both sides). Four sandbox games on big_empty and
trauma versus Hunter v20 finish 4–0, with zero timeouts or unexpected invalid
actions. All 76 no-action deaths are after round 400 with only PROTOCOL output,
consistent with the inherited feed action. They are not reported as zero
invalid deaths. CPU values are runner-rounded per-game percentile ranges:

'''
    candidate += ccpu
    candidate += '''
## Parameters and convergence limits

`pearl.prepos`: boolean, neutral 0; consumed by choose_target.
`pearl.compact_only`: boolean, default 1; area ≤625 gate.
`pearl.prediction_ttl`: 0–30 rounds, default 4; overdue reward decay.
`pearl.confirmed_only`: boolean, neutral 0; consumed by simulate.
Other P/RP knobs retain their reference names and consumers.

This is a measured pearl-component candidate, not a claim of full HANDOFF
architecture completion. Inherited 12-bit lifetime IDs, 8-bit portal IDs and
portal gossip correction still need repair. The complete map×phase doctrine,
scout quota, parity pricing and hunter-style priority parameter point remain
open. See docs/leviathan/CONVERGENCE.md for interfaces and explicit scope.

No other line or shared file was changed and no online submission was made.
'''
    (ROOT / 'bots' / CANDIDATE / 'README.md').write_text(candidate)
    results_path = ROOT / 'docs/leviathan/RESULTS.md'
    old = results_path.read_text()
    if not old.startswith('# Cycle 1 convergence results'):
        results_path.write_text('# Cycle 1 convergence results\n\n' + decision + common +
            '\n' + table + '\n\nCandidate CPU:\n\n' + ccpu +
            '\n29 regression tests pass; 18 reference and six neutral full-stream equivalence cases pass. '
            'Both cores pass four sandbox games each, with no sampled timeouts.\n\n'
            'See bots/leviathan-v09-arrival/README.md for ablations, flips, CPU, and inherited gaps; '
            'docs/leviathan/CONVERGENCE.md is the component handoff.\n\n'
            '---\n\nThe following is the preserved v07 historical report.\n\n' + old)
    for name in (BASE, CANDIDATE):
        with zipfile.ZipFile(out / (name + '.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
            for path in sorted((ROOT / 'bots' / name).iterdir()):
                if path.suffix in ('.py', '.toml') or path.name == 'README.md':
                    z.write(path, path.name)
    print(table + '\n\n' + decision)


if __name__ == '__main__':
    main()
