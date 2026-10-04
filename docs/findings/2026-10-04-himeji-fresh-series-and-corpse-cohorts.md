# Himeji unit28 — fresh ranked series, corpse cohorts, and an entry trace

4 October 2026, 07:39 UTC. Ten newly collected ranked games verify two 5–0 series for carthage-05-free-sprint (14585). All four round-limit wins used longest-dragon fallback with both queens dead. A separate measurement audit finds that Shenzhen's corrected corpse-origin query still mixes birth and meal cohorts. Neither result releases a new field target. H-H6 entry-risk and H-H7 productive replacement remain live hypotheses, with tests below.

## Population, collection and reproducibility

Frozen index at07:23:44Z:121313 games, +514 since unit27, including10 own games; latest own start06:35:02Z. Sole collector35400 healthy/zero reported errors. All ten were watched through opponents939/98. Ownwatch remains absent and corpus source still removes team7: **H26-02 integration/backfill request remains open**. New arrivals do not certify complete own collection. Read-only immutable/query-only DB, excluding WAL, reports14585 active/14265 idle at07:15Z and1165 cached series/latest06:42Z. No API call, collector/config/executor change, or main-source write in this unit.

Ladder071500Z: team7 rank75/Elo1720,939 rank84/1682,98 rank78/1708. Frozen top ten264/306/112/213/55/91/507/842/952/566. Opponents are not top-ten controls; all ten opposing replay submission identifiers are blank. No switching or intent inference; H-H2 unresolved. Read sources main21186bf24, KZ4aca2103c, SZa1d088d33, CQb50bbe886, Naraa884062ea and the other unchanged lane statuses. Rome advanced5704a6602→b926cdf64 during the unit; its final finding is read below. Full commits, source hashes, data hashes and cursor are in `tools/himeji/unit28_audit/manifest.json`.

All ten replay SHA256s, full map-text hashes, version2 headers and official winners verified; twenty terminal queen checks agree. Query rows retain full hashes, series, seat and mode. Rules era is post-1.2.3; map references use exact hashes in the post-m2 window, never pooled old/new-map rates. This mixed-map two-series selection is a measurement sample, not a map/cluster benchmark. No defensible series-level population interval from two selected series; rates below describe these games only. Historical references and intervals remain frozen; matched live-us gaps remain NA. Stores31games/62sides+1110 queue and historical754 unchanged; shared51353 only peer-reported.

Reproduce from the Himeji worktree with main's decoder environment (no simulator, shared norms or store build):

```sh
PY=/Users/alik/Documents/Projects/UNSW-Battlecode-2026/.venv/bin/python
MAIN=/Users/alik/Documents/Projects/UNSW-Battlecode-2026
$PY tools/himeji/corpse_cohort_check.py --repo "$MAIN" --metadata tools/himeji/unit28_audit/new-own-metadata.json --out /tmp/himeji-u28-cohorts.json
$PY tools/himeji/summarize_corpse_cohort.py tools/himeji/unit28_audit --out /tmp/himeji-u28-summary.json
$PY tools/himeji/queen_corpse_case.py --repo "$MAIN" --out /tmp/himeji-u28-case.json
```

The existing `recent_live_check.py` produced committed20 side rows and official outcome summary from the frozen index minus unit27 game IDs. That large selection index stays in local `work/himeji-unit28/`; the ten selected metadata records with replay hashes are committed, so the chosen games are reproducible independently of later downloads. Its `era=post` denotes rules, not a pooled map-era target. Derived checkpoint values use the existing start-of-round490 contract with actual reach, not terminal carry. One query worker at a time, all complete. Summary reproduces exactly; no bots/models/experiments built.

## Fresh official outcomes and denominators

| Series opponent / own seat | Games | Official W–L | Reached490 / own alive | Early-end censoring | Round-limit verdicts |
|---|---:|---:|---:|---:|---|
|939 / A, b9d7c969… at06:26Z|1021318–1021322|5–0|2 / 0|3|Maze and weakhold: longest|
|98 / B, 1b72e6e0… at06:35Z|1021809–1021813|5–0|2 / 0|3|Australia and Portals: longest|

