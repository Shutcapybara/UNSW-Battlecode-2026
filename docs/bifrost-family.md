# Bifröst family

Bifröst combines Gavroche V54's supported trade, dive, sparse late-game search,
and crown/endgame policy with portal-exit risk memory from the Scholze V03 and
Witten X01 lines. V01 is the first measured family member; it was submitted as
server v64. Its native six-map panel scored 273–99 over 372 games. That panel
is descriptive and did not test judge CPU limits.

## User-observed matchup issues

These are observations reported by the user. The map and turn details below
are retained as given; replay IDs were not supplied for these cases, so they
have not been independently replay-verified here.

| Map / timing | Observed behavior | Policy question to investigate |
|---|---|---|
| Autarky | Dragons enter pearl-filled dead ends, then split to escape; the resulting growth can be zero, wasting the pearls and length. | Price a dead-end harvest against its required escape split and likely surviving length. Avoid choosing a farm when the net material gain is negligible. |
| Default, turn 63 / round 4 | A dragon moves beside a smaller enemy and gives it an opportunity to suicide for a net gain to the opponent's team. | Recheck early adjacent-head choices against suicidal or intentional-trade responses, including how the death benefits nearby enemy units. |
| Prisoner's Dilemma | Similar dead-end farming. Sometimes a sacrifice could be net-positive, but the split leaves a two-segment escapee while the larger remainder dies. | Compare split orientations and segment allocations. When the head is trapped, test shedding two segments as the sacrifice while the larger tail section escapes. |
| Devil | Dragons circle low-impact cells with little pearl income and no important territory to defend. | Detect repeated low-value routes and weigh fresh resource areas or contested territory more strongly. |
| Queen of Spades | After using the blue portal, a dragon reaches a high-value pearl area but splits into a congested group and loses value to deaths. In another case a length-six dragon split 3/3 although the left branch was certain to die; 2/4 would have been better. | Make production contingent on local space and resource value; score split direction, branch survival, and resulting length balance rather than relying on a fixed child size. |
| Slithery Flight | A dragon remains stuck in a narrow corridor, blocking the route without dying or splitting enough to escape. | Detect corridors with no safe continuation and choose an escape split before repeated moves trap the body. |
| Trophy | Dragons take similar opening routes and claim little territory, letting the opponent gather pearls and outgrow them. | Diversify opening targets by unit identity and coordinate, and measure early area/resource coverage rather than just safe movement. |

These observations make split safety and early map coverage first-class
family issues. They also show that a split can be both a survival action and a
resource transfer: score the material that survives, not only the action's
immediate legality.

## Losses in the focused V01 control

The six-map V01 control scored 43–5 on 48 fixtures against Gavroche V54, Avery V09, Hydra V01 and Godel X02. Its five losses were three on Devil, one on Prisoner’s Dilemma and one on Trophy. Replay review shows a sharp compact-map growth and territory gap:

| Loss | Bifröst result | Opponent result |
|---|---|---|
| Devil vs Gavroche V54, round 213 | 0 units; 63 pearls; 27 splits | 39 units; 515 pearls; 207 splits |
| Devil vs Avery V09, round 500 | 1 unit / length 8; 79 pearls; 5.9% space | 8 units / length 36; 1,333 pearls; 94.1% space |
| Devil vs Godel X02, round 313 | 0 units; 99 pearls; 38 splits; 33 head-to-head deaths | 62 units; 1,026 pearls; 399 splits |
| Prisoner’s Dilemma vs Gavroche V54, round 172 | 0 units; 44 pearls; 21 splits; 11 wall deaths | 9 units; 119 pearls; 48 splits |
| Trophy vs Gavroche V54, round limit | 1 unit / length 12; 331 pearls; 111 splits | 10 units / length 16; 528 pearls; 151 splits |

These are native replay outcomes, not evidence that a particular death was deliberate. The complete [matched control report](../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md) and [replay diagnostics](../experiment_data/bifrost-v01-portal-memory_20260927121857063579/loss-review/) and the [V54 Devil review](../experiment_data/bifrost-v01-portal-memory_20260927121857063579/loss-review-v54/) preserve the underlying data.

## Iteration record

- **V01 — portal memory:** baseline benchmark at
  [`experiment_data/bifrost-v01-portal-memory_20260927104358397848`](../experiment_data/bifrost-v01-portal-memory_20260927104358397848/summary.md).
- **V02 — crown banking:** rejected after a 120-game focused screen (77–43).
  On 108 common fixtures against the same nine opponents, V01 scored 88–20
  and V02 scored 73–35. It swept Avery V08 but regressed against V01 and the
  active Gavroche V54 control. See
  [`experiment_data/bifrost-v02-crown-banking_20260927114128240310`](../experiment_data/bifrost-v02-crown-banking_20260927114128240310/summary.md).
