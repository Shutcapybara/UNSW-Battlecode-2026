# RL-1 (Alicia) — closing report: learning-driven training on Ares

**Date:** 2026-10-01 · **Author:** Claude Opus 5.5 (lineage Alicia, branch `r/alicia`) · **State:** lane paused at
wrap-up. Stage 1 is complete (two versions, both REJECT). Stage 2 was interrupted after 8 of 16 generations. Stages 3
and 4 were not started.

**Read with:**

- design memo: `docs/findings/2026-09-30-alicia-rl-design.md`
- stage-1 finding: `docs/findings/2026-10-01-alicia-stage1.md`
- status: `claude/alicia-status.md`

## Answer

**A learned weight vector on Ares (layer (a), evolution strategies) does not pass D-032 yet.** What blocks it is not
the optimiser. It is two properties of the problem:

1. **The reward must have the gate's shape.**
   - The lead's curve reward weights material (units and length at r100) half. Optimised, it learns *less churn*:
     equal material and win rate, every death rate down, ally head-on −14 %, births −12 %.
   - The gate's economy term is 38 % ally corpses (L29), so it scores that as −0.097 (`alicia-03`).
   - With the gate-shaped reward (four economy checkpoints as the objective, material and death rates as hinge
     guards) the optimiser finds real slopes:
     - the centre's economy is +0.016 ± 0.007 per paired generation over 15 generations;
     - six weights have |t| 3–4;
     - the first positive pool lower bound in the lane: +0.046 [+0.022, +0.066] (`alicia-04`).
2. **Whatever it learns stays on the maps it trains on.**
   - `alicia-04` loses the generalisation panel: win −0.066 [−0.099, −0.031], economy −0.018.
   - Stage 2 added five off-panel maps to training. After 8 generations its centre gains on the pool (ΔC +0.036 ±
     0.015) and not on the held-in maps (ΔC −0.014 ± 0.018).
   - With 20 of 30 fixtures per generation still pool maps, the pool dominates the gradient.
   - A global 24-weight vector with no map input reproduces L28's pool-vs-unseen split. The out-of-sample rule binds
     on training data, not only on map-keyed code.

**The lead's hypothesis ("hitting the curve is most of the win") was not supported where it could be read.**

- The curve-optimised `alicia-03` moved material on the generalisation panel (length +0.036, significant) with no
  change in win rate on either panel.
- The economy-optimised `alicia-04` raised the pool economy at equal pool win, and lost win off-pool.
- In neither version did curve gains turn into wins.

## Versions

| Bot | Parent | What | D-032 vs `alicia-01-nodevil` (seeds 1–3, paired) |
|---|---|---|---|
| `alicia-01-nodevil` | `lune-r1-07-latecap8x-only` | D-033 base: the 32×16 terms off | lane base |
| `alicia-02-tunable` | 01 | `ALICIA_PARAMS` boot override of 89 `Params` (local only; the sandbox passes no environment) | golden parity 0 / 30,558 turns |
| `alicia-03-es-curve-pool` | 01 (built from 02) | stage 1, curve reward, `s1` gen-2 centre | **REJECT**. Pool econ −0.097 [−0.131, −0.060]; generalisation (interrupted 572/744) econ −0.030, length +0.036 |
| `alicia-04-es-gate-pool` | 01 (built from 02) | stage 1, gate-shaped reward, `s1c` gen-14 centre | **REJECT**. Pool econ **+0.046 [+0.022, +0.066]**, units lb −0.062, win lb −0.042; generalisation econ −0.018 [−0.034, −0.001], win −0.066 [−0.099, −0.031] |

- **Parity.** Both learned versions golden-check with the learned part disabled: 0 / 30,558 turns.
- **CPU.** Neither was probed. Both were rejected, and their search caps stay within R-1's measured range: 03 is
  176 / 395, 04 is 143 / 355, against the parent's 160 / 384.

## Training runs

All runs use 8 antithetic pairs per generation, with the centre and the parent on the same fixtures. Summary rows
are in `game_stats/runs/alicia-train-<run>.jsonl`.

| Run | Stage | Reward | σ / optimiser | Fixtures per generation | Generations | Centre vs parent (paired) |
|---|---|---|---|---|---|---|
| `s1` | 1 | curve (½ economy, ¼ units, ¼ length) | 0.2 / Adam 0.05 | 20 pool, seeds 1000+ | 7 (gen 7 interrupted) | +0.02 in gens 1–3, then drifted to −0.115 |
| `s1b` | 1 | curve | 0.1 / SGD 0.01 | 20 pool, seeds 2000+ | 1 (stopped; same reward as `s1`) | — |
| `s1c` | 1 | gate-shaped | 0.1 / SGD 0.01 | 20 pool, seeds 3000+ | 16 | economy +0.016 ± 0.007 per generation |
| `s2` | 2 | gate-shaped | 0.1 / SGD 0.02 | 20 pool + 10 held-in, seeds 4000+ | 8 (gen 8 interrupted at wrap-up) | economy pool +0.036 ± 0.015, held-in −0.014 ± 0.018 |

