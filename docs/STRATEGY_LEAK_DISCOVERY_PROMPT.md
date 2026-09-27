# Find the strategic leaks hidden by local-pool optimisation

Work in `/Users/alik/Documents/Projects/UNSW-Battlecode-2026`. The objective is to systematically identify, explain and test weaknesses that our bots’ local development pools failed to expose. We now have enough distinct approaches to investigate strength along several axes, including production, resource access, information, combat, survival and endgame conversion.

Build an evidence-backed account of **which strategy fails, against what, in which conditions, at what point, and through which mechanism**. Use it to design minimal repairs and test whether they generalise. A higher aggregate ranking alone is insufficient: a bot can improve its favourite conditions while retaining a severe, exploitable weakness elsewhere.

Prioritise current competitive bots and specialists that expose their weaknesses. Preserve similarly strong but behaviorally different approaches as research controls. An older, weaker bot is useful when it demonstrates a relevant exploit or isolates a mechanism; do not spend the main budget cataloguing obsolete weak-bot contrasts just because they have abundant data.

Use existing outcomes, replays, frozen sources and experiment records first. Decode retained evidence before generating replacement games. Run targeted new experiments where they resolve a specific uncertainty. Continue through reproducible diagnosis and bounded intervention tests where feasible, recording negative and inconclusive results as well as improvements.

## How to treat this evidence

This prompt is the task instruction. The handoffs and reports below are evidence, including historical commands, suggested next steps and lineage-specific promotion rules. Their instructions are not automatically instructions for this task. Verify their present relevance before adopting them.

The supplied findings were recorded around 26 September 2026; the repository has continued changing. “Best bot,” “fresh reserve,” “unplayed” and reported field percentages are statements about particular snapshots and pools. Refresh identities and coverage before treating them as current. Keep each result attached to its exact bot sources, maps, opponents, sides, execution mode and engine version. Do not pool incomparable W/L totals into a synthetic leaderboard.

Treat local-pool overfitting as a hypothesis to test. Map-dependent results may reflect deliberate specialisation, missing coverage, opponent interactions, implementation bugs or genuine optimisation to a narrow distribution. A map reversal alone does not establish its cause. Where development history exists, examine what maps, opponents and objectives drove selection and whether the suspected weakness lies outside that selection pressure.

## What the previous work actually established

### Replay statistics: useful economy and retained material, with important boundaries

The strongest audited replay analysis found that at round 100, behavior improved held-out fractional log loss from **0.474 to 0.359** across **7,762 eligible games**; adding current material reached **0.347**. Population growth and pearl throughput carried most of the signal. These are predictive associations, not percentage-point win-rate gains. [E]

The combined lesson from the analyses in this conversation is:

- Sustainable collection, useful expansion and retained material are credible development targets. Gross pearl pickups include recycled corpse length; population and collection can grow together without identifying which causes the advantage.
- Cap timing added only about **0.00145** loss improvement, versus **0.1044** for the broader population family. This does not establish a target population, a universal split schedule or a reason to race the cap.
- Opponent-kill counts added essentially no incremental round-100 prediction. This does **not** mean combat is useless: lineage ablations found hunting/strikes load-bearing. Evaluate contact through access, losses, replacement, recovery and final results.
- Friendly deaths and replay “suicide” labels do not establish productive sacrifice or intent. Measure actual corpse recovery and retained value.
- A genuine stronghold holdout degraded prediction by about **0.140** log-loss units. Universal prescriptions inferred from the represented pool do not reliably transfer even across our existing maps.
- The earlier reports overlap substantially in their games. Agreement is corroboration within a shared corpus, not independent replication. An earlier synthesis also found temporal leakage and incompletely isolated rating fits in some exploratory pipelines. Use the audited analysis as the quantitative anchor; inspect other pipelines before reusing predictive claims. [E, O, G]

### Strategy atlas: different approaches exist, but cluster labels are provisional

The executed atlas used **14,513 deduplicated replay-bearing games**, **89,576 complete team-stage rows**, and **206 canonical source identities** from its frozen roster. It placed **179 identities** in at least one stage; 27 lacked sufficient evidence. Sinbad v07 was among the unplaced bots despite its high rating. Newer Serre/Fafnir versions need fresh identity and coverage checks rather than inherited cluster assignments. [A]

