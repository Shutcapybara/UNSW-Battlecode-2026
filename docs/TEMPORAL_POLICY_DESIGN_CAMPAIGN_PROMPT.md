# Iterative design campaign: make policy depend on game phase

## User-supplied context

**Other-team analysis / additional files:** `<paste analysis here or list file paths; optional at startup>`

**Preferred lineage/framework:** `<optional; otherwise choose from current evidence>`

**Explicit resource or time limit:** `<optional; otherwise use bounded batches, check load, and continue while useful progress is feasible>`

Work in `/Users/alik/Documents/Projects/UNSW-Battlecode-2026`.

## Mission and working contract

Take a promising existing bot/policy as the framework for an **aggressive, sustained campaign of temporal policy design**. Build and test a suite of ideas for opening, middle and endgame behavior. Start with explicit phase thresholds because they are easier to inspect and ablate; also test whether bounded continuous time features or time-plus-state conditioning improve on those thresholds.

This is an instruction to **design, implement, run experiments, interpret the results, revise, and continue**. A proposal alone is not the deliverable. Neither a single failed screen nor a first successful variant completes the task. Do not return after one iteration to ask whether to proceed. Failure should change the next experiment, not end the campaign.

Aim for stronger playing options and a better explanation of when behaviors pay. Improve an existing framework substantially; avoid a catalogue of tiny threshold changes with no strategic distinction. Preserve useful specialists and rejected-mechanism evidence. A broadly stronger candidate is desirable, but meaningful conditional improvements and a well-tested boundary are also valuable.

Plan several adaptive cycles—normally three to five substantive cycles covering multiple mechanism families—then continue or redirect according to evidence and the user's actual resource constraints. This is an initial planning horizon, not a quota of variants or a self-imposed stopping rule. Use bounded batches so you can cut bad arms, incorporate incoming work and protect other running jobs.

## 1. Choose the framework and freeze the baseline

Refresh the current campaign, ratings, source identities, runtime evidence, new reports and incoming experiments. Briefly compare two or three plausible frameworks for:

- Supported strength and coverage on both original and synthetic maps, including weaknesses that timing could plausibly address.
- Existing production, risk, routing, crown/feeding and phase mechanisms; ease of changing their conditioning without rebuilding the whole bot.
- Runtime margin, instrumentation, reproducibility and ability to preserve the original behavior behind an off switch.

Choose one primary host and freeze its exact source, parameters, engine and baseline records. Keep an alternative host in view for later transfer or if evidence exposes an architectural limitation. Make the choice yourself unless the supplied context fixes it. Do not simply pick the highest sparse rating, start from an empty scaffold, or spend the entire session deciding.

**Dated context, checked 28 September 2026:** the active campaign has 105 frozen versions, 24 references and 33 maps. Its latest inspected ratings include established Gavroche v32 and Newton x10, while several newer Gavroche leaders are sparse and have unresolved conservative CPU gates. Serre/Fafnir and the Valjean/Porthos family remain useful alternative frameworks and controls. This is a shortlist, not an instruction to use one particular chassis. Check the actual sources and latest evidence before selection.

Preserve the original parent throughout the campaign. Compare revisions with both that parent and the best relevant incumbent on common fixtures; a chain of tiny improvements on changing screens is not evidence of overall progress.

## 2. Read the temporal evidence critically

Begin with the linked sources and any user-supplied team analysis. Convert external observations into testable hypotheses, not copied constants or presumed internal algorithms.

