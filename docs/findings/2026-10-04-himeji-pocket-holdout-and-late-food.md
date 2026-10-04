# Himeji unit14 — pocket rescue holds at opening, needs a late space safeguard

**H-H3 now has an outcome-independent holdout:** all17 newly collected Schooltime games absent from the unit13 freeze,13ranked/4unranked,17series,34sides and28teams. All34 queens start in a filled four-cell cycle with no static beds and no empty adjacent move. Thirty-three split first, shed their child and survive r25;29of those33 survive actualr490. The remaining queen moves into a wall at r0. This supports the proposed opening sequence as a feasible behavior, but does not establish its causal benefit or guarantee endgame survival.

The new failure mechanism is **growth filling the last spare cell**. All four late deaths occur one turn after a pearl increases the queen from3to4. Three happen with64 own units at the start of the death round; the fourth has62. A blanket rule to split again may fail at the unit limit, so legality and the actual turn state must be checked. No bot, intervention or simulator experiment ran.

## Held-out cohort and uncertainty

Selection was fixed before decoding outcomes: every Schooltime game newly present in corpus freeze116143 at00:23:48Z relative to unit13 freeze115805. Collection grew by338games;17matched. These games started3Oct21:51:02Z–4Oct00:07:40Z. This is a holdout by collection snapshot, **not a strictly future-time validation**; some games were played before H-H3 was proposed. There are four map hashes, both seats, no live-us games and only two current-top10 sides (566 and952, both survive at3). Opponent submission headers are unknown in all34sides.

| Population | Games / series | Sides | First split / alive r25 | Reach r490 / alive r490 | Descriptive survival, series-bootstrap95% interval |
|---|---:|---:|---:|---:|---|
| Ranked |13 /13|26|25 /25|26 /23|88.5% [76.9%,100%]|
| Unranked |4 /4|8|8 /8|8 /6|75.0% [25%,100%]|

All17 games reach the checkpoint; no r490 censoring in this cohort. Both sides share a game/series and are resampled together (5000whole-series draws, seed114). Four geometry hashes and repeated teams limit generalization; especially the four-series unranked interval is not stable. These are collected-cohort diagnostics, not field-percentile targets, causal contrasts, or replacements for frozen references. Matched top10-minus-us gaps remain missing. A33/33 opening count is not33 independent geometries.

## Why one opening split is insufficient

| Game / team | Last growth | Next action/death | Own units at start of death round |
|---|---|---|---:|
|996984 /280|pearl r324,3→4|wall r325|64|
|997644 /187|pearl r267,3→4|wall r268|64|
|997644 /280|pearl r267,3→4|wall r268|64|
|998186 /791|pearl r319,3→4|wall r320|62|

These are four queens in **three games**, not four independent failures. In996984 the same queen previously grew to4at r195, split2+2at r196 (61own units at round start), and returned to3after an allied-corpse meal at r197. Thus repeated splitting is an observed possible continuation, but this trace does not prove it was legal at the later failure. Turn-start unit counts are not a full action-time legality audit.

A separate survivor (997816,team470) pays one segment on a two-step sprint at r148 and finishes at2. This shows another observed way to create spare space; it does not prove an intended safety policy or a winning tradeoff. A length2 queen can lose to a length3 queen. Do not combine sprint-shrinking and repeated splitting into one experiment and attribute success to either mechanism.

Team470 also moves into a wall at r0in998463. Both games list sideA, but the original queen IDs/orientations differ (0versus1). Two games with unknown submissions and unmatched opponents/layouts do not establish bot switching, much less spoofing. Use actual original-queen identity and local structure, never side→ID parity or map-name rules.

## H-H3 refinement / proposed ledger L24 and L49

Weight stays0.5. **Mechanism:** preserve free space for the original queen throughout a sealed-cycle occupancy process, including after new food; an opening2+2split is only the first repair. H-H4's late feeding proposal must remain structurally separate: feeding a sealed four-cell queen can remove its last legal continuation rather than help it.

**Next test, owner:** Rome after its already running L39/L49 arm, or a free tester explicitly assigned by the director. First perform small action-order/legality checks in the isolated1.2.3 runtime: rotated/reflected full cycles, parent retention, child clearance, growth to4, unit-limit states and unknown observations. Compare a validated opening-only rescue with the same rescue plus repeated legal recovery, holding other behavior fixed. A sprint-space variant is a separate possible contrast, not silently bundled. Use actual visible topology/occupancy; do not promise recovery when the policy cannot observe or legally execute it. Log every child death and segment payment, retaining hygiene and production guards.

**Falsifier:** reject guaranteed sufficiency of a one-time opening split—the late failures already contradict that strong claim. The weaker recovery hypothesis is rejected if legality checks cannot preserve the original queen through an exposed growth event, or if a powered paired exposed test has an upper95% survival-gain bound≤0. Failed overall-win, opening economy/material or hygiene guards reject usefulness despite a survival gain. Inconclusive intervals remain unresolved. Unknown legality at saturation is an explicit gap, not evidence that more splitting is always possible.

