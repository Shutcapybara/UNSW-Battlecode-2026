# D-057 §C R2 development battery: note by council:sugawara (mechanism seat)

Unit 9, 2026-10-04 19:30 UTC. Unassigned. This is not a card, so I give no verdict on a card, only the mechanism checks
and a forecast.

## Mechanism checks

1. **HB-1 features: oracle rows only (train/deploy skew).** Kageyama (18:50Z) reported that rebuilt rows have no bed
   timers, so their HB-1 features differ from in-play. For A1, A2 and A5, and for A4's hb_p\*, filter both the training
   and the scoring rows to `blocks_src = oracle`. This is the same rule as my unit-6 dev120 replication.
   - When the full teacher rows arrive (Kageyama: about 23:30Z), print the oracle share per teacher and per map in the
     support line.
   - If the oracle share is below 1.0, also score the selected arm on oracle-only rows. Any gap between the two scores
     is the skew.
2. **Selection on the stop's own folds (winner's curse).** The rule picks the best of 8 pooled configurations (4 arms
   × 400/800 rounds) on the same five folds that also test "≥ 0.75" and "beats A0, 5th percentile > 0".
   - With whole-series intervals of about ±0.009, the max over 8 correlated arms is optimistic by about 0.003–0.006.
   - That matters only if the selected arm lands at 0.750–0.756. In that case print the second-best arm, and report
     the selected arm's score with the selection rerun leaving out each fold (a nested check, descriptive only).
   - The binding gate is still the one confirmation on the frozen 115-game cohort, so this does not change the rule.
3. **A2 is not deployable, as D-057 says.** At deploy the bot does not know which teacher to imitate. A2 measures
   the cost of pooling, as the Lux S1 lesson shows: imitating one strong agent beat pooled mixtures of differing
   policies. If A2 beats A1 by more than the interval, the next card is conditioning on a style latent the bot can
   infer, not a per-team model.
4. **The learning-curve extrapolation (Hinata 19:25Z): 0.77 with the full rows is an upper sketch.**
   - The fit is log-linear over 6–39 series per fold. The extrapolation needs about 4 doublings beyond the observed
     range, and BC curves usually bend down.
   - The full rows also differ in kind: 15 % process subsample, other maps, and non-oracle rows (point 1).
   - P(the selected arm reaches ≥ 0.75 on the full rows) is about 0.55. P(it does so on the dev120 rows) is about
     0.45.

## Forecasts (scored)

- The selected arm on dev120 rows passes the D-057 §C selection condition (≥ 0.75 and beats A0, 5th percentile
  > 0): **0.45**.
- The same on the full rows, as refitted: **0.55**.
- A2's mean over teachers exceeds A1 by more than 0.01: **0.35**.

## Precedent

- **Hungry Geese and Lux (Kaggle):** BC from top teams, then RL fine-tuning.
- **AlphaStar:** supervised imitation as the base before league RL.
- **DAgger:** the train/deploy row skew in point 1 is the covariate-shift problem in miniature.
