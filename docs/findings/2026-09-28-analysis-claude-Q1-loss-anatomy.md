---
id: A1-Q1-loss-anatomy-v2
author: claude/analysis/session-01KHqE
kind: observation
title: Every live source loses the same way — behind on material by r100, eliminated on compact maps, out-grown on open maps
task: A1 statistics analysis (handoff §3.1)
supersedes: A1-Q1-live-loss-anatomy (gpt-6/analysis/codex-session, 12:15 UTC; field pool only, no per-opponent strata, no survival curves, no first-behind stage)
evidence: LIVE/state/state.json results (updated 2026-09-28T12:12Z; 446 verified of 486), re-derived by `python -m tools.analysis.a1_report --state LIVE/state/state.json --ladder LIVE/state/ladder.json` (build/a1_report.md §Q1); hub function `tools/hub/analysis_a1.loss_anatomy`
---

**Unit:** game. **Sample:** verified, controlled, API side A, field and dev pools together (425 games; the dev pool adds
20 games per source against 545/752 and is reported separately in the opponent strata). Codex's field-only numbers
(n=265) are reproduced exactly where they overlap (9508: 51 compact field games, 28 eliminations; units r100 6/15). All
stage fields carry the terminal state forward for eliminated sides (units 0, total 0), so medians over losses are not
survivor-only. Opponents are stratified by submission id; 545 changed from 9371 to 9571 at ~03:20 UTC and the two are
kept apart.

## 1. Loss split per source (sources with ≥ 20 controlled A-side games)

| source (bot) | n | share | losses elim / RL | elim round median (q25–q75) | elim round compact / open | RL-loss longest margin median (q25–q75) | compact share (n, elim losses) | open share (n, elim losses) |
|---|---:|---:|---:|---|---|---|---|---|
| 9508 (fenrir-v18, teammate incumbent) | 143 | 0.441 | 48 / 32 | 170 (114–278) | 140 / 350 | −10.5 (−24 – −5) | 0.31 (59, 31) | 0.54 (84, 17) |
| 9663 (yuna-v02-core) | 70 | 0.414 | 24 / 17 | 168 (111–283) | 122 / 255 | −12 (−16 – −10) | 0.29 (28, 13) | 0.50 (42, 11) |
| 9639 (ein-dog-v02-momentum) | 52 | 0.288 | 25 / 12 | 194 (64–387) | 150 / 387 | −9 (−18 – −6) | 0.18 (22, 16) | 0.37 (30, 9) |
| 8540 (bifrost-v01-portal-memory) | 51 | 0.431 | 16 / 13 | 180 (128–287) | 155 / 298 | −12 (−20 – −6) | 0.43 (21, 10) | 0.43 (30, 6) |
| 9980 (tidus-t02-spread-only) | 49 | 0.367 | 20 / 11 | 180 (104–296) | 158 / 200 | −14 (−16 – −4) | 0.20 (20, 13) | 0.48 (29, 7) |

Losses are eliminations first (60 % of all losses pooled; 74 % of compact-map losses), and they come early: the
median compact elimination is round 122–158, i.e. before the r250 crown election of every current line. Round-limit
losses lose the longest-dragon race by 9–14 segments at the median — not by one or two.

## 2. Per-opponent strata (the same games, split by opponent submission)

Win share / units r100 (ours vs theirs) / total r250 (ours vs theirs) / elimination losses:

