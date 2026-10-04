# Himeji unit27 — newborn food capture and a corpse-food measurement correction

4 October 2026, 06:52–07:08 UTC. Main21186bf24 read without merging; own parent20d19cef2.
One read-only query worker; no bot, simulator, API, collector deployment or shared-store writes.

## Result and scope

New endpoints on the **frozen unit25 sample**, not independent replication: six ranked14585 Slithery games, each with three frozen top-ten matches at the same full map hash and seat within49.85 minutes. There are18 field slots,17 unique field games,10 teams and five connected series groups; opponents are unmatched and field bot IDs unknown. Two post-m2 hashes are preserved per block. The cohort uses unit25's ladder, not today's changed top ten. Collection selection limits from unit26 apply.

All23 payload hashes, full replay map hashes and official winners agree with frozen metadata; own bot headers are14585. All23 games reach399. Child birth is the split event creating a new ID; a parent is not re-aged when it splits. Young means child age0–9 inclusive. Food uses FRAME7 event provenance, with its `bed` label meaning environmental/non-corpse spawn. No fertility field is recovered from a hidden replay header. Windows are start-inclusive/end-exclusive; action-turn denominators count recorded actions, including fatal ones. Meals of children born in the window are censored at that window's end, not called lifetime totals.

| r250–399 endpoint, equal own-block weighting | Us | Matched field mean |
|---|---:|---:|
| Environmental meals |238.67|362.61|
| Environmental meals eaten by age0–9 children |73.50|160.00|
| Mean young-child share of environmental meals |30.90%|42.29%|
| Young-child share of recorded action turns |10.28%|23.13%|
| Environmental meals / young-child action turn |0.0749|0.0786|
| Environmental meals / older-or-initial action turn |0.0192|0.0315|
| Children born in the window |112.33|258.67|
| Those children eating environmental food before r400 |66.33|107.17|
| Environmental meals taken by those children |154.00|279.83|

The field's young-child environmental-meal advantage is **+86.5**, range+47.7 to+138.7 across six blocks, accounting arithmetically for69.8% of the +123.94 environmental-meal gap. This is an endpoint decomposition, not causal mediation: children inherit positions/body, splits can be responses to food, and parents/other units might substitute if a child were absent. Young-food share is higher in all six blocks (+1.72 to+20.58pp). Young per-turn efficiency has mixed sign (−0.0235 to+0.0257); **exposure volume is more consistent than superior young-unit efficiency**. Older-unit environmental capture per action is also higher in all six field blocks (+0.0092 to+0.0167), so newborns are not the entire gap.

Phase matters: over r0–249, young-child environmental share is **55.34% us versus44.12% field**; field still takes59 more environmental meals but39 fewer through young children. A universal early-production prescription would not follow from the late pattern. Full per-block/hash values and ranges are in `tools/himeji/unit27_audit/newborn-summary.json`. Five connected groups do not support a stable population interval or target here. The24 matched late side slots reproduce unit25's origin counts exactly; no new material-balance discrepancy.

## Correction: template location is not pearl provenance

Shenzhen76e09d6a5 `fountain.py` joins each eaten cell to the authored `maps/live` bed set and calls every other cell a corpse pearl. That proxy is not valid on these public replays. On **exactly the same Slithery sides/window**, it yields mean corpse shares **93.80% us /92.86% field**, while event provenance yields **52.81% /52.88%**. These percentages average side ratios by own block; they are not ratios of the table's aggregate means.

Across all46 unique side-windows (both sides of23 games, including sides outside the matched comparison), the confusion table is:

| Meal provenance from event stream | On template bed | Off template bed |
|---|---:|---:|
| Environmental (`bed`) |2202|14350|
| Ally corpse |1218|16243|
| Enemy corpse |75|1472|

No unknown-origin meals occur in this window. Both error directions exist: non-corpse food outside template beds and corpse food on them. This does **not** revise the peer's whole387-game table to53%; cohorts/windows differ. It falsifies the cell-location classification used to derive its85–99% corpse claim, which needs rerunning with event provenance and mode/hash/series strata.

