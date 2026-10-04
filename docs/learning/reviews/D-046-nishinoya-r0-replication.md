# D-050 §5 — Nishinoya replication of Kageyama's R0 parity/label/audit tests (4 Oct 2026, ~12:05Z)

**Unaudited** (probe seat). Kageyama's exact fixtures (truth pkl.gz set, the 12 Heartbreaker games, the
audited dataset) are not on this Mac — `build/learn/kageyama/` holds only `smoke.parquet` — so this is a
**same-tests, fresh-fixtures** replication, not a same-counts one. Every test was run from `r/nishinoya`
at the merged `main` state (`60f4b6f48`+), `nice 15`, single-threaded, no heavy-job lock taken.

## Results

| test | Kageyama (BOARD 11:20Z) | Nishinoya replication | fixture |
|---|---|---|---|
| encoder parity (`test_parity.py`) | 40,002 turns / 1,214 processes / 0 mismatches | **37 processes / 1,549 turns / 0 mismatches** | 3 fresh post-m2 corpus replays (1037799, 927882, 1040029) — never used by Kageyama; ≥1,000-turn macro gate met |
| helper-path parity (`test_helper_parity.py`) | 40,002 / 40,002 identical via official `helper.hpp` | **1,549/1,549 identical over 37 processes** | the same fixture; official `helper.hpp` from the venv's `unswbc/templates/cpp` |
| labels vs HB-1 (`test_labels_hb1.py`) | 100 % of 75,306 turns, 12 HB games | **100 % on 31,061 turns, 6 label families** (family, first, nsteps, child, sonar_n, sonar_mask_phys) | 2 corpus replays × both sides — agreement holds off the Heartbreaker population too |
| leakage audit (`audit.py`) | 9 checks pass | **9/9 checks 0, pass=true** | fresh 3-game train-split dataset (57,316 rows) built by `dataset.py --allow-split train` |

The macro's R0 encoder gate (bit-for-bit on ≥1,000 turns) is met independently on data outside the
author's fixtures. Same results at smaller n; counts are not literally Kageyama's because the inputs
differ.

## Two findings from running it

1. **`build/learn/kageyama/smoke.parquet` fails the leakage audit as it stands**: 3,562 of 5,935 rows
   carry `test`-split series (checks `wrong_split` and `test_series`). Expected for a smoke file, but it
   should not be mistaken for a train-purpose artifact — rebuilding or deleting it avoids the trap.
2. **`test_labels_hb1.py` needs `capnp`** (HB-1's `features_v5` path), which the main `.venv` lacks. I
   ran it in an ephemeral `uv run --with pycapnp` env. If the native executor queue (D-050 §8) is to run
   this test, `pycapnp` must be in its environment — it is not in the package list named in D-050 §8
   (lightgbm, xgboost, torch).

## Decode census (context for D-047 §2's 5 Oct 00:00Z backstop)

In-scope post-m2: 17,206 games; decoded 11,455; queue 5,751 (was 7,617 at 10:44Z) — the lead's writer is
draining ~1.9k net/h (newest part 11:45Z). On trend the queue clears ~3 h before the backstop; the
confirmation fit's "complete decode" condition is comfortable, not marginal.

## Provenance

`tools/learn/*` at `r/nishinoya` = `main` post-`60f4b6f48`; main `.venv` (py 3.13, pyarrow 21) except the
label test (uv ephemeral + pycapnp); replays from `public_replays/corpus/replays/`; outputs under `/tmp`.
