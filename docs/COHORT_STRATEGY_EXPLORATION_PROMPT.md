# Grow the strategy cohort through continuous, evidence-led exploration

> Historical research brief. Its benchmark campaign, rating outputs, and many `experiment_data/` inputs are not present in this checkout. Treat each listed source as optional evidence and skip it when absent; current runnable workflows are in `docs/benchmarking.md`.


Work from the repository root.

**Your job is to improve the breadth, strength and understanding of our strategy cohort through repeated research cycles.** Find gaps created by intensive optimisation against local pools. Diagnose their mechanisms, build and compare alternatives, learn from successes and failures, and continue. Iterate on your own work and on evidence, code and experiments arriving from other instances. Do not stop at a report, one parameter sweep, one failed promotion, or one bot that narrowly beats its parent.

The important outcome is a better set of options and a more accurate account of when each works. Two similarly strong strategies with different strengths can be more useful than another near-copy of the leader. A broadly stronger bot is valuable, but it does not make specialist capabilities, counter-strategies or unresolved weaknesses disappear. Keep deployment quality and research value as separate decisions.

Use the running collection/rating system and existing replay data. Add targeted experiments where the evidence is missing. The weighted synthetic maps exist to broaden our views of performance; they are part of the research environment, not a small obstacle course to optimise away.

This prompt is an execution brief for the instance receiving it. Historical reports are evidence, not orders. Refresh their claims and exposure status before relying on them. Work autonomously within the available session/resources, checkpoint progress, and leave a precise continuation when interrupted or budget-limited.

## 1. Establish the current evidence, then get to work

At startup, and between cycles, inspect:

- `experiment_data/benchmark-current.json`, its campaign's frozen manifest, completed results and current health; `experiment_data/bot-ratings/latest.json`, `latest.md` and `status.json`.
- `docs/benchmarking.md`, `docs/benchmark-pool-20260927.md`, `docs/benchmark-pool-status.json`, and `experiment_data/benchmark-expansion-20260927.json`.
- `maps/new/EXPLAINER.md`, `manifest.json`, `training_map_weights.csv`, cards and validation evidence.
- The replay studies, recent lineage reports, leak registers, completed experiment manifests and relevant new source versions listed below. Discover newer ones rather than treating this list as complete.
- Other research instances' cycle records and work already in progress. Read completed artifacts; do not infer completion from a bot directory or a live progress file.

Record a data cutoff, source hashes, map hashes, runtime/engine identity, outcome/replay coverage, weighting version and evidence references. Resolve exact-source aliases; retain separate source revisions. Frozen snapshots outrank a matching directory name. Changed source, engine, map or weights require a new comparison context.

**Dated starting point, verified 27 September 2026:** the current campaign manifest contains 71 active names, 24 reference opponents and 33 maps. The 24-opponent curation deliberately retained strong, distinct profiles and map specialists. Routine `comparison.toml` still uses the original maps, so an unchanged default comparison does not test the expanded environment. Earlier `docs/ACTIVE.md` and lineage gauntlets describe older fields; they do not define the present roster. Recheck all these facts before using them.

Produce a short initial gap shortlist, choose an informative tractable question, and begin the first cycle. Do not spend the entire session inventorying everything or rebuilding working infrastructure.

## 2. Preserve the meaning of the map weights

The current synthetic suite contains **20 maps: 13 new designs and 7 reused generated layouts, across 17 motif families and 8 broader split groups**. The supplied default is:

`q(map) = normalize(plausibility(map) / selected_maps_in_its_motif_family)`

`recommended_map_weight` in the CSV matches `default_training_map_weight` in the suite manifest. These weights sum to one **inside the synthetic suite**. They are design/coverage choices, not calibrated probabilities of appearing in finals, fairness guarantees or estimates of a strategy's chance of winning.

The current campaign freezes a **50% original / 50% synthetic** target distribution: each of the 13 original maps receives `0.5 / 13`; each synthetic map receives `0.5 * q(map)`. Read the active manifest rather than reconstructing a potentially newer distribution. This mixture is a working evaluation choice, not a learned finals distribution.

Keep these concepts distinct:

