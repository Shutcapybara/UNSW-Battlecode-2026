# Kenma free lane

State: ACTIVE. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma.
Updated 2026-10-05 01:12 UTC.

Best: no measured improvement yet; carthage-05-free-sprint remains the reference.

- Kenma 01 free combat sprint: **48–54**, 0 errors, 17 ranked maps x both seats x seeds 1–3. Rejected as an improvement; Australia 0–6. Output: main build/kenma/k01-v-carthage-s123/.
- Baseline smoke: Carthage self-play completed Schooltime; small reference panel vs Hunter V20 scored **6–2**, with both losses on Weakhold, 0 errors. Output: main build/kenma/baseline-eight/.
- Kenma 02 top-team prior: A1-400 development fold-f0 model replaces HB-1 direction prior only. 20,000 prediction parity rows: all argmax equal, max probability error 4.66e-8. Zip 1,142,429 bytes. Full 102-game Carthage screen running. Output: main build/kenma/k02-v-carthage-s123/; export/parity build/kenma/a1/.

Kenma 03 pocket queen: in the Schooltime seed-1 native smoke, the queen survived all 500 rounds (parent queen died at round 0), with zero runtime errors. A 12-game Schooltime/Weakhold screen, both seats and seeds 1–3, is running in the fourth worker slot; its first game won on queen length 3–0. Source frozen at e60733a926fc. Output: main build/kenma/k03-pocket-screen/.

Next: finish Kenma 02/03 screens; broad benchmark and deployment checks for the pocket rescue if its local result holds. No best declared or ladder request yet.

Resource controls: nice 15, at most four game workers, <6 GiB aggregate RSS (observed 2.93 GiB with three workers), disk floor 40 GB, output ceiling 30 GB. Actual outputs <0.2 GB. Each game has a new engine process. No server access.

Reserve: new maps and seeds 11–13 excluded from tuning. Required final scorecard still outstanding: Kageyama H2H, pool, sandbox points and any posted free-lane best.
