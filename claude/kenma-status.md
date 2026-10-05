# Kenma free lane

State: ACTIVE. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma.
Updated 2026-10-05 01:28 UTC.

Provisional best: **kenma-03-pocket-queen**, 58–44 vs carthage-05 over all 102 required fixtures, zero errors. Full by-map table in its README and main build/kenma/k03-v-carthage-s123/score.json. Posted to main BOARD. Kageyama H2H now running; pool still pending. No ladder request yet.

- Kenma 01 free combat sprint: **48–54**, 0 errors, 17 ranked maps x both seats x seeds 1–3. Rejected as an improvement; Australia 0–6. Output: main build/kenma/k01-v-carthage-s123/.
- Baseline smoke: Carthage self-play completed Schooltime; small reference panel vs Hunter V20 scored **6–2**, with both losses on Weakhold, 0 errors. Output: main build/kenma/baseline-eight/.
- Kenma 02 top-team prior: A1-400 development fold-f0 model replaces HB-1 direction prior only. 20,000 prediction parity rows: all argmax equal, max probability error 4.66e-8. Zip 1,142,429 bytes. Full Carthage screen finished **42–60**, zero errors; rejected as an improvement. Output: main build/kenma/k02-v-carthage-s123/; export/parity build/kenma/a1/.

Kenma 03 pocket queen: in the Schooltime seed-1 native smoke, the queen survived all 500 rounds (parent queen died at round 0), with zero runtime errors. The 12-game Schooltime/Weakhold screen finished **9–3**: Schooltime **6–0**, all on queen length 3–0, Weakhold **3–3**; zero errors. The full Carthage panel finished 58–44. Four heavy-map sandbox checks passed: maximum 10.91 M points, first-turn maximum 10.81 M, zero errors. Zip 3,923,010 bytes. Source frozen at e60733a926fc. Output: main build/kenma/k03-pocket-screen/.

Next: finish Kenma 03 versus Kageyama (102 games) and Kenma 04 versus Carthage (102 games), both running with two workers apiece. Then run the provisional best on the required 272-game zoo panel; compare any stronger Kenma 04 directly against Kenma 03 and meter that exact source. Finally use reserved seeds 11–13/new maps for independent validation before requesting a ladder slot. No server access or ladder request yet.

Resource controls: nice 15, at most four game workers, <6 GiB aggregate RSS (observed 4.42 GiB with two native games plus one metered game), disk floor 40 GB, output ceiling 30 GB. Actual outputs <0.5 GB. Each game has a new engine process. No server access.

Reserve: new maps and seeds 11–13 excluded from tuning. Required final scorecard still outstanding: Kageyama H2H, pool, sandbox points and any posted free-lane best.

Kenma 04 keeper action: independent new candidate on Kenma 03; original queen outside sealed pockets uses a small seven-class keeper action clone. 26,820 oracle queen turns, 17 held-out development series: action accuracy 81.75% (majority 32.71%). Export parity on 19,627 move rows: 100% argmax, max error 5.49e-8; zip 4,030,139 bytes. H2H vs Carthage, 102 games, running. Training/export: main build/kenma/queen-action-v1/.

Resource/reproduction notes: the model tools use the installed torch/lib/libomp.dylib via DYLD_LIBRARY_PATH, with OMP/BLAS threads set to 1. The panel runner compiles C++20 under main build/kenma/bin (the current official helper requires C++20), pins runtime source fingerprints, starts a fresh engine for every game, and enforces 5 GiB aggregate lane-process RSS to leave headroom below the 6 GiB limit. All generated artifacts are in main build/kenma; sources only in this worktree.

Known robustness follow-up: Shenzhen’s prior cage study reported one-slot reserve failure on Schooltime seed 5; Kenma 03 checks split legality and succeeded on all six s1–3 games, but reserved-seed confirmation and possibly a separately numbered reserve-3 variant are still needed. Do not edit measured bot source in place.
