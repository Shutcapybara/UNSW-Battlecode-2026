# P-7 — Tanaka scoping review

2026-10-04 21:25 UTC; D-061 assignment, before the authorized Mac throughput measurement or any PPO run.

**Verdict: AMEND, suitable for scoping, not training release.** Keep the differentiable-network entry condition and six-iteration cap. If trees win R2, this card is void as written. Do the already-authorized in-loop measurement first; the Evaluator owns it. No throughput experiment or training was run for this review.

## Required contract before training

1. **Budget the complete loop and storage.** The G1 source records 497,642 callbacks / 62.57 seconds / 3.05 average cores: 383.49 CPU-microseconds per callback for that complete workload. This is not an independent measurement of raw engine time, and it does not substantiate the card's 80-microsecond engine estimate. It used a different encoder, untrained MLP, GPU and engine 1.2.5. The proposed Mac A10 measurement must include deploy encoding, legal masking, process communication and realistic game duration; report engine version and callback count. An untrained-policy pass remains a readiness measurement, not proof of cloned-policy training throughput.
2. **Twelve hours are already rollouts at the entry floor.** 120 million decisions / 10 million per hour = 12 hours. Using the author's *unmeasured* 8,000 update samples/sec/core with perfect eight-core scaling, four epochs over all decisions add 2.08 hours, before critic, KL-reference inference, evaluations, checkpointing and contention. Thus 15 hours is a tight cap, not an established runtime. A naive dense float32 observation store for one 20-million-decision iteration costs 95.44 GB (1,193 features), before actions/returns/critic inputs; specify compact or streamed rollout storage and measure peak RAM/disk. Keep the cap; if it cannot finish, record budget exhaustion rather than silently extending.
3. **Freeze the evaluation unit and support.** Replace “≥200 paired games” with a fixed manifest and exact count: e.g. 100 map×seed fixtures, both seats = 200 games. Define win share as wins plus half draws divided by all completed scheduled games; missing games make the result incomplete, not losses or silently smaller n. Use whole paired-fixture clusters, not dragon decisions as independent observations. Name whether the panel +.02 requirement applies to each panel or a predeclared pooled weight; I recommend each panel to prevent a pool gain hiding gen regression. Define both the seed-1 comparator pairing and interval convention before running.
4. **Separate diagnosis from the final claim.** Keep per-iteration head-to-head/KL/death mix diagnostic, but freeze the final checkpoint as iteration 6 and use disjoint training-map evaluation seeds; no choosing the best intermediate checkpoint or changing league/shaping after diagnostic wins. Safety-stop failures count as failures of the attempted line, not missing observations. Keep held-out maps/series out of training and preserve the one-shot confirmation rules; no refreshed test split. Record valid-command deaths, collisions and self-harm separately, with dragon-turn denominators. Define the invalid-death doubling rule when the clone has zero events.
5. **Pin the actor/critic boundary.** Keep the deployed observation, action wrapper, mask, normalization and per-process memory identical for clone and PPO. A critic may use privileged *current* state in training, but that does not justify a future-aware potential. For shaping, freeze gamma, time indexing, team-reward aggregation and zero terminal potential (or an equivalent explicit terminal correction). At a finite stopping time, the shaping sum is −Phi(s0)+gamma^T Phi(sT); a variable terminal term can change preferences. Discounting terminal win also changes the objective with variable game length unless specified. Per-dragon disappearance must not silently become team terminal. Avoid multiplying team reward by the number of surviving dragons. Print KL on the same masked, normalized action distribution and declared rollout population as the deployed actor.

## Replication and precision

The arithmetic above is independently calculated from the frozen G1 report and the P-7 card, not a replication of G1 hardware throughput or the author's numpy speed experiment. G1 has 712.95 callbacks/game; that is an untrained workload and cannot supply the trained-game rate. No benchmark or game was launched.

As a precision illustration only, with **200 independent decisive games**, the point rule “at least .55” means at least 110 wins. Exact binomial probabilities are .08948 at true win chance .50, .52926 at .55 and .93451 at .60. At 110/200 the central exact 90% interval is [.48937,.60951]. Actual paired games are correlated and may draw, so these are **not** the proposed design's type-I error or power. Retain the point threshold as a practical falsifier if desired, but do not describe it as a confidence bound establishing a 5-point gain. Report the paired-cluster interval alongside it.

I independently reproduced the published R2 development outputs (post-m2, 14 training maps, 97 games / 49 series / 10 teachers, 188,250 F/R/L rows of 189,630 moves). A3-400 = .71446481 [.70613843,.72387977]; A10-e4 = .67268526 [.66405781,.68148378]; paired difference = +.04177955 [.03789811,.04627209]. Intervals are 1,000 whole-series bootstrap draws, seed 7, linear 5th/95th percentiles. This establishes the current four-epoch development gap, not the eventual battery winner, deployed strength, or impossibility of neural improvement. The fixed A10 learning curve remains relevant. Receipts: `tanaka-round10/audit.json`.

## Forecasts and expected effect

Filed before Mac E2 measurement and before any PPO run. Events 2–3 are conditional on a network parent, entry conditions and a Chair-authorized attempt with the original six-iteration budget; an early safety stop fails the attempt. A tree-only outcome voids those events, not a scored failure. Event 4 is unconditional for this line this season. Chair should record these conditions alongside the four events.

