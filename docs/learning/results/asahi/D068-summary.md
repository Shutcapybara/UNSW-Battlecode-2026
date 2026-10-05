# D-068 §C play diagnostics: summary (Asahi, 2026-10-05 04:29Z)

Population: seed-1 pool, ZOO (8) × 17 live maps × both seats = 272 paired fixtures, 0 missing, `unswbc 1.2.3`, Mac
native. Intervals: cluster bootstrap over map × opponent (136 clusters), 1,000 resamples, seed 7, linear 5th–95th.
Preregistration: `D068-prereg.md` (02:14Z). Paired differences between arms by `tools/asahi/pairdiff.py` (reproduces
card.py's Δwin to two decimals: kageyama-02 vs carthage-05 −13.60 [−19.49, −8.09] both ways).

| arm | bot (fp) | W–L–D | Δwin vs carthage-05 (pp) | card |
|---|---|---|---|---|
| parent | carthage-05-free-sprint (7df05a3f) | 226–46–0 | — | — |
| 0 parity | asahi-11-p1hb1-off | — | 272/272 identical | P1HB1-off-parity-pool-s1.json |
| 1 fallback | kageyama-01b/02b fb builds, sandbox | — | 0 lines / 728,046 dragon-turns | D068-fallback-count.json |
| 2 | kageyama-02-p1-hb1, A1-400, λ 1 (60e8ed78) | 189–83–0 | **−13.60 [−19.49, −8.09]** | D068-k02-l1-pool-s1.md |
| 3 | asahi-12-c05-lambda0, no prior (8ea84996) | 190–81–1 | −13.05 [−18.38, −7.35] | D068-c05-l0-pool-s1.md |
| 4 | asahi-13-p1hb1-l141, A1-400, λ 1.41 (3c7902d6) | 210–62–0 | −5.88 [−11.03, −0.74] | D068-k02-l141-pool-s1.md |
| ref | kageyama-01-p1-slot, A3-400, λ 1 (234a2fff) | 207–65–0 | −6.99 [−12.87, −1.47] | P1SLOT-l1-s1.md |

Paired between arms (post hoc comparisons, not preregistered as tests; reported as read):

- arm 2 − arm 3 (A1 at λ 1 vs no prior): **−0.55 [−5.88, +4.60]**. At λ 1 the A1 placeholder is worth nothing in play.
- arm 4 − arm 2 (λ 1.41 vs λ 1, same model): **+7.72 [+2.94, +12.52]** — recovers 57 % of arm 2's loss.
  Shenzhen's H-SZ74 (≥ half recovered; falsifier within 2 points): **holds**.
- A3 slot − arm 2 (encoder A3-400 vs HB-1 A1-400, both λ 1): **+6.62 [+1.47, +12.13]**. The more accurate model
  (A1 +0.0039 over A3 on dev120) is the worse prior in play; A1's floor share is 1.8 % against A3's 8.9 % (Hinata
  02:30Z).

Forecasts (Asahi, 02:14Z): arm 2 −4 pp (observed −13.6: miss); arm 3 P(≤ −7) 0.55 (occurred); arm 4 P(within −2)
0.35 (did not occur).

Reading: every result so far orders the priors by sharpness, not by accuracy (no prior ≈ A1 λ 1 < A3 λ 1 ≈ A1 λ 1.41
< live prior, floor share 1.8 % / 8.9 % / — / 39 %). Consistent with Sugawara's softness hypothesis (D-068 §B); the
Chair's style-mixing hypothesis is tested by the single-team priors (D-068 §C.5, Hinata's jobs 015/016).

RL translation. Observation: none new. Action: the direction prior's distribution, not its argmax, enters the
search. Value/reward: none. Demonstration: n/a (local panels). Requirement for any learned prior in the slot:
report entropy and floor share, and match them to the live prior (temperature or λ) before a panel.
