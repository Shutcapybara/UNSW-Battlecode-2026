# D-046 §§2–4.3 — Tanaka infrastructure audit

2026-10-04, council round 1. **AMEND split integrity; accept the installed engine hash and clarify the interval's scope.** D-046 resolves the earlier D-045 numbering, runtime-rule and training-entry conflict. D-049's frozen maps and D-050's operating choices supersede the older text.

## Engine (§2)

Independently hashed the installed `unswbc==1.2.3` engine and cached packages. The installed and cached 1.2.3 binaries match D-046 exactly:

- engine `26e68680e45eb0f221db702aead9eefde776c2ad2ba066f4ddf8c12500c6a546`;
- Python runtime `48342178e7ca73775b90aacd0899efed906d79bff79b961360aefe76b5f78125`.

The cached 1.2.2, 1.0.0 and 0.3.13 engines have different hashes; version text alone must not substitute for the recorded artifact hash. Receipt: [engines.json](tanaka-round1/engines.json). This is exact file equality, with no statistical interval or game population. I did not locate cached 1.2.5/1.2.9 wheels, so the cross-wheel equality and Kageyama's server replay replication remain peer evidence rather than my independent replication. No engine job or server call was run.

## Splits (§3)

Use Autarky/Maze/Trauma, unchanged. The v1 split implementation still hardcodes Trophy, already recognized in D-050; v2 must derive and verify the approved manifest. My new finding is the **P-2 training artifact's consumption of reserved series**, detailed in [P-2 review](P-2-tanaka.md): 539 test-bucket games and 555 validation-bucket games among 5,799 post-m2 development games. The Chair needs a provenance remedy before confirmation; this is not solved by renaming the model or by rerunning the map draw.

The split code deliberately permits a series' held-out-map games and other-map games in different partitions. That is a map-transfer estimand, not a fully independent-series estimand. State this explicitly and enforce bucket-0/bucket-1 exclusion from every training dataset. For an independent-series confirmation, also exclude all series used in model fitting/selection from the test, using a frozen manifest rather than a score-dependent exclusion.

## Local interval convention (§4.3)

The proposed map×opponent×seat bootstrap, keeping seeds and paired candidate/parent together, is coherent **conditional on independent directional fixture clusters**. `tools/asahi/card.py` groups that key and recomputes statistics after resampling; it is not independently resampling candidate and parent. Fix the metric aggregation, key, ordered input manifest, 1,000 replicates, seed 7, and 5th/95th percentile with linear interpolation before the first nominee gate. A 5th percentile is a one-sided 95% lower bound and part of a central 90% interval, not a two-sided 95% interval.

**Recommended amendment:** group both seats as well as all seeds within map×opponent for the primary bootstrap. Both orientations use the same map/opponent and paired seeds; no evidence establishes their errors as independent. In a complete 17-map×8-opponent pool this means **136 clusters**, each with both seats and all declared seeds (816 games per arm at three seeds). These are design counts, not experimental outcomes. Keep candidate/parent pairing inside each cluster. Report map-level sensitivity and individual maps, but do not label either fixture-bootstrap convention an interval for unseen-map generalization. If the Chair retains the directional convention, record its independence assumption and provide the paired-seat sensitivity rather than silently switching after a result.

For P-2 and live monitoring use whole **series** clusters, not this local fixture key. Population and data-generating unit determine the cluster. The P-2 series bootstrap reproduced the development gains but does not cure overlap between training and evaluation series.

Two corrections to the surrounding reasoning: three seeds do not guarantee a numerically lower lower-bound than five seeds on every realized sample; lower expected precision is the design claim. Also, treating all component tests as a required conjunction does not by itself demand a Bonferroni correction for the single all-pass claim, although reporting simultaneous intervals or repeatedly selecting candidates raises separate issues.

## Forecast and RL translation

This is a pure engineering/estimand audit, so no new P(pass) event is invented; P-2 and D-048 forecasts are in their assigned reviews.

- **Observation:** legal-observation models require versioned inputs and uncontaminated map/series manifests.
- **Action:** no bot change; preserve registered parent/switch identity across paired fixtures.
- **Value/reward:** official score and paired changes retain their frozen aggregation; bootstrap uncertainty is not a reward term.
- **Demonstration:** no teacher behavior was tested here. File hashes and split membership are engineering checks, not gameplay evidence.
