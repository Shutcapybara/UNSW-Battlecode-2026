---
id: gpt-eunchae-s03-swarm-dissolve
author: gpt/eunchae/2026-09-28-s03
kind: observation
title: Eunchae S03 local iteration
task: S1 swarm-dissolve iteration
supersedes: gpt-eunchae-s02-swarm-dissolve
evidence:
  - "unswbc 1.0.0 sandbox Portals: candidate B lost by length at round 500; p99 37.0M and max 46.2M over 5,859 candidate turns; one candidate no-valid-action event at r322; no CPU faults."
---

Change: retain moderated production; lower split danger threshold to 0.20 and local crowd allowance to 6.

Test: one unpaired local control match on Portals. Candidate lost by length. It emitted all intended mechanism markers, including three dissolves, and stayed under the CPU cap. One candidate `no valid action` appeared at r322 during the donor phase. It may be the intended no-command death after a recipient-first dissolve; confirm against a replay before treating it as a fault. The measured result does not establish H-prod, H-dissolve, or H-cert.