| source | 62/9343 Heartbreaker (rank 40) | 45/9433 WeLikCoding (59) | 470/6350 龙虎豹 (6) | 545/9571 dev1 (15) | 752/3887 dev2 (85) |
|---|---|---|---|---|---|
| 9508 | 0.36 · 6 v 17.5 · 17.5 v 88 · 25 of 27 losses | 0.52 · 13.5 v 16 · 46 v 57 · 6 of 19 | 0.39 · 11 v 18 · 35 v 91 · 7 of 19 | (9371) 0.20 · 10.5 v 19.5 · 4 of 8 | 0.80 · 11 v 10 · 76 v 47 · 1 of 2 |
| 9663 | 0.30 · 8.5 v 21 · 19.5 v 72.5 · 11 of 14 | 0.65 · 16.5 v 16 · 61 v 42 · 1 of 7 | 0.10 · 13 v 22.5 · 23.5 v 102.5 · 4 of 9 | 0.30 · 9.5 v 20 · 4 of 7 | 0.60 · 9.5 v 16 · 4 of 4 |
| 9639 | 0.25 · 2.5 v 20 · 0 v 67 · 9 of 9 | 0.40 · 15.5 v 17.5 · 54 v 69.5 · 2 of 6 | 0.30 · 10.5 v 18.5 · 46 v 80.5 · 4 of 7 | 0.00 · 11 v 23.5 · 5 of 10 | 0.50 · 11 v 21 · 5 of 5 |
| 8540 | 0.30 · 6 v 22.5 · 9.5 v 78 · 5 of 7 | 0.60 · 12 v 17 · 38.5 v 57.5 · 2 of 4 | 0.36 · 14 v 11 · 27 v 80 · 3 of 7 | (9371) 0.20 · 12 v 23 · 5 of 8 | 0.70 · 12.5 v 12 · 1 of 3 |
| 9980 | 0.22 · 9 v 18 · 0 v 79 · 6 of 7 | 0.50 · 12 v 15 · 56.5 v 37.5 · 2 of 5 | 0.30 · 11 v 11 · 35 v 89 · 4 of 7 | 0.10 · 6 v 20.5 · 5 of 9 | 0.70 · 11 v 11.5 · 3 of 3 |

Heartbreaker (62) is the elimination machine: 56 of 64 losses to it across the five sources are eliminations, and
against it every source has a median total length of 0–20 at r250 against its 67–88. 470 and 45 beat us on the round-limit longest race
(19–20 vs 14–20 at r499 for 9508). Note that 470 (rank 6) and 545 (rank 15) are far above the band that decides our
rating (ranks 60–76); the screen panel [62, 45, 470] contains one band-like opponent (45).

## 3. When the loser falls behind

The earliest stored stage is r100. In losses, the losing side already trails the opponent on **total length by r100**
in 68/80 (9508), 36/41 (9663), 34/37 (9639), 24/29 (8540) and 28/31 (9980) games; the same holds on unit count. So the
decisive divergence happens before r100 and the record cannot locate it more precisely (research item: add r25/r50
stage points to the decoder). Wins are split: 28 of 63 wins of 9508 were also behind at r100 and recovered.

Win share conditional on the r100 total-length lead (all five sources pooled, 425 games):

| map class | behind at r100 | ahead at r100 |
|---|---|---|
| compact | 0.14 (n = 127) | 0.78 (n = 46) |
| open | 0.31 (n = 159) | 0.76 (n = 87) |

The same split holds inside every source (compact behind 0.05–0.19 vs ahead 0.60–1.00; open behind 0.18–0.39 vs
ahead 0.57–0.92). Being behind at r100 is the norm (67 % of our games), which is the statistical form of "we are
out-produced in the opening".

## 4. Survival curves (share of games with our units > 0, by stage)

| source, class | n | r100 | r200 | r250 | r300 | r400 | r499 | opponent r499 |
|---|---:|---|---|---|---|---|---|---|
| 9508 compact | 59 | 0.85 | 0.59 | 0.49 | 0.47 | 0.47 | 0.47 | 0.86 |
| 9508 open | 84 | 0.99 | 0.95 | 0.95 | 0.92 | 0.87 | 0.80 | 0.92 |
| 9663 compact | 28 | 0.86 | 0.68 | 0.64 | 0.61 | 0.54 | 0.54 | 0.86 |
| 9639 compact | 22 | 0.73 | 0.50 | 0.50 | 0.45 | 0.36 | 0.27 | 0.95 |
| 9980 compact | 20 | 0.80 | 0.60 | 0.60 | 0.50 | 0.40 | 0.35 | 0.90 |
| 8540 compact | 21 | 0.81 | 0.62 | 0.57 | 0.57 | 0.52 | 0.52 | 0.81 |

