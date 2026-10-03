---
id: shenzhen-unit2-hunting-feeding-matchups
author: Shenzhen (P2-A analyst, Opus 5.5, replay lead)
kind: measurement + hypotheses
title: Unit 2 — nobody hunts queens, crowns are fed on ally corpses, keepers are the hard matchup; the Schooltime bug is the map, not the bot version
evidence: build/shenzhen/lean/ (5,928 post-change games); build/shenzhen/hazard/ (833 post-m2 games, every dragon-round)
queries: tools/shenzhen/q_slate2.py (H-SZ6/8/9/10), tools/shenzhen/hazard.py + q_hazard.py (H-SZ5/7/8b)
---

All numbers post-m2 (started ≥ 2 Oct 03:49Z), cohorts by the 3 Oct post-reset ladder (Chongqing C1-02: the ladder was
reset to 1500 on 1 Oct, so every rank is post-rules).

# 1. Correction to two readings: it is the map swap, not hb1-14 vs carthage-05

- **Schooltime round-0 queen death (Chongqing C1-03, H-C1; my H-SZ1).** Team 7 on Schooltime by map hash: old maps
  (e09bd6e0cd8e, b1ab27eaae9f) **0/51** round-0 queen deaths; new maps (four hashes) **22/22**, both seats. Both of our
  submissions are affected only on the new map. A tester checking "does the local Schooltime fixture reproduce it" will
  find it does not: `maps/schooltime.map` is the old, open spawn. Use `unswbc==1.2.9`'s `templates/maps/schooltime.map`.
- **Default spawn hazard (Chongqing H-C3, field queens dead by r5 0.22–0.36).** Top-50 sides: pre-swap 8/34 (24 %),
  post-swap **10/443 (2.3 %)**. The hazard belongs to the old Default; four edges changed in the swap.

# 2. H-SZ5: nobody hunts queens

Every enemy-caused death (h2h or body) against every dragon-round in 833 games, queen vs non-queen, length-stratified
(Mantel–Haenszel rate ratio over length bins 2–3/4–6/7–12/13+), by the killing team:

| killer | queen kills | queen rate /1k rounds | other dragons /1k | rate ratio queen ÷ other |
|---|---|---|---|---|
| top ten | 186 | 2.84 | 6.53 | 0.44 |
| ranks 11–50 | 250 | 1.87 | 5.07 | 0.37 |
| below 50 | 124 | 1.64 | 3.88 | 0.43 |
| us | 81 | 1.45 | 5.28 | 0.28 |
| most "huntery" team: horse | 24 | 4.53 | 5.50 | 0.83 |
| least: Vibing++ | 12 | 1.46 | 6.90 | 0.21 |

No team kills queens faster than other dragons of the same length; every ratio is below 1. Queen survival is the
keeper's avoidance, not the field's neglect alone, but nobody spends effort on the queen even though its id is visible:
`DragonPart.get_id()` exposes the dragon id of every visible segment, and the queens are ids 0 and 1 (Antioch, 2,448/2,448).
A queen hunter faces a target nobody else is chasing.

Exposure (H-SZ7): a living queen has an enemy head within 3 (torus Manhattan) in 10–14 % of its rounds in every cohort,
ours included (10.9 %); escort (ally head within 3) 32–37 %, SSS 52 %, Sponge 22 %. Our queens do not die because they
are more exposed per round; they die early (median r59–79) and never get to be keepers.

# 3. H-SZ8: crowns are fed on ally corpses, late

Queen length by checkpoint, round-limit games where the queen survives (median):

| team | r50 | r150 | r250 | r400 | r490 | queen meals |
|---|---|---|---|---|---|---|
| Vibing++ | 4 | 5 | 11 | 23 | 37 | 46 |
| Sponge | 4 | 6 | 10 | 24 | 27 | 46.5 |
| horse | 3 | 3 | 3 | 16 | 28 | 37 |
| SSS | 3 | 3 | 3 | 3 | 15 | 18 |
| 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 | 3 | 3 | 5 | 4 | 20 | 26 |
| free trip to sydney pls (runner) | 2 | 2 | 2 | 2 | 5 | 7 |
| forgot to mention, WeHaveQuizzes | 3 | 3 | 3 | 3 | 3 | 1–4 |

What the queen eats (sum over sampled games, top ten): before r150 mostly bed pearls (e.g. SSS 234 bed / 19 ally
corpse); from r150 mostly **ally corpses** (Sponge 493 ally-corpse vs 74 bed in r150–399; SSS 293 vs 32 after r400; 𓎼 259
vs 24 after r400; horse 325 vs 68 in r150–399). Enemy corpses are negligible everywhere. The crown is grown by the
team's own dragons dying next to it. Three timings exist in the top ten: grow from r150 (Vibing++, Sponge), from r250
(horse), and only in the last 90 rounds (SSS, 𓎼) — the last costs nothing until r400 and still ends at length 15–20,
which beats the median opponent queen (3–4) and is half of what the crowns reach.

# 4. H-SZ6, H-SZ9, H-SZ10: what the queen is worth, and against whom

- Top-ten win by queen fate: queen alive or never killed **0.93** (n 824); died r11–50 0.63; r51–150 0.54; r151–300 0.47;
  r301–498 0.52. Association, not effect (winning keeps queens alive), but a top-ten team that loses its queen after r150
  wins about half its games, like everyone else.
- Opponent queen policy (share of the opponent's RL games ending with its queen alive, teams with ≥ 20 RL games):
  every cohort does worst against keepers — top ten 0.73 vs no-queen opponents → 0.60 vs keepers; us 0.29 → **0.19**.
  The runner team (free trip to sydney pls) is the odd one: 0.38 vs no-queen, 0.65 vs some, 0.32 vs keepers.
- How games against top-ten opponents end: top ten (mirror) 21 % elimination wins, 29 % RL wins; us **8 % elimination
  wins, 5 % RL wins**, 52 % RL losses. We neither kill them nor outlast them.

# 5. New hypotheses (slate)

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ5 hunt | Target the enemy queen by id (0/1 not ours, in vision): a strike/trap bonus on it. Nobody does this; 42 % of top-ten RL games end with their queen alive and 40 % of RL games are queen-decided. | vs a keeper opponent (carthage-08 as proxy), opponent queen alive@end drops < 15 pp, or econ LB < −0.03 | pool + gen s1–3 with a keeper in the pool (none of the panel bots keeps a queen; add carthage-08) | Claude tester; needs live maps |
| H-SZ8 late feed | Keep a small queen to r400, then route doomed/small allies to die adjacent to it (SSS/𓎼 form). Cheap: no cost before r400. | queen len@490 (alive) < 10, or win on RL fixtures not up, or own-body/invalid tier-2 > +10 % | pool s1–3 on live maps, RL fixtures | any tester; stacks on an alive-queen arm |
| H-SZ12 queen-death is a 0.4 swing | For top teams a queen death after r150 costs ~0.4 win probability; for us (never alive) the swing is untested. A bot that knows its queen is dead should switch to elimination play (we win 8 % by elimination vs top ten). | elimination win share vs top-ten opponents unchanged when the switch fires | local; needs an opponent that keeps queens | tester, later |
| H-SZ13 opponent-policy read | By r100 an opponent's queen policy is legible (queen moves every round, stays near allies, len 3–5). Keepers are the hard matchup for every cohort: play hunt + outlast against keepers, play pure longest/total against non-keepers. | win vs keepers ≤ win vs non-keepers − 0.1 persists after H-SZ5 | descriptive first (corpus), then an arm | analyst then tester |
