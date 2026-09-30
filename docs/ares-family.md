# Ares family

Ares is a C++ research family built from the Anna protocol-3 chassis. It copies anna-a02-chassis into its own versioned directory and does not modify the Anna control.

## V01 — safe launch routing

The ares-v01-safe-launch-routing snapshot keeps Anna's time-aware movement model and adds four switchable behaviors:

1. Routine splits wait for a known nearby resource and a clear child site.
2. A trapped escape split chooses the largest viable rear child rather than always shedding two segments.
3. A small identity bonus breaks opening target ties; one in three dragons mildly prefers a known paired-portal route.
4. A recent same-pair return is softly discouraged near the remembered exit.

The target and crowding conditions follow the newborn-death and small-dragon crowding measurements in the efficiency ledger. The emergency split responds to the wall-step replay and the repeated dead-end split observations. The target tie-break borrows Tyr V12's positive-only lane idea, but leaves the route objective primary: Bifröst's broader opening-sector and route-ownership changes often regressed outside their target maps. The portal cost borrows Bifröst's exit-memory direction and Tyr's room-return work while avoiding a hard portal ban; the field measurement found portal safety, rather than transit volume, is the issue.

Tyr V12 is a useful matchup reference, not the all-map Ares parent: its 50–42 all-map result versus Yuna V05 had a strong seat split and remaining sandbox faults. Fenrir V20 remains the top measured all-map frontier candidate in FRONTIER.md. Heimdall V10's broad panel success also supports the value of spatially informed routing, but its echo-role design is not copied into this single-process C++ policy.

## V01 benchmark result

The completed seed-1 panel used unswbc 1.2.1: 8 opponents × 10 live maps × 2 seats (160 Ares games and 160 Anna control games), plus 20 direct Ares–Anna games. All 340 replays extracted successfully. The scorecard applies the saved per-map field medians and field distributions in docs/analysis/benchmarks; the raw field corpus was not present to regenerate them. Table values are medians across 160 side-games.

| Metric | Ares V01 | Anna A02 | Change |
| --- | ---: | ---: | ---: |
| Mean of four field-normalised pearl checkpoints | 0.4705 | 0.4402 | +0.0303 |
| Pearls at r50, field-normalised | 0.5000 | 0.4674 | +0.0326 |
| Pearls at r100, field-normalised | 0.5078 | 0.4772 | +0.0306 |
| Pearls at r150, field-normalised | 0.4751 | 0.4280 | +0.0471 |
| Pearls at r250, field-normalised | 0.3991 | 0.3883 | +0.0107 |
| Dragons at r100, field-normalised | 0.7500 | 0.7295 | +0.0205 |
| Total length at r100, field-normalised | 0.7746 | 0.7040 | +0.0706 |
| Births by r100, field-normalised | 0.5316 | 0.5266 | +0.0050 |

The economy mean is below BENCHMARKS.md's +0.05 acceptance gate. Dragons and total length at r100 did not fall. Both bots scored 21 wins, 138 losses, and 1 draw against the fixed roster (21.5/160 expected-score points).

| Tier 2 hygiene rate (per 1,000 dragon-turns) | Ares V01 | Anna A02 | Change |
| --- | ---: | ---: | ---: |
| Wall deaths | 3.9976 | 3.6447 | +9.7% |
| Own-body deaths | 0.0000 | 0.0000 | unchanged |
| Ally-body deaths | 1.3008 | 0.9016 | +44.3% |
| Ally head-on deaths | 1.1640 | 1.4344 | −18.9% |
| No-valid-action deaths | 0.0000 | 0.0000 | unchanged |

Ally-body deaths exceed the 10% guardrail. Newborn deaths within ten rounds fell from 29.41 to 22.22 per 100 births. Tier 3 proxies were mixed: pearl share at r150 and territory at r100 improved, while bed capture and length share at r250 fell. The direct Ares–Anna screen was 14–6 for Ares, with 9–1 as Team A and 5–5 as Team B; this small seat-skewed matchup does not override the equal fixed-panel score.

No atlas-off generalisation panel was run, so the results cover the known live maps only. V01 stays experimental and does not pass the documented acceptance gate. Its runtime-source fingerprint (C++/headers and bot.toml) is 6af8a6f47bd05da28b9d5b7ce2ca28a8d0acbcb10850c9138110a4ac27d24a62. The full result and run details are in [the V01 finding](findings/2026-09-29-ares-v01-safe-launch-routing.md). This closes the V01 report; no follow-up seed or tuning pass was run.

