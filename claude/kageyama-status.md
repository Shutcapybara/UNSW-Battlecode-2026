# kageyama — Phase 3 Data lane (Claude Opus 5.5)

STATUS: RUNNING

Branch `r/kageyama`: private tree `build/_stage_kageyama/tree` on the Mac (shared object store of the main checkout,
private index `.index`, plumbing commits via `commit.sh`/`g.sh`; never touches main's index or HEAD). Tools `tools/learn/`. Engine truth runs
use the Cowork cloud container (official engine in-process, no Mac CPU). Corpus-scale builds: Mac native.

## Unit 11 (2026-10-05 06:45 UTC; fresh session, shell works)

- **Shell back.** I committed and pushed the waiting handoff status (97f3a3031).
- **D-072 §E, hidden bed layouts: done.** All five variants are accepted. Finding:
  `docs/findings/2026-10-05-kageyama-hidden-beds.md`.
  - **Mechanism:** countdown = lo + (u mod span), with u from mt19937_64(seed). Pairs draw in row-major order at
    round −1 and at each expiry.
  - **Emulator:** `tools/learn/beds/emu.py`, verified against the engine (0 differing cells).
  - **Maps:** `maps/live_var/{devil_b,queen_of_spades_b,slithery_fight_b,schooltime_open4,dilemma_10}.map`, with
    `*.beds.json`.
  - **Per-game labels:** `docs/learning/datasets/kageyama-bed-variants-v1.json`. The 14,240 post-m2 games on the
    five maps each get one of {template, variant, ambiguous (233)}; none is explained by neither list.
  - **Oracle:** 828 / 828 games reproduced turn for turn (tv1 failures plus 100 random games per variant).
  - **Coverage:** the variants are 4,598 of 31,793 ranked post-m2 games (14.46 %).
- **Mac VM engine:** the aarch64 wasmtime wheel and the unswbc engine files are unpacked into `~/pyk` (from
  `build/_stage_kageyama/{wasmtime-49.0.0-…aarch64.whl,unswbc_engine_pkg.tgz}`), so oracle runs work on the VM with
  `PYTHONPATH=$HOME/pyk`. Keep at most about 20 games per process (memory) and at most 3 processes.
- **Team-213 and team-91 slot exports: done** (83ee5a073). They are `bots/kageyama-02-p1-hb1-t213` and `-t91`, each
  with one file changed (`p1_model.hpp`).
  - Python against C++: 7,125 rows, ≤ 3.2e-8.
  - In-bot parity on 4 maps × both seats (self-play): 111,592 and 114,741 turns, ≤ 5.7e-8.
  - Sandbox max 11.0 M and 10.9 M points; zip 1.075 and 1.040 MiB.
  - Results are in `build/learn/kageyama/export/t213_t91/`.
- **D-067 §E.7 trajectory block: built.** It is a separate column group (TRAJ_VERSION 1, 7 int32 columns,
  `x_traj_*`).
  - Columns: units Δ20 and Δ100, own length Δ20, rounds since an enemy was seen, contacts and close contacts in the
    last 20 rounds, and own turns in the last 20 rounds. The unit-count level is v1's `x_unit_count`.
  - Code: Python `tools/learn/traj.py`; C++ twin `tools/learn/cpp/learn_traj.hpp`.
  - Parity (`test_traj_parity.py`): 89,845 turns in the cloud and 165,307 turns natively on the Mac VM, 0 mismatches.
    The in-bot input is the same `learn::Block` as encoder v1, whose helper parity is 40,002 / 40,002.
  - `traj_rows.py` writes the columns for the teachers_v1 rows, keyed by game, dragon, round and turn.
- **Queue once traj_rows.py is on main** (a learn job, about 10 min with 8 workers):
  `{"kind":"script","script":"tools/learn/traj_rows.py","argv":["--jobs","8"],"heavy":true,"timeout":2700,"by":"kageyama","env":"learn","id":"kageyama-02-traj-v1"}`.
  Then post the manifest; first users are P-8 S0 (Sugawara) and R3 offline (Hinata).
- **Delete when deletion is allowed:** the cache symlink `build/_stage_kageyama/tree/maps/live` and
  `build/_stage_kageyama/ev_snap.jsonl.gz`.

## HANDOFF — read this first (2026-10-05 ~05Z; the lead is restarting the lane in a new session)

- **No scheduled wake is pending for Kageyama** (the hourly self-wake was not renewed). Nothing runs on its own.
- **Shell:** this session's device shell failed from 04:11Z (EACCES on its old session folder, after the D-073 disk
  reset). File copy (stage/commit) still worked. A fresh session should have a shell.
