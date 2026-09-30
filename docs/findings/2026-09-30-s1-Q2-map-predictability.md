---
id: S1-Q2-map-predictability
author: s1
kind: observation
question: Are some maps just more random?
evidence: index + ladder (40,233 decided in-scope games with ratings; 17,497 top-50-vs-top-50); elimination and length from the replay store (40,593 decoded)
query: python3 tools/s1/questions.py q2   → build/s1/out/q2/maps.csv
---

**Answer: yes.** Portals is the least predictable map at every scope, and Schooltime and Queen of Spades the most.

- Among top-50 pairs, 100 Elo is worth 0.16 logit on Portals and 0.49–0.53 on Schooltime/QoS, 3×–3.4× more.
- Predictability tracks how games end. Portals almost never ends in elimination and is decided by length at round 500.
  The elimination maps are more predictable.

**Model.** Per map: `logit P(A wins) = a + b·gap/100`.

- **Brier skill** = 1 − Brier(model) / Brier(constant).
- **Upset rate**: the share of |gap| > 100 games that the lower-rated side won.
- Elimination share and median game length (`R`, rounds) come from decoded replays.

| map | slope/100 Elo (in scope) | slope (top-50 v top-50) | Brier skill (in scope) | skill (top-50 pairs) | upset rate | side-A intercept at gap 0 | elimination share | median rounds |
|---|---|---|---|---|---|---|---|---|
| Portals | **0.29** ± 0.02 | **0.16** ± 0.05 | 0.072 | 0.006 | 0.30 | −0.03 | **0.02** | 500 |
| Prisoners Dilemma | 0.32 | 0.33 | 0.098 | 0.028 | 0.27 | −0.01 | 0.77 | **126** |
| Trauma | 0.35 | 0.36 | 0.102 | 0.028 | 0.24 | −0.16 | 0.09 | 500 |
| Default | 0.38 | 0.29 | 0.108 | 0.023 | 0.26 | −0.12 | 0.57 | 418 |
| Trophy | 0.39 | 0.29 | 0.124 | 0.023 | 0.22 | −0.16 | **0.94** | 183 |
| Slithery Fight | 0.42 | 0.27 | 0.124 | 0.016 | 0.25 | +0.09 | 0.03 | 500 |
| Queen Of Spades | 0.44 | **0.53** | 0.128 | **0.055** | 0.23 | −0.10 | 0.78 | 270 |
| Devil | 0.45 | 0.37 | 0.144 | 0.033 | 0.21 | −0.11 | 0.88 | 168 |
| Autarky | 0.46 | 0.41 | 0.147 | 0.042 | 0.18 | −0.21 | 0.54 | 434 |
| Schooltime | **0.49** | 0.47 | **0.148** | 0.048 | 0.22 | +0.02 | 0.24 | 500 |
| pooled | 0.39 ± 0.007 | 0.34 ± 0.02 | | | | | | |

"In scope" = games with a current top-50 side or team 7. "All games" gives the same order.

- **Draws** are essentially absent: 7 in 53k.
- **Seat.** At equal Elo, side A is worse on Autarky (−0.21 logit), Trauma and Trophy (−0.16) and Default (−0.12).
  Q3's seat table shows it in play: at r100, side B has more pearls on every map but Slithery (Devil 124 vs 71). Layout
  parity is part of the map.
- **Among top-50 pairs, Elo barely predicts a single game on any map.** Brier skill is 0.006–0.055.

**Reading.**

1. Map length is the other axis of "early game".
   - On **PD** (median 126 rounds), **Devil** (168) and **Trophy** (183), the game is usually *over* by round 150–200, and
     77–94 % end in elimination.
   - Portals, Slithery, Trauma and Schooltime run to round 500 and are decided by length.
   - The opening is the whole game on the first group. Q1's worst maps for us (PD, Autarky, Trophy) are all elimination maps.
2. **For gates and screens:**
   - A Portals result carries the least information about strength. Among top-50 pairs its slope (0.16 ± 0.05) is the
     smallest by far, so at equal games a Portals result is worth about (0.16/0.49)² ≈ 1/9 of a Schooltime result.
   - Weight maps by slope², or report Portals separately.
   - Our +354 Portals effect (Q1) should be read against that noise; its CI is still clear of 0.