## V02 — Tyr V12 C++ policy port

Ares V02 is a separate copy of the Anna A02 protocol-3 scaffold with a native
C++ translation of Tyr V12's local target and movement policy. It carries the
resource-value target field, hysteresis, direction momentum, length/endgame
valuation, split decisions, enemy head-trade scoring, bounded sprint search,
and the Devil center/lane/friendly-trail bonuses. Its source implementation is
[here](../bots/ares-v02-tyr12-cpp-port/), and the strategy reference is
[tyr-v12-devil-scout-tiebreak](../bots/tyr-v12-devil-scout-tiebreak/).

The port also implements Tyr's sonar food gossip, remote density reports, crown
and prey beacons, paired-portal sharing, crown inheritance on large-child
splits, constrained-spawn separation, and retried split handoffs. It retains
Anna's hard safety tiers and room-valid split checks, so action ordering is an
adaptation rather than an exact Tyr V12 replay. It passed a C++20 executable
compile-check. A separate direct matchup screen against Tyr V12 is recorded
below. V02 remains experimental and separate from V01's measured scorecard;
the direct screen is not the fixed-panel acceptance benchmark.

## V03 — pure Tyr V12 C++ policy port

Ares V03 ports Tyr V12's scalar target and move policy, split scoring, threat valuation, sprint candidates, communication roles, and newborn separation to C++ on the Anna A02 protocol-3 runtime scaffold. The active policy does not use Anna's action tiers, enemy-near split veto, hard parent-room split gate, or map atlas. Anna's C++ controller adapter and persistent world model remain; body reconstruction can therefore differ from Tyr's Python observation state. See the [V03 source](../bots/ares-v03-tyr12-pure-cpp-port/) and [direct matchup finding](findings/2026-09-29-ares-v03-vs-tyr-v12.md).

The native seed-1 direct matchup covered the same ten live maps and both seats. Tyr V12 won **12–8**. Replay extraction succeeded on all 20 fixtures. On the benchmark-aligned round-100 diagnostics, Ares had 1.168 field-median births but 0.820 field-median units and 0.818 field-median total length; newborn deaths within ten rounds were 38.0 per 100 births, against Tyr's 29.0. This points to weaker retention after splitting. The direct screen is not the documented 140-side-game fixed-panel acceptance run. V03 remains experimental; no policy tuning followed this screen.

## V04 — Tyr V12 behavioral parity port

Ares V04 is a C++ translation of Tyr V12's active decision policy on Anna's
protocol-3 runtime scaffold. The port aligns Tyr's action scoring and the
state semantics that feed it, including partial-body observations, bounded
topology searches, radio freshness and crown memory, newborn separation, and
fallback behavior. Anna supplies the protocol adapter; its action rules do not
participate in decisions. See the [V04 source](../bots/ares-v04-tyr12-behavior-parity/)
and [behavioral parity finding](findings/2026-09-29-ares-v04-behavior-parity.md).

The ordered golden transcript suite covered ten live maps in both seats: 168,123
turns across 5,089 dragons, with zero move, split, or sonar
output differences against Tyr V12. This establishes parity only for those
recorded inputs. The seed-1 fixed-panel benchmark used all eight opponents in
the current `run_panel.ZOO`, ten live maps, and both seats (160 games); Ares
scored **117–43 with no draws**. The field-normalized pearl checkpoint mean
was 1.090, while r100 dragons and length were 1.118 and 1.000. Its hygiene
rates and full field-reference scorecard are in the finding. This absolute run
does not establish the parent-relative acceptance gate. V04 remains
experimental and is not admitted to the local frontier. The contest API lists
the requested upload as active submission v83 (ID 11244); the upload auto-
activated after processing. See the finding for its timestamp and scorecard.

## V05 — separation exception fixes

Ares V05 branches from V04 and fixes two confirmed separation failures: the
zero-`bed_wait` bed-value division and the constrained-newborn pearl pause's
missing global counter. A zero wait now values a bed only when it spawns in the
current round; the newborn can use its existing six-pearl pause budget while
keeping the normal route and first-step mask. These remove two exception
fallback paths from Tyr V12's Python behavior; they intentionally change
behavior on those cases. See the [V05 source](../bots/ares-v05-tyr12-separation-bugfix/)
and [bugfix finding](findings/2026-09-29-ares-v05-separation-bugfix.md).