All ten original queens died; early-ended games have no observed490 length. **Queen-decided loss share is0/0, undefined**, because there are no losses. It is not a new0% loss reference. Round-limit losses with a material lead divided by round-limit losses is likewise0/0. Conditional on our total-length lead among these four round-limit games, losses are0/1 at490 and0/2 at terminal; these tiny counts support no target.

| Round-limit map / game | Our / their total490 | Our / their longest490 | Our / their total end |
|---|---:|---:|---:|
|Maze1021319|88 / 97|63 / 53|102 / 96|
|weakhold1021321|71 / 4|21 / 4|55 / 7|
|Australia1021810|100 / 238|27 / 13|51 / 242|
|Portals1021813|38 / 63|29 / 21|34 / 56|

Three of four wins were behind in total at490, two remained behind at terminal. Longest fallback remains important when both queens die; this neither refutes queen keeping nor proves a strength change. Do not merge these opponents with top-team mechanisms or refresh H20's frozen18/45 queen-loss estimate without a new eligible population and intervals.

## Corpse recovery must follow one birth cohort

Accept Shenzhen's unit12 withdrawal of the template-cell85–99% corpse claim and H-SZ27 dismissal. Event origins fix that error. The new `corpse.py` still divides meals eaten at r≥150 by corpse pearls **created** at r≥150. Old corpses consumed later are in the numerator only. This can exceed100%: fresh Autarky1021322 sideB has24 late births but25 loose recoveries (3 ally+22 enemy); two enemy meals were born149/eaten153 and155. Correct same-birth-cohort recovery is23/24. Default1021318 B similarly gives62/61 loose versus57/61 aligned.

Across all20 sides,74 carry-in meals affect14 side-games (64 ally,10 enemy). Late births4105; loose ally/enemy3511/473 becomes3447/463 after restricting birth≥150. Own ten sides:2228 births,1959/202 loose becomes1918/198 aligned;45 carry-in. These are accounting totals across different maps, **not pooled strategy rates or a recalibration of Shenzhen's463-game cohort**. The original leakage direction remains an open hypothesis, not globally disproven by this counterexample.

For a reproducible follow-up label, select corpse births150..min(399,R−20) and follow each for20 elapsed rounds, event age≤20 (inclusive age0..20 spans21 integer labels). Record ally, enemy, or not eaten by20. There are3097 fully followed births:2487 ally,349 enemy,261 not eaten by20; own1665:1386/132/147. All donor/round/cell keys unique; fate sums equal births. This complete-follow-up subset excludes births too close to termination; report those separately in a population analysis rather than silently treating them as lost. `Unconsumed_by_end` is an accounting residual, not proof the pearls remain physically present.

H-SZ28 should be re-estimated on donor-spawn cohorts, separate map hashes/mode/phase and series uncertainty. H-SZ30 spawn-to-eat latency needs **all eligible environmental spawns**, including uneaten/terminated and competing-team captures; consumer-only mean age selects the successful meals. Equal endpoint economy on Portals cannot by itself rule out an economic pathway to wins. Preserve the peer targets alongside these qualifications until their own cohort is re-run.

## Fresh weakhold trace: entry after a child's death

Game1021321, hash9c3aa9986574cab5df8c60b5a6bd2ac5514ff8e5cb72a76d5725cca212aaee24, ranked14585 sideA. Queen1 enters the three-cell corridor at r40, (29,14)→(28,14); official wall deathr44. At the actual queen TurnStart, north is its body, south wall, east(30,14) empty, west the chosen pocket. This verifies an alternative empty first step only—not a safe multistep route or counterfactual rescue.

