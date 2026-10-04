# At the cap, measure food throughput as well as deaths and unit count

4 October 2026, 06:07 UTC. Himeji unit25. Ranked post-m2 Slithery pilot, plus new analyst/tester readings. No bot, simulator or learner experiment.

**The top-team comparators make more splits and eat more bed food, while spending less time near the unit cap.** This is evidence against treating production splits at the cap as automatically worthless. It does not establish that more splitting causes better play: the opponents are not matched, and only five independent connected series groups underlie this pilot.

## Cohort, checkpoints and accounting

Selected all **six collected ranked Slithery games of confirmed carthage-05 /14585** after its activation. For each, selected the nearest three current-top-ten sides with the **same full map hash and seat**, within six hours. Actual maximum separation is49.85minutes. This gives18 field slots,17 unique field games/series, all10 top-ten teams represented; one reused field game connects two own blocks, leaving **five connected series groups**. The six own opponents are347/104/30/328/55/801, not the field comparators' matched opponents. Keep the fully opponent-matched live-us gap missing.

All games use post-m2 Slithery geometry, hashes `2b2eaa9c0cd978c17348887b5270b24ba8dc868219d327dec776d7e403b81129` and `c8e8fa61335b7fca9e180ecd947ef28eb7bb2ce054f323bec875bd72da8cd655`. Own games range2Oct04:23 to4Oct00:18. This is current collected coverage, not six newly downloaded games. Top-ten membership is frozen to4Oct05:49:53Z. All18 field-slot submission identifiers are blank: team behaviour is observed, active bot identity remains unknown. Ranked only; unranked and local populations are excluded.

Checkpoints are **start of round**, with intervals [0,250) and [250,400). All23 unique games reach both windows; no early-end carry. Verified23 payload hashes,23 full replay-map-text hashes and23 official winners. The decoder's aggregate identity closes with **zero residual in all92 side-windows**:

`change in live body length = bed + ally-corpse + enemy-corpse + unknown food eaten − sprint segments − body segments lost at death + split mass change`.

Split mass change is0 throughout; unknown-origin meals are0. Splitting and eating an ally corpse redistribute previously existing body material. Bed intake is an external food source for the team; enemy corpses transfer material from the opponent. Corpses may still remain uneaten at the window boundary. This accounting does not assume that every dead segment becomes a recoverable pearl.

## Observed flow

Values are equal-weight means over six own blocks; each field value first averages that block's three matched sides. These are arithmetic means, not medians or field percentiles.

| Quantity | Ours | Top-team comparators | Field minus us |
|---|---:|---:|---:|
| Initial total length | 47.0 | 47.0 | 0.0 |
| Total at start250 | 165.7 | 212.1 | +46.4 |
| Units at start250 | 63.8 | 62.1 | −1.8 |
| Total at start400 | 181.8 | 215.5 | +33.7 |
| Bed food, rounds0–249 | 634.8 | 693.8 | +59.0 |
| Ally-corpse food, rounds0–249 | 479.0 | 494.3 | +15.3 |
| Segments lost at death, rounds0–249 | 1,017.0 | 1,037.9 | +20.9 |
| Bed food, rounds250–399 | 238.7 | 362.6 | +123.9 |
| Ally-corpse food, rounds250–399 | 238.0 | 376.7 | +138.7 |
| Enemy-corpse food, rounds250–399 | 30.3 | 30.5 | +0.2 |
| Segments lost at death, rounds250–399 | 478.3 | 751.2 | +272.8 |
| Sprint segments, rounds250–399 | 12.5 | 15.2 | +2.7 |
| Splits, rounds250–399 | 112.3 | 258.7 | +146.3 |
| Share of rounds250–399 starting at≥62units | 90.2% | 28.4% | −61.8pp |

The field's length lead already exists at250. During250–399, its greater food intake is more than offset by greater segment loss; the lead **narrows by12.7**. Thus the late throughput difference cannot explain the entire origin of the lead. In0–249, the accounting decomposition is +59.0bed +15.3ally −7.0enemy −0.06sprint −20.9death =+46.4total. This is an accounting identity, not a causal mediation estimate.

