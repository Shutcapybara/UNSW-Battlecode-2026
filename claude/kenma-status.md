# Kenma free lane

State: **ACTIVE**, updated 2026-10-05 03:26 UTC. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma. Keep iterating until told to stop. No contest API, key access, submission or ladder request.

## Provisional best

**kenma-03-pocket-queen**, runtime e60733a926fc056a6cd596582c64c535e461a18679ae1d97f4a725a4cb4612a1.
- Carthage **58–44/102**; Kageyama **61–41/102**; 17 ranked maps × both seats × seeds1–3, zero errors.
- Zoo **220–52/272**, zero errors, six fewer wins than supplied Carthage226–46 reference. Same-host parent diagnostic64 exactly matched reference57–7 versus03 at49–15 on the same fixtures; pool deficit confirmed on those maps, no promotion claim.
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
| 12 observed-empty-orbit | Require observed no-bed=-1 | 54–48 | Rejected; Weakhold/Trauma6–0 offset by losses elsewhere |
| 13 keeper-search-prior | Existing keeper model inside parent movement search | Running102 | Started on clean12 completion; original prior experiment |
| 14 queen-corridor-caution | Prefer visible turning room for short original queens | Smoke3–1 | Activated, same winners as12; full screen held |
| 15 pocket-without-reserve | Remove only08 global one-slot reserve | Queued conditionally | Eight Schooltime and eight UNSW probes after13 if not improved |
| 16 lossless-model-text | Base64 byte-plane source encoding of08 | Equivalent control | All node/probability parity and4 sandbox games pass |
| 17 stacked-direction-prior | A5-400 combined encoder/HB/HB-probability prior | Deploying | Actual4.083MB zip; full feature and prediction parity pass |

Outputs: main build/kenma/kNN-v-carthage-s123/score.json for completed screens. Runtime manifests pin source, fixtures, engine and compiler. Never edit measured runtime snapshots.

## Active workers and next steps

Exactly **two game workers**, nice15:
1. Kenma13 Carthage102, panel38553, parent91562 / session38679, log k13-v-carthage-s123.progress.log. Sequence after-k13.py / session36413 waits exact91562 and clean102 completion: if13 wins>58, run13 versus03 on102 fixtures; otherwise run15 Schooltime8 (seeds1/2/3/5, both seats) then UNSW8 (Fenrir/Yuna/Chaewon/Gavroche, both seats,seed1). All options dry-run-previewed.
2. Kenma17 deployment, parent80091 / session33020, log k17-deploy.progress.log. after-k17-deploy.py / session63263 waits exact80091, passed summary with exact fingerprint, and runtime parity; then starts17 Carthage102 with logs/all replays retained. Audit every retained replay for fallbacks, then inspect losses. No extra concurrent games.

Parent64 completed57–7, exactly supplied map totals;03 same fixtures49–15. Outputs parent-pool-diagnostic-s1/score.json and parent-pool-comparison.json. after-parent-diagnostic/session33367 completed14 smoke3–1; after-k14-smoke/session23315 completed16 deployment. Sessions15167(12),69469(parent64),33367(14 queue),23315(16 queue) are terminal. Kenma14 full screen is held; no strength claim.

16 runtime e4590915c3ef49df22635a8dde10e45adb711bea3bcabd39d360a3434b6608fa;17 runtime1f11fcbb25ebd6a0f75d9dd47804e033800826dd6a83939e94f60d7cadff6961. Best remains03. Any new best still requires full Kageyama/other posted free-lane/pool scorecards, deployment and independent reserved validation.

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

2026-10-05 03:08 UTC: Kenma15 prepared from08 with only the three reserve-limit lines removed from main.cpp; all other runtime files identical. Runtime5b7ecd83917e9178938d1a811f025b1b0916a0fa783f749505ac61578886b659. Dry-run previews: Schooltime seeds1/2/3/5 both seats8 games with replays, then UNSW seed1 both seats against Fenrir/Yuna/Chaewon/Gavroche8 games. Not launched or queued: both workers still occupied. The check must establish whether pocket survival remains reliable without a global slot and whether the pool regressions recover. Main build/kenma/parent-pool-partial-comparison.json records completed paired fixtures, explicitly incomplete. Avoid conclusions before full results.

2026-10-05 03:14 UTC: 12 final54–48/102, zero errors, rejected; full map table in README. All12 retained replays read and analyzed. 13 started automatically on exact clean12 completion. Complete native executable check on the recorded163-turn queen stream:13 changes87 actions;14 changes only round157 (to south), logging5 filter applications. Counterfactual replay choices do not predict game outcomes. Both exact native binaries cached under main build/kenma/bin/.

New packaging avenue: current08 hexadecimal model header compresses to3,539,354 bytes. Lossless byte-plane-separated base64 would compress node data to2,829,065 bytes (all824,580 original32-bit nodes), saving roughly0.7MB before framing. This may enable the stronger combined A5 prior that was previously too large. Copied only existing development fold0 from main build/hinata/r2/battery/A5-u/ (read-only); source SHA6695befe886641235869dfea42d51f42816dec17eb621b037963f230d23b899b, stored in main build/kenma/stacked-prior/. Explicitly truncated to400 rounds and exported: **4 classes**,1600 trees,200,000 nodes,100,800 leaves,1466 features,1,124,584-byte zipped header. Estimated combined package4,013,531 bytes vs4,194,304 cap. **No new bot yet:** actual text framing/archive, exact node and probability parity, feature binding (encoder+HB features+HB probabilities,4-class direction mapping), and sandbox first-turn cost must all be verified. Output model-text-storage/feasibility.json and stacked-prior/{source,export-feasibility}.json. Full800-round source was not accidentally adopted. Next investigate a standalone lossless storage control before the combined learned candidate. At03:14 UTC output1.0GB,free disk252GiB.

2026-10-05 03:26 UTC: This turn progressed via16 and17 source generation, verified native parity,16 successful sandbox and17 launch.16 all824,580 native nodes exact;21,024 bit-identical prediction vectors incl1,024 NaN cases; zip2,950,863, max12,958,553 points, firstturn12,238,377, zero errors in4 heavy-map games. Every gameplay statistic except compute matches08.17 actual archive4,083,138;2,759 turns/40 processes/4 replays give4,044,694 exact feature values,2,759 matching LightGBM argmax, max probability error2.609e-8. Model4 classes F/R/B/L,1600 trees; F/R/L normalized for search, weight1. Original HB probability inputs explicitly rounded to six decimal places to match training. All118 side-file hashes and1193 encoder names verified against source manifest. Tools pack_direction_text.py,verify_model_text.py,prepare_stacked.py,verify_stacked.py; outputs lossless-model-text/,stacked-prior/,deploy/.17 emits kenma_stacked_fallback if binding/inference fails; full run logs needed to audit. No new training or reserved-map exposure.

14 smoke activation audit: Weakhold filter5(A)/9(B) times; Australia0/0. Same3–1 winners as12. Weakhold B queen survives now, A dies at221; Australia queen histories unchanged. All four replays read. This mixed mechanism result and12's54–48 keep14 below priority for a full screen.15 controlled reserve probe remains next conditional use of13's worker.
