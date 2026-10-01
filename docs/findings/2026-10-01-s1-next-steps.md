---
id: S1-next-steps-1oct
author: s1 (Claude, Ouroboros lane)
kind: findings
title: Authenticity tags, the authenticated atlas, the split-stall diagnosis, hb1-04 vs hb1-12, and a crown graft
code: tools/s1/authenticity.py, tools/s1/splitstall.py, tools/s1/atlas_analysis.py --auth, tools/s1/tempo_gate.py; bots/ouroboros-g0{1,2,3}-hbmimic-ares-r{150,250,350}
data: s1 corpus (40,593 live games), atlas panel (20,243 games), graft run (cloud, seed 1, same panel)
---

## TL;DR

1. **Authenticity tags are built.** `build/s1/corpus/authenticity.parquet` covers 81,186 side-games.
   - SSS's sonar-silent decoy: 76 % of those games are flagged, against 5 % of its sonar-active games.
   - Cutlery: 46 % of its unranked games are flagged. Those games under-perform Elo by −0.38; the rest by −0.08.
   - Controls: 0.4 % flagged.
   - 80.6 % of side-games count as authentic (ranked, or unranked and fingerprint-consistent).
2. **The authenticated atlas corrects one claim.** Our best local family (hb1-12, fenrir-v19, sciel…) is not unoccupied
   live. It plays like **ranks 11–30**: Sabotage-d, Team SKKU and Peanut Butter (~1960–2040 Elo), plus Heartbreaker.
   The top ten sit in other niches:
   - calc, Stockfish, SSS 09-28, ddabap;
   - 中国必须人能飞, 3.14159265, Cache me outside;
   - cheji bt, forgot to mention;
   - Cutlery.

   Strength-behaviour links are unchanged or slightly stronger.
3. **Split stall: we do not decline splits. We split too eagerly and eat less.**
   - We split 75 % of eligible dragon-turns (95 % when the head has two free exits); the top ten split 52 % (46 %).
   - When the top ten decline, the dragon eats 0.53 pearls in the next 5 rounds; ours eat 0.27.
   - The top ten eat **20 % more pearls per dragon-turn** in r20–39 (0.107 vs 0.089), and their children die less
     (37 % vs 44 % within 10 rounds).
   - This is foraging and split timing, not reluctance.
4. **hb1-04 vs hb1-12: faster opening, loses the round-500 tiebreak.**
   - Tempo is −4.8 rounds, CI [−7.3, −2.2], but Devil and Schooltime are significantly slower, so the gate's verdict is
     MAP GUARD, not ACCEPT.
   - Win share is 0.64 vs 0.84.
   - On Portals, Slithery, Default and Schooltime it ends with **196 total length but a longest dragon of 12, against
     the opponent's 24**. It loses on the longest-dragon tiebreak while out-massing the opponent: no crown.
5. **The crown graft works, and r150 is the best hand-over point tested.** `ouroboros-g01-hbmimic-ares-r150` runs the hb1-04 mimic until round 150, then Ares V06.
   - Panel win share rises from 0.64 to **0.84**: 26 fixtures better and 2 worse, sign test p < 0.0001.
   - It ties hb1-12 (11 better, 11 worse) while keeping the fastest opening of any local bot.
   - Switching later is worse (r250 0.79, r350 0.78), and so is switching earlier (r100 0.81; tempo gate REJECT,
     +0.85 rounds).
   - Games are deterministic across machines (43/43 identical), so cloud and Mac fixtures pair exactly.

## 1. Authenticity tags (fingerprinting step 1)

The method follows `2026-10-01-s1-F-fingerprinting.md`:

- **Anchor.** The team's ranked games that UTC day, widened to ±1–2 days when the day has fewer than 12.
- **Features.** Seven features pass the screen (outcome-invariance KS < 0.15, and between-team spread above within-team
  spread):
  - refracted-ray share;
  - suicide and invalid-action deaths per 1k dragon-turns;
  - child length 4–5 share;
  - first split round;
  - has-sonar;
  - transits by r50.

  Rejected:
  - per-direction ray shares and ray targeting (outcome KS 0.18–0.44);
  - sonar rate, sprint share, splits by r50 and first pearl.