On the seed-1 fixed panel (eight current opponents, ten maps, both seats), V05
scored **118–41–1** over 160 games, with no runner or extraction errors. Against
V04's matched-panel run, its normalized pearl-checkpoint mean rose only 0.007
(1.0905 to 1.0974), below the +0.05 gate; r100 dragons fell 0.047 while r100
length rose 0.009. None of the tier-2 death rates rose more than 10%, and panel
expected score rose 0.94 percentage points. The documented acceptance gate is
not met, so V05 remains experimental, is not admitted to the frontier, and was
not submitted. No seed-2 confirmation or further tuning pass was run; V04 and
active contest submission v83 remain untouched.

## V06 — expanded search and supported threat evaluation

Ares V06 branches from V05 and restores bounded high-effort search settings
measured in historical Bifröst and Skadi candidates: 160 target nodes normally,
64 at saturation, 60 in the first two turns, larger room-flood limits, and
Tyr's 12-length three-step candidate horizon. It also ports Skadi V02's
experimental Fafnir rule that discounts a predicted threat when a visible ally
at least as long as the attacker is within three tiles. Existing saturation,
late-game, and sparse-board guards remain. See the
[V06 source](../bots/ares-v06-expanded-search-support/) and
[experiment finding](findings/2026-09-29-ares-v06-expanded-search-support.md).

On the seed-1 panel (eight opponents, ten maps, both seats), V06 scored
**122–38–0**, compared with V05's 118–41–1. The normalized pearl mean rose
+0.0133, below the +0.05 gate; normalized r100 dragons improved from 1.071 to
1.200 and length from 1.009 to 1.035. No tier-2 death rate rose more than
10%. Dense Schooltime/Portals sandbox probes had zero timeout/crash errors,
with p99 max-of-games 7.4M points and an 8.6M maximum. It remains experimental,
not admitted to the frontier, and not submitted; no seed-2 confirmation or
further Ares iteration was run.

## V07 experiment — isolated Chaewon components

The V07 experiment tested two Chaewon-derived components in separate children of V06: atlas-only activated the unique public-map matcher, while [HOLD-only](../bots/ares-v07-hold-only/) sent a post-move head report through a known distant portal. Each variant had its own activation marker and neither included the other component. The atlas-only snapshot is now named [Ares V08](../bots/ares-v08-atlas-only/); its source and measured behavior are unchanged by the rename.

On identical seed-1 panels of 160 fixtures, atlas-only (now V08) scored 119–41–0 and raised the normalized pearl mean by 0.188, but lost r100 retention, breached three tier-2 death-rate guardrails, and reduced expected score. HOLD-only scored 114–46–0; ally head-on deaths fell 13.2%, but the pearl mean rose only 0.005, r100 units fell, and expected score dropped 5 percentage points. Both measured variants fail [`BENCHMARKS.md`](analysis/BENCHMARKS.md) and remain experimental. Four dense-map sandbox fixtures per variant had no timeouts/crashes. Full metrics and artifacts are in the [V07 finding](findings/2026-09-30-ares-v07-chae-won-components.md).

## V08 — atlas-only

Ares V08 is the unchanged atlas-only V07 snapshot, renamed after its isolated comparison. Its existing 160-game seed-1 result is 119–41–0; it fails the documented acceptance gate and remains experimental, not admitted to the frontier or submitted. No new benchmark was run for the rename. See the [V07 finding](findings/2026-09-30-ares-v07-chae-won-components.md) for the full measurements and artifact paths.

## V09 — deeper bounded search

Ares V09 is a separate child of V06 that applies Robert V01's deeper bounded
search parameters: first-pass target depth 20, target caps of 256/96/80,
frontier depth 6, and room-flood caps of 32/48. V06's late-round and sparse
caps and all other policy behavior are retained. The new snapshot is
[here](../bots/ares-v09-deeper-bounded-search/). It has not been benchmarked;
score and CPU/TLE behavior remain unmeasured.

## Ares V21–V28 — dead-end split iterations

These snapshots iterate from V19 against the dead-end feeding observations in the
[September 29 live-loss review](findings/2026-09-29-tyr-v01-live-loss-review.md).
All screens used unswbc 1.2.2, seed 1, sandbox execution, and direct Ares V19
matchups. V21 through V24 received the full ten-map, both-seat panel; V25 through
V27 were narrowed diagnostics; V28 advanced from an eight-game diagnostic to
the full panel.

