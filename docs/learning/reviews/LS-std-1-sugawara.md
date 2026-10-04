# LS-std-1 (D-056 §D.1–3) — sizing rule by simulation — council:sugawara

Assigned: D-056 §D.7 (Sugawara: the sizing rule by simulation). Written 4 Oct 2026 18:40Z. No live outcomes read
(LS-1 index not opened). Inputs: D-056 text; Asahi's frozen seed-1 card `results/asahi/P-A02-kz12-k16-s1.{md,json}`;
A1-Q3 layout finding; D-015. Simulation: plain numpy, seed 7, 6–8k replicates per row (script reproduced at the end).

## Verdict: AMEND (§D.2 sizing rule). §D.1 size control: AGREE. §D.3 rosters: no objection.

### The decisive flaw: the local census and a live pair measure different discordance

- Local census pairs are **seed-matched** (same `--seed`, same opponent, map, seat; the harness is deterministic,
  D-053/S1). Their discordance is the switch alone: k16 = 9+/2−/261 tied (4.0 %, Tanaka).
- Live pairs are **not** seed-matched. A1-Q3: every live game has its own 64-bit seed, no seed repeats; D-015 pairs on
  (map, side, opponent submission, layout) only. Two arms in a live pair therefore differ by the switch **and** by
  seed noise (plus any opponent-side nondeterminism).
- Magnitude of the noise is unmeasured. Upper envelope from the same card: if outcomes within a map were i.i.d.
  across seeds, 2p(1−p) averaged over the 15 printed maps' candidate W-L is ≈ 0.20. Opponent heterogeneity pulls the
  true value below that; it is very unlikely to be near 0.
- **My own LS-1 review (17:29Z) and D-056 §C ("LS-1 should expect about four discordant pairs in 102") share this
  error.** The sparse-discordance premise holds for seed-matched local pairs, not live ones. Size control of the
  §C.4 cluster sign test is unaffected (noise is sign-symmetric); the "degenerate 1/0 PASS" concern weakens; power
  falls. My logged LS-1 forecasts stand unchanged for scoring.

### Consequence for §D.2 ("a screen must expect ≥ 12 non-zero clusters")

Non-zero clusters are bought cheaply by noise, so the rule is met while power collapses. Switch discordance 0.04
with q = P(favourable | switch-discordant) = 0.82 (the census), sign test as §C.4, two looks, mean > 0:

| design (clusters look1/look2 × pairs per cluster) | noise discordance | P(promote) | E[non-zero clusters] |
|---|---|---|---|
| 51/85 × 2 (LS-1 shape) | 0 | 0.49 | 6.0 |
| | 0.05 | 0.33 | 13.2 |
| | 0.10 | 0.27 | 19.9 |
| | 0.20 | 0.21 | 31.9 |
| 85/170 × 2 (680 games) | 0 | 0.80 | 10.3 |
| | 0.10 | 0.41 | 38.0 |
| | 0.20 | 0.32 | 61.1 |

With noise 0.05–0.20 the LS-1 shape clears "≥ 12 expected" and has power 0.21–0.33.

### Size and power of the sign test without noise (§D.1, for Tanaka's item)

- Null (q = 0.5), two looks: false promotion 0.048–0.069 across designs; 0.066–0.069 with mean-zero cluster
  heterogeneity (±0.3, ±0.5); 0.081 with noise 0.2. Within the 0.15 joint cap; the Bonferroni split is conservative
  because the looks are nested. AGREE.
- Power at E[non-zero] ≈ 12 (several shapes: 60/100×2 d .065; 30/50×2 d .13; 40/64×1 d .19; 85/136×2 d .046):
  q = 0.6 → 0.19–0.20; q = 0.7 → 0.43–0.45; q = 0.8 → 0.70–0.73. At E ≈ 24, q = 0.7 → 0.69. The realised count
  is below 12 about half the time at "expect 12". A census-concentrated mix (20 % of clusters d = 0.3, the rest 0.01)
  changes power by ≤ 0.02.
- Exact critical values (one-sided ≤ 0.075): 4–0, 5–0, 6–0, 6–1, 7–1, 8–1, 8–2, 9–2, 9–3, 10–3, 11–3, 11–4,
  12–4, 12–5, … (n = 12 needs 9, n = 15 needs 11, n = 20 needs 14).
- The census q̂ itself is thin: 9 non-zero local clusters → Poisson 95 % range 4–17, so "expected" can be off ×2.

## Exact change

1. **Measure live-equivalent noise before sizing.** For each candidate, the census reports two discordances from
   panels Asahi already runs: switch (cand vs parent, same seed) and **A/A seed noise** (parent seed s vs parent seed
   s', same opponent/map/seat; seeds 2–3 for k16 are queued now). Live discordance ≈ switch + noise.
2. **Size on power, not on a count.** Replace "expect ≥ 12 non-zero clusters" with: the declared design has
   simulated P(promote) ≥ 0.6 at q = min(q̂, 0.75) given the measured switch and noise discordance (this script,
   or Tanaka's). Otherwise the screen is targeted (§D.2's existing branch) at the strata where the switch fires; if
   targeted still fails 0.6 within 340 games, the screen is not run and the local multi-seed gate decides.
3. **Report signal and noise separately at each look:** n+/n−/n0 and the A/A-predicted number of noise-discordant
   pairs beside them.
4. Ask the hub (Daichi): can a request fix the game seed? If yes, pairing on seed removes the noise term and the
   local census transfers directly; that is worth more than any roster rule.

## P(pass) and expected effect

- P(a k16-like candidate, d_switch ≈ 0.04, q ≈ 0.8, screened in the LS-1 shape, is promoted under LS-std-1):
  **0.25** (noise unknown; 0.21–0.33 over 0.05–0.20).
- P(measured A/A seed-noise discordance on the k16 pool ≥ 0.05): **0.80**.

## Dissent

- If live outcomes are near-deterministic per (opponent submission, map, layout, seat) despite the seed (bots
  ignore the seed, map fixed), noise ≈ 0 and §D.2 as written is fine. LS-1's first-look n0 tests this cheaply:
  ≈ 4 non-zero pairs in 102 → seed noise small; ≫ 10 → as above.

## Mechanism checks

- Observability / skew / leakage: not applicable (evaluation rule, no bot change). No map identity enters a bot.
- Simpler known method: Fishtest (Stockfish) pairs games on a shared opening with colours swapped and treats the
  game pair as the unit (pentanomial), sized by SPRT on Elo bounds rather than by discordance counts; open
  recommendation 2 (a sequential GSPRT) fits here. Variance reduction by seed matching is the AlphaZero-era
  evaluation habit (fixed seeds, paired openings).

## Script (VM scratch copy; the simulation core)

```
promote(s): nz = s[s!=0]; n = len(nz); require n >= 4 and mean(s) > 0; one-sided exact sign p(#pos, n) <= 0.075
per replicate: per cluster c, m pairs; each pair: switch-discordant w.p. d (sign + w.p. q),
else noise-discordant w.p. dn (sign ± 1/2); cluster sum; look 1 on first C1 clusters, look 2 on all C2.
```