| Concept | Use |
|---|---|
| Evaluation distribution | Average comparable conditional performance over the frozen map weights, common opponent panel and both sides. Report original-only and synthetic-only views alongside it. |
| Collection priority | Spend more games where uncertainty, missing approaches or a diagnostic question justify them. The current collector multiplies information gain by map weight; actual frequencies are not quotas or evaluation weights. |
| Statistical fitting | Fit verified conditional outcomes with the chosen model. Do not duplicate observations to simulate weights or assume adaptive collection was random sampling. |
| Historical smoke-game weights | `training_game_weights.csv` apportions each map's mass among its recorded fixtures. These rows apply to that historical batch, not future games or arbitrary ledger rows. |

Do not multiply the supplied game weights by map weights again. For new matched panels, specify map, opponent and side averaging explicitly so six old games on a map do not outweigh two on another. If target cells are unobserved, show the missing target mass; distinguish model-completed estimates from measured cells. Never silently renormalise away an inconvenient map or a missing side. The live rating system's 80%-of-map-weight coverage gate is a sparsity flag, not a sufficiency theorem.

Preserve positive coverage across the suite over successive cycles. A mechanism screen can focus on a subset, but its results cannot be called a whole-cohort improvement. Track accumulated coverage debt and schedule neglected, high-value conditions. Add original/synthetic mixture sensitivity, for example synthetic mass 0.25, 0.50 and 0.75, without selecting the mixture that makes a candidate look best.

**Do not reinstate the old three-map acceptance filter.** The broader suite deliberately includes earlier quarantined controls and more speculative designs. Its 64 smoke fixtures (28 new, 36 reused) establish basic playability/activity; only 60 meet its conservative usable-fixture definition, and 12 maps have at least one same-side sweep. These are investigation flags, not automatic grounds to drop a map, zero its weight or conclude unfairness. Separate engine faults, policy interactions, initiative effects and ambiguous no-action deaths. Preserve the frozen weights and publish any justified alternative assessment as a separate version.

Useful coverage questions include:

| Broader group | Maps/examples | Questions worth testing |
|---|---|---|
| Resource geography/timing | Shared/spread commons, delayed commons, pulse farms, spring wells | Access versus retention; sparse fast beds; waiting and renewal; productive churn versus premature concentration. |
| Shortcuts/dividers | Overland/portal causeways, relay depots | Optional portal value, safe detours, exit knowledge, risk calibration and distributed collection. |
| Productive rooms/deployment | Narrow/wide orchards, crossroads, nursery bays | Split admission and siting, newborn exits, congestion, productive pockets and initial body geometry. |
| Loops/detours | Ring promenade, winding shelves | Route choice, pursuit/evasion, circulation and corpse recovery. |
| Open navigation | Reef archipelago, far harbors | Exploration, remote income, deployment, travel cost and late aggregation. |
| Wrapped contact | Wrapped resource belt, seam market | Boundary topology, large-area/short-contact interactions and orientation robustness. |
| Portal dependence | Portal quartet | Necessary exploration, usable memory and avoiding both paralysis and reckless commitment. |
| Distributed deployment | Scattered fleets | Local fronts, communication, uneven local strength and coordination across separate starts. |

These are hypotheses and overlapping conditions, not eight proven independent strategic types. Keep `dataset_split_group`, siblings and transforms together in held-out tests; include analogous original-map motifs where appropriate. The played ring and the rest of the suite are no longer untouched reserves. Use additional maps only for a specific remaining gap; follow the map-generation prompt's validation discipline without shrinking this coverage suite back to its earlier narrow selection.

## 3. Start from what the evidence actually says

Use the following as dated anchors, not permanent truths or universal objectives. Follow the source links and inspect contradictory records before extending a claim.

