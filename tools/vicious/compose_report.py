"""Compose final campaign documentation from completed, reviewed evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = Path(json.loads((ROOT / 'tools/vicious/current.json').read_text())['directory'])


def read(name):
    return json.loads((C / name).read_text())


def pct(v):
    return f'{100*v:.3f}%'


def wl(a):
    return f"{a['wins']}–{a['draws']}–{a['losses']}"


def runtime(rows):
    selected = [r['usage'][r['side']] for r in rows]
    return {'games': len(rows), 'turns': sum(s['turns'] for s in selected),
            'p99': max(s['p99'] for s in selected),
            'max': max(s['maximum'][0] for s in selected),
            'pass': all(s['conservative_pass'] for s in selected)}


primary = read('cycle_04/BROAD_RESULTS.json')
late = read('cycle_05/LATE_BROAD_RESULTS.json')
parent = 'vicious-v01-frozen'; crown = primary['candidate']; feed = late['candidate']
ca = read('cycle_04/BROAD_ACTION_RESULTS.json')[crown]
fa = read('cycle_05/LATE_ACTION_RESULTS.json')[feed]
carrier_sens = read('cycle_05/CARRIER_SENSITIVITY.json')
feed_sens = read('cycle_05/FEED_SENSITIVITY.json')
holdout = read('cycle_05/OPPONENT_HOLDOUT.json')
cpu1 = runtime(read('release/CPU.json')); cpu2 = runtime(read('release/LATE_CPU.json'))
assert cpu1['pass'] and cpu2['pass'], 'Revise the release verdict before reporting a failed CPU gate.'
verdict = read('release/SECONDARY_VERDICT.json')
integrity = read('release/INTEGRITY_AUDIT.json')
smoke = read('release/ARCHIVE_SMOKE.json')
assert not integrity['panels_with_issues'], integrity['panels_with_issues']
assert len(smoke) == 2 and all(s['equal_actions'] and s['equal_trajectory'] for s in smoke)
parities = sum((read('release/' + f) for f in (
    'NATIVE_PARITY.json', 'VALJEAN_PARITY.json',
    'LATE_NATIVE_PARITY.json', 'LATE_VALJEAN_PARITY.json')), [])
assert all(p['equal_actions'] and p['equal_trajectory'] for p in parities)
qa = read('release/FIGURE_QA.json')
assert len(qa) == 5 and all(q['visually_inspected'] for q in qa)
assert primary['pairs'] == late['pairs'] == 132

table = '\n'.join('| ' + ' | '.join([
    label, wl(a), pct(a['original']), pct(a['synthetic']), pct(a['weighted'])]) + ' |'
    for label, a in [('Frozen parent', primary['arms'][parent]),
                     ('Vicious v02 crown state', primary['arms'][crown]),
                     ('Vicious v03 timed feeding', late['arms'][feed])])
opponents = '\n'.join('| ' + o + ' | ' + ' | '.join(
    pct(a['by_opponent'][o]) for a in [primary['arms'][parent], primary['arms'][crown], late['arms'][feed]]) + ' |'
    for o in primary['comparison_opponents'])
mixtures = '\n'.join('| ' + alpha + ' | ' + ' | '.join(pct(v) for v in [
    primary['mixture_sensitivity'][key][parent], primary['mixture_sensitivity'][key][crown],
    late['mixture_sensitivity'][key][feed]]) + ' |' for alpha, key in [('25%', '0.25'), ('50%', '0.5'), ('75%', '0.75')])
sensrows = '\n'.join(f"| {key} | {r['wins']}–{r['draws']}–{r['losses']} | {r['games']} |"
                     for group in [carrier_sens, feed_sens] for key, r in group.items())
holdrows = '\n'.join(f"| {key} | {r['wins']}–{r['draws']}–{r['losses']} | {len(r['changed_fixtures'])} |"
                     for key, r in holdout.items())


def effects(summary):
    return ', '.join(f"{name}: {row['delta']*4:+g}/4" for name, row in summary['per_map'].items() if row['delta']) or 'No map-level net changes.'


def interval(summary):
    lo, hi = summary['descriptive_family_bootstrap']['delta_90pct']
    return f'{lo*100:+.2f} to {hi*100:+.2f} percentage points'


headline = verdict['recommendation']
body = f'''# Vicious temporal-policy campaign — final synthesis

{headline}

Five adaptive cycles produced 27 experimental source versions plus the frozen parent. The useful results are better crown-state handling, a separately tested feeding doctrine, a working but non-transferring newborn exit protocol, and a verified partial-body representation correction. This is not evidence that every known weakness is fixed. The finalists retain the inherited opening, and no new bot was submitted or added to the shared evaluation roster.

## Playable artifacts and verdicts

- [Vicious v02 crown ZIP](release/vicious-v02-crown.zip): exact x12 source. **Conditional option; general gate failed** because original-map performance regressed. Source folder: `bots/vicious-v02-crown` at the repository root.
- [Vicious v03 feeding ZIP](release/vicious-v03-feeding.zip): exact x15 source. **{verdict['strategic_status']}**. Source folder: `bots/vicious-v03-feeding`.
- `vicious-v01-frozen` preserves the original Gavroche-v54 parent. Off-switch controls and research alternatives remain under their original experiment names; the shared cohort is not flooded with release aliases for every attempted arm.

Both release archives have flat source layouts, verified SHA256 manifests and native replay parity after extraction. Their validated Python/TOML bytes match the frozen experiment sources. Runtime gates pass on the measured fixtures; they do not certify every possible game.

## Complete paired comparison

Each row covers all 33 frozen maps × two frozen strong opponents × both sides: **132 whole-game fixtures per policy**, zero missing target map mass. The original 13 maps share 50% of the target; synthetic maps share 50% under the supplied family-balanced weights. This is an observed score against those two controls, not a modeled score over the full 24-reference field or a live ladder estimate.

| Policy | W–D–L | Original | Synthetic | Weighted combined |
|---|---:|---:|---:|---:|
{table}

The registered general gate requires improvement overall and on both original and synthetic subsets, with gains beyond the selecting orchard. x12 keeps its failed verdict. For x15: **{verdict['gate_explanation'].rstrip('.')}**. Neither finalist was retuned on confirmation outcomes; later sensitivity tests cannot retroactively replace it.

| Comparison opponent | Parent | Crown | Feeding |
|---|---:|---:|---:|
{opponents}

The opponent interaction is material. Crown handling has {len(ca['changed_fixtures'])}/132 changed action streams and {len(primary['paired_flips'])} winner changes; timed feeding has {len(fa['changed_fixtures'])}/132 and {len(late['paired_flips'])}, respectively. A phase branch or parameter change is not counted as useful activation without downstream decisions.

Map-level net win changes (four fixtures per map):

- Crown: {effects(primary)}.
- Feeding: {effects(late)}.

![Crown paired map effects](figures/map_effects.png)
![Feeding paired map effects](figures/feed_map_effects.png)

Bars show within-map win-rate differences, not weighted contributions. Full per-map cells and exact flipped fixtures are in [crown results](cycle_04/BROAD_RESULTS.json) and [feeding results](cycle_05/LATE_BROAD_RESULTS.json).

## Transfer, selection and uncertainty

On the 23 maps new to Vicious at finalist freeze (65.801% target mass), the parent scores {pct(primary['fresh_at_freeze']['weighted'][parent])}; crown scores {pct(primary['fresh_at_freeze']['weighted'][crown])}; feeding scores {pct(late['fresh_at_freeze']['weighted'][feed])}. On the four designated reserve maps, the respective scores are {pct(primary['reserved_maps']['weighted'][parent])}, {pct(primary['reserved_maps']['weighted'][crown])}, and {pct(late['reserved_maps']['weighted'][feed])}. Those maps are now exposed. Other historical lineages may already have used them.

| Original-map mixture weight | Parent | Crown | Feeding |
|---|---:|---:|---:|
{mixtures}

Grouped descriptive resampling keeps both sides and opponents together, groups synthetic siblings, and retains original/synthetic strata. Its 90% difference range is **{interval(primary)}** for crown and **{interval(late)}** for feeding. These describe sensitivity of a finite selected panel; they are not selection-corrected significance tests. Fixed engine-clock tags and repeated/native runs are not new independent random samples.

The separate Valjean holdout uses the four reserve maps, both sides, eight games per policy:

| Policy | W–D–L | Changed action streams versus parent |
|---|---:|---:|
{holdrows}

The parent's 8–0 record creates a ceiling: matching it establishes no incremental winning benefit. These games are not pooled into the declared two-opponent score.

Feeding loses Wide Orchard side A against Valjean, where both the parent and crown policy win. That fresh-opponent regression reinforces its failed transfer verdict.

## What was learned over five cycles

1. **Distinct initial mechanisms:** exit intent plus split admission, an opening renewable-bed bonus, and staged conversion. None passed the initial +2/16 advancement rule. The opening implementation's out-of-phase search-bound effect was found and rejected.
2. **State and component revision:** egress without the strict admission guard improved one fixture; corrected opening valuation stayed neutral; crown-state handling reached 9–7 versus 7–9. This selected a hypothesis for widening, not a general winner.
3. **Representation and conversion doctrines:** a partial body can be length 14 while only four cells are tracked. The correction passes 168 full-body-oracle paths but has no demonstrated winner gain. Hard, soft, state-only and static late doctrines produced opposing effects; early elimination limited activation.
4. **Component and activation confirmation:** minimum carrier admission plus observed crown-length refresh outperformed either isolated piece on the selecting screen. Crown plus egress erased the gain. A five-map late panel then qualified unchanged x15 with gains on Stronghold and Big Empty. Both sources were frozen before the broad comparisons above.
5. **Transfer and timing sensitivity:** all-map comparisons, a fresh opponent, native equivalence, judge CPU checks and neighboring/static/soft schedules establish the reported boundaries. All attempted arms and historical failures remain in the [design register](DESIGN_REGISTER.json).

The exact mechanisms, legal information limits, clock precedence and negative findings are described in [MECHANISMS.md](MECHANISMS.md). In particular, the feeding policy's early effect is role assignment and routing. Its moving `grow_from` origin does **not** advance the inherited material-value ramp. The new three-quarter cohort does not guarantee one quarter of all dragons remain collectors, because inherited recruitment still exists.

The user-suggested continuity problem was tested with an addressed, expiring exit waypoint. One instrumented game records 119 packets sent, 27 accepted by the intended newborn, and ten changed selected moves. It works mechanically; its combination fails strategically. A movement EWMA was not tested. The host already has target hysteresis, and a compass average cannot represent a parent's vacating body or a corridor exit.

## Timing checks and phase trajectories

| Arm | W–D–L | Matched diagnostic games |
|---|---:|---:|
{sensrows}

These are small postselection panels, not full-map scores. Carrier arms use orchard against two opponents plus Big Empty against v32; feeding arms use Stronghold and Big Empty against v32. “Static” removes only the new carrier cutoff. Feeding neighbors retain donation at 400 and the same receiver/threat constraints. Finalist sources remain unchanged regardless of these outcomes.

![Timing checks](figures/timing_sensitivity.png)
![Crown weighted phase trajectories](figures/phase_trajectories.png)
![Feeding weighted phase trajectories](figures/feed_phase_trajectories.png)

Curves retain early losses by carrying terminal state forward. Crown markers are rounds 250/380; feeding markers are 340/400. They distinguish entering a stage in a better state from improving within it. More total mass, fewer newborn deaths or more allied-corpse income alone does not establish a stronger final crown.

The feeding failure illustrates this directly: weighted final team material rises from **73.147 to 78.704**, while weighted final longest length falls from **11.694 to 10.254**. More material survives, but its concentration into the winning carrier worsens. These are descriptive whole-panel means, not a causal estimate of one specific donor's value.

For example, on Big Empty side A against Newton, crown handling raises bed income and slightly raises own final material, yet changes a win into a loss while large-carrier losses rise from three to seven. Against v32 on that same map and side, losses fall from three to zero and own final longest length rises from 40 to 63, converting a loss to a win. See [representative replays and statistics](cycle_04/REPRESENTATIVES.json). These are explanatory trajectories, not proof that one particular death caused the outcome.

## Runtime, protocol and reproducibility

| Finalist | Judge games | Candidate turns metered | Worst fixture p99 | Maximum turn | Conservative gate |
|---|---:|---:|---:|---:|---|
| Crown | {cpu1['games']} | {cpu1['turns']:,} | {cpu1['p99']:,} | {cpu1['max']:,} | {'Pass' if cpu1['pass'] else 'Fail'} |
| Feeding | {cpu2['games']} | {cpu2['turns']:,} | {cpu2['p99']:,} | {cpu2['max']:,} | {'Pass' if cpu2['pass'] else 'Fail'} |

The gate is p99 <60M and max <80M in each tested fixture, with zero timeouts; the judge hard ceiling remains 100M. The installed CLI omits CPU counters from replay serialization, so exact unrounded verbose judge records are joined with independently decoded turn counts. Coverage is complete. See [CPU measurement provenance](release/CPU_MEASUREMENT.md), [crown CPU records](release/CPU.json), and [feeding CPU records](release/LATE_CPU.json).

The {len(parities)} finalist native comparisons match all **{sum(p['actions'] for p in parities):,} actions** and complete trajectories. Initial adapter validation separately matched 148,073 actions in ten games. Instrumented probes and off-switch comparisons also preserve their respective streams. These repeats validate execution; they are not additional strength games. Extracted archive smoke games also match their frozen references.

The final audit records {integrity['row_count']} saved panel rows, including {integrity['reused_row_count']} reused rows and diagnostic/native/judge work. Do not treat that total as an independent sample size. Frozen source/map hashes, replay winners and durations, controller faults and fixture completeness were checked; historical infrastructure launch errors remain explicitly separated. [Integrity audit](release/INTEGRITY_AUDIT.json).

The initial 16 unsupported-CLI launch attempts are excluded from playing scores. The early cycle-2 native partition contains 13 games; its remaining 51 fixtures were completed in the accelerated panel, which also reuses those exact 13 native results. This historical partial directory is not a gap in either final 132-fixture comparison.

Fault checks cover emitted diagnostics and judge timeouts. The frozen Newton control can silently take its inherited exception fallback with tracing disabled, so absence of reported faults does not prove that no internally caught exception occurred. Its source and behavior are held fixed across paired comparisons.

## Sources and continuation

The campaign read GPT and GLM reports on Vibing++, Heartbreaker and **龙虎豹** (Dragon, Tiger, Leopard; team 470). The latter's rank is dated context. The new GLM 470 and Claude/Ouroboros Vibing++ reports arrived during confirmation and were frozen under [context_refresh](context_refresh/ASSESSMENT.md), with a separate [Claude assessment](context_refresh/CLAUDE_ASSESSMENT.md). They did not change running sources. Shared corpora, incompatible action interpretations and different policy eras were kept distinct. Claude's reported 1.1.0 results are not pooled with this 1.0.0 campaign.

Remaining priorities are opening production opportunities, safe carrier survival, local salvage without a formal crown, and predicting when a parent vacates a newborn's exit. Read [CONTINUATION.md](CONTINUATION.md) for concrete next experiments, exact resume commands and the limits that should remain fixed. Final synthesis and continuation also have an identical verified copy outside the repository; the completion record stores paths and SHA256 hashes.
'''
(C / 'SYNTHESIS.md').write_text(body)
print('Final synthesis composed from completed evidence.')
