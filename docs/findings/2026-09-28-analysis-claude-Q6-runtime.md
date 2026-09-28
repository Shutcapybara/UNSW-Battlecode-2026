---
id: A1-Q6-runtime-v2
author: claude/analysis/session-01KHqE
kind: observation
title: Only the teammate incumbent is at the cap; every executor upload has 17–23 M of headroom; the local probe set misses the Slithery Fight peak
task: A1 statistics analysis (handoff §3.6)
supersedes: A1-Q6-runtime-headroom (gpt-6; field pool only, no map/stage/fault decomposition, no probe data)
evidence: cpu_max / faults / stage cpu_max of 425 verified controlled A-side games (LIVE/state/state.json 12:12Z); per-turn points of 10 probe logs (`LIVE/state/runtime/<candidate>/{9-A,20-B}.log`, 160k dragon-turns, parsed by `tools/analysis/probe_turns.py`, summarised in `build/a1_turns_*.csv.gz`); `tools/hub/analysis_a1.runtime_table`
---

**Units:** game for the live table (cpu_max is the game maximum over all our dragon-turns; `cpu_recorded == turns`
in all 425 games, so the maximum is complete), dragon-turn for the probe table.

## Live game maxima (M points)

| source | n | p50 | p90 | max | games > 90 M | games at cap | TLE faults (games with faults) | map maxima ≥ 80 M |
|---|---:|---:|---:|---:|---:|---:|---|---|
| 9508 fenrir-v18 (teammate) | 143 | 93.6 | 100 | 100 | 81 | 69 | 1096 (69) | all ten maps 87.5–100 |
| 9663 yuna-v02 | 70 | 69.5 | 79.8 | 97.5 | 3 | 0 | 0 | Slithery Fight 97.5 |
| 9573 / 9604 fenrir-v18 repairs | 20 / 20 | 71.5 / 70.0 | 78.9 / 77.3 | 82.5 / 82.4 | 0 | 0 | 0 | Portals 82.5 / 82.4 |
| 9639 ein-dog-v02 | 52 | 62.0 | 72.8 | 79.7 | 0 | 0 | 0 | — |
| 8540 bifrost-v01 | 51 | 62.6 | 73.5 | 79.7 | 0 | 0 | 0 | — |
| 9980 tidus-t02 | 49 | 64.7 | 71.0 | 77.5 | 0 | 0 | 0 | — |
| 10013 yuna-v03 | 20 | 64.0 | 76.3 | 77.9 | 0 | 0 | 0 | — |

9508's faults are map-specific: Portals 518 TLE turns (37 per game, up to 50), Slithery Fight 213 (15/game), Trauma
201 (14/game), Devil 132 (9/game); Default, Trophy, QoS, Autarky, PD ≤ 3 in total. In 49 of its 69 capped games the
cap is first hit by r100, in 15 more by r200. These are the two portal-dense maps plus the two with the most dragons —
cost scales with what is on the board (below), and the 100 M cap is hit by newborn/portal search paths that the
repairs 9573/9604 removed.

**Faults do not lose games.** Within 9508, games with more faults have a *higher* win share (0 faults: 0.28, n=74;
1–5: 0.50; 6–20: 0.60; 21–60: 0.75, n=20) and fewer elimination losses — because faults happen when the swarm is
large and alive late; games lost early have no faults. Survivorship, not causation; but it rules out TLE as a driver
of the loss mode (Q1), and the exact pairs of Q2 confirm it (−7 faults/game, Δ outcome 0).

## What the judge sandbox charges (probe logs, unswbc 1.0.0, 160,234 dragon-turns)

| candidate | fixture | dragon-turns | p50 | p99 | max | rays/turn |
|---|---|---:|---:|---:|---:|---:|
| bifrost-v18-control (= 9508 source) | Schooltime A / Portals B | 21,928 / 6,721 | 17.8 / 19.5 | 47.6 / 50.5 | 94.5 / 93.0 | 3.97 / 3.95 |
| yuna-v02 | Schooltime A / Portals B | 24,029 / 10,569 | 18.1 / 20.5 | 45.4 / 53.4 | 57.7 / 74.4 | 4.00 |
| yuna-v03-core | Schooltime A / Portals B | 23,262 / 8,217 | 17.5 / 19.7 | 46.3 / 50.8 | 58.1 / 68.8 | 4.00 |
| ein-dog-v02 | Schooltime A / Portals B | 24,881 / 9,172 | 26.8 / 26.7 | 50.0 / 51.4 | 68.7 / 66.6 | 3.02 / 3.91 |
| tidus-t02 | Schooltime A / Portals B | 23,237 / 8,218 | 28.8 / 28.8 | 52.5 / 54.0 | 73.3 / 70.8 | 3.01 / 3.96 |

Within-fixture OLS of points on (rays sent, round, living dragons on the board): **a ray costs −0.6 to +1.2 M with
standard errors of the same size (R² 0.02) — indistinguishable from zero**; each living dragon on the board adds
0.08–0.16 M per turn (60 dragons ≈ +5–10 M); the round adds ≤ 0.006 M. The expensive turns are the exception
fall-back turns of 9508's source (turns whose stdout starts with a LOG line: median 37.6 M, max 94.5 M, vs 19.5 M for
ordinary MOVE turns) — 2 of its 3 probe turns above 90 M are of that kind.

## Live vs probe

For the four executor uploads probed on Portals B, the live A-side Portals maximum exceeds the probe maximum by
+5.1 M (9573/9604: 82.5 vs 77.4) or is below it (9980 72.3 vs 70.8; 9663 71.3 vs 74.4) — the probe is a fair estimate
of the live peak *on the probed map*. It is not on unprobed maps: yuna-v02's live peak of 97.5 M came on Slithery
Fight (14 starting dragons, 63×27), a map the fixture set (Schooltime A, Portals B) never runs; its probe maximum was
74.4 M.

## Decision

Keep the local gate at 80 / 60 M and add **Slithery Fight A** (largest unit count) and **Trauma** to the probe
fixtures; a Python host needs a degradation mode only if its p99 exceeds ~60 M on those fixtures (no executor upload
does; 9508 does). Do not spend candidates on runtime repairs of 9508 — the repairs (9573/9604) already exist, pass
the gate, and did not change outcomes (Q2).

## Falsifier

An executor upload that passes the extended probe set and still records a game above 95 M live, or a fault-free
candidate that beats 9508 in exact pairs by ≥ +0.15 on the four fault-heavy maps only.