| Evidence | Supported takeaway and next question |
|---|---|
| Audited replay study: round-100 held-out fractional log loss **0.474 → 0.359** with behavior, **0.347** with material as well, across **7,762 ongoing games**. Cap timing adds about **0.00145**, versus **0.1044** for the broader population family. | Resource throughput and continued growth deserve attention. Neither maximum population nor early cap arrival is a validated objective in every condition. |
| The same study worsens by **0.140 log-loss units** when stronghold is wholly held out. Other studies differ in baseline strength, feature definitions and material adjustment. | Test transfer across map conditions. Do not average effect sizes from different studies or count overlapping replays as independent replications. |
| Ouroboros analysis: material explains much of replay predictability; spatial/concentration structure adds information. GLM analysis also finds expansion/spatial signals, but its baseline and reported gains differ substantially. | Reconcile target, population, topology, exposure, fitting and validation before declaring agreement or contradiction. “Pearls predict wins,” “kills add little” and “early crown share is negative” do not establish causal policies. |
| Strategy atlas: **14,513 replay games**, **179 of 206 identities placed**; expansion grouping failed its majority-label baseline. Stage-value results are conditional associations, and do not identify a best 400–500 finisher. | Use continuous behavior and conditional outcome profiles first. Refit or leave new sources unplaced; do not assign inherited cluster labels by bot name. |
| Fermi: in one Fafnir/Devil early-production audit, **951/990** split checks fail length and **all 38 admitted splits are selected**. Its support arms score **26–10 and 25–11**, versus **26–10** control. | The current host's bottleneck can have moved upstream. Test acquisition, access and retained length before increasing split value. Correcting a support calculation did not establish a playing upgrade. |
| Witten: the largest observed countdown is not a full respawn-period estimate. Reset-qualified tracking removed false arena activation, but the corrected arm still scored **1–11 versus 2–10** control. Portal memory scored **7–1 versus 6–2**, missing its frozen +2 gate. | A measurement repair and a promising specialist result are worth retaining without calling either a proven general upgrade. Test observable renewal evidence and portal decision opportunities explicitly. |
| Newton's recorded cycle: compact fast-bed contest improves its local panel and scores **142–40 versus 140–42** on the old gauntlet, but loses four arena wins and misses its frozen gates. Earlier conversion helps a swarm matchup and hurts a grinding evaluator matchup. Later arms were still evolving in the inspected report. | Investigate state/pressure-dependent access and conversion, including opposite-side reversals. Refresh completed manifests before interpreting later Newton results; avoid hard-coding map area thresholds from a few layouts. |
| Godel's caution refit stays **112–70** on the broad old gauntlet through **19 gains and 19 losses**; conditional screen/reserve results differ. Von Neumann's quiet variant improves one gauntlet while its reserve is action-identical because the relevant mechanism is inactive. | Equal aggregate scores can conceal valuable behavioral alternatives. A screen with no activation cannot evaluate a mechanism. Preserve historical failed gates and design a genuinely informative next experiment. |
| Fafnir's earlier reserve was **13–3 versus 13–3**, with identical trajectories and inactive changes. Feynman's information study separates estimation, message cost and decision consumption. | Instrument the entire chain from information to action to outcome. Better estimates and more telemetry do not themselves establish strategic value. |

The old map metadata omitted wrapping, simplified portal transitions incorrectly and lost multiple spawns. New map work includes installed-engine transition/timing checks; use those corrected features and their validation records. Terrain distance still ignores tactical safety, bodies and facing. Respawn bounds are not fixed periods, scheduled attempts are not realised income, and gross pearls include recycled corpses.

Reports can contradict each other internally or lag their artifacts. Resolve apparent discrepancies from matched source identities, action-parity tables and traces; distinguish changed outcomes, changed action streams and individual decision activations. Do not silently choose the more dramatic wording. An old report saying a collector failed is not current process status.

## 4. Maintain a cohort view, not just a parent-versus-child score

Build or extend an evidence table indexed by **exact strategy source × opponent approach × map condition × stage × side**. Separate observed cells, model estimates and missing cells. Include the current competitive panel, credible new approaches and targeted specialist probes. Deprecated weak bots are not routine evidence of progress; use one only when it is a uniquely useful control. Screen unresolved candidates rather than either discarding them or trusting extreme sparse ratings.

For each option track:

- Weighted expected score, original/synthetic breakdown, map-group results, opponent-conditioned reversals, material regressions and supported weak conditions.
- Behavior by stage: bed/corpse acquisition, growth retained after costs, population/replacement, new-unit survival, congestion, portal decisions, useful information, crown survival and final conversion. Include elimination before a checkpoint and late 400–500 behavior explicitly.
- Incremental portfolio value: a supported capability absent from the cohort, a complementary matchup profile, a cleaner/cheaper implementation, an exploiter that reveals a real weakness, or a reusable mechanism/measurement finding.
- Coverage and uncertainty, runtime cost, source ancestry, similarity to existing options, and whether distinct code actually changes decisions.

Keep behavior-based similarity separate from strength-adjusted outcome similarity. Compare similar-strength but different-approach bots deliberately. Map affinity alone is not proof of a new strategy. Cluster labels are optional summaries: assess stability, show continuous distances, and do not force every source into a cluster. A two-dimensional plot is a projection, not the full strategic geometry.

