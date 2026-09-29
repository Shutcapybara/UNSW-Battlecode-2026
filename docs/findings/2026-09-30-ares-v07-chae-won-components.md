# Ares V07 — isolated Chaewon components

**Date:** 2026-09-30  
**Status:** both candidates experimental; neither passes the parent-relative acceptance gate

## Question and variants

This experiment tests Chaewon-derived components separately on children of Ares V06. The atlas-only snapshot was subsequently renamed to `ares-v08-atlas-only` without source or benchmark changes; the original V07 name is retained here to describe the experiment and its artifact paths. `ares-v07-atlas-only` activated Ares's dormant exact public-map matcher. Once one map uniquely matches the visible edges and portal ids, the policy receives complete terrain and portal topology; atlas-loaded portal ids are also registered with the existing radio scheduler.

`ares-v07-hold-only` ports Chaewon Y05's HOLD report. A non-crown move that ends beside a known paired portal with a landing outside vision replaces the turn's sonar schedule with one ray carrying the post-move head cell and round. A receiver trusts that cell for two rounds and raises the blind-landing risk to the existing occupied-body level. Ares already assigns packet type 7 to split handoff, so HOLD uses type 8 and does not replace a pending handoff. The HOLD child does not activate the atlas or probe-result cache.

Logged mirror scrims verified activation: the atlas marker `ACT:atla` was recorded 621 times on Schooltime, and `ACT:hold` 1,646 times on Portals. These are activation events across both teams, not unique maps or unique portal pairs. The replay logger stores at most eight marker characters, which is why the atlas marker uses the shortened `ACT:atla` label.

## Build and benchmark method

Both final sources compiled with C++20 and `-O2 -Wall -Wextra -Wpedantic`; both candidate manifests parse as TOML. Each arm ran the same seed-1 panel: the eight current `run_panel.ZOO` opponents, ten live maps, both seats (160 fixtures), with `unswbc 1.2.2`. All fixtures returned `rc=0`; all 160 replays per arm extracted successfully. Metrics below use the fixed per-map field medians in [`map_reference_medians.json`](../analysis/benchmarks/map_reference_medians.json). Each displayed Tier-1 number is the median across side-games of the per-map-normalized value; the pearl mean is the arithmetic mean of the four checkpoint medians. Tier-2 rates are medians per side-game, in deaths per 1,000 dragon-turns.

| Version | W–L–D | Expected score | Pearls mean4 | Units r100 | Length r100 |
|---|---:|---:|---:|---:|---:|
| V06 parent | 122–38–0 | 76.25% | 1.111 | 1.200 | 1.035 |
| V07 atlas-only | 119–41–0 | 74.38% | 1.299 | 1.052 | 0.965 |
| V07 HOLD-only | 114–46–0 | 71.25% | 1.116 | 1.134 | 1.042 |

| Version | Pearls r50 | Pearls r100 | Pearls r150 | Pearls r250 | Mean4 change vs V06 |
|---|---:|---:|---:|---:|---:|
| V06 parent | 0.970 | 1.102 | 1.152 | 1.219 | — |
| V07 atlas-only | 1.217 | 1.326 | 1.309 | 1.342 | +0.188 |
| V07 HOLD-only | 0.970 | 1.107 | 1.152 | 1.235 | +0.005 |

| Tier-2 death rate / 1k turns | V06 | Atlas-only | Change | HOLD-only | Change |
|---|---:|---:|---:|---:|---:|
| Wall | 7.763 | 8.141 | +4.9% | 7.602 | −2.1% |
| Own body | 3.662 | 4.561 | +24.6% | 3.539 | −3.4% |
| Ally body | 2.467 | 3.006 | +21.9% | 2.617 | +6.1% |
| Ally head-on | 0.974 | 2.967 | +204.8% | 0.845 | −13.2% |
| Invalid action | 0.000 | 0.000 | unchanged | 0.000 | unchanged |

## Decision

**Atlas-only fails.** Its pearl mean clears the +0.05 economy threshold by a wide margin, but both normalized r100 units and length fall, own-body and ally-body deaths exceed the 10% guardrail, ally head-on deaths rise sharply, and expected score falls 1.88 percentage points. Its median share of deaths within two steps of a portal also rose from 0.251 to 0.446. The added map knowledge appears to drive more pearl capture while creating dangerous portal/occupancy routes.

**HOLD-only fails.** It reduces ally head-on deaths 13.2% and no tier-2 rate rises more than 10%. However, its pearl mean improves only +0.005, normalized r100 units fall 0.066, and expected score falls 5.00 percentage points. The HOLD signal's targeted safety improvement did not preserve the full-panel result.

Neither version meets the [`BENCHMARKS.md`](../analysis/BENCHMARKS.md) gate. No seed-2 confirmation, combined variant, or tuning pass was run. They remain separate experimental snapshots; V06 and the active contest candidate are unchanged.

## Sandbox CPU screen

Each candidate also ran four sandbox fixtures against Gavroche V32: Schooltime and Portals, both seats, seed 1. Both had zero timeout/crash errors.

| Version | p50 max-of-games | p99 max | Maximum |
|---|---:|---:|---:|
| V06 dense probe reference | 4.7M | 7.4M | 8.6M |
| V07 atlas-only | 4.4M | 6.6M | 7.9M |
| V07 HOLD-only | 4.7M | 7.4M | 8.4M |

These are small samples; they establish no rare worst-case guarantee.

**Atlas runtime-source fingerprint:** `3eae1b33d69435fd2cc46fe823d80593f88aaef0fd881916d3f8c3d7149383dd`  
**HOLD runtime-source fingerprint:** `82d03bc48a105f176f5a5b113b66824ff8974a26c85af81384167caa6c5be057`

**Artifacts:** fixed panels and extracted features are in the ignored `build/zoo/ares-v07-atlas-only-20260929/` and `build/zoo/ares-v07-hold-only-20260929/` directories. The paired scorecard is `build/zoo/ares-v07-chae-won-scorecard-20260930.json`; CPU probes are under `build/cx/ares-v07-atlas-cpu-probe-20260930.jsonl` and `build/cx/ares-v07-hold-cpu-probe-20260930.jsonl`.
