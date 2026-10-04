---
id: shenzhen-unit14-corpse-leak-cohort
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: corpus measurement (birth cohort, fixed horizon — Himeji H28-03's method)
title: Unit 14 — the corpse leak holds by birth cohort: the enemy eats 29–39 % of our corpse pearls on the open cap maps vs 16–19 % for the top ten; about half is where we die, half is who collects
evidence: tools/shenzhen/corpse2.py — 349 post-m2 games (after 2 Oct 04:31Z, R ≥ 250) on Around UNSW, Australia, Islands, Slithery, Trauma, Portals with a top-ten side or us; query tools/shenzhen/q_corpse2.py
---

# 1. Method

Every corpse pearl born in rounds [150, R − 50] (spawn event with origin = the donor's side) is followed 50 rounds. Its
consumer is the first eat on that cell after the birth (a cell holds one pearl). Fates: eaten by its own side, by the
other side, uneaten. Death context of the donor: **contact** = an enemy head within 3 (Chebyshev, torus) of the donor's
head at death, else **home**. 90 % intervals: game-clustered bootstrap.

# 2. Result (share of corpse pearls by fate)

| map | cohort | sides | pearls born | own side eats | **enemy eats** [90 %] | uneaten | born in contact | enemy eats \| contact | enemy eats \| home |
|---|---|---|---|---|---|---|---|---|---|
| Around UNSW | top ten | 55 | 37,307 | 0.81 | 0.16 [0.15, 0.17] | 0.03 | 0.40 | 0.36 | 0.03 |
| | us | 16 | 7,537 | 0.68 | **0.29** [0.27, 0.32] | 0.03 | 0.59 | 0.43 | 0.09 |
| Australia | top ten | 61 | 28,949 | 0.79 | 0.19 [0.18, 0.21] | 0.02 | 0.52 | 0.34 | 0.03 |
| | us | 16 | 4,843 | 0.59 | **0.38** [0.33, 0.42] | 0.03 | 0.70 | 0.51 | 0.07 |
| Islands | top ten | 62 | 35,679 | 0.79 | 0.18 [0.17, 0.19] | 0.04 | 0.50 | 0.33 | 0.03 |
| | us | 18 | 7,206 | 0.57 | **0.39** [0.34, 0.44] | 0.04 | 0.70 | 0.53 | 0.06 |
| Slithery Fight | top ten | 51 | 43,706 | 0.90 | 0.07 [0.06, 0.07] | 0.04 | 0.41 | 0.15 | 0.01 |
| | us | 11 | 6,679 | 0.82 | **0.11** [0.10, 0.13] | 0.07 | 0.51 | 0.21 | 0.02 |
| Trauma | top ten | 53 | 15,196 | 0.89 | 0.05 [0.05, 0.06] | 0.06 | 0.23 | 0.22 | 0.00 |
| | us | 14 | 2,935 | 0.80 | 0.08 [0.06, 0.12] | 0.12 | 0.30 | 0.24 | 0.01 |
| Portals | both | 47 / 14 | | 0.96 | 0.00 | 0.04 | | — | — |

Unit 12's gross-flow direction survives the cohort re-cut with tighter numbers. Two mechanisms, about equal on Around
UNSW (counterfactual: our conditional rates with the top ten's contact share give 0.23, half-way from our 0.29 to their
0.16):
1. **We die in contact more** (59–70 % of our corpse pearls are born next to an enemy head vs 40–52 %).
2. **Contact corpses go to the enemy more** (43–53 % vs 33–36%), and even our home deaths leak 6–9 % vs 2–3 %.

Portals has no cross-side corpses for anyone, so the leak cannot explain our Portals losses (economy equal, win 0.21).

# 3. Hypotheses

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ28 (supported by cohort) | Our corpse loop leaks to the enemy on the open cap maps (Around UNSW, Australia, Islands): 29–39 % vs 16–19 %. | — (measured) | — | — |
| H-SZ32 salvage | After an ally dies in contact, nearby allies should value its corpse pearls above other food for ~10 rounds (deny the enemy). Expected to move "enemy eats \| contact" toward the top ten's 0.33–0.36. | in simulator self-play (C+D vs C+D+salvage, Around UNSW/Islands/Australia, 12 sides), our enemy-eaten share of contact corpses not down ≥ 5 pp, or total not up | simulator, then panel | Claude tester / Shenzhen probe |
| H-SZ33 die at home | Culls and trapped deaths should happen away from enemy heads (a dragon that is going to die anyway — trapped, or a cull — first steps away from enemy heads when it can). Targets the contact share (59–70 % vs 40–52 %). | contact share of our corpse births not down ≥ 10 pp in simulator | simulator | Claude tester |