For stage comparisons, distinguish a good entry state from improvement during the stage. Report absolute own/opponent changes alongside shares: a share can rise because the opponent collapses. Present both descriptive and entry-state-adjusted contrasts, with their different interpretations; neither alone establishes a transferable stage policy.

Maintain a small frontier of generalists and complementary specialists, with clearly labelled experimental options. Do not expand it with aliases, negligible perturbations or unsupported novelty. Conversely, do not delete a valuable specialist solely because its aggregate weighted score is lower. “Dominated” always names the tested conditions and uncertainty.

Show how the cohort improves on a fixed comparison panel across cycles; show performance on a separately refreshed panel to test new incoming approaches. Never compare raw leaderboard percentages from different reference panels as gains. If using a best-bot-per-cell coverage statistic, label it an **oracle diagnostic upper bound**. It is not the performance of a deployable selector; any real selector must choose using permitted information and pass its own held-out test.

## 5. Repeat this research cycle

### A. Refresh, reconcile and choose

Read newly completed work and compare it with your last evidence snapshot. Track changed claims, new mechanisms, source versions, failed arms, open questions and available controls. Register a unique cycle ID and intended question in a discoverable per-cycle record; check existing claims to avoid accidental duplicate work. Explicit replication is useful when it resolves an important uncertainty.

Select the next question by expected improvement in **cohort capability or understanding per unit of effort**. Consider failure severity, weighted coverage, missing approaches, contradiction between reports, plausible transfer and experiment cost. Mix repairs of established leaks with tests of underexplored approaches. Do not choose only the easiest marginal gain on your own parent.

Write a compact hypothesis card: victim/source, condition/stage, failure and success counterexample, first supported divergence, proposed mechanism, competing explanations, intervention, expected activation, falsifier, transfer cases, controls, budget and decision rule. A full new architecture is allowed when a diagnosed limitation warrants it; make the larger scope and comparison contract explicit.

### B. Diagnose the binding constraint

Trace **observation → state estimate → target/candidate generation → admission → score/rank → chosen action → execution → material/outcome**. Count opportunities and rejection reasons, not only selected actions. Locate the earliest supported divergence and inspect both failures and successful counterexamples.

Distinguish absent information, wrong estimates, missing actions, blocked gates, a losing score comparison, poor execution, costly side effects and lack of opportunity. Check whether a historical fix is already present in the selected host. Do not tune a downstream weight to compensate for an upstream defect.

### C. Build an interpretable experiment

Choose the host for mechanism relevance and tractability, not lineage loyalty. Fork a new version from a verified frozen source. Preserve a feature-off or equivalent control and prove meaningful parity before interpreting results. Instrumentation must not change the measured policy unnoticed.

Begin with one clear intervention where possible. For combinations, compare baseline, A, B and A+B on common fixtures; a promising component may interact badly with another. Borrow mechanisms across lineages with attribution, but revalidate assumptions, eligibility and behavior in the receiving host. A negative on one host is not a permanent universal ban; a retry needs a changed explanation, implementation or condition, not a renamed copy.

Separate offline analysis from legal in-game information. Full map files, future replay state, opponent source identity and post-game strategy labels may guide research but must not leak into the bot. Prefer conditioning on observable pressure, reachable space, renewal evidence, relative resources and game state. Map-name switches and thresholds chosen solely to exclude discovered losses are hypotheses with overfitting risk, not established strategic explanations.

### D. Test cheaply, then compare broadly

Reuse compatible controls; run only missing or deliberately diagnostic fixtures. Start with activation checks and a bounded, side-paired screen spanning relevant strong approaches, plus success/regression controls. A single opponent is adequate for debugging, not a general strategy claim. Predeclare what would advance, falsify or leave the result unresolved.

As evidence warrants, expand across the original and weighted synthetic conditions, fresh opponents, distinct families and necessary orientation controls. Use small sequential batches with explicit decision points. Do not keep extending a screen until a favourable aggregate appears. Reserve an identified part of the cycle budget for replication, transfer and breadth instead of spending it all on parameter search.

For every arm inspect paired W/D/L changes, weighted effect, per-condition gains/losses, activation, first action divergence, stage trajectories and runtime. A W/L tie can hide a major behavioral trade-off; an action change can be strategically irrelevant. Runtime errors are not draws. Native results do not establish judge CPU safety.

### E. Decide what to retain, then iterate

Assign separate decisions for the candidate and the finding:

