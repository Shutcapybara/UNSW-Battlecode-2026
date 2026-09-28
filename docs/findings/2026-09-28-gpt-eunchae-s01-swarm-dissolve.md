---
id: gpt-eunchae-s01-swarm-dissolve
author: gpt/eunchae/2026-09-28
kind: observation
title: Initial swarm and recipient-constrained dissolve candidate
task: S1 swarm-dissolve iteration
supersedes: ""
evidence:
  - "Local unswbc 1.0.0 sandbox probe: Schooltime, candidate as A vs sinbad-v07, 325 rounds; candidate CPU p99 34.2M, max 42.4M over 1,613 turns; no reported faults."
  - "Local unswbc 1.0.0 sandbox probe: Portals, candidate as B vs sinbad-v07, 500 rounds; candidate CPU p99 34.8M, max 43.2M over 5,371 turns; no reported faults."
  - "Paired seeded panels and replay-derived statistics not yet available."
---

## What changed

Created a new `gpt/eunchae` candidate from ouroboros-v10-beacon. It raises all size-class unit targets to 64, limits voluntary production to round 100, uses two-segment children, begins crown selection at round 250, and conditions the feed onset on the fixed public map dimensions for Portals and Slithery Fight. A donor now dissolves only when it is adjacent to a fresh directly sensed crown, which must be longer; donors farther away use the inherited target steering.

## Falsifiers

- **H-prod:** not evaluated. The one Schooltime sandbox run does not produce replay-derived units at round 100 or death rates.
- **H-dissolve:** not evaluated. No conversion funnel, recipient survival, or longest-at-400 statistic is available.
- **H-cert:** not evaluated. The host's backward-ray handoff remains, but its packet is not the complete proposed birth-certificate layout; no first-turn delivery check or newborn ablation was run.

The activation tags appeared in both probe logs. Schooltime emitted 24 production, 2 salvage, 2 crown, and 10 certificate markers. Portals emitted 56 production, 102 salvage, 116 crown, 96 escort, 4 dissolve, and 59 certificate markers. The candidate lost both probes (Schooltime by elimination; Portals by length). No win-rate or paired delta is claimed. The installed toolkit is unswbc 1.0.0. A temporary pip install for 1.2.2 returned “No matching distribution found”, so the requested seeded panel could not run. These unpaired probes are not evidence of live strength.

## Next version

Run on unswbc 1.2.2 with the complete paired panel and the prescribed 2×2 subset. Decode replay funnel and survival metrics before changing onset. Implement the full certificate payload and an explicit target hysteresis layer only if the matching ablations show value. Confirm the map signature classification and collect the Portals B CPU probe.