| Version | Split change | Matched result | Decision |
|---|---|---:|---|
| V21 | Upgrade smaller selected splits to the largest safe child in critical enclosures | 9–11 | Rejected |
| V22 | Fit split size to forecast child and parent room | 10–10 | Rejected |
| V23 | Apply largest-child upgrade to pearl-rich under-room farms | 10–10 | Rejected |
| V24 | Add a newborn handoff guard to V23 | 10–10 | Rejected |
| V25 | Require an ordinary non-portal child exit | 2–2 on Portal and Slithery | Rejected; Portal 0–2 |
| V26 | Require both farm and critical-reach signals | 2–2 on Portal and Slithery | Rejected; Portal 0–2 |
| V27 | Also suppress the farm upgrade when portal topology is known | 0–4 on Portal and Slithery | Rejected |
| V28 | Keep V19's critical trigger, but detach only two tail segments | **12–8** | Best measured child; experimental |

[V28](../bots/ares-v28-minimum-sacrifice-enclosure-split/) changes only the
split size used by V19's critical-enclosure fallback: `SPLIT 2` leaves the
longer head parent intact, following the review's minimum-sacrifice
recommendation. Its four-map diagnostic scored 6–2. In the
full panel, it won both seats on Default, Portals, and Slithery Fight, and lost
both seats on Trauma; the remaining maps split 1–1. The V19 mirror baseline was
10–10, so V28 won two additional games, with zero runner errors. Replay decoding
succeeded on all 20 games. Maximum observed sandbox usage was 9.14M points.
The seed-1 matchup is a development screen only; V28 has not passed the broader
promotion gate and remains outside FRONTIER.md. The contest upload later became
active as submission v87 (ID 12440); deployment does not change its local
experimental status.

The completed V28 panel, summaries, and replays are under the ignored
`build/ares-v28-vs-v19-all10-seed1-20260930/` directory. See the
[V28 finding](findings/2026-09-30-ares-v28-minimum-sacrifice-enclosure-split.md)
for the map-by-map score and replay-derived split counts.

## Ares V29–V33 — dead-end recovery and child routing

V29–V31 investigate the Autarky loss in match 658569. The successive changes
delay the split through the last pearl; V31's replay still used `SPLIT 2`,
leaving the trapped length-3 parent to die while the length-2 child survived.
V32 keeps that feed-before-split behavior and, only when every one-step head
move is fatal in a critical enclosure, searches from the largest tail child
downward for a child with a free exit and enough forecast room
([source](../bots/ares-v32-save-long-child-at-dead-end/policy.hpp:1162)).

In the saved Autarky A-side replay against V28, dragon 61 moves onto the final
pearl at round 65, then issues `SPLIT 3` at round 66. The length-3 child 76
exits south; the original length-2 dragon wall-dies at round 67. Child 76 later
dies in a head-to-head at round 102, away from the dead end. V32 won this
233-round A-side game with no runner errors.

The direct seed-1 sandbox panel against V19 covered ten maps and both sides.
V32 won **11–9**, with no runner errors; all 20 replays decoded and their
winners matched the result records. By map: Autarky 2–0, Default 2–0, Devil
1–1, Prisoners Dilemma 1–1, Portals 1–1, Queen of Spades 1–1, Schooltime 0–2,
Slithery Fight 1–1, Trauma 1–1, Trophy 1–1. V28 scored 12–8 on this same
panel, so the specific fix retains a positive result against V19 but does not
improve on V28's score. This one deterministic seed is not the broader
promotion gate. The target-case replay, transcript, and review are in
`build/ares-v32-dead-end-screen-658569-seed1/`; the V19 panel games and decoded
reviews are in `build/ares-v32-vs-v19-all10-seed1-20260930/` and
`build/ares-v32-vs-v19-replay-review-20260930/`. See the
[V32 finding](findings/2026-09-30-ares-v32-dead-end-split-orientation.md).
The contest upload completed as submission v88 (ID 12501), named
`ares-v32-save-long-child-at-dead-end-ai`; it was active before the later V33
upload. Server deployment is recorded separately from local frontier
admission.

## Ares V33 — split-time portal route handoff

