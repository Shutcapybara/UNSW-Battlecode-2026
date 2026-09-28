---
id: A1-Q10-rating-table
author: claude/analysis/session-01KHqE
kind: correction
title: The campaign table's top 62 are all Sparse, four of its top-18 bots score 0.29–0.44 live against local 0.75–0.79, and shrinkage does not restore rank order — the table must not order the queue
task: A1 statistics analysis (handoff §3.10)
supersedes: D-002's use of "tops the local table" as a registration argument for tidus-t02; A1 memo item 5 (gpt-6) — the ledger was read here
evidence: experiment_data/bot-ratings/latest.json (12:07Z, 280 active bots, 108,339 fixtures), live shares from the Q1 tables; `tools/analysis/ratings_sanity.py`
---

**Units:** bot version (rating), game (live share). Local scores are the model-adjusted predicted share against the
reference panel; "Sparse" is the table's own flag (< 60 fixtures, < 5 opponents, < 8 maps, or < 80 % of the map weight).

## The evidence

| local rank | bot | local score | fixtures / opponents / maps / map-weight coverage | flag | live field share (n) | live all-controlled share (n) |
|---:|---|---:|---|---|---:|---:|
| 1 | fenrir-v18-arrival-ready-beds (= 9508) | 0.794 | 82 / 41 / 13 / 0.50 | Sparse | 0.431 (123) | 0.441 (143) |
| 9 | tidus-t02-spread-only (9980) | 0.771 | 110 / 25 / 12 / 0.46 | Sparse | 0.345 (29) | 0.367 (49) |
| 11 | ein-dog-v02-momentum (9639) | 0.765 | 98 / 49 / 13 / 0.50 | Sparse | 0.312 (32) | 0.288 (52) |
| 18 | yuna-v02-core (9663) | 0.747 | 86 / 43 / 13 / 0.50 | Sparse | 0.400 (50) | 0.414 (70) |
| 62 | yuna-v03-core (10013) | 0.693 | 76 / 38 / 13 / 0.50 | Sparse | — | 0.500 (20, dev only) |
| 236 | bifrost-v01-portal-memory (8540) | 0.545 | 34 / 17 / 11 / 0.42 | Sparse | 0.419 (31) | 0.431 (51) |

- The top 62 bots are all Sparse (map-weight coverage 0.42–0.53: the new lineages were only ever run on the
  13-map subsets, never on the 33-map campaign); the first Established bot is newton-x10-candidate at rank 63
  (0.693, 1,248 fixtures). 179 of 280 active bots are Sparse; the 101 Established bots have a mean score of 0.578
  (SD 0.07).
- Spearman correlation of local score with live field share over the five live-tested sources: **+0.10** (p = 0.87);
  the self-audit's −0.64 on seven earlier versions is not contradicted (different bots), the sign is simply not
  stable. The absolute inflation (local score − live share) is 11–48 pp.
- The table's own confidence ranges (middle 80 % of opponent-pair bootstraps) put fenrir-v18 at 0.74–0.82 — a range
  that excludes its live share by 30 pp. The ranges describe sampling noise inside the local panel, not transfer.

## Shrinkage does not repair it

A minimum-evidence rule plus shrinkage was applied as proposed by the handoff: n_eff = fixtures × map-weight coverage
× min(1, opponents/5) × min(1, maps/8); score_shrunk = (n_eff·score + k·μ)/(n_eff + k) with μ = 0.578 (Established
mean) and k = 60. The top of the table becomes tidus-t05-midcrowd (734 fixtures, 0.691), newton-x10 (1,248, 0.688),
witten-x02 (890, 0.680); the five live sources move to ranks 7, 5, 10, 31 and 224. Spearman with live share becomes
**−0.20** — shrinkage fixes the evidence tier, not the ordering, because the ordering error is panel bias (the
reference panel is our own weaker lineages, none of which produces the live opponents' 17–24 units at r100; Q4), not
sparsity.

## Proposed patch (for `tools/benchmark_ratings.py::summary`, keeping the model untouched)

1. Add columns `n_eff` and `score_shrunk` (formula above; μ and k printed in the header) and **sort the table by
   `score_shrunk`**; keep `score` visible.
2. Print a hard evidence tier: `Established` (existing rule) may be quoted in a registration argument; `Sparse` may
   not — the summary states this in its legend.
3. Add a `live` column joined from `hub-state/status.json` (live field share and n, when ≥ 10 games exist for a
   fingerprint-matched bot) so the disagreement is visible in the same row.

The patch is mechanical; it is not committed here because the score computation lives in
`benchmark_dashboard_data.py`, which this analysis did not have, and the ordering rule below makes the table's rank
irrelevant to the queue anyway.

## Decision

The campaign table may not order the queue. Queue priority uses (i) exact-pair live evidence, (ii) the seeded
live-pool panel once it exists (research item 1), (iii) lineage diversity — and quotes the local score only as a
Sparse/Established-tagged context number. D-010's band-mean expectation (0.41) stands as the prior for any new
upload.

## Falsifier

A version of the table (after the live-pool panel replaces the reference set) whose top-10 by `score_shrunk` reach
paired sign agreement ≥ 70 % with live exact pairs on ≥ 10 pairs.
