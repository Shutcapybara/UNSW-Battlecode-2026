# Himeji unit17 — Rome04 cannot test early survival; pocket prevention has an earlier window

4 October 2026,02:08UTC. Primary work: tester-result interpretation and H-H3 precursor falsification. H-H1/H-H3 weights remain0.5. Local panels, live ranked and live unranked remain separate.

## Rome04: the preregistered endpoint precedes the intervention

Read-only source comparison finds exactly one policy change: `role_crown && split > len-split` becomes `>=` (policy.hpp718). Both paths that set role_crown true are gated at **r>=250** (548–568); the variable starts false and has no other assignments. Therefore this change cannot improve **r150** queen survival. Flat r150 survival is a pre-treatment parity check, not a falsification of H-H1.

This also changes **all crowns**, not only original queens. The type7 inheritance receiver checks `parent != me` and recent birth before setting inherit_pending (464–473), i.e. the packet targets a new split child. Engine queen identity stays with the original parent/head, as established in H16. Thus label this a late crown-to-child equal-split handoff contrast; do not equate it with retaining more queen head material. The parent already uses length−2 on the relevant escape split, leaving no additional legal head-allocation contrast at length4. H-H1's original proposed allocation intervention is not implemented by04. More trials of the same mistimed endpoint cannot repair that mismatch.

I sent Rome the source timing issue and a tuple-unpacking fix in its analysis script. Rome acknowledged the timing issue and is inspecting post250 events. That new endpoint is an **exploratory correction**, not a retroactively preregistered success criterion. Request crown identity at actual equal-split handoff, original queen ID involvement, receiver and pre/post intervention outcomes; simply counting every queen2+2 split overstates treatment exposure.

Independent paired read of saved FRAME7 features:

| Local1.2.3 panel | Pairs | Parent W–L–D |04 W–L–D|Score change, pp (95% block interval)|r150 queen alive / reached, both arms|
|---|---:|---|---|---|---|
|Pool|480|396–83–1|390–90–0|−1.354 [−3.125,+0.417]|95/423|
|Gen|1392|1036–356–0|1036–356–0|0 [−0.503,+0.503]|244/994|

No paired r150 queen-survival differences. All12 tested opening columns (pearls/units/total/births at50/100/150) are identical fixture by fixture in both panels.57pool/398gen games end before150 and are censored for conditional survival; all-fixture survival counts use no invented future queen state. Queen ID chosen as lowest initial ID per side, keeping that row's death field intact.

Nineteen pool scores differ:14Portals,1Slithery,4Trauma; net−6.5 expected-score points. Portals alone contributes−5.5 (−11.458pp on48pairs). Gen has10changed scores despite a zero aggregate delta:8transformed-Portals,1commons-spread and1transformed-Trauma. Zero aggregate is not behavior parity. Intervals use5000 bootstrap draws over map/opponent/seat blocks (160pool,464gen), descriptive fixed-panel uncertainty. Thirty-two official replay-header spot checks agree with cached outcomes (first8rows per arm/panel); this is not a3744-header census. Feature/index/source hashes and1872paired rows are pinned.

**Reading:** the published scorecard fails its gate; no positive performance evidence or adoption case. The pool interval includes zero, so this is not a statistically established universal win regression. Do not mark early H-H1 falsified from r150. The next diagnostic is actual late handoff exposure, which Rome is already doing; no duplicate panel or new arm here.

## H-H3: food on the first step defeats the shrinking sprint

Raw event-time reconstruction of the four selected late failures (threegames:2ranked/1unranked) checks exact TurnStart occupancy, pearl state and earlier split/death events. This is an outcome-selected mechanism audit, not a field rate.

| Game / queen | Turn before growth: own units / food-free two-step route | Growth turn: units / only empty first step | Fatal next turn: units |
|---|---|---|---:|
|996984 /0, ranked|r323:63 /NE (also r322:64 /WN)|r324:64 /E holds a new pearl|64|
|997644 /0, unranked|r266:64 /NE|r267:63 /E holds a new pearl|64|
|997644 /1, unranked|r266:64 /NW|r267:63 /W holds a new pearl|64|
|998186 /0, ranked|r318:62 /NE|r319:62 /E holds a new pearl|62|

Each preceding turn has a food-free route; at the growth turn, the only initially unoccupied step contains the pearl. The64-unit gate would have been true with a safe path in an earlier observed turn for all three cap-blocked queens, but not the below-cap fourth case. Cap counts can change between turns, so checking only the eventual fatal count hides the earlier decision window. Two queens share one unranked game; four rows are not four independent series.

Two small fixed-action checks in isolated unswbc1.2.3 confirm the missing edge case, seed117, identical64-unit length3 pocket geometry:

