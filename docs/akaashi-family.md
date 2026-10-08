# Akaashi family — queen escape safety

Created 8 October 2026, Australia/Adelaide. Parent: immutable atlas-disabled
`bots/bokuto-18-queenfeed`. Initial candidate: `akaashi-01-queen-escape`.
This is an experimental safety family; the qualifier fallback remains Bokuto 18.

## 01: avoid an allied alcove trap

Initiating replay: https://game.battlecode.au/visualiser?match=1404793,
Trophy, team B, queen ID 0. At round 66 the queen at (2,7) chooses north to
(2,6). Ally 38 at (4,7) subsequently chooses west to (3,7), closing the
alcove exit. At round 67 the queen moves east to (3,6), then dies against
kelp at round 68. There are five friendly dragons, so Bokuto 18's stronger
queen/head-clearance mode and teammate yielding are disabled.

Akaashi 01 demands six continuation moves for queens from round zero and
applies the existing future head-adjacency exclusion at every team size.
Dodge overrides must meet that same horizon before returning. Existing
teammate yielding also runs at every team size. The inherited relaxation
still permits head-adjacent continuations if no strict escape survives.
Economy, feeding, atlas-disabled configuration and non-queen survival horizon
remain inherited. This is a bounded local survival search, not a guarantee
against every future teammate or opponent move.

### Measured regression

- Original replay reproduced with the official engine and seed
  `7698345d63307078`: 3,916 turns, zero reconstructed-observation mismatches,
  zero extra engine turns; A wins at final protocol round 127.
- On the reconstructed queen history, Bokuto 18 chooses north at round 66;
  Akaashi 01 chooses east, guard tag `G`.
- Branch experiment: preserve recorded actions through round 65, then use
  native Akaashi decisions for queen 0 and ally 38 from round 66. Other
  dragons retain recorded actions/sonar; exhausted action lists use empty
  MOVE. B wins at final protocol round 128, queen alive with length four.
  This scripted counterfactual verifies the initiating failure, not general
  playing strength against a responsive opponent.
- Synthetic alcove regression passes for both baseline (north) and candidate
  (east): `python3 tests/test_akaashi_queen_escape.py`.

Artifacts: `build/queen-safety-1404793/` (replay, reconstructed histories,
probes, oracle/branch script, metadata, branch replay and verification summary).
Server bed timers are redacted; the oracle uses official Trophy template
bed timings and the server seed, rather than treating reconstructed timers
as ground truth.

### Measured development screen

Seed 81008, one worker, both seats, candidate against exact Bokuto 18:

| Map | Akaashi wins | Losses |
|---|---:|---:|
| Trophy | 1 | 1 |
| Weakhold | 2 | 0 |
| Schooltime | 1 | 1 |
| Total | 4 | 2 |

Zero runner errors and zero replay TLE/invalid-action faults. Direct score
advantage +0.1667, 90% map-cluster interval [0, +0.3333]; positive-screen
gate false. Audit: the run's `analysis.json`.
This six-game, three-map development screen is insufficient for promotion.
Artifacts: `build/finals/20261008-akaashi01-screen/`.
The frozen native screen source differs from the current snapshot only in
explanatory comments added after its source freeze.

Reproduce with:

```sh
.venv/bin/python tools/finals/screen.py --candidate akaashi-01-queen-escape \
  --opponents bokuto-18-queenfeed \
  --maps maps/live/trophy.map maps/live/weakhold.map maps/live/schooltime.map \
  --seeds 81008 --output build/finals/akaashi01-new-screen --dry-run
```

Remove `--dry-run` to execute in a fresh output directory. Before considering
promotion, run a broader paired development pool and a separately frozen
confirmation set, with map-cluster uncertainty and metered runtime checks.

### Metered runtime check

Two Trophy fixtures, both seats, seed 81008, official sandbox: 1–1, zero
runner errors and zero replay TLE/invalid-action faults. Candidate peak
points per turn 8.3M; p99 at most 7.8M. Native and metered results agree
on these fixtures. Artifacts: `build/finals/20261008-akaashi01-runtime/`.
This is a focused runtime check, not an all-map runtime guarantee.

Final source fingerprint (tools/finals/screen.py): `128f6c396312837b5af15bcf7836f8a90731fc1506f1554cff4dbc69ad29e1c8`.

### User-selected deployment — 8 October 2026

At the user's explicit request, uploaded and verified **20222 (v104)** as
sole active: `LV-akaashi-01-queen-escape-4cf62807-ai`. Server compilation
completed successfully. Server sourceHash:
`188b90bbba4dcc0cd28d69dce51e9e1e4d60415d66a398039c1da1ed18ef0f8f`.
All 15 ZIP files match the tested local snapshot. Receipts:
`build/finals/20261008-akaashi01-submit/`. This is a deployment decision,
not confirmation of greater general strength. Bokuto 18 remains fallback.

## 02: take visible, affordable queen strikes

