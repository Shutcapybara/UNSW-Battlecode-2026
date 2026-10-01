# Himeji unit 5 — ranked cohorts, gen winner correction and peer readings

Published 2026-10-01 16:40 UTC. **Rome gen corrects to 74.43%; Cutlery has genuine ranked queen-survival evidence after 13:00.**
The larger Cutlery claim still mixed ranked/unranked games and carried early endings into r490.

## Standing direction from the user

After the rules change, give **ranked versus unranked** greater weight. Use recent ranked games for deployed-strength
claims and report unranked games separately as a live-testing cohort. Teams are returning to live testing: do not assume
pre-change unranked behaviour still identifies a decoy, or treat an unranked version as the deployed ranked bot. Unranked
replays remain useful mechanism evidence, with their version/time/population labels. This direction persists across units.

Next reference revision will split these cohorts. Preserve Himeji's historical 400-game freeze, including its old
eligibility filter, as historical/provisional rather than silently relabelling it ranked-only. It cannot be promoted to
a current deployed-strength benchmark as-is. Live team-7 gaps remain missing; local panels remain a third population.

## 1. Rome gen: all 1,392 official outcomes checked

| Source | W / L / D | Expected-score share |
|---|---:|---:|
| Old inferred longest/total rule, matching Rome report | 1,041 / 351 / 0 | 74.7845% |
| **Official replay header** | **1,036 / 356 / 0** | **74.4253%** |

Seven winners differ, six old wins become losses and one loss becomes a win: net −5/1,392 = **−0.3592pp**.
All 1,392 records are terminated and all runner winners agree with their replay headers. The completed pool audit from
unit 4 was 396/83/1 = **82.6042%**, also five net old-rule wins too high. Re-extract winner-dependent features before
Rome's L10 candidate comparison; keep the historical scorecards labelled superseded. We did not change Rome's files.

Rome's gen cohort has 29 map labels and 1,392 games, unlike Carthage/Kyoto's 744 games over 31 maps; these headline shares
are not matched bot-strength comparisons. Full per-map official W/L/D and round-limit counts are in the audit JSON.
The new gen queen report, **6/1,392**, remains the joint reached-and-alive event, not conditional r490 survival; report
actual reach count and early wins/losses. The 72,334 successful sprint checks and 38 queen-verdict checks support the
instrument, but do not establish a treatment gain. Rome's L10 CPU max 10.82M is a feasibility result, not a gate result.

Query: `tools/himeji/audit_panel_winners.py --repo <wt-himeji> --panel <gen fingerprint directory>
--out <private-output> --expected-games 1392 --jobs 2` (join on one line). Normal runner index SHA256:
`eb26af65ff27e47b9096a8140a697e606b5cbb329a88938702256129e6f8925b`. Read-only, checkpointed per game; no shared decoder/cache writes.

## 2. Cutlery: separate ranked evidence from live testing and censoring

Nara's current `build/nara/queen_cutlery.jsonl` has 7,956 side rows, of which **146** are Cutlery. Its published
0/62→23/84 narrative is not the exact current artifact at a 13:00Z cutoff. The stored positive-length counts are
**1/62 before** and **22/84 after**, and half the after positives are not round-limit games. `queen_probe.py` still uses
`min(checkpoint,last_snapshot)`, so a surviving queen in an early elimination win becomes a false r490 observation.

We joined the ranked flag and series ID from the corpus index, then independently checked all 146 official result
headers. All round-limit labels agree; **three stored winners are wrong**. Here is the useful comparison:

| Cohort | Games | Round-limit games | Queen positive at r490 among those RL games | Queen alive at RL end |
|---|---:|---:|---:|---:|
| Ranked, before 13:00Z | 62 | 31 | **0/31** | **0/31** |
| Ranked, from 13:00Z | 64 | 31 | **9/31** | **9/31** |
| Unranked, from 13:00Z | 20 | 9 | **2/9** | **2/9** |

The ranked before/after groups each span 14 series, with changing maps/opponents. This is **credible evidence of a
ranked behavioural change worth dissecting**, but not proof of an exact deployment timestamp or a causal 29pp policy
effect. There is no matched control or stable population target here. We did not verify arbitrary early games that
might reach r490 then end by elimination; these are explicitly **RL-conditioned**, not all-reached-r490 rates.

Nara's 23 positive rows across the mixed cohort contain 12 early endings and 11 RL survivors. Official wins among those
23 are **22/23**, versus stored 20/23. Ranked post-13:00 RL queen survivors win **8/9**. These outcome-conditioned
comparisons do not measure the value of preserving a queen; good positions can both preserve queens and win. Keep the
moving/large-queen examples as mechanism evidence, while distinguishing pearl consumption from deliberate ally feeding
and survival-conditioned trajectories from typical play. N6 queen-as-crown is a reasonable test proposal, not a measured
causal winner. Prior Himeji 1/5 was a different frozen subset; it does not refute this larger later cohort.

Artifact SHA256, compact source rows, ranked joins and official-header rows are frozen under `tools/himeji/unit5_audit/`.
`audit_cutlery_headers.py` reproduces the header comparison from those frozen source rows. The source query remains
Nara's; Himeji did not alter it. Request its actual-checkpoint fix and corrected labels, not a replacement of its section.

## 3. New tester readings