Independent raw-event control on852617,887284,999613, covering both hashes: positive pearl spawns directly follow `RoundStart`, before any turn or death that round, at off-template-bed cells81/107/44 times in r250–399. Eight concrete examples per replay are committed, e.g.852617 r252 cell(34,26). This check reads raw events, not the decoder's origin label. Thus these cannot be attributed to a contemporaneous corpse drop. It does not certify the template's hidden fertility/timers or reveal why the live spawn distribution differs. H-SZ27's interval-one interpretation also remains unsupported by a cell-location lookup alone.

Finally, gross corpse-meal volume is **recycling**, not new team material production: the same body mass may be eaten repeatedly after deaths. Even a correctly measured high corpse-meal share would not identify the source of terminal length or justify replacing environmental capture with culling. Keep the H25 food/death/paid-sprint mass balance alongside any turnover statistic.

## Hypothesis and test guidance

**H-H7, proposed L36/L41, weight0.4 retained:** near saturation, production children can sustain environmental capture; suppressing production may reduce food as well as deaths. The child-food pathway is now observed in this selected late window. It remains an observational mechanism candidate, not a resolved causal or learning result. Retain H-SZ28/H-SZ29 and the earlier H-SZ26 target/history alongside this qualification.

Tester Rome/assigned lane, after the existing cage-priority screen: keep escape splits unchanged, compare full/half/quarter production eligibility at sensed units≥60, parent dose0=unchanged carthage05 on liveM2. Expected sign: increasing suppression reduces late environmental food; survival/death counts may improve. Use60 shared eligible paired cases for a mechanism/variance pilot (not180 independent observations), report phase, exact hash, environmental/ally/enemy food, age exposure, deaths and material. At paired SD20% or30%, a two-sided5%/80%-power approximation for a10% food effect needs32 or71 independent pairs before clustering; estimate actual variance rather than treating these planning values as guaranteed. Falsifier: a sufficiently precise contrast rules out a10% food cost and fails to support a child-capture pathway; wide nulls/unexposed cases are inconclusive. Only a selected dose proceeds to the full win-led gate. This updates guidance; no arm requested to start here.

For H-SZ28 leakage, count **spawned corpse pearls as the denominator**, link donor/team, and observe each pearl's ally-eaten/enemy-eaten/unconsumed fate at a fixed horizon, with game-end censoring. Consumer meal share alone mixes supply and recovery. Keep environmental source distinct; initial pearls and unknown donor identities stay unknown. This is feature/label guidance for the already proposed hypothesis, not another duplicate query assignment.

## Tester and analyst readings

- **Shenzhen76e09d6a5:** live Slithery template, carthage05-derived C+D parent, unswbc1.2.9, seeds1–3/both seats. Production thresholds60/52 lose reported total19%/28% and environmental meals19%/11%; consistent with H-H7, no win benefit demonstrated. Dose60 is5 sides after a build-race loss;52 is6. Do not claim a monotone paired dose response across unequal fixture sets without a common-five comparison. Wins2/5 versus3/5 and3/6 versus3/6 are too small for a general win-based falsification; this is adverse mechanism-screen evidence, not a full liveM2 gate. The environmental counts in the simulator may have separate provenance; the corpus classification correction does not automatically invalidate those simulator numbers.
- **Carthage12 H-S1, new on main/Seoul1edac66c2:** agree with rejection of the implemented missed-heartbeat portal memory. Parentcarthage05, unswbc1.2.5, historical480pool/744gen sets, not the17-template LIVE_MAPS_M2 zero. Per-transit died3 falls2.7%/1.3%, below25%, while traffic falls24.6%/26.4% and economy lower bounds−.065/−.038 fail. Raw death declines largely track lower traffic. The inclusive transit-round..+3 label spans four round indices; freeze that horizon. This does not falsify every portal-state representation or justify resuming paused training. D-045 is a prospective learned-arm1.2.5 gate, not a revision to historical verdicts or Himeji's simulator permissions.
- **Rome5704a6602/chatcursor18:** cage package seed1 dose1 pool/gen complete, dose3 pool complete/gen past halfway; no full dose table/gate verdict yet. H26 fixed-parent/package attribution guidance delivered, along with this unit's food correction. No extra run or interruption requested.
- **Chongqingb50bbe886:** accept withdrawal of H-C5/H-C6 cull attribution, reference-grade label and acknowledgement that old canonical parts need migration. This closes those disagreements; preserve measured wall shares and frozen references. Conditional death-state reach alone is not a prospective avoidability label, and mixed all-mode us versus rankedtop10 remains unmatched. Its Rome reading must keep19/160 losses separate from live18/90 games or18/45 losses; completed baseline timeouts were resolved, not still missing. Universal “nothing off Schooltime changes” requires source/turn parity because D's sprint policy can act elsewhere.
- **Kanazawad0a3a793b:** accept tail inclusion and reported14/19+12/19 refinement, consumed holdout label and H-KZ11.3. However `q_forced2.py` still assembles occupancy from R[t]/R[t+1], not actual event-time TurnStart: a lower-ID dragon may act before the queen but die later that round, and newly spawned higher-ID bodies may not yet exist at the queen's turn. “Exact” is too strong without proving these cases absent. Request event-stream TurnStart snapshots for affected entries (Himeji `queen_wall_attribution.py` demonstrates the read-only method); do not claim14/19 numerically wrong without that comparison. A legal first/onward cell is not proof a one-step veto saves the queen. Weakhold r30/r45 snapshot timing also needs distinction from official death-event r29/r44. H-H6.5 retained.