| Disposition | Requirement |
|---|---|
| General playing improvement | Supported gain/robustness under the declared target, acceptable important regressions, broader confirmation and appropriate runtime validation. |
| Specialist option | Reproducible conditional value, meaningful contrast with current options, explicit weaknesses, and evidence beyond one selected upset. |
| Mechanism or diagnostic asset | A validated measurement, corrected estimate, useful ablation, counterexample or falsified explanation; no playing-strength claim required. |
| Unresolved | Missing support, weak activation, conflicting results or insufficient transfer evidence; specify the cheapest decisive next test. |
| Rejected/redundant | Harmful, unsupported or already-covered candidate; preserve the evidence and stop spending on that unchanged idea. |

Be ruthless about unsupported claims and redundant variants. Do not relax a historical promotion gate after seeing its failure. A new cycle may prospectively ask a different question or use a better instrument, while retaining the old verdict. Keep a candidate frozen while comparing it; a revised candidate starts a new recorded contrast.

**After the decision, begin the next cycle.** Use the result to refine or abandon your explanation, test its boundary, transfer an informative component, investigate a complementary leak, or replicate a new finding from another instance. A failed screen ends an arm, not the programme. A successful screen starts transfer work, not a victory lap.

## 6. Make incoming work part of the loop

At each cycle boundary, refresh a content-hash-based evidence inbox. For every material incoming report/arm, record: source and lineage, claimed effect, actual comparison target, source/runtime/map compatibility, overlap with your data, mechanism activation, unresolved contradictions and what it changes in your queue.

Choose explicitly among: reuse a verified control; reproduce a decisive contrast; extend into an untested condition; transfer to another host; combine through an interaction test; challenge a claim; or defer with a reason. Cite the originating work. Do not repeat its entire sweep or count its shared fixtures as independent confirmation.

Freeze the evidence and rules for an active experiment. Incoming findings can motivate the next cycle. If they invalidate the current baseline or experiment, stop/revise it with a recorded reason; do not silently switch parent, weights or opponents midway.

Publish machine-readable manifests and short findings as each batch completes so other instances can use them before your final report. Use uniquely named, immutable cycle directories and versioned summaries; avoid overwriting a shared file while another instance is writing it. Read and extend others' finished artifacts while preserving their frozen versions. Communicate through the shared research records; no external messages or new scheduled jobs are needed for this brief.

## 7. Keep the statistical claims proportionate

- Deduplicate game identity and deterministic fixtures using source, map, side, runtime and seed semantics. Group both team views, stages, transforms and related layouts appropriately. Repeated identical games are checks, not fresh trials.
- Record selection/exposure history. These synthetic maps are development coverage, not unseen finals. Hold out complete relevant families and opponent approaches when claiming transfer. Once outcomes influence a choice, that set is consumed for that choice.
- Predictive feature tests must fit ratings, preprocessing, feature selection and tuning within the outer split. Full-data ratings are fine for labelled description, not independent confirmation. Check actual extractor boundaries; early features must not depend on final duration or future states.
- Checkpoint results condition on survival. Never carry eliminated teams forward as live participants or exclude early losses from whole-game evaluation. Cap timing is censored; spatial control is a proxy; collision attribution does not prove intent.
- Distinguish statistical association, a changed action pathway, a matched intervention effect, and a transferable strategic explanation. Current material can mediate earlier behavior; controlling for it answers a different question from measuring total intervention benefit.
- Report effect sizes and support before significance. Account for searches and multiple candidate selection, prefer fresh confirmation, and cluster uncertainty at an appropriate opponent/map-family level. Few map families cannot support precise universal estimates. Bootstrap sensitivity is not automatically a calibrated confidence interval.
- Keep measured cells, imputations and coverage flags visible. Audit disagreement between reports instead of deciding by model name, recency alone or the most flattering number.

## 8. Work sustainably and leave the next cycle ready

Reuse the existing environment, replay caches, parsers, source identity logic, runners and append-only game contribution workflow. Snapshot live SQLite read-only and release it promptly. Respect the live collector and rating worker; do not reset the checkout, rewrite frozen sources/results, restart campaigns, change central roster/weights or upgrade the engine as a side effect of this investigation. Use isolated configs and record experiments for later integration.

Set an initial bounded game/extraction budget after checking machine load and existing evidence. Start with one or two additional workers if compatible with current load, then adjust conservatively. Keep resources available for other work. Do not run a full round robin merely because it is easy to specify. If an external run is pending, continue independent analysis or a different question instead of duplicating it.