All six blocks have greater field bed intake at250–399 (**+80.3 to+188.0**) and more splits (**+110.3 to+196.7**), with lower cap occupancy (**−74.7 to−39.8pp**). The total400 gap ranges **−11.3 to+86.0**; it is negative in two blocks. Early bed-food differences range−59.0 to+195.3. These ranges are the uncertainty disclosure for a small selected pilot: **no stable confidence interval, significance claim or target** from five connected groups. Exact per-hash/seat/series rows, matches and dependence are published alongside the query.

## H-H7: productive replacement, not occupancy alone

**Proposed ledger L36/L41, weight0.4; suitable for Shenzhen's mechanism probe, Rome/assigned tester after the M2 zero, and Osaka's feature work.** At saturation, a unit slot has value through the future external food its occupant can collect. Turnover may replace low-yield units with productive descendants. Reducing production splits can therefore lower trapped deaths while also reducing bed capture; the corpse stream partially returns lost material but does not create it. The six-block pattern and Shenzhen's G trade-off motivate this mechanism; **we have not measured newborn-versus-resident bed capture**, so it remains a hypothesis.

Prediction for a production-only throttle, escape splits unchanged: stronger throttling decreases newborn bed intake and total bed intake on genuinely cap-exposed trajectories; the decrease can offset retained length from fewer deaths. The competing H-SZ26 interpretation predicts that suppressed production is unproductive and retained length raises total without a material food loss. Preserve both claims for a decisive test, rather than recommending a blanket split stop from a length-per-unit snapshot.

First extract age/parent-linked bed intake and the actual split opportunity/escape reason on an independent later set. For the temporary test, one production-admission mechanism with predeclared **full / half / quarter eligibility** at sensed turn-start unit count≥60 (eligibility periods1/2/4; dose0=unchanged parent, below60 unchanged) supplies a D-044 response curve. Use carthage05/LIVE_MAPS_M2, keep escape treatment and all other rules fixed; do not add E or a cull policy silently. The output must include bed/ally/enemy intake, lost segments, birth/split counts, cap occupancy, queen checkpoints, length, cause-specific deaths and official wins by regime and exact map/era.

Falsifier: verified throttling substantially lowers production yet a precise comparison rules out even a10% decline in bed intake, and newborn capture does not account for the proposed throughput pathway; a gain in total/wins without that food cost supports H-SZ26 instead. No exposed opportunities or a wide null is inconclusive. A **60 eligible paired-fixture pilot shared across doses** estimates the response/variance; for a10% food effect, paired SD20%/30% of parent food implies approximately32/71 independent pairs at80% power and two-sided5%, before clustering or dose selection. Treat60 as a pilot, not guaranteed power. Use later held-out fixtures and the full D-042 gate only for the selected shipping dose. No arm started here.

## New readings and corrected reference status

**Shenzhen9d8a76207, unit10:** live-template Slithery, unswbc1.2.9, carthage05-derived **C+D parent versus C+D+G**, seeds1–6/both seats: trapped deaths174→97, total1587→1218, wins6/12 each. Seed1–3's5/6 reverses on later seeds. Agree mechanism response and material cost; equal observed wins in12 sides do **not** establish no win effect. E3's150vs83 trapped deaths on six sides tests a different intervention that blocks escapes. Cage-conditional E is a proposed revision needing its own dose evidence. Feed our flow columns into the next dose table; no claim that corpus differences causally validate either arm. Direct reading sent to active Rome without requesting extra work.

**Kanazawafcab18e31, unit6:** accept the inclusive-capacity correction and later-game tree/cycle replication (19/19 own first tree entries wall-positive in the peer window). Any-death is a useful additional auxiliary outcome: self/invalid after entry are not safe survivors. Preserve cause-specific labels too; declare the eight-round horizon prospectively and censor terminal entries. The94 games are now a consumed holdout, not reusable for a fresh confirmatory claim. Request ranked/submission/series counts before treating38/190 as current14585 risk. A cycle's existence does not guarantee a body-legal route into it, and observed deaths do not establish avoidability; retain H-KZ11. H-H6 .5 retained; no duplicate cycle pass.

