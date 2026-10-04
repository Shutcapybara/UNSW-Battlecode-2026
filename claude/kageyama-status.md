# kageyama — Phase 3 Data lane (Claude Opus 5.5)

STATUS: RUNNING

Branch `r/kageyama`: a private tree in the Cowork VM (`~/wt-kageyama`, shared object store of the main checkout,
private index, plumbing commits only; never touches main's index or HEAD). Tools `tools/learn/`. Engine truth runs
use the Cowork cloud container (official engine in-process, no Mac CPU). Corpus-scale builds: Mac native.

## Top — read this first (unit 4, 2026-10-04 16:10 UTC)

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
- 2026-10-04 10:35 UTC — lane started; read macro, prompts, D-042..D-048, briefs, BOARD, chongqing wrap-up, HB-1.
- 2026-10-04 16:10 UTC — unit 4: dev teacher set (235,798 rows, audit pass), hidden bed variants, in_scope answer.
- 2026-10-04 13:55 UTC — unit 3: decode done, variant maps not reproducible (report), died diagnosis, top-teams v1.
- 2026-10-04 12:40 UTC — unit 2: manifest v2 + consumed series, mapcheck (2 map variants), smoke rebuilt, BOARD.
- 2026-10-04 11:20 UTC — unit 1: rebuild, oracle, encoder + C++ twin, labeller, splits, audit; BOARD K1-01..06.
