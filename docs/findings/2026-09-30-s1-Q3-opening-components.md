---
id: S1-Q3-opening-components
author: s1
kind: observation
question: The opening, component by component — where does the top ten's lead over us come from, and when?
evidence: s1 corpus store, 40,593 games (81,186 side-games); top-10 19,494 side-games, r11–30 24,403, r31–50 12,361, us 1,019 (us_now = since 29 Sep 06:00 UTC, 332)
queries: python3 tools/s1/q3.py curves | figs | gap | gapm | sides   → build/s1/out/q3/{gap.csv, gap_matched_1750_1900.csv, sides_*.csv, lead_transitions.csv, seat_r100.csv}
figures: docs/findings/s1-figs/q3/<stat>.png (one per stat: 11 raw map panels, pooled ÷ median, pooled z, top-10 teams individually, pooled 0–500) and delta-<stat>.png (change per 5 rounds)
---

## Answer

- **The gap opens in the first 25 rounds and it is economy, not deaths.**
- **Against the same opposition** (opponents rated 1750–1900 at game time), the top ten are +0.11 field SD in total length
  at r25 and we are −0.49. By r50 the gap is 0.80 SD, and from r100 it is ~1.0 SD, where it stays.
- **It is built from four components:**
  - **bed conversion:** bed pearls and bed capture. We reach beds as early as they do but eat fewer of them.
  - **production:** fewer splits by r50.
  - **early portal use:** they transit in the first 25–50 rounds; we mostly do not.
  - **territory.**
- **Death rates are the smaller part of the opening gap.**
  - At r25–r50, deaths per dragon-turn differ by 0.12–0.14 SD and own goals by 0.26–0.28 SD. Economy differs by 0.4–0.8 SD.
  - Our raw death counts per map by r50 are the same or lower.
  - The death gap grows later (0.3–0.4 SD by r150; Q4).
