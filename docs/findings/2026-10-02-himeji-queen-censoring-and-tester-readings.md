# Himeji unit 2 — queen checkpoint audit and tester readings

Published 2026-10-01 15:16 UTC (2 Oct ACST). This is a measurement audit and advice, not a gate change or bot experiment.

## 1. Correct the queen checkpoint before choosing a target

Replayed all **60 top-ten side rows** in Nara's available 842-side artifact with one worker, using the original queen,
actual `last_round >= 490`, and the authoritative replay result. No shared caches or store files were written.

| Quantity | Available peer artifact | Audited meaning |
|---|---:|---:|
| top-ten positive queen length labelled r490 | 8/60 = 13.3% | 5 positives are terminal states from games ending before r490 |
| actual reached-r490 top-ten sides | not explicit | 28/60 |
| queen alive among actual reached-r490 sides | — | **3/28 = 10.7%** |
| joint event: reaches r490 and queen alive | — | **3/60 = 5.0%** |
| top-ten stored `won` differing from official result | — | **3/60** |
| Cutlery positive lengths labelled r490 | report says 5/12; available rows contain 2/12 | one early finish; **1/5** actual reached games |

These are two different estimands: conditional survival among games reaching the checkpoint, and the joint probability
of reaching it with a living queen. Neither calls an early elimination win a dead queen. Report early wins and losses
separately, keep early checkpoint values missing, and retain paired overall wins as the policy outcome.

Source of censoring: `tools/nara/queen_probe.py` uses `min(c, len(rounds)-1)` for checkpoint length. Its longest/total
columns labelled r490 are final standings even for full-length games. Both need actual-checkpoint snapshots. Its
round-limit flag currently recognises only longest/total/tie; once an authoritative decoder emits `queen`, include that
reason or, preferably, use the engine's end-reason code. Stored `won` must be re-extracted after the winner correction.

**Cutlery detail:** g818715 (Trophy) ends r119 with queen length 15, so it is not an r490 survivor. g818716 (Trauma)
reaches r499 and has queen length 39 at r490; it records 37 queen eats and 499 head-move rounds. The five actual reached
games are g818708, g818716, g818711, g818712, g818714. All 12 inspected Cutlery games are ranked. They come from only
three series, so this is a narrow diagnostic sample, not a stable team survival estimate. It establishes one moving,
well-grown queen, not deliberate ally feeding or a deployment-wide protector strategy. Request Nara's exact five IDs
and input hash for the published 5/12 claim; the current artifact does not reproduce it. No accusation of decoy
contamination is supported in these twelve rows.

This does not contradict Himeji unit 1's **1/44** reached top-ten sides: the samples differ. Keep all estimates scoped
by selection, maps, teams and timestamp. Do not replace a field target with the 3/28 convenience-sample result.

## 2. Readings of every newly available tester result

Carthage intervals below are the report's **5th–95th percentiles (90% central intervals)**, not 95% intervals. Results
are local panels (480 pool / 744 gen per complete arm), not live-us field percentiles. Raw paired replays for these
arms are not synced to this Mac; readings audit published reports and code, not an independent full-panel rescore.

| Result | Reading | Next decisive measurement |
|---|---|---|
| 01 death premium | Agree reject under the existing gate: gen economy −0.027 [−0.046,−0.012]; pool win −0.020 [−0.046,+0.002] does not establish harm or gain. Survival improvement alone is insufficient. | Paired all-game wins, reach counts and cause-specific risk per queen-alive round. |
| 02 no production splits | Agree reject: gen win **−0.221 [−0.249,−0.193]**, economy −0.317 [−0.352,−0.284]. Queen verdicts 23–6 versus 1–7 are a changed outcome subset, not 22 causal added wins. | Preserve production in any split intervention; compare birth/length paths and overall win on paired fixtures. |
| 06 enemy avoidance | Agree reject: gen survival rises to 23.6%, but gen win **+0.013 [−0.012,+0.037]** remains inconclusive and economy is −0.040 [−0.054,−0.016]. | Ally-yield arm is justified to test, with exposure-normalised hazard and split-relative risk. |
| 06 death anatomy / 07 proposal | Ally deaths **97/271=35.8%**, enemy deaths 45/271=16.6%, and 88/271=32.5% die within three rounds after a production split. These are death-conditioned shares, not hazard rates or proof that splitting causes death. | Count ALL queen-alive rounds after splits and otherwise; stratify by map, phase, queen length and ally density. Publish both raw and adjusted descriptive rates; test the treatment on paired fixtures. |
| 04 sprint-price correction | Pool win **+0.040 [+0.016,+0.065]** supports a pool effect; gen **+0.003 [−0.011,+0.017]** leaves transfer unestablished, not proven absent. Economy near zero does not establish exact neutrality. | Preserve old gate verdict; director may classify a separate correctness baseline after validation. Freeze/re-measure any changed base and use 04 as 05's parent. No analyst promotion. |
| Rome baseline | **2/480=0.42%** is the joint reached-and-alive event, not comparable to Carthage's **2/219=0.91%** reach-conditioned survival. 22,364 successful sprint checks and 18 queen verdict checks support the instrument, not a policy gain. | Publish reach count, conditional survival, early W/L; keep gen outcome pending. |
| Kyoto probes / queued stack | r41→r171/r214 is a useful mechanism probe, not panel evidence. Latest board says the stack is queued even though status still says shelved. The revised arm includes a no-production-split intervention already costly in Carthage 02. | Treat as a distinct multi-change stack, not independent replication of 01 or 06; interpret via existing no-split control and two panels. Freeze fingerprint before runs. |

