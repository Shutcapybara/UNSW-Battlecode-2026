# tools/learn — Phase 3 data pipeline (Data lane, kageyama)

Replay → legal observation → features + labels + value targets, with a C++ twin of the encoder for the bot.

| file | what | gate evidence (4 Oct) |
|---|---|---|
| `block.py` | parse / format the per-turn protocol block (the only encoder input) | |
| `rebuild.py` | replay → the exact block every dragon received, per turn, in engine order; plus label ctx | 401,434 / 401,434 blocks identical to the engine's (`test_rebuild.py`, 22 maps random walkers ×3 seeds + carthage-05 self-play on 17 live maps) |
| `oracle.py` | re-run the official engine on a **server** replay with the index seed + template beds, answering each turn with the recorded action → ground-truth blocks with real bed countdowns | 4 / 4 server post-m2 games reproduced exactly (87,830 turns); rebuild = oracle on every field except countdowns |
| `encode.py` | ENC_VERSION 1: blocks only → int32 vector, 49 cells × 23 channels (egocentric, facing up) + 66 scalars incl. the queen block | invariants in `test_encode.py` |
| `cpp/learn_encode.hpp` | C++ twin (header-only) | **40,002 turns / 1,214 processes, 0 mismatches** (`test_parity.py`); ~0.6 M turns/s native |
| `cpp/learn_helper.hpp` | official `helper.hpp` state → `learn::Block` (what a bot calls) | 40,002 / 40,002 identical through the real helper parser (`test_helper_parity.py`) |
| `labels.py` | LABEL_VERSION 1: kind, first step (F/R/B/L), sprint length, split size, sonar mask (requested), cull, death | vs HB-1 v5 on 12 Heartbreaker games: family, first, nsteps, child, sonar count, sonar mask (HB-1's physical convention) **100 %** of 75,306 turns |
| `dataset.py` | replay list → parquet rows (meta + x_* int16 + y_* + outcome), held-out maps never written | |
| `splits.py` | D-046 §3 + D-049 split (held out: Autarky, Maze, Trauma) of every known game, consumed series, fixture manifest |
| `mapcheck.py` | corpus-wide server map vs `maps/live/` check (one replay per map_hash) | |
| `audit.py` | leakage audit of any dataset file | |
| `coverage.py` | label-free oracle coverage of a frozen cohort (reproduced flag, turns, teacher processes only) | R2 confirmation cohort: 115 / 115 reproduced |
| `cpp/hb1_scores.cpp`, `hb1prior.py` | the parent's HB-1 direction prior (p over F/R/L) on teacher rows through carthage-05's own C++ extractor; `dataset.py --hb1` adds `hb_pF/hb_pR/hb_pL` | text path = the bot's helper path on 3,091 / 3,091 turns (`cpp/hb1_helper_check.cpp`); ~3.2 k turns/s |
| `build_dev.py` | resumable sharded build (one parquet per game), restarts bound the wasm memory growth | |
| `gen_truth.py`, `drive_native.py` | engine truth runs (random walkers / native bots, one process per dragon) | |

Facts the pipeline depends on (found 4 Oct, kageyama):
- **Server replays redact bed timers** (every `TILE` line `0 0`, no `PearlCountdown` events) and may **swap spawn seats**
  relative to the template (team A's queen can be id 1). Never assume A = id 0; never read beds from a server replay's
  map text (use `maps/live/` or the oracle).
- The engine re-run with the index `seed` (hex) and the template beds reproduces server games turn for turn, so the
  server runs the same engine as the 1.2.x wheels (D-046 §2's open check).
- Sonar mask labels use the **requested** direction (a ray aimed into the neck leaves through the tail; HB-1 recorded
  the physical direction and so loses that bit). `y_sonar_mask_phys` keeps HB-1's convention.
- `pearl_in` is unavailable in rebuilt server rows (`x_cd_known = 0`); use oracle rows (`blocks_src = oracle`).
