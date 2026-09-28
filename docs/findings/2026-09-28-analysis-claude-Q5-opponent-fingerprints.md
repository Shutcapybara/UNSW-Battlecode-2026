---
id: A1-Q5-opponent-fingerprints
author: claude/analysis/session-01KHqE
kind: observation
title: The live record already fingerprints six opponents; the screen panel is off-band (ranks 6/40/59) and the band itself has never been profiled
task: A1 statistics analysis (handoff §3.5)
supersedes: nothing (the band corpus does not exist locally; no download was performed — downloads need explicit authorisation)
evidence: opponent_stages of 435 verified A-side games in LIVE/state/state.json; LIVE/state/ladder.json (901 teams, 12:12Z); `tools/analysis/a1_report.py §Q5`
---

**Unit:** game; medians per opponent submission over our A-side games (all our sources pooled — the opponent's
numbers depend on who it played, so treat them as "against JKS-class bots").

| team (ladder name, rank, Elo) | submission | n | our share | units r100 / r250 | total r250 | longest r320 / r400 / r499 | peak units | splits | rays per turn | h2h / wall / self deaths per 1k | newborn ≤10 | portal steps | sprints | eliminated us |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---|---:|---:|---:|---:|
| 62 Heartbreaker (40, 1825) | 9343 | 103 | 0.32 | 19 / 26 | 78 | 8 / 9 / 10 | 34 | 80 | 3.95 | 11.1 / 7.2 / 0.1 | 21 | 45 | 7.5 | 60 |
| 45 WeLikCoding (59, 1764) | 9433 | 90 | 0.54 | 16 / 17.5 | 52 | 5 / 5 / 18 | 26 | 124 | 0.54 | 7.1 / 9.4 / 1.5 | 36 | 86 | 9 | 13 |
| 752 dev test 2 (85, 1712) | 3887 | 80 | 0.66 | 13 / 19 | 47 | 4 / 4 / 7 | 29.5 | 131.5 | — (no sonar) | 7.9 / 7.5 / 2.3 | 34 | 11 | 10 | 23 |
| 470 龙虎豹 (6, 2039) | 6350 | 72 | 0.32 | 14.5 / 36 | 89 | 4 / 5 / 18.5 | 43 | 154.5 | 1.10 | 4.2 / 6.1 / 3.5 | 41 | 26.5 | 14 | 22 |
| 545 dev test 1 (15, 1960) | 9571 | 55 | 0.18 | 21 / 37 | 97 | 7 / 10 / 15 | 42 | 192 | 3.83 | 4.0 / 11.1 / 1.9 | 57 | 51 | 6 | 28 |
| 545 dev test 1 (15, 1960) | 9371 | 25 | 0.16 | 22 / 41 | 97 | 5 / 6 / 15 | 47 | 144 | 1.27 | 6.0 / 6.7 / 4.8 | 34 | 35 | 12 | 10 |
| 306 Cutlery (1, 2147) | 6985 | 10 | 0.50 | 11.5 / 28.5 | 66.5 | 3 / 4 / 4 | 29.5 | 89.5 | 2.45 | 4.9 / — / 0 | 12.5 | 21 | 12 | 5 |

Our sources on the same measures: units r100 9–14, r250 10–21; total r250 27–51; longest r499 3–13; peak units 17–27;
splits 80–137; h2h deaths 8–12 per 1k; wall 3.7–8; self 2.8–5.9.

## Clusters (behavioural, from these seven rows)

1. **Early swarm + mid-game conversion** — 62 (Heartbreaker) and both 545 versions: 19–22 units by r100, 78–97
   total by r250, longest 7–10 at r320–r400, and very low self-collision rates (0.1–1.9 per 1k: exact simulation).
   They eliminate us (60 + 28 + 10 eliminations). 62 sends 4 rays/turn; 545/9571 also 3.8 — the same sonar-heavy
   style as our lines.
2. **Big late swarm, length race** — 470: modest r100 (14.5) but 36 units / 89 total at r250, peak 43, most splits,
   lowest h2h death rate (4.2), longest 18.5 at r499. Wins on the round limit.
3. **Mid swarm, few rays, portal-heavy** — 45: 16 units r100, 0.54 rays/turn, 86 portal steps, longest 18 at r499
   only through late growth (5 at r400). Beatable (0.54) and the only screen opponent near our band.
4. **No sonar at all** — 752 (dev test 2): 13 units r100, 0 rays; beaten 0.66.
5. 306 (Cutlery, rank 1, 10 games only) plays small (29.5 peak, 89.5 splits) and still holds 0.50 against 9508 with
   the lowest h2h rate — an evaluator, not a swarm; too few games to place.

## The band has no data

Our rating is decided by ranks 60–76 (534, 875, 473, 485, 241, 75, 47, 790, 19, 406, 347, 74, 722, 522, 977, 133 at
12:12 UTC). None of them appears in the controlled record; six of them (790, 75, 19, 977, 133, 406) appear only as
ranked-series opponents in `seen_series` (5-game series requested by their members or by the 2-hourly autoscrim),
whose replays were not harvested. The screen panel [62, 45, 470] is ranks 40/59/6 — two opponents far above the band.
Elo-wise the band (1724–1764) is bracketed by 45 (1764) and 752 (1712).

## Recommendation for the six clone representatives (pending the band corpus)

Until the band replays are downloaded (≤ 60 newest per team, authorisation needed), clone what we have and what is
band-like: (1) 62/9343 — the elimination specialist, cluster 1; (2) 545/9571 — cluster 1 with the largest r250
material; (3) 470/6350 — the length racer; (4) 45/9433 — the band-like mid swarm; (5) 752/3887 — the no-sonar baseline;
(6) one band team once profiled (790 "Yyy" or 133 "Jingling Munmin", both of which played ranked series against us
today). Teammate uploads to recover as local opponents: 9508 (fenrir-v18) is already recovered as `bifrost-v18-control`
and fingerprint-matched to `bots/fenrir-v18-arrival-ready-beds`; 9943 (Heimdall v10, the 08:13–08:41 incumbent) and
9808 have no recovered source under `LIVE/candidates/` (whether a `bots/` directory matches them is unverified — the
API zips are the only proof) and should be recovered next.

## Decision

Re-balance the screen panel toward the band: keep 45, replace 470 with a band team once its replays are profiled,
keep 62 as the elimination stress test. Do not read the screen share as a rating proxy while two of three screen
opponents sit 20–60 ranks above the band.

## Falsifier

A profiled band corpus in which the band teams' r100/r250 material lies within the cluster-1 range (then 62/545 are
the right screen, and the band is harder than it looks).