| Starting evidence | Design implication to test |
|---|---|
| Newton's conversion stop at round 200 flips a Devil/Tew length race, but loses a Devil/evaluator grinding fixture. Its final x10 record is 147–35 on the old gauntlet after timeout correction, yet it failed its frozen screen gate. Its reserve was action-identical because the mechanism's area gate excluded both maps. | Timing can have real, opposing effects across conditions. Preserve the failed verdict, test activation, and investigate continued production versus conversion under observable pressure. |
| Faye's synthetic-map investigations describe churn opponents that either establish a large population advantage or stall, with differences between opponents. | A fixed clock may be standing in for an evolving resource/control race. Test state-conditioned timing without hard-coding opponent names. |
| Gavroche already has numerous early/middle/late search and sprint-budget variants. Some reduce CPU cost but lose important map matchups. | Reuse these experiments. Distinguish temporal strategy changes from changing the action/search budget, and avoid rediscovering an existing arm under a new name. |
| The team-470 report describes donor-like behavior beginning at round 300 on two maps and at 400 elsewhere in one policy era, with another era differing. A learned local graft was inactive on its main screen; a broad early-feeding rule did not demonstrate improvement. | The interesting question is joint timing, eligibility and recipient choice. Map dimensions and offline classifier accuracy were inadequate substitutes for that mechanism. |
| Vibing++ reports describe late redistribution and concentration around a post-r320 pattern; Heartbreaker retains much more population and often loses with a total-material surplus. | Test multiple conversion doctrines. Do not infer that copying another team's round number or death command transfers its success. |
| The replay studies associate early growth with success, but have important map-transfer failures. The strategy atlas does not establish an optimal rounds-400–500 policy. | Use replay evidence to locate decisions and propose regimes. Establish benefit through controlled interventions, including early eliminations and the actual final objective. |

Verify target team, submission/era, map and side when interpreting public reports. Different reports can use overlapping games or incompatible cuts. Do not treat them as independent votes for a threshold. An observation that behavior changes at a particular round does not prove that boundary is optimal, clock-driven, or implemented as a hard switch.

Maintain a short context-to-experiment table: **claim → confidence → local analogue/prior attempt → proposed change → expected activation → falsifier**. When new context arrives, update this table and the next-cycle queue. Do not silently change an experiment already underway.

## 3. Build an explicit temporal design surface

First inventory every clock-related rule in the host: opening exceptions, split stop, crown election, feeding, aggression, exploration, search caps and emergency overrides. Record what actually activates and which rule takes precedence. Avoid layering a new phase controller over contradictory old clocks without noticing.

Use the actual global game round `r` and configured maximum horizon `R`. Distinguish:

- Absolute time: `r`.
- Normalised progress: `r / R`.
- Time remaining: `R - r`.
- Dragon age / time since a local event: a separate feature, never a substitute for game time.

Never use the game's eventual observed duration as the normalising horizon. Compute phase on each decision; a child born late must not restart the team's opening because its process is new. Verify the runtime's zero-based round convention, initialization and memory semantics.

Implement a small auditable interface returning the phase, relevant gates or schedule weights and their reasons. Keep legal-action checks, protocol validity and hard runtime safeguards active throughout. With the new temporal feature off, reproduce the frozen parent's behavior. Instrument phase decisions without silently changing it.

### Track A — explicit phases first

Start with `opening: r < t1`, `middle: t1 <= r < t2`, `endgame: r >= t2`, with `0 <= t1 < t2 < R`. Give each phase a concrete behavioral purpose, not merely a label. Phase-specific choices may include production admission and size, resource targets, sprint expenditure, commitment, material concentration and protection.

Use a small coarse search followed by local refinement of promising regions. As illustrative initial hypotheses for a 500-round game, opening boundaries could span roughly 20–100 and conversion boundaries 200–440, including the previously studied 200/300/320/400 region. Adapt these ranges to the host's traces and supplied evidence. They are not defaults to adopt and do not justify an exhaustive Cartesian sweep.

Do not assume every mechanism should switch together. Compare a shared phase clock with a few separately justified clocks—for example stop ordinary production, elect/protect a receiver, then admit donations. Preserve emergency production and survival where appropriate. Test neighboring boundaries, not only the best individual integer.

### Track B — time plus observable state

Test whether a clock enables a regime while state decides when or how strongly to enter it. Candidate conditions include observed pressure/churn, resource access, local congestion, useful collector opportunities, safe recipient availability, estimated travel time and crown loss. Specify how each signal is available to the acting dragon and how uncertainty is handled.

Compare the inherited policy, a state-only version of the **new** mechanism, a time-only version, and time-plus-state. Do not remove all inherited clocks and call that a clean ablation. Use hysteresis, persistence or a latch when needed to prevent oscillation; permit deliberate recovery/re-entry where warranted. These design choices themselves need measurement.

