# Kenma free lane

State: **ACTIVE**, updated 2026-10-05 05:34 UTC. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma. Keep iterating until told to stop. No contest API, key access or submission. Live ops reports03 trial submission17388 active, ranked window starts05:02UTC; Kenma never touched the server.

## Provisional best

**kenma-03-pocket-queen**, runtime e60733a926fc056a6cd596582c64c535e461a18679ae1d97f4a725a4cb4612a1.
- Carthage **58–44/102**; Kageyama **61–41/102**; current live Asahi05 **57–45/102**; requested Bokuto04 **54–48/102**; 17 ranked maps × both seats × seeds1–3, zero errors.
- Zoo **220–52/272**, zero errors, six fewer wins than supplied Carthage226–46 reference. Same-host parent diagnostic64 exactly matched reference57–7 versus03 at49–15 on the same fixtures; pool deficit confirmed on those maps, no promotion claim.
- Four heavy-map sandbox games: max **10,910,667** points, first-turn max10,814,937, zero errors. Zip3,923,010 bytes.
- Extra Schooltime seed5 check **2–0**, both queens survive500 rounds, zero errors, sampled population63. Reserve-slot burst risk is not disproven.
- Full by-map/opponent scorecard in bot README. Outputs main build/kenma/k03-v-carthage-s123/, k03-v-kageyama-s123/, k03-zoo-s1/, deploy/kenma-03-pocket-queen/, k03-schooltime-s5/.
- Best/full scorecard reported on main BOARD. Bokuto04 requested cross-match completed54–48; newer Bokuto07 reported60–42 versusCarthage04:33, its full scorecard remains pending. Reserved **seeds11–13 and new maps remain untouched**.

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
| 13 keeper-search-prior | Existing keeper model inside parent movement search | 54–48 | Rejected; below03 |
| 14 queen-corridor-caution | Prefer visible turning room for short original queens | Smoke3–1 | Activated, same winners as12; full screen held |
| 15 pocket-without-reserve | Remove only08 global one-slot reserve | Probes8–0,6–2 | Pool recovery, queen deaths3/8; no promotion |
| 16 lossless-model-text | Base64 byte-plane source encoding of08 | Equivalent control | All node/probability parity and4 sandbox games pass |
| 17 stacked-direction-prior | A5-400 combined encoder/HB/HB-probability prior | 46–56 | Rejected; full102 replay fallback audit zero |
| 18 entropy-matched-prior | Renormalize17 prior with exponent1.61 | 49–53 | Rejected;102 replays read, zero fallback |
| 19 pocket-sprint | Local two-step length control, no global reserve | Probes8–0,6–2 | All Schooltime queen verdicts2–0;20 aims to retain length3 |
| 20 pocket-countdown | Prefer length3 unless observed food/spawn needs slack | Probe8–0 | All queens survive at2; end-length objective not met |
| 21 proven-reserve | Relay proof queen is outside any small sealed pocket | **60–42/102** | First Carthage gain over03; full scorecard outstanding |
| 22 keeper-split-prior | Existing keeper probabilities adjust ordinary queen split scores only | Prepared, held | Sanitizers pass;163-turn stream unchanged; no games |
| 23 corridor-only |14 corridor filter on08, without12 orbit | Smoke5–3, held | Same8 winners as03; both Weakhold queens still die |
| 24 space-reserve | Asahi05 space filter plus21 conditional reserve | **Asahi05 58–44/102** | Zero errors;all102 replay review running |
| 25 occupied-bed |20 pressure check respects projected bed occupancy | Smoke8–0 | All queens alive;four3/four2;full held |
| 26 space-noreserve |25 pocket control plus exact Asahi05 space filter | Direct03 full102 running | Source parity and sanitizers pass |
| 27 queen213-blend |21 plus queen-only50/50 geometric direction blend | Prepared | Export2832-row parity,runtime997-turn checks;no games |

Outputs: main build/kenma/kNN-v-carthage-s123/score.json for completed screens. Runtime manifests pin source, fixtures, engine and compiler. Never edit measured runtime snapshots.

## Active workers and next steps

Current bounded work, nice15, max4 heavy workers /6GiB; game guard5GiB:
1. Kenma26 versus03 direct102 under run-k26-best.py / parent30438 / session22224, log k26-v-k03-s123.progress.log; all102 replays read on completion. Runtime0dd6bb5a97fb1f448ee19fa085c1b82bc70cb46b97939da203b63517a9c71438.
2. Kenma24 Asahi05 full102 complete58–44,zero errors; parent75540 / k24-after-crossmatch.py / session1052 reconstructs and audits all102. Runtime716eee526ab7456e29bafe590ec9a63d0ad405913110abef45e771108ba102c3. Smoke9–3,all12read,474 proof markers andzero onSchooltime.
3. Kenma21 matched four-map64 pool complete57–7,zero errors,vs03 at49 andparent57:School15,UNSW13,Australia14,Maze15 wins. pool-after-k21.py / parent76289 / session90020 reconstructsall64 then writespairedreport. Exact deployment waiter replaced while idle:no game interrupted;old68440/session3126 exit143. Sole current waiter deploy21-after-pool.py / parent29325 / session60858 waits full64 replay review and at most1 other game worker, then four heavy sandbox games with explicitPASS required. scorecard21-after-deploy.py / session17585 waits exact29325 andPASS, then runs full pool272 (hard-link/reuse64 successful fixtures and their read diagnostics;only208new games) andKageyama102,one worker each. Reads all new pool replays and12 retainedKage replays;stops for review. No other21 panels queued.
4. Kenma27 prepared, no games/queue. Existing213 model source SHAaa2fc510ac06766a25b6070a98789b8984dc3b30d26873365068a8e03b6d1bee. Lane-local exporter corrects478 missing_type=None NaN routes;2832 real/missing input vectors matchLightGBM,maxerror2.84e-8,allargmaxequal. Measured ancestors/sharedtools unchanged. Exact270feature binding;classF/R/B/L,FRL normalized. Runtime997turns:922control actions unchanged,75queen activations,no fallback,oneBround40change. Blend mathsanitizerspass;zip~4.02MB,exactmetadata teacher213/package.json. Deploy pointsoutstanding.