Behavior profiles used 19 descriptors across growth, resources, distribution, space, losses and movement, adjusting for map, opponent and side. Outcome and rating did not enter clustering. Strength was a separate common-panel estimate. Keep that separation: a style label should describe an approach rather than encode “good bot.”

The stage cuts were 0–50, 50–100, 100–250 and 250–400. Cluster IDs apply only within their stage and snapshot. Two-dimensional maps show about 57–63% of profile variation; compare full-space distances and supported feature contrasts. Expansion classification scored **81.5% against an 84.0% majority baseline**: it is not a validated taxonomy. Some seemingly useful groups are unstable.

The later performance overlay included **89,867 team-stage observations**, including **10,875 terminal-stage rows**. It compared changes in relative total length and longest-dragon length, accounting for starting position, map, side and both bots’ strength. Among the then-current top quartile:

| Stage | Relevant approaches | Exploratory adjusted progression |
|---|---|---|
| Opening | G7: Valjean/Porthos/Athos; G6: Von Neumann variants | G7: **+0.9 pp total-length share**, −0.5 pp longest share. G6: −0.4 pp total, +0.4 pp longest. |
| Expansion | G5 contains most leaders | The grouping provides little useful discrimination among strong bots. |
| Midgame | G6: Tew support/Ouroboros ladder; G5 includes many current leaders | G6: **+2.4 pp longest share**, versus −2.6 pp for G5. G6 has only six top-quartile members and **32% average membership retention**. |
| Conversion | G6: selected Von Neumann/Tew/Ouroboros; G7: Valjean/Porthos/Athos | G6: **+0.6 pp total**, +0.1 pp longest. G7: **−1.8 pp total**, +0.9 pp longest. |

These are material-share residuals, not win-rate effects or causal policy values. Shares can improve because the opponent loses material. State descriptors also help define the clusters. The overlay conditions on fixed earlier ratings and memberships; its uncertainty does not cover the complete analysis pipeline. Later stages select games reaching their start. There is no established best 400–500 finishing policy. [P]

Use this as a hypothesis about the trade-off between sustaining the economy and converting it into a winning longest dragon. The earlier suggestion to use Valjean for a transition experiment was one candidate, not a commitment to that host for the broader research programme.

### Sinbad: structural diagnoses beat broad retuning

The Sinbad handoff reports v07 at **150–48 on its 11-map comparison**, with gains from arrival-aware bed valuation and reducing the portal-dive incentive. Replays showed dragons wavering toward beds whose pearls were not due and portal dives fatal about **37%** of the time in the inspected sample. Portal-map results improved **36–20 → 45–11** with the dive adjustment. [S]

Relevant remaining weaknesses include losing fast-bed control on devil, openings decided within 20–30 rounds on arena, long dragons killed by short enemy heads, and a large orientation gap: about **75% versus 50%** against one opponent on original versus flipped maps. A newborn body-reading bug was separately fixed in e23; distinguish correctness repairs from strategic doctrine changes.

Small parameter changes and tie-breaking changes can materially alter deterministic fixture outcomes. Treat the handoff’s suggested sample counts as historical practice, not a universal significance threshold. Flips and transposes are correlated tests of robustness, not independent random replications. A single clean judge game provides limited runtime coverage.

### Valjean: better information can fix excessive caution; safety and conversion remain open

Valjean’s base reproduced Monte Christo v01 with all features off on **54/54 fixtures**. Its portal-memory change addressed a concrete failure: a full-dragon penalty for unseen exits left dragons trapped in portal boxes. The reported dilemma/autarky result improved **3–21 → 14–10**. On its 156-fixture pool, the parent scored **94–62**, portal memory **99–57**, and the release with Sinbad settings **101–55**. [V]

Rejected changes included broad crowding/enclosure split penalties and dead-end pearl discounts; the latter damaged pocket farming and roughly halved intake. Mass radio and several other mechanisms were inconclusive in small runs. A failure in one implementation/context does not prove the entire idea impossible; require a new diagnosis before retrying it.

The handoff reports **36 of 55 losses at the round limit**, material stalling around 60 from roughly round 120, and one stronghold trace with **56 of 107 non-feeding collision deaths** contradicting the previous turn’s “safe” assessment. Arena opponents harvested about twice as much by round 20. These are distinct hypotheses: perception/preview errors, economy under contact, and conversion failures. Do not assume an earlier feeding schedule fixes all three.