- Empty first step, MOVE WN: queen reaches next turn atlength2, charged one segment.
- Pearl on first step, MOVE WN: consumes pearl, becomeslength4, then **self-collides on step2 without a segment charge**. No successful shrinking rescue once that meal fills the pocket.

The empty-case queen deliberately terminates at r1; this is a turn-legality check, not endgame survival or a bot experiment. Fixture observations expose the distinction: tile `2 2 0 -1` versus `2 2 1 1`; the7×7 observation also includes this entire pocket's body and walls. This demonstrates local visibility in the fixture. Public live replays do not preserve the precise bot input/countdown, so actual live knowledge of future spawn timing remains unknown. Do not substitute authored fertility or hindsight. No replay binary committed.

### Refined test card

**H-H3 / proposed L24/L49, weight0.5:** test a single observable preventive action while length3, local four-cell geometry and a food-free two-step route are verified, and capacity is at its limit. Spending one segment before saturation can maintain a spare cell; attempting that action after food occupies the only exit fails the edge-case check. Use only current known state; a timer-based refinement must first prove timer availability. This is not a universal length2 target: a shorter surviving queen can lose a tiebreak. The below-cap fourth failure remains a separate legal-choice problem.

**Falsifier/controls:** illegal or stale-observation route, failure despite pre-growth exposure, or paired wins/economy/hygiene failing predeclared guards. Include food-on-first-step as a required negative, blocked/unknown paths, below-cap and open-component controls. At least60 independent late-exposed fixture pairs; zero legality failures gives a one-sided95% upper bound4.87%, not proof of a small win benefit. For10pp paired binary gain, planning149/306/463independent pairs at discordance.2/.4/.6 before cluster inflation. The current2engine cases and3live games do not meet those sample requirements. Tester: Rome after its current diagnosis or a director-assigned free tester; H-H4feeding and H-H5fallback remain separate.

## Analyst replies and data freshness

Nara a67b1aef7's Autarky/proposal concessions and f8ae877e4's fertility acknowledgment accepted. Its new L47 slice reports526/634 PD-opening and6996/12233 Portals-late “regret” events. Read the query before treating those as restraint opportunity: kept material sums only parent+immediate child, omitting their later descendants; horizon is min(r+10,last round), mixing complete and truncated observations. Mode/series are not in its output. Request descendant accounting, complete-horizon/censoring, mode/series joins and series-level uncertainty before interpreting field percentages. Chosen-death attribution alone cannot fix these denominators; parent-death plus material-loss is observational, not a no-split counterfactual. Nara owns this analysis; Himeji did not rerun its cohort.

Freeze01:53:15Z:117879games (+468,0new own), latest01:51:48Z; ladder014638Z top264/91/306/213/566/952/55/842/87/507. Solecollector35400 healthy40per recentpass,0errors; DB read-only connection succeeds,14585active/14265idle lastseen01:46:37Z. No competing collection, credentials/API/source/deployment changes.

Versioned FRAME7 store533→663games,130new/0errors in162s withoneworker;1326side-results agree with official index.459ranked/204unranked,allpost123cutoff1Oct06:00Z; latestdecoded4Oct01:45:11Z,18maplabels. Currenttop10sides680/own21 include previously pending games, not9new-live-own games this wake. Metadata now frozenunit17's117879 rows.399selectedgames remain; resume this same immutable snapshot next wake before selecting anew. No worker remains running. Oldstores/norms unchanged; no stable field percentiles or matched live-us gaps invented. H-H2switching remains unresolved, with no new identity-matched regime evidence.

## Reproduction

Own tools (read-only unless writing SCRATCH/ownstore):

```text
python tools/himeji/rome04_reading.py --repo MAIN --rome WT_ROME --out SCRATCH/rome04-reading.json
python tools/himeji/pocket_precursor.py --repo MAIN --prior tools/himeji/unit14_audit/pocket-failure-traces.json --index SCRATCH/index.jsonl --out SCRATCH/pocket-precursor.json
ISOLATED_123_PYTHON tools/himeji/pocket_food_step_check.py --repo MAIN --tools tools/himeji --out SCRATCH/food-legality
python tools/himeji/store_coverage.py --store OWN_STORE --out SCRATCH/store-coverage.json
```

MAIN=/Users/alik/Documents/Projects/UNSW-Battlecode-2026; WT_ROME=/Users/alik/Documents/Projects/wt-rome;
SCRATCH=/Users/alik/Documents/Codex/2026-10-01/p2-a-analyst-one-claude-opus/work/himeji-unit17;
ISOLATED_123_PYTHON=../himeji-venv/bin/python relative toSCRATCH. Main analysis Python handles decoding only.
Compact evidence/source hashes `tools/himeji/unit17_audit/`. Future pocket_holdout.py no longer filters by invalid bed-absence inference; historical manifests/results remain frozen. The slow full-header reread was stopped without outputs and replaced by the explicit32-header preflight, not reported as completed. No bot built, run or changed.
