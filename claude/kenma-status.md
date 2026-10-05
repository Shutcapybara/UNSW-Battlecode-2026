# Kenma free lane

State: **ACTIVE**, updated 2026-10-05 03:06 UTC. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma. Keep iterating until told to stop. No contest API, key access, submission or ladder request.

## Provisional best

**kenma-03-pocket-queen**, runtime e60733a926fc056a6cd596582c64c535e461a18679ae1d97f4a725a4cb4612a1.
- Carthage **58–44/102**; Kageyama **61–41/102**; 17 ranked maps × both seats × seeds1–3, zero errors.
- Zoo **220–52/272**, zero errors, six fewer wins than supplied Carthage226–46 reference. Same-host parent diagnostic ongoing; no promotion claim from this pool result.
- Four heavy-map sandbox games: max **10,910,667** points, first-turn max10,814,937, zero errors. Zip3,923,010 bytes.
- Extra Schooltime seed5 check **2–0**, both queens survive500 rounds, zero errors, sampled population63. Reserve-slot burst risk is not disproven.
- Full by-map/opponent scorecard in bot README. Outputs main build/kenma/k03-v-carthage-s123/, k03-v-kageyama-s123/, k03-zoo-s1/, deploy/kenma-03-pocket-queen/, k03-schooltime-s5/.
- Best/full scorecard reported on main BOARD. No other free-lane best found at last inspection. Reserved **seeds11–13 and new maps remain untouched**.

## Candidate record

Completed Carthage screens use the same102 fixtures and have zero errors.

| Version | Change | Carthage W–L | Disposition |
|---|---|---:|---|
| 01 free-combat-sprint | Combat free triples | 48–54 | Rejected |
| 02 topteam-prior | A1-400 development direction model | 42–60 | Rejected |
| 03 pocket-queen | Proven sealed-pocket rescue, donor culling, one reserved slot | 58–44 | Provisional best |
| 04 keeper-action | Seven-class queen imitation from round0 | 50–52 | Rejected |
| 05 post-opening-keeper | Same clone starts round25 | 54–48 | Rejected |
| 06 pocket-space | 03 plus exact AsahiK16 space-filter sources | 57–45 | Rejected |
| 07 keeper-moves-parent-splits | 04 with parent split decisions preserved | 51–51 | Rejected |
| 08 lossless-direction | Reversible32-bit direction node encoding | Equivalent control | Native exact parity and four sandbox games passed |
| 09 learned-donors | Teacher306 nonqueen cull classifier | 57–45 | Rejected; three changed summaries, one win lost |
| 10 short-queen-orbit | Local four-cell keeper loop | Cancelled | Wrong freshness convention; source/attempts retained |
| 11 current-view-orbit | Fix freshness, add activation logs | Smoke2–2 | Zero activations; wrong no-bed convention; frozen |
| 12 observed-empty-orbit | Require observed no-bed=-1 | Running102 | Smoke3–1 with activation in all four games |
| 13 keeper-search-prior | Existing keeper model inside parent movement search | Prepared | Conditional next screen; integration tests pass |
| 14 queen-corridor-caution | Prefer visible turning room for short original queens | Queued smoke | Recorded avoidable entry redirects; no real games yet |

Outputs: main build/kenma/kNN-v-carthage-s123/score.json for completed screens. Runtime manifests pin source, fixtures, engine and compiler. Never edit measured runtime snapshots.

## Active workers and next steps

Exactly **two game workers**, nice15:
1. Kenma12 Carthage102, process66712, unified session15167. Log main build/kenma/k12-v-carthage-s123.progress.log. First34 complete19–15 (03 scored18–16 on those fixtures); no conclusion from partial results.
2. Same-host Carthage pool diagnostic64, parent process20374 / session69469, panel64885. Schooltime/UNSW/Australia/Maze × eight opponents × both seats × seed1. Log parent-pool-diagnostic-s1.progress.log. Schooltime complete14–2, matching supplied reference; remaining maps running. Reference totals57/64; 03 totals49/64. This is post-result mechanism/portability evidence, not independent strength validation.

Queued sequence main build/kenma/after-k12.py (session38679) waits for exact66712 and clean102 completion. If12 wins>58, run12 versus03 on102 fixtures; otherwise screen13 versusCarthage102. Both choices were dry-run-previewed. No additional games while both current workers are occupied. Any best candidate still needs Kageyama/other posted free-lane/pool scorecards, exact-source deploy, and independent reserved validation before a ladder request.

12 runtime ab99829d2d7b5073fdac35682d1fba07d5ba6dea4e52b55db3f2bfcd2a7add68. 13 runtime0446146e81c6f8328ef85eb5c3210dbd07d5617e7e0a06e1a595fa0100197c67; initial archive3,698,474 bytes. No13 games yet.

## Evidence and diagnostics

