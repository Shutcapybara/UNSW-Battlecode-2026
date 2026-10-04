---
id: shenzhen-unit12-corpse-flow-correction
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: correction + corpus measurement
title: Unit 12 — retraction of unit 11 §2 (late income is about half beds, not 85–99 % corpses); the real gaps are bed income and a leaky corpse loop
evidence: tools/shenzhen/corpse.py — 463 post-m2 games (after 2 Oct 04:31Z) on Slithery, Around UNSW, Islands, Trauma, Portals with a top-ten side or us; eats classified by the frame's own origin label (bed / ally_corpse / enemy_corpse), corpse pearls attributed by the spawn's donor side
---

# 1. Retraction

Unit 11 §2 classified eats by looking up each cell in `maps/live` with cell = (i mod W, i div W). That mapping does not
match the replay's cells, so real bed eats were counted as "other" and read as corpse pearls. **The claims "late-game
length is 85–99 % corpse pearls", "the top ten recycle +46–60 %", and "fountains yield nothing" (H-SZ27 dropped) are
withdrawn.** `tools/shenzhen/fountain.py` is marked withdrawn; H-SZ27 returns to untested. The unit-11 simulator dose
result (H-SZ26 refuted) does not depend on this and stands.

# 2. Corrected flow after r150 (per side, means)

| map | cohort | n | bed meals | own-corpse meals | enemy-corpse meals | own corpse pearls made | share of own corpses we eat | share eaten by the enemy | win |
|---|---|---|---|---|---|---|---|---|---|
| Around UNSW | top ten | 87 | 745 | 632 | 122 | 758 | 0.83 | 0.16 | 0.74 |
| | us | 16 | **491** | 356 | 144 | 530 | **0.67** | **0.31** | 0.31 |
| Islands | top ten | 89 | 571 | 526 | 136 | 655 | 0.80 | 0.18 | 0.82 |
| | us | 18 | **427** | 259 | 129 | 445 | **0.56** | **0.42** | 0.39 |
| Slithery Fight | top ten | 102 | 913 | 934 | 81 | 1,013 | 0.92 | 0.08 | 0.59 |
| | us | 11 | **548** | 567 | 69 | 665 | 0.85 | 0.13 | 0.36 |
| Trauma | top ten | 98 | 336 | 322 | 20 | 355 | 0.89 | 0.06 | 0.71 |
| | us | 14 | **207** | 192 | 20 | 229 | 0.80 | 0.14 | 0.14 |
| Portals | top ten | 96 | 386 | 523 | 0 | 527 | 0.99 | 0.00 | 0.68 |
| | us | 14 | 431 | 589 | 0 | 594 | 0.99 | 0.00 | 0.21 |

Two gaps, both large:
1. **Bed income.** The top ten eat 35–67 % more bed pearls after r150 on four of five maps (Portals equal).
2. **A leaky corpse loop.** We recover 56–85 % of our own corpse pearls; the top ten 80–92 %. On Islands **42 %** of our
   corpse pearls are eaten by the enemy (top ten 18 %); on Around UNSW 31 % (16 %). We feed the opponent.

Portals is different: no corpse ever crosses sides there (0 enemy-corpse meals both cohorts), and our economy matches the
top ten's — our Portals losses (0.21 win) are not economic. That is the map to look at for queen/tiebreak causes.

# 3. Hypotheses

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ27 | interval-1 bed "fountains" | back to untested (unit-11 evidence withdrawn) | corpus with a correct cell mapping | analyst |
| H-SZ28 (refined) | Our late economy leaks: our dragons die where enemies collect the corpses (Islands 42 %, Around UNSW 31 % vs 16–18 %). Dying at home (culls next to our own heads, retreating before a trap closes) keeps the corpse in the loop. | a death-location analysis shows our leaked corpses are not in contact zones (enemy head within 3 at death) more than the top ten's | corpus: deaths by enemy-head distance × who eats the corpse | analyst (next unit) |
| H-SZ29 | cull next to a long ally head (unchanged; now motivated by the leak, not by volume) | ally-corpse recovery per cull not +20 % in simulator | simulator 12 sides | Claude tester |
| H-SZ30 bed income | The top ten take 35–67 % more bed pearls late at equal map. Candidate mechanism: they keep heads on bed clusters as timers come due (`Tile.get_pearl_time()` is visible in the 7×7 view). Corpus check: share of bed pearls eaten within 1–2 rounds of spawning, by cohort. | the top ten's spawn-to-eat latency on beds is not shorter than ours | corpus, 300 games | analyst |
