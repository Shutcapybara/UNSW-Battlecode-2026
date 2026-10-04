# P-A02 k16 full gate (D-053 §D): Sugawara's forecast and mechanism note

4 Oct 2026, 14:45Z. Filed before the gate card is posted. Inputs are frozen seed-1 files only:
`docs/learning/results/asahi/P-A02-kz12-k16-s1.json` and `P-A02-kz12-curve-s1.json`. I did no new run.

## Forecast

**P(the gate returns PASS on seeds 2–3 under D-046 §4, with map × opponent clusters) = 0.35.**

Expected effect:

- **Pool Δwin:** about +1.5 pp, almost all of it from Weakhold.
- **Gen:** about 0.
- **Wall deaths on classes C and E:** −3 to −5 per 1k.
- **Queen columns:** unchanged.

## Replication (cheap, from frozen per-map rows)

**The whole seed-1 pool gain is one map.** Seed 1 gives +7 net games out of 272 (+2.57 pp). Weakhold alone is
**+7**: 15-1 against the parent's 8-8. The other 16 maps net 0: Portals −1, Tower Defense −1, Slithery +1,
Stripes +1, and 12 maps identical.

- A map-cluster bootstrap on the same rows (17 clusters, 1,000 resamples, seed 7) gives the pool Δwin 5th–95th as
  **[−1.10, +7.72] pp**. The map × opponent × seat interval of [+0.74, +4.43] holds up only because Weakhold's +7 is
  spread over about 7 opponent clusters.
- Map × opponent clusters (D-052 §C) should stay close to the seat-split figure, so the cluster change is not what
  decides the gate. Whether Weakhold replicates is what decides it.

**Weakhold's response is not monotone in the dose.**

| dose | Weakhold vetoes per 1k queen decisions | Weakhold win swing |
|---|---|---|
| k4 | 147 | +2 |
| k8 | 151 | +2 |
| k16 | 98 (fewest) | +7 |

Fallbacks on Weakhold are 39 at k16. Two readings fit this:

- a threshold effect, where Weakhold's corridors need Cb ≥ 16 to be refused;
- a seed-1 draw.

**Winner's curse.** k16 was picked as the best of three doses on this same seed. Seeds 2–3 are a fair test; my
estimate of the effect is shrunk from +7 to about +5 per seed on Weakhold.

**Other gate clauses look safe on seed 1:**

- econ: pool lower bound −0.005, gen lower bound −0.002;
- units@100 and total@100: lower bounds 0 and −0.012;
- no tier-2 flag (wall −15 %, all others within ±1.3 %);
- 0 invalid commands; 0 missing.

## How the 0.35 is built

- P(Weakhold's effect is mostly real) is 0.65. Given that, the pool needs about 9 net games out of 544 to clear lower
  bound > 0 with about 26 discordant pairs. That comes to about 0.60.
- If the effect is mostly noise, P is about 0.05.
- Mixed: 0.41. Multiplied by about 0.85 for the other clauses and deploy limits passing jointly, that gives **0.35**.

## Mechanism checks

- **Legal observation:** passes. Cb is computed from own body and visible cells. The original-queen flag is in
  per-process memory from r0. There is no map identity: the dial fires on 16 of 17 maps.
- **No train/deploy skew:** this is a hand rule.
- **Leakage:** the gate seeds (2–3) are disjoint from the seed that picked the dose. The held-out splits are not
  touched.
- **RL translation:** complete in the card. Cb is an R4 feature-block candidate.
- **Simpler known method:** a flood-fill "space after move" heuristic, the standard Tron/Snake survival term. This is
  that heuristic.

## Recommendations (report-only, no relabelling of the gate letter)

1. Print Weakhold per seed, and the pool net with Weakhold excluded, beside the gate letter. This is the D-046 §4.6
   stratified readout with the target stratum named now: **Weakhold**.
2. Print Weakhold fallbacks and vetoes per 1k at k16 for seeds 2–3, so that a threshold effect can be told apart from
   noise.

## Dissent and precedent

- If the gate passes on one map, the promotion is a Weakhold patch, and the live value depends on Weakhold's share of
  the live rotation. That is cheap and fine as a `temporary` dial, but it should not be read as a general improvement
  in queen survival. The queen endpoint failed at every dose.
- Precedent: Tron/Snake space-counting heuristics (Google AI Challenge 2010 Tron; Battlesnake flood fill) give large
  wins on corridor maps and roughly zero elsewhere. This is the same shape.
