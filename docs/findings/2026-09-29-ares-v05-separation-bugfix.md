# Ares V05 — Tyr V12 separation exception fixes

**Date:** 2026-09-29
**Status:** experimental; not admitted to the all-map frontier; not submitted

Ares V05 branches from the behaviorally matched V04 C++ port and fixes the two confirmed separation exceptions inherited from Tyr V12. These are narrowly scoped policy corrections; they intentionally change outputs only when the affected exception paths would have been reached.

## Defects and corrections

1. **Zero `bed_wait` division.** Tyr V12's active `override.py` sets `bed_wait` to `0.0`. In the separation waypoint resource scorer, a bed with a known spawn round at or after the current round was scored by dividing by this parameter. V05 gives a bed full `bed_value` only when it spawns now; a future bed receives zero value. This matches the meaning of a zero wait horizon and avoids division by zero.
2. **Missing global on newborn pearl pause.** Tyr's separation planner increments `RESOURCE_PAUSE_USED` without declaring it global in `plan()`. If an eligible constrained newborn sees a nearby fresh pearl, Python raises `UnboundLocalError` and the outer policy falls back for that turn. V05 uses its existing per-activation six-use counter, targets that pearl, and preserves the normal route distances and first-step mask before resuming separation.

Tyr's exception handler turns these failures into a safe single-step move with empty sonar. V05 removes the two confirmed fallbacks. This does not establish that every possible Ares or Tyr edge case is bug-free.

## Build and fixed-panel benchmark

The source compiled warning-clean with:

```sh
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic \
  bots/ares-v05-tyr12-separation-bugfix/main.cpp \
  -o build/ares-v05-tyr12-separation-bugfix
```

The seed-1 panel used `unswbc 1.2.2`, the eight bots in the current `run_panel.ZOO`, ten live maps, and both seats: 160 V05 games. Every runner returned `rc=0`; all 160 replays extracted successfully. The V04 parent comparison uses its corresponding seed-1 run on the same panel. Ratios divide each side-game's value by the saved per-map field median in `docs/analysis/benchmarks/map_reference_medians.json`.

| Metric | V04 | V05 | Change |
|---|---:|---:|---:|
| Wins–losses–draws | 117–43–0 | 118–41–1 | +1.5 expected-score points |
| Expected score share | 73.13% | 74.06% | +0.94 percentage points |
| Mean of four field-normalized pearl checkpoints | 1.0905 | 1.0974 | +0.0069 |
| Pearls at r50, field-normalized | 0.990 | 0.988 | −0.002 |
| Pearls at r100, field-normalized | 1.016 | 1.054 | +0.038 |
| Pearls at r150, field-normalized | 1.127 | 1.134 | +0.007 |
| Pearls at r250, field-normalized | 1.229 | 1.214 | −0.015 |
| Dragons at r100, field-normalized | 1.118 | 1.071 | −0.047 |
| Total length at r100, field-normalized | 1.000 | 1.009 | +0.009 |

Tier-2 self-inflicted death rates are per 1,000 dragon-turns. V05 versus V04 medians changed by +7.5% for wall deaths, +9.4% for own-body deaths, +4.6% for ally-body deaths, −2.1% for ally head-on deaths, and 0 for invalid-action deaths. None increased by more than BENCHMARKS.md's 10% guardrail; own-body deaths were closest.

## Interpretation and limits

V05 does **not** meet the documented parent-relative acceptance gate on this seed: the economy mean rises by 0.007 rather than at least 0.05, and field-normalized r100 dragons fall. Length does not fall, tier-2 increases remain below 10%, and the fixed-panel expected score improves slightly. This panel supports the runtime fix and describes its measured effect; it does not justify promotion. No seed-2 confirmation was run, and no tuning pass or V06 iteration followed. V04 and active contest submission v83 (ID 11244) are unchanged.

The panel covers ten known live maps at seed 1; it does not measure unknown-map generalization. Replay, index, feature, and cache artifacts are under the ignored `build/zoo/ares-v05-tyr12-separation-bugfix-20260929/` directory.

**Runtime-source fingerprint:** `cccae8b9bd815b5d3d898c43833a6ce0bba0cd12aaa0b3dca49778e1846ee007` (SHA-256 over sorted relative C++/header and `bot.toml` paths and file contents, NUL-separated).
