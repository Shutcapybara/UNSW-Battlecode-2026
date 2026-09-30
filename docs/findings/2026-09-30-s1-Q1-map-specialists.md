---
id: S1-Q1-map-specialists
author: s1 (statistics assistant, Opus 5.5)
kind: observation
question: Are the top teams map specialists?
evidence: public_replays/corpus/index.jsonl (53,744 games, 26–30 Sep; the ten ladder maps) + ladder/ (250 snapshots); top 50 at the 07:57 UTC snapshot
query: python3 tools/s1/questions.py q1   → build/s1/out/q1/{teams,map_effects}.csv, docs/findings/s1-figs/q1-map-effects.png
---

**Answer: yes, almost all of them.** For 50 of the 51 teams tested (the current top 50 plus team 7), map fixed effects
improve on the gap-only model (likelihood-ratio test, 9 df, Benjamini–Hochberg q < 0.05). The exception is Average
Individuals (#48, n = 354).

The effects are large:

- The median team's map effects have an SD of **153 Elo** (10th–90th percentile 106–235).
- The median |effect| is 108 Elo. The whole top 50 spans ~300 Elo.

They also replicate:

- Across disjoint halves of each team's games (odd/even game id): pooled r = 0.50 over 510 team-maps, per-team median
  r = 0.73, and 98 % of teams positive.
- Early vs late halves (a version-drift check): pooled r = 0.39, median r = 0.66, and 96 % positive.

**Model.** Per team, one row per game from that team's side:
`logit P(win) = a + b·gap/100 + c·seatA + Σ map_m`, with sum-to-zero map effects, so each is relative to the team's own
average map.

- `gap` = team Elo − opponent Elo at the latest ladder snapshot at or before the game start, clipped to ±800.
- `seatA` is in because side A is usually the lower-rated side.
- Draws are dropped (7). Maps with fewer than 500 games (three retired maps, 18 games on 26 Sep) are dropped.
- **Gap-equivalent Elo** = effect ÷ field slope × 100. The field slope is 0.419 logit per 100 Elo with seat held, below
  the Elo formula's 0.576, so ratings are noisy and compressed. Per-team slopes are unstable, and the per-team conversion
  is also in the CSV.

**Sensitivity.** Using only games with a snapshot before them, 49/51 teams have q < 0.05. Using only ranked games, 46/51 do.

**Top ten and us:** gap-equivalent Elo vs the team's own average map; * = 95 % CI excludes 0.

| # | team | Autarky | Default | Devil | Portals | PD | QoS | School | Slithery | Trauma | Trophy |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cheji bt | −88* | 118* | −157* | −41 | −171* | **458*** | 161* | **−303*** | 106* | −83* |
| 2 | Cache me outside | −191* | 64 | 45 | −38 | 166* | 68 | −184* | −265* | **389*** | −54 |
| 3 | Cutlery (306) | 24 | −29 | −41 | −119* | −94* | 63* | 83* | 34 | −47 | 126* |
| 4 | SSS | 123* | −50 | −32 | −148* | 18 | −38 | 108* | 161* | −25 | −117* |
| 5 | forgot to mention | 253* | −211* | 227* | −249* | 234* | 23 | −77* | −100* | 86* | −186* |
| 6 | calc | 291* | 184* | −7 | −51 | −115* | 82 | −76* | −158* | −125* | −24 |
| 7 | 中国必须人能飞 | −108* | 194* | 30 | 356* | −223* | −1 | −234* | −270* | 78 | 177* |
| 8 | Stockfish | −85* | 25 | −173* | 138* | −173* | −90* | 148* | 112* | 44 | 56 |
| 9 | Team SKKU | 4 | −25 | 34 | −27 | 183* | −163* | 79* | 119* | −205* | 1 |
| 10 | ddabap | 172* | −250* | 56 | −125* | 107 | −40 | −43 | 185* | 1 | −64 |
| 70 | **us (7)** | **−237*** | −52 | −54 | **354*** | **−417*** | −82 | 252* | 389* | −8 | −143* |

**Per map:** teams (of the 50 with q < 0.05) with a significantly positive / negative effect there.

| map | strong | weak | SD of team effects (Elo) |
|---|---|---|---|
| Portals | 17 | 13 | 202 |
| Autarky | 12 | 19 | 195 |
| Trauma | 15 | 13 | 185 |
| PD (6 and 10 pooled) | 9 | 15 | 178 |
| Devil | 10 | 10 | 173 |
| Slithery | 17 | 11 | 170 |
| Default | 12 | 12 | 153 |
| Schooltime | 15 | 14 | 152 |
| QoS | 7 | 12 | 145 |
| Trophy | 10 | 13 | 128 |

**Reading.**

1. A ladder rating is an average over map-specific strengths whose spread is about half the spread between teams.
   Rank 1 (cheji) is +458 on QoS and −303 on Slithery.
2. Our profile is among the most extreme:
   - **Prisoners Dilemma −417** (win share 0.10) and **Autarky −237** (0.19) are where our rating leaks.
   - Slithery +389, Portals +354 and Schooltime +252 are already above our rating.
   - Q3 shows the PD mechanism: our total length collapses from round ~10 on PD and PD 10, while the top ten hold theirs.
   - Our 1,019 games mix every submission since 26 Sep. This is the programme's profile, not one bot's.
3. With team-map effects this large, a local gate averaged over maps can hide a map-specific loss. The ten ladder maps
   reward map-shaped play that unseen tournament maps will not.

**Caveats.**

- Effects are relative to the opponents' own map strengths, averaged over whoever the team met.
- Series games are not independent, so p-values are optimistic. The split-half replication is the real test.
- Decoy submissions (306) and version changes are pooled. The early/late split bounds how much that matters.

**Ledger rows touched** (`docs/hub/HYPOTHESES.md`):

- **L08** (atlas, 0.1 by rule): unchanged. The ladder rewards map identity, which is the reason the OOS rule exists.
- **L28** (pool edge partly map identity, 0.9): consistent at field scale.
- **Proposed new row:** "our PD and Autarky deficits (−417, −237 Elo-equivalent) are opening-mechanism gaps, not map
  memory", 0.6. Q3's per-map curves show the PD loss happening by round 10–40, through deaths to enemies rather than own
  goals.
