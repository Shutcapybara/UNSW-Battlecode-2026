# LS-1 — Tanaka council audit

2026-10-04 17:56Z. **AMEND the proposed statistical interpretation; preserve the frozen D-055 verdict.** The screen has already dispatched (Daichi17:42Z). I have read no live outcomes. Sugawara's17:29 proposal predates dispatch; Nishinoya's17:52 endorsement does not. Any Chair amendment now must be explicitly timestamped as post-dispatch, before outcome access if that is still true, retain the original-rule verdict beside it, and explain its consequences. This review changes no job, roster, stopping rule or operational permission.

## Independent replication

From the previously frozen derived seed1 paired table in `tanaka-round4/k16-seed1-pairs.csv`: pool272pairs, **9 positive,2 negative,261 zero**, net+7;9opponent×map clusters contain discordant pairs. The sparse-outcome premise is supported by an exact4.04%discordance census, not merely a bound from aggregates. It does not establish the live discordance rate or prove that the switch fires on only4%of games. Equal scores can follow different actions; even all-zero score differences would not establish “never fired” or no behavioral difference.

A fully invented D-055 example with one+1difference and101ties has mean+0.00980392 and51-cluster1000/seed7/linear5–95 interval[0,0.02941176]; it **passes** the frozen rule. This verifies weak evidence for superiority in the sparse regime. D-055 is a noninferiority margin plus a positive point estimate, however, not a predeclared5%test of superiority. Its pass must not be described as proving improvement. Conversely, rejecting a zero point estimate is a promotion decision, not proof of harm.

One-sided exact binomial tails under *independent* discordant signs:

| Positive–negative | p |
|---|---:|
|4–0|0.062500|
|5–1|0.109375|
|6–1|0.062500|
|7–2|0.08984375|
|8–2|0.0546875|
|9–3|0.07299805|
|9–4|0.13342285|

All meet0.15. This corrects Nishinoya's17:52 arithmetic and his exclusion of7–2; Sugawara's listed qualifying examples are valid. His list is not a set of minimal thresholds (e.g.3–0already hasp=.125, though his separateK≥4rule blocks it). At fixedK=2,4,6,10,20 with theK≥4rule, single-look null pass probabilities under independent fair signs are exactly0,.0625,.109375,.0546875,.131588, respectively. No Monte Carlo is needed for these numbers; they are not the rate of the actual clustered two-look screen.

## Why the proposed pair test is not an automatic repair

**Seats share opponent×map clusters.** Counterexample: two independent clusters, each with two perfectly correlated seat differences, each cluster positive or negative with probability1/2. Both clusters positive occurs with probability1/4. That gives4positive pairs and0negative: naive pair signp=.0625, so it passes the proposed0.15rule. The null pass probability is25%, already above the claimed15%bound at one look. Adding49zero clusters yields LS-1's102pairs, passes its positive-mean/noninferiority conditions, and leaves this counterexample intact. The cluster-sign tail for the same two positive clusters is.25. Thus “≤.15by construction” needs independent pair signs, which the declared cluster design deliberately does not assume.

The sign test also counts half-point and full-point differences equally; it tests a direction-of-discordance probability, not the mean score estimand. Finally, permitting a second read after Hold is part of the procedure: a one-look bound is not a bound on passing at either read. A valid amendment must address dependence, effect magnitudes and the declared extension together.

**Concrete recommendation now:** retain and report D-055's frozen decision, print n+/n−/n0 and each cluster's summed difference, and enforce identical opponent submission IDs within each matched pair. Mixed-version pairs are missing, with a reason and original denominators shown. Print pair-sign p as descriptive with its independence assumption, not a guaranteed error bound. As a cluster-aware sensitivity, flip both seat differences together within each opponent×map cluster and use the summed score statistic; exact enumeration is cheap when only a few clusters have nonzero sums. This relies on independent, jointly sign-symmetric cluster differences under a sharp no-arm-effect null, not merely zero mean. It is not a new binding test for this ongoing run.

For a future screen, freeze the inferential unit and both looks together. One conservative option is valid cluster-level tests with at most.075size at each of two looks (union bound≤.15); power and sign symmetry must be stated before dispatch. Do not retrospectively retrofit that rule to select the favorable LS-1 result. Sugawara's300-simulation false-pass rates are peer evidence, not independently replicated here; the exact counterexamples above suffice for this recommendation.

## Forecast, expected effect, dissent, precedent and RL translation

No Tanaka LS-1 forecast was filed before dispatch. Current **post-dispatch, pre-outcome** subjective P(PASS under original D-055, including its declared extension)=**0.45**, expected mean+0.01score/pair, with wide uncertainty from three opponents and variant layouts. This is not a preregistered calibration entry. Do not substitute it for the existing0.35forecast of the separate local seeds2–3gate. I decline to score an undefined “amended” event until a complete rule is fixed.

Dissent: support honest sparse-data reporting and opponent-version pairing; do not endorse a pair-independent sign-test guarantee under clustered seats or call a late rule change pre-dispatch. Precedent is D-052's insistence on preserving seat/seed dependence within map×opponent clusters and P-2's distinction between missing and excluded data. Evidence is arithmetic and internal frozen data, not a literature claim.

RL translation: the queen safety rule changes action selection; score differences are a sparse terminal reward signal. A switch firing, an action changing and a match outcome changing are different observations. Pairing controls opponent policy/version; uncertainty must retain shared matchup dependence. A screen against three opponents estimates that roster, while the post-activation monitor measures the later ladder population.

Receipt and runnable probe: `tanaka-round7/audit.json`, `tools/tanaka/revision4_audit.py`. Nice10, bounded CPU; no live data, bot game, deployment or model fit. Live ops owns the reported accidental upload activation and restore; this review neither changes those controls nor repeats its already-filed repair request.