Avoid map-name and opponent-name tables. If geometry matters, use observable or legally inferred properties with transfer tests. Team coordination cannot use omniscient replay state or assume all dragons share memory.

### Track C — bounded continuous schedules

After establishing the interpretable threshold baseline, run a genuine comparison with a low-complexity continuous schedule: clipped linear ramps, piecewise-linear weights, or a small smooth transition. One possible form is:

`score(s, a, r) = parent_score(s, a) + g_open(r/R) * delta_open(s, a) + g_late(r/R) * delta_late(s, a)`

Keep the schedule bounded and preserve the score's units and intended signs. Multiplying every candidate score by the same positive time factor usually preserves its ranking; a useful temporal change must alter relative preferences, eligibility or action generation. Do not scale away safety or multiply every heuristic indiscriminately.

Compare hard and soft transitions implementing the same intended trade-off under comparable search budgets. Inspect boundary instability, gradual loss of production, donor cascades and downstream runtime. A small learned gate or tree using time plus legal state is optional if it answers a specific unresolved question; a larger ML model is not required for this campaign.

## 4. Test a suite of strategic ideas

Maintain competing hypotheses, not only descendants of the latest winning constant. Start with the most promising distinct families below and replace them as evidence arrives:

| Family | Intervention and question |
|---|---|
| Opening investment | Temporary production/collection priority; split admission, size and siting; preserve enough newborn survival for growth to compound. Is an early population gain retained? |
| Middle-game economy and pressure | Change contested-resource commitment, exploration, replacement and sprint expenditure after the opening. Is time useful beyond the actual contact/resource state? |
| Production-to-conversion | Compare stopping, tapering, selective continued production and a minimum useful collector force. Is the gain concentration, reduced waste, or merely a favourable matchup? |
| Conversion lead time | Start preparation early enough for travel, collection and redistribution. Does staged preparation outperform an abrupt late switch? |
| Selective donors and receivers | Condition transfer on recipient knowledge, reachability, survival, expected recovery and donor opportunity cost. Does more final longest length justify lost material and defensive capacity? |
| Crown protection and handoff | Different late risk/sprint/split-size rules for long carriers and small collectors; preserve a viable receiver and fallback after crown death. |
| Recovery and reversibility | Resume production or change recipients after losing the crown, local control or a productive region. Does a one-way phase latch strand the team? |
| Staggered transition | Keep roles or subsets productive while others convert. Compare coherent coordination with every dragon switching simultaneously. |
| Time-budget interaction | Separately test search/action-budget schedules where they constrain the strategy. Measure strategic loss and CPU benefit rather than treating speed as strength. |

Not every family deserves equal simulation. Diagnose the binding constraint before sweeping it. An early bottleneck can prevent a late policy from ever mattering; improve activation or choose a different test rather than declaring the endgame idea neutral. Combine promising mechanisms only after informative single-component tests, and use baseline/A/B/A+B comparisons to expose interactions.

## 5. Run adaptive cycles with strong comparisons

### Cycle setup

Write a compact manifest before each batch: parent and candidate identities, hypothesis, temporal mechanism, parameter ranges, opponents/maps/sides, activation expectations, outcome/diagnostic metrics, compute budget and advancement/rejection rules. Use the same compatible controls for paired contrasts. Freeze the evidence and map-weight version for that comparison.

Plan the campaign across several cycles. A useful starting sequence is: diagnose and establish phase baselines; widen the best threshold regions and test state conditions; compare continuous/staggered schedules and selected combinations; test transfer and robustness. Change that sequence when the results justify it, recording why.

### Cheap checks before broad games

Verify off-switch parity, boundary cases (`t-1`, `t`, `t+1`), late-born dragons, unit-age/global-time separation, legal actions, score bounds and phase-state transitions. Test zero-coefficient/equal-phase configurations where relevant. Confirm that each advertised change can actually alter a decision on the chosen screen.