Trigger: https://game.battlecode.au/visualiser?match=1407768, Trophy, team A.
Visualiser round 47 is protocol round 46. Dragon 4 at (12,10), length two,
can move north onto the pearl at (12,9), then east into enemy queen 1 at
(13,9). Akaashi 01 chooses west. Its sprint generator requires starting
length >=3 even when a pearl funds the paid step; its ordinary strike score
values the queen like any other dragon. Three-step generation also requires
starting length >=4, missing other pearl-funded attacks.

02 forks immutable 01 and searches one-to-three-step, fully observed queen
attack paths before ordinary scoring and split selection. Prefix simulation
checks terrain, current bodies, pearls and paid-step affordability. Non-queen
attackers take the shortest confirmed queen trade without the ordinary
material/team-size threshold. Own queens retain their safety behavior. The
main loop revalidates the full command and every prefix before bypassing
all guard overrides for the deliberate trade. No enemy prediction or global
replay state enters decisions. Searches are bounded; four-step attacks and
attacks through unknown terrain remain outside scope.

### Measured replay regression

Official-engine reproduction with seed `17cdd44f3399e666`: 2,530 turns, zero
observation mismatches, zero extra turns; original B win at final protocol r118.
Reconstructed history outputs for 02: dragon 4 `NE` at r46, dragon 20 `EEE`
at r46 and `ENE` at r47, dragon 30 `SSE` at r46. These are separate legal
observation probes, not simultaneous independent kill claims.

Branch: preserve all recorded actions through protocol r45, then use native
02 only for dragon 4 from r46; all other actors remain scripted with recorded
actions/sonar, empty MOVE after their lists end. Enemy queen 1 dies by head-on
collision at r46. B still wins at final protocol r91 with both queens dead.
This verifies the missed kill, not a guaranteed win or general improvement.
Artifacts: `build/queen-strike-1407768/` (oracle, probe histories, branch
script/replay and source). Server bed timers are recovered from the official
Trophy template and seed for engine reproduction.

Synthetic tests cover pearl-funded two/three-step attacks, insufficient
length, ordinary enemies, own-queen exclusion, allied heads, unknown terrain,
blocking bodies and commands with steps after the collision. The alcove
regression is also extended to 02 to preserve the prior safety fix.

02 is local and experimental; submission 20222 (Akaashi 01) stays active.

### 02 development screen

Serial Trophy screen, seed 81009, both seats against each opponent:
1–1 against Akaashi 01 and 1–1 against Bokuto 18; zero runner errors and
zero replay TLE/invalid-action faults. Four games on one map are insufficient
for promotion. Artifacts: `build/finals/20261008-akaashi02-screen/`.
Source fingerprint: `b4661bcdfe8722014a70361d119c4889ec12034837ef09a4f7c20ead3105ad60`.

02 metered Trophy check: seed 81009, both seats vs 01, 1–1, zero runner
errors or replay TLE/invalid-action faults. Candidate peak 10.3M points per
turn, p99 <=7.9M. Native and sandbox outcomes agree on these fixtures.
Artifacts: `build/finals/20261008-akaashi02-runtime/`. This focused check
is not an all-map runtime guarantee.

## 03: dodge threatened queen splits at any round

Same Trophy 1407768, team A. At protocol r109 queen 0 at (19,11), length four,
sole friendly unit, chooses SPLIT 2. Enemy 51 at (19,14) executes NNN and
kills both heads later that round. Only two disconnected enemy-51 segments
are in the queen's view, so complete enemy length is unknown. The guard
already marks her stationary cell as threatened, but split-to-dodge forcing
was restricted to the feeding phase (r290 onward). A stationary split can
pass terrain survival despite being exposed to a same-round enemy sprint.

03 forks immutable 02 and forces a dodge evaluation for queen splits on
enemy-reachable cells at any round. Replacement still must pass the full
six-step continuation test and uses existing risk ranking. Distant safe
production splits and essential cage splits remain available. Missing or
cut enemy body data now consistently receives bounded four-step reach.
Each enemy has a separate BFS visited mask; the old shared result mask
could wrongly suppress traversal through another enemy's threat region.
The final result is the union of all enemy searches.

Measured replay regression: original oracle remains 2,530 turns, zero
mismatches/extra turns. On the reconstructed queen history, 03 retains
MOVE W at r108 and replaces SPLIT 2 with MOVE N (guard Q) at r109.
Branch preserves all recorded actions through r108 and uses native 03 only
for queen 0 from r109. Other actors keep recorded actions/sonar, empty MOVE
after recorded lists end. Queen survives; A wins at final protocol r119,
queen length two, compared with original B win at r118. This is a scripted
counterfactual, not general strength evidence against adaptive opponents.
Artifacts: `build/queen-strike-1407768/split-branch.py`,
`split-branch.replay`, `split-probe/`, and `d0-akaashi03.stdout`.

Synthetic regression compares parent retaining a threatened split with 03
choosing north; verifies safe production and cage splits, unknown-body
four-step coverage and overlapping-enemy reach. Prior alcove and visible
queen-strike tests also cover 03.

