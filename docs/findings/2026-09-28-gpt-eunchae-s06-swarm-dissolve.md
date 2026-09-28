---
id: gpt-eunchae-s06-swarm-dissolve
author: gpt/eunchae/2026-09-28-s06
kind: observation
title: Eunchae S06 local iteration
task: S1 swarm-dissolve iteration
supersedes: gpt-eunchae-s05-swarm-dissolve
evidence:
  - "unswbc 1.0.0 sandbox Default: candidate A was eliminated at round 337; p99 40.6M and max 54.4M over 2,410 candidate turns; no CPU faults."
---

Change: retain prior changes; reduce production cutoff to round 80 and raise danger threshold back to 0.25.

Test: one unpaired local control match on Default. Candidate was eliminated at round 337 and stayed below the CPU budget. Only 18 production and 8 certificate markers appeared, with no escort or dissolve. H-prod remains unverified; the r80 production cutoff may be too early, but this single game cannot isolate that effect.