The report’s unplayed fresh maps and uncompleted release-source judge checks must have their present status verified. Similar opponents can generate identical games in particular cells; that does not add independent diversity.

### Leaklab/Fafnir: complementary doctrines are promising, and integration gates are decisive

Leaklab reports a 76,552-game ledger and pronounced map/matchup reversals. Its useful working axes are compact fast-resource production/contact, open or sparse resource distribution, and portal information/risk. These axes overlap: autarky is narrow and portal-rich; schooltime is large but has close spawns and maze structure. Recompute mechanism-relevant geometry and resource measures rather than treating area or a map label as a sufficient classifier. [L]

Examples motivating investigation:

- A devil fixture showed Serre at **197 pearls/72 splits** versus Ouroboros v13 at **1,509 pearls/522 splits**. Compact production/contact specialists exposed a weakness in a strong evaluator.
- Ouroboros v13’s compact advantage reversed on portal maps against the Sinbad/Serre line.
- Gavroche’s density approach reportedly beat Serre on both sides of big_empty; investigate the information/control mechanism and coverage rather than proclaiming a universal big-map winner.
- The Von Neumann/Godel line’s strong results on some portal/corridor maps coexist with severe devil weaknesses. A scalar score hides that structure.

The intervention ledger is especially valuable:

1. **A production score boost was ineffective on the target devil fixtures.** Earlier split-admission gates—ambient-threat charging, newborn room requirements and parent trap penalties—prevented it from changing the chosen action.
2. **A strike-support bonus was inert:** strike candidates were rejected before receiving it. A gate change and a score change are different interventions.
3. **Period-aware bed multipliers regressed badly** when early period estimates contaminated the value field. Information quality and calibration matter before increasing a feature’s weight.
4. **Self-centred support discounts hurt stronghold.** Moving support to the attacker’s vicinity then hurt big_empty: small feeders surrounding a crown were credited with protection they could not provide. The subsequent size-qualified support rule addressed that particular error.
5. **Fafnir f12 was released with screen 25–7 versus 23–9 and gauntlet 140–42 versus 134–48.** Devil improved 2–12 → 5–9 but remained a weakness; arena improved 5–9 → 6–8. Default_small regressed by one game. “Gap closed” or “no cost anywhere” overstates this result.
6. **Its reserve was 13–3 versus 13–3, all 16 fixtures identical, because the mechanisms never activated.** The stated reserve +1 promotion gate was not met. Four judge games were clean. A released directory does not establish that every promotion criterion passed; an inactive reserve cannot confirm the proposed improvement. [L, F]

Map-symmetry inference, endgame transitions, route-sensitive safety and length-density communication remain hypotheses to verify. Do not translate either “always avoid dead ends” or “pocket farming is always good” into a universal rule.

## Investigation method

### 1. Freeze an auditable view of the present field

Inventory the running ranking/pairing system without interrupting it. Freeze compatible ledger inputs, current source identities, proven aliases, map hashes, runtime/version, seed semantics and replay provenance. Identify which historical reserves have already influenced decisions. Keep failures, unknown attribution and missing replays explicit.

Reuse existing rating and analysis components where available. The September 26 atlas artifacts still exist, but several earlier chat-authored summary documents and `tools/strategy_discovery/` source files were absent when this prompt was prepared. Recover or reconstruct only what is necessary, validate against saved outputs, and record that provenance gap. Do not assume every old command is currently runnable.

Collapse deterministic repeated fixtures and duplicate sources consistently. Keep native and judge modes separate. Link every claimed effect to actual independent fixture groups. Do not invent identities for unnamed public opponents or treat a bot name as a source hash.

### 2. Build a performance map across meaningful axes

Keep three views distinct: overall common-panel strength, stage-specific behavior, and conditional matchup performance. Estimate map/side effects and inspect nontransitive matchups. Separate observed cells from model-completed cells and retain uncertainty and missingness.

Construct a compact challenge panel from current strong approaches and credible exploiters: Sinbad/Serre/Fafnir, Valjean and Von Neumann/Porthos, compact production specialists such as Ouroboros/Tew/Gavroche, and supported information/endgame specialists. Choose exact versions from evidence; avoid over-representing one family’s near-identical revisions.

Cross opponent approach with resource regeneration/access, contact distance, congestion, corridor/portal structure and stage-entry state. Use mechanism-relevant distances and connectivity. A large map can produce immediate contact; a compact map can be dominated by portal access.