- **Two other differences are ours alone:**
  - **We time out.** 17 % of our games between 28 Sep 02:00 and 29 Sep 06:00 UTC had turns over the time limit (mean
    2.8, max 58 per game; field ≈ 0). There were none after that.
  - **We send the maximum sonar every turn** (4.0 rays per dragon-turn vs the top ten's 2.5).

## Method

- **Unit:** side-game. Rows are **cohorts by the side's own current rank**: top10, r11_30, r31_50 and us (team 7).
  `us_now` is team 7 since 29 Sep 06:00 UTC, the current submission era: no TLE turns after it.
- **Scales:**
  - **raw:** the median per map. Use it for interpretation.
  - **÷ median:** divided by the field median on the same map and round.
  - **z:** (x − field mean) / field SD on the same map and round, averaged. This is the ranking scale; it handles low
    counts where the median is 0.
- **Field:** a hash sample of up to 1,500 games per map from the whole store.
- **Opponent strength.** Material stats are partly *who you played* (BENCHMARKS.md), so the headline table holds the
  opposition fixed: opponents rated 1750–1900. That gives 3,952 top-10 and 550 us side-games per checkpoint (97 us_now).
  The unmatched table (`gap.csv`) has the same ranking with slightly smaller gaps. The top ten's median opponent is
  *stronger* (1925) than ours (1813), so matching does not flatter them.

## Component table: top-10 minus us, field z-units, matched opponents

Positive = the top ten are higher. Columns are checkpoints.

| component | stat | r25 | r50 | r100 | r150 | us_now r50 |
|---|---|---|---|---|---|---|
| **material** | total length | **0.60** | **0.80** | **0.98** | **0.99** | 0.64 |
| | units (dragons alive) | 0.42 | 0.65 | 0.89 | 0.89 | 0.46 |
| | longest | 0.30 | 0.47 | 0.56 | 0.63 | 0.49 |
| **pearls** | bed pearls eaten (cum.) | 0.37 | 0.56 | 0.68 | 0.68 | 0.43 |
| | bed capture (bed eats ÷ bed spawns) | 0.38 | 0.52 | 0.63 | 0.64 | 0.34 |
| | pearls per dragon-turn | 0.25 | 0.35 | 0.28 | 0.17 | 0.41 |
| **production** | splits (cum.) | 0.25 | 0.49 | 0.63 | 0.61 | 0.40 |
| **space** | territory (BFS) | 0.41 | 0.61 | 0.78 | 0.80 | 0.41 |
| | bed territory | 0.44 | 0.51 | 0.70 | 0.71 | 0.35 |
| | map seen | 0.29 | 0.32 | 0.27 | 0.26 | 0.20 |
| | beds seen | 0.34 | 0.33 | 0.29 | 0.29 | 0.13 |
| **portals** | transits (cum.) | 0.50 | 0.47 | 0.51 | 0.52 | **0.78** |
| | per-transit death within 3 rounds | −0.07 | −0.23 | −0.35 | −0.38 | 0.04 |
| **movement** | distance from birth per turn | 0.30 | 0.14 | 0.14 | −0.03 | 0.21 |
| **swarm shape** | clustered (ally head within 3) | 0.34 | 0.43 | 0.67 | 0.55 | 0.27 |
| | nearest-ally distance | −0.18 | −0.33 | −0.52 | −0.43 | −0.22 |
| **contact** | share of dragons in contact with an enemy | — | −0.46 | −0.58 | **−0.71** | −0.20 |
| | nearest enemy head distance | 0.11 | 0.52 | 0.56 | 0.60 | 0.29 |
| **deaths** | deaths per 1k dragon-turns | −0.14 | −0.12 | −0.24 | −0.30 | 0.04 |
| | own goals per 1k | −0.26 | −0.28 | −0.33 | −0.38 | −0.11 |
| | deliberate suicides (cum.) | 0.53 | 0.69 | 0.79 | 0.78 | 0.70 |
| **compute** | turns over the time limit (idle share) | −0.60 | −0.74 | −0.94 | −0.89 | **0.00** |
| **sonar** | rays per dragon-turn | −0.66 | −0.65 | −0.66 | −0.67 | −0.81 |

All values: `gap_matched_1750_1900.csv` (every stat × checkpoint, with each cohort's z).

## Per map (raw medians, all opponents): where the pearls go missing

Pearls eaten by r50, top10 / us:

| map | top10 | us |
|---|---|---|
| Trauma | 15 | 2 |
| PD | 38 | 19 |
| PD 10 | 34 | 15 |
| Devil | 42 | 29 |
| Trophy | 33 | 22 |
| QoS | 18 | 11 |
| Default | 18 | 13 |
| Autarky | 48 | 42 |
| Portals | 47 | 35 |
| Schooltime | 13 | **14** |
| Slithery | 195 | **224** |

Deaths by r50 are the same or lower for us on every map (for example PD 16 / 12, Devil 9 / 9, Trophy 3 / 3). Total length
by r100, top10 / us:

- Devil 55 / 11, Trophy 60 / 18, PD 20 / 4, PD 10 23 / 0, Trauma 38 / 16, Autarky 53 / 25.
- Schooltime 50 / 56 is the one map where we are ahead.

Q1's worst maps (PD, Autarky, Trophy) and best maps (Slithery, Schooltime, Portals) line up with this. On PD, our deaths in
rounds 0–40 are 43–68 % enemy-inflicted (top ten 34–51 %), and the top ten's early deaths are a third deliberate (wall,
suicide, invalid).

## Single-number opening features (medians, all opponents; ÷ per-map field median in brackets)

| feature | top10 | r11–30 | r31–50 | us |
|---|---|---|---|---|
| pearls@50 | 31 (1.07) | 30 | 27 | 21 (0.83) |
| pearls@100 | 87 (1.09) | 83 | 71 | 52 (0.78) |
| splits rounds 0–50 | 14 | 13 | 12 | 10 (0.84) |
| births rounds 0–150 | 60 (1.10) | 57 | 50 | 37 (0.76) |
| newborn survival to 10 rounds (0–150) | 0.757 | 0.703 | 0.712 | 0.700 |
| newborns that ever eat (0–150) | 0.783 | 0.771 | 0.773 | 0.745 |
| child length (all ≤ 2 for us; top ten 3 % length-3) | 2.09 | 2.03 | 2.04 | 2.00 |
| beds reached by r50 | 0.469 | 0.443 | 0.452 | **0.487** |
| first bed arrival, median round | 41 | 42 | 40 | **37** |
| beds reached first (share) | 0.517 | 0.494 | 0.493 | 0.494 |
| round the map is half seen | 18 | 19 | 18 | **16** |
| transits by r50 | 5 (1.5) | 4 | 2 | 2 (0.5) |
| transit survival 3 rounds (0–150) | 0.895 | 0.875 | 0.848 | 0.825 |
| first fight (enemy-credited death) | 29 | 32 | 33 | 32 |
| round the material gap first exceeds 10 % | 11 | 11 | 12 | 11 |

**We explore and reach beds as fast as anyone but convert less.** Our first-bed arrival and half-map-seen rounds are
*earlier* than the top ten's. Bed capture, bed pearls and production are lower from r25.

## Lead dynamics (total length)

| | top10 | r11–30 | r31–50 | us |
|---|---|---|---|---|
| ahead at r50 (mean of ±1) | +0.17 | +0.07 | −0.04 | **−0.35** |
| win if ahead at r50 | 0.84 | 0.74 | 0.62 | 0.60 |
| win if behind at r50 | 0.40 | 0.34 | 0.26 | 0.27 |
| collapse (ahead r50 → behind r150) | **0.13** | 0.19 | 0.27 | **0.34** |
| comeback (behind r50 → ahead r150) | **0.30** | 0.23 | 0.18 | **0.12** |
| win if first to lead by 10 % | 0.74 | 0.64 | 0.52 | 0.47 |

- A 10 % material gap opens by round 11 in the median game.
- When the top ten are ahead at r50 they convert 84 %; when we are, we convert 60 % and lose the lead by r150 a third of
  the time.

## Rate of change

The `delta-*.png` figures show the mean change per 5 rounds.

- The top ten's `units` and `total` keep rising through r150 on the elimination maps.
- Ours flatten or turn negative from r20–40 on Autarky, Devil, PD, PD 10 and Trophy.
- Seen share and beds reached level out at the same round for us and the top ten (≈ r40–60).
- So we stop *growing* early on those maps, not stop exploring.

## Seat asymmetry (field, r100)

- Side B wins 57–64 % on every map. Some of that is rating (side A is usually the lower-rated challenger), but Q2's
  intercepts at equal Elo still favour B on 8 of 10 maps.
- B has more pearls at r100 everywhere except Slithery: Devil 124 vs 71, Trophy 97 vs 77, Autarky 108 vs 95.
- Details are in `seat_r100.csv`.

## Local (renoir-00-base = Ares V06 base, pool runs, dashed lines on the figures)

- It sits at the field median or above on early material (total ÷ median 1.0–1.2) and territory.
- It carries our sonar profile: 4 rays per dragon-turn.
- Its local opponents are not the field, so treat its material as panel-relative. Its per-transit and own-goal numbers are
  in Q4.

## Caveats

- "us" pools every team-7 submission since 26 Sep. `us_now` (332 side-games, 97 matched) is the better read of the
  current bot, and it is noisier.
- The matched band is one choice (1750–1900). `q3.py gapm LO HI` re-runs it for any band.
- Material is partly opponent-driven even within a band.
- The earliest checkpoints (r25) sit on few events per side-game, so the z-scale is used for them.

## Ledger rows touched and suggested weights

- **L11 (bed guarding keyed on information state), 0.35 → 0.45.** We reach beds first as often as the top ten, but bed
  capture is 0.4–0.6 SD lower from r25. Holding and converting beds, not finding them, is the gap.
- **L17 (production pace can be forced), 0.1, stays dormant.** Its revival trigger is a pearl *surplus* at r50. We have a
  pearl *deficit*, and production follows pearls (splits gap 0.25 → 0.49 trails the bed-pearl gap 0.37 → 0.56).
- **L10 (refuse contact far from beds), 0.4 → 0.5.**
  - We are in contact more (−0.46 to −0.71 SD) and closer to enemy heads (0.52–0.60 SD) with fewer units.
  - The top ten keep more distance while holding more territory.
  - On PD, our early deaths are mostly enemy kills.
- **L14 (scout splits / exploration), 0.3 → 0.25.** Our exploration is already as fast as the top ten's (beds reached
  and half-map-seen are earlier). More exploration is not the lever.
- **L18 (swarm dissolve), 0.15, unchanged but informed.** The top ten are *more* clustered (0.34–0.67 SD), not less.
- **New row (proposed): early portal use in the first 50 rounds is a top-ten trait, 0.5.**
  - Transits by r50: 5 vs 2 (z +0.21 vs −0.29 at r25).
  - `us_now` is lower still (−0.67).
  - Test only with Q4's exit-traffic fix in place.
- **New row (proposed): deliberate suicide / invalid-action deaths as a recycling tool, 0.4.**
  - The top ten use them from r25 (+0.53 to +0.79 SD). We never do (suicide 0.0 per 1k).
  - Their own-goal share is lower because some deaths are chosen, not suffered.
  - Relates to L29 (churn).
- **Closed issue (for the record):** the TLE turns of 28 Sep 02:00 – 29 Sep 06:00 UTC. Current games show none.
