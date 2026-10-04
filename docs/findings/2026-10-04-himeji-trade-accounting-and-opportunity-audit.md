# Himeji unit34 — live trade accounting and queen-opportunity corrections

4 October 2026,10:31UTC. Final bounded unit before the user's wrap-up. No new bot experiment.

## Live head-on trades: answer to Shenzhen, complement to Chongqing C9

Forty existing ranked post-m2 games on4Oct:20own14585 and20unique frozen-top10 field games. Selection is independent of outcomes: latest eligible own series per map, matched full map hash and seat, nearest field start within120minutes, no field-game reuse, maximum12pairs/map. Available support:7pairs AroundUNSW,7Australia,6Islands; two hashes/map. All40payload/fullmap/officialwinner checks pass. Frozen ladder101347Z and complete selection in `tools/himeji/unit34_audit/trade-selection.json`. Opponents are unmatched. Fullhash/mode cells are retained in `hash-cells.json`; these small matched samples are not stable percentile references.

Count deaths fromr150 onward. Mover=the dying dragon was the recorded actor in that enemy head-on; partner=the other dragon. This is a fraction of **head-on deaths**, not a propensity to initiate conditional on all contact opportunities.

| Map | Own mover / enemy h2h deaths | Field mover / deaths | Field−own,pp [95%] |
|---|---:|---:|---:|
| AroundUNSW |310/598 =51.8%|357/727 =49.1%|−2.7 [−22.0,14.7]|
| Australia |224/544 =41.2%|622/1053 =59.1%|+17.9 [1.9,32.9]|
| Islands |356/803 =44.3%|409/736 =55.6%|+11.2 [−4.2,23.7]|

4000 connected-series bootstrap draws, seed3434; matching links own/field series,7/7/6 independent connected blocks per map. Small-cluster intervals are exploratory. Australia supports the directional lead in C9; AroundUNSW does not support a universal deficit. C9's own displayed0.52−0.47 is5pp, not9pp;0.56−0.43 is13pp. Different selections do not make either table a replication of the other. Do not set a universal≥0.52 mover target from these data.

For4290 cross-team trades with actual50rounds follow-up, both deaths and their pairing are verified, lengths are measured **at death**, and corpse meals join donorID+birthround+cell. No round-only first-cell-eat matching. Counts include all such trades in each selected game, one focal side per game. The two participant teams' ledger obeys exactly:

`relative material result = (partner length − mover length) + (corpse meals to mover team − corpse meals to partner team)`.

| Map / focal cohort | Trades | Starting-length term | Capture term | Relative material result | Equal-length trades: capture term [series95%] |
|---|---:|---:|---:|---:|---:|
| AroundUNSW / own |572|1.794|0.816|2.610|140:1.057 [0.545,1.421]|
| AroundUNSW / field |665|1.759|1.060|2.820|197:1.015 [0.658,1.425]|
| Australia / own |519|1.915|0.811|2.726|170:1.065 [0.395,2.029]|
| Australia / field |1027|0.322|1.166|1.488|384:1.172 [0.949,1.451]|
| Islands / own |791|0.652|0.662|1.315|338:0.793 [0.483,1.064]|
| Islands / field |716|0.728|1.360|2.088|294:1.514 [1.311,1.775]|

Units here are **body segments/pearls**, not dragon counts. Equal-length rows remove the mechanical starting-length term; a descriptive mover-side capture advantage persists in1523equal-length trades. These are whole-series bootstrap intervals within cohort, not independent-per-trade intervals. Spatial position, surrounding allies, player strength, direction, turn order and choice to initiate remain uncontrolled. This supplies a collection hypothesis, not a causal “swap mover and gain” estimate. Multiplying a conditional1.9 differential by65trades to promise124new units/game (Nara10:02) is invalid: the actors, lengths, risk set and subsequent game change when the policy changes; recycled food is not new material.

Retain H-SZ34 as a proposed L24/L49 mechanism with this qualification: relative body length and recoverable corpse access may help price an enemy collision. A separate body-avoidance intervention and post-trade salvage intervention must not claim each other's effect. A decisive next observational pilot would select≥60 **pre-collision contact opportunities**, including no-trade outcomes, across≥20series and match hash/seat/mode/length/nearby collectors/order. This is a coverage/variance pilot, not a win gate. Falsifier: precise no incremental payoff calibration after spatial/length controls, or an assigned intervention's overall win loss despite its role-count gain. Suitable tester: Shenzhen/Seoul after current work; no arm requested during wrap-up. If assigned, fixedcarthage05/liveM2 parent, penalty0/x/2x, expected fewer costly partner contacts; selected dose needs D042 full win gate.149/306/463 independent pairs for10pp at discordance.2/.4/.6 are only pre-cluster planning values.

## Kanazawa unit15: reproduce the numbers, correct what they mean

Same96 consumed games, not fresh replication:17ranked14585,71unranked14585,3ranked14265,5unranked14265.96payload/fullmap/winner checks. The queen-only opportunity query reproduces264/25own and586/18opponent opportunity/hit counts exactly, plus9324/18805queen-rounds and238/554risk-indicator rounds.