Show conditional reversals, likely counters, complementary niches and weakest supported cells. High overall strength is not strict dominance. Similar-strength comparisons are valuable, but a clearly stronger or weaker specialist can still expose a mechanism. The old ±5 percentage-point paired score tolerance is a configurable screening convention, not a universal equivalence fact.

### 3. Turn statistical anomalies into leak dossiers

For each priority leak, record:

- Victim source, exposing opponents, map/state conditions, phase and independent support.
- The result deficit and first observable divergence: for example lost bed access at round 20, failed production under contact, repeated portal hesitation, newborn misread, crown exposure or late material stall.
- Predicted behavior versus observed behavior; plausible competing explanations and what would falsify them.
- Which layer is responsible: observation/state, objective formation, candidate generation, legality/safety gate, valuation, choice, execution or memory/communication.
- A representative success and failure replay, relevant trace/code locations, and an opportunity-normalised diagnostic.
- A minimal intervention, its expected activation conditions, and likely regressions elsewhere.

Prioritise by practical impact on competitive bots, recurrence across independent opponents/conditions, strength of mechanism evidence and cost to resolve. Do not turn an arbitrary priority formula into a statistical probability.

Inspect the entire decision path. Count opportunities, candidates proposed, candidates rejected with reasons, candidates admitted, choices changed, commands executed and subsequent outcomes. A parameter that never changes this path is an activation or integration finding, not a clean negative test of its intended strategy. Instrumentation itself should preserve baseline behavior when disabled.

### 4. Use matched probes and targeted ablations

Compare both candidate approaches against the same third-party opponents, maps and starting sides; add direct head-to-heads when they answer a counter-matchup question. Reuse exact historical controls where provenance matches. Do not repeat identical deterministic fixtures to manufacture sample size.

For a repair, preserve the host’s functioning mechanisms and change one diagnosed component behind a switch. Verify feature-off parity. Use small factorial comparisons when one mechanism enables another—for example admission-gate repair, valuation change, and their combination. A transplanted mechanism must carry the intended semantics, information and prerequisites, not just its coefficient.

Use both map transformations and genuinely new mechanism-bearing maps/opponents. Check that transformations preserve intended rules and geometry. Diagnose hard-coded directional assumptions or tie-breaking only when traces support that explanation; deterministic divergence alone is not a bug.

Keep discovery, tuning and confirmation separate. Freeze evaluation weights, important regression cells, candidate budget and acceptance criteria before inspecting confirmation outcomes. Test behavior activation on separate diagnostic fixtures; ensure the reserved distribution actually covers the mechanism. Do not retrofit a consumed or inactive reserve until it produces a favourable verdict.

### 5. Measure strategy value without rewarding the wrong proxy

Final expected score/WDL on the declared challenge distribution is the primary outcome. Report important map/approach regressions alongside the aggregate. Useful secondary diagnostics include new bed income, retained material, productive collector survival, contact and recovery value, absolute longest-dragon growth, crown survival, and successful conversion by the actual win rule.

The engine’s round-limit objective is longest living dragon, then total living length; elimination can finish earlier. A higher population, larger territory estimate or better intermediate share is not sufficient evidence of improvement. Include early terminations in evaluation. For stage analysis, distinguish entry cohorts, incomplete stages, terminal outcomes and missing measurements; never fill a dead strategy forward as if it continued playing.

Use pre-checkpoint information only for prediction. If reporting held-out predictive value, fit ratings, preprocessing, representations and feature selection within the outer split. Resample/group at appropriate fixture, source-pair and map-family levels, with sensitivity to related bot revisions. Label fixed-model descriptive analyses honestly. Development samples, reserves, flips and repeated deterministic games must not silently become independent trials.

Runtime decisions may use observations, legitimate game information, memory and received reports. Offline full replay state is diagnostic evidence, not a feature the bot can magically observe. Verify deployed-source judge cost on relevant stress cases; native success and one clean sandbox sample do not establish general budget safety.

## Initial priorities and host selection

Start with these questions, revising their order when the refreshed evidence warrants it:

1. **Production under contact:** which strong evaluators concede renewable resource access, and which candidate/gate/value decisions prevent useful replacement? Retest the remaining Fafnir/Serre devil and arena gaps without blindly rewarding population.
2. **Information versus risk:** distinguish portal paralysis from reckless diving; test whether memory, credible support and route-aware safety remain calibrated across congestion, long dragons and map transformations.
3. **Survival and conversion:** separate state/preview mistakes from allocation mistakes and from an inadequate late objective. Extend measurement through rounds 400–500 before claiming a best finisher. Determine whether the economy-to-crown transition should depend on local return, losses, threats and available time.

