# Ares V06 — expanded search and supported threat evaluation

**Date:** 2026-09-29
**Status:** experimental; not admitted to the all-map frontier; not submitted

V06 tests whether C++ headroom can recover search-heavy ideas from older Tyr,
Bifröst, and Skadi work while staying inside the sandbox CPU budget. It branches
from Ares V05, which already contains the two separation exception fixes. V05,
V04, and active contest submission v83 were left unchanged.

## Changes

- Restored the broad bounded-search profile used by historical Bifröst and
  Skadi snapshots: 160 target nodes normally, 64 at saturation, and 60 during
  the first two turns. Existing late-game and sparse-board caps remain active.
- Raised room flood limits from 22/36 to 24/40 and restored Tyr's
  12-length three-step candidate horizon, retaining Ares's saturation, late,
  and sparse guards.
- Ported Skadi V02's experimental Fafnir size-matched support rule. A threat
  cost is discounted only when an observed ally at least as long as the
  attacker is within three tiles; support counts are cached for each decision.

The source trail and decision to exclude other ideas are documented in
[the Tyr](../tyr-family.md), [Bifröst](../bifrost-family.md),
[Skadi](../skadi.md), and [Fafnir](../fenrir-family.md) notes. In particular,
V06 does not import Bifröst's wider route-ownership rule or Skadi's exit-only
guard, which lacked robust positive evidence.

## Build and CPU probe

V06 compiled cleanly with C++20 and `-O2 -Wall -Wextra -Wpedantic`.

The four-game native sandbox probe on Schooltime and Portals, both seats, had
**zero timeout or crash errors**. The CPU tool reported p50 max-of-games 4.7M
points, p99 max 7.4M, and an 8.6M maximum. A prior four-game Big Empty/Trauma
probe also had zero errors (p50 5.2M, p99 7.1M, maximum 8.1M). These small
samples show comfortable observed headroom, but do not estimate rare worst-case
runtime reliably.

## Seed-1 fixed panel

The panel used the eight current `run_panel.ZOO` opponents, ten live maps, and
both seats (160 games per version). V06 used `unswbc 1.2.2`; all fixtures
returned successfully and all 160 replays extracted. The scorecard divides
each side-game by its map's saved field median in
`docs/analysis/benchmarks/map_reference_medians.json`.

| Metric | V05 | V06 | Change |
|---|---:|---:|---:|
| Wins–losses–draws | 118–41–1 | 122–38–0 | +3.5 expected-score points |
| Expected-score share | 74.06% | 76.25% | +2.19 percentage points |
| Mean of normalized pearl checkpoints | 1.0974 | 1.1107 | +0.0133 |
| Pearls at r50, normalized | 0.988 | 0.970 | −0.017 |
| Pearls at r100, normalized | 1.054 | 1.102 | +0.048 |
| Pearls at r150, normalized | 1.134 | 1.152 | +0.019 |
| Pearls at r250, normalized | 1.214 | 1.219 | +0.004 |
| Dragons at r100, normalized | 1.071 | 1.200 | +0.129 |
| Total length at r100, normalized | 1.009 | 1.035 | +0.026 |
| Births by r100, normalized | 1.000 | 1.085 | +0.085 |

Tier-2 death rates are per 1,000 dragon-turns:

| Rate | V05 | V06 | Change |
|---|---:|---:|---:|
| Wall | 7.669 | 7.763 | +1.2% |
| Own body | 4.247 | 3.662 | −13.8% |
| Ally body | 2.531 | 2.467 | −2.5% |
| Ally head-on | 0.929 | 0.974 | +4.8% |
| Invalid action | 0.000 | 0.000 | unchanged |

## Decision and limits

V06 improves round-100 retention substantially and improves its fixed-panel
expected score. Length at r100 also rises, and no hygiene rate increases by
more than the 10% guardrail. However, the normalized economy mean improves
only +0.0133, short of the documented +0.05 parent-relative gate. The r50
pearl checkpoint falls. Therefore V06 does **not** pass the BENCHMARKS.md
gate and remains experimental; it is not submitted or added to the frontier.

This is one seed over ten known live maps. No seed-2 confirmation or unknown-map
screen was run, and the four-game CPU probes cannot rule out rare TLEs. The
measured sandbox points support using the larger bounded profile, but do not
justify treating timeouts as eliminated. No further Ares iteration was run.

**Runtime-source fingerprint:** `f51351c008b3e55fc13252cd3e265fba6b80d9211aa8aecba7a76226c359a294` (SHA-256 over sorted C++/header and `bot.toml` names and contents, NUL-separated).

**Artifacts:** ignored local panel output is under
`build/zoo/ares-v06-expanded-search-support-20260929/`; CPU probes are under
`build/cx/ares-v06-cpu-probe.jsonl` and
`build/cx/ares-v06-dense-cpu-probe.jsonl`.