- **Score.** Per game there are two numbers:
  - **Robust distance** to the anchor median (MAD floored at a quarter of the between-team SD).
  - **Neighbourhood enrichment:** the share of ranked games among a game's k nearest team-window games, divided by the
    base rate.

  The first version used the distance alone and failed on SSS. SSS's real bot also has sonar-silent *ranked* games:
  short games where it was eliminated early, with 16 splits by r50 and a first split at round 0. Those games widened the
  distance calibration. The decoy differs in a way enrichment catches: it splits for the first time at round 62, and
  ranked games never sit near it.
- **Decoy flag.** A game is flagged when its enrichment is below 0.25 and, in that team-day, those low-enrichment
  unranked games under-perform Elo by at least 0.15 (n ≥ 15).
  - The per-game score never sees the result.
  - The residual only gates the team-day.
  - A game is **authentic** if it is ranked, or if its enrichment is ≥ 0.5 and it is not flagged.

**Results.**

| team | unranked flagged | Elo residual, flagged | Elo residual, authentic unranked | reading |
|---|---|---|---|---|
| SSS (91) | 45 % | **−0.66** | +0.06 | decoy bot (no splits until r62, no sonar) |
| Cutlery (306) | 46 % | **−0.38** | −0.08 | decoy or older bot (low invalid-action recycling) |
| 75 | 26 % | −0.38 | −0.01 | probable decoy (n 185) |
| STAR (467) | 15 % | −0.21 | −0.12 | variant, 29–30 Sep |
| SKKU (249) | 23 % | −0.16 | −0.03 | **unranked variant** on 09-29 (invalid recycling, sonar, transits 7 vs 2–3) |
| 507 | 11 % | −0.15 | −0.06 | **unranked variant** on 09-29 (suicide 0.38 per 1k vs 0.09; first split 5 vs 0) |
| controls (|residual| < 0.05, n ≥ 100) | 5.5 % low enrichment, 0.4 % flagged | | | |

**Two kinds of flag:**

- **Decoys** (SSS, Cutlery, 75) lose far more than the rating implies.
- **Unranked variants** (SKKU, 507, STAR) are teams testing other versions in unranked play. They under-perform modestly.

Both are excluded from "what the rated bot does". The table keeps them apart so nobody reads a variant as deception.
The authentic flag removes about 19 % of side-games overall; most of the removed games are not flagged but have no
anchor or sit between clusters.

**Use it.**

- The store has `authenticity.parquet`, with `authentic`, `decoy`, `enrich` and `p_real` per (game, side).
- `atlas_analysis.py --auth` uses it.
- The next tempo reference should be built from authentic games, which lets SSS and Cutlery back in.

## 2. The atlas on authenticated live games

- 150 live team-versions; k = 13 by silhouette.
- Outputs: `build/atlas/out/auth/`, figure `docs/findings/s1-figs/atlas/atlas-pca_auth.png`.

| niche | local bots (best) | live (top 10) | live examples |
|---|---|---|---|
| 5 | 58 (hb1-12 1774, fenrir-v19 1735, hb1-13) | 12 (1) | Sabotage-d 2037, Team SKKU 2022, Peanut Butter 1958, Heartbreaker, ddabap 09-28 |
| 9 | 2 (hb1-04, hb1-01) | 55 (11) | calc 2061, Stockfish 2044, SSS 09-28 2037 |
| 12 | 0 | 36 (9) | 中国必须人能飞 2072, Cache me outside 2046 |
| 1 | 1 (hb1-03) | 16 (6) | cheji bt 2116, forgot to mention 2064 |
| 11 | 0 | 8 (2) | Cutlery 2154, Sponge |
| 10 | 36 (yuna-x33 1716) | 5 (0) | PPP 1962, C-- 1930 |
| 4, 6, 7 | fermi, tew, r3/skadi/spike | 10 | Computers, Just Keep Swimming, ComTamSuonNuong |

**Team 7 by day:**

| day | niche | nearest local bots |
|---|---|---|
| 09-27 | 4 | sinbad, ein-dog |
| 09-28 | 6 | |
| 09-29 | 6 | hb1-11, tew, ouroboros-v11 |
| 09-30 | 7 | fenrir-v20, gavroche-v66 |

**Strength in both worlds** (local vs panel strength / live vs Elo):

- top-1 length share −0.79 / −0.50;
- enemy-head distance +0.79 / +0.49;
- contact −0.82 / −0.49.

These are slightly stronger than on the unfiltered live set.

**Reading.** Our best local family plays like the ~2000-Elo second tier. The top ten are in niches no local bot
occupies except hb1-04 and hb1-01, the Heartbreaker mimics. Moving from niche 5 to niche 9 or 12 means:

