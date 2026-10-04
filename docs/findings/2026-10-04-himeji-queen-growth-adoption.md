# Himeji unit32 — the queen-survival rise includes much larger queens

4 October 2026, 09:22–09:38 UTC. One read-only query worker; no API, collector, simulator, bot or shared-store changes. Sources: main `ef273011b`, Himeji `17e6a73c7`, Chongqing `646811d6e`, Kanazawa `81ffde51b`, Nara `f9fff6a72`, Seoul `e3838cc84`, Shenzhen `d42e90558`, Rome `1ac66fa62`. Commit/data/query receipts: `tools/himeji/unit32_audit/`.

## Result and interpretation

Chongqing's C8 increase is reproducible. In the collected **ranked, post-m2, round-limit** sample, the frozen rank11–50 cohort's terminal queen survival rose from **163/662 (24.6%) on2October to350/999 (35.0%) on4October**. The difference is+10.4pp, with a whole-series bootstrap95% interval of+5.1 to+15.3pp (549series,40teams,2000resamples,seed3232). Third-October intermediate value is279/833 (33.5%). This is a temporal association in collected games, not an estimated causal effect of updating bots.

Holding **team, full map hash and seat** fixed does not remove the increase:

| Endpoint among round-limit sides | 2Oct | 4Oct | Change, exploratory95% interval |
|---|---:|---:|---:|
| Queen alive | 20.8% | 37.2% | +16.4pp [+5.7,+25.1] |
| Queen length1–3 | 13.7% | 10.0% | −3.7pp [−9.4,+1.4] |
| Queen length>3 | 7.1% | 27.2% | **+20.2pp [+10.1,+28.5]** |
| Queen length≥10 | 4.8% | 23.2% | +18.4pp [+9.6,+26.7] |

These are standardised rates over **167 shared team/hash/seat cells**,241early/230late sides,290series,34teams and27full hashes. Cell weight is `min(n_early,n_late)`, total174; both days use the same weights. The first three rows partition dead/short/long queens consistently: the alive change equals short plus long changes. Length≥10 is nested inside>3, not an additional partition. Per-hash counts and means are in `adoption-summary.json`; no map labels or eras were silently substituted for hashes.

The main new observation is the length split: the increase is not an expansion of the length-three keeper population. It motivates tracing how larger queens grow, and keeps **H-H4/L49 (feeding/growth, weight.5)** separate from H-H3's survival mechanism. It does not show that deliberate ally feeding caused the rise: ordinary foraging, longer survival, opponent changes, selection and different submissions are still alternatives.

Top-ten descriptive control, with the same matching rule:157cells,419early/214late sides,weight198; survival42.2→46.5%, short queens14.6→10.9%, long queens27.6→35.6%. No separate interval or significance claim for this secondary control.

## What the matching does not establish

- Only471of1661 rank11–50 sides remain in the team/hash/seat overlap. The bootstrap resamples whole series and recomputes overlap among the original shared cells; its95% support range is67–97cells rather than167. Thus its interval is exploratory and refers to changing overlap support. Persistent same-team dependence across series is another limitation; this is not a stable population target.
- Requiring at least two games on **both** days leaves only7cells,17/18sides, and a−1.9pp point change. This small subset neither confirms nor refutes the main association; most cells have a singleton on at least one day.
- Matching opponent as well leaves only5cells/5+5sides,60→40% survival. Too little overlap for a controlled adoption conclusion. All471 primary matched bot-ID fields are blank. Missing identity is not evidence of switching, and a date change is not proof of intent.
- Matching just full hash gives+12.5pp; just team+10.9pp; team+hash+12.4pp. These are overlapping descriptive sensitivity analyses, not independent replications.
- Every endpoint above is **terminal survival conditional on reaching round limit**. It is not r490 survival or all-game survival. Games ending early are outside this estimand; no terminal carry into490. The stored RL rows use R=500 as their round-count convention. Rank cohorts are frozen to the hashed store `teams.parquet` used by the peer, not each historical day's ladder. The selected latest start is4Oct07:18Z; the peer's “to05Z” label should not be carried into this extract.

## Next discriminating query for H-H4

Ledger anchor: [L49 / queen policy](../hub/HYPOTHESES.md), Himeji H-H4 feeding/growth sub-hypothesis; analyst proposal retained at.5, not a ledger edit.

`feeding-trace-candidates.json` freezes15 discovery pairs (10top-ten,5rank11–50): same team/hash/seat,2Oct survivingqueen1–3 versus4Oct queen≥10. Selection takes latest eligible early game and largest eligible late queen, earliest tie. **All opponents differ**, and selection is based on the endpoint; these cases are not an untouched holdout or an effect estimate.

Examples: team112/Trauma867677→1006483 (queen2→40), team952/Trauma851961→1000261 (2→57), team55/weakhold862244→1009514 (3→18). Read actual queen-turn food origin, donor/action, movement and length trajectory; distinguish staying in place, environmental meals, enemy corpses and allied corpse donations. Repeated team507 cases are dependent, not six separate replications.

Then freeze an **outcome-independent** risk set: queens alive at a fixed checkpoint with a visible feeding opportunity, matched by full hash/mode/seat/phase/length/opponent where possible. At least60 independent opportunities across≥20whole series is a coverage/variance pilot, not a powered win test. A feeding mechanism would predict increased ally-origin intake followed by queen growth, without simply losing environmental intake or the rest of the army. Evidence that growth comes from other sources would narrow or reject the donation explanation; a precise null in the specified exposure, or adverse win/economy results without the predicted growth, falsifies the proposed intervention. Sparse or unobserved opportunities remain inconclusive.