**Ledger rows touched:** none directly. Suggested for the gate design (D-032): weight per-map contributions by Q2 slope²,
and split the gate into elimination maps (decided before r200) and length maps (decided at r500).

## Addendum (Q2b): noisy, or complicated?

Query: `python3 tools/s1/q2b.py` → `build/s1/out/q2b/maps.csv` (58k games at 10:24 UTC). Held-out test: fit on odd game
ids, predict even ones, and the reverse. Test games need both teams to have ≥ 8 training games on that map.

| map | Elo skill | other-maps BT skill | this-map BT skill | map-specific gain | Elo acc. | this-map acc. | same-pair repeat agreement | lead→win AUC r50 / r150 |
|---|---|---|---|---|---|---|---|---|
| Trophy | 0.069 | 0.060 | 0.139 | 0.079 | 0.64 | 0.68 | 0.69 | 0.90 / 0.99 |
| Queen Of Spades | 0.076 | 0.057 | 0.151 | 0.094 | 0.63 | 0.67 | **0.67** | 0.83 / 0.96 |
| Schooltime | 0.100 | 0.097 | 0.203 | 0.105 | 0.64 | 0.70 | 0.68 | 0.68 / 0.84 |
| Devil | 0.088 | 0.076 | 0.196 | 0.120 | 0.64 | 0.71 | 0.71 | 0.95 / 0.99 |
| Autarky | 0.075 | 0.076 | 0.210 | 0.134 | 0.65 | 0.72 | **0.77** | 0.80 / 0.90 |
| Prisoners Dilemma | 0.056 | 0.055 | 0.190 | 0.135 | 0.61 | 0.70 | 0.72 | 0.96 / 0.99 |
| Default | 0.056 | 0.061 | 0.197 | 0.135 | 0.63 | 0.70 | 0.68 | 0.80 / 0.94 |
| Trauma | 0.068 | 0.060 | 0.208 | 0.148 | 0.61 | 0.71 | 0.68 | 0.66 / 0.79 |
| Slithery Fight | 0.078 | 0.048 | 0.236 | 0.187 | 0.62 | 0.72 | 0.69 | 0.60 / 0.66 |
| **Portals** | **0.037** | **0.025** | **0.279** | **0.253** | **0.59** | **0.73** | 0.72 | 0.63 / 0.66 |

**Columns.**

- Skill = held-out Brier skill.
- BT = a per-map Bradley–Terry strength per team (ridge, seat term).
- "Other-maps BT" is the same model fitted on the other nine maps, with the same data freshness.
- Map-specific gain = this-map minus other-maps.
- Repeat agreement = the same pair on the same map within 3 h has the same winner.

**Reading.**

- Elo is weak everywhere: 59–65 % accuracy. A team's strength on the other maps is no better than Elo, so this is not
  rating lag.
- Knowing the team *on this map* lifts every map to 67–73 %. The "noise" in Q2's Elo slopes is mostly map-specific skill.
- **Portals and Slithery are specialist maps, not random ones.** They are the worst for Elo and the best with map-specific
  strength. Correction to the reading above: a Portals result says little about general strength, but a lot about
  strength on Portals.
- **Trophy and Queen of Spades are the noisy ones.** Map-specific strength reaches only 0.14–0.15 skill, and QoS has
  the lowest repeat agreement. Both are decided in the opening (the r50 lead already has AUC 0.83–0.90), so the
  randomness sits in early contact, not late play.
- **The ceiling is modest everywhere.** The same pair on the same map repeats its winner 67–77 % of the time.
  0.72 agreement corresponds to about an 83/17 matchup.

## Addendum 2 (Q2c): Elo is a good predictor; the low skill numbers above came from matchmaking and three teams

This corrects the headline reading of both tables above.

**1. Elo is calibrated.** Across all 57k decided games, here is the favourite's win rate by rating gap, against the Elo
formula:

| gap | 0–25 | 25–50 | 50–100 | 100–150 | 150–200 | 200–300 | 300–400 | 400–600 | 600+ |
|---|---|---|---|---|---|---|---|---|---|
| actual | 0.52 | 0.55 | 0.61 | 0.67 | 0.71 | 0.77 | 0.79 | 0.84 | 0.97 |
| Elo formula | 0.52 | 0.55 | 0.61 | 0.67 | 0.73 | 0.81 | 0.88 | 0.94 | 0.98 |

**2. Most games are close by design.**

- 56 % of games have a gap ≤ 100, and ranked games have a median gap of 31. Autoscrims pair teams within 8 places.
- If Elo were *exactly* right, it would call only 58.3 % of ranked games correctly. It calls 57.3 %.
- Unranked games without three teams: exactly-right Elo would call 70.5 %; it calls 70.4 %.
- Low Brier skill is a property of the matchups, not of the rating.

**3. The overconfidence at 200+ gaps is three teams whose unranked games are not their rated bot.** Actual vs
Elo-expected win share:

| team | games | actual | Elo-expected |
|---|---|---|---|
| SSS (#5), unranked | 1,538 | **0.36** | 0.64 |
| SSS (#5), ranked | 145 | 0.46 | 0.50 |
| Cutlery (306, #7), unranked | 2,794 | **0.60** | 0.81 |
| Cutlery (306, #7), ranked | 158 | 0.51 | 0.61 |
| STAR (#45), unranked | 2,011 | | residual −0.13 |

SSS loses 77–79 % of its unranked games against teams rated 200–500 below it. Cutlery wins only 54 % against teams
300–500 below.

- **Every other top-ten team matches Elo in ranked play** (actual / expected): cheji 0.754 / 0.767, forgot to mention
  0.641 / 0.637, calc 0.644 / 0.642, Cache me outside 0.570 / 0.547, 中国必须人能飞 0.530 / 0.540.
- **Rating lag is not the cause.** A rating 6 h later changes the favourite in 0.7 % of 300+ gap upsets, and Brier moves
  0.2157 → 0.2133.
- **Slope per 100 Elo** (formula 0.576): all games 0.419; ranked 0.507; all games without those three teams 0.449.

**4. Per map, without SSS / STAR / Cutlery (52k games).** The maps do differ, though less than the first table said.

| map | slope/100 Elo | Elo accuracy − its ideal |
|---|---|---|
| Portals | 0.42 | −3.5 pts |
| PD | 0.47 | −1.2 |
| Trauma | 0.49 | −1.0 |
| Slithery | 0.51 | −3.2 |
| Default | 0.51 | −0.6 |
| Trophy | 0.52 | +0.3 |
| QoS | 0.56 | +0.2 |
| Autarky | 0.59 | +2.3 |
| Devil | 0.64 | +1.4 |
| Schooltime | 0.64 | +1.0 |

- Heterogeneity is significant: χ² = 78, 9 df, p < 10⁻¹².
- Q2b holds on the clean sample. This-map strength beats other-maps strength on every map, most on Portals (+0.28 skill,
  74 % accuracy vs Elo's 60 %) and Slithery (+0.21), least on Trophy / QoS (+0.08 / +0.09).
- **Revised reading:** Trophy and QoS are not unusually noisy for Elo. They are the maps where map-specific skill adds
  least. Portals and Slithery are where team-specific map skill matters most.

**5. Map specialism at the top, concretely** (win share vs Elo-expected, per map):

| team | strongest vs Elo | weakest vs Elo |
|---|---|---|
| cheji bt (#1) | QoS 0.97 vs 0.77, Schooltime 0.90 vs 0.76 | Slithery 0.63 vs 0.78 |
| forgot to mention | Autarky 0.87, PD 0.86, Devil 0.87 vs ~0.68 | Portals 0.51 vs 0.68, Default 0.56 vs 0.70 |
| calc | Autarky 0.91 vs 0.72, Default 0.86 vs 0.72 | Slithery 0.61 vs 0.72 |

**Consequences.**

- Q1 and Q2b should be read on the clean sample; `maps_clean.csv` holds it.
- Exclude or flag SSS, STAR and 306 unranked games when their record is used to estimate strength (panels, clones,
  calibration).