- more births and transits by r50;
- tighter clustering (niche 12);
- deliberate recycling (niches 1 and 11).

## 3. Split stall: policy, foraging or churn?

**Method.**

- `tools/s1/splitstall.py`: every dragon-turn in rounds 20–100.
- **Us:** team 7 since 29 Sep 06:00.
- **Top ten:** ranked games only.
- 15 side-games per cohort and map; 162–165 side-games per cohort.
- Eligible = length ≥ 4. Free exits = neighbours that are neither kelp nor occupied.

| | top 10 r20–39 | r40–59 | r60–100 | us r20–39 | r40–59 | r60–100 |
|---|---|---|---|---|---|---|
| dragons per round | 9.9 | 13.7 | 18.3 | 8.9 | 11.1 | 14.3 |
| pearls eaten per dragon-turn | **0.107** | 0.096 | 0.082 | **0.089** | 0.093 | 0.090 |
| share of dragon-turns eligible (L ≥ 4) | 0.082 | 0.080 | 0.078 | 0.051 | 0.052 | 0.051 |
| share at length 2 | 0.64 | 0.63 | 0.63 | 0.71 | 0.68 | 0.66 |
| split rate when eligible | 0.57 | 0.52 | 0.44 | **0.76** | 0.75 | 0.73 |
| … with two or more free exits | 0.54 | 0.46 | 0.36 | **0.95** | 0.95 | 0.83 |

| eligible dragon-turns, r20–59 | top 10 | us |
|---|---|---|
| split rate right after eating | 0.65 | 0.82 |
| split rate otherwise | 0.31 | 0.39 |
| pearls in the next 5 rounds when the split is declined | **0.53** | **0.27** |
| children's pearls per turn, ages 0–10 | 0.132 | 0.141 |
| children dead within 10 rounds | **0.37** | **0.44** |

**Verdict: foraging and timing, not policy reluctance.**

- **Timing.** We split almost every time a dragon reaches 4 with room. The top ten hold length 4+ while food is near:
  their declined dragons eat twice as much in the next 5 rounds. They split when the run ends.
- **Foraging.** Their dragons eat 20 % more per turn in r20–39. The gap is worst on Trauma (0.073 vs 0.021) and
  Prisoners Dilemma (0.106 vs 0.060).
- **Churn.** Children eat at the same rate once born, but ours die more often within 10 rounds.

**Evaluation-term implication.** Value a split by the parent's expected intake over the next ~5 rounds (pearls within
reach) against the child's safe intake. Do not split by threshold. Keep an eligible dragon on a pearl run.

## 4. hb1-04 vs hb1-12 (tempo gate on the panel)

**Fixtures.** 120 paired panel fixtures (seed 1; 10 maps × 6 opponents × 2 seats).

```
tempo delta -4.79 rounds, 95% CI [-7.34, -2.21]
Autarky -9.3, PD -52.9, Trauma -15.7, QoS -7.2, Trophy -3.4 | Devil +13.3 [+6.1, +20.7], Schooltime +26.3 [+14.7, +39.4]
guards: own goals 13.1 -> 17.6, ally head-on 1.6 -> 4.3, newborn dead10 0.26 -> 0.30, win share 0.84 -> 0.64
```

**Gate fix.** The tempo gate printed INCONCLUSIVE here. Its rule fell through when the CI passed but the map guard
failed. It now prints `MAP GUARD`.

**Win and loss shape.**

| | hb1-04 | hb1-12 |
|---|---|---|
| wins by elimination | 52 | 59 |
| losses by elimination | 8 | 5 |
| losses on length at round 500 | **35** | **14** |

On the four maps where hb1-04 loses (Portals, Slithery Fight, Default, Schooltime; 48 games), at round 499:

| | hb1-04 | hb1-12 |
|---|---|---|
| win share | 0.35 | 0.77 |
| total length, own vs opponent | 196 vs 53 | 136 vs 42 |
| longest dragon, own vs opponent | **12 vs 24** | **36 vs 21** |
| splits r250–500 | 194 | 124 |

The mimic keeps splitting to the end and never grows a crown. The round-500 tiebreak is longest dragon first, then
total length. This matches the family comparison in `docs/family-comparison.md`: the swarm ladder loses the
longest-dragon tiebreak while winning total length.

## 5. Crown graft: hb1-04 opening plus Ares endgame

