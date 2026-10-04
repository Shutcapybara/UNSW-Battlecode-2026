# D-048 §8 — Tanaka rollback review

2026-10-04, round 1. Verdict: **AMEND in favor of a frozen incumbent-relative reference**, with whole-series windows, explicit missing-data handling and one declared statistical look. The absolute residual trigger confuses an incumbent rating bias with damage from the new candidate. The replacement comparison costs precision and remains a before/after drift test, not a randomized estimate of the candidate's effect.

## Replication

Audit source: `tools/daichi/live_monitor.py`, reconstruction cutoff **2026-10-04T10:45:39.291111Z**, ranked submission 14585 only. All these incumbent games start after its 2 Oct 04:22Z activation, hence post-m2. Statistic = official index score minus the Elo expectation from the last available pre-start ladder snapshot. An independently written whole-series bootstrap reproduces the monitor's endpoints (1,000 replicates, Python random seed 7; ordered bootstrap indices 50 and 949):

| Population at the cutoff | Games / series | Mean residual | 5th–95th percentile |
|---|---:|---:|---|
| First 40 ranked | 40 / 10 | −0.05206 | [−0.20425, +0.07079] |
| Last 40 ranked | 40 / 8 | −0.09296 | [−0.18362, −0.00230] |

**The full 417-game history is not replicated.** The now-backfilled index contains 596 qualifying games / 122 series before that same start-time cutoff; it gives -0.02943 with [−0.06302, +0.00284]. This is a different census, not a contradiction of the original monitor. A start-time cutoff does not freeze collection membership. Daichi should retain the original game-ID/residual manifest and ladder references for every monitor decision. The two 40-game endpoint summaries match, but the old manifest is absent, so identical game membership cannot independently be certified.

Evidence: [audit and design calculation](tanaka-round1/rollback-audit.json); audit program `tools/tanaka/rollback_audit.py`. The derived evaluation rows are frozen in `tanaka-round1/rollback-residuals.json`; no replay payload was copied or rerun. The eight-series window is not a future-power dataset representative of every candidate.

## Power of the two forms

The last-40 window's cluster-robust standard error is **0.05817**, treating its **8 series / 40 games** as the independent units. Two independent windows of that size and variance give SE(diff) ≈ **0.08227**. The following is an **analytic normal plug-in approximation**, not a simulation success count, measured operating characteristic or confidence interval. It assumes equal variance, independent windows, stable opponent/map mix and no repeated looks. With only eight series the approximation is uncertain.

Use each proposed conjunction: point < −0.08 AND one-sided 95% upper bound < 0. Under the normal approximation these are absolute mean < −0.09569 and difference < −0.13532, respectively.

| Assumed incumbent mean residual | True candidate change | Absolute-trigger probability | Relative-trigger probability |
|---:|---:|---:|---:|
| 0 | 0 | 5.0% | 5.0% |
| 0 | −0.08 | 39.4% | 25.1% |
| 0 | −0.15 | 82.5% | 57.1% |
| −0.09296 | 0 | 48.1% | 5.0% |
| −0.09296 | −0.08 | 90.8% | 25.1% |
| −0.09296 | −0.20 | >99.9% | 78.4% |

Thus the apparent power of the absolute test at today's negative residual includes a high chance of rolling back an equally strong candidate. The relative rule has only about **25%** power for an eight-point degradation at this plug-in variance; roughly **20.5 points** are needed for 80% power. Because the rule also requires the point estimate to be strictly below −0.08, its limiting power at a true change of exactly −0.08 is only 50% under symmetric estimation noise. No sample-size increase alone can deliver 80% power at that boundary; an 80% target must name a larger degradation or a different decision threshold prospectively. These arithmetic design values have no sampling denominator; their empirical variance input is the 40-game/eight-series window above.

## Exact changes recommended before activation

1. Freeze the incumbent reference at activation, including submission fingerprint, ordered game IDs, whole series, maps/map_era, scores, Elo snapshots, expectations and activation-window exclusions. Use the last **at least 40 games ending at a whole-series boundary**; take all games in the boundary series. Use the new submission's first at least 40 games with the same boundary rule. State both actual denominators. Never split a series between the baseline and candidate; a mixed-submission series is excluded and reported.
2. Compute **candidate mean residual minus frozen incumbent mean residual**. Independently resample whole series in each window, preserving each cluster's games and weighting the statistic by games, then difference the means in each replicate. Do not subtract separately computed interval endpoints or bootstrap candidate games against a fixed, variance-free old mean. Use 1,000 replicates, seed 7, and a recorded quantile convention.
3. Retain the proposed point threshold −0.08 and 95th-percentile upper bound < 0, and the immediate crash/disqualification rule. Run the statistical trigger **once at that first completed window**. Keep later rolling residuals as drift alerts, not repeated automatic 5% tests; a later automatic monitoring rule needs a prespecified sequential error budget or confidence-sequence design.
4. Require the complete scheduled series and attribution, rather than selecting the first 40 games that happen to have arrived and have usable expectations. Missing games, snapshots or fault information mean an incomplete comparison. No unknown outcome should become a draw. An unexplained human activation or mixed activation window remains a pause.
5. Report map, opponent, seat, rating and temporal mix in both windows. A negative difference can come from field drift or mismatch even after Elo adjustment; call it an operational rollback signal, not causal proof. The matched, concurrent unranked promotion screen remains the cleaner comparison. Do not retrospectively select a friendlier reference or add games after seeing a borderline result.

The new rule's reference is appropriate, but a non-trigger is weak evidence of safety. Preserve ongoing fault monitoring and the frozen promotion evidence; do not call 40 games a non-inferiority certificate.

## Monitor implementation check

A bounded synthetic probe of `rating_at` with a game one second **before the earliest snapshot** returns that future snapshot's rating (1500), instead of missing. The cause is `if i < 0: i = 0`. Change this to missing and test it before the monitor is used for an automatic decision. I did not measure its incidence in the reproduced 40-game windows and do not claim it changed their residuals. Also, `own_games` maps an empty winner to 0.5; require an explicit draw verdict and list unknown outcomes as missing. These are requests to Live ops, not edits to its tree.

## Prediction, dissent and known precedent

**P(pass)=0.80**, subjective, for the amended implementation passing a preregistered A/A false-rollback calibration check whose nominal target and tolerance the Chair/Live ops freeze before running it; this forecast is not scored until that event is specified. Expected effect: no direct change in game score; fewer erroneous rollbacks when the incumbent has a persistent negative residual, with lower sensitivity to modest regressions. The model calculation above is the quantified trade-off, not a live effect estimate.

Dissent: I support changing the reference but reject calling the proposed first-40/last-40 comparison adequately powered for an eight-point loss. Do not hide the increased variance or treat a rolling upper-bound crossing as the same one-shot rule. Standard precedent is a two-sample difference with cluster bootstrap; repeated looks require a separate sequential monitoring design.

## RL translation

- **Observation:** model evaluation needs timestamped map/opponent/seat, submission attribution, series IDs and pre-start ratings; these are evaluation metadata, not policy inputs.
- **Action:** restore the previously tested submission under the Chair's rule; no bot action or activation was made here.
- **Value/reward:** official score remains the outcome; Elo residual is an operational normalization, not a new training reward.
- **Demonstration:** no teacher behavior or replay mechanism is inferred from these monitoring statistics.

Follow-up after D-051: [D-048-tanaka-followup.md](D-048-tanaka-followup.md); original forecasts and replication scope remain unchanged.
