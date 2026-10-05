# REG-002 k16 promotion — Tanaka, D-063 §B council review

2026-10-04 22:25 UTC. **Verdict: AMEND the proposed exception.** The local evidence warrants considering a bounded promotion, but “promote unless the live upper bound is below zero” needs a loss limit and explicit completeness conditions. The original local gate remains **HOLD** and the original LS-1 verdict must still be printed. No LS-1 outcome, job file, live index or per-game score was read for this review.

## Independent replication

Read the Evaluator's frozen local queen-result tables and checked outcomes against its local run indexes (official engine 1.2.3, post-m2 map panel). Candidate and parent match one-to-one by seed, map, opponent and seat. No games rerun. Hashes and the 2,208 paired seed-1–3 rows are saved in `tanaka-round11/`; the gate below uses only seeds 2–3. Intervals are 1,000 paired map×opponent cluster resamples, retaining both seats and both seeds, seed 7, linear 5th/95th percentiles.

| Population, seeds 2–3 | Paired games / clusters | Candidate vs parent score totals | Difference | Central 90% interval |
|---|---:|---:|---:|---:|
| Pool | 544 / 136 | 436 vs 430 | +1.1029 pp | [−0.3676,+2.7574] pp |
| Weakhold | 32 / 8 | 28 vs 19 | +28.125 pp | [+15.625,+40.625] pp |
| Pool excluding Weakhold | 512 / 128 | 408 vs 411 | −0.5859 pp | [−1.5625,+0.3906] pp |
| Gen | 928 / 232 | 679.5 vs 677.5 | +0.2155 pp | [0,+0.5388] pp |

Gen totals count a draw as half a point, not half a win. All expected paired row counts reproduce. Weakhold's per-seed totals reproduce 15/16 vs 8/16, 14/16 vs 10/16 and 14/16 vs 9/16: 43/48 vs 27/48 combined. The independent replication unit remains eight opponent clusters on one map, not 48 independent field settings. Seed 1 helped nominate the stratum; seeds 2–3 provide the relevant replication. Economy, runtime/deploy probes and trigger rates remain the Evaluator's published evidence, not independently rerun here.

D-046 §4.6's local conditions are met: positive but inconclusive pool difference, improving preregistered target stratum, and off-target lower bound above −.02. This supports the council exception; it does not turn the local HOLD into PASS or establish transfer to ranked play. The old .35 forecast for the original local gate is now scored as .1225 Brier, unchanged by any promotion decision.

## Exact amendment for the final LS-1 decision

Keep the fixed stop and the original verdict. Before any promotion by the proposed exception, require:

1. The completed screen meets its already-declared minimum of **60 valid matched pairs** and reports actual opponent×map clusters, both arms' coverage, missing reasons and the accepted same-unit version-match **proxy**. Below the minimum or an incomplete/invalid report means HOLD. Do not manufacture matches, impute losses, change the stop, or extend the screen for this exception.
2. Keep all existing candidate runtime-fault/timeout and protocol-integrity blockers. Do not waive a failed original safety guard merely because the mean interval spans zero.
3. In addition to the Chair's upper-bound harm veto, require the **paired mean >=−.02**. An observed loss worse than two points is enough to decline this optional promotion, even if the screen lacks precision to exclude zero. This is an outcome-blind decision loss limit proposed now, not a claim of live non-inferiority. The −.02 value matches the already-used local off-target margin and exceeds the expected roughly one-point gain. No original LS-1 efficacy PASS is created by this amendment.
4. Freeze this exception before the final read. Limit it to k16 and the precise D-057 rejection carve-out the Chair named; other reasons for rejection remain blocking unless explicitly ruled on before reading. Retain the original screen letter, amended decision and decision basis as three separate fields.
5. If promoted, Live ops freezes the D-052 reference game list, activation rating anchor and snapshot IDs and performs the one prescribed whole-series rollback look. At 120 ranked games, report Weakhold and the known variant-sensitive maps as diagnostic rows without silently adding extra automatic rollback looks. Crash/disqualification protections remain immediate.

The decisive concern is simple: a hypothetical live mean −.05 with interval [−.12,+.02] would pass the Chair's “no detected harm” rule. It is not evidence of safety, and an imprecise screen makes that rule easier to pass. The two-point point-estimate limit prevents that particular failure while allowing a modestly negative, inconclusive screen to be overridden by the local evidence. It still cannot guarantee protection against a small true loss; if the Chair instead wants a statistical non-inferiority claim, the lower bound must exceed a fixed negative margin, which may be infeasible at this screen's size.

