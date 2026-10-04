---
id: shenzhen-unit3-queen-home-and-feeding
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: measurement + hypotheses
title: Unit 3 — keepers' queens stay home and are seen early (hunting is feasible); crowns are fed by allies that kill themselves next to them
evidence: build/shenzhen/qsight/ (469 post-m2 games with a top-ten side or us, R ≥ 150); lean table now 6,299 games
queries: tools/shenzhen/qsight.py, tools/shenzhen/q_qsight.py
---

# 1. H-SZ14: the enemy queen can be found

Vision is the 7×7 square around a head (`Constants.VISION_RADIUS = 3`). For every queen alive at r5, the share of its
rounds in which any of its segments is inside the opposing team's vision:

| queen's team | n | median rounds alive | share of rounds seen by the enemy | ever seen | first seen (median round) |
|---|---|---|---|---|---|
| top ten | 501 | 247 | 0.27 | 0.92 | 40 |
| ranks 11–50 | 225 | 176 | 0.27 | 0.92 | 49 |
| below 50 | 140 | 172 | 0.36 | 0.96 | 42.5 |
| us | 59 | 74 | 0.23 | 0.85 | 31.5 |

And keepers stay home. Chebyshev distance (torus) of the queen's head from its own spawn head, queens alive ≥ 400 rounds,
medians at r150 / r300 / r490: Vibing++ 5.5 / 7 / 7, Sponge 5 / 8 / 7, SSS 6 / 8 / 6, horse 8 / 6 / 5, 𓎼 5 / 7 / 5,
tungtung67 3.5 / 6 / 1, forgot to mention 1 / 1 / 1, free trip to sydney pls 2 / 1 / 5. Top-ten interquartile range at
r490: 2–11.

Every map header carries `SYMMETRY` and both queens spawn at mirrored positions, so a bot knows the enemy queen's spawn
cell at round 0 from its own. Combined: the enemy queen's id is visible, its home is known at r0, it stays within ~6 cells
of home all game, and it enters our vision by r40 in most games and a quarter of its rounds thereafter. Nobody uses this
(unit 2: no team kills queens faster than other dragons).

# 2. H-SZ8 mechanism: allies die next to the crown on purpose

Every queen meal whose donor was an ally corpse, top-ten queens (469 games): the donor's cause of death.

| phase | invalid | self | h2h | body | wall |
|---|---|---|---|---|---|
| r0–149 | 0.57 | 0.18 | 0.15 | 0.06 | 0.04 |
| r150–399 | **0.76** | 0.17 | 0.04 | 0.02 | 0.01 |
| r400+ | 0.64 | **0.34** | 0.02 | 0.01 | 0.00 |

By team: Sponge 1,227 of 1,288 donor-meals invalid, Vibing++ 1,016/1,045 invalid, forgot to mention 327/345 invalid,
free trip 202/222 invalid; horse 296/328 self, 𓎼 422/495 self, Cache me outside 176/235 self; SSS mixes (269 invalid, 212
self). Donors are short (median length 3, 5 after r400) and young (median age 15 → 36 → 48 rounds); the queen eats the
corpse a median 3 rounds after the death. Enemy kills supply almost none of the corpses the crown eats.

Two cull primitives, then: (a) an ally next to the queen sends an **invalid command** and the engine kills it (Vibing++,
Sponge, ftm); (b) an ally **steers into its own body** (horse, 𓎼). Either leaves its body as pearls beside the queen. This is
L39's conversion with the queen as the fed dragon — and it already exists in our code as the cull used by TT's tt-05.

# 3. New hypotheses

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ14 home hunt | Send one or two hunters (len ≥ 4) to the mirror of our queen spawn from r150; strike the dragon with id 0/1 not ours when in vision and a safe head-on/trap exists. Feasibility measured above. | vs a keeper proxy, hunters see the enemy queen by r250 in < 50 % of games, or opponent queen alive@end unchanged | 60 RL fixtures vs carthage-08 on live maps | Claude tester; needs live maps and a keeper in the pool |
| H-SZ15 invalid-feed | Feed the queen by culling short allies adjacent to its head with an invalid command (the Vibing++/Sponge primitive), from r150 or r400. Cheaper and safer than self-collision (no body left in the queen's path). | queen length gain per culled ally < 2, or own-body/self tier-2 up > 10 %, or RL win not up | pool s1–3 on live maps, with an alive-queen arm as parent | any tester; stacks on H-SZ1 + survival |
| H-SZ16 stay home | A queen that stays within ~6 cells of its spawn (the keepers' range) survives longer than one that roams (our living queens are 8 at r50, 11 at r150). | in a queen-survival arm, a home-range leash does not raise alive@490 by ≥ 5 pp at econ LB > −0.03 | pool + gen s1–3 live maps | tester |
| H-SZ17 decoy cost | Because nobody hunts, the queen needs no escort; SSS escorts (ally head within 3 in 52 % of rounds), Sponge does not (22 %) and both keep the queen ~50 %. Escort is not the survival mechanism; distance from enemy heads and staying home are. | descriptive: escort share does not predict survival across keeper teams (rank correlation < 0.3) | corpus query | analyst |
