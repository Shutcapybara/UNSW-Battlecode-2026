---
id: A1-Q2-paired-contrasts-v2
author: claude/analysis/session-01KHqE
kind: observation
title: None of the four rejected screens is distinguishable from zero; when a pair flips, it flips on r250 material
task: A1 statistics analysis (handoff §3.2)
supersedes: the screen "net −2" verdict numbers are reproduced, not superseded; supersedes A1 memo item 4 (gpt-6) "exact matched contrasts have not been reconstructed" — they are, below and in the hub
evidence: LIVE/state/state.json blocks/results (12:12Z); `tools/hub/analysis_a1.paired_contrast` (hub, every cycle) and `tools/analysis/a1_report.py §Q2`; pairs on (block, map, API side, opponent submission, map_hash)
---

**Unit:** exact pair — one candidate and one control game inside the same screen block on the same map, API side,
opponent submission and starting layout (`map_hash`). Nothing unpaired is pooled. Sign tests are exact two-sided
binomials on discordant pairs. All arms are side A.

| experiment | candidate − control | pairs (unpaired c/k) | cand share | ctrl share | paired Δ | better / same / worse | sign-test p | Δ by class (n) | Δ by opponent (n) |
|---|---|---|---:|---:|---:|---|---:|---|---|
| a01aee66 | 8540 − 9508 | 30 (1/1) | 0.40 | 0.47 | −0.067 | 4 / 20 / 6 | 0.75 | compact 0.00 (12), open −0.11 (18) | 45 0.00 (10); 62 −0.10 (10); 470 −0.10 (10) |
| 8b12ae55 | 9639 − 9508 | 30 (2/2) | 0.33 | 0.40 | −0.067 | 4 / 20 / 6 | 0.75 | compact +0.17 (12), open −0.22 (18) | 45 0.00; 62 0.00; 470 −0.20 |
| 02356998 | 9663 − 9508 | 19 (1/1) | 0.53 | 0.53 | 0.000 | 3 / 13 / 3 | 1.00 | compact +0.14 (7), open −0.08 (12) | 45 +0.11 (9); 62 −0.10 (10) |
| 88a5b9be | 9980 − 9663 | 17 (12/13) | 0.41 | 0.47 | −0.059 | 1 / 14 / 2 | 1.00 | compact +0.17 (6), open −0.18 (11) | 45 −0.11 (9); 62 0.00 (8) |

The 470 block of 88a5b9be paired 0 of 10 maps (opposite layouts in every game — see Q3) and is excluded, hence 12/13
unpaired.

## Stage-profile deltas on the same pairs (median / mean)

| experiment | units r100 | total r250 | longest r400 | longest r499 | deaths | h2h deaths | newborn ≤10 | splits | sonar rays | cpu max (M) | faults |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 8540 − 9508 | 0 / −0.5 | 0 / −1.4 | 0 / −1.1 | 0 / 0.0 | −2.5 / −7.4 | +1 / −8.4 | −2 / −0.9 | −2.5 / −7.6 | −228 / −1958 | −25.3 / −25.8 | 0 / −7.0 |
| 9639 − 9508 | 0 / −1.3 | 0 / −4.1 | 0 / +0.1 | 0 / −0.2 | −5.5 / −7.9 | −2.5 / −5.3 | −5 / −3.5 | +7 / −7.8 | −5574 / −7683 | −28.4 / −28.6 | 0 / −7.0 |
| 9663 − 9508 | +3 / +3.5 | +5 / +7.6 | 0 / +1.1 | 0 / −1.4 | +21 / +10.8 | +8 / +11.1 | +6 / −13.5 | +21 / +9.5 | +4436 / +5673 | −19.0 / −17.0 | 0 / −8.2 |
| 9980 − 9663 | −1 / −0.7 | 0 / −10.0 | 0 / +1.1 | 0 / +1.9 | −3 / −0.4 | −2 / −8.9 | +2 / +9.5 | −3 / −4.1 | −4470 / −11762 | −3.8 / −3.9 | 0 / 0 |

Three candidates removed 17–29 M points of peak runtime and all of 9508's TLE faults (−7 to −8 per game) and won
nothing by it: runtime is not what decides these games (Q6). yuna-v02 produced more (+3 units r100, +5 total r250)
and died more (+21 deaths, +8 h2h per game) for a net of exactly zero.

## What changed when the outcome changed

29 discordant pairs in all. In 26 of them the sign of the r250 total-length difference agrees with the sign of the
outcome difference (8/10, 9/10, 6/6, 3/3). The longest-at-r499 sign agrees in 20 of 29. Flips are therefore
material flips at r250, not conversion flips — the same mechanism as Q1. Typical flip rows (Δ total r250): 8540 −
9508 on Trophy −62 (candidate eliminated), 9639 − 9508 on Default vs 62 −80, on QoS vs 470 −67; the rare gains are
of the same size in the other direction (9663 on Devil vs 45 +84).

## Power of the instrument

With 30 pairs and ~1/3 discordance the sign test only rejects at 9/10 or 10/10 discordant pairs one way, i.e. a paired
delta of about ±0.25 or more. The four screens (Δ −0.07 to 0) were never going to reject or promote anything of the
size lineages actually produce (±0.05–0.10). This is a statement about the screen design, not about the candidates.
A 60-pair screen (both layouts per map via the Q3 request pattern, 3 opponents) halves the detectable delta.

## Decision (mechanism ledger)

Stop re-testing: (1) runtime repairs alone (9573/9604 lineage, and the 8540 recovery) — removing TLE faults does not
move outcomes; (2) whole-policy transfers whose local signature is "fewer deaths" (9639, 9980) — on live pairs they
lose material at r250 on open maps against 470/45. Keep testing only mechanisms that raise r100 units / r250 total on
compact maps, and size the screen at ≥ 60 pairs.

## Falsifier

A future exact-pair screen in which ≥ 30 % of flips have the r250 sign disagreeing with the outcome sign, or a
candidate that wins a screen at p < 0.05 with a median Δ total r250 ≤ 0.