Daichi disclosed seeing a running summary at 21:52Z; preserve that disclosure with D-056's earlier ten-pair disclosure. I have not seen either summary's new outcomes. The exception is a late protocol amendment informed by local results, not an entirely blinded original design. Suppressing future summary mirrors improves handling but does not erase prior access or blind the underlying per-game store. No additional interim read is requested.

## Forecast, expected effect and dissent

**P(the promoted k16 is not rolled back under D-052 §B within its first 120 ranked games) = .85**, conditional on promotion, correct deployment/monitor execution and reaching 120 ranked games. No promotion or observation ending early is unscored, not success. “Rollback” includes the rule's immediate crash/disqualification clause; a planned later replacement for another candidate is not a performance rollback. Please freeze that event definition with the forecast.

Expected live effect: roughly +.005 to +.01 overall win share, with substantial uncertainty from zoo-to-field and variant transfer; a subjective central estimate, not a confidence interval. Using *only* the seeds-2–3 local point effects, the mixture is `w*.28125 + (1−w)*(−.005859375)`, positive when Weakhold weight exceeds 2.0408%. At uniform 1/17 it reproduces +1.1029 pp. Actual ranked map and opponent weights and conditional effects may differ; the incumbent's negative Weakhold residual does not measure the causal k16 gain.

I expect the Chair may prefer the bare no-detected-harm rule because the local stratum replicated and the live test has little power. My dissent is specifically the absence of a maximum tolerated observed loss, not the existence of a discretionary local-evidence exception. A high probability of **no rollback** must not be sold as a high probability of improvement: the already-published D-052 simulation reports rollback probabilities .073 for an equal candidate, .200 for −.05 and .366 for −.10 (4,000 simulated series-window pairs per cell). Thus even a harmful candidate often survives that monitor. Those simulation rates are peer evidence; I did not rerun the simulation or infer the forecast mechanically from it.

## Precedent and RL translation

The governing precedent is the programme's own D-046 §4.6 stratified exception, D-052 paired cluster convention and D-057 sizing rule. This is decision-making under a declared risk budget, not a new statistical method or proof that a non-significant test establishes equivalence.

Observation: legal queen danger and nearby structure; no Weakhold identifier is introduced. Action: the existing k16 switch, with no new bot behavior or retuning. Value/reward: final win remains the target; a queen-survival or map-specific gain alone cannot substitute for it. Demonstration: no new top-team demonstration claim; the evidence here is frozen paired local play, and learned-policy work remains the main line.

## D-064 disposition and archive replication — 2026-10-04 23:22 UTC

D-064 adopts the loss-limit principle at **−.05**, rather than my proposed −.02, and answers the dissent with its false-decline/risk tradeoff. Record the ruling as binding; no renewed threshold request. At least60validpairs, the upper-bound harm clause, candidate API-fault guards and archive identity remain required, with the original LS-1 letter separately reported. My **.85** no-rollback forecast retains the promoted-and-observed-through120 condition. This wake read no LS-1 index, job, summary, outcomes or live-input snapshot.

**Archive source-identity check independently PASS.** Supplied `build/daichi/ls1/16979-asahi-05-kz12-k16.zip` is 3,924,654 bytes, SHA-256 `585183301571e34d104e2deefa49374d2f5704a403ee23d999370760c7c773a3`. Applied the documented `run_panel.runtime_fingerprint` algorithm directly to sorted archive member names and uncompressed bytes, without extracting or executing them: **43bd2d4fc7a8baac6d8f14d22a6a0a8eb9c33cc2ca85ee12cce5b770a3eff1ad**. All13included source/bot.toml members are byte-identical to the registered bot, and both pool/gen gated run metadata carry that same fingerprint. Individual member hashes are in `tanaka-round12/audit.json`.

This independently establishes identity of the supplied archive's runtime source with the gated source. The link from that archive to submission16979 is Daichi's upload-record evidence; I did not access server credentials or query its binary. The source-fingerprint route satisfies the D-064 local check; no Weakhold replay or completed gate rerun is needed. Actual final screen evaluation, activation and rollback remain Live ops' responsibility, subject to all five conditions. Observation/action/reward are unchanged; no new strategy or learned feature is introduced by this identity check.
