# D-080 §B — queen feeding census for bokuto-18 (Sugawara, queen owner, 5 Oct 2026 ~10:45Z)

Asked by D-080 §B: when the top teams start feeding, how many feeders, where the queen sits. Analysis only; no bot built.

## Data

- Ranked corpus `public_replays/corpus/index.jsonl` (fetched to 10:26Z), decoded with `tools/analysis/features/frame.decode`.
- **TOP**: the 10 highest non-dev teams on ladder snapshot 20261005T101713Z (264, 306, 91, 454, 213, 55, 952, 842, 507, 566),
  their newest ranked games since 4 Oct 18Z against opponents rated ≥ 1650: **210 team-games** (6–39 per team).
- **US**: team 7 ranked games requested since 5 Oct 08:15Z (17530 trial window): **55 games** (gids 1124275–1133280), 28–27.
- Queen = the team's lowest initial id. "Feed" = the queen eats a pearl dropped by an **ally corpse** (frame `origin`).
  Distances are torus Manhattan from the queen's head. Script and rows: `build/sugawara/feed/{feed.py,summ.py,rows.jsonl}`.
- map_era: current live maps (post-m2). Pooled over maps; no intervals (descriptive; per-team n is small).

## 1. The excess queen deaths are walls, not fights

| | games | queen h2h deaths | queen wall | self + body | queen alive r100 | r300 | r400 |
|---|---|---|---|---|---|---|---|
| TOP vs ≥ 1650 | 210 | 89 (0.42/g) | **7 (0.03/g)** | 16 | 161/190 (85 %) | 95/147 (65 %) | 74/130 (57 %) |
| US 17530 | 55 | 23 (0.42/g) | **14 (0.25/g)** | 3 | 39/53 (74 %) | 19/41 (46 %) | 13/37 (35 %) |

Our head-to-head queen death rate equals the top's. The whole survival gap is the wall/self/body column (17 vs 23 in
4× the games). Our 14 wall deaths: rounds 76–347; weakhold 4, Portals 4, Tower Defense 2, Islands, Maze, Around UNSW, Trauma;
7 of the 14 games lost. Fixing walls alone would put r300 survival near the top's (rough: +10–15 pp).

## 2. When the top teams feed

- Queen length (alive queens), TOP p25/50/75: r100 2/3/4 · r200 3/3/6 · r300 3/3/7 · **r350 3/3/17** · r400 3/4/15 · **r450 3/10/29**.
  US: 2/3/3 at every checkpoint to r400; r450 5/8/16.
- The median top queen stays at 3 until r400; the upper quartile starts growing at **r300–350**. Bokuto's "hide to
  r250–300, then feed" is the upper quartile, i.e. the strongest feeders (213, 842, 55), not the whole top ten.
- First ally-corpse feed: TOP median r85 (p25 40) — opportunistic early eats; **10th feed: median r329 (p25 245, p75 425)**
  in 46/210 games. US: 10th feed in 7/55 games, median r438.
- By team (n; feeds/g; 10th-feed median; end queen length of surviving queens):
  213 (19; 17.6; **r255**; 27) · 842 (39; 12.7; r284; 42) · 55 (23; 21.3; r344; 28) · 952 (24; 7.3; r325; 24) ·
  566 (28; 6.1; r426; 12) · 91 (18; 6.6; r463; 10) · 264 (20; 6.0; r444; 3) · 507 (15; 3.7; r498; 3) · 454 (18; 2.3; r293; 3).
  **US 17530 (55; 3.5; r438; 14).**

## 3. How many feeders, and how

- Queen eats overall, TOP: ally corpses 2,047, beds 1,538, enemy corpses 75. The queen grows mainly on her own team's dead.
- Distinct donors per fed game: median 3, p75 12 (US: median 1, p75 6).
- **Suicide is not the mechanism for most:** only 4 of 10 use it (264 120/game, 507 80, 213 32, 91 16; the other six 0).
  Only 485/2,047 (24 %) of queen corpse eats fall within 0–3 rounds of a team suicide. 17530 uses **0** suicides.
  So feeding = allies dying (combat, culls, crowding) **next to the queen** and the queen collecting, plus suicide for some.

## 4. Where the queen sits

- TOP alive queens: **2 allies within 5 tiles** (median, r150–350), nearest enemy head median 7 (p25 5), head cell open
  degree 4 (3 after r350). US is the same or farther from enemies (median 8–11) with the same escort count.
- So position/escort is not what separates us; wall deaths and the absence of a feeding phase are.

## 5. Payoff at the limit (TOP, games ending by the round limit, own queen length at end)

1–3: 15/23 · 4–12: 7/10 · 13–25: 8/9 · ≥ 26: 16/17. (Short queens still win 65 % against ≥ 1650 sides; long ones ~95 %.)

## Recommendations for bokuto-18 (mechanism, in order)

1. **No queen wall deaths** — target ≤ 0.05 per game (now 0.25). Check the move generator: never let the queen take a move whose
   next cell can lead into a dead end / wall within the sprint, and treat portal cells and 1-exit cells as walls for the queen.
   This is the cheapest gain and does not depend on feeding.
2. **Feeding phase from r280–300**: keep 2 escorts within 5 tiles; route ally corpses (culls of short/ stuck allies, and units
   about to die anyway) to die adjacent to the queen. Target: ≥ 10 queen feeds by ~r330 and queen ≥ 13 at the limit in
   half of limit games. Suicide is optional (6 of 10 top teams do without).
3. Measure on qk/qk2 and the new card columns (alive r100/200/300/end, both queens' length), plus **queen deaths by cause per game**
   — add `wall` to Asahi's card as its own column.

Forecast (not scored, D-072 §B): a bokuto-18 that cuts queen wall deaths below 0.08/g on the ladder lifts queen alive at r300
from 46 % to ≥ 58 %: 0.6.

## Caveats

Top games are newest-first, vs ≥ 1650 only; a top team's opponents are mostly weaker than it. Per-team n 6–39. Our 55 games
include the trial-2 window only. Feed definition counts any ally-corpse pearl eaten by the queen, including early incidental ones.

## LOO on bokuto-13-cull (D-080 §B instruction)

No LOO build is in `../wt-asahi/build/asahi/runs/` yet (10:30Z); nothing to read on qk/qk2. When it lands I read it on the
keeper panels against the base only.