V33 branches from V32 to address match 658574. Its parent had already seen one
edge of portal 1, but the newborn did not inherit that route and moved away
from the pearl-side portal. At a split, V33 sends the nearest known edge and
portal ID in a type-9 sonar packet; the child routes to that endpoint and drops
the waypoint after transit or timeout.

A stateful run over the replay's recorded parent turns emitted portal 1 / edge
954 at the round-15 split. Replacing the replay's two parent-to-child split-turn
radio deliveries with that packet made the replay-state child travel to
`(4,3)`, cross to `(8,33)` at round 19, and collect the pearl at `(10,32)` at
round 22. On the same initial child observation, V32 moves east while V33 moves
south toward the handed-off endpoint. This is a targeted replay-state
simulation, not a fresh full-game
match or a broad screen. V33 was uploaded as submission v89 (ID 12584) at
2026-09-30 05:24 UTC and is active. Its API source hash is
`fd313ece33ff0dfc14bb1d04dd96c8e6e291f269ac015146f2c226c95c8ea776`. The
local candidate remains experimental. See the [V33 finding](findings/2026-09-30-ares-v33-split-portal-route-handoff.md).

### Four-version live-map comparison

The seed-1 sandbox screen used unswbc 1.2.2 on the same ten live
maps, every pairing, and both seats (120 games; 60 per version). There were no
draws or runner errors. Overall records were V33 **33–27**, V32 **32–28**, V28
**30–30**, and V19 **25–35**. The six direct head-to-head results were:

| Pairing | First version's wins–losses |
|---|---:|
| V33–V32 | 10–10 |
| V33–V28 | 11–9 |
| V33–V19 | 12–8 |
| V32–V28 | 11–9 |
| V32–V19 | 11–9 |
| V28–V19 | 12–8 |

Each cell below is wins–losses over that bot's six games on the map (three
opponents, both seats):

| Map | V33 | V32 | V28 | V19 |
|---|---:|---:|---:|---:|
| Autarky | 4–2 | 6–0 | 1–5 | 1–5 |
| Default | 0–6 | 5–1 | 5–1 | 2–4 |
| Devil | 3–3 | 3–3 | 3–3 | 3–3 |
| Dilemma | 2–4 | 4–2 | 3–3 | 3–3 |
| Portals | 4–2 | 2–4 | 5–1 | 1–5 |
| Queen of Spades | 6–0 | 2–4 | 2–4 | 2–4 |
| Schooltime | 3–3 | 2–4 | 3–3 | 4–2 |
| Slithery Fight | 5–1 | 2–4 | 3–3 | 2–4 |
| Trauma | 3–3 | 3–3 | 2–4 | 4–2 |
| Trophy | 3–3 | 3–3 | 3–3 | 3–3 |

V33's overall lead over V32 is one win, while their direct series is even.
V33 swept Queen of Spades and went 5–1 on Slithery Fight; it lost all six
Default games. This single deterministic screen is developmental evidence,
not the broader promotion gate, so V33 remains experimental. The manifest,
standings, results, and per-game logs are in the ignored
`build/ares-v33-v32-v28-v19-live10-seed1-20260930/` directory; replays were
not saved.


## Ares V34–V35 — crown dash survival