**Size:** retain the unit13 plan of≥60independent eligible fixture pairs for mechanical reliability, now including **late growth exposures**, plus inactive-trigger controls on open/partly occupied components and cases where splitting is illegal. Zero failures in60independent cases gives a one-sided95% failure upper bound4.87%; repetitions of four map hashes do not supply60independent geometries. For a10pp paired binary gain, approximate n149/306/463at discordance.2/.4/.6 (two-sided5%,80%power), before cluster inflation. Use existing pool/gen panels for all-game outcomes and report actual eligible events; nominal panel size is not exposure size. Preserve H-H4/H-H1's existing Rome queue and weight0.5; no extra experiment is launched by this report.

## Pearl origin is a measurement caveat

The four late growth events are labeled `bed` by FRAME_VERSION7. In997644, direct raw-event audit shows a pearl appearing at round267 on(3,1), whose map TILE record is(0,0), with no countdown events in the four-cell component. The event occurs immediately after RoundStart, not in an adjacent recorded death sequence. `frame.py` assigns `bed` to a pearl appearance unless its adjacent-event death tracker supplies a donor; it does not verify a static bed.

Therefore “no static beds” does **not** mean “no future food,” and this label alone cannot establish the source of the late pearl. Preserve these events as **non-static-bed / origin unresolved** in interpretation until the engine's spawning cause is verified. Do not change the legacy decoder/store or silently count this finding as a new bed-income target. Request an origin audit before publishing revised Q3 bed/transit components; static-bed versus other spawn provenance may matter beyond this pocket. The observed food→length4→wall sequence does not depend on knowing its origin.

## New peer readings

Nara53861abb2's00:05board entry correctly identifies four queen-decided ranked losses, but only **three of its four cited games have a terminal material lead**:81–50,249–6,268–3. Australia995614is154–155at finish and146–148at actualr490, so it is not a material-lead loss at either checkpoint. Schooltime996205is268–3at finish and270–3at r490; queen self-death at0is independently verified. The3/4figure is conditional on Nara's four cited losses, not a denominator over all15live games or all round-limit leads.

Nara's acceptance also still describes its737old games as14265-only. Frozen official headers instead contain501of14265and236of14585;14585is already observed in game852606with indexed start2Oct04:22:43Z. That is an observed game timestamp, not a verified activation time (registry creation time differs). Neither a14265-only restatement nor a3Oct21:56activation boundary follows. Terminal queen2/398also means rare, **not literally zero**. Preserve historical statements and append these corrections. L10HOLD is agreed; no new completed tester result arrived, and Rome's queen-conversion extraction was still running at this wake.

## Provenance and next action

Source main0298966ec /D-042; Antioch2c7113f66, Carthage5b69fa9d0, Kyoto fccea71c0, Rome6f1ec3527 unchanged; Nara53861abb2new. Protocol, targets, board and all five peer statuses read. Himeji prior commitb97bbfef1; current boardH14-01..06. FRAME_VERSION7source hash in selection; source dependencies remain read-only. Era: started≥1Oct06:00Z, post123; no local population pooled.

Read-only SQLite connection succeeds (`mode=ro`,query_only1);14585active /14265idle lastseen4Oct00:22:27Z. Sole collector35400healthy,19–30downloads/pass and0errors in inspected passes; no competing collector/API call/configuration change. Raw freeze116143/lateststart00:20:26Z; indexSHAc42aa8f42d9b38189461179989cfbefc32508869bb24d44cc959f3f485a9d717. Ladder002228Z SHA2c736c7d5f2b409d54c2044407067db9358ff307ab46e3372cc98f932e44cdbb; top264/306/91/213/55/842/87/952/82/566. No new own games among338new downloads. Collection coverage requestsH11-05/H12-05remain pending.

Versioned store remains423games/846sides and its110-game unit12 queue checkpointed, with no active Himeji writer. One replay worker used because Rome was extracting with16workers. This unit audited19distinct replays (17holdout+2named corrections),19official-winner matches and38terminal queen header/body matches; targeted trace/provenance queries add detail without changing the cohort. No simulation, bot build/experiment, environment modification or shared-store write.

Reproduce from immutable snapshots (MAIN is the source checkout; U13/U14 are the saved unit directories):

```sh
python tools/himeji/pocket_holdout.py --repo MAIN --snapshot U14 --previous U13
python tools/himeji/pocket_failure_trace.py --repo MAIN --snapshot U14
python tools/himeji/pocket_summary.py --snapshot U14
python tools/himeji/pearl_origin_audit.py --repo MAIN --out U14/pearl-provenance.json
```

Selection, raw compact side rows, trace data, hashes and intervals are frozen under `tools/himeji/unit14_audit/`. Next: check Rome's finished result with queen-at-trigger exposures; investigate non-static-bed pearl provenance and action-time legality at saturation before stronger H-H3 claims. Negative trigger specificity beyond the fresh Schooltime cohort remains untested. Resume the saved broader store queue when shared capacity allows; do not repeat these unchanged audits. H-H2spoofing remains unresolved; no inferred identity or intent.
