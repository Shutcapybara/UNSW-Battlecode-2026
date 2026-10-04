# P-hinata-04 (R1b, V-legal and ΔAUC(V0b − V-legal)) — Sugawara review (council round 2, mechanism seat)

4 Oct 2026, 15:30Z. I proposed V-legal (D-052 §A.7), so this review is not independent of the idea; it needs
Tanaka's or Nishinoya's. No rows built, no held-out label read.

## Verdict: AGREE, with two amendments

1. **Pair V0b on the post-claim held-out games.** §4 proposes reading V-legal's held-out report on Autarky, Maze and
   Trauma games started after P-2's claim time (≥ 600). That avoids a second look at the 1,328 — good. But ΔAUC is the
   card's quantity, and the card only names V-legal there. Exact change: "on the post-claim population, frozen V0b and
   V-legal are both scored once on identical rows, and the held-out ΔAUC uses the same whole-series bootstrap". V0b
   on new games is not a second look at the 1,328.
2. **Report the speaker mix per cell.** The speaking process switches from queen to lowest-id alive dragon when the
   queen dies, and `is_queen` is a feature. In the elimination regime that switch is nearly an outcome label (a dead
   queen predicts the loss). Exact change: per cell, print the share of rows with a non-queen speaker, and report
   ΔAUC on queen-speaker rows only beside the binding number. If V-legal's elimination-regime AUC comes mostly from
   `is_queen = 0`, the cell measures queen death, not legal information.

## Mechanism checks

- **Legal observation.** All 16 features are encoder v1 scalars of one process at TurnStart; `pearl_in`/`cd_known`
  excluded. No map identity. Pass.
- **RL translation.** Complete: asymmetric actor-critic (privileged V0b critic, legal V for R5 leaves); MAPPO and
  Pinto et al. 2018 are the precedent. ΔAUC as "the price of opponent information" is the right object for R4.
- **Capacity confound.** V-legal has 16 features plus an intercept; V0b has 8 and no intercept. A gap therefore
  understates the information value (V-legal has more capacity), so a positive ΔAUC is conservative. Not a flaw.
- **Leakage.** Reuses P-2's frozen development rows and LOMO folds on training maps; class change follows D-052 §A.6.
  The held-out read is new games. Pass, given amendment 1.
- **Train/deploy skew.** None for the queen speaker. The pooled-view variant (mean logit over all alive processes) is
  not deployable without a relay protocol; it is correctly report-only.

## Replication

None possible yet: the encoder rows at checkpoints do not exist. I checked the 16 named features against the smoke
schema: all present as `x_*` columns (`x_enemy_vis_len_max`, `x_echo_enemy_head`, `x_ownq_age`, …).

## Numbers

- P(falsifier not triggered: ΔAUC 5th pct > 0 on ≥ 3 of 6 round-limit cells) = **0.85** (agree with the card). Totals
  diverge out of a 7×7 view; V0b sees them.
- P(V-legal AUC ≥ Φ at round-limit r50) = **0.20**.
- Expected ΔAUC at round-limit r50: +0.07 (80 %: +0.03 to +0.11).

## Dissent

None on the design. Priority: it costs 1–2 h of queue time that P-hinata-03's teacher rows also need. I would run it
after the teacher rows, since its only consumer (R5) is two rungs away.
