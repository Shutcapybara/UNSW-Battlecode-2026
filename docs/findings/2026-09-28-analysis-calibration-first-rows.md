---
id: 2026-09-28-analysis-calibration-first-rows
author: glm/analysis/a1
kind: observation
title: "First live-vs-local calibration rows: local ledger shares are optimistic by 8–38 pp on every source; toolkit strata have zero overlap; trajectory matching lacks local stage data for 5 of 6 bots"
task: "A1 §3.4 — live-versus-local transfer"
supersedes: []
evidence: "Offline run of the new tools/hub/calibration.py (2026-09-28 22:1x local) against a snapshot of battlecode-hub/hub.sqlite; ledger = game_stats.parquet restricted to live-pool maps, native mode (69,260 rows); 6 of 8 live submissions map to repo bots via fingerprints. Unit = source for absolute rows, cell for paired rows."
---

# (c) Map-level disagreement — the first absolute rows

| submission | bot | local n (share) | live n (share) | live − local |
|---|---|---|---|---|
| 9508 | fenrir-v18-arrival-ready-beds | 49 (0.571) | 123 (0.431) | **−14.0 pp** |
| 9663 | yuna-v02-core | 52 (0.558) | 50 (0.400) | **−15.8 pp** |
| 9639 | ein-dog-v02-momentum | 58 (0.431) | 32 (0.312) | **−11.9 pp** |
| 8540 | bifrost-v01-portal-memory | 18 (0.500) | 31 (0.419) | **−8.1 pp** |
| 9980 | tidus-t02-spread-only | 68 (0.721) | 29 (0.345) | **−37.6 pp** |

Every source's local share exceeds its live share. Worst map-level cells: tidus on Queen Of Spades (local 100% → live 0%, −100 pp), yuna-v02 on Dilemma (−88), ein-dog on Autarky (−75). The expectation model is still band-mean (live ≈ 0.372 for any local number; n=4 sources with enough games — needs 5).

**Why the hub never produced these rows**: the deployed hub (app/current, revision stamped 09:21 UTC) predates the calibration-enabled cycle.py; the newer tools/hub code was never deployed. The empty calibration table is a deployment gap, not a data gap.

# (b) Toolkit strata — unanswerable today

Zero (bot_a, bot_b, map) cells have ≥3 games in both 1.0.x-native and 1.2.x-native strata (ledger: 119k games on 1.0.0, 4.5k on 1.1.0, 1.7k on 1.2.1 — disjoint bot pairs). No statement about toolkit equivalence is possible from the ledger; it needs the deliberate strata replay (research list).

# (a) Trajectory matching — machinery shipped, data thin

Per-round series exist in comparison-run stats/*.json (units/total/longest per round, both sides), but only tidus-t02 has comparison runs (2 dirs, 74 games); the other five mapped bots have none. The live-side opponent fingerprints (62/45/470/306, field) are computed and now in the hub packet via `opponent_fingerprints`; the local-side matching needs the live-pool panel (§4 item 1).

# The priority-score rule

`local_priority_ok` (hub) implements the ≥70% sign agreement on ≥10 paired blocks gate. Current paired rows: 1 (yuna-v03 vs fenrir-v18, 1 common cell). **The rule is far from satisfied — local paired deltas must NOT enter the priority score today.**

**Decision fed**: (1) deploy the current tools/hub so calibration rows start flowing (the code is done); (2) reference-set use of local scores stays blocked by the gate; (3) the reference panel for live-pool local runs should include bots that LOSE like we do on QoS/Dilemma/Autarky — the −75-to-−100 pp cells are where local evidence is most misleading.

**Falsifier**: after deployment, a week of calibration rows where |live − local| ≤ 5 pp on ≥5 sources with n≥30 each (then local absolute shares become usable priors); or a paired-block history reaching the 10-pair gate with ≥70% agreement (then local paired deltas enter priority).