## 3. Answer Carthage's gate question without changing the gate

An economy-led superiority gate can reject a useful endgame intervention; that is a reason to propose a prospective
win-led evaluation, not to relabel past failures. Queen interventions do **not** necessarily lose economy by
construction: production-preserving movement may have either sign. Current observations show a tradeoff in these arms.

A future director-approved endgame gate should use paired **overall** win share as primary, plus fixed, predeclared
map/structural strata. Conditional win among games that happened to reach the limit can change its population under
treatment; report it as a diagnostic with arm-specific reach counts. A proposed economy noninferiority margin must be
chosen before the next test and justified as an acceptable cost, not chosen to pass this result. The suggested −0.03
lower-bound guard would **still fail 06** (pool −0.033, gen −0.054) and 02 (gen −0.352). Nor does 06 establish positive
overall gen gain. Existing D-032 verdicts therefore stand regardless of this debate.

H-H1 remains proposed L24/L39, weight **0.5**, not confirmed: a larger retained queen head piece on escapable production
splits may protect it at lower birth cost than banning production. The observed 88 post-split deaths make a denominator
audit worthwhile, but do not increase its evidential weight. Falsifier, test sizes and tester fit remain unit 1:
upper 95% bound of queen-survival gain <=0 or upper bound of overall-win gain <0; demonstrate production advantage;
paired seeds 1–3 both panels; about 149/306/463 independent binary pairs for a 10pp effect at discordance .2/.4/.6,
with map/series clustering assessed. Rome after baseline or Carthage's production-preserving follow-up suits it.

Antioch H-Q7 measurement warning: a **p90 sighting gap of 25 rounds is not proof of death after 25 silent rounds**.
Keep alive/dead/unknown state; prove death from observed evidence or validate a calibrated inference. Sighting gaps
conditional on eventual reappearance do not describe permanent non-observation. Freeze and score state-classification
errors before attributing policy wins to queen-state switching. This is guidance on an existing hypothesis, not a new
ledger row or a bot implementation.

## 4. Era and decoder reconciliation

Nara uses 09:00Z and Antioch 06:00Z as classification thresholds. The current index has **0 games starting in [06:00,09:00)**,
so these classify current games identically. Neither threshold is a measured deployment instant. The current earliest
post-gap start is g800028 at **09:23:44.121Z**, earlier than Antioch's sampled 09:26:58 boundary; late pre-gap indexed starts
exist through 05:57:06.388Z. These metadata endpoints do not independently prove engine semantics in every endpoint replay.
Keep Antioch's store-era rule until its owner revises it; request an endpoint reconciliation, not a second store write.

Prefer Antioch's **authoritative result** decoder patch for mixed historical corpora. Carthage's inferred queen-first
ranking is appropriate for its known 1.2.3 panels but defaults to that rule for any replay; `FRAME_RULES=pre123` is
required for historical inputs. Its cache key does include RULES, so this review found no cross-rule cache-key collision.
Both call themselves FRAME_VERSION 6 despite different implementations: record source commit and rule mode, not version
number alone. Carthage's statement that replay files lack queen fields conflicts with the result header: unit 1 validated
all 800 final queen values against reconstructed queens. No shared decoder was edited by Himeji.

## 5. Reproduction, freshness and next action

Query: `tools/himeji/audit_peer_queens.py --repo <wt-himeji> --corpus <main>/public_replays/corpus
--peer-rows <main>/build/nara/queen_post.jsonl --out <private-output>` (join this shell example on one line).
One worker; 60 full decodes; query outputs committed under `tools/himeji/peer_audit/`. Input peer SHA256
`ff67228a1b39c41279999734d4883f8c4ed12f7de1755aa0c8b0f4bc82577fe7`. Output rows freeze game IDs and series keys so an altered peer artifact is detectable.

Index snapshot: **78,281 unique games**, latest start **2026-10-01T15:05:09.495Z**; SHA256
`1cb0c9398259ee6f52f63286585bcd3ab816c7b06fd59b9b3c28f3c1306bbe10`. **0 post-era team-7 games**, so all live-us gaps remain NA. Ladder still
`20261001T062107Z.json`. Mac S-1 `corpus/games.parquet` contains **58,040 games**, latest start
2026-09-30 10:26:08.003Z, **no era column**; the published post-era desktop store is not present here. Himeji's unit-1
400-game references stay frozen and provisional; this unit audits measurement instead of rerunning them.

Sources read: main `cb2e920c7`; Antioch `ed714f51e`; Carthage `de85e8c58`; Nara `762ae51df`; Kyoto `5d7f3863b`;
Rome's uncommitted Mac status (pool done; gen 712/1392 at read). All five peer lineages are now identified. Board entries
have mixed UTC/ACST labels, so the change cursor is source commit plus entry content, not timestamp ordering alone.
Main's untracked Phase 2 protocol was reread without changing that checkout.

Next: obtain Nara's exact five claimed IDs / fix checkpoint labels; request Antioch's post store sync and current ladder
through the director; read Carthage 07/05 and Kyoto/Rome completed panels. If those are absent, perform the post-split
queen-alive exposure audit on existing replays. No fresh corpus pull or bot experiment is needed.
