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
