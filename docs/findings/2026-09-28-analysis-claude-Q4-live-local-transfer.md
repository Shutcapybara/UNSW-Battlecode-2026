---
id: A1-Q4-live-local-transfer
author: claude/analysis/session-01KHqE
kind: observation
title: The local ledger cannot calibrate the live sources — 18–68 games each, no common opponents, no local opponent that produces a live-like swarm
task: A1 statistics analysis (handoff §3.4)
supersedes: D-010's "band mean 0.41" expectation model is confirmed as the only defensible one; supersedes the handoff's assumption that trajectory matching is feasible on today's data
evidence: game_stats.parquet (126,100 games, 12:10Z) joined to the live record through legacy fingerprints (`build/a1_source_map.json`: 9508→fenrir-v18-arrival-ready-beds, 8540→bifrost-v01-portal-memory, 9639→ein-dog-v02-momentum, 9663→yuna-v02-core, 9980→tidus-t02-spread-only, 10013→yuna-v03-core); per-round series of 7 comparison runs (`build/a1_local_series.csv`, 3,246 rows; `tools/analysis/scan_runs.py`); `tools/analysis/transfer.py`
---

**Units:** game (ledger outcomes), game (live), (map, opponent) cell for paired deltas, run × opponent for trajectories.
Local rows are native mode, live-pool maps only; live rows are verified controlled A-side.

## (a) Absolute calibration: local overstates live for 6 of 6 sources

| source | local bot | local n (opponents) | local share | live n | live share | live − local |
|---|---|---:|---:|---:|---:|---:|
| 9508 | fenrir-v18-arrival-ready-beds | 48 (24) | 0.562 | 143 | 0.441 | −12 pp |
| 8540 | bifrost-v01-portal-memory | 18 (9) | 0.500 | 51 | 0.431 | −7 pp |
| 9639 | ein-dog-v02-momentum | 58 (29) | 0.431 | 52 | 0.288 | −14 pp |
| 9663 | yuna-v02-core | 52 (26) | 0.558 | 70 | 0.414 | −14 pp |
| 9980 | tidus-t02-spread-only | 68 (15) | 0.721 | 49 | 0.367 | −35 pp |
| 10013 | yuna-v03-core | 44 (22) | 0.614 | 20 (dev only) | 0.500 | −11 pp |

The whole 126k-game ledger holds only 18–68 native games per live source on the live maps (0 on Portals and Slithery
Fight for every one of them; the ledger has 40 games on each of those maps in total), all against our own lineages.
The live opponents are stronger than that panel by a margin that varies 7–35 pp between sources, so no linear map
local→live exists (Spearman of local share vs live share over the five field sources: +0.1). The largest map-level
gap is Prisoners Dilemma (local 0.88 vs live 0.12 for 9508; 0.88 vs 0.00 for 9663), where the server deals a
10-dragon version in 56 % of games that no local run has ever played (Q3).

## (b) Paired calibration is impossible on the current ledger

For the four screens, common (map, opponent) cells between candidate and control bots in the ledger: 8540 vs 9508
**0**, 9639 vs 9508 **0**, 9663 vs 9508 **4** (two maps), 9980 vs 9663 **1**. The rule "local scores may enter the
priority score after ≥ 70 % paired sign agreement on ≥ 10 pairs" cannot even be evaluated; `calibration.py`'s paired
rows will stay empty until a panel is played on purpose.

## (c) Trajectory matching: no local opponent induces what the live opponents induce

Per-round series exist for two of the six sources (ein-dog and tidus-t02 as candidates, 7 comparison runs, unswbc
1.0.0, native, random seeds). Medians of (our units r100, their units r100, our total r250, their total r250, our and
their longest r400), live vs the nearest local opponent (standardised Euclidean distance, local opponents with ≥ 4
games on the live maps):

| live opponent (source 9639) | live profile: units r100 / total r250 / longest r400, ours vs theirs | nearest local opponents (distance) |
|---|---|---|
| 62/9343 | 2.5 v 20 / 0 v 67 / 0 v 7.5 | gavroche-v32 (4.8), gavroche-v17 (5.6) |
| 545/9571 | 11 v 23.5 / 24 v 96.5 / 6 v 14 | gavroche-v16 (4.7), gavroche-v17 (4.9) |
| 470/6350 | 10.5 v 18.5 / 46 v 80.5 / 6 v 5.5 | gavroche-v32 (2.0) |
| 45/9433 | 15.5 v 17.5 / 54 v 69.5 / 8 v 5.5 | scholze-v05 (1.9), gavroche-v17 (2.2) |
| 752/3887 | 11 v 21 / 32.5 v 52.5 / 6 v 5 | gavroche-v32 (2.5) |

The 28 local opponents ein-dog faced produce 7–16 units at r100 and 14–68 total at r250; the live opponents produce
17.5–23.5 units and 52–103 total. The closest local proxies for 470/45/752 are gavroche-v32 and scholze-v05 at ~2
standardised units, and nothing is within 4.7 of Heartbreaker (62) or dev test 1 (545). tidus-t02's four local
opponents (ouroboros-v13, leviathan-v09, avery-v08, porthos-x04) are all ≥ 1.5 away from every live opponent and it
beat them 0.80–1.00 while scoring 0.10–0.70 live. **Opponent-proxy table:** live 45 ≈ local gavroche-v32 /
scholze-v05 (weak match); live 62, 545, 470: no proxy exists in the ledger.

## (d) Toolkit strata

The ledger's live-map games are 1.0.0 native (99 %); 1.2.1 rows exist only for autarky/QoS/schooltime/trauma (216–256
each) and 40 per map for portals/slithery/devil/trophy/dilemma; none of the six source bots has any 1.2.x game. The
toolkit comparison in §3.4(b) of the handoff cannot be made on existing data.

## Decision

Keep local scores out of the priority score (D-010 stands). Build the live-pool panel (research item 1) with
**swarm-heavy references first** — the S1 m01 Vibing mimic, gavroche-v32, and clones of 62 and 545 — because the
present references do not exercise the failure mode (being out-produced by 20+ units at r100) that decides live games.
Add a 10-dragon Prisoners Dilemma to the map set.

## Falsifier

A local reference whose induced profile against one of our bots lies within 1.0 standardised units of a live
opponent's on ≥ 10 games per map class, or five sources with residual SD < 8 pp on a live = a + b·local fit.