- **V03 — expanded late feeding:** rejected. It scored 72–48 overall, including
  a 3–9 loss to V01. Across 108 shared external fixtures, all seeds matched:
  V01 won 88 and V03 won 69. V03 gained 8 results but regressed on 27 V01
  wins. The wider feeding range is not retained. See
  [`experiment_data/bifrost-v03-expanded-feeding_20260927115819514324`](../experiment_data/bifrost-v03-expanded-feeding_20260927115819514324/summary.md).
- **V04 — net-growth farms:** rejected. Its 60-game screen scored 36–24 and
  went 5–7 head-to-head with V01. On 48 shared external fixtures with the same
  seeds, V01 scored 43–5 and V04 scored 31–17: one gain and 13 regressions.
  The rule helped on Prisoner's Dilemma but hurt Autarky and Queen of Spades.
  See [`experiment_data/bifrost-v04-net-growth-farms_20260927121518462201`](../experiment_data/bifrost-v04-net-growth-farms_20260927121518462201/summary.md)
  and the matched [V01 control](../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md).
- **V05 — population-aware production:** rejected. It scored 36–24 and lost
  3–9 head-to-head against V01. On the 48 shared external fixtures, V01 scored
  43–5 and V05 scored 33–15; V05 gained one and regressed on 11. The broad
  team-size cap hurt despite sweeps over Avery V09 on Autarky, Dilemma and
  Trophy. See [`experiment_data/bifrost-v05-population-aware-production_20260927122158858320`](../experiment_data/bifrost-v05-population-aware-production_20260927122158858320/summary.md).
- **V06 — local split crowding:** rejected. It scored 32–28 and lost 3–9 to
  V01. On the same 48 external fixtures, V01 scored 43–5 and V06 scored 29–19
  (two gains, 16 regressions). It failed to improve Queen of Spades and lost
  broadly on Autarky and Default. See
  [`experiment_data/bifrost-v06-local-split-crowding_20260927122649557512`](../experiment_data/bifrost-v06-local-split-crowding_20260927122649557512/summary.md).
- **V07 — stronger anti-dither:** rejected. It scored 36–24 and lost 4–8 to
  V01. On 48 shared external fixtures, V01 scored 43–5 and V07 scored 32–16;
  V07 gained zero results and regressed on 11. Raising the global visit penalty
  hurt Autarky and Queen of Spades without a Devil gain. See
  [`experiment_data/bifrost-v07-stronger-anti-dither_20260927123050410233`](../experiment_data/bifrost-v07-stronger-anti-dither_20260927123050410233/summary.md).
- **V08 — opening sector spread:** rejected. It scored 37–23 and lost 5–7 to
  V01. On 48 shared external fixtures, V01 scored 43–5 and V08 scored 32–16;
  V08 gained zero and regressed on 11. It won the two direct Trophy fixtures,
  but lost elsewhere often enough to reject the broad compact-map bonus. See
  [`experiment_data/bifrost-v08-opening-sector-spread_20260927123457377306`](../experiment_data/bifrost-v08-opening-sector-spread_20260927123457377306/summary.md).
- **V09 — shorter-enemy trade safety:** rejected. It scored 33–27 and lost
  4–8 to V01. On the same 48 external fixtures, V01 scored 43–5 and V09 scored
  29–19; V09 gained zero and regressed on 14. The extra threat cost did not
  improve Default results. See
  [`experiment_data/bifrost-v09-shorter-enemy-trade-safety_20260927123913152596`](../experiment_data/bifrost-v09-shorter-enemy-trade-safety_20260927123913152596/summary.md).
- **V10 — arrival-ready beds:** rejected. It scored 1–59 with no errors and
  lost all 12 direct games to V01. Witten X03's `bed_wait=0` rule depends on
  its other bed-cycle logic and does not transfer as a standalone change.
  See [`experiment_data/bifrost-v10-arrival-ready-beds_20260927124438424001`](../experiment_data/bifrost-v10-arrival-ready-beds_20260927124438424001/summary.md).
- **V11 — compact-map territory aggro:** rejected. It scored 36–24 and lost
  3–9 to V01. On the 48 shared external fixtures, V01 scored 43–5 and V11
  scored 33–15 (two gains, 12 regressions). It gained one Devil result against
  Godel and one Trophy result against Gavroche, but lost both Hydra Dilemma
  games. See
  [`experiment_data/bifrost-v11-compact-territory-aggro_20260927124937481171`](../experiment_data/bifrost-v11-compact-territory-aggro_20260927124937481171/summary.md).
- **V12 — multi-head threat cost:** rejected. It scored 35–25 and lost 3–9 to
  V01. On 48 shared external fixtures, V01 scored 43–5 and V12 scored 32–16;
  V12 gained zero and regressed on 11. See
  [`experiment_data/bifrost-v12-multi-head-threat_20260927125442323133`](../experiment_data/bifrost-v12-multi-head-threat_20260927125442323133/summary.md).