Source fingerprint: `99a4a584d0255a5016ba961d949218db18a8446a26316485857e355bd35d4a8c`. No upload or activation: 20222 remains deployed
Akaashi 01. Broader paired development and untouched confirmation remain
proposed before statistical promotion.

03 serial native development screen: seed 81010, both seats vs exact 02,
Trophy 1–1 and Schooltime 1–1; total 2–2 with zero runner errors.
Artifacts: `build/finals/20261008-akaashi03-screen/`. Dry-run completed
before execution. This small two-map screen does not establish improvement.

03 verification completed: all three synthetic regression suites pass.
Native screen replay audit: zero TLE/invalid-action faults. Metered Trophy
check, seed 81010, both seats vs 02: 1–1, zero runner errors or replay
faults. Candidate peak points 8.7M, p99 <=8.2M; native and metered fixture
outcomes agree. Artifacts: `build/finals/20261008-akaashi03-runtime/`.
Focused checks do not establish all-map strength or runtime guarantees.

Akaashi 03 server compilation succeeded and authenticated readback verified
20244 as sole active. The server auto-activated it; no activation POST was
needed. With 20244 active, POST /api/v1/battles accepted 11 unranked games
against Heartbreaker (team 62), one for every lost map in the earlier series.
IDs **1410660–1410670**, series `05360044-7f0a-42b1-b33e-66de0fdcfa18`.
GET readbacks verified every opponent/map and pending status; outcomes are
not measured yet. Receipts: `build/finals/20261008-akaashi03-submit/`,
including `verified-active.json`, `queue-response.json`, `queue-verified.json`.

## 8 October 2026 — ongoing Heartbreaker iteration, Akaashi 04

User authorized continuous general-rule iterations: inspect completed loss
maps, fix evidenced weaknesses, upload/activate and retest remaining losses
until they clear the goal. Akaashi 03 series 05360044-7f0a-42b1-b33e-66de0fdcfa18
completed **5–6**, zero TLE/invalid-action replay faults. Six losses: Around
UNSW, Autarky, Default, Prisoners Dilemma, Slithery Fight, Stripes.

Added `tools/finals/heartbreaker_review.py` to emit start-of-round plus final
curves (total, queen, longest, units), samples, economy-event totals, queen
deaths, largest deaths and longest drops linked separately to splits/deaths.
Plots use matplotlib. Detailed map-by-map evidence/inferences and next
weaknesses: `docs/finals-campaign/HEARTBREAKER_ITERATION.md`. Downloaded
series/metadata, legal-history probes, CSVs/plots and summaries:
`build/finals/heartbreaker-iteration/akaashi03/`.

First evidenced implementation target: Around UNSW dragon 711 at r408,
length 36 but only four represented chain cells. Parent chooses NEE and
self-collides at length 37 because visible disconnected own-body pieces
are ignored. 04 includes all currently visible own segments in simulation,
and does not release a partial chain's front as if it were the real tail.
Final movement revalidation can replace a known doomed command with a legal
step; intentional feeder/cap-cull deaths remain. No map names/coordinate
conditions/atlas. Source fingerprint `4756f20750712479f60135dda2064156d14cf584df2a2c6e038572b7c618341a`.

Measured: official-engine original oracle reproduced 36,347 turns, zero
mismatches/extra turns, B wins at r499. Preserve recorded prefix through
r407 and use native 04 only for dragon 711 from r408: avoids the observed
r408 self-collision, chooses N. Dragon later dies against a wall at r411.
The scripted branch ends A win at r477, but that does not establish general
strength; recorded lists exhaust and later actors use empty MOVE. The
regression claim is limited to avoiding the observed self-collision.
Artifacts: `body-branch.py`, `body-branch.replay`, `1410660-d711.input`.

`test_akaashi_visible_body.py` passes (disconnected/partial body rejection
and exact full-tail release); all three previous regression suites now
include 04 and pass. Local serial screen vs03: Around UNSW/Stripes, seed
81011, both seats, 2–2, zero runner/replay faults. Metered Stripes, same
seed/both seats: 1–1, zero faults, candidate peak 9.5M points, p99 <=9.1M.
Artifacts: `build/finals/20261008-akaashi04-screen/` and `...-runtime/`.
Both screen dry-runs and replay fault audits completed. These narrow checks
do not establish strength or all-map runtime guarantees.

Outstanding biggest weaknesses: early corridor/food-access failures on
Stripes/Prisoners Dilemma/Autarky; early economy/contact attrition on Default;
midgame attrition/queen death on Slithery Fight; late queen/long-head deaths
and remaining partial-body wall risks on Around UNSW. Next loop: submit04,
retest six loss maps, inspect new failures before implementing the next version.

### Akaashi 04 deployment and live retest

