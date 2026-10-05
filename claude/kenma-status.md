# Kenma free lane

State: ACTIVE. Updated 2026-10-05 02:58 UTC. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma. No server access, submission or ladder request.

## Provisional best

**kenma-03-pocket-queen**, runtime e60733a926fc056a6cd596582c64c535e461a18679ae1d97f4a725a4cb4612a1.
- Carthage: **58–44**, 17 ranked maps × both seats × seeds 1–3, zero errors.
- Kageyama: **61–41**, same 102 fixtures, zero errors.
- Zoo: **220–52/272**, zero errors, full by-map and by-opponent tables in bot README. Output main build/kenma/k03-zoo-s1/. Six fewer wins than the supplied Carthage 226–46 reference; not a pool improvement. Same-host parent reproduction outstanding.
- Deployment: four sandbox games (Schooltime/UNSW, both seats, seed 1), max 10,910,667 points, first-turn max 10,814,937, zero errors. Zip 3,923,010 bytes at packaging, earlier README but same runtime source. Output main build/kenma/deploy/kenma-03-pocket-queen/.
- Extra development check: Schooltime seed 5 **2–0**, both queens alive through round 499, length 3–0, zero errors. Sampled population reached 63; did not reproduce the prior Shenzhen reserve-1 failure, but burst-cap risk is not disproven. Output main build/kenma/k03-schooltime-s5/ and k03-schooltime-s5-diagnostics.json.
- By-map H2H tables in bot README. Best posted to main BOARD at 01:28 UTC; other free-lane best not found in latest main BOARD inspection. No ladder recommendation yet.

## Candidate record

All completed Carthage screens below use 102 games: 17 ranked maps × both seats × seeds 1–3, zero bot runtime errors.

| Version | Change | Carthage W–L | Disposition |
|---|---|---:|---|
| 01 free-combat-sprint | Combat free triples | 48–54 | Rejected |
| 02 topteam-prior | A1-400 development fold direction model | 42–60 | Rejected |
| 03 pocket-queen | Proven sealed-pocket rescue and donor culling; one reserved slot | 58–44 | Provisional best |
| 04 keeper-action | Queen-only seven-class keeper clone from round zero | 50–52 | Rejected |
| 05 post-opening-keeper | Same clone starts at round 25 | 54–48 | Rejected versus 03; Weakhold 0–6 |
| 06 pocket-space | 03 plus exact Asahi K16 space-filter sources | 57–45 | Not selected; Weakhold +2 wins offset by three losses elsewhere |
| 07 keeper-moves-parent-splits | 04 with learned movement but all parent SPLIT decisions preserved | 51–51 | Rejected versus 03 |
| 08 lossless-direction | 03 with reversible 32-bit model node storage | Equivalent control | Native parity and four sandbox games passed |
| 09 learned-donors | 08 plus teacher-306 nonqueen cull classifier | 57–45 | Rejected; only three score summaries changed, one win lost |
| 10 short-queen-orbit | 08 plus observed empty four-cell cycles for length-2/3 queens | Cancelled | Freshness test repeated a memory convention error; attempts retained |

| 11 current-view-orbit | Fix freshness to round+1; activation logs | Smoke 2–2 | Zero activations: no-bed encoding still wrong; frozen |
| 12 observed-empty-orbit | Require observed no-bed value -1 | Running102 | Smoke3–1, zero errors, activation in all four games |

| 13 keeper-search-prior | Existing keeper movement probabilities inside parent search | Prepared | Conditioning/rotation tests pass; no games yet |

Outputs for completed screens: main build/kenma/kNN-v-carthage-s123/. Kageyama output k03-v-kageyama-s123/. Current sequence after-k05 verified the complete Kenma 05 result, finished the seed-5 probe, then launched Kenma 06; main build/kenma/after-k05.progress.log. No additional games should start until the current two-worker resource allocation has room.

## Evidence informing next choices

The retained Weakhold seed-1 replays show 03 queens dying to walls immediately after splits (rounds 29/44). The 04 queens survive both games (A wins by elimination at round 272, B wins by queen at 500). Delaying control in 05 loses both queens and both games (rounds 29/388). This motivates testing movement-only imitation without suppressing parent expansion. Exact death-event/standing audit: main build/kenma/queen-diagnostics.json; tool tools/kenma/replay_diagnostics.py.

