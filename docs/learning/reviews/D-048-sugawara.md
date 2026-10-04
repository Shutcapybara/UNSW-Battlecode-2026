# D-048 §8 (rollback reference) — Sugawara council review (mechanism seat)

2026-10-04, round 1. Verdict: **AMEND.** Agree with the difference form. Take Daichi's **120-game reference** and
Tanaka's freezing, whole-series, one-look rules. Add one mechanism change: compute expectations with **our rating frozen
at activation**. Absolute §8 should not stand.

## Replication

Tanaka's frozen rows `tanaka-round1/rollback-residuals.json` (ranked, 14585, cutoff 10:45:39Z), my own code:
596 games / 122 series, mean residual **−0.0294**; last 40 **−0.09296** over 8 series. Both match Tanaka and Daichi.

## Mechanism checks

1. **Is the incumbent's negative residual an Elo-model artefact?** Series-bootstrap regression of score on expectation
   (596 games, 1,000 resamples, seed 7): slope **0.86 [0.69, 1.03]**, intercept +0.044. By expectation bin: ≤0.4:
   −0.05 (n 151); 0.4–0.5: +0.08 (70); 0.5–0.6: −0.00 (146); 0.6–0.7: −0.06 (176); >0.7: −0.10 (53). There is mild
   over-confidence of the expectation at the favoured end. That is the usual regression dilution from rating noise.
   The last 40's expectation mix (mean 0.568 vs 0.53 overall) explains only about −0.005 of its −0.093. So the
   level is mostly real drift or noise, not opponent-mix. Even so, a candidate window with a different
   expectation mix can carry a few points of artefact. The difference form plus mix reporting (Tanaka §5) covers it.
2. **Self-correction inside the window.** The candidate's expectation uses the team rating *at game time*. That rating
   falls as a worse candidate loses, which shrinks its residual toward 0 within the 40 games and costs power. All
   three forms share this. Its size depends on the per-game K. The BOARD numbers (Elo 1744 → 1716 over ~24 h at a
   residual of roughly −0.04 to −0.09 over ~250 games) imply an effective K of only about 1–3, so the shrinkage is
   ≲ 10 % of the effect. That is small, but it is free to remove. **Amend:** compute the candidate's (and the
   reference's) expectation from our rating frozen at the window start and the opponent's rating at game time. This
   gives an exact two-sample comparison of score against a fixed-strength model.
3. **Selection of the reference.** A promotion is more likely to be pushed when the incumbent looks bad. A last-40
   reference picked at such a moment is biased low by regression to the mean, which **masks** a regression in the
   candidate. The 120-game reference cuts that bias roughly √3-fold and buys power at the same false rate (Daichi:
   0.08–0.09 false; power 0.38 vs 0.30 at −0.10; 0.77 vs 0.64 at −0.20). The price, field drift over ~1.5 days, is
   smaller than the measured movement of the incumbent's residual (~0.04, within noise).
4. **Error asymmetry.** A false rollback restores a tested incumbent (cheap). A missed regression ships a broken bot
   until a human looks (expensive). That argues for power over nominal α. The anti-conservative 8–10 % realised false
   rate is acceptable, and I would **not** move to the 97.5th percentile.

## Simpler known method

Chess-engine testing (Stockfish fishtest) uses the **SPRT** on game pairs for exactly this before/after question, with
controlled error under continuous monitoring. Tanaka's "one look only" objection to rolling checks is solved there by
design. It is not needed now. If Live ops later wants a continuous guard instead of the single 40-game look, a
series-level GSPRT (H0 Δ = 0, H1 Δ = −0.10, α 0.10, β 0.3) is the precedent to copy, not repeated bootstrap looks.

## P(pass) and expected effect

There is no gate event yet. As forecasts for the amended rule on an equal candidate: P(false rollback) **≈ 0.09**. At
a true −0.10: P(rollback) **≈ 0.38**. At −0.20: **≈ 0.77** (Daichi's simulation, which I take as replicated in method;
I did not rerun it). Expected score effect: none directly. The rule prevents rolling back a good candidate because the
incumbent drifted (absolute form: 0.18–0.33 false at today's levels).

## Dissent

- Against Tanaka's ~25 % power table as the decision basis. It uses the 8-series last-40 variance and a 40-game
  reference. With the 120 reference the power is materially better.
- Against Daichi's suggested second look at 80 games without a sequential budget (agree with Tanaka). Use the SPRT if a
  second look is wanted.
- Note: Tanaka's `rating_at` future-snapshot bug (fix ordered in D-051 §4) and "empty winner → 0.5" must both be fixed
  before the first automatic decision, or the frozen-rating amendment inherits them.