20265 (v106), `LV-akaashi-04-visible-body-safety-78d38fff-ai`, compiled and
was verified sole active. Archive 15 files / 3,941,039 bytes, ZIP integrity
and source-byte checks passed. Archive SHA256
`78d38fff65215b9d1897e533e4d268c6caf2567480cd0c42467becfba584afa9`;
server sourceHash `e0606fff4a87c81a1f4fa103db3515b38026952c42c49da60724cbe09f852f16`.
User-authorized unranked retest accepted **1412255–1412260**, one each on
Around UNSW, Autarky, Default, Prisoners Dilemma, Slithery Fight, Stripes.
Receipts: `build/finals/20261008-akaashi04-submit/`. Results pending.
Next continuation must refresh this series, analyze new losses, and make
a further general change from evidence. Goal remains active.

## Akaashi 04 retest — completed

Submission 20265 vs Heartbreaker: **1–5**, six games, one per map, fresh server seeds. Around UNSW is a win; five losses remain. This is not a matched causal estimate of the effect of 04. All six replays have zero TLE/invalid-action faults.

| Loss | Total A/B r50; r100; r200 | Queen death | Largest dragon death | Current primary weakness |
|---|---|---|---|---|
| Autarky (1412256) | r50 13/49 | r44, length 2 | r4, length 3, wall | Early corridor/food deficit; repeated length-three dead-end deaths before queen loss. |
| Default (1412257) | r50 21/19; r100 62/27; r200 79/37 | r166, length 2 | r367, length 9, h2h | Economy leads at r100/r200, then material/contact attrition reverses it; queen killed at r166. |
| Prisoners Dilemma (1412258) | r50 2/40 | r52, length 2 | r2, length 6, h2h | Opening population collapses: spawned heads collide and short chains strand before resource growth. |
| Slithery Fight (1412259) | r50 98/95; r100 141/113; r200 152/184 | r116, length 3 | r494, length 72, h2h | Midgame economy lead reverses; early queen loss plus decisive length-72 head-on at r494. |
| Stripes (1412260) | r50 2/24 | r38, length 3 | r38, length 3, h2h | Very weak food collection; queen collision at r38; partial-body fix cannot solve narrow-route starvation. |

Artifacts: `build/finals/heartbreaker-iteration/akaashi04-series/review/` (all curves, event-linked drops, summaries and plots).

Akaashi 05 adds general bounded sprint escape for queens: shortest-first legal prefixes of up to three steps, known visible terrain, exact body/pearl/paid-step simulation, lower endpoint risk, six continuation steps. Safe incumbent moves remain. It fixes a restricted single-step dodge search, without map identifiers or coordinate conditions.

Two measured counterfactuals: Around UNSW 1410660 oracle 36,347 turns/zero mismatches; original prefix through r387 then 05 only for queen 0. NN avoids r388 collision but queen dies at r397. Stripes 1412260 oracle 505 turns/zero mismatches; prefix through r36 then 05 only for queen 0. SE avoids original r38 collision, queen dies at r44; branch draws at r61 rather than original B win at r60. Other actors use recorded commands/sonar; exhausted lists use empty MOVE. These demonstrate avoidance of specific deaths, not wins against adaptive opponents.

05 synthetic endpoint escape test and all four earlier regression suites pass. Native Trophy/Autarky screen vs04, seed 81012, both seats: 2–2, zero faults. Metered Trophy same seed/both seats: 1–1, zero faults; candidate peak 8.8M points, p99 <=8.5M. Artifacts: `build/finals/20261008-akaashi05-screen/`, `...-runtime/`.

05 source fingerprint: `4a8d86ca8dc1cca4270d7623723bd42ddd28c8703204881df83aad7ecd19d7d0`.

Outstanding economy targets remain, especially opening corridor viability on Autarky/Prisoners Dilemma/Stripes. Next inspect 05 failures, and prioritize food/production changes or valuable late-dragon survival from the new evidence.

### Akaashi 05 deployment and five-map retest

20276 (v107), `LV-akaashi-05-sprint-queen-escape-55ad3fc2-ai`, compiled
and was verified sole active. Archive: 15 files, 3,941,224 bytes, ZIP integrity
and local-source byte checks passed. Archive SHA256
`55ad3fc299b062320aa2cc66fd5c77c860fb3175fbae6e157f4b3487b26976a0`;
server sourceHash `2ce46a1e8404ea60bb59150309cbd1167393f11a702a387b47d10d7feefd03d6`.
Accepted and verified five unranked Heartbreaker games **1413068–1413072**:
Autarky, Default, Prisoners Dilemma, Slithery Fight, Stripes; series
`66b05548-b3dd-4129-8db4-085a3c7fa0d1`. All pending at readback. Receipts:
`build/finals/20261008-akaashi05-submit/`. Goal remains active.

Next continuation: refresh 1413068, collect finished replays and generate
all loss curves. In addition to opening food/production viability, prioritize
Slithery Fight 1412259 dragon 1590's length-72 H2H at r494: authoritative
final standings show both queens dead and longest 12 vs55. This is a
plausibly outcome-changing late material loss; verify a legal escape from
its current observations before changing late long-dragon behavior.