Choose a host for the specific leak, its current supported strength, and the clarity of the intervention. Serre/Fafnir and Valjean are plausible but different hosts. Four-game head-to-heads, architectural convenience and earlier chat recommendations do not settle this choice. Combining the “best cluster per stage” is a hypothesis requiring compatibility and transition tests; cluster labels alone do not specify executable policies.

## Deliverables and stopping criteria

Save a reproducible run under `experiment_data/strategy_leaks_<timestamp>/` with a concise Markdown report and machine-readable supporting tables. Deliver:

1. A current evidence inventory and a strength/approach/condition map, with uncertainty, aliases and missing coverage visible.
2. A prioritised leak register and detailed dossiers for the most consequential supported failures, including counterexamples and competing explanations.
3. A frozen probe/ablation manifest, reusable controls, activation diagnostics and every attempted result, including errors, nulls and regressions.
4. Tested repairs where justified, with source hashes, feature-off parity, targeted mechanism evidence, broader evaluation and honest confirmation/runtime status.
5. A clear decision for each candidate: retain as a specialist, advance for confirmation, promote within a stated scope, reject, or remain inconclusive. State which original weaknesses remain.

Success means exposing and explaining meaningful cross-strategy failures and testing whether targeted changes repair them without hiding regressions. A well-supported rejection or a demonstrated inactive mechanism is useful progress. Do not declare universal robustness, or relax a failed promotion gate after seeing the result.

Coordinate new experiments with the existing runner and avoid competing campaigns for identical fixtures. Preserve ongoing work and existing records. Use resumable, bounded batches, a compatible installed runtime and writable temporary/cache directories. There is no instruction here to restart infrastructure, upgrade the engine or repeat obsolete experiments indiscriminately.

## Source map

Paths are relative to the repository unless absolute. The two repository handoff copies were verified byte-identical to the supplied Downloads files when this prompt was prepared on 27 September 2026.

- [S] `docs/handoffs/sinbad-handoff.txt`; supplied as `/Users/alik/Downloads/SINBAD_HANDOFF.md`.
- [V] `docs/handoffs/valjean-handoff.txt`; supplied as `/Users/alik/Downloads/valjean-handoff.md`.
- [L] `docs/leaklab-findings.md`; preserve its complete failed-arm ledger and reserve caveat.
- [F] `bots/fafnir-v01-phalanx/README.md`; actual foundation name is `bots/serre-v01-foundation`, not the shorthand `serre-v01`.
- [A] `experiment_data/strategy_discovery_20260926/REPORT.md`, `snapshot.json`, `behavior.json`, `validation.json`, `ratings.json`, stage/coverage Parquets and bootstrap arrays.
- [P] `experiment_data/strategy_discovery_20260926/stage_value/REPORT.md`, `method.json`, `summary.json`, `observations.parquet`.
- [E] `experiment_data/replay_analysis_20260926_evidence/REPORT.md` and its provenance/results.
- [O] `experiment_data/replay_analysis_20260926024932_ouroboros/REPORT.md` and saved extraction/results.
- [G] `experiment_data/replay_stats_20260926_features/REPORT.md` and audit/results.
- Data/tool entry points: `game_stats/runs/`, `game_stats/sources/`, `experiment_data/benchmark-current.json`, `experiment_data/bot-ratings/`, `tools/performance_model.py`, `tools/comparison_metrics.py`, `tools/public_replay_review.py`, `tools/leaklab/`, and the existing lineage harnesses when present.

[S]: handoffs/sinbad-handoff.txt
[V]: handoffs/valjean-handoff.txt
[L]: leaklab-findings.md
[F]: ../bots/fafnir-v01-phalanx/README.md
[A]: ../experiment_data/strategy_discovery_20260926/REPORT.md
[P]: ../experiment_data/strategy_discovery_20260926/stage_value/REPORT.md
[E]: ../experiment_data/replay_analysis_20260926_evidence/REPORT.md
[O]: ../experiment_data/replay_analysis_20260926024932_ouroboros/REPORT.md
[G]: ../experiment_data/replay_stats_20260926_features/REPORT.md
