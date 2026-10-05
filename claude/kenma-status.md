# Kenma free lane

State: ACTIVE. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma.
Updated 2026-10-05 01:42 UTC.

Provisional best: **kenma-03-pocket-queen**, runtime e60733a926fc. Carthage **58–44**, Kageyama **61–41**, each 17 ranked maps × both seats × seeds 1–3, zero draws or runtime errors. Full by-map tables in its README. Posted provisional best to main BOARD. Required 272-game zoo panel running with one worker; no other posted free-lane best found. No ladder request or server access.

Deployment complete for Kenma 03: four sandbox games on Schooltime/UNSW, both seats, seed 1; max 10,910,667 points, max first-turn 10,814,937; zero errors; zip 3,923,010 bytes at packaging. Outputs main build/kenma/deploy/kenma-03-pocket-queen/. Zip contains the earlier README, same runtime fingerprint.

Completed Carthage screens, all 102 games and zero runtime errors:
- Kenma 01 free combat sprint: **48–54**, rejected. Australia 0–6. Output main build/kenma/k01-v-carthage-s123/.
- Kenma 02 A1-400 direction prior: **42–60**, rejected. Export parity 20,000 rows, all argmax equal, max error 4.66e-8. Output main build/kenma/k02-v-carthage-s123/ and a1/.
- Kenma 03 pocket queen: **58–44**, provisional best. Schooltime 6–0, all on queen length 3–0. Output main build/kenma/k03-v-carthage-s123/; Kageyama 61–41 in k03-v-kageyama-s123/.
- Kenma 04 keeper action: **50–52**, rejected. Offline imitation: 26,820 oracle queen turns, 81.75% action accuracy on 17 held-out development series, export parity all 19,627 argmax. Output main build/kenma/k04-v-carthage-s123/ and queen-action-v1/.

Running: **kenma-05-post-opening-keeper** vs Carthage, 102 games. Same as Kenma 04 except learned queen actions start at round 25, preserving opening expansion. Initial two-worker batch was terminated by the aggregate 5 GiB memory guard at 5.03 GiB (two interrupted games, no bot fault evidence). Resumed with one worker and --retry-errors; original attempts retained. Both interrupted games now completed cleanly. Full outcome pending.

Prepared next: **kenma-06-pocket-space**, Kenma 03 plus the existing Asahi K16 queen space filter; source files copied exactly, no map conditions added. Unmeasured. Test when worker/memory headroom is available.

Resource controls: nice 15; currently two game workers total (zoo 1, Kenma 05 1), hard ceiling four; guard at 5 GiB aggregate lane RSS to stay below 6 GiB. Disk floor 40 GB, output ceiling 30 GB, outputs currently <0.5 GB. Fresh engine per game. All generated output in main build/kenma. Runtime snapshots frozen once measured. Runner now returns failure on incomplete/error panels and explicitly preserves failed attempts before retries; retry regression test passed.

Remaining for best: finish 272-game pool; compare any later posted free-lane best; use reserved seeds 11–13/new maps for independent validation before requesting a ladder slot. No server access or account credentials used.

Known robustness follow-up: Shenzhen's prior cage study found a one-slot reserve failure on Schooltime seed 5. Kenma 03 passed six s1–3 games but needs a separate development seed-5 check; a reserve-3 change would be a new numbered snapshot. Reserved seeds 11–13 remain untouched.

Reproduction: tools/kenma/panel.py pins runtime source fingerprints and exact fixture manifests, compiles C++20 with clang++ -O2 (required by current helper), uses unswbc 1.2.3, and logs engine version. Model tools use installed torch/lib/libomp.dylib with OMP/BLAS threads 1. Baseline eight-game reference vs Hunter V20: 6–2, both losses Weakhold, zero errors.

Replay finding: both seed-1 Weakhold games show Kenma 03/parent queens trapped immediately after splitting: queen 0 dies to a wall at round 29 (split at 28), queen 1 at round 44 (split at 43). Kenma 04 queen 1 survives to round 499 in the B-seat replay; queen 0's last recorded turn is 271 (no own-turn death event). This supports testing movement-space avoidance and phase-dependent learned control; it does not establish a whole-panel gain. Read replays retained in main build/kenma/k03-v-carthage-s123/ and k04-v-carthage-s123/.

2026-10-05 01:49 UTC resource update: the zoo guard stopped two overlapping Ouroboros/Slithery games at aggregate 5.06 GiB. Verified runner exit; preserved 42 valid results and archived the two interrupted attempts before resuming with one zoo worker. Kenma 05 remains live at one worker. Queue session after-k05 runs only after that exact process exits and a complete error-free score exists: Kenma 03 Schooltime seed 5, then Kenma 06 Carthage102, each one worker. Output main build/kenma/after-k05.progress.log. Diagnostic replay retention now covers both named maps on every requested seed, including the seed-5 check.

Prepared Kenma 07 keeper-moves-parent-splits: copies Kenma 04 but preserves every parent SPLIT and uses only learned movement classes otherwise. No model or timing changes; unmeasured and not best. Intended to separate the movement benefit from lost expansion.

Replay audit complete (12 retained games, main build/kenma/queen-diagnostics.json): Kenma 04 queens survived both Weakhold s1 games (A win by elimination at r272; B win on queen at r500). Kenma 05 lost both: A queen died at r29, B at r388, both wall deaths. Kenma 03 queens die at r29/r44. This corrects the earlier ambiguous r271 last-turn observation: the Kenma 04 A queen was alive when its opponent was eliminated. tools/kenma/replay_diagnostics.py checks all death events, including another dragon's turn, and official final population consistency.