## Akaashi 06 validation checkpoint

Latest user steering: finish current iteration and test. 05 live retest completed 0–5; all loss curves are in `build/finals/heartbreaker-iteration/akaashi05-series/review/`. 06 applies bounded dodge checks to late non-feeder heads of length >=12 before the partial-body shortcut. Partial known cells with >=6 unseen tail cells remain occupied for the six-step horizon. Reconstructed 1412259 dragon 1590 changes W to S at r494. Full oracle failed (39,133 mismatches / 39,147 turns); attempted branch rejected. No counterfactual win/survival claim. Synthetic asset/exclusion tests and prior safety cases compiled against06 pass. Native Slithery/Dilemma seed81013 both seats: 2–2, zero replay faults. Initial metered run was interrupted with truncated artifacts; recovery run is `build/finals/20261008-akaashi06-runtime-recovery/`.

06 focused runtime recovery completed: 0–2 vs05 on Slithery Fight, zero runner/replay faults, candidate peak13.6M points, p99<=8.6M. Uploaded 20296 (v108), LV-akaashi-06-late-material-safety-406f4835-ai; server sourceHash 4d5d6364ca83997284e2779cd8ba9b510c9116383a025bca236219e2ff01b98b; archive SHA256 406f4835b0edbf17f4f7201197fa48ce5063baf5a5b6c5eafe47bc1e438a1ea8. Compilation/readback and five-map live test pending. No general improvement claim.

06 compilation/readback succeeded: 20296 sole active. Accepted and API-verified five-map Heartbreaker test1415322–1415326, seriesc7153758-39cf-42e0-bf8e-201ad801e97a. User steering: finish current iteration and test; no new version started. Receipts build/finals/20261008-akaashi06-submit/; monitor/collection build/finals/heartbreaker-iteration/akaashi06-series/.

## Akaashi 06 current iteration — finished

Heartbreaker test1415322–1415326 completed **1–4**: Default won; Autarky, Prisoners Dilemma, Slithery Fight and Stripes lost. All five replays collected; total/queen/longest curves and linked death/split diagnostics are under `build/finals/heartbreaker-iteration/akaashi06-series/review/`. Own bot TLE/invalid-action faults: 0. Authenticated post-test read verifies20296 (v108) sole active. No next version started.

Autarky/Prisoners Dilemma/Stripes retain early food/population deficits (r50 total A/B25/50,3/38,2/18 respectively). Slithery Fight leads at r100143/114 and r300160/130 but loses its queen at r198 and substantial late heads (largest25 at r459); late material/queen safety remains incomplete. Default won despite queen death at r66, with strong early economy (r10056/19). Results use fresh server seeds, so no causal strength improvement is established by the single win.

## Akaashi 07 — local hotspot capacity (8 October 2026)