12 fixes two integration mistakes in frozen10/11. World.seen is round+1; World.bed is -1 for observed no-bed, 0 unknown, 1 bed. tools/kenma/test_orbit.cpp now feeds an actual protocol block through helper parsing and World::sense and requires activation before testing80 persistent synthetic turns and hazard guards. ASan/UBSan pass. Earlier mistaken fixtures retained as test_orbit_v10.cpp/test_orbit_v11.cpp. Real Weakhold/Australia smoke seed1 both seats3–1, zero errors; all four replays activated (168/140 Weakhold,144/239 Australia log entries) and were analyzed. Outputs k12-orbit-smoke/, k12-smoke-diagnostics.json.

The Weakhold B queen left its orbit, entered a food-filled corridor, split at the dead end and died at round162. Reconstructed protocol replay reproduces all163 queen actions exactly. An optimistic terrain lookahead cannot reject entry at157 because the endpoint is outside vision; it proves the trap at158, after commitment. **Not a demonstrated fix.** Probe tools/kenma/test_queen_corridor.cpp; input/output/finding main build/kenma/orbit-audit/. No new bot based on this probe yet.

13 copies08 and uses the already exported04 keeper model only as the original queen's first-step log prior, conditioned on its four movement classes, weight1.0. Parent search still evaluates room, threat, growth and sprints and chooses splits. No orbit or new training. Conditioning, all four facing rotations and zero-mass floor verified under sanitizers in test_keeper_prior.cpp. Prior hard-action variants' poor results motivate this separate integration experiment.

08 storage evidence: all824,580 nodes reconstruct exactly;21,024 native probability vectors bit-identical including1,024 NaN cases. Arrays6,596,640→3,300,848 bytes. Four sandbox outcomes, rounds, deaths and noncompute stats identical03; max10,968,532 points, firstturn10,850,012, zero errors; zip3,591,843. Evidence lossless-direction/ and deploy/kenma-08-lossless-direction/.

Queen model:26,820 oracle keeper rows;81.75% held-out action accuracy on17 development series; all19,627 move-row argmax export parity. Donor model:208,158 teacher306 rows; validation precision99.69%, recall73.87% at preselected0.9;20,000 native threshold decisions match. High-confidence donor predictions mostly describe terminal traps; full09 did not improve play. Offline accuracy is not strength evidence. Training outputs queen-action-v1/ and feeder-v1/.

## Limits and runner

At most4 heavy workers and6GiB aggregate RSS; intentionally use2 game workers with guard5GiB after earlier overlapping Ouroboros runs hit the guard. Fresh engine each game. Interrupted attempts were archived and retried, never counted as bot losses. Output about0.9GB, cap30GB; free disk253GiB, floor40GiB. All outputs main build/kenma/. Do not touch other lanes, HEAVY.lock or queue.

panel.py uses engine1.2.3, clang++-O2-std=c++20, current Python opponents via toolkit /usr/bin/python3 3.9.6. Map/roster hash39961c55d0e6 and parent runtime match supplied reference. Resume --retry-errors only after confirming old process terminal; retry regression passed. --logs enables activation logs and retains all selected replays with --keep-replays; ordinary runs retain Schooltime/Weakhold only. Read retained replays. deploy.py registers compiler/game helpers as killable process groups and propagates guard termination; verified with mocks and actual08 deployment.

2026-10-05 03:06 UTC: Previous turn made concrete progress (12 integration tests and real activation,09 result,13 prepared); current12, parent64 and waiting sequences revalidated through live session handles. Kenma14 prepared from12: short original queens prefer a legal route with visible turning room (branch, loop or portal traced through at most8 observed corridor cells) when available, retaining parent choices otherwise. This is a heuristic, not a proof about unseen endpoints. The initial immediate-degree test was insufficient because a safe narrow loop also has only one onward edge; corrected before measurement. Recorded-observation test now redirects round157 south and preserves fallback at158 under sanitizers. Log kenma_corridor_filter. Runtime c356ab501d912e7dd09fdc18a4c5e41951a4831e5726c1de2ec3de76d69083ed. Queued main build/kenma/after-parent-diagnostic.py (session33367) waits exact20374 and clean64 completion, then runs four Weakhold/Australia games (both seats,seed1,logs/replays). It stops for activation audit before any full14 screen. No extra concurrent game workers.

Pool mechanism evidence from completed same-host UNSW fixtures: parent wins four games lost by03 (Fenrir B,Yuna B,Chaewon B,Gavroche A). Death-event prefixes match until rounds68–77; sampled populations then diverge around the cap (parent64 versus03 at63). This supports investigating the global one-slot reserve as a cause, but full64 and a controlled reserve ablation are still required. No random APIs found in those four opponent source trees. A premature partial-log claim that Schooltime differed from the supplied reference was corrected: actual completed parent Schooltime14–2 matches reference;03 is15–1.