**Bots.** `bots/ouroboros-g01/g02/g03-hbmimic-ares-r150/250/350` are copies of hb1-04 (lane hb1, not modified) with
one change: the mimic decides while round < R, and the Ares V06 policy decides from round R. Ares's `World::sense`
runs every mimic turn, so its memory is warm at hand-over.

**Run.**

- 360 games: 3 variants × 10 maps × 6 panel opponents × 2 seats, seed 1, the same fixture names as the panel.
- Played in the cloud container (x86 Linux, 2 cores). hb1-04 and hb1-12 come from the Mac panel run, so pairs are
  cross-machine.

**Cross-machine pairing is exact.** The game is deterministic for a given seed.

- A cloud copy of hb1-04, with the switch disabled, reproduced the Mac outcome in 43 of 43 fixtures.
- The grafts' first R rounds reproduce hb1-04's opening exactly (tempo delta 0.00 on all maps).
- So every difference below comes from the hand-over.

| bot | win share (120 fixtures) | fixtures better / worse than hb1-04 | vs hb1-12 better / worse |
|---|---|---|---|
| hb1-04 (parent) | 0.64 | — | — |
| **g01, switch at r150** | **0.84** | **26 / 2 (sign test p < 0.0001)** | 11 / 11 (tie) |
| g02, switch at r250 | 0.79 | 21 / 3 (p = 0.0003) | 10 / 16 |
| g03, switch at r350 | 0.78 | 19 / 2 (p = 0.0002) | 9 / 16 |
| g04, switch at r100 | 0.81 | 23 / 3 (p < 0.001) | 11 / 15 (and 10 / 14 vs g01) |
| hb1-12 (reference) | 0.84 | | |

Per map (win share):

| map | hb1-04 | g01 | g02 | g03 | hb1-12 |
|---|---|---|---|---|---|
| Autarky | 1.00 | 1.00 | 1.00 | 1.00 | 0.92 |
| Default | 0.50 | **0.92** | 0.75 | 0.58 | 0.92 |
| Devil | 0.75 | 0.75 | 0.75 | 0.75 | 0.83 |
| Prisoners Dilemma | 1.00 | 1.00 | 1.00 | 1.00 | 0.92 |
| Portals | 0.25 | 0.67 | **0.92** | 0.83 | 0.75 |
| Queen of Spades | 0.67 | **0.92** | 0.75 | 0.58 | 0.83 |
| Schooltime | 0.42 | 0.58 | 0.42 | 0.58 | **0.75** |
| Slithery Fight | 0.25 | 0.67 | 0.67 | 0.67 | 0.67 |
| Trauma | 0.58 | **0.92** | 0.67 | 0.83 | 0.92 |
| Trophy | 1.00 | 1.00 | 1.00 | 1.00 | 0.92 |

**Reading.**

- **The missing crown was the main problem with the Heartbreaker mimic.** Handing over to Ares turns a 0.64 bot into
  a 0.84 bot. The opening is unchanged; the gain comes after round 150.
- **Round 150 is the best of the four hand-over points tested.** Win share by switch round: r100 0.81, r150 0.84,
  r250 0.79, r350 0.78.
  - Later than 150 loses ground, so Ares's mid-game helps as well as its crown.
  - Earlier than 150 costs the mimic's opening economy. The tempo gate on g04 vs hb1-04 gives **REJECT**, +0.85 rounds
    [+0.35, +1.38]: length at r150 drops from 91 to 80, and per-transit death rises from 0.15 to 0.21.
  - The mimic is the better policy up to about r150, and Ares after it.
- **g01 ties hb1-12 overall but by a different route.**
  - It keeps hb1-04's opening, the fastest of any local bot, with PD 40 rounds ahead of the top-ten curve.
  - It is perfect on the elimination maps (Autarky, Prisoners Dilemma, Trophy) and weaker on Schooltime and Devil.
  - A map-conditional switch is the obvious next variant: mimic longer where the mimic's opening dominates, hand over
    early on Schooltime and Devil.
- **Upload.** g01 inherits the 61.6 MB mimic model, so it is not uploadable. Shipping it needs the hb1-14/hb1-15
  truncated direction model (4 MiB limit) and a check that the truncated mimic keeps the opening. That is the hb1
  lane's packaging work; the graft change itself is three lines in `main.cpp`.

**Gate note.** The tempo gate correctly reports NO GAIN for the grafts: delta 0.00, because their opening is identical
to the parent's. Tempo is an opening gate; this gain is whole-game and is judged on win share and the round-500 reason.