Queen clone training: 26,820 oracle queen turns from keeper teams; action accuracy 81.75% on 17 held-out development series, versus 32.71% majority. Export parity all 19,627 move-row argmax, max error 5.49e-8. Model evidence is not play strength. Output main build/kenma/queen-action-v1/. Model tools use installed torch/lib/libomp.dylib and OMP/BLAS threads 1.

08 model storage: all 824,580 original nodes reconstruct exactly; 21,024 native probability vectors are bit-identical, including 1,024 synthetic NaN cases. Model arrays 6,596,640 → 3,300,848 bytes; initial archive 3,591,664 bytes. Evidence main build/kenma/lossless-direction/report.json. Sandbox first-turn metering passed; this is not a new strength claim.

## Remaining work and bounds

03 pool completed 220–52; investigate the six-win deficit to the supplied reference before any promotion. 06 completed 57–45 with zero errors. 07 finished 51–51; 08 metering passed. Test orbit activation before a full 12 screen. Any stronger candidate gets direct comparison against 03, full Kageyama/other posted free-lane/pool scorecards and exact-source deployment checks. Preserve seeds **11–13 and new maps** for independent confirmation before a ladder request; none used yet.

Nice 15; currently **two** games total (same-host parent64 1, Kenma 12 Carthage102 1), maximum four. Guard at 5 GiB aggregate lane RSS to stay below 6 GiB. Initial 05 two-worker start and later overlapping Ouroboros zoo games hit 5.03/5.06 GiB guards; those interrupted attempts were archived and retried, not counted as bot losses. Two-game concurrency since then. Fresh engine each game; source/fixture manifests pinned; actual engine version logged (unswbc 1.2.3), clang++ -O2 -std=c++20 required by current helper. Resume with --retry-errors only after verifying the previous process terminal. Retry regression passed.

All generated outputs stay in main build/kenma (currently about 0.53 GB); 30 GB ceiling, 40 GB disk floor (about 256 GiB free). Never change measured runtime snapshots. Baseline small reference panel versus Hunter V20 was 6–2, both losses Weakhold, zero errors.

2026-10-05 02:16 UTC: Active sequences: after-k06 waits for exact live after-k05 process and a clean 102-game Kenma 06 score, then runs 08 deployment and 07 Carthage102. after-zoo waits for exact zoo PID and clean 272-game score, then runs 09 Carthage102. Logs main build/kenma/after-k06.progress.log and after-zoo.progress.log. Two game workers retained. Deployment build/game helpers now run in registered process groups so the parent memory guard actually terminates them; mock checks of registration, cleanup and guard propagation passed.

New donor experiment: 208,158 eligible teacher-306 oracle training rows (4,311 culls), 48 training/12 validation series. Fixed 160-round, 31-leaf binary classifier, preselected threshold 0.9: validation 653 TP, 2 FP, 231 FN, 45,430 TN (99.69% precision, 73.87% recall). No original queens; length <= 8, visible allied head, at least two units. All 20,000 native threshold decisions match LightGBM; max probability error 3.24e-8; zip 3,648,802 bytes. Uses binary sigmoid correctly, not generic multiclass softmax. Offline accuracy is not playing evidence. Tools feeder_train.py/prepare_feeder.py; main build/kenma/feeder-v1/. Training used nice -n 15 env DYLD_LIBRARY_PATH=.../torch/lib (setting DYLD before macOS nice was stripped and caused an initial import failure; corrected run succeeded).

Kenma 06 early replay evidence: both Weakhold seed-1 games won; queen survives A, dies at round 285 in B, which still wins on longest dragon. Four completed diagnostic replays audited in main build/kenma/k06-early-diagnostics.json. Full score pending.

2026-10-05 02:21 UTC: Kenma 06 finished 57–45/102, zero errors; 03 retained. after-k06 verified completion and started 08 sandbox metering; 07 follows. Donor mechanism audit: all 299 high-confidence predictions in the 20,000-row export sample have no nominal exit, so high offline precision may mostly reflect terminal traps. Full 09 screen remains queued to establish whether it changes actual play; no strength claim.