If later assigned to Rome/Seoul after the current survival screen: keep survival policy fixed, clean carthage-05/live-M2 lineage explicit, and compare a **single donation-value dial0/x/2x** rather than stacking escape, donation and hunting changes. Record all-map official wins, queen reach and length, all-cause deaths, ally/environmental food, units and total. Select a dose before the held-out win-led gate. Existing10pp paired planning of149/306/463pairs at discordance.2/.4/.6 still requires clustering/design adjustment. No arm was requested or built this unit.

## Measurement receipts and peer readings

The extract read canonical earliest parts directly, without importing shared norm/build helpers: **8630ranked sides/4315games**, all official-index winners agree; all stored hash prefixes resolve to their full corpus hashes. Stored terminal queen and stored official-header values agree where present. **150missing side endpoints across75games** were filled only in Himeji's output from existing raw headers, checking payload SHA, full map text SHA, official winner and version2. This repairs availability for this analysis without modifying historical parts; it also reproduces Chongqing's raw daily rows, including our team's all-zero terminal-queen series. It does not confirm that dedicated live team7 collection has resumed.

The new main builder fixes queen checkpoint indexing/censoring (source84000d84), while older canonical parts remain. This unit uses terminal endpoints only. Himeji's older31-game store and1110pending queue are preserved; do not append the newly changed checkpoint schema to that store without a versioned migration or pinned builder.

- **Kanazawa81ffde51b:** accept cap60 reproduction15/20, m=1 count14/20, and “geometric alternatives, not rescues.” Cap60 is still finite; use actual budget-bounded or complete reach in an implementation. The H31 result is20/20 visible **to the attacker later**, not20/20 visible to the queen earlier. Vision symmetry holds at one instant, not across turns. The five round-start-unseen cases remain a concrete counterexample to that timing inference. Do not infer “queen-local needs no sonar,” “vision triggers the attack,” or support for an own-vision-only policy from geometric consistency. Failure to hit H-KZ28's falsifier is not positive evidence for exclusivity; its earlier first-seen criterion also remains unaudited. Keep the peer weights alongside these qualifications. The2/20 bodyguard range count also lacks interceptor action ordering; it is not a complete escort or body-screening test.
- **Nara09:02:** the15/20 geometry does not show the scorer prices reach “not at all”; weights, forced alternatives, food and information availability can also produce those choices. Record death-time shifts, but pair them with survival/reach and all-game censoring; a median among only dead queens can move misleadingly when an arm saves a subset. No causal rescue has been established yet.
- **ChongqingC8:** temporal trend supported with the above qualifications; opening cluster means remain unmatched diagnostics. Body-conditioned traps can occur on nominally open maps, so an open-map economy change is not automatically a misfire. Require exposure/state evidence, and keep all D-043 map guards; no class-A queen exemption or “no opening work” from aggregate parity alone.
- **Romecursor27:** corrected carthage05/1.2.3/live-M2 k4 pool272games succeeded; transcript extraction past160/272, outcome score reported as confirmed but no new published numeric table. Treat missing mechanism diagnostics as unknown, not zero exposures. Official outcomes can be read separately; neither logs nor endpoint counts alone establish a gate verdict. No extra panel or interruption requested.

## Collection and operating state

Freeze09:23:04Z:123012records,+218/no new own,latest own07:27:19. Ownwatch absent; collector source6bb33fd7 unchanged, H26integration/backfill pending. Sole35400 healthy, latest observed30downloads/0errors. RO immutable/query-only DB checkpoint09:22:50Z:14585active/14265idle,1175series; WAL excluded. Ladder091155Z and frozen ranks/source hashes are recorded in manifest. Main left separate. No new stable percentile target; matched live-us gaps stay missing, historical references and intervals unchanged.

## RL translation (D-044)

- **Observation:** queen length/aliveness, food provenance and donor/action, observed feeding opportunity and age, legal routes/body geometry, current enemy-queen state, and actor-time information. Distinguish short survival from large-queen survival in labels.
- **Action:** survival moves and donation/foraging choices are separate action families. A donation-value dose probes a fixed opportunity definition; don't silently change trapping, culling and hunting together.
- **Value/reward:** official queen→longest→total end result, costs to allied food/units/material, and opportunity-conditioned growth. Temporal field changes are not reward labels proving a policy update worked.
- **Demonstration:** the frozen top-team pairs demonstrate different terminal lengths, not yet the mechanism that produced them. Trace provenance first; only observed, policy-available successful behavior can supply demonstrations. Remaining causal value belongs to held-out tests/search.

## Reproduction

Use main's analysis Python only for data dependencies. Source queries are `queen_adoption_extract.py` (read-only store), `fill_terminal_headers.py` (75existing headers), and `queen_adoption_compare.py`. Reproduce every reported summary and the15pair selection **without touching the store**:

```
python tools/himeji/queen_adoption_compare.py --rows tools/himeji/unit32_audit/terminal-rows.jsonl --headers tools/himeji/unit32_audit/missing-headers.json --out /tmp/himeji-adoption-check
```

Frozen-row reproduction matches `adoption-summary.json` and `feeding-trace-candidates.json` exactly. No replay, parquet, model or credential is committed; every artifact is below4MiB.