- **V13 — compact contested-resource value:** rejected. It scored 38–22 and
  lost 4–8 to V01. On 48 shared external fixtures, V01 scored 43–5 and V13
  scored 34–14 (two gains, 11 regressions). It swept Avery on Devil and Trophy
  but did not improve the broad panel. See
  [`experiment_data/bifrost-v13-compact-contested-value_20260927125904217355`](../experiment_data/bifrost-v13-compact-contested-value_20260927125904217355/summary.md).
- **V14 — proactive corridor rescue:** rejected. It scored 34–26 and lost
  4–8 to V01. On 48 shared external fixtures, V01 scored 43–5 and V14 scored
  30–18; V14 gained zero and regressed on 13. The broad rescue trigger hurt
  other maps, and Slithery Flight was not available for a direct test. See
  [`experiment_data/bifrost-v14-proactive-corridor-rescue_20260927130543949170`](../experiment_data/bifrost-v14-proactive-corridor-rescue_20260927130543949170/summary.md).

These comparisons use fixture-hash seeds to repeat pearl layouts and
opponent/map/side combinations. The runner notes that native execution does not
repeat bots' own random streams. In this focused panel, however, the repeated
V01 control scored 43–5 both times and all 48 outcomes matched exactly; see the
[second control report](../experiment_data/bifrost-v01-portal-memory_20260927130948614175/summary.md).
This provides a stable baseline for the candidate results on these fixtures.

- **V15 — compact bed timing:** rejected. The 60-game screen scored 35–25
  with no errors, but went 3–9 against V01. On the 48 identical external
  fixtures, V01 scored 43–5 and V15 scored 32–16: V15 gained two results and
  regressed on 13. The map results were particularly poor on Queen of Spades
  (3–5); shortening the predicted-bed wait from 12 to 6 on compact maps did not
  solve the portal congestion issue. See
  [`experiment_data/bifrost-v15-compact-bed-window_20260927131401130593`](../experiment_data/bifrost-v15-compact-bed-window_20260927131401130593/summary.md).
- **V16 — empty-route repeat penalty:** rejected. The 60-game screen scored
  36–24 with no errors and went 4–8 against V01. Across the 48 matched external
  fixtures, V01 scored 43–5 and V16 scored 32–16, with zero gains and 11
  regressions. Devil stayed even with the control at 5–3, while Queen of Spades
  regressed to 3–5. The early repeat trigger was too broad to improve the
  reported low-impact circling. See
  [`experiment_data/bifrost-v16-empty-route-repeat_20260927132057316691`](../experiment_data/bifrost-v16-empty-route-repeat_20260927132057316691/summary.md).
- **V17 — sustained empty-route repeats:** rejected. It scored 36–24 and went
  4–8 against V01, exactly matching V16's 32–16 record on the 48 shared
  external fixtures. Its per-map results were also identical, including no
  Devil gain. Raising the revisit threshold did not address the issue. See
  [`experiment_data/bifrost-v17-sustained-empty-repeats_20260927132523938820`](../experiment_data/bifrost-v17-sustained-empty-repeats_20260927132523938820/summary.md).
- **V18 — moderate compact contested-resource value:** rejected. It scored
  36–24 overall and went 3–9 against V01. On the shared external panel it
  scored 33–15 against V01's 43–5, gaining one result and regressing on 11.
  The intermediate 0.72 enemy-reach value did not recover the Queen of Spades
  regressions. See
  [`experiment_data/bifrost-v18-moderate-contested-value_20260927133008858921`](../experiment_data/bifrost-v18-moderate-contested-value_20260927133008858921/summary.md).
- **V19 — combined compact territory contest:** rejected. It scored 35–25
  overall and went 3–9 against V01. On the 48 shared external fixtures, V01
  scored 43–5 and V19 scored 32–16, with one gain and 12 regressions. Combining
  the V11 and V13 changes did not add to their separate Devil/Trophy gains.
  See
  [`experiment_data/bifrost-v19-combined-territory-contest_20260927133408285723`](../experiment_data/bifrost-v19-combined-territory-contest_20260927133408285723/summary.md).
- **V20 — compact-map teacher ranker:** focused screen in progress. It gates
  Loki's learned Bifröst action-ranking bonus to maps up to 625 cells. In the
  matched external panel, Loki v01 gained on Devil and Prisoner's Dilemma but
  lost on Autarky, Default, and Queen of Spades; this gate retains the first
  profile while preserving V01 behavior on larger maps.

Experimental versions remain separate from the submitted V01 candidate until
a paired screen shows a broad gain without losing the important map behaviors.
