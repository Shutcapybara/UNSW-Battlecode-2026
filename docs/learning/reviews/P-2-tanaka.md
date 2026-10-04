# P-2 — Tanaka council review

2026-10-04, round 1. Verdict: **AMEND; hold confirmation until the Chair resolves the data and baseline defects.** The queen-information gain reproduces on the frozen development predictions. Neither proposed gate, as written, makes the existing artifact a split-compliant Phase 3 result.

## Replication

Read only the frozen development artifacts in `build/hinata/v0/fit-lq`; no held-out map outcomes, model refit, or `confirm` call. Independent weighted-rank AUC and bootstrap implementation: `tools/tanaka/p2_audit.py`; full results and hashes: [audit](tanaka-round1/p2-audit.json), [table](tanaka-round1/p2-table.csv).

The training-file hash is exactly `c958e8c7f830c4c5d1b5e322adc44f16152d2a4c4c96714d5d1c30eb091cae76`. Population: post-m2, decisive, in-scope, running checkpoint states; 5,799 development games, 1,777 series, 14 maps, 71,956 two-side training rows. These comprise **3,427 ranked and 2,372 unranked games**, pooled by the original fit. There are no Autarky/Maze/Trauma rows and no duplicate game/side/checkpoint keys. Counts are exact artifact censuses, not sampled estimates.

All 14 cells' AUCs and original 5th/95th-percentile game-bootstrap endpoints reproduce within 3e-16 (1,000 replicates, seed 7). Independently optimized calibration slopes differ by at most 0.00050, consistent with optimizer tolerances; the gate reading is unchanged. G-asis fails; the printed table passes G-amend. This replicates predictions-to-metrics, not training-to-predictions: current source hash starts `2920bb5746c41cac`, whereas the registry names `3138d10777ce5490`. Archive the latter source and dependency versions to complete provenance.

A second, paired **whole-series** bootstrap retains the same predictions and rows, drawing all games of each selected series together, 1,000 replicates, seed 7:

| RL checkpoint | Games / series | ΔAUC | Original game 90% interval | Series 90% interval |
|---|---:|---:|---|---|
| 50 | 3,503 / 1,545 | +0.01969 | [+0.01279, +0.02630] | [+0.01253, +0.02678] |
| 150 | 3,387 / 1,528 | +0.03119 | [+0.02300, +0.03954] | [+0.02223, +0.03909] |
| 250 | 3,273 / 1,503 | +0.05574 | [+0.04625, +0.06606] | [+0.04470, +0.06656] |
| 400 | 3,141 / 1,482 | +0.10172 | [+0.08906, +0.11390] | [+0.08748, +0.11415] |

These are **mixed-mode development** estimates, conditional on the fitted OOF predictions. They are not ranked-only claims, do not incorporate refitting/model-selection uncertainty, and do not prove generalization to new maps or series.

## Decisive prerequisites

1. **The frozen fit consumed reserved series.** Applying the exact D-046 hash rule to its training rows gives **539/5,799 games in bucket 0 (173/1,777 series)** and **555/5,799 in bucket 1 (175/1,777 series)**. The loader filters map names but never filters series buckets. All 96 LOMO folds also share series across fitting and scoring: **28,216/35,948 scored game-checkpoint rows** have their series in that fold's training set. This does not mean map-name exclusion failed; it means the table is not an independent-series transfer test.
2. **Do not silently repair by refitting P-2.** D-049 freezes the 10:52 artifact. The Chair must retain that artifact as development-only or authorize a separately registered data-corrected candidate with fixed hyperparameters. Data must mark the already consumed test/validation series; filtering them from a later fit does not undo their use for model selection. Preserve the frozen maps and hash rule; no better holdout draw. Define an uncontaminated evaluation population prospectively and audit overlap with all consumed series before reading labels.
3. **Freeze the comparator too.** `cmd_confirm` reloads current non-held-out rows and refits Φ, while scoring frozen V0b coefficients. No Φ export exists in `fit-lq`. Archive a baseline fitted solely from the same frozen training rows, its exact implementation and coefficients, before confirmation; never quietly substitute newly decoded data for the baseline. This is a comparator reconstruction, not permission to refit V0b.
4. **Complete the confirmation implementation before using it.** It currently writes point AUC/slope only, without ΔAUC intervals or a G-amend verdict; missing model files are silently skipped. Require every declared cell, both outcome classes, a population/series manifest, immutable predictions, and an atomic one-shot claim before scoring. Undefined or absent cells mean INCOMPLETE. Preserve a failed run's receipt rather than allowing a fresh confirm after partial output.
5. **Separate populations.** Freeze ranked as the primary confirmation population and report unranked separately; do not decide which binds after seeing either table. Also state that checkpoint metrics condition on the game still running. A low-power late elimination cell is not proof that queen information is useless.

