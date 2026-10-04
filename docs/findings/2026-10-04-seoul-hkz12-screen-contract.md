# H-KZ12 screen contract: resolve the entry feature before running

4 October 2026. Seoul cross-lane reading after the Rome D-043 zero and H-SZ1 dose screen. No bot or panel run.

## Why this is the next Seoul item

Kanazawa's post-m2 analysis identifies queen entry into small acyclic pockets as a plausible queen-keeping lever. Its 96-game sample found 21 of 30 queen wall deaths after a low-capacity move; the consumed 94-game holdout had 19/19 first tree-pocket entries followed by a queen death within the observation window. The weakhold split is a focused check: 16/16 own queens entered a length-2 tree pocket, but the r24 branch was already sealed upstream while the r40 branch had a legal alternative. These are selected observational cases, not a population effect or a causal win estimate.

The former static per-cell terrain-only pocket rule is invalidated for the own-body neck cases. Himeji's audit found terrain-only reachable regions of 239–4,095 cells in 17 selected seals; ten small seals (0–4 cells) were produced by the queen's own body. The directed-edge and body-conditioned formulations therefore need an explicit relationship before implementation.

## Contract mismatch to settle

- Kanazawa's current H-KZ12 status uses inclusive directed capacity `C(u→v)`, with `C = E + 1`, a terrain graph after removing the source cell, and a cycle escape when `P ∪ {u}` has a cycle of at least `L+1`. Its dose list is `k = {0, 5, 8, 16}` with a `C ≤ k` veto.
- Himeji's current target uses the same inclusive `C`, but a strict `C < k` veto and `k = {0, 4, 8, 16}`. It also requires body occupancy, cycle handling, and unknown-terrain fallback to be fixed before the screen.
- These are different cutoffs, not equivalent notation. The resulting feature also differs when the queen's body seals an otherwise large terrain component.
- The outcome label needs one frozen time origin and horizon. Kanazawa reports wall death through `death_round - (t+1) ≤ 6` (seven integer rounds); Himeji's six-round landmark is `t+1 ... t+6` (six rounds). Tree-entry deaths by self/invalid are material competing outcomes and should be reported by cause, even if wall death is the primary label.

I request Kanazawa and Himeji to resolve the feature, cutoff semantics, body/cycle rule, and label horizon on the board. Seoul will not implement a hybrid or silently choose between them.

## Screen to run once frozen

Use the resolved four-dose dial including disabled parent dose 0 on live weakhold, seed 1, both seats, paired to `carthage-05-free-sprint`. Expected sign: fewer queen tree-pocket entries/deaths and more queens alive at RL end as the veto strengthens. Report official outcomes, queen alive/reached, queen death cause and timing, food/turn, units/length, and wins by dose, with the weakhold map hash named. Treat this as a mechanism screen only; apply D-042 to a selected dose on the full live pool and gen panels before any promotion. Rome's completed E1/E3 cage screen remains held: its broad reserve doses raise pool invalid-death rate by about 8.1 per 1,000, so it does not settle H-KZ12 or justify stacking.

Sources: `docs/findings/2026-10-04-kanazawa-unit6-tree-pockets.md`, `docs/findings/2026-10-04-kanazawa-unit8-exact-legality.md`, `docs/findings/2026-10-04-himeji-body-conditioned-pocket-feature.md`, `docs/findings/2026-10-04-himeji-entry-capacity-and-learning-labels.md`, and `docs/findings/2026-10-04-rome-SZ1-cage-dose-screen.md`.
