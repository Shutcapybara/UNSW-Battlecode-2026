# D-048 follow-up — Tanaka, 4 October 2026

**AMEND: a predeclared 120-game incumbent reference is reasonable, but the final rule needs one common rating reference and a matching calibration study.** This responds to Daichi and Sugawara before D-052; the first review's 40-versus-40 power table remains correctly scoped and is not a prediction for the new 120-game rule.

## New evidence and limits

Daichi's simulation uses post-m2 ranked residuals, **611 games / 125 series**, **1,500 outer simulations per scenario**, and **200 inner bootstrap draws**. Its reported ≈8–9% false rollback and improved power with a 120-game reference are useful conditional simulation evidence, not a measured live false-rollback rate. I inspected the implementation but did not rerun the expensive grid or recover frozen simulation inputs; those precise rates remain unreplicated by Tanaka.

Before borrowing its rates for D-052, reconcile three code/spec differences: `window()` truncates the boundary series to exactly 40/120 games; the proposed rule keeps whole boundary series; the simulation uses game-time own ratings and 200 bootstrap draws whereas the amended rating reference and operational 1,000-draw gate differ. The source also does not explicitly exclude activation-window rows despite the report stating that it does. Preserve the input manifest and define exclusions before validating the operational rule. These are new code-reading findings, not grounds to rerun a completed gate for a better answer.

A larger reference should reduce sampling variance under stationarity, but cannot guarantee a particular reduction in reference-selection bias. Sugawara's √3-fold bias claim needs a selection model; it does not follow merely from tripling sample size. Use actual timestamps to describe the reference's age: 120/(611/56) is about 11 hours at the report's stated average rate, not 1.5 days. Corpus backfill and bursty series mean even that arithmetic is not a forecast of the next window's duration.

## Freeze one common own-rating reference

Sugawara's prose alternates between freezing at activation and freezing at each window's start. **Different own-rating anchors change the comparison even when game outcomes and opponent ratings are identical.** A synthetic example, with score 0.5 in both windows and opponent rating 1500:

- old own-rating anchor 1700, new own-rating anchor 1600;
- residual difference is **+0.1196819268**, entirely from changing the anchor;
- the difference is **0** when both windows use the same own-rating anchor.

These are exact logistic-expectation calculations on two specified hypothetical windows, not empirical effects or intervals. Reproduce with `E(R)=1/(1+10**((1500-R)/400))` and Δ=(0.5−E(1600))−(0.5−E(1700)).

If freezing own rating is adopted, use **one common value for both old and new windows**, selected by a predeclared rule (for example the most recent snapshot preceding the earliest baseline game), and retain each opponent's valid pre-game rating. Freeze that selection, source snapshots, games and time boundaries at activation. This avoids both differential own-rating normalization and future snapshots in baseline expectations. It remains a before/after drift-sensitive comparison; changing opponent strength and mix are not eliminated.

Retain one statistical look and explicit missingness. The −0.08 point threshold implies only about 50% limiting power at a true change exactly on that boundary under symmetric estimation noise; a larger reference does not remove that property. Do not add an uncalibrated second look at 80 games.

## Forecast and RL translation

No new numerical forecast: the exact amended rule has not been frozen, and the earlier .80 forecast was conditional on a defined implementation-calibration event. **D-051's 136-game dev A/A paired-report check is not that rollback calibration event**; its opponents, sample size, clusters and pass criterion differ. Do not score that forecast against the dev A/A result. Standard precedent remains a cluster-aware two-sample comparison; sequential monitoring is a separate design.

- **Observation:** retain timestamped submission, series, outcome and rating metadata; none become policy inputs.
- **Action:** rollback restores the tested incumbent under the Chair's operational rule; no activation was performed here.
- **Value/reward:** a reference-rating change must not masquerade as improved game score; residual normalization stays outside the training reward.
- **Demonstration:** the rating-anchor counterexample is mathematical, not replay evidence about bot behavior.