| Author's event | Tanaka P(pass) |
|---|---:|
| E2: measured A10 in-loop >=10 million decisions/hour on <=8 Mac cores | .55 |
| Final head-to-head win share >=.55 after six iterations | .40 |
| Seed-1 panel delta >=+.02 after six iterations | .20 |
| Later LS-std-1 live promotion from this line this season | .10 |

Conditional on an authorized attempt, my central effect expectation is about +.03 head-to-head win share and +.005 panel win share versus the frozen clone; these are subjective point estimates, not measured effects or intervals. The panel forecast assumes +.02 on each panel if the recommended clarification is adopted; otherwise record the Chair's precise event before execution.

## Dissent and precedent

I support a separately authorized filtered self-imitation probe as a cheap baseline, but **do not make its failure a logical refutation of PPO**. Filtering only wins can amplify opponent/map luck and copies visited actions; PPO can use graded advantages and negative evidence. This additional probe needs its own fixed parent and budget and must not silently consume P-7's six-iteration budget or create another selection opportunity.

The primary [PPO paper](https://arxiv.org/abs/1707.06347) supports alternating sampled experience with multiple minibatch update epochs. It does not establish this contest's hardware cost or multi-agent performance. [Ng, Harada and Russell's shaping paper](https://ai.stanford.edu/~ang/papers/shaping-icml99.pdf) supplies the potential-difference construction; my finite-horizon telescoping calculation explains the terminal requirement above. Neither result establishes policy-invariance for an arbitrary replay-derived reward implementation. Contest-specific precedent verification remains Sugawara's separately sourced review adopted in D-061; no new claim here that imitation alone placed top ten elsewhere.

## RL translation

- Observation: identical legal deploy encoder and local process memory; privileged critic inputs remain training-only, without future leakage.
- Action: the same F/R/L policy and frozen non-policy wrapper on both sides of every comparison; mask validity is separate from collision prediction.
- Value/reward: team terminal objective, explicit discount/terminal handling, fixed potential and frozen clone KL; reward must not depend on how many processes report it.
- Demonstration: the selected clone initializes and anchors PPO; new self-play data are training observations, never confirmation rows.

## D-063 disposition — 2026-10-04 22:25 UTC

Chair adopted the evaluation contract, chunked rollouts (at most 1M rows), throughput-first order and filtered self-imitation as a baseline rather than falsifier. The original tree-only void condition is superseded: a tree-selected line may enter through a distilled network with >=.95 top-1 agreement and development accuracy within .01. My four recorded forecasts (.55/.40/.20/.10) stay on record; the two training-outcome forecasts remain conditional on an admitted network and authorized attempt, now including that explicitly approved distillation path. This ancestry expansion is recorded prospectively, not a numerical forecast revision. No actual throughput measurement or training result was inspected this wake. The author's new engine/encoder microbenchmark is acknowledged as peer evidence; it does not replace Asahi's assigned full in-loop measurement.

## Completed throughput measurement: arithmetic audit — 2026-10-05 00:23 UTC

**The reported eight-worker rollout rate reproduces; the exact <=8-core condition is not independently evidenced in the retained receipt.** This is an audit of completed job179, not a new engine run. Result SHA `8abe94ace1aacfe37c3df5616fe93f081e95daad22ae3e04d14e0afa4458a172`; benchmark source `896440ffb2625f5cde6f551e88bbe5b10624248a3cb1726e931b350f741a75d0`. Frozen copies and independent sums are in `tanaka-round13/`.

All80network tasks have unique task IDs and no returned errors. Their counts sum exactly to **16,002,916callbacks /18,371games /3,466,414rounds**. Dividing by the rounded304.1-second wall time gives189,445,898decisions/hour; the reported189,472,546 uses an implied304.05723seconds, consistent with rounding. Mean188.689rounds/game and4.6166callbacks/round reproduce. Summed worker elapsed time2415.4328seconds gives150.937microseconds/decision; encoder58.9427 and network66.8297microseconds reproduce. These are elapsed timer measurements, **not measured CPU core-seconds**. Eight worker processes and80recycled tasks are verified from code and receipt; the host exposes18logical CPUs.

The arithmetic rate is about18.95times the entry bar. The source and saved job179 configuration do not pin or record BLAS/Accelerate thread limits or process CPU usage. The daemon inherits its process environment for these script jobs; it could have contained a limiting setting, but that setting is not in the audited record. Thus eight workers should not silently become proof of at most eight active CPU cores. **Asahi: attach any retained thread-limit or CPU-accounting evidence for this run; otherwise label the result “eight workers” and ask the Chair to settle the exact E2 forecast disposition. No rerun is requested.** My .55 forecast stays on record; if the Chair accepts the exact event as passed its Brier is .2025, but I have not written a completed score into calibration.

This scope point does not dispute the measured callback rate or hold independent battery/deploy work. It also does not authorize PPO training. The code measures an untrained four-action argmax policy, uses scalar scaling by .01 rather than trained normalization, and does not implement the complete legal mask; these are limitations of the requested workload, with E1/E3 and full training readiness still separate. It does call the legal encoder and both convolutional layers per callback. Worker recycling avoids the observed address-space exhaustion for this completed run; indefinite stability, critic/update/storage costs and many-dragon cloned-policy traffic were not measured. Neither a five-minute synthetic workload nor its 4.6callbacks/round estimates the full learner's hours reliably.

Observation/action/value translation: this provides actor-side collection-speed evidence, not stronger policy actions or an improved critic. Retain the actor/critic separation, fixed rollout chunks and legal deployment checks already adopted by D-063. Training-outcome forecasts .40/.20 and season-promotion .10 are unchanged.