Child9 was bornr11 fromparent5 with body(30,14),(29,14), **entirely outside the pocket**. It died on a wallr20 at(26,14), age9/length3. At round-start40 the pocket holds two corpse pearls from this child and one environmental pearl bornr21. Thus this particular child later entered the pocket; corpse food is not its only attraction, and ancestry does not identify why the queen chose the move. The case overlaps Kanazawa's fresh3/3 list, so it is an audit of the same evidence, not independent replication.

Kanazawa4aca2103c's withdrawal of “exact” for q_forced2 is accepted; its38-entry event-time audit remains theirs. H-KZ22 cannot be generally falsified merely because all13 donor ages exceed3: check birth geometry for each. This trace supplies one such check. H-KZ21 death-site memory must distinguish known observed ally death from unknown provenance; “not seen as an environmental spawn” is not proof of corpse origin. Actual policy visibility and memory delivery remain unverified here.

Retain **H-H6 proposedL24/L49, weight.5** (observable entry-risk avoidance) and **H-H7 proposedL36/L41, weight.4** (productive replacement), with prior falsifiers and test sizes. No new weight from a selected overlapping case. Suitable tester Rome/assigned lane, parent0carthage05 onLIVE_MAPS_M2. H-H6 geometry doses0/4/8/16 with fixed body/cycle/unknown semantics: expected fewer sealed entries/queen deaths, food/units/longest costs measured;60 shared eligible paired pilot, selected dose then held-out win gate. For a separate H-KZ21 memory mechanism, suggested TTL0/10/30, same parent and fixed geometry, only observed death information; do not bundle both mechanisms. Falsifier is no precise targeted-risk benefit or negative overall win, not an unexposed or wide null. Prior10pp paired-win planning149/306/463 at discordance.2/.4/.6 precedes series clustering. H-H7 food-cost planning32/71 independent pairs at20/30% paired SD for10% effect remains provisional, followed by selected-dose win gate; no arm launched.

## Tester reading within this unit

Rome b926cdf64: carthage05 parent, unswbc1.2.3, LIVE_MAPS_M2 seed1 both seats,272 pool/464gen per dose. Accept **HOLD/no stack**: pool wins226/229/224 for0/1/3, Schooltime14/16/15 of16 and reached/alive16/0,12/11,13/13. Report joint11/16 and13/16 as well as reached fractions; changing reach is part of the response. Dose1's better win count versus dose3's better survival is not a monotone win benefit. Invalid-death rate0→8.07/8.11 per1k turns on pool is a real side effect; use cause-inclusive mortality as well as category shifts. Current/unflagged gen wins288/292/294 of400; four stale twins64games remain historical,61wins each. Missing open4 Schooltime/PD10 variants are not transfer evidence. This is a package0 vsC+D+E1/E3 screen, not an E-specific curve; fixedC+D/E0 and a separately defined conditional reserve remain sensible attribution work. Regime-specific win rates condition on a treatment-affected outcome (elimination/RL); do not interpret them as paired causal subgroup effects without common fixture groups. Full gate/seed2–3 still needed. Direct early handoff delivered; final reading posted on board.

## D-044 learning translation

- **Observation:** directed terrain capacity, current body occupancy and legal alternatives, queen identity/length, cap state, and observed death-site age/provenance with an explicit unknown flag. Future death, corpse donor ancestry unavailable to the bot, and end-of-round states after its action are labels only.
- **Action:** rank legal exits; optionally avoid a known hazardous corpse site for a dose-controlled time. Keep rescue split, production and memory mechanisms separate. Unseen-origin pearls cannot be masked as known corpses.
- **Value/reward:** future cause-inclusive queen survival/sealed state with explicit horizon and censoring; official team win, longest/total and food costs. Spawn-cohort competing recovery and capture latency are auxiliary labels, not additional created material or substitutes for win value.
- **Demonstration/exploration:** the fresh trace and Kanazawa entries identify candidate failures, not validated safe alternatives. Hold out whole later series/map hashes, include nonfatal/unknown-origin controls, and test feature removal/direction permutation. The Rome Schooltime response supplies a mechanism screen; its reserve/global policy is not established by top-team demonstrations. No learner or bot was built.
