# Himeji unit13 — two falsifiable queen hypotheses

This unit prioritizes hypothesis generation following the user's direction. It proposes **H-H3: preserve the queen inside a full spawn pocket by splitting off a child**, and **H-H4: separate early queen production from later queen growth**. H-H4 refines the already queued L39/L49 work; it is not a claim that a second independent tester queue is needed. Neither proposal has been implemented or experimentally validated by Himeji.

## H-H3 — free one cell, keep the original queen

**Proposed ledger link:** L24/L49, initial weight0.5. **Suitable tester:** Rome after its current queued arm, or a free tester assigned by the director. Do not restart paused Carthage/Kyoto or interrupt Rome's ongoing run.

**Mechanism.** A length4 queen can fill a four-cell cycle at spawn. Every ordinary step then hits its own body or a wall. A legal2+2 split retains the original head/queen ID; removal of the tail child can free a cell. The queen can collect one corpse pearl, remain length3, and circulate inside the four-cell component. This preserves the queen tiebreak without requiring escape into the wider board or a long queen. The trigger must use visible topology, body occupancy, split legality and child/parent action ordering—not the map name, coordinates or ID parity.

**Evidence.** Unit12's Schooltime995611 queen loss (total249–6) is one of21 freshly event-audited Schooltime turn-zero self-deaths from21 series:6ranked/15unranked, across two own submissions. All21 queens have **zero empty non-wall one-step destinations** at spawn. The selected negative case, Default828475, instead has three empty destinations and dies in a head-on collision; it belongs to a different mechanism. Thus my initial generic safe-move-veto idea is not supported as a solution for these21 pocket cases: it would have no empty step to choose.

The prior737-game artifact contains these Schooltime counts (a historical sample census, not a controlled version comparison):

| Own submission | Mode | Schooltime games / series | Queen self-death at r0 |
|---|---|---:|---:|
|14265|ranked|14 /14|1|
|14265|unranked|39 /39|1|
|14585|ranked|4 /4|4|
|14585|unranked|14 /14|14|

Adding995611 contributes one more ranked14585 case. Four deterministically selected non-r0-death controls from14265 all split first, have **two empty adjacent steps**, and survive r25. Their map hashes differ from the self-death cases. Consequently the18/18 versus2/53 difference is confounded by changing geometry/time/opposition; it does **not** prove that the sprint update caused the deaths. Preserve modes, submissions and actual geometry when testing.

Among the21 paired opposing queens,20 split first;19/20 survive r25 and18/20 survive actualr490 (all20 reach that checkpoint). This is an observational comparison across opposing policies/seats, not a causal effect estimate. It is nevertheless a direct existence proof against a blanket claim that pocket queens must die.

In995611 the opponent's original queenID1 performs SPLIT2 at r0. ChildID6 makes a north move and self-dies in the same round. At r1 the queen moves east into the freed cell and eats one allied-corpse pearl from child6, becoming length3. Its heads occupy exactly the four cells(56,1),(56,2),(57,1),(57,2) throughout the replay. A terrain flood confirms a **four-cell component with no beds**; its queen finishes alive at3. Our queenID0 on sideB instead moves north into its neck at r0. This is **survival within the pocket**, not successful escape. The observed child death/action is explicit; the opponent's internal intention remains unknown.

**Suggested one-switch test.** Add this rescue only when the original queen is fully observed in the requisite component, has a legal split, and the parent/child sequence can leave a legal next queen move. Keep the rest of the policy and production unchanged. Explicitly log any deliberately removed child; do not count its corpse as new income, or silently exempt an opening cull from hygiene guards. The same trigger must remain inactive in open components, for non-queens, with length<4, at the unit cap, or where the action order cannot clear the required cell. Those are negative controls.

**Falsifier and decision.** First verify engine legality and ID retention with a small deterministic action check under the isolated1.2.3 runtime. Reject this form if the original queen still has no legal continuation after the split/child sequence, or the policy cannot detect the needed state using available observations. On paired exposed fixtures, reject the survival mechanism if the upper95% bound on r25 survival improvement is≤0; uncertain bounds mean unresolved. Overall-win upper95%<0 or failed opening production/material/hygiene guards falsifies the useful-policy claim even if pocket survival improves. Report r25 and r490 reach/survival, early elimination outcomes, original ID retention, child cost and all-game wins; no survivor-only acceptance.