For each arm record the activation funnel: phase eligible → state eligible → action available → score/admission changed → selected action changed → resulting trajectory/outcome. A changed parameter, entered phase or logged branch is not evidence of useful activation.

### Focused screening and widening

Use a compact paired screen against several strong, behaviorally different opponents, with targeted failure cases and success/regression controls. Inspect both sides. Reuse completed compatible fixtures. Reject obvious defects early; allocate more evidence where uncertainty is decision-relevant. Do not run every arm against the entire roster.

Advance informative candidates to broader opponents and weighted maps. Preserve a fixed panel for comparisons across cycles and a separate expanding panel for incoming strategies. Test components on another suitable host when their value appears reusable, without requiring a complete port for every rejected arm.

**Current evaluation context:** the 13 original maps share 50% of target weight; the 20 synthetic maps share 50% using their supplied family-balanced weights. Refresh and use the active frozen manifest. The default single-bot comparison still covers original maps only, so make an explicit expanded config for broad evaluation. Do not silently drop difficult synthetic maps or mistake their smoke-game weights for weights on new games.

Report original-only, synthetic-only, weighted combined and relevant map-group/opponent results. Show missing target mass and distinguish observed cells from model completion. Collection priority may focus on diagnostic gaps; it does not change the evaluation target. Check sensitivity to reasonable mixture changes without selecting the one that flatters a candidate.

### Diagnose each result and continue

For failures, determine whether the cause is inactivity, mistimed activation, wrong behavior inside the phase, insufficient input information, coordination failure, adverse interaction, a real strategic trade-off or an implementation/runtime defect. Choose a discriminating next experiment.

For successes, identify where they occur and what they cost. Check adjacent thresholds, shifted schedules, component ablations, different opponents and related but untrained map families. Prefer a broad stable region over a narrow isolated optimum. Do not stop at a win on the screen that selected the schedule.

At the end of every cycle, update the finding/decision ledger and **start the next useful cycle without asking for permission to continue**. Incorporate new reports, completed arms and contextual team analysis from others. Preserve frozen work, cite the source, and reuse controls rather than duplicating another instance's study. If a whole family fails, move to a different family or host with an explicit explanation.

## 6. Separate temporal benefit from confounding and selection

Use W/D/L under the declared distribution as the primary playing outcome, alongside supported weak-condition performance and runtime. Stage diagnostics explain the result: bed/corpse income, retained growth after sprint/loss costs, productive splits, newborn survival, population, longest length, donor recovery, carrier survival and terminal cause.

Distinguish a good stage entry state from improvement within that stage. Whole-game interventions begin from the same initial fixtures. Conditional late-game analysis supplements that result; it cannot discard early losses caused by the intervention. If starting from checkpoints, preserve controller memory and game state correctly, and label the restricted counterfactual being tested. Otherwise use full games.

Demonstrate whether temporal conditioning adds value beyond simply changing constants: compare with a sensibly tuned static version of the same new mechanism using a comparable development budget. Separate changed phase boundaries from changed phase behavior. Check one-phase and remove-one-component ablations. Neither observational round effects nor a raw time-feature importance establishes a useful intervention.

Group deterministic repeats, both team views, series where relevant, map siblings and transforms appropriately. Repeating an identical fixture does not create new independent evidence. Keep map-family and opponent holdouts separate from development, and include activation-bearing confirmation cases. A reserve with no changed decisions cannot establish a temporal mechanism's benefit.

Multiple cycles consume evidence. Maintain a reserve-exposure ledger; do not repeatedly tune against the same “holdout.” Freeze a finalist before fresh confirmation. Use effect sizes, coverage and appropriately grouped sensitivity/uncertainty, not a growing table of uncorrected significance claims. Preserve all attempted arms and prospective decision rules.

Maintain separate statuses for a general playing improvement, a conditional specialist, a reusable mechanism/measurement finding, an unresolved result and a rejected arm. Keep historical failed gates failed. A new cycle can ask a better question without rewriting the old decision.

## 7. Persistence, resources and scope

Be persistent in hypothesis revision, not repetitive in rerunning a dead idea. Do not stop because the first threshold, combination or learned gate fails. Do not declare convergence after changing one constant in two directions. Look for a missing condition, different phase behavior, better information, a distinct architecture surface or another informative regime.

