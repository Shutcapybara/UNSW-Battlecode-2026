---
id: nara-queen-hazard-anatomy
author: glm/nara (P2-A analyst)
kind: measurement
title: Unit 3 — queen hazard anatomy by map, the h2h length rule, and what Cutlery's flip actually changed
task: P2-A third unit
evidence: tools/nara/queen_cause_probe.py; build/nara/{queen_cause,queen_cutlery}.jsonl (main checkout); 1,054 post-era side-rows incl. all 146 Cutlery games; h2h rule check on 120 games
---

# 1. What kills queens, by map (post-era field, deaths to r490)

| regime | maps | alive@490 | dominant cause | enemy-credited |
|---|---|---|---|---|
| **pocket** (H-Q3) | Autarky, Slithery, PD | 0 % | wall/self/**invalid** (deliberate culls) | **0 %** |
| **contact** | Trophy, Default, QoS, Schooltime | 7–13 % | h2h (60–101 of ~100 deaths/map) | **65–84 %** |
| **corridor-mixed** | Devil, Trauma | 7 % / 21 % | Devil half wall+self; Trauma mostly wall+self | 45 % / 20 % |

- The corpus (ten ladder maps) confirms and extends kyoto's panel split: the field's pool-map queens die by
  **enemy h2h on the contact maps and by geometry on the corridor/pocket maps**. kyoto's "pool wall-first" number
  is about **our** base bot's queen — different population, same structure.
- **Implication for the H-Q1 arm family:** the missing pool lever for OUR bot is **queen-keyed enclosure/trapped
  avoidance** (carthage-08's remaining pool deaths: 171 of 259 trapped), i.e. L24's reach-band rule applied to the
  one dragon whose death costs a verdict — not more enemy-avoidance (carthage-06 moved gen survival only, exactly
  because gen kills are enemy-h2h and pool kills are geometric).
- The field itself invalid-culls queens on pocket maps (PD 10, Autarky 12, Slithery 8) — there the cull is correct.

# 2. The h2h length rule: length is not armor

1,207 h2h deaths with an identified killer (120 games): **victim longer than killer 857, tie 808, shorter 496**;
plus 2,161 mutual (both die). A fed queen does not win collisions. So N6's fed-crown value is the **tiebreak
margin** (queen length is compared first, then longest, then total) and queen-vs-queen duels — not collision
survival. The "grow the queen big so it survives" justification is dead; "grow it because 8.2 % of rl games are
already queen-decided and protectors are appearing" stands.

# 3. Cutlery's 13:00Z flip, mechanism identified

| | pre-flip (11–12h, n=62) | post-flip (13h+, n=110) |
|---|---|---|
| alive@490 | 1 | 23 |
| death round median | 24 | 35 |
| causes | **invalid 40** (65 % — deliberate cull), h2h 19 | h2h 39, self 22, **invalid 24** |

- **The flip is "stop culling the queen"**: pre-flip Cutlery killed its own queen by invalid command in 65 % of
  deaths; post-flip it stopped, and the residual invalid culls sit almost entirely on the pocket maps
  (PD 6 + Slithery 6 + Autarky 4 of 24) — a **state-keyed cull**: keep the queen where it can matter, recycle it
  where it cannot.
- No avoidance premium: the surviving queen's min distance to an enemy head at r100/200/300 is 10/9/11 — the same
  as its own teammates (11/9) and the field's surviving queens (7/7.5/7). It moves 454/500 rounds at normal
  exposure. Survival came from removing the self-inflicted cull, not from hiding or armor.
- Post-flip survival by map: Trauma **11/13**, Schooltime 3/11, Default 3/12, QoS 2/8, Trophy 3/14, Portals 1/7,
  and 0 on Autarky/PD/Slithery (0/33) and Devil (0/12) — matching §1's hazard map exactly.

# 4. Adaptation clock (16:50Z)

- No second top-10 flipper: Stockfish 1/56 → 2/49 → 2/32; cheji bt/ftm/CMO have no post-era games (antioch's
  collector-target request stands).
- Mid-tier risers (survival up in 13–14h vs 11–12h): fandagong 4/93 → 12/58, Shannon 1/98 → 9/64, No Idea 5/55 →
  8/30, 😹 2/81 → 8/71, Settlers 0 → 6/99, SHINK AI 0/15 → 5/56.
- Persistent (style, not flip): :3 (19/77, 9/48), Sponge (12/103, 9/76) — antioch's earlier list confirmed.
- Cutlery's 15h+ window reads 1/9 — small n, watch whether they toggled off.
- **First queen-vs-queen rl games are coming** (Cutlery × {fandagong, Shannon, No Idea…}): those compare queen
  LENGTH before longest — the fed form (N6) wins them; parked queens (length 3–5) lose them.

# 5. Readings this unit

- **carthage-05/04 (free on-route sprints, win LB > 0 both panels): agree, promote-ready.** It is N4 in bot form:
  the field mishandles free sprints (own-goals +12 %), this arm exploits them. The era edge decays as the field
  re-tunes — same clock as the queen. My reading for the director's gate question: era-adaptation arms
  (carthage-04+05) and queen arms share the shape — **win-led with econ guard**, not econ-led; the econ LB should
  not reject a neutral-economy change that wins on both panels.
- **carthage-08 (best H-Q1 form, gen verdicts 46–0, pool survival 4.7 %):** the corpus says the pool gap is the
  trapped/enclosure hazard on the queen specifically — next arm = queen-keyed reach-band avoidance (L24 applied to
  q0), expected to move pool survival without touching economy elsewhere.
- **antioch H-Q8 (queen feature block):** agree; add the §1 hazard regime (pocket/contact/corridor queen-hazard
  class) and "own queen in invalid-cull state" as features — Cutlery's flip shows the cull decision is where the
  value was.
- **himeji's Φ audit (H5-07/08):** agree with both requests — carried terminal states must be filtered before the
  checkpoint AUC means anything; Φ is not a percentile. Hold target adoption until active-only validation.

# 6. Reproduction

```
python tools/nara/queen_cause_probe.py --since "2026-10-01T09:23" --per-team 10 --out build/nara/queen_cause.jsonl
```
