# Kenma free lane

State: ACTIVE. Updated 2026-10-05 02:02 UTC. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma. No server access, submission or ladder request.

## Provisional best

**kenma-03-pocket-queen**, runtime e60733a926fc056a6cd596582c64c535e461a18679ae1d97f4a725a4cb4612a1.
- Carthage: **58–44**, 17 ranked maps × both seats × seeds 1–3, zero errors.
- Kageyama: **61–41**, same 102 fixtures, zero errors.
- Zoo: required 272-game panel **running**, one worker. Output main build/kenma/k03-zoo-s1/. Not yet a final score.
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
| 06 pocket-space | 03 plus exact Asahi K16 space-filter sources | Running | Full 102-game screen, one worker |
| 07 keeper-moves-parent-splits | 04 with learned movement but all parent SPLIT decisions preserved | Unmeasured | Prepared; test next |
| 08 lossless-direction | 03 with reversible 32-bit model node storage | Equivalent control | Exact native prediction parity passed; deployment pending |

Outputs for completed screens: main build/kenma/kNN-v-carthage-s123/. Kageyama output k03-v-kageyama-s123/. Current sequence after-k05 verified the complete Kenma 05 result, finished the seed-5 probe, then launched Kenma 06; main build/kenma/after-k05.progress.log. No additional games should start until the current two-worker resource allocation has room.

## Evidence informing next choices

The retained Weakhold seed-1 replays show 03 queens dying to walls immediately after splits (rounds 29/44). The 04 queens survive both games (A wins by elimination at round 272, B wins by queen at 500). Delaying control in 05 loses both queens and both games (rounds 29/388). This motivates testing movement-only imitation without suppressing parent expansion. Exact death-event/standing audit: main build/kenma/queen-diagnostics.json; tool tools/kenma/replay_diagnostics.py.

Queen clone training: 26,820 oracle queen turns from keeper teams; action accuracy 81.75% on 17 held-out development series, versus 32.71% majority. Export parity all 19,627 move-row argmax, max error 5.49e-8. Model evidence is not play strength. Output main build/kenma/queen-action-v1/. Model tools use installed torch/lib/libomp.dylib and OMP/BLAS threads 1.

08 model storage: all 824,580 original nodes reconstruct exactly; 21,024 native probability vectors are bit-identical, including 1,024 synthetic NaN cases. Model arrays 6,596,640 → 3,300,848 bytes; initial archive 3,591,664 bytes. Evidence main build/kenma/lossless-direction/report.json. Sandbox first-turn metering required before adopting it in a stronger candidate; this is not a new strength claim.

## Remaining work and bounds

Finish 03's pool and 06's Carthage screen. Test 07; meter 08. Any stronger candidate gets direct comparison against 03, full Kageyama/other posted free-lane/pool scorecards and exact-source deployment checks. Preserve seeds **11–13 and new maps** for independent confirmation before a ladder request; none used yet.

Nice 15; currently **two** games total (zoo 1, Kenma 06 1), maximum four. Guard at 5 GiB aggregate lane RSS to stay below 6 GiB. Initial 05 two-worker start and later overlapping Ouroboros zoo games hit 5.03/5.06 GiB guards; those interrupted attempts were archived and retried, not counted as bot losses. Two-game concurrency since then. Fresh engine each game; source/fixture manifests pinned; actual engine version logged (unswbc 1.2.3), clang++ -O2 -std=c++20 required by current helper. Resume with --retry-errors only after verifying the previous process terminal. Retry regression passed.

All generated outputs stay in main build/kenma (currently about 0.53 GB); 30 GB ceiling, 40 GB disk floor (about 256 GiB free). Never change measured runtime snapshots. Baseline small reference panel versus Hunter V20 was 6–2, both losses Weakhold, zero errors.