Both Chair-requested03 cross-matches complete and posted:Asahi57–45,Bokuto04 54–48,zeroerrors,12retainedreplaysread each. Kenma03 trialreportedlive byDaichi05:11:submission17388,first rankedseries05:02;trialresultsawaitLiveops. Candidate21 remains promising60–42Carthage and57–7four-map pool;03remainsprovisionalbest until broader scorecards complete. No new ladder request.

Third-worker experiments23/25areterminal anddocumented inREADMEs. Body-segment proof diagnostic examined2452processes fromeight21UNSWreplays:only1process releases2turnsearlier,soheldwithoutanewbot. Outputs reserve-body-seed-probe.json;toolprobe_reserve_seeds.cpp. No newmodeltraining. Reservedseeds11–13/newmapsuntouched. maps/live_var stillabsent05:32; --map-root supportsread-only variants withpinnedhashes whenavailable.

## Evidence and diagnostics

12 fixes two integration mistakes in frozen10/11. World.seen is round+1; World.bed is -1 for observed no-bed, 0 unknown, 1 bed. tools/kenma/test_orbit.cpp now feeds an actual protocol block through helper parsing and World::sense and requires activation before testing80 persistent synthetic turns and hazard guards. ASan/UBSan pass. Earlier mistaken fixtures retained as test_orbit_v10.cpp/test_orbit_v11.cpp. Real Weakhold/Australia smoke seed1 both seats3–1, zero errors; all four replays activated (168/140 Weakhold,144/239 Australia log entries) and were analyzed. Outputs k12-orbit-smoke/, k12-smoke-diagnostics.json.

The Weakhold B queen left its orbit, entered a food-filled corridor, split at the dead end and died at round162. Reconstructed protocol replay reproduces all163 queen actions exactly. An optimistic terrain lookahead cannot reject entry at157 because the endpoint is outside vision; it proves the trap at158, after commitment. **Not a demonstrated fix.** Probe tools/kenma/test_queen_corridor.cpp; input/output/finding main build/kenma/orbit-audit/. No new bot based on this probe yet.

13 copies08 and uses the already exported04 keeper model only as the original queen's first-step log prior, conditioned on its four movement classes, weight1.0. Parent search still evaluates room, threat, growth and sprints and chooses splits. No orbit or new training. Conditioning, all four facing rotations and zero-mass floor verified under sanitizers in test_keeper_prior.cpp. Prior hard-action variants' poor results motivate this separate integration experiment.

08 storage evidence: all824,580 nodes reconstruct exactly;21,024 native probability vectors bit-identical including1,024 NaN cases. Arrays6,596,640→3,300,848 bytes. Four sandbox outcomes, rounds, deaths and noncompute stats identical03; max10,968,532 points, firstturn10,850,012, zero errors; zip3,591,843. Evidence lossless-direction/ and deploy/kenma-08-lossless-direction/.

Queen model:26,820 oracle keeper rows;81.75% held-out action accuracy on17 development series; all19,627 move-row argmax export parity. Donor model:208,158 teacher306 rows; validation precision99.69%, recall73.87% at preselected0.9;20,000 native threshold decisions match. High-confidence donor predictions mostly describe terminal traps; full09 did not improve play. Offline accuracy is not strength evidence. Training outputs queen-action-v1/ and feeder-v1/.

## Limits and runner

At most4 heavy workers and6GiB aggregate RSS; normally use2 game workers with guard5GiB after earlier overlapping Ouroboros runs hit the guard. Fresh engine each game. Interrupted attempts were archived and retried, never counted as bot losses. Latest output3.77GB, cap30GB; free disk240.5GiB, floor40GiB. All outputs main build/kenma/. Do not touch other lanes, HEAVY.lock or queue.

panel.py uses engine1.2.3, clang++-O2-std=c++20, current Python opponents via toolkit /usr/bin/python3 3.9.6. Map/roster hash39961c55d0e6 and parent runtime match supplied reference. Resume --retry-errors only after confirming old process terminal; retry regression passed. --logs enables activation logs and retains all selected replays with --keep-replays; ordinary runs retain Schooltime/Weakhold only. Read retained replays. deploy.py registers compiler/game helpers as killable process groups and propagates guard termination; verified with mocks and actual08 deployment.

