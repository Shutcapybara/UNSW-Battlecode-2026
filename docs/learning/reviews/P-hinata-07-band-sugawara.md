# Review: Hinata 13:37Z ≥ 1725 reading (P-hinata-07 append; D-083 §A, D-084 §D) — Sugawara, 5 Oct 2026 14:40Z

**Verdict: amend.** Numbers replicate; the conclusion "conversion/combat, not the queen" should read **"early combat and no lead built; conversion is band-invariant; queen difference unresolved (CI ±0.2)"**.

Inputs: `build/hinata/curves2/g_s*.jsonl` (rows 8e7ecc6d6735, owner-corrected), population 17530 ranked post-m2, band = opponent Elo in last snapshot, series bootstrap 1,000 × seed 7, 5–95 %. Code `build/sugawara/qband/{chk.py,chk_mid.py,out.txt}`.

## Replication

| 17530 vs | view | n games / series | queen alive r300 us/opp (diff) | total r300 us/opp (diff) | r300 leads converted |
|---|---|---|---|---|---|
| ≥ 1725 | reached r300 (Hinata) | 33 / 9 | 0.45/0.48 (−0.03 [−0.18, +0.12]) ✔ | 92.1/85.9 (+6.2 [−18.4, +31.3]) | 10/16 |
| ≥ 1725 | carried (all games) | 45 / 9 | 0.42/0.49 (−0.07 [−0.27, +0.11]) | 78.4/77.6 (+0.8 [−24.9, +24.8]) | 15/21 = 71 % |
| 1725–1900 | reached r300 | 29 / 8 | 0.45/0.45 (0.00) | **94.4/76.6 (+17.8 [−0.7, +38.8])** ✔ (Hinata [+0.1, +39.4]) | 10/15 |
| 1725–1900 | carried | 40 / 8 | 0.42/0.45 (−0.03) | 80.7/69.7 (+10.9 [−11.2, +35.2]) | 15/20 |
| < 1725 | carried | 45 / 9 | 0.51/0.53 (−0.02) | 103.8/62.3 (+41.5 [+15.7, +64.2]) | 26/35 = 74 % |

W–L ≥ 1725 17–28; losses: elimination 11, longest 10, queen 7 ✔. Carried view: an eliminated side counts as 0 at r300; a winner that ended the game before r300 carries its final state (approximation).

## Points

1. **Survivorship.** 7 of the 11 elimination losses vs ≥ 1725 end before r300 (rounds 158–270), so the r300 columns drop them. The "length lead at r300" vs 1725–1900 is +17.8 among games that reach r300 but +10.9 [−11.2, +35.2] over all games, and +0.8 vs all ≥ 1725. The lead claim does not survive the carried view. Report both views at the trial-3 look.
2. **Conversion is not the gap.** Leads converted at r300: 71 % (≥ 1725) vs 74 % (< 1725), carried. What changes with band is how often we lead (21/45 vs 35/45) and the size of the lead (+0.8 vs +41.5). So it is the economy race plus early combat, not "defend the lead mid-game". The RL "action: defend the lead" line has no support in these rows.
3. **Queen.** Parity is a point estimate with ±0.2 intervals (9 series). "Not the queen" is not established; "no detectable queen deficit for 17530 at n = 9 series" is. Note that 17 of 28 losses ended at the limit with our queen dead (queen 7 + longest 10, where both queens are dead), against 12/16 below 1725. The mix shifts towards elimination, which is consistent with the rest of this review.
4. **Mechanism/legality:** descriptive only. Band = opponent Elo is fine for analysis, but must never become a bot input (identity/rating are not in the IO block). Hinata's "in-play strength proxies (opp length/heads)" are legal observations. No leakage issue: no split is touched.

## Precedent

Lux S2 / Halite post-mortems: mid-skill gaps were usually economy tempo, with conversion roughly constant across bands. That is the same pattern as point 2.

## Forecast (log; Brier closed per D-072 §B)

At the trial-3 look, for bokuto-18 vs ≥ 1725, carried view: lead converted ≥ 65 %: 0.65; total r300 diff carried ≥ +10: 0.35.
