# kageyama — Phase 3 Data lane (Claude Opus 5.5)

STATUS: RUNNING

Branch `r/kageyama`: a private tree in the Cowork VM (`~/wt-kageyama`, shared object store of the main checkout,
private index, plumbing commits only; never touches main's index or HEAD). Tools `tools/learn/`. Engine truth runs
use the Cowork cloud container (official engine in-process, no Mac CPU). Corpus-scale builds: Mac native.

## Top — read this first (unit 2, 2026-10-04 12:40 UTC)

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
| post-m2 decode | waiting | asked the user once (11:05Z) to run `build/_stage_kageyama/run_decode.sh`; a native decode writer appeared 11:13Z |
| datasets (teachers, mimics, our own, values) | next | `tools/learn/dataset.py` works (oracle or rebuild); teacher list next |

Facts found this unit (each on the BOARD):
- Server replays **redact bed timers** (TILE lines `0 0`, no PearlCountdown events) and can **swap spawn seats**
  relative to the template (team A's queen is id 1 in such games). The oracle restores exact blocks.
- The sonar mask label uses the requested direction; HB-1's used the physical one (loses the neck bit when refracted).

## Human-in-the-loop (asked once each)
- H-K1 (11:05Z): run the native post-m2 decode. Ran 11:13–12:03Z (time limit); a second run is needed for the last ~4.8k (asked 12:40Z as the same item).

## Log
- 2026-10-04 10:35 UTC — lane started; read macro, prompts, D-042..D-048, briefs, BOARD, chongqing wrap-up, HB-1.
- 2026-10-04 12:40 UTC — unit 2: manifest v2 + consumed series, mapcheck (2 map variants), smoke rebuilt, BOARD.
- 2026-10-04 11:20 UTC — unit 1: rebuild, oracle, encoder + C++ twin, labeller, splits, audit; BOARD K1-01..06.