| Quantity | Own queen | Opponent queen |
|---|---:|---:|
| Hits initiated by the queen itself |1/25|6/18|
| Hits where queen was the partner |24/25|12/18|
| Non-hit opportunities |239|568|
| Non-hit and both dragons survive next round |224|548|
| Flee / jointly surviving non-hit opportunities |165/224 =73.7%|444/548 =81.0%|
| Chase / jointly surviving non-hit opportunities |75/224 =33.5%|202/548 =36.9%|

The published69%/78% flee figures divide by all non-hits, including15/20 cases in which the follow-up is unmeasurable. They are not the conditional fractions stated in the definition. Retain those earlier numbers as historical labels, corrected above. Seven of43“strikes” are queen-initiated collisions; if discussing an incoming enemy attack, distinguish these roles. Partner-hit fractions on the original opportunity denominator are24/264 and12/586, descriptive only.

The query uses **round-start** geometry, not actual attacker's TurnStart vision. In11own+10opponent opportunities, the enemyID is smaller than the queenID, so “queen moves first” also is not universal. B+1, body-free terrain distance and omission of food remain approximations. A risk indicator on238/9324queen-rounds does not measure which candidate moves a real veto rejects, its fallback behaviour or its cost. “About10firings per strike prevented” assumes unmeasured prevention.

Most importantly, chase/flee is conditioned on neither dragon dying. It cannot separate the cause of fatal outcomes or establish absence of targeting; the compared queens also differ in length, phase, map, opponents and survival selection. The policy may price reach, but this query does not prove the field implements a veto or that queen motion causes the full gap. Retain peer H-KZ26.65 alongside this disagreement; Himeji H-H8.4 remains a feature hypothesis. Leave KZ's new tier/pincer/sonar tests to that lane. Next validation should use actual decision-time observable risk sets and fixed-policy paired doses, with series-level uncertainty and held-out series.

## Other readings and operational close

CQ's r50→r250 survivor-conditioned z gaps are useful descriptions, but changing alive cohorts, varying per-checkpoint normalisation and ranked-field versus all-mode-us do not identify a causal attrition trajectory. A portal pearl z-gap closing does not by itself prove deaths explain the remaining length gap. Keep fullhash/mode rows and account for retained split mass, sprint costs and elimination censoring. Frozenreferences stay; no new stable target/matched-live-us replacement.

Rome cursor30: correctedcarthage05/1.2.3/LIVE_MAPS_M2 k4 gen diagnostics140/464, first89transcripts match official outcomes and yield8793queen decision rows. Pool272/272parity already published. No new completed dose table or gate verdict. No extra run or interruption requested.

Collector PID35978 healthy,10:21:27pass40downloads/0errors, own2524/4000 at10:22:51. Freeze10:23:57:124161index (+685/+171own),latestown10:17:12. ROimmutable/query-only SQLite10:13:46 active14585/idle14265,1178series,WALexcluded. Ladder101347Z. Newmainbuilder45267ddc adds `deaths.mover`; absent columns in historical parts remain missing, not0. Own31games/62sides+1110queue and old754 unchanged; CQ reports shared51396/idle, not recounted here. Source commits in manifest; newCQ/KZ/Nara/Seoul and board/TARGETS read. CQwrap-up leaves no shared-store writer. No collector/API/main checkout/store/bot/simulator changes by this unit.

All query workers finished. Trade summary reproduces exactly from committed per-map shards; every artifact<4MiB. User then requested wrap-up/main publication and cancellation: Himeji's recurring automation was deleted successfully; no further analyst cycle scheduled. Other listed jobs belong to other chats and were already paused. Main is merged/published from the Himeji worktree; the shared main checkout remains untouched.

Reproduce with MAIN analysisPython: `trade_trace.py --repo MAIN --selection tools/himeji/unit34_audit/trade-selection.json --out SCRATCH`; `trade_summary.py --data tools/himeji/unit34_audit --out SCRATCH/summary.json`; `queen_opportunity_audit.py --repo MAIN --selection tools/himeji/unit34_audit/kz-selection.json --out SCRATCH`. Initial matching query: `trade_select.py --snapshot FROZEN_INDEX_AND_LADDER_DIR`. Selectedmetadata+hashes preserve the40-game selection without a live query. Never commit the unsharded5MiB trade output.

## RL translation (D044)

**Observation:** actual decision-time heads/bodies, original queen, relative lengths, turn order, visible pearls, nearby potential collectors and path accessibility. Future corpse fates are training labels, not policy inputs.

**Action:** avoid, initiate or yield at contact; later collect a corpse. These are separate decisions, not a magic actor-label swap. Reach penalty0/x/2x needs measured candidate rejection and fallback, not round-start indicator counts.

**Value/reward:** official win first; body lost and food recaptured by each team, lost production and queen-first consequences. Retain starting-length and capture terms separately. Do not add a fixed1.9 reward to every initiated collision.

**Demonstration:** live matched replays supply4290trade ledgers and1523equal-length examples with observed mover-side recovery advantage. They lack counterfactual alternatives. The96-game queen audit supplies corrected observational labels only; learning effectiveness requires independent state support and held-out policy/value evaluation.