Latest user request: maintain centre control while sending surplus resources to attack and claim other hotspots. This authorizes a focused local candidate; the earlier continuous server loop remains paused. Trigger is Trophy [1416376](https://game.battlecode.au/visualiser?match=1416376), Team A. Measured at r100: A85/B20 segments, A32/B8 units; 16 A heads and zero B heads inside the illustrative centre box x/y7–17. At r125, 17 of34 A heads remain there. Food collection reverses from82/28 over r50–99 to64/81 over r100–149, then72/105 over r150–199. A queen survives until r309; B queen died at r17. Congestion contributes a plausible economy/distribution weakness, but these observations do not prove it is the sole cause of defeat.

Code finding: `radio_density_factor` returns1.0 for currently visible targets, bypassing the radio crowding penalty. 07 adds local identity-based reservations during r50–289: a resource with >=4 nearby visible allied heads reserves the nearest two plus one per enemy head within five toroidal Manhattan cells; ties use IDs. Surplus collectors value that resource at3%. The factor also applies to remembered-pearl fallback. Ordinary split production is suppressed at >=5 nearby allies exceeding that enemy-adjusted capacity. Queen/crown/feed roles, early rescue and escape splits retain their behavior; attacks retain existing rules. No map identifier or fixed centre coordinates enter the policy.

Limitations: these are per-target local reservations, not a persistent hotspot squad or global command. Different views and terrain can disagree, multiple nearby targets can retain different defenders, and sonar density packets lack IDs. The change encourages expansion but does not explicitly assign coordinated attack groups.

Measured validation: `python3 tests/test_akaashi_hotspot_capacity.py` passes; the six existing safety CPP fixtures compiled against07 pass (queen escape E, queen strike, threatened split B, visible body with `-DFIXED`, sprint escape, late material). Four native fixtures vs06, Trophy/Default, both seats, seed81014: Trophy1–1, Default1–1; total **2–2**, no runner errors or TLE/invalid-action replay faults. This screen does not establish stronger play. On Trophy r100, candidate A8/22 central heads vs parent A9/20 in the paired fixture; this is descriptive, with adaptive interactions, not an isolated causal estimate. Metered Trophy same seed/both seats finishes **1–1**, matching native winners, zero runner errors or candidate TLE/invalid-action faults. Candidate peak9.9M points per turn, p99<=8.0M. This is a focused runtime check.

Artifacts: `build/finals/centre-expansion-1416376/` for server replay/metadata, measured windows and spatial summaries, and compiled safety fixtures; `build/finals/20261008-akaashi07-screen/` for frozen sources, manifest, replays and spatial audit; `build/finals/20261008-akaashi07-runtime/` for the focused metered check. No server mutation or promotion.

07 source fingerprint: `24936696c026e2ac457852b9007255dd5cf390ed7c78ea95cb7405552f8cac3a`.


### User-requested Heartbreaker test — 8 October 2026

Archive `build/finals/20261008-akaashi07-submit/bot.zip`, 3,942,992 bytes, SHA256 `05e3b9c81bbb959dc336e225b619fbd8dadb8fd95bba079d0cfd6f02fe5c142e`; all archived files byte-verified against local candidate. Uploaded as **20333 (v109)**, `LV-akaashi-07-hotspot-capacity-05e3b9c8-ai`, sourceHash `76e6ba9a0eec83c8ab2ebd405e48bb9028117f2452bbef350f3cbb7d67b485c6`. Server compile succeeded; API readback verified 20333 sole active. At user request queued unranked Heartbreaker team62 on all seven losses from series 1416361–1416377: **1418905 Australia, 1418906 Autarky, 1418907 Devil, 1418908 Maze, 1418909 Prisoners Dilemma, 1418910 Stripes, 1418911 Trophy**, series `d80af811-b386-40c0-9572-08f80742afb0`. Each detail readback verified expected map, teams7/62, unranked=true. All seven completed **2–5**: wins Devil/Trophy; losses Australia, Autarky, Maze, Prisoners Dilemma and Stripes. Zero own TLE/invalid faults. Full curves and linked death/split diagnostics in `build/finals/heartbreaker-iteration/akaashi07-series/review/`; replay/metadata receipts in the submit directory. These fresh server seeds are a retest, not a matched causal estimate. No next iteration started.


### Akaashi 07 seven-map results

Server series `d80af811-b386-40c0-9572-08f80742afb0` completed **2–5** with zero own TLE/invalid-action faults. Devil and Trophy wins. Australia lost despite totals122/29 r100 and217/71 r200; queen died by H2H r60, large 57-length self death r497. Autarky has early deficit14/43 r50, queen H2H r66. Maze totals46/66 r100, queen H2H r260. Prisoners Dilemma totals7/16 r50, queen H2H r49. Stripes totals5/22 r50, queen wall death r64. Curves and linked event diagnostics: `build/finals/heartbreaker-iteration/akaashi07-series/review/`. The five losses show that local capacity change did not clear those maps in this one retest; fresh seeds prevent causal attribution. Stop here; prior iteration loop remains paused until requested.


## Akaashi 08 — escort a queen from a pursuing equal dragon

Team A Australia match1418905. The user observed an interception opportunity around visualizer round48. Existing history has dragon21 repeatedly moving west while enemy10 shadows queen1. The replay's turn order is key: when 21 acts at protocol round47, B10 has already moved east. A direct north move onto its previous head cell would be unsafe, but stepping north to (34,27) puts A21 in B10's next eastward cell. On protocol r48, B10 hits A21 head-on; both equal length-two dragons die. Visualizer/replay round labels differ by one in this fixture: protocol r47 is the corresponding setup action.

`akaashi-08-queen-intercept` forks07 with a general visible-queen escort potential. When a comparable enemy is within five steps of a visible queen and this dragon is the nearest visible nonqueen ally, safe movement scores reward closing toward both queen and pursuer. The ordinary simulator and enemy-reach penalties remain active, so the unit cannot route into an already occupied enemy body cell. It uses observations and does not identify this map or dragon by ID. The rule positions an escort; it does not assert an immediate legal trade on protocol r48.

Validation: original server replay reproduced through the official engine at seed `cb06256202a7d9f9`, 31,975 turns, zero observation mismatches and zero extra turns. On the reconstructed dragon21 history, Akaashi08 changes the setup action at protocol r47 from W to N. A scripted branch uses Akaashi08 for queen1 and escort21 from r47, with recorded actions for all other agents. The enemy10/escort21 mutual H2H occurs at r48; the queen survives and Akaashi's side wins at r181 with queen length3. The opponent does not adapt, and altered board states make some later recorded commands invalid (21 invalid-action deaths in branch), so the terminal win is not strength evidence; the direct escort trade and queen survival are the targeted observations. The branch is a counterfactual, not a live server result.

The hotspot allocation regression and six Akaashi safety regressions pass against08. Source fingerprint `3538265a77e7355410d97bc989fe5595ae14b7317ec29d4429539c6aed151d8f`. Local source and branch artifacts: `bots/akaashi-08-queen-intercept/` and `build/finals/queen-intercept-1418905/`. Akaashi08 was not uploaded; 20333 remains the active server submission.

## 8 October 2026 — six-snapshot family round robin

The user requested the best Akaashi snapshot under a 500-game cap. The frozen
roster at run start was Akaashi 01–06. On 16 maps, every unordered pairing was
played in both seats on every map: 480 core games, 160 per snapshot and 32 per
pair. Akaashi 02 ranked first at 88–72, narrowly ahead of 04 (86–74) and 03
(85–75). This is a native development ranking, not promotion evidence. Newer
07 and 08 were added to the workspace after the roster was frozen and are not
included. Full head-to-head and per-map results are in the
[experiment log](finals-campaign/EXPERIMENT_LOG.md#8-october-2026--akaashi-01-06-family-round-robin).

## Akaashi 09–12 composite candidates — 8 October 2026

The user asked for a new Akaashi family that combines the useful behaviors
from the line and accounts for untested snapshots 07/08. Akaashi 08 already
inherits the 01–07 behavior stack. I tested variants rather than assuming
that the newest cumulative snapshot was strongest:

| Snapshot | Change | Focused line result |
|---|---|---:|
| 09 `akaashi-09-adaptive-capacity` | Smooth surplus-resource target discount from 45%, tapering to a 12% floor | 44–52 vs 01–08 (96 games) |
| 10 `akaashi-10-ranked-capacity` | Steeper graded discount from 12%, tapering to a 3% floor | 53–55 vs 01–09 (108 games) |
| 11 `akaashi-11-escort-expansion` | Disable per-target hotspot discounts; retain crowded-production suppression and 08 escort | 57–63 vs 01–10 (120 games) |
| 12 `akaashi-12-queen-strike-escort` | Start from 02, then port 08's general queen escort/intercept movement bonus | **71–61 vs 01–11 (132 games)** |

The 12 schedule played both seats against every opponent on Autarky, Default,
Prisoners Dilemma, Slithery Fight, Stripes, and Trophy (12 games per opponent).
Its direct results were 5–7 vs01, 7–5 vs02, 6–6 vs03, 5–7 vs04, 5–7 vs05,
7–5 vs06, 7–5 vs07, 9–3 vs08, 8–4 vs09, 7–5 vs10, and 5–7 vs11. Per-map
results were Autarky13–9, Default10–12, Dilemma14–8, Slithery Fight12–10,
Stripes11–11, and Trophy11–11. It beats the original 01–08 group in aggregate
51–45 and the full 01–11 pool 71–61, with zero runner errors. The experiment
does **not** show that one bot beats every Akaashi version: 12 lost to01,04,
05, and11, and tied03.

A 40-game follow-up focused on 12's weak maps (Autarky, Default, Slithery
Fight, Stripes) against01,03,04,05, and11 finished **16–24**, zero runner
errors. In particular, Default remains a weakness. That follow-up should
remain separate from the balanced 132-game line screen; the reweighted total
would obscure why it was selected.

All fixtures were native `unswbc 1.2.9`, with replay files retained and
sandbox metering disabled. No runner errors occurred; at the time of the
original screen, replay feature analysis and sandbox runtime checks had not
been run. The later replay-feature analysis is summarized below. The hotspot regression
`python3 tests/test_akaashi_hotspot_capacity.py` passes for06,07,09,10, and11.
The tournament compiles and runs all snapshots, including12. These are
development screens on six maps, not a promotion-quality unseen-map result.
At the time this screen was recorded, 12 remained local and experimental; no
server upload or active-bot change had been requested.

Artifacts and machine-readable stats:

- `build/finals/20261008-akaashi09-lineup-96/` — standings, manifests, logs,
  and replays for the first composite.
- `build/finals/20261008-akaashi10-lineup-108/` — standings, manifests, logs,
  and replays for the second composite.
- `build/finals/20261008-akaashi11-lineup-120/` — standings, manifests, logs,
  and replays for the third composite.
- `build/finals/20261008-akaashi12-lineup-132/` — frozen main comparison,
  plus `akaashi12-head-to-head.csv` and `akaashi12-per-map.csv`.
- `build/finals/20261008-akaashi12-hard-map-confirm-40/` — focused weak-map
  follow-up against the five selected opponents.

The four main candidate screens and the follow-up ran 496 matches total. Run
IDs: `5524174a13fd444ead1d0c0ff276c6db`,
`0fd96369bae6403e9266257ec2ffc717`,
`80a9eb51c9ef4ee79911ebd40f66929d`,
`fff9e6ee653a493ca67b30d684f90cc7`, and
`db7d17c3f54d4dd39851a7e5a48b3def`.

### Replay-feature comparison

I decoded the retained replays with the registered F1 feature extractor and
summarized the features documented in [`docs/analysis/FEATURES.md`](analysis/FEATURES.md).
The comparison covers two cohorts on the same six maps: a balanced 01–06
round robin (180 games, 60 appearances per bot) and the 12-focused screen
(132 games, 12 games against each of 01–11). They share maps, but not an
identical opponent distribution; use the 12-game head-to-head row for each
opponent when comparing those bots directly.

| Sample / bot | Record | Win rate | Dragons @100 | Total @100 | Longest @100 | Pearls @100 | Pearls @499 | Deaths / 1k dragon-turns | End longest margin | End total margin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01–06 shared-map RR — 01 | 24–36 | 40.0% | 20.9 | 50.7 | 3.47 | 118.9 | 554.0 | 18.35 | −1.05 | +1.9 |
| 01–06 shared-map RR — 02 | 34–26 | 56.7% | 20.9 | 51.2 | 3.63 | 118.7 | 572.4 | 17.88 | −0.50 | +6.6 |
| 01–06 shared-map RR — 03 | 30–30 | 50.0% | 20.9 | 52.1 | 3.67 | 120.9 | 577.9 | 18.54 | +1.38 | +4.3 |
| 01–06 shared-map RR — 04 | 31–29 | 51.7% | 20.6 | 50.4 | 3.75 | 118.7 | 559.5 | 17.81 | +1.77 | +3.9 |
| 01–06 shared-map RR — 05 | 28–32 | 46.7% | 20.3 | 49.9 | 3.78 | 120.1 | 545.3 | 19.57 | −2.15 | −13.9 |
| 01–06 shared-map RR — 06 | 33–27 | 55.0% | 21.0 | 51.2 | 3.72 | 120.8 | 538.1 | 18.13 | +0.55 | −2.9 |
| 12 line screen — 12 | 71–61 | 53.8% | 20.4 | 50.0 | 3.66 | 108.4 | 529.0 | 16.70 | +0.30 | +2.1 |

These are side-game means, not an opponent-adjusted strength estimate. Early
material is similar across the older six and 12; the 01–06 screen averages
roughly 119–121 pearls by round 100, while 12's broader opponent pool averages
108. The 12 screen's per-opponent records show the composition clearly: 12
went 35–37 against 01–06, then 36–24 against 07–11. Its overall 71–61 score
therefore does not mean it outperformed the entire older line. The 12-game
direct comparison with 02 was 7–5: 12 averaged 553.6 vs 473.3 pearls at the
last checkpoint and an end total margin of +11.7 vs −11.7, while 02 averaged
slightly more early total material at round 100 (49.7 vs 47.4). This is
encouraging direct evidence for 12, but too small and schedule-specific to
replace 02's 34–26 result in the separate balanced 01–06 pool as the strongest
measured family result.

Map results for 12 were Autarky 13–9, Default 10–12, Prisoners Dilemma 14–8,
Slithery Fight 12–10, Stripes 11–11, and Trophy 11–11. Its lower round-100
pearls in the 12-run than in the older round robin mainly reflects the
opponent/map interactions; it should not be interpreted as an intrinsic
economy regression without matched same-opponent contrasts.

The extraction produced 312/312 decoded games, 624 side rows, and 2,808 V0
feature-check rows with zero failed identities. It recorded no TLEs or
invalid-death events. These are replay bookkeeping/fault indicators, not
sandbox CPU-limit measurements. The legacy shared-map subset is a balanced
180-game slice of the original 480-game round robin; it is not a replacement
for that full 16-map result.

Full extracted features and summary outputs are under
`build/finals/20261008-akaashi-replay-stats/`: `registered-feature-summary.csv`
and `registered-12-head-to-head.csv` retain means and medians for all extracted
numeric features; `bot-summary.csv`, `by-map.csv`, `12-head-to-head.csv`, and
`12-vs-02.csv` provide compact tables. Per-side source features, death events,
and check rows are in the two `extracted-*` directories. Definitions and
units are in [`docs/analysis/FEATURES.md`](analysis/FEATURES.md).

### User-requested upload — Akaashi 12

At the user's request, uploaded the frozen Akaashi12 archive as submission
**20432 (v110)**, `LV-akaashi-12-queen-strike-escort-634cb502-ai`. The archive
is 3,940,958 bytes (SHA256
`634cb502b90b3f320914de853c3b6f2df1f7264650557aa8fe0ec8669bbe56d9`); the
server sourceHash is
`fa2be5835f99045d642111a6c803cdbe34d04956a39ec5fcfc496dffbe22ce7d`. Server
compilation succeeded. Uploading auto-activated12 asynchronously, so I
re-activated the pre-existing **20333 / Akaashi07** submission under the
campaign's active-entry gate. Final authenticated readback confirms 20333 is
the sole active submission and 20432 is idle. 12 was submitted but not
promoted: its current development evidence does not clear the strength gate,
and no server match or sandbox runtime validation was run.

Receipts: `build/finals/20261008-akaashi12-submit/`, including
`bot.zip`, `archive-manifest.json`, `preflight.json`, `upload.json`,
`restore-readback.json`, and `final-readback.json`.
