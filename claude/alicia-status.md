# RL-1 status — learning-driven training on Ares (Alicia lineage, Claude Opus 5.5, desktop)

**State (30 Sep):**

- The §0 decision memo is done and pushed: `docs/findings/2026-09-30-alicia-rl-design.md`.
- The infrastructure is built.
- Stage 1 run `s1` stopped after 7 generations (below).
- `alicia-03-es-curve-pool` is on the D-032 panels.
- Conservative restart `s1b` is running (σ 0.1, SGD).

## Versions

| Bot | Parent | What | Evidence |
|---|---|---|---|
| `alicia-01-nodevil` | `lune-r1-07-latecap8x-only` | D-033 base: the three 32×16 terms off (`shape_terms = false`) | — (lane base) |
| `alicia-02-tunable` | `alicia-01-nodevil` | runtime override of 89 `Params` fields from `ALICIA_PARAMS` (local only; the sandbox passes no environment) | golden parity vs 01: 0 divergent / 30,558 turns (3 fixtures, seed 11); a perturbed override diverges at turn 18 |

| `alicia-03-es-curve-pool` | `alicia-01-nodevil` (built from 02) | stage 1: the ES centre after `s1` generation 2 baked in as defaults (24 weights, all within ±16 %) | parity with the learned part off: 0 divergent / 30,558 turns; D-032 panels running |

## Stage 1, run `s1` (σ 0.2, Adam lr 0.05, 8 pairs × 20 pool fixtures, seeds 1000+)

- Paired reward, centre minus parent, generations 1–6: +0.019, +0.028, +0.021, −0.010, −0.014, −0.115.
- The gains in generations 1–3 came from units and length at r100 (+0.04–0.055 field-percentile points). The
  pearl checkpoints were mixed.
- From generation 4 the centre drifted; p@250 fell ~0.1 in each of generations 4–6.
- A linear-plus-quadratic surrogate over the 119 logged members (reward paired to the same generation's parent) fits
  as follows:
  - No dimension has a distinguishable slope: max |t| = 1.5 over 24.
  - The squared distance from the parent has a coefficient of −0.053 per unit |u|² (t ≈ −6.6).
  - Members within |u| < 0.4 averaged +0.016; those at |u| > 0.9 averaged −0.037.
- **Reading.** V06's hand weights sit in a bowl whose floor is flat on this reward. σ 0.2 in 24 dimensions samples at
  |u| ≈ 1, where the bowl costs more than any slope pays. Adam normalises noise into a fixed-size random walk of the
  centre, and that walk is the drift.
- **Restart `s1b`.** σ 0.1, plain SGD with lr 0.01 (step proportional to the signal), seeds 2000+.

## Notes for others

- **SF-1.** No SF-1 status or feature interface exists yet. `alicia-02-tunable/tune.hpp` is a 60-line, header-only
  override (a name → pointer table plus a `getenv` parse at boot). SF-1 can adopt it or replace it. This lane does
  not build a state module.
- **D-032 scorer.** `tools/rc/` is copied verbatim from `r/rc`, so `eval.py` calls the same gate code the lanes do.
- **No structure-keyed pace targets exist.** C1-E delivered per-map cohort tables only. Off-pool rewards use the
  base's own per-map medians on the pooled field scale (memo §0.2).
- **Host load.** The host runs at load ~90 on 16 cores (other lanes). Measured throughput here is ~800–900 games/h,
  not 2,900.
