---
id: shenzhen-unit6-sprint-tax
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: measurement + hypotheses
title: Unit 6 — top-ten queens sprint constantly and almost never pay; long queens are fast for free
evidence: build/shenzhen/qpay/ (416 post-m2 round-limit games with a top-ten side or us; every move's `paid` field)
queries: tools/shenzhen/qpay.py, tools/shenzhen/q_qpay.py
---

# 1. H-SZ21 (the queen never pays sprint segments): what the field does

Segments paid for multi-step moves (unswbc 1.2.3: the first ⌈L/4⌉ steps free), per side per RL game:

| cohort | sides | all dragons, paid/game | queen, paid/game | queen multi-step share of its moves | queen alive at end |
|---|---|---|---|---|---|
| top ten | 366 | 31.6 | **0.17** | 8.2 % | 0.42 |
| ranks 11–50 | 158 | 21.9 | 0.60 | 3.3 % | 0.31 |
| below 50 | 150 | 20.9 | 0.34 | 5.8 % | 0.23 |
| us (carthage-05) | 158 | 27.9 | 0.11 | 1.0 % | 0.00 |

Queens alive at the end: top ten pay 0.11 segments per game (8 % ever pay), ranks 11–50 pay 0.63 (25 % ever pay) — and
those mid-table queens end at length 3, where one paid segment is a third of the tiebreak. Vibing++'s queen makes 75
multi-step moves per game and pays 0.95 segments; SSS's 50 and 0.29; 𓎼's 50 and 0.00. **The top ten sprint the queen
a lot and inside the free allowance.** The team-level sprint tax is a style choice, not a top-ten marker (SSS 79
segments/game, tungtung67 69, Vibing++ 60; Cache me outside 3, 𓎼 3).

# 2. Why it matters: a long queen is fast for free

Free steps grow with length (⌈L/4⌉): a 21-long queen (the top ten's median when alive) moves up to 6 cells a turn at
no cost. Unit 2's hazard table already showed the queen's enemy-kill rate falling with length (2–3: 2.04 / 1k rounds;
13+: 1.12). Length is both the tiebreak and the escape speed.

# 3. Hypotheses

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ21 (supported by the field) | The queen moves multi-step only within its free allowance. Top-ten queens already do (0.11 paid/game alive vs 0.63 for ranks 11–50). | probe D's rule changes no fixture outside cages in a parity run (then it is free to carry) — or it costs RL wins | parity + pool s1–3 | any tester, bundle with H-SZ1 |
| H-SZ23 speed loop | Feeding the queen early buys free speed (⌈L/4⌉) and speed buys survival: queen hazard falls with length after controlling for team. Implication: feed the queen to ≥ 8 (2 free steps) before r150, not only late. | within keeper teams, queen enemy-kill hazard at length ≥ 8 is not < 0.7× the hazard at 3–7 | corpus (hazard pass, team-stratified) | analyst, then tester |