Half of our compact-map teams are dead by r250 for every source; the opponent's survival is 0.81–0.95 at r499.

## 5. Stage curves and deaths, wins vs losses (medians; deaths per 1k dragon-turns, terminal state)

| source, class, result | n | units r100 (opp) | total r250 (opp) | longest r400 (opp) | longest r499 (opp) | wall / self / body / h2h per 1k | newborn ≤10 deaths | splits |
|---|---:|---|---|---|---|---|---:|---:|
| 9508 compact W | 18 | 12.5 (15) | 54 (47.5) | 8.5 (6.5) | 25.5 (7.5) | 14.6 / 8.8 / 4.0 / 10.4 | 174.5 | 317 |
| 9508 compact L | 41 | 5 (19) | 0 (86) | 0 (5) | 0 (6) | 5.1 / 4.9 / 1.7 / 22.2 | 10 | 24 |
| 9508 open W | 45 | 18 (13) | 96 (51) | 9 (5) | 29 (12) | 5.9 / 2.9 / 2.5 / 4.4 | 48 | 167 |
| 9508 open L | 39 | 11 (16) | 24 (91) | 5 (9) | 7 (19) | 6.4 / 1.6 / 1.7 / 11.6 | 23 | 76 |
| 9663 compact W | 8 | 21.5 (15.5) | 64.5 (31) | 6.5 (3) | 19.5 (3) | 15.2 / 9.9 / 4.2 / 10.4 | 154 | 324 |
| 9663 compact L | 20 | 4 (20) | 1 (81.5) | 0 (7) | 0 (10.5) | 5.3 / 4.6 / 1.7 / 19.2 | 7.5 | 22 |
| 9639 compact L | 18 | 4.5 (22.5) | 0 (88.5) | 0 (4) | 0 (4) | 8.2 / 9.0 / 1.7 / 27.6 | 18.5 | 57 |
| 9980 compact L | 16 | 7 (19.5) | 1 (80) | 0 (4) | 0 (5) | 7.7 / 10.2 / 2.6 / 20.8 | 14 | 30 |

Two regularities. (a) The h2h death rate doubles in losses (19–28 per 1k vs 8–12 in wins) while wall/self rates fall —
losers die in head-to-heads with a bigger enemy swarm, not to their own moves. (b) Compact wins are churn: 150–235
newborn deaths and 250–430 splits per game, i.e. the "feeding by crashing" economy — when it starts, it wins; the
losses never reach it (splits 14–57).

## Diagnosis (two lines per source)

- **9508:** out-produced by r100 on compact maps (5 vs 19 units in losses) and eliminated by r140; open losses are
  round-limit longest deficits of −10 against 470/45 with half the opponent's r250 material. Runtime faults (1096 TLE
  turns) are not the mechanism — see Q6.
- **9663:** identical shape with a better compact win mode (21.5 units r100 in wins) but 11 of 14 losses to 62 are
  eliminations; 1–9 against 470.
- **9639:** the weakest opening of the five (median 2.5 units r100 against 62; 0/10 against 545); 16 of 22 compact
  games lost by elimination. Its momentum mechanism does not survive contact.
- **8540:** the most balanced (0.43 on both classes) but the oldest policy; compact losses are still 10 of 21 eliminations.
- **9980:** spread posture did not buy units (10 vs 11 for 9508 at r100); 13 of 20 compact games lost by elimination.

## Decision

Target opening production and early survival (rounds 0–100) before any late-conversion work; the compact-map
elimination mode is 74 % of compact losses and r100 material lead predicts the outcome at 0.78 vs 0.14. Late
conversion (RL longest margin −9 to −14) is the second problem and only matters on open maps against 470/45.

## Falsifier

A candidate that raises units r100 by ≥ 4 on compact maps in exact pairs (Q2 instrument) without raising its compact
win share, or a seeded live-pool panel (research item 1) in which r100 lead stops predicting the outcome (share
difference < 0.2 between ahead and behind).