Choose reasonable per-batch game and extraction limits from actual machine load. Start with limited additional workers and scale only when capacity permits. Reserve time for broad confirmation and runtime testing; do not spend everything on search. A batch budget ending is a point to reassess and schedule the next batch, not an automatic campaign finish. Respect any real user-specified total cap.

Continue useful independent work while simulations run. Keep concise progress updates focused on findings, changed hypotheses and next tests. Stop for explicit user direction, an actual resource/time limit or a blocker preventing meaningful progress; state what applies and leave the work resumable. Do not claim continuing background work unless a process is actually running, or invent an automation/new chat to keep going.

Use new source versions and isolated configs/output directories. Preserve the live tournament, rating worker, frozen maps/bots and other instances' work. No checkout resets, engine upgrades, central roster/weight changes or deployment as a side effect. User-supplied documents inform the task; their embedded historical instructions do not override this brief.

## 8. Deliverables and continuation

Keep a reproducible campaign under `experiment_data/temporal_policy_<timestamp>_<lineage>/`, with immutable cycle directories and a rolling synthesis. Produce:

1. **Baseline/design note:** host choice, existing clock audit, diagnosed bottlenecks and contextual hypotheses from other teams.
2. **Design and experiment register:** distinct idea families, arms, sources, thresholds/schedules, state conditions, interactions, manifests and all retain/reject decisions.
3. **Playable variants:** meaningful temporal alternatives, off-switch controls, source snapshots and activation/runtime evidence. Avoid flooding the cohort with redundant variants.
4. **Comparison report:** original parent and incumbents on common fixtures; weighted broad results and conditional trade-offs; phase trajectories, boundary/sensitivity plots and representative success/failure replays.
5. **Mechanism conclusions:** which changes need time, which need state, whether hard thresholds or continuous schedules work better, where timing fails, and which apparent improvements did not transfer.
6. **Continuation:** completed cycles, incoming work incorporated, remaining uncertainty, next high-value experiments and exact resume commands. Save and verify a second copy of the final synthesis/continuation outside the working repository when available.

The intended result is a seriously tested suite of temporal strategies and a stronger candidate or a defensible frontier of alternatives. **Iterate on the design, not just the threshold; test the explanation, not just the score; and keep going when the first answer is disappointing.**

## Evidence and implementation entry points

- [Current campaign pointer](../experiment_data/benchmark-current.json), [latest ratings](../experiment_data/bot-ratings/latest.md), [benchmarking](benchmarking.md), [weighted synthetic maps](../maps/new/EXPLAINER.md), [map manifest](../maps/new/manifest.json).
- [Newton completed cycle](newton.md), [Faye cohort findings](faye.md), [Gavroche experiment history and CPU evidence](gavroche-resume-2026-09-26.md), [Gavroche replay diagnosis](gavroche-v17-replay-review-2026-09-26.md).
- [Fermi](../experiment_data/strategy_leaks_20260926T225505Z_fermi/REPORT.md), [Witten](../experiment_data/strategy_leaks_20260926T225633Z/REPORT.md), [Godel](godel.md), [Von Neumann](von_neumann.md), [Feynman](feynman.md).
- [Team 470 report](../experiment_data/team_recon_470_20260927T150303Z/REPORT.md), [Heartbreaker report](../experiment_data/team_recon_62_20260927T140359Z/REPORT.md), [Vibing++ report](../experiment_data/team_recon_306_20260927_codex/REPORT.md). These are dated evidence packages; inspect related reports, conflicts and newly supplied context rather than treating one author as authoritative.
- [Audited replay statistics](../experiment_data/replay_analysis_20260926_evidence/REPORT.md), [strategy atlas](../experiment_data/strategy_discovery_20260926/REPORT.md), [stage-value analysis](../experiment_data/strategy_discovery_20260926/stage_value/REPORT.md), [continuous cohort-research brief](COHORT_STRATEGY_EXPLORATION_PROMPT.md), [game and information constraints](BAHAMUT_HANDOFF.md).
