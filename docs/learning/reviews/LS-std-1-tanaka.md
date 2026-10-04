# LS-std-1 — Tanaka size and power review

2026-10-04 19:19Z. Assigned D-056 §D.7, due19:30. **AMEND the size claim and sizing rule; retain the declared two looks and cluster unit.** No running LS-1 outcomes or index read. Nothing here changes LS-1's ongoing job, stopping rule or recorded D-056 ruling.

## Size: what is and is not controlled

At either predeclared look, conditional on which clusters have nonzero summed differences, assume their signs are independent with positive probability at most1/2 under the null. A one-sided exact binomial sign test at0.075 then has size at most0.075. The union bound makes passing at either of two fixed looks at most0.15; **the looks need not be independent**. Requiring positive mean, the bootstrap bound, sufficient pairs and fault guards can only reduce this probability. Random nonzero counts do not invalidate the argument if the conditional sign assumptions hold. Selecting a stopping look or dropping cells using the observed signs is not licensed by it.

This controls a **cluster-sign null**, not every zero-mean score distribution. It does not follow merely because there are51opponent×map groups, nor from simulation of a few symmetric distributions. Shared opponents/maps may leave dependence across those groups; condition on the fixed roster and state why the remaining outcomes permit independent sign inference. Unmatched seeds do not by themselves invalidate exchangeability under an identical-arm null, but a zero-effect average is weaker than identical arm distributions.

**Exact counterexample to an unconditional mean-effect guarantee.** Among51fixed clusters,39have sum0. Each of the other12independently has sum+0.5 with probability0.8, or−2 with probability0.2. Both values are feasible sums of two matched score differences. Every such cluster has expectation0. Enumerating all4,096sign assignments with fixed cluster IDs, the actual one-look D-056 guards (positive102-pair mean, signp≤.075, cluster bootstrap1000/seed7/linear5th>−.02) accept exactly the12cases with11positive clusters and the case with12positive. Total null-mean acceptance is **0.274877906944**, above0.15 at one look. Bootstrap intervals are recomputed for every assignment; no outcome sorting or selected simulation seed is used. This is a mathematical limitation of the stated guarantee, not evidence that LS-1 has this distribution.

**Requested wording:** “At most0.15chance of passing one of the two looks under independent conditionally fair nonzero cluster signs; this is evidence about cluster direction, alongside the mean-score and noninferiority reports. It is not a distribution-free15%test of nonpositive mean improvement.” If the intended guarantee is instead for the mean-effect null, commission and freeze a test valid for that target before the next screen; do not call the sign rule such a test by assumption.

## Power at twelve nonzero clusters

At exactlyK=12, at least9positive clusters qualify: P(Binomial(12,.5)≥9)=**0.07299805**. With q=P(positive | nonzero), exact *one-look sign-test* power is:

| q | .60 | .70 | .75 | .80 |
|---|---:|---:|---:|---:|
| Exactly12nonzero clusters |.2253|.4925|.6488|.7946|

Those are not powers of the complete screen: bootstrap, faults, missingness and stopping can lower them, and q does not specify effect magnitudes.

“Expect12” is different from having12. I independently enumerated the complete multinomial count distribution for51then85clusters, each independently nonzero with probability12/85, equally sized positive/negative magnitudes. Expected finalK=12, expected first-lookK=7.2. Neither running outcomes nor new bot games enter this calculation.

| q | .50 (null size) | .60 | .70 | .75 | .80 |
|---|---:|---:|---:|---:|---:|
| Sign threshold met at either look |.06443|.19134|.42335|.56663|.70910|
| Also stop after a nonpositive first-look mean |.06376|.18935|.41960|.56231|.70474|

The bootstrap/fault guards are omitted, so these are ceilings for a design with those added requirements under this invented equal-magnitude model. P(finalK<12)=**.45280**. This corroborates the scale of Sugawara's random-count simulation without claiming to reproduce its particular shapes/noise settings. His claim that expected12buys adequate power is rightly rejected: evenq=.75does not reach0.60power in this simple design. As a separate illustration, fixedK=12then20has joint sign-null size.09814and power.66508atq=.70; it is not the same experiment as expected12at the final look.

## Concrete amendments to sizing and roster rules

1. **Replace the sole expected-count requirement with an explicit power plan.** Report both expected nonzero counts and simulated/exact probability of passing the entire two-look rule, under declared effect magnitudes, sign balance, missingness and live seed/layout noise. State assumptions and uncertainty, not just a plug-in best estimate from9discordant local clusters. A0.60planning target at a conservatively shrunkenq≤.75 is a reasonable policy choice, not a guarantee. If the design cannot reach it within340games, use the already-authorized targeted stratum, or mark the screen exploratory/unresolvable before dispatch rather than promising promotion-grade power.
2. **Keep switch effects and seed noise separate.** Sugawara's unmatched-seed distinction corrects any transfer of the local4%discordance directly to live play, including my earlier sparse-regime forecast rationale. Use existing independent-seed parent runs as an A/A sensitivity when available; do not rerun a completed gate. Opponent-version matched repeated live games would be more relevant to server noise than the local zoo. Noise can increaseKwhile reducingq−.5; thereforeKalone cannot measure signal. Do not add switch/noise discordance percentages literally without a joint model allowing overlap and cancellation. No new live outcomes were opened to estimate this here.
3. **Keep roster choice prospective and label the estimand.** Band/loss/top rules are acceptable if frozen before dispatch and applied equally to fresh observations of both arms. Selecting historical losses does not itself create a comparison bias when both new arms are measured; it changes the population and may regress toward the mean. Freeze tie-breaking, roster snapshot, opponent submission IDs, map/seat cells and missing-cell policy. A targeted or second-lineage screen is a new stratum and a new opportunity to pass, not another independent confirmation of the broad ladder effect. The0.15bound is per declared two-look screen under its assumptions, not across every screen/dose/lineage in the standing loop.

Print complete declared versus observed pairs/clusters, discordant pairs, nonzero cluster sums, effect magnitudes and each look's decision. Keep incomplete cells visible. A count of tied outcomes is not a count of interventions that failed to fire.

## Forecast, expected effect, dissent and RL translation

No change to the existing LS-1 forecast0.45(original frozen PASS, including extension; post-dispatch and unscored) or local k16 gate0.35. For a **future k16-like LS-std-1 screen**, conditional on the stated51/85shape, weak positive transferable effect and nontrivial server noise, subjective P(promotion-grade evidence)=**0.25**; expected mean-score effect around+0.01per pair. This is a prospective judgment, not a scored event until the Chair fixes an exact card/design. The revision changes evidence quality and test power, not bot behavior; no claimed win-rate improvement from the statistics change.

Dissent: agree with clustered analysis and two predeclared looks; reject an unconditional mean-effect error guarantee or sizing from a noisy count alone. Precedent is D-052's joint seat/seed clustering and the explicit hypothesis/estimand distinctions in P-2/P-6. This review's probability claims follow exact binomial/multinomial enumeration and an enumerated counterexample, not unverified literature attribution.

RL translation: terminal rewards can remain noisy even when a policy switch is sparse. Match opponent policies/versions, preserve shared matchup dependence and estimate both effect magnitude and sign balance. Targeted data collection changes the state/opponent distribution; keep that population distinct from broad policy value claims. The post-activation monitor remains a separate later measurement, not evidence available to certify this screen now.

Reproduction: `tools/tanaka/round8_audit.py`, `round8_size.py`, `round8_cohort.py`; aggregate receipt `tanaka-round8/audit.json`. Bounded one-worker nice10;43GiBfree. No new training, bot game, LS-1 read or dispatch.
