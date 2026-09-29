# Ares V04 — Tyr V12 behavioral parity and benchmark

**Date:** 2026-09-29
**Status:** experimental; not admitted to the all-map frontier

Ares V04 is the C++ translation of Tyr V12's active policy on Anna A02's protocol-3 runtime scaffold. Anna supplies the runtime adapter; it does not supply action rules.

## Behavioral parity

The source compiled warning-clean with:

```sh
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic \
  bots/ares-v04-tyr12-behavior-parity/main.cpp \
  -o build/ares-v04-tyr12-behavior-parity
```

The repository's strict ordered-output golden harness compared Ares with Tyr V12 on the same saved inputs. The suite covers ten live maps in both seats, with one duplicate default-map check: 21 replay files, 20 unique map-seat transcripts. Across the unique transcripts it checked 168,123 turns from 5,089 dragons. Move, split, and sonar outputs matched in order with **zero divergences**.

The transcripts exposed semantic gaps that a win/loss screen could not isolate: Tyr's partially represented body state, its active policy overrides, wrapped density coordinates and report freshness, crown record retention and update ordering, maximum-degree topology search, separation transitions, and exception/fallback behavior. V04 now follows those Tyr V12 semantics. The transcript result establishes output parity on the recorded inputs; it is not an exhaustive proof over every possible state.

Golden artifacts are in the ignored `build/cx/golden/ares-parity/` directory. The harness is `tools/cx/golden.py`.

## Fixed-panel benchmark

The seed-1 fixed panel used `unswbc 1.2.2`, all eight bots in the current `tools.analysis.features.run_panel.ZOO`, ten live maps, and both seats: 160 games. All 160 replays extracted successfully. One parallel startup hit a transient permission error while the Ares executable was being made available; that fixture was rerun serially and completed successfully. There are no failed fixtures in the final index.

Ares scored **117 wins, 43 losses, and no draws** (73.1% expected-score share). Per `docs/analysis/BENCHMARKS.md`, the table gives medians over Ares side-games; field ratios divide each side-game value by that map's saved field median. The top-10 column is the ratio to that map's saved top-10 median. Percentiles use the saved same-map field distributions, with ties half-counted.

### Tier 1: economy and retention

| Metric | Raw median | Field median ratio | Top-10 median ratio | Field percentile |
| --- | ---: | ---: | ---: | ---: |
| Pearls at r50 | 31.0 | 0.990 | 0.914 | 0.491 |
| Pearls at r100 | 86.5 | 1.016 | 0.946 | 0.511 |
| Pearls at r150 | 152.5 | 1.127 | 1.041 | 0.598 |
| Pearls at r250 | 250.0 | 1.229 | 1.112 | 0.627 |
| Dragons at r100 | 17.0 | 1.118 | 0.940 | 0.592 |
| Total length at r100 | 41.0 | 1.000 | 0.863 | 0.509 |
| Births by r100 | 36.0 | 1.018 | 0.913 | 0.509 |
| Largest-dragon share at r100 | 0.083 | — | — | — |

The mean of the four field-normalized pearl checkpoints is **1.090**. Against the absolute targets in BENCHMARKS.md, only the r250 pearl median reaches 1.20; dragons, length, and births at r100 remain below 1.15. The median early concentration is within its 0.09 target.

### Tier 2: self-inflicted deaths

Rates are deaths per 1,000 dragon-turns. “Excess vs top 10” subtracts the map-specific top-10 median; positive values mean more deaths than the top ten.

| Metric | Raw median | Excess vs top 10 | Field percentile (higher is better) |
| --- | ---: | ---: | ---: |
| Kelp deaths | 7.132 | 5.783 | 0.340 |
| Own-body deaths | 3.884 | 3.843 | 0.319 |
| Ally-body deaths | 2.419 | 1.326 | 0.286 |
| Ally head-on deaths | 0.949 | 0.516 | 0.248 |
| No-valid-action deaths | 0.000 | — | — |

The first four rates miss the document's absolute targets (<1, <1, <0.8, and <0.5 respectively); no-valid-action deaths meet its zero target. These are single-panel absolute results, so they do not measure the required change against a parent bot.

### Tier 3: fixed-panel outcome proxies

| Metric | Median |
| --- | ---: |
| Bed capture share | 0.598 |
| Pearl share at r150 | 0.602 |
| Territory at r100 | 0.563 |
| Total-length share at r250 | 0.635 |

These values are only comparable on this exact opponent, map, seed, and seat panel.

## Contest submission

The requested upload completed as **submission v83 (ID 11244)**, named
`ares-v04-tyr12-behavior-parity-ai`, uploaded at 2026-09-29 06:47:28 UTC.
A read-only `GET /api/v1/submissions` check after processing reported its status
as `active`. The platform auto-activated the upload. This server status is
separate from local frontier admission and does not change the benchmark limits
below.

## Interpretation and limits

The BENCHMARKS.md acceptance rule requires a parent comparison: at least +0.05 on the four-checkpoint economy mean, no reduction in r100 dragons or length, no tier-2 rate increase above 10%, and no drop in panel win rate. This pure port has no separately measured parent on the same 160 fixtures, so the run provides an absolute scorecard and an outcome screen, not an acceptance delta. Do not infer a measured gain over Tyr V12 from the 117–43 panel result.

The run covers the ten documented live maps at seed 1; it is not an unknown-map or multi-seed generalization result. V04 remains experimental and is not promoted to the frontier.

**Runtime-source fingerprint:** `b204867be71cbe31f514737207a0833eaae418c07d04a6d1489ec4389a61dcb0` (SHA-256 over sorted relative C++/header and `bot.toml` paths and file contents, NUL-separated). Benchmark replays, extracted features, index, and cache are under the ignored `build/zoo/ares-v04-fixed-panel-20260929/` directory.