## Freshness and reproduction

Collector35400 healthy with0errors, but ownwatch still absent and collector source unchanged6bb33fd7…; H26 patch is merged as a **proposal**, not integrated into runtime. Frozen120799 games at06:56:13Z, +330/0own, latestown03:25:53. Ladder065337Z, top264/306/112/213/55/91/842/507/952/87. Read-only immutable DB checkpoint shows14585active/14265idle06:53:35; WAL excluded. No repeat of the completed coverage census and no fresh live-rate claim. Store31games/62sides+1110pending and historical754 preserved; Chongqing shared51353 is peer-reported. Main builder remains old source ea432824…; no migration/build here.

```sh
python3 tools/himeji/newborn_food.py --repo /Users/alik/Documents/Projects/UNSW-Battlecode-2026 --selection tools/himeji/unit25_audit/mass-flow-selection.json --index /Users/alik/Documents/Codex/2026-10-01/p2-a-analyst-one-claude-opus/work/himeji-unit25/index.jsonl --out /tmp/himeji-newborn
python3 tools/himeji/summarize_newborn_food.py --selection tools/himeji/unit27_audit/mass-flow-selection.json --rows tools/himeji/unit27_audit/newborn-food.jsonl --flow-rows tools/himeji/unit25_audit/mass-flow-flows.jsonl --out /tmp/himeji-newborn-summary.json
python3 tools/himeji/spawn_origin_check.py --repo /Users/alik/Documents/Projects/UNSW-Battlecode-2026 --out /tmp/himeji-spawn-check.json
```

Use main's analysis Python for replay imports; no simulator invocation. Summary reproduction uses committed derived rows only. Source/data hashes, two map hashes and peer query receipts are in `tools/himeji/unit27_audit/`. No stable target or matched opponent-adjusted gap released; all previous references remain frozen.

## RL translation

**Observation:** own child age/birth identity, sensed cap occupancy, food opportunities and congestion can help represent production value. Mask unknown opponent ages and hidden fertility; do not substitute authored bed cells for observed live food. Raw omniscient provenance is an offline label, not necessarily an available policy input.
**Action:** production split frequency and rescue/escape splits are separate decisions; keep dose changes confined to production. Parent continuation and child continuation both matter.
**Value/reward:** train on correctly sourced environmental food, ally/enemy recovery, deaths and net material, alongside official queen/longest/total outcomes. Gross food can count recycled mass repeatedly. Parent-plus-child future food is an outcome label, not a causal action advantage without a counterfactual; retain horizon censoring and whole-series held-out evaluation.
**Demonstration:** these replays demonstrate young-child feeding activity, not optimal extra production. The dose screen supplies intervention evidence; test whether child-age/food features improve held-out P/V before calling H-H7 resolved for learning. Independent later-series evidence awaits collection repair.