Match [669722](https://game.battlecode.au/visualiser?match=669722) exposed a
round-477 failure. Ares Team A's 24-length crown, dragon 20 at `(20,10)`, moved
south to `(20,11)`. Enemy dragon 414 was length 4 at `(22,12)`, but its visible
chain was clipped by the crown's vision. V33 estimated only three segments and
two dash steps. The enemy moved north-west; after its second step it was at
`(21,11)`, adjacent to the crown, and both died head-to-head. Team A was
eliminated.

V34 tried a broad crown retreat bonus, treated clipped enemies as full-dash
threats, and prohibited crown-initiated head trades. Its seed-1 screen against
V33 scored **7–13** on ten maps and both seats, with zero runner errors. It lost
both games on Portals, Queen of Spades, and Slithery Fight. The general retreat
bonus was too costly and V34 is rejected.

V35 branches from V33, retaining its target and movement scoring. It changes
only crown threat accounting: a clipped enemy can dash the maximum three cells,
and the existing threat penalty also covers adjacent head-contact cells around
predicted endpoints. This models the round-477 collision without broadly
steering the king away from every visible enemy. In a controlled replay drive
that kept V33's local decisions through round 476 and enabled the V35 threat
rule at round 477, the crown chose `WN` instead of the replayed `S`. From the
recorded head at `(20,10)`, `WN` ends at `(19,9)`, two Chebyshev cells from the
attacker's recorded contact cell `(21,11)`. The local replay driver differs
from the live V33 action at round 473, so this checks the decision from saved
observations rather than a full counterfactual game.

| Candidate | Direct result vs V33 | Decision |
|---|---:|---|
| V34 broad retreat | 7–13 | Rejected |
| V35 clipped dash and adjacent contact | **10–10** | Retain as experimental |

V35's map records were Autarky 1–1, Default 1–1, Devil 1–1, Dilemma 1–1,
Portals 2–0, Queen of Spades 1–1, Schooltime 0–2, Slithery Fight 1–1, Trauma
1–1, and Trophy 1–1. That 20-game screen used unswbc 1.2.2, seed 1, sandbox
execution, and both seats, with no errors. V35 was then screened against the
other three versions on the same fixtures:

| Opponent | V35 wins–losses |
|---|---:|
| V33 | 10–10 |
| V32 | 6–14 |
| V28 | 9–11 |
| V19 | 13–7 |

Across these four matchups, V35 went **38–42** in 80 games. Combining those
results with the existing three-way comparisons gives one-seed five-bot
standings of V32 **46–34**, V33 **43–37**, V28 **41–39**, V35 **38–42**, and
V19 **32–48**. There were no runner errors. This is a single-seed screen, not
a promotion gate. V35 remains experimental and outside `FRONTIER.md`; its
upload as submission v90 (ID 12675) does not promote it locally. The API source
hash is `870f4bbb1b20371e472728363fe05479ecf92c0a9d260ce70c4c21106eb04c1d`.
The new 60-game results are in the ignored
`build/ares-v35-vs-v19-v28-v32-live10-seed1-20260930/`; the V33 results are
in `build/ares-v35-vs-v33-live10-seed1-20260930/`. See the
[V35 finding](findings/2026-09-30-ares-v35-crown-clipped-dash-threat.md).

## Ares V36 — no-pearl portal scout

Match [674727](https://game.battlecode.au/visualiser?match=674727) shows V35
turning north at round 52 beside the unpaired Queen of Spades portal at
`(6,17)`. Dragon 1 last ate a pearl on round 33 and next ate one on round 86.
V35's target score is 3 for a portal and 5 for unseen ground, so an
unexplored-ground target can pull it away even without a fresh pearl lead.

V36 branches from V35. From dragon age 3, it scores an unpaired portal at 8
when there is no fresh pearl memory; ordinary unseen ground remains 5, and
pearl and bed targets retain their existing values. This also makes the
existing 40-round memory TTL determine whether a pearl still suppresses
portal scouting. V36 was uploaded as submission v91 (ID 12728) on 2026-09-30
07:02 UTC and became active. Its API source hash is
`8d5e4b3dba5ec9f948d4985581349267928b88933da47dc4dda847d57b6aa0b1`. It remains
experimental locally and outside FRONTIER.md. Its seed-1 sandbox screen over
the ten live maps and both seats scored 13–7 vs V35 and 9–11 vs V19, with zero
errors. V35 scored
13–7 vs V19 on the same fixture, so V36's value of 8 is too aggressive for
promotion. This was a full-match screen, not a counterfactual replay of the
reported turn. See the [V36 finding](findings/2026-09-30-ares-v36-no-pearl-portal-scout.md)
and [source snapshot](../bots/ares-v36-no-pearl-portal-scout/).

## Ares V37 — near-portal scout

V37 narrows V36's no-pearl portal value from 8 to 6. This still outranks
unseen ground at value 5 for a nearby portal approach like the one in match
674727, while reducing the pull toward more distant portals. It retains V36's
40-round pearl-memory check and age-3 gate. V37's seed-1 sandbox screen on
the ten live maps and both seats scored 17–3 vs V35 and 10–10 vs V19, with
zero errors. It went 2–0 against both opponents
on Queen of Spades, but did not improve on V35's 13–7 V19 result. V37 was
uploaded as submission v92 (ID 12851) on 2026-09-30 08:44 UTC and became active;
its API source hash is
`d0b6e74c95f9d98e1cbceb58c8d82179d21ad676b699aa2ab3e11d2248ca683f`. The upload
does not change its local experimental status or admit it to the frontier. For
details, see the
[V37 finding](findings/2026-09-30-ares-v37-near-portal-scout.md) and [source snapshot](../bots/ares-v37-near-portal-scout/).

## Ares V38 — purposeful short sprints

V38 branches from V37 and adds a score premium to two-step moves by length-3
dragons. The premium is repaid only when the extra step collects a pearl or
reaches a selected high-value target; a sufficiently strong tactical score can
still justify the dash. Its focused regression distinguishes V37's EN dash
from V38's one-step E in a dense-threat stress fixture and preserves dashes to
a pearl and ripe bed. The seed-1 ten-map panel lost **7–13** to V37. Replay
action counts showed V38 dashing on 3.89% of length-3 turns, versus 1.12% for
V37, so the 4.0 reimbursement overcompensates. The local replay reconstruction
omits persistent policy and radio state, so it does not reproduce the exact
match-686866 action. V38 remains an experimental control. See the
[V38 finding](findings/2026-09-30-ares-v38-purposeful-sprints.md) and
[source snapshot](../bots/ares-v38-purposeful-sprints/).

## Ares V39 — reduced short-sprint reimbursement

V39 lowers V38's length-3 dash reimbursement to 2.5 and removes the refund for
escape-plan arrivals. Its seed-1 ten-map panel also lost **7–13** to V37, so
lowering the bonus did not change the direct result. See the
[V39 finding](findings/2026-09-30-ares-v39-balanced-short-sprints.md) and
[source snapshot](../bots/ares-v39-balanced-short-sprints/).

## Ares V40 — length-priced sprints

V40 branches from V37 and removes the duplicate sprint charge: the simulator
already accounts for each extra move by removing one tail segment. Successful
moves score that length change once, pearls do not receive a separate generic
growth bonus, and uncontested pearls collected on a dash get a small future-
growth opportunity cost. A pearl within two tiles of an enemy instead receives
a one-segment denial value. On the seed-1 ten-map panel, V40 beat V37 **11–9**
with zero runner errors. Length-3 dash rates were 2.43% for V40 and 1.94% for
V37 on this panel. This is a positive one-seed development screen, not a
promotion result; V40 remains experimental outside FRONTIER.md. The contest
API lists the upload as active submission v93 (ID 13010), source hash
`1a4ee3dc7148ef7b8c2488879d09c75d8b9cfbc32364d8c03e96e35013597737`.
Activation does not promote the local candidate. See the
[V40 finding](findings/2026-09-30-ares-v40-length-priced-sprints.md) and
[source snapshot](../bots/ares-v40-length-priced-sprints/).

## Ares V41 — portal-bed dispersion

V41 branches from V40 and lowers pearl or bed target value when visible allied
heads are already within two tiles. This covers the case where a portal makes
the candidate's route shorter than the covering ally's Manhattan distance, so
V40's nearest-ally test does not yield. It also tracks the landing and pair of
the most recent crossing; for 12 rounds, while within two tiles of that
landing, it lowers targets routed through the same pair and penalizes crossing
back. The decoded Queen of Spades replay 700279 showed dragon 18 returning
through P0 after five rounds and child 82 returning after eleven rounds while
three allied heads clustered around its landing. The focused regression passes
and the V41 bot compiles. In a ten-map, both-seat screen, V41 beat V40 **11–9**
with zero runner errors; `unswbc` generated the per-game seeds. V41 swept
Dilemma, Portals, and Slithery Fight, V40 swept Default and Devil, and the other
five maps split. This is one development screen; V41 remains experimental
outside FRONTIER.md. The upload auto-activated as submission v94 (ID 13086) on
2026-09-30 11:49 UTC. Its API source hash is
`1c1f1fa7bd0b672ab3f6641373ba532514d5ecaca2a6c267832ae4b79cab9088`; activation
does not change local experimental status. See the
[V41 finding](findings/2026-09-30-ares-v41-portal-bed-dispersion.md) and
[source snapshot](../bots/ares-v41-portal-bed-dispersion/).

## Ares V42 — memory and teammate dispersion

V42 branches from V41, removes the Devil lane bonus, discounts exploration in
remembered sectors with no known pearl beds, and adds a bounded cost when a
move closes distance to a visible teammate head. The sector discount also
applies to fallback exploration targets. This is intended to send explorers
toward fresher or pearl-bearing areas and reduce convergence around visible
allies while preserving the inherited resource and hunt scoring. In a native
ten-map, both-seat screen against V41, V42 scored **8–12**, with no runner
errors, replay-analysis errors, or runtime faults. It swept Portals and
Slithery Fight; V41 swept Autarky, Default, Devil, and Trophy, and four maps
split. This is one generated-seed development screen; V42 remains experimental.
See the
[V42 finding](findings/2026-09-30-ares-v42-memory-team-dispersion.md) and
[source snapshot](../bots/ares-v42-memory-team-dispersion/).

## Ares V43 — exploration-only teammate separation

V43 keeps V42's Devil lane bonus removal and bedless-sector exploration
discount, but applies the visible-teammate approach cost only while pursuing
exploration. This avoids charging moves toward known pearls and prey. In a
native ten-map, both-seat screen against V41, V43 scored **12–8** with no
runner errors, replay-analysis errors, or runtime faults. It swept Default,
Dilemma, Queen of Spades, Slithery Fight, and Trophy; V41 swept Devil, Portals,
and Schooltime; Autarky and Trauma split. This is one generated-seed screen,
and the V42 screen used different seeds, so the 8–12 to 12–8 change is only a
promising comparison, not a controlled estimate. V43 remains experimental.
See the [V43 finding](findings/2026-09-30-ares-v43-exploration-only-dispersion.md)
and [source snapshot](../bots/ares-v43-exploration-only-dispersion/).
The contest accepted V43 as submission v95, reported as processing; this does
not promote it locally.

## Ares V44 — shared sector exploration

V44 forks V43 and relays the strongest single-dragon coverage estimate for
each 8×8 sector, plus whether any pearl bed was observed there. Reports merge
by maximum coverage and positive bed sightings, so overlapping surveys cannot
inflate confidence. Explorers also publish eight-round sector claims, refreshed
every three rounds. Teammates discount unseen cells in claimed sectors and
prefer unclaimed sectors; claims and improved sector reports relay through
available sonar lanes. V44 keeps V43's visible-teammate approach penalty.

This change responds to match 710870, where Ares V43 (submission 13183) played
as Team A on Autarky. The replay showed repeated scouting into low-value areas;
target diagnostics were not recorded. In a three-seed screen against V43 on
the ten live maps and both sides, V44 scored **32–28** over 60 games with no
runner errors. It went 4–2 on Autarky. This small screen is inconclusive; V44
remains experimental and is not promoted. See the
[V44 finding](findings/2026-09-30-ares-v44-shared-sector-exploration.md) and
[source snapshot](../bots/ares-v44-shared-sector-exploration/).

## Direct matchup screens: Tyr V12

### Ares V01

A native screen played Ares V01 against tyr-v12-devil-scout-tiebreak on the
same ten live maps, one game from each seat per map. With unswbc 1.2.2 and
simulation seed 1, Tyr won **20–0**, taking both seats on every map. Each game
returned rc=0; there were no draws. The 20 replay files and index are in the
ignored build/ares-v01-vs-tyr-v12-20260929/ directory. Full details are in
[the V01 finding](findings/2026-09-29-ares-v01-safe-launch-routing.md).

### Ares V03

A native seed-1 screen used the same ten live maps and both seats. Tyr V12 won **12–8**: Tyr swept Autarky, Dilemma, Portals, Queen of Spades, and Schooltime; Ares swept Default, Slithery Fight, and Trauma; Devil and Trophy split 1–1. All games returned rc=0. All 20 replays were extracted successfully. Logs, results, standings, manifest, features, and replays are in the ignored build/ares-v03-vs-tyr-v12-20260929/ directory. Benchmark-aligned measurements and limits are in [the V03 finding](findings/2026-09-29-ares-v03-vs-tyr-v12.md).

### Ares V02

A separate native screen used the same ten maps, both seats, unswbc 1.2.2,
and simulation seed 1. Tyr V12 won **20–0**, taking both seats on every map.
All 20 games returned rc=0, with no draws or runner errors. Logs, results,
manifest, standings, and 20 replays are in the ignored
build/ares-v02-vs-tyr-v12-20260929/ directory. The map-by-map results and game
rounds are in [the V02 matchup finding](findings/2026-09-29-ares-v02-vs-tyr-v12.md).

Each screen is one game per seat and map. These direct comparisons are separate
from the fixed zoo panel and its unswbc 1.2.1 Anna control. They measure only
these bot pairs and do not replace the fixed-panel gate or establish an all-map
ranking.