2026-10-05 02:24 UTC: 08 exact-source deploy PASS: zip 3,591,843 bytes; max 10,968,532 points including first turns, boot max 10,850,012; four heavy-map games, zero errors. All four outcomes, round counts, death records and non-compute stats match 03. Evidence main build/kenma/deploy/kenma-08-lossless-direction/{summary,parent-game-parity}.json. after-k06 started Kenma 07 Carthage102; zoo remains live and after-zoo will start 09 only on clean full completion.

2026-10-05 02:33 UTC: Kenma 10 prepared and queued behind exact after-k06 PID 94829 / Kenma 07 clean 102-game completion. Runtime 1cde55daabeb13f031a5cb5ed451370ad32b1d2d983a86e3462ba8641797386f. General local short-queen cycle, at least three team units, parent SPLIT and pocket rescue priority. Eight projected single-step turns prove entry/cycle, and fresh terrain/food/body/threat checks repeat every turn. ASan/UBSan behavior checks passed for 80 simulated turns and hazard/population guards. Main build/kenma/after-k07.progress.log tracks the wait and eventual 102-game screen; no strength claim before results.

2026-10-05 02:36 UTC: 03 zoo final 220–52, zero errors; full required local scorecard complete (Carthage 58–44, Kageyama 61–41, pool 220–52, deployment pass). No independent reserved-seed validation yet, and no ladder request given the pool deficit. after-zoo verified 272 clean fixtures and started 09. Reference audit confirms the same 8-bot roster, 17-map list and parent runtime fingerprint; compiler flags both C++20/O2. Current host Python bot interpreter is /usr/bin/python3 via toolkit selection, so cross-host runtime differences remain possible but unproven. Need same-host parent diagnostic on Schooltime/UNSW/Australia/Maze to distinguish this from the reserve behavior.

Baseline audit: both worktree and main map/roster hashes are 39961c55d0e6, matching the supplied Asahi reference. Current Python bot interpreter is /usr/bin/python3 3.9.6. The reference's parent map totals on the four diagnostic maps are Schooltime 14/16, UNSW 14/16, Australia 14/16, Maze 15/16 (57/64); Kenma 03 totals 15+9+11+14 = 49/64. A 64-game same-host Carthage diagnostic is dry-run-previewed and queued after exact after-zoo PID 36086 / clean Kenma 09 completion. This is a post-result mechanism/portability check, not a new independent strength test. Main build/kenma/after-k09.progress.log and parent-pool-diagnostic-s1/.

2026-10-05 02:54 UTC: Kenma 07 finished 51–51, zero errors; rejected. Kenma 10 trial was cancelled after freshness mismatch was found; source, fixture attempts and cancellation audit retained. Kenma 11 fixes freshness but its four-game real activation smoke (Weakhold/Australia, both seats, seed 1) finished 2–2 with zero activations: World encodes observed no-bed as -1, not 0. Both drafts are frozen. Kenma 12 corrects bed==-1 and explicitly rejects unknown bed=0. Test now constructs a protocol block and calls the actual helper parser and World::sense before requiring activation, then covers 80 persistent simulated turns and hazard guards under ASan/UBSan. Test fixtures v10/v11 retained for audit. Real smoke running; do not start a full screen without activation evidence. Panel --logs enables diagnostic logs and retains every selected map replay when --keep-replays is set; default manifest/output behavior preserved, retry regression passes. Kenma 09 approaching completion; after-k09 still queues the same-host parent64 diagnostic on clean completion.

2026-10-05 02:58 UTC: 09 final57–45/102, zero errors, rejected. after-k09 started same-host parent64 (one worker). 12 smoke3–1/4, zero errors, orbit activated in all four games; all four retained replays analyzed. Weakhold A queen survives to elimination victory; B queen dies at round162 after a split but still wins. Australia queens eventually die in both seats. Full12 Carthage102 launched on unchanged runtime; smoke is not treated as an independent strength result. Kenma13 prepared from08: existing keeper model supplies normalized F/R/B/L log probabilities to the parent movement search for original queens, same prior weight1.0, rather than replacing the final decision. Four facing rotations and zero-mass conditioning checked with sanitizers. No13 games until a worker is free; prioritize any promising12 result's validation.