**Stage-2 economy deltas per generation** (centre − parent, field-percentile points; held-in maps on the
base-referenced pooled scale):

| gen | pool | held-in | Δwin |
|---:|---:|---:|---:|
| 1 | −0.034 | −0.045 | 0 |
| 2 | +0.032 | −0.051 | −0.033 |
| 3 | +0.062 | −0.065 | −0.067 |
| 4 | +0.061 | +0.023 | −0.033 |
| 5 | +0.031 | −0.038 | 0 |
| 6 | +0.015 | +0.066 | −0.067 |
| 7 | +0.082 | +0.013 | +0.033 |

- **Moves after `s2` gen 7** (u = log-multiplier):

  | weight | u |
  |---|---:|
  | `bed_value` | −0.43 |
  | `w_flank` | +0.20 |
  | `pearl_value` | +0.19 |
  | `visit_weight` | +0.15 |
  | `split_value` | +0.14 |
  | `w_bed_block` | +0.12 |
  | `search_cap_late` | +0.12 |
  | `unseen_value` | −0.10 |

- **No version was made from `s2`.** It was interrupted, and its own held-in signal is negative.

## What the lane leaves behind

- **The infrastructure the brief asked for, in working order.**
  - `bots/alicia-02-tunable`: a runtime parameter override with golden parity (`tune.hpp`, 60 lines, header-only,
    and offered to SF-1).
  - `tools/alicia/env.py`: paired fixtures through `unswbc run` with the policy injected, scored by
    `tools.analysis.features`; resumable.
  - `tools/alicia/reward.py`: field-percentile curve, base-referenced pooled percentiles off-pool, hinge guards and
    the terminal term.
  - `tools/alicia/train.py`: antithetic ES with Adam/SGD, `--resume`, a checkpoint per generation.
  - `tools/alicia/eval.py`: checkpoint → bot directory, parity, D-032 panels and score through `tools/rc/lane.py`,
    which is copied verbatim so the scoring is not forked.
  - `tools/alicia/refs.py`: base references for maps without field data. `tools/alicia/report.py`: learning curves.
- **Measured facts for whoever continues.**
  - Per-member reward noise on 20–30 fixtures is ~0.04–0.06 (population sd). The economy slopes are ≤ 0.08 per unit
    log-multiplier.
  - Steps must be proportional to the signal: Adam's normalisation produced a random-walk drift.
  - σ must keep members at |u| ≲ 0.5: the curve reward has curvature −0.053 per unit |u|².
  - At 20–30 fixtures the pooled death-rate and material hinges fire on about half of all members (s1c 135/272, s2
    49/102), mostly on noise. The parent's own pooled rates move ~15 % between generations.
- **Unseen-map references are thin.**
  - C1-E delivered no structure-keyed targets.
  - Only five maps sit outside both panels (`arena`, `big_empty`, `Colosseum`, `default_small`, `stronghold`), and
    three of them end by elimination before r150.
  - `dilemma_10.map` fails the engine's map check.

## Recommendations

1. **If the lane resumes, do not continue `s2` as it stands.** Training must be weighted *toward* off-pool maps, not
   merely include them.
   - Either balance the gradient per map family (equal weight pool vs held-in), or select checkpoints on held-in
     reward only.
   - That needs more held-in maps. Generate them with the `maps/new` generator, so no panel map is used.
2. **Fix the guard noise before more ES.** Use the guards as constraints on the *centre* checked every k generations
   on a larger fixture set, not as per-member hinges on 20 games.
3. **Layer (b), the scorer, is not warranted yet** (the L16 trigger). The weight surface has slopes, but they do not
   transfer. A richer function of the same features would fit the pool faster.
4. **For the gate (L21/L29):** two independent results now show the economy term rewarding churn and the material
   term rewarding its absence. A corpse-share column, or a material-adjusted economy, would let a curve-optimising
   lane be scored on what it optimises.

## Ledger rows touched (proposed weights)

- **L16** (offline-learned weight table), 0.5 → **0.4**.
  - The gate-shaped ES finds real pool slopes, but no learned vector carries to unseen maps (04: generalisation win
    −0.066; stage 2 held-in −0.014 ± 0.018).
  - One step only: stage 2 was interrupted, and off-pool-weighted training is untested.
- **L04** (fitted weights beat hand weights), 0.6 → **0.5**. They do on the fitted maps, and they do not off them.
- **L29** (the metric rewards churn), 0.8 → **0.9**. An independent mechanism: `alicia-03` churned less and lost 0.10
  economy at equal material and win.
- **L28** (pool edge is map identity), 0.9. Unchanged, with new evidence: a map-blind weight vector learns the pool
  as well.
- **L21** (the +0.05 gate is the right shape), 0.3. Unchanged; `alicia-03` is direct evidence for a retention clause.
- **L14** (exploration value). The joint economy slope in `s1c` is against more unseen value (t −4.0), the opposite of
  `ra`'s single-knob pool result. No weight change.
- **L27** (learned decision functions). Not tested (layer (c) was not attempted, by design). Unchanged.