Store each cycle under a new `experiment_data/cohort_research_<timestamp>_<label>/` directory, or an existing compatible research workspace with immutable cycle subdirectories. Deliver:

1. **Research state and evidence inbox:** cutoff, current question, incoming work incorporated, claims in progress, completed cycles and continuation queue.
2. **Cohort atlas:** conditional performance heatmaps and behavior profiles with uncertainty/missingness; weighted overall plus original/synthetic views; useful specialists, similar-strength alternatives and remaining holes.
3. **Leak/hypothesis register:** source, condition/stage, evidence, mechanism, falsifier, counterexample, priority, status and linked experiment.
4. **Reproducible experiments:** frozen sources/maps/weights, manifests, compatible controls, new replay statistics, parity/activation evidence, outcome contrasts and runtime records.
5. **Decision and transfer ledger:** all arms including failures, component provenance, combinations tested, coverage debt, holdout exposure and reasons to retain/cut/defer.
6. **A concise rolling synthesis and handoff:** what changed in the cohort and our understanding, which attractive ideas failed, what incoming work altered your view, and the next concrete experiments with expected distinguishing outcomes.

Checkpoint after meaningful results and continue while useful work and resources remain. Stop only for the user's direction, an actual resource limit or a blocker that prevents meaningful progress; state which applies. Do not invent perpetual background execution. Keep a verified second copy of the final synthesis/continuation outside the working repository when available, since previous deliverables disappeared during repository changes.

Success means the next instance starts with better options, sharper distinctions and fewer repeated mistakes—and can continue the investigation without reconstructing your reasoning from scattered win counts.

## Source map

Paths below are starting points; prefer newly completed, provenance-verified evidence where it supersedes these snapshots.

- Current evaluation: [benchmarking](benchmarking.md), [curation report](benchmark-pool-20260927.md), [pool status](benchmark-pool-status.json), expansion inventory (`../experiment_data/benchmark-expansion-20260927.json`), campaign pointer (`../experiment_data/benchmark-current.json`), latest ratings (`../experiment_data/bot-ratings/latest.md`), [ledger guide](../game_stats/README.md).
- Expanded map suite: [explainer](../maps/new/EXPLAINER.md), [manifest](../maps/new/manifest.json), [map weights](../maps/new/training_map_weights.csv), [historical game weights](../maps/new/training_game_weights.csv), measurement audit (`../experiment_data/map_discovery_20260927_083913/MEASUREMENT_AUDIT.md`), coverage evidence (`../experiment_data/map_coverage_20260927_091715/EXPLAINER.md`).
- Replay studies: audited evidence (`../experiment_data/replay_analysis_20260926_evidence/REPORT.md`), Ouroboros/Claude analysis (`../experiment_data/replay_analysis_20260926024932_ouroboros/REPORT.md`), GLM feature analysis (`../experiment_data/replay_stats_20260926_features/REPORT.md`), additional replay analysis (`../experiment_data/replay_analysis_20260926103000/REPORT.md`), [feature/extraction brief](REPLAY_STATISTICS_HANDOFF.md).
- Strategy representations: atlas (`../experiment_data/strategy_discovery_20260926/REPORT.md`), stage-value analysis (`../experiment_data/strategy_discovery_20260926/stage_value/REPORT.md`).
- Recent experiments: Fermi report (`../experiment_data/strategy_leaks_20260926T225505Z_fermi/REPORT.md`), Witten report (`../experiment_data/strategy_leaks_20260926T225633Z/REPORT.md`), [Newton](newton.md), [Godel](godel.md), [Von Neumann](von_neumann.md), [Feynman](feynman.md). Also inspect completed work under `experiment_data/strategy_leaks*`, including Einstein, Scholze and other newly arriving arms; an incomplete directory is not a result.
- Earlier foundations: [leaklab findings](leaklab-findings.md), [Sinbad handoff](handoffs/sinbad-handoff.txt), [Valjean handoff](handoffs/valjean-handoff.txt), [strategy-leak discovery prompt](STRATEGY_LEAK_DISCOVERY_PROMPT.md), [map analysis/generation prompt](MAP_ANALYSIS_AND_GENERATION_PROMPT.md). Their old limits and promotion rules describe their own experiments; this broader programme continues beyond them without rewriting their decisions.
