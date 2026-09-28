---
id: gpt-eunchae-s02-swarm-dissolve
author: gpt/eunchae/2026-09-28-s02
kind: observation
title: Eunchae S02 local iteration
task: S1 swarm-dissolve iteration
supersedes: gpt-eunchae-s01-swarm-dissolve
evidence:
  - "unswbc 1.0.0 sandbox Schooltime: candidate A lost by elimination at round 332; p99 40.1M and max 46.6M over 3,039 candidate turns; no reported faults."
---

Change: small map target lowered from 64 to 40; mid 48; large 60.

Test: one unpaired local control match on Schooltime. The candidate lost by elimination at round 332. Its CPU was within the budget. No paired delta or replay-derived swarm statistics are available; H-prod remains untested. Markers: 42 production, 23 salvage, 10 crown, 32 certificate. No escort or dissolve markers occurred before elimination.