**Chongqing1d9642bab, C5-05:** repaired `queen_cols` passes six synthetic cases and the real boundaryg867918. Actual end489 gives q_len490=NULL for both sides, surviving queenB censored1, already deadA censored0; death-round cases0/489/490 agree. New q_len@k means **after roundk**. Himeji's historical start-round checkpoints stay labelled and frozen. Source repair does not repair earlier parts. `qq.py` selects the first filename per game; adding a corrected later part alone cannot displace an old canonical part. Keep schema/version provenance, and use the established death-derived terminal views for older parts. Shared/main source and stores were not edited or rebuilt; own qcols31/62 remains separate pending source/schema integration.

**Chongqing C5 references:** accept the larger descriptive sample, but not the claim that Himeji's release criteria are met just from side counts. Those also require independent game/series blocks, team coverage, interval width and later-window drift; queen-event precision was explicitly separate. The0.413 cohort survival mean is **not a top-ten team median**. Opening comparison uses ranked top ten versus all-mode us and is not a matched live gap; agreement between stores over overlapping corpus is not independent replication. No queen-map exemptions under D-043. Wall cause still does not identify a deliberate cull; H22's four pre-sealed weakhold cases remain counterexamples to that attribution. Retain their table alongside this disagreement, with Himeji targets provisional.

**Rome:** active carthage05/LIVE_MAPS_M2 zero reports pool816/816 complete, gen837/1392 at wake. No final scorecard/gate result yet. The six stale gen twins remain historical and the pool's missing Schooltime-open4/PD10 variants remain coverage limits. The earlier four timeouts are not losses; final fixture reconciliation belongs in the scorecard.

## Reproduction, freshness and next action

`tools/himeji/cap_mass_flow.py --repo MAIN --snapshot SNAPSHOT --out LOCAL --start 250 --end 400`, then the same command with a separate LOCAL and `--start 0 --end 250`. Aggregate each with `summarize_mass_flow.py --input LOCAL --out SUMMARY`. Frozen SNAPSHOT is the chat workspace's `work/himeji-unit25`; committed selections/derived flow records/summaries under `tools/himeji/unit25_audit` reproduce all arithmetic without raw replays. One worker at a time, all done. Boundary tool accepts `--ref 1d9642bab`; receipts freeze source hashes and semantics.

Raw119991 at05:52:55Z, +310/0new own since unit24; latest05:50:27Z. Collector35400 healthy, zero inspected download errors; ROimmutable DB checkpoint05:49:52Z14585active/14265idle, WAL excluded. Team7 collection resumption was last directly evidenced by unit21's03:25Z series; unrelated arrivals do not prove new own coverage. Ladder054953Z, current10 unchanged as a set. Shared store expansion to51,233/7,030post-m2 is Chongqing's report, not a Himeji rebuild or schema certification. No APIs, bots, executor changes or main edits.

Next: later independent age-linked bed-capture evidence for H-H7; read Rome's completed scorecard and the analyst replies. Do not rerun this23-game pilot merely on the next wake. Blank field submission IDs and unmatched opponents prevent switching/spoofing conclusions.

## RL translation — D-044

**Observation:** sensed unit count and near-cap headroom, individual age/length and productive bed access, recent food intake, queen/escape state and actor-order information. Use only observable estimates online; retrospective corpse origin and descendant food are training labels, not privileged policy inputs.

**Action:** production split timing/size versus continued foraging, with an explicitly separate emergency escape split. The model must distinguish a low-value birth from a useful replacement. A blind cap threshold cannot make that distinction.

**Value/reward:** official win remains the terminal target. Add diagnostic predictions for external bed food, retained body length, death loss and corpse recovery. Do not reward every split/corpse meal as fresh production or penalize every death equally; those counts can cycle without net value. Compare held-out P/V accuracy and chosen-dose wins, not a training-only reduction in deaths.

**Demonstration:** these ranked top-team traces demonstrate higher turnover and food throughput, not known intent or a verified main-bot identity. Descendant/food links could supply demonstrations after observability checks. Whether throttling or replacement improves our policy requires tester exploration; no learner or bot was built.