**Size.** Start with mirrored/rotated reachable-state and action-order checks, then at least60 independent eligible fixture pairs plus matched ineligible controls. If zero mechanical failures occur in60 independent exposed cases, the one-sided95% binomial upper failure bound is4.87%; repeated versions of one layout do not supply60 independent cases. This tests execution reliability, not a global win gain. A10pp paired binary gain needs approximately149/306/463 independent pairs when candidate-parent discordance is.2/.4/.6 (two-sided5%,80% power, formula below). Use the existing three-seed pool+gen panels and count actual exposed fixtures/independent clusters; extend with new held-out geometry/seeds only if exposure and precision require it. Rare pocket exposure dilutes an all-game effect, so do not promise10pp overall gain.

## H-H4 — produce early, then grow the queen when conversion becomes useful

**Proposed ledger link:** refinement of L39/L49 and H-H1, weight0.5 unchanged. **Suitable tester:** Rome's already queued queen-keyed conversion experiment; use these distinctions in its reading before claiming another experiment. Carthage10 is an existing time-triggered comparator only if its lane resumes independently.

**Mechanism.** Keeping a queen alive need not mean withholding all its early production. Retain the original head while allowing productive splits, then direct retention/feeding toward that queen at a predeclared observable conversion trigger. The causal claim is that separating these phases avoids the opening cost of an always-long queen while improving endgame conversion relative to the same producing parent. Early pocket rescue and late growth are separate switches, tested sequentially with explicit parent identity; do not combine them and attribute the result to either one.

**Evidence without selecting only long survivors.** Freeze all collected ranked306/91 games on Maze and Slithery Fight started on3October in the23:53Z corpus:12games/12series,8team306 and4team91. All12 queens production-split beforer100. All11 round-limit games actually reachr490, and7/11 queens remain alive; the one early elimination is censored forr490. Seven eventualr490 survivors all grow beyond theirr100 length and consume allied corpses fromr300 onward. Failed cases remain in the sample: four queens die beforer490 in round-limit games, and one dies before its team wins an early elimination. No causal effect, field percentile or population survival target is inferred from this collected two-map sample.

| Team / map | Games | Queen lengths at r100 | Reached490 / alive490 |
|---|---:|---|---:|
|306 Maze|5|7,7,7,7,7|4 /3|
|306 Slithery Fight|3|14,20,13|3 /2|
|91 Maze|2|3,2|2 /1|
|91 Slithery Fight|2|3,3|2 /1|

Team91's surviving Maze example remains length3 at r400 and reaches35 byr490. Team306's surviving Maze examples grow earlier. Both strategies include production; neither justifies a universal length2–3 target or a universal r300 switch. The two-map selection tests whether unit11's four selected examples were exceptional; it does not establish deployment identity, spoofing or the best trigger. The existing failed no-production arms (Carthage02/03) motivate the tradeoff, not an exemption from measuring it.

**Suggested contrast.** For the already queued arm, report the complete parent contrast first. If it is informative enough to justify a timing test, compare an always-retain queen policy with a producing-until-trigger policy while holding the queen selector, movement safety, donor routing and trigger observability fixed. Keep policy constants/thresholds predeclared and structural; no map-name rules. Use only information the bot actually observes—unknown enemy queen state stays unknown. The present corpus does not determine a numerical optimal trigger.

**Falsifier and decision.** A producing-then-growing arm must retain early net income, births and total length, then improve queen margin/conversion and all-game wins under the authorized gate. Reject the delayed-growth mechanism if a well-exposed paired test's upper95% bound on the chosen endgame improvement is≤0, or the opening/hygiene/overall-win guards fail. A queen already dead when conversion could begin is **not exposed** to the late mechanism: report that count, but keep those games in all-game outcomes. For a timing contrast, exposure must be defined before policies diverge; conditioning on candidate-specific survivors is biased. A null from almost no live queens at trigger does not test feeding quality—it exposes the need for a survival intervention first.

**Size.** Begin with the existing480pool/1392gen paired fixtures/seeds1–3 for the queued arm, recording actual eligible triggers and seed×map plus map×opponent×seat clustering. For a further late-only contrast, about52 independent exposed pairs resolve a20pp binary improvement at discordance.3; require at least60 eligible independent pairs as a practical floor and report cluster inflation. Overall10pp gains have the149/306/463-pair planning range above; smaller effects need more. The BENCHMARKS45–60 side-game pearl and70–80 units/length resolution figures concern half a between-bot SD and are not substitutes for the binary-win power calculation. Do not launch a large extra panel just to meet a timer.