## Gate recommendation and power

Use **G-amend with corrections**, once the prerequisites have a Chair ruling:

- Paired whole-series 5th-percentile ΔAUC > −0.01 in every predeclared regime/checkpoint cell; late RL r150/250/400 lower bounds > 0. Freeze 1,000 replicates, seed 7, and percentile interpolation. Resample the same series together across checkpoints and both models.
- Replace the one-sided slope clause with **|slope_V−1| ≤ |slope_Φ−1| + 0.05** from r25. The proposed `slope_V ≥ slope_Φ−0.05` would accept arbitrarily large, badly under-confident slopes. Report slope/intercept intervals and Brier loss separately; this point-slope rule alone is not a calibration-equivalence test.
- Retain **ranked RL r50 AUC ≥ 0.66** and AUC_V ≥ AUC_Φ. The changed baseline does not itself justify lowering a predeclared absolute usefulness target. A failure produces diagnosis, not a new threshold or model.
- State the estimand as performance on the fixed held-out maps, and report each map separately. Do not label the result an all-live-map or unseen-map guarantee.

Three maps can supply many games for a **conditional fixed-map** test, but only one elimination map (Autarky) and two RL maps (Maze/Trauma) cannot estimate the distribution of transfer across map classes. No bootstrap over games or series creates additional independent maps. Actual confirmation power needs the frozen per-cell positive/negative counts, series structure and paired prediction covariance; I have not read confirmation outcomes to estimate it.

For planning only, a one-sided normal approximation requires SE < 0.01/(1.645+0.842) ≈ **0.0040** for 80% power to establish a −0.01 margin when the true ΔAUC is zero. Detecting true +0.03 superiority needs SE < **0.0121**. These are analytic design calculations, not empirical confidence intervals or measured held-out power. Requiring every cell to pass lowers joint power. A conjunction of prespecified component tests does not automatically require Bonferroni for the single all-components-pass claim; intervals still are not simultaneous and many candidate attempts remain a separate selection issue.

## Predictions and dissent

Subjective probabilities for the **frozen P-2 artifact meeting the numerical clauses in one valid confirmation**, conditional on resolving provenance and eligibility without changing its weights: **P(G-asis)=0.03; P(G-amend as written)=0.35; P(the corrected gate above)=0.20**. These are forecasts, not measured rates or intervals. Expected RL ΔAUC is roughly +0.02 at r50, +0.04 at r250, +0.08 at r400; map and population shift could reverse that expectation. Current eligibility is HOLD irrespective of these probabilities. Score the prediction only for the gate/population the Chair actually freezes; a replacement model needs a new forecast.

I dissent from the assertion in P-1/P-2, D-049 and Nishinoya's reading that no model ranking like Φ can pass the calibration band. A strictly increasing transformation `sigmoid(a + b logit(p))`, b > 0, preserves ranking/AUC while changing calibration slope. This is standard sigmoid recalibration; any fitted correction must use training/validation data, never confirmation labels. [Scikit-learn calibration documentation](https://sklearn.org/stable/modules/calibration.html). Also, failure to establish positive late ΔAUC does not logically imply that tree interactions are required; lack of power, population shift or labels can explain it.

## RL translation

- **Observation:** queen state adds diagnostic information, but replay-truth opponent state and map-name regimes are not a deployable per-dragon observation. Use the legal observation/knowledge-age encoder for R5.
- **Action:** none at R1; no bot arm was run in this review.
- **Value/reward:** ranking improvement is reproduced; calibration and causal decision value are separate. The queen/longest/total outcome remains the value target.
- **Demonstration:** this audit reads frozen predictions, not teacher trajectories; it does not certify cloneability or a runtime gain.

Follow-up after D-051: [P-2-tanaka-repair-audit.md](P-2-tanaka-repair-audit.md); original forecasts and replication scope remain unchanged.