- **Git:** r/kageyama = e96491cde (unit 10 status), pushed up to eedd7b6a7 (both fallback builds, merged to main
  03:25Z). This status file (handoff) was written by file copy into the private tree and is NOT committed: commit it
  with `build/_stage_kageyama/tree/commit.sh` (paths use `$HOME/mnt/Projects/UNSW-Battlecode-2026`; scripts may lose
  +x after sed, `chmod u+x` them).
- **Open order: D-072 §E, rebuild the hidden bed layouts.** Work in progress, with notes and tools, is in
  `build/learn/kageyama/beds/` (README there). The key findings are on the BOARD at 04:18Z:
  - the bed schedule is play-independent;
  - symmetric pairs share draws in row-major pair order;
  - a draw is lo + (u mod span), with u_k read from the engine by a probe map.
  - Devil's variant list is fitted, but the full oracle does not yet reproduce: the ranges must be resolved per pair.
  - Then do Queen of Spades, Slithery Fight, Schooltime open-4 and Dilemma 10-dragon. Write the maps under
    `maps/live_var/`; accept a map at ≥ 95 % of its variant's games reproduced.
- **Other open items:**
  - export Hinata's single-team priors (213, 91) into the HB-1 slot (`kageyama-02-p1-hb1`) when they exist, with
    gbt_parity, multi-map slot_e2e_parity and sandbox points;
  - R4 feature blocks;
  - P-8 S0 legality question (which half of a split keeps the process).
- **Cloud-only state is lost with the container:** the /tmp venv (unswbc 1.2.9, lightgbm 4.7.0), the bot build
  copies, and the e2e/fallback scripts. All results are on the Mac under `build/learn/kageyama/export/`, and the
  tools are in the repo.

## Unit 10 ( 2026-10-05 03:15 UTC)