**Carthage 08:** agree reject. Pool win −0.009 [−0.037,+0.021], gen +0.022 [−0.003,+0.048] do not establish positive
overall gain; gen economy −0.031 [−0.050,−0.010] also fails a proposed −0.03 lower-bound guard. Gen conditional queen
survival 33.3% and queen verdicts 46–0 are useful mechanism signals, not 46 added wins. Publish arm-specific reach
counts and an **08−06** paired contrast for the incremental premium; comparison versus 00 alone evaluates the stack.
Its 4.7% pool survival is not evidence that the 50% aspiration is an observed field target. Quoted intervals are 90%
central (5th–95th percentile), as in Carthage's report. Preserve the existing gate; director owns revisions.

**Kyoto baseline:** reported 0.836 pool win still uses the old decoder. A fixed ±0.4pp bias bound and an assumption that
paired bias cancels are unsupported: the same-type Rome pool corrected by **−1.0417pp**, and treatment can change the
queen-decided cases. This is a warning, not a Kyoto-specific correction; rescore its exact games with official outcomes.
The stated cross-host difference 0.836−0.826 is about 0.010, so 'less than 0.01' is not established from rounded figures.
Keep normalized means and medians distinct: lane.py's `econ|n~` averages checkpoint medians, whereas `|n` is a mean;
the displayed p50/100/150/250 values should identify their aggregation and normalizer before cross-lane comparison.

**Kyoto queen report:** 1/217 pool and 3/152 gen are **end-of-RL** survival, not the same measure as Carthage's
reach-r490 2/219. Its 10%/15% 'any-game alive@490' carries early terminal snapshots; label those as
queen-alive-at-min(490,end), or replace with actual checkpoint fields and missing early endpoints. Acknowledge the
report already flags the inflation, but that does not make the r490 label valid. 4/4 wins given a surviving queen
is consistent with the tiebreak and too selected/small for policy value. Pool wall-first versus gen enemy-head-on death
counts identify different failure profiles; they do not prove which intervention must work.

**Kyoto D-033 cost:** seed-1 pool Δwin +0.034 [+0.009,+0.062], Δecon +0.026 [−0.009,+0.060] are a pool ablation under
old inferred wins. Recompute paired official wins; do not treat this as an out-of-pool result or restore prohibited
map-identity terms. The cap-lift remains pending; no outcome is inferred from CPU feasibility or a placeholder.

## 4. Win-potential proposal: source audit before promotion to a target

Antioch's Φ is a useful proposal, but the checked-in `value_target.py` loads **s.ended** without filtering it; S-1 carries
terminal states forward (`tools/s1/build.py`, ended = checkpoint > last played round). Leave-one-map-out alone does not
remove already-resolved outcomes. Request **active-only checkpoint** AUC/calibration, ended fractions, and a separate
all-games descriptive score. We have not rerun the post-store fit and do not claim a numerical AUC correction.

The published reproduction command fits six pooled shares and writes `phi_post.json`; shipped `phi_post_v1.json` has
five features and two regimes. The finding says 2,433 games; export metadata says 2,739. Supply the exact producing
query/script, data fingerprint, filters and fold memberships for the reported regime metrics before adoption. Regime
metadata lists map names; a deployment/scoring router for unseen maps must use predeclared structural features, not map
identity or a game's eventual end reason. No shared target or coefficients were modified by Himeji.

Predicting which existing positions win does not establish that increasing Φ improves treatment wins. H-V1's arm-level
validation is therefore necessary; freeze it before testing new arms, report both panels and uncertainty. Top-ten mean
Φ is a model score, not a field percentile: add its ECDF position, cohort counts, confidence intervals and ranked scope
before presenting it as the requested percentile anchor. Keep terminal win as the policy outcome.

For the shaping claim, finite-episode discounted terms telescope to
`sum_t gamma^t (gamma*Phi(s[t+1]) - Phi(s[t])) = -Phi(s[0]) + gamma^T*Phi(s[T])`.
Record terminal-potential and horizon handling; the endpoint must be handled consistently before claiming unconditional
policy invariance. This is a boundary-condition check, not a request for Himeji to implement or train a bot.

## Cursors, ownership and next work

Read protocol, five statuses, boards and targets. Source cursor: main cb2e920c7; Antioch 48c7906cf; Carthage f9b86bf5b;
Nara f7ad05a41; Kyoto 7c835936c; Rome local status complete baseline and L10 claimed. Peer clock labels differ, so source
commits and content define the cursor. No own query was running at start; at most three read workers, all finished.

Corpus index **79,343 unique**, latest **2026-10-01T16:31:38.148Z**, SHA256 `8825b60273a3e2060520d97c3a8ada10030743a702870b8618ef6ad4e4bf723e`;
**0 post-era team-7**, ladder `20261001T062107Z.json`. Antioch reports 2,862 post-store games but its Mac sync was blocked
by its permission review; Himeji remains read-only and will not work around that by writing the shared store. Main and
all peer files were untouched. Current live anchors remain provisional; next revision will explicitly split ranked and
unranked cohorts per the user's direction. Preserve historical benchmark verdicts.

Next: read 09/L10/cap-lift results, pursue a ranked-only temporal/structural Cutlery anatomy if no new tester result
needs a reading, and review Φ's active-only/provenance corrections when posted. Rome pool/gen winner audits and the
three-seed split-exposure replication are complete; do not repeat them without changed inputs.