For planning, with paired outcome differenceD∈{−1,0,1}, discordance d=E[D²] and effectδ, use n≈(1.96+.84)²(d−δ²)/δ². These are independent-pair approximations; estimate d and clustering from an initial fixed sample. Inconclusive intervals stay inconclusive. Survival/growth thresholds above are proposed test criteria, **not field-percentile targets**.

## Readings and coordination

Nara5242954ac acknowledges the renewed own series but asks whether a later activation exists. Yes: the exact737 audited headers are501submission14265 and236submission14585, with the later version first observed at2Oct04:22Z in that sample. H11's frozen header rows and H12's active registry evidence establish this; no inference from an activation timestamp is needed. The pooled737 headline does not describe14265 alone. The new geometry result also means version differences must be stratified by spawn structure.

Retain the disagreement on Nara's new units ruling: the reported−.0228/−.0322 bounds are normalized median changes, **not paired log changes**, so they cannot be declared passes against a log−.10 rule. L10 was not automatically reclassified by D-042's adaptation exception; H12's preregistered median-estimator HOLD stands. No new complete tester result arrived on Rome; its queen-conversion queue is already claimed. Nara has claimed Seoul's existing-replay split-opportunity decomposition; Himeji does not duplicate it. New hypotheses and requests go through the numbered branch board; no paused lane is awakened.

## Scope, freshness and reproduction

One read-only decoder worker audited38 distinct replays:21Schooltime self-death cases,1Default head-on negative case,4open Schooltime controls and12ranked growth games. Both original-queen terminal fields match bodies and official winners match the frozen index in every replay. The detailed995611 split trace adds the child/death/food sequence. No simulator, bot build, bot experiment, API request or shared-store write ran. Broader store decoding is deliberately deferred this unit to honor the user's hypothesis-generation priority; the110-game unit12 queue remains checkpointed, not active.

Collector PID35400 healthy,32–40 downloads/pass with0errors in inspected passes; read-only DB connection succeeds and14585 remains active at23:50Z. Frozen corpus115805 at23:53:25Z, lateststart23:49:36Z; indexSHAf8bc8a15e7f001c5610f7c36556084375fd1f73d382e77942d3f6369ea2b873f. Ladder235044Z SHA0760e383eece7050a1b10649b037f13b56a1d8f8236b85e5df5f5017f22a246b; top306/91/264/213/87/842/952/55/82/566. Store remains423games/846sides, lastdecoded23:11:43Z3Oct; its source hashes unchanged. Existing collection patches/own-coverage requests remain pending; no service restart or deployment action.

Source cursor: main0298966ec/D-042; Antioch2c7113f66; Carthage5b69fa9d0; Kyoto fccea71c0; Rome6f1ec3527; Nara5242954ac23:35 entries new. All five statuses, protocol and target changes read. Himeji boardH13-01..06. All evidence is post1Oct06:00Z; ranked/unranked separated, local panels only mentioned as prospective tests. Unknown opponent identities remain unknown; H-H2 spoofing is unresolved. Historical references/verdicts and other analysts' proposals remain intact.

`tools/himeji/unit13_audit/` freezes selection rules, IDs, raw rows, summaries and replay hashes. Case selection uses Nara's prior death-round fields only as leads, then re-verifies raw events; four controls are two lowest SHA256(gameID) cases per available submission/mode. There are no14585 no-r0-death controls in that earlier Schooltime sample. Growth selection includes every matching collected game in the declared window, independently of outcome. Collection bias and small per-stratum counts preclude stable targets or an inferred current-top10-minus-us gap.

```sh
python tools/himeji/hypothesis_evidence.py --repo MAIN --snapshot UNIT13 --audit tools/himeji/unit11_audit
python tools/himeji/summarize_hypotheses.py --snapshot UNIT13
python tools/himeji/split_pocket_trace.py --repo MAIN --out TRACE.json --game 995611 --side A
```

Use the existing analysis Python for decoding; no helper rebuilds norms. Next runnable analysis: evaluate H-H3's geometry trigger on a fresh held-out collected cohort and await the tester's legal-sequence/paired result; read Rome's current arm with exposure counts. Resume the saved decode queue when capacity permits, without making downloads the main analytical deliverable.