- **D-068:** the ten-team clone loses in play as a prior (A3-400 at λ 1: −7.0 points on the pool), and selection
  by accuracy is suspended. My items:
  - **§C.1 fallback count: done.** Built `bots/kageyama-01b-p1-slot-fb` and `kageyama-02b-p1-hb1-fb`
    (eedd7b6a7), which print `LOG p1_fallback` in the catch around `slot.observe`. Play is identical to the parents.
  - Local count: 0 fallbacks in 76 games (19 maps × 2 seats × 2 paths). Asahi's count binds.
  - **§C.5 single-team priors (213, 91):** Hinata fits them; I export each into the slot when the files exist (HB-1
    path, kageyama-02's code), with gbt_parity, multi-map in-bot parity and sandbox points.
- **Cloud note:** background processes in the container stall while no tool call runs. Long local game sweeps run in
  foreground chunks (`/tmp/fb_fg.sh` pattern, resumable).

## Unit 9 ( 2026-10-05 02:05 UTC)

- **HB-1-vector slot (D-066 §E): built.** `bots/kageyama-02-p1-hb1` (bcd93db88; push requested; merge asked).
  - `p1::INPUT` in the model header picks encoder v1 (0) or the HB-1 row (1). The same slot code serves A1 and A3.
  - A8b switch `KAGEYAMA_P1_MIRROR_AVG` (mirror tables from export_gbt, equal to r2_mirror.py).
  - Placeholder: A1-400 f0.
  - Parity: Python–C++ 20k rows, max |Δp| 3.3e-8.
  - In-bot parity on 4 maps (xy and y) × both seats: A1 96,082 turns, A1+A8b 117,187, A3 path 102,085; all
    ≤ 3.1e-8, with per-column non-zero counts in `build/learn/kageyama/export/e2eres/`.
  - Points: A1 p50 7.3 M, max 10.8 M; with A8b p50 8.0 M, max 11.8 M (one evaluation ≈ 0.7 M). Zip 1.098 MiB.
- **To ship the selected arm:**
  1. Export it with `export_gbt.py lgb MODEL.txt p1_model.hpp --ns p1 --features FEATS.txt`.
  2. Rerun `gbt_parity.py`.
  3. Run `slot_e2e_parity.py` on ≥ 3 maps × both seats with a debug-writer copy (see `/tmp/e2e_run.sh` in the
     cloud: `dbg-*` copies add a per-process writer after `pol.p1_p = slot.p.data();`).
  4. Run the sandbox points.
- **Not done:** H-SZ64 (own unit-count win AUC) is noted for the R4 blocks.

## Unit 8 ( 2026-10-05 00:45 UTC)

- **Deploy slot (D-065 §D): built.** `bots/kageyama-01-p1-slot` (λ 1) and `-l05` (λ 0.5); r/kageyama f536785f7,
  push requested, merge to main asked on the BOARD.
  - One switch `KAGEYAMA_P1_SLOT` (`p1_switch.hpp`). Encoder v1 → `p1_model.hpp` (export_gbt.py) →
    gbt_compact.hpp; slot rule D-055 §E.
  - Model is a PLACEHOLDER: Hinata's A3-400 fold f0. Swap `p1_model.hpp` for the selected arm
    (`python tools/learn/export_gbt.py lgb MODEL.txt bots/<bot>/p1_model.hpp --ns p1`), then rerun
    `gbt_parity.py` and `slot_e2e_parity.py`.
  - Parity: 40,000 rows with max |Δp| 2.9e-8; in-bot end-to-end 11,187 / 11,187 turns; golden parity off
    44,613 / 44,613 turns.
  - Zip 1.053 MiB; points max 10.1 M (UNSW), no errors.
  - Compact sizes: A3-400 1.05 MB zipped; the present HB-1 prior in the same format 4.34 MB (its own format 3.87 MB).
    So A4–A7 (both models) do not fit 4 MiB as they stand.
- **Cohort series per team** for r2_battery `--cohort-series`:
  `docs/learning/splits/kageyama-r2-confirm-v1-series-by-team.json` (795e2e335); it agrees with Tanaka's
  replication.
- **Cloud build environment** (lost if the container is reclaimed): unswbc 1.2.9 + lightgbm 4.7.0 in a /tmp venv;
  `unswbc run --sandbox` gives CPU points.
- **Next:** export the selected arm when Hinata names it; A1 needs an HB-1-vector slot variant (hb1::Proc row → 270
  features), which is not built yet; teacher-specific arms the same way.

## Unit 7 ( 2026-10-04 22:55 UTC)

- **teachers_v1 full rows: done.** They are in `build/learn/kageyama/teachers_v1/`.
  - Size: 1,709 per-game shards, 2.2 GB, largest 2.5 MB, 1,502 columns each.
  - Games: 26 have no sampled process and sit in `_empty/` as markers.
  - Rows: 3,415,158; 2,753,685 are oracle F/R/L moves.
  - Build: learn-queue job kageyama-01-teachers-v1, rc 0, 20 min on 12 workers.
  - Checks: audit 9 / 9 pass; overlap with the frozen R2 cohort is 0 games / 0 series; dev120 cross-check
    235,798 / 235,798 rows equal.
  - Manifest: `docs/learning/datasets/kageyama-teachers-v1-rows.json` (b896eae4f; push requested).
- **Order of work from the 21:16Z brief:** items 1–5 are done; item 6 is this commit.
- **Next:** answer Hinata on the full-row folds if asked. Then the R4 feature blocks and the mimic datasets per the role
  prompt, or whatever the Chair rules next.
- **VM notes:**
  - Background processes in the Mac VM do not survive the end of a device_bash call; run in ≤ 170 s chunks
    (rows_manifest.py has `--part/--combine` for that).
  - pyarrow for the VM goes under `/tmp/pyk` (`pip install --target`).

## Unit 6 ( 2026-10-04 22:15 UTC; fresh session after the 18:56Z disk cut-off)

- **Session change.** The previous session lost its link at 18:56Z (full Cowork session disk). The Chair committed
  unit 5 on its behalf (25d78afab, D-062 §B). This session continues on the same branch; `commit.sh`/`g.sh` now use
  `$HOME/mnt/Projects/UNSW-Battlecode-2026`. The old cloud build (155 / 1,735 games) is gone, and nothing reads it.
- **HB-1 feature vectors, dev120: done.** They are in `build/learn/kageyama/hb1_dev120/`: 118 shards, 235,798 rows,
  hb_pF/R/L plus 270 `hb_f_*` (the direction GBT's inputs in model order, with no map identity), and `_manifest.json`.
  - Tools: `cpp/hb1_feats.cpp`, `hb1_export.py`.
  - Join: 235,798 / 235,798 keys, with blocks_src, y_kind and y_first equal on every row.
  - Prior parity: hb_p* matches hb1_scores on 4,077 / 4,077 turns.
  - A0 descriptive: 0.6977 on 188,250 F/R/L oracle moves.
  - Hinata had not run the scorer by 21:20Z, so there was nothing to cross-check.
- **Answered on the BOARD:**
  - Window layout: `x_f{3..m3}r{m3..3}_{23 ch}`, with `m` for minus.
  - Mirror rule for the window, the scalars, the labels and the HB-1 vector.
  - Frozen-cohort counts per teacher (label-free, `cohort_counts.py`): 124 sides, 39,851 processes, 1,579,699 turns.
    A6 covers 25 series; A7 (SSS) only 6.
- **Full teachers_v1 build is next:** `tools/learn/build_teachers.py` (one oracle pass per game: encoder, labels,
  hb_p and hb_f; per-game shards; `_empty/` markers; resumable; stops under 20 GB free). It goes through the learn
  queue as soon as r/kageyama (1a2bd7241) is on main. Expected about 3.4 M rows, 2–3 GB, 1–2 h. Job file:
  `{"kind":"script","script":"tools/learn/build_teachers.py","argv":[],"heavy":true,"timeout":28800,"by":"kageyama","env":"learn","id":"kageyama-01-teachers-v1"}`.
  Afterwards: the audit (`audit.py` over the shard dir) and the manifest `docs/learning/datasets/kageyama-teachers-v1-rows.json`.
- **For the user:** `build/learn/kageyama/_xfer/` holds transfer tarballs (about 330 MB). Deleting is off in this
  session; they can be removed by hand. The empty folder `build/learn/kageyama/hb_dev120/` can go too.

## Top (unit 4, 2026-10-04 16:10 UTC) (unit 4, 2026-10-04 16:10 UTC)

- **R0 passed (D-053 §A).** R1/R2 open. Asahi's native queue (`build/learn/queue`) not built yet.
- **Development teacher set built (cloud container):** `build/learn/kageyama/teachers_dev120.p{0,1}.parquet`,
  235,798 rows, 118 games (2 of 120 had no sampled teacher process), 10 teams x 14 maps, 15 % of teacher
  processes, 1,229 columns (meta + 1,193 `x_*` + `y_*` + outcome). Audit v2 9/9 pass (`teachers_dev120.audit.json`).
  Labels: move 96.96 %, split 2.72 %, invalid 0.32 %; first step F .418 / R .286 / L .288 / B .008.
- **Hidden bed variants are wider than two maps:** the engine oracle reproduces 97 / 118 games; the 21 that diverge
  are on Slithery 7/10, Schooltime 6/10, Queen of Spades 5/7, Prisoners Dilemma 2/7, Devil 1/10 — all other maps
  10/10. The visible map text matches there, so the server carries bed layouts (redacted in replays) that differ from
  the templates on those maps. Those rows are `blocks_src = rebuild_redacted` (`x_cd_known = 0`).
- **in_scope (Hinata 14:48Z):** both tables right for their time; `in_scope` follows the latest ladder top 50; the 9
  games all involve team 28 (top 50 at v2, crank 94 now). Use the manifest's flag.
- `oracle.py`: one EngineModule per process (a fresh module per game leaked); `build_dev.py` resumable per game
  parts; wasm memory still grows ~3 GB over ~60 games: restart workers (parts make it resumable).

## Unit 3 (2026-10-04 13:55 UTC)

- **Decode complete:** post-m2 in-scope 19,754 / 19,754 decoded (second native run, user-started). R0 item 1 done.
  Manifest v2 is left as recorded (D-052 cites it); new games take their split from the same rule.
- **Map variants (D-052 §E): not added.** Template beds + replay text do NOT reproduce variant games (Schooltime
  open4: 4 games, divergence by r23–28; Dilemma 10: 4 games, r13–38) while template-variant games reproduce exactly
  (4 / 4, 2 Oct and 4 Oct). The variants have their own, redacted bed layouts: Schooltime-open4 bed spawns hit 175–178
  cells, only 60 of them template beds; Dilemma-10 spawns stay on template bed cells but the gaps differ. Neither the
  1.2.3–1.2.8 wheels nor any repo map (incl. `maps/dilemma_10.map`, 28 Sep) carries them. Options to the Chair.
- **`dragons.died` (Asahi 12:25Z):** frame deaths for ids 0/1 agree with the engine's queen header on 166 / 166 sides
  of my engine-truth games; the contradiction is downstream (extract.py's table or the side→queen mapping); need
  the replay path to finish.
- **Top-team KB v1:** `docs/learning/top-teams.md` (post-m2 ranked, held-out maps excluded).
- `oracle.py` fix: EngineModule import (a NameError would have crashed the dataset oracle path).

## Unit 2 (2026-10-04 12:40 UTC)

- **Manifest v2** (D-049 held-out maps Autarky, Maze, Trauma): `docs/learning/splits/kageyama-games-v2.json`, 126,694
  games / 28,602 series, sha256(game,split) ba21ac40…; series consumed by P-2 marked (`consumed_by`), P-2's frozen rows
  c958e8c7… = 5,799 games: 4,705 train / 555 val / 539 test (Tanaka's count reproduced), 1,777 series. Held-out post-m2
  games whose series has no P-2 game, in-scope and decisive: Autarky 435 ranked / 198 unranked, Maze 446 / 185,
  Trauma 447 / 243. Fixtures v2 in `kageyama-fixtures-v2.json`. `smoke.parquet` rebuilt train-only: audit v2 9/9 pass.
- **Map check (R0 item 9)**: 38 distinct post-m2 map texts; 36 match `maps/live/` up to bed redaction + seat swap.
  **Two live maps have a second variant the templates lack**: Prisoners Dilemma (679 of 1,376 games: 10 initial
  dragons, not 6) and Schooltime (882 of 1,860 games: 4 kelp edges open). Both variants run through the whole era.
- Decode: native run ended at its 3,000 s limit (~12:03Z); post-m2 14,041 / 17,206 in scope decoded; queue 4,849.

## Unit 1 (2026-10-04 11:20 UTC)

R0 Data deliverables — state:

| item | state | evidence |
|---|---|---|
| block rebuild (replay -> the exact protocol block each dragon got) | **done** | 401,434 / 401,434 blocks identical to the engine's own (22 maps random walkers x3 seeds; carthage-05 self-play, 17 live maps, full 500-round games) |
| server-engine identity (D-046 §2 open check) | **done** | index `seed` (hex) + template beds re-run reproduces 4 / 4 post-m2 server games turn for turn (87,830 turns) |
| encoder v1, Python | **done** | `tools/learn/encode.py`, 1,193 int32 columns: 49 cells x 23 rotated channels + 66 scalars incl. queen block |
| encoder C++ twin (R0 gate: >= 1,000 turns bit for bit) | **pass** | 40,002 turns / 1,214 processes, 0 mismatches; also 40,002 / 40,002 through the official `helper.hpp` (`learn_helper.hpp`) |
| action labeller (R0 gate: > 99 % vs HB-1) | **pass** | 100 % on 75,306 Heartbreaker turns (family, first, nsteps, child, sonar count, sonar mask in HB-1's convention) |
| frozen splits manifest | **v2 done** | v1 superseded by D-049; v2 as above |
| leakage audit | **done** | `tools/learn/audit.py` (9 checks); smoke test catches a planted test-series game |
| post-m2 decode | **done 13:36Z** (19,754 / 19,754) — was waiting | asked the user once (11:05Z) to run `build/_stage_kageyama/run_decode.sh`; a native decode writer appeared 11:13Z |
| datasets (teachers, mimics, our own, values) | next | `tools/learn/dataset.py` works (oracle or rebuild); teacher list next |

Facts found this unit (each on the BOARD):
- Server replays **redact bed timers** (TILE lines `0 0`, no PearlCountdown events) and can **swap spawn seats**
  relative to the template (team A's queen is id 1 in such games). The oracle restores exact blocks.
- The sonar mask label uses the requested direction; HB-1's used the physical one (loses the neck bit when refracted).

## Human-in-the-loop (asked once each)
- H-K1: native post-m2 decode — done (two runs, last part 13:36Z). Closed.

## Log
- 2026-10-05 07:20 UTC — unit 11b: t213/t91 slot exports; trajectory block (traj.py + C++ twin, parity 0 / 255k), traj_rows.py.
- 2026-10-05 06:45 UTC — unit 11: D-072 §E hidden beds done (5 variants, mt19937_64 mechanism, maps/live_var, labels, oracle 828/828); BOARD.
- 2026-10-05 ~04:20Z — unit 10b (file copy, shell down): D-072 §E bed facts + Devil variant fit in progress; handoff for restart.
- 2026-10-05 03:15 UTC — unit 10: D-068 §C.1 fallback-logging builds and a 76-game local count (0); BOARD.
- 2026-10-05 02:05 UTC — unit 9: kageyama-02-p1-hb1 (HB-1 input path, A8b switch), multi-map in-bot parity, points; BOARD.
- 2026-10-05 00:45 UTC — unit 8: cohort series JSON; deploy slot bot + export/parity tools; BOARD.
- 2026-10-04 22:55 UTC — unit 7: teachers_v1 built on the learn queue (3.42 M rows, audit pass), manifest, BOARD.
- 2026-10-04 22:15 UTC — unit 6 (new session): hb_f export dev120, layout/mirror answers, cohort subset counts, native builder; merge requested.
- 2026-10-04 10:35 UTC — lane started; read macro, prompts, D-042..D-048, briefs, BOARD, chongqing wrap-up, HB-1.
- 2026-10-04 16:10 UTC — unit 4: dev teacher set (235,798 rows, audit pass), hidden bed variants, in_scope answer.
- 2026-10-04 13:55 UTC — unit 3: decode done, variant maps not reproducible (report), died diagnosis, top-teams v1.
- 2026-10-04 12:40 UTC — unit 2: manifest v2 + consumed series, mapcheck (2 map variants), smoke rebuilt, BOARD.
- 2026-10-04 11:20 UTC — unit 1: rebuild, oracle, encoder + C++ twin, labeller, splits, audit; BOARD K1-01..06.
