# D-048 §8 review — Daichi (Live ops), 4 Oct 2026 12:00Z

**Recommendation: amend.** Adopt the difference form, with the reference window widened to the replaced submission's
last **120** ranked games (all of its ranked games if fewer). Keep the −0.08 threshold, the series-bootstrap 95th
percentile < 0 condition and the crash/disqualification clause. Report the realised false-rollback rate (about 8–9 %,
not 5 %) next to the rule.

## Method

`tools/daichi/rollback_power.py` (on `r/daichi`). Source: submission 14585, 611 ranked games / 125 series since
2 Oct 04:22Z (corpus team-7 games, replay-header attribution, score − Elo expectation from the ladder snapshots;
map_era post-m2). The series are centred to a true residual of 0, then shifted to an incumbent level (0, the observed
−0.029, the rolling-40 −0.07). Windows are built by resampling whole series until 40 (or 120) games. A candidate's
first 40 is shifted by the true difference delta. Each simulated decision applies the rule as written, with a 200-
resample series bootstrap for the 95th percentile. 1,500 simulations per cell (Monte Carlo SE ≤ 0.013).

## Result: P(rollback)

| incumbent true level | candidate − incumbent (true) | absolute §8 | difference, ref last 40 (D-048 §8) | difference, ref last 120 |
|---|---|---|---|---|
| +0.000 | +0.00 | 0.10 | 0.08 | 0.08 |
| +0.000 | -0.05 | 0.24 | 0.16 | 0.21 |
| +0.000 | -0.08 | 0.37 | 0.24 | 0.29 |
| +0.000 | -0.10 | 0.46 | 0.30 | 0.38 |
| +0.000 | -0.15 | 0.67 | 0.45 | 0.59 |
| +0.000 | -0.20 | 0.85 | 0.64 | 0.77 |
| -0.029 | +0.00 | 0.18 | 0.08 | 0.09 |
| -0.029 | -0.05 | 0.38 | 0.17 | 0.22 |
| -0.029 | -0.08 | 0.51 | 0.24 | 0.31 |
| -0.029 | -0.10 | 0.58 | 0.30 | 0.39 |
| -0.029 | -0.15 | 0.78 | 0.48 | 0.59 |
| -0.029 | -0.20 | 0.90 | 0.63 | 0.75 |
| -0.070 | +0.00 | 0.33 | 0.08 | 0.09 |
| -0.070 | -0.05 | 0.53 | 0.16 | 0.19 |
| -0.070 | -0.08 | 0.67 | 0.26 | 0.31 |
| -0.070 | -0.10 | 0.74 | 0.29 | 0.37 |
| -0.070 | -0.15 | 0.90 | 0.49 | 0.59 |
| -0.070 | -0.20 | 0.96 | 0.65 | 0.78 |

## Reading

1. **The absolute form (§8 as written) is not a test of the candidate.** It rolls back an *equal* candidate with
   probability 0.10 when the incumbent is at expectation, 0.18 at the incumbent's measured level (−0.029) and 0.33 at
   its rolling-40 level (−0.07). Its apparent power (0.51–0.67 at delta −0.08) is mostly the incumbent's own drift.
   The Chair's concern holds.
2. **The difference form fixes the level dependence.** False rollback stays 0.08 at every incumbent level. Cost: the
   difference of two 40-game windows has about √2 the noise. Power is 0.24 at delta −0.08, 0.30 at −0.10, 0.48 at
   −0.15 and 0.64 at −0.20.
3. **A 120-game reference keeps the false rate (0.08–0.09) and regains power:** 0.31 at −0.08, 0.38 at −0.10, 0.59 at
   −0.15, 0.75–0.78 at −0.20. 120 games is about 1.5 days of ranked play at the present rate (611 games in 56 h). Field
   drift over that span is the price. The incumbent's residual moved by about 0.04 between its full window and its last
   40, which is within noise, so I judge the trade worth it.
4. **None of the forms holds 5 %.** With 8–10 series per 40-game window, the series bootstrap is anti-conservative.
   The realised one-sided false rate is 8–10 %. If the Chair wants 5 %, using the 97.5th percentile is the obvious
   lever. Not simulated here, so not recommended blind.
5. **What 40 games can see.** At n = 40, any form catches a −0.20 regression only about 2 times in 3 and a −0.10
   regression about 1 time in 3. The rule is a guard against a broken promotion, not a measurement of a small loss.
   The crash and disqualification clause and the D-046 §4 local gate carry the rest. I suggest a second look at 80
   games under the same rule (not simulated, and it raises the family-wise false rate).

## Assumptions and limits

- 14585's series-level dispersion is assumed to apply to a candidate. Old and new windows are drawn independently,
  and drift *between* windows is not modelled.
- The Elo expectation uses the team rating at game time. That rating is inherited and then moves with the new
  submission's results, which shrinks a real residual over the window. All three forms share this.
- Ranked games played inside a battles.json activation window are excluded (D-048 §4) before either window is formed.
