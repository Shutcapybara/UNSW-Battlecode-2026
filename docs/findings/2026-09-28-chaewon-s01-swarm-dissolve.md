---
id: 2026-09-28-chaewon-s01-swarm-dissolve
author: claude/chaewon/cowork-016ueqq
kind: observation
title: "S1 swarm-dissolve on the v10 host: all three falsifiers fire; atlas and portal probes are the leads"
task: next-gen-prompt-S1-swarm-dissolve
supersedes: ""
evidence:
  - bots/chaewon-s01-swarm-dissolve/README.md (2x2, funnel, metering)
  - tools/chaewon/panel.py, tools/chaewon/cstats.py (harness and replay statistics)
  - bots/chaewon-s02-atlas/README.md, bots/chaewon-y0*/README.md (follow-up screens)
---

# S1 swarm-dissolve (chaewon line): what the 2×2 says

**Setup.** Host `ouroboros-v10-beacon`. Four arms with one `main.py` (control / production / dissolve / both), 80
paired fixtures each: 10 live maps × 2 sides × seed 1 × {yuna-v02-core, sinbad-v07, ouroboros-m01, ouroboros-v10},
unswbc 1.2.2 with `--seed`. Harness `tools/chaewon/panel.py`; statistics from replays (`tools/chaewon/cstats.py`).

| Arm | Score | Δ vs control | better/worse | sign p |
|---|---|---|---|---|
| control | 0.438 | — | — | — |
| production (λ_unit to r100, salvage, certificate v2) | 0.400 | −0.037 | 7/10 | 0.63 |
| dissolve (crown r250, onset r300/r400, adjacent recipient-first) | 0.350 | −0.087 | 4/11 | 0.12 |
| both (`chaewon-s01-swarm-dissolve`) | 0.300 | −0.138 | 4/15 | **0.019** |

## Falsifiers

- **H-prod fired.** Units at r100 stay at 12 in every arm (falsifier: < 15). Loosening the split rule does not add
  units: production is limited by pearl intake. On Trophy (every tile a slow bed) the v10 host eats 60 pearls in a
  game that sinbad-v07 eats 630 in; sinbad has 25 units at r75 to our 8.
- **H-dissolve fired.** Longest at r400 is 11–12 in the dissolve arms vs 10.5 in control (target ≥ 18), and the
  dissolve arms lose. Funnel per open-map game (both arm): 376 escort turns → 8.8 dissolves → 12.5 corpse pearls →
  8.1 eaten by the crown within 2 rounds → crown alive at r500 in 40/64 games → longest margin −4.3. Per corpse the
  recipient-first rule is efficient (65 % reaches the crown, vs 8–19 % for crash-feeding), but adjacency to a
  moving crown head is rare, so the volume is tiny while escorts give up hundreds of foraging turns. Crowns still
  die often (h2h, blind portal landings, boxed in by escorts); crown elections: ~21 per game.
- **H-cert inconclusive.** Newborn deaths ≤ 10 rounds fall 38.9 → 21.3 per 100 births with production+salvage+cert,
  but salvage relabels trapped wall/self deaths as deliberate noValidAction deaths, which the statistic excludes;
  the certificate was not ablated separately. First-pearl round did not fall (6 → 7).
  Delivery mechanics (new): the backward ray leaves the new tail along body[n+1]→body[n], so it reaches the child
  only if the body is straight at the cut (35–49 % of splits). Preferring straight cuts lifts it to ~46 % of births
  overall (salvage splits cannot choose).

## Other findings

1. **Newborn neck bug (v10 and yuna hosts).** A split child's segments keep the parent's facings, so body
   reconstruction by facing fails and the newborn believes its neck is free. Link by adjacency (fixed in all chaewon
   bots).
2. **Portal pockets on Portals.** 1-cell bed pockets reachable only through a portal kill any dragon ≥ 2 long; v10
   loses ~190 dragons per Portals game to self-collisions, mostly there, fed by exploration dives into unpaired
   portals.
3. **Portal steps are the biggest killer in the yuna family.** yuna-v05 vs sinbad on Default: 47 of 89 deaths are a
   first step through a portal into a body/head (sinbad 15). A solo sonar ray cast through the adjacent portal
   (echo attributable to that ray alone) tells next turn whether a dragon stands on the far line.
4. **Atlas.** Shipping the ten public maps' terrain and loading it on an exact first-view match: +0.15 on the v10
   host (s02 vs s01, 20 fixtures), +0.25 on yuna-v02 (y01, 20 fixtures), ±0 on yuna-v05 (y02, 32 fixtures).
   Adding bed-rate expectations and rich-sector far targets (y03) is −0.16: rejected.

## What s02 / next should change

- Stop building on the v10 host: against the current local band it scores 0.15–0.30 (yuna-v02, sinbad-v07).
- Do not move production or conversion clocks on any host until pearl intake is fixed; pursue economy and survival
  (portal probes, blind-landing pricing) on the yuna-v05 host (`chaewon-y04-probe`).
- If conversion is revisited: dissolve at distance ≤ 2 from any longer allied head (Vibing's rule) rather than
  escorting to one crown; escorts are the cost.
