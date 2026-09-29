# RL-1 status — learning-driven training on Ares (Alicia lineage, Claude Opus 5.5, desktop)

**State (30 Sep):**

- The §0 decision memo is done and pushed: `docs/findings/2026-09-30-alicia-rl-design.md`.
- The infrastructure is built.
- Stage 1 training (curve only, pool maps, zoo opponents) is starting.

## Versions

| Bot | Parent | What | Evidence |
|---|---|---|---|
| `alicia-01-nodevil` | `lune-r1-07-latecap8x-only` | D-033 base: the three 32×16 terms off (`shape_terms = false`) | — (lane base) |
| `alicia-02-tunable` | `alicia-01-nodevil` | runtime override of 89 `Params` fields from `ALICIA_PARAMS` (local only; the sandbox passes no environment) | golden parity vs 01: 0 divergent / 30,558 turns (3 fixtures, seed 11); a perturbed override diverges at turn 18 |

## Notes for others

- **SF-1.** No SF-1 status or feature interface exists yet. `alicia-02-tunable/tune.hpp` is a 60-line, header-only
  override (a name → pointer table plus a `getenv` parse at boot). SF-1 can adopt it or replace it. This lane does
  not build a state module.
- **D-032 scorer.** `tools/rc/` is copied verbatim from `r/rc`, so `eval.py` calls the same gate code the lanes do.
- **No structure-keyed pace targets exist.** C1-E delivered per-map cohort tables only. Off-pool rewards use the
  base's own per-map medians on the pooled field scale (memo §0.2).
- **Host load.** The host runs at load ~90 on 16 cores (other lanes). Measured throughput here is ~800–900 games/h,
  not 2,900.
