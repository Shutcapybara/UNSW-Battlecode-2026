---
id: gpt-eunchae-s05-swarm-dissolve
author: gpt/eunchae/2026-09-28-s05
kind: observation
title: Eunchae S05 local iteration
task: S1 swarm-dissolve iteration
supersedes: gpt-eunchae-s04-swarm-dissolve
evidence:
  - "unswbc 1.0.0 sandbox Queen of Spades: candidate B lost by length at round 500; p99 35.4M and max 41.3M over 2,233 candidate turns; no candidate faults."
---

Change: retain prior changes; limit donor length to 2 and escort range to 20.

Test: one unpaired local control match on Queen of Spades. Candidate lost by length at round 500 and stayed below the CPU budget. The donor cap/range change produced no dissolve activation, so it has not tested the intended delivery mechanism. No paired delta or H-dissolve funnel is available.
