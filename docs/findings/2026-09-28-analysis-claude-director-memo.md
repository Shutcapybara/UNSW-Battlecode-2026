---
id: A1-director-memo-v2
author: claude/analysis/session-01KHqE
kind: observation
title: Director memo — five findings that change what is built or tested next, and three lineage claims that did not reproduce
task: A1 statistics analysis (handoff §5.5)
supersedes: A1 director memo v1 (gpt-6/analysis/codex-session, 12:14 UTC) — every item there is either reproduced with numbers below or resolved
evidence: docs/findings/2026-09-28-analysis-claude-Q1…Q10; docs/analysis/ATLAS.md §2; all numbers re-derivable with tools/analysis/{a1_report,transfer,ratings_sanity}.py
---

**As of 12:12 UTC, 446 verified live games (425 controlled A-side), 126,100 ledger games, 121 replay-driven live games.**
A second analyst (gpt-6/codex) wrote a shallower pass at 12:13–12:15 UTC; its files are untouched, its atlas and
research list are appended verbatim to v2, and its `tests/test_hub_analysis_a1.py` imports functions that are not on
`main` (it fails at import — retire it or restore its functions; not mine to delete).

## Five findings

1. **Change the request shape before the next screen (Q3).** The starting orientation is `f(map, game-id parity)` —
   446 of 446 games, 0 violations (unit: game) — and a 10-map batch is uniform, so two arms pair on all ten maps
   exactly when their first ids share parity, a coin flip set by other teams' traffic (the 09:22 blocks flipped twice
   on 1- and 5-game gaps). A 20-game request listing the maps as M0..M9, M1..M9, M0 gives both orientations per map
   in every batch: 20 exact pairs per opponent, no fills. Prisoners Dilemma is also dealt in two versions (6 or 10
   starting dragons, 22/28 of 50) that no local map reproduces. *Falsifier:* one verified game off the parity table
   (the hub now counts them every cycle), or a 20-game request returning < 10 cells per orientation.

2. **Screens of 30 pairs cannot see the effects lineages produce (Q2).** The four rejected/frozen screens are
   Δ −0.067, −0.067, 0.000, −0.059 with sign-test p 0.75–1.0 on 30/30/19/17 exact pairs (unit: pair); a 30-pair sign
   test rejects only at |Δ| ≳ 0.25. When a pair flips, it flips on r250 material (26 of 29 flips agree in sign with
   Δ total r250); removing 17–29 M of peak runtime and all TLE faults moved nothing. *Build:* size screens at ≥ 60
   pairs (finding 1 makes that affordable); stop re-testing runtime repairs and "fewer deaths" transfers.
   *Falsifier:* a candidate winning a screen at p < 0.05 with median Δ total r250 ≤ 0.

3. **Every source loses the same way, before r100 (Q1).** Losses are 60 % eliminations (74 % on compact maps),
   median compact elimination round 122–158 (unit: game; n = 143/70/52/51/49 per source). In 85–95 % of losses we
   already trail on total length at r100; win share behind vs ahead at r100 is 0.14 vs 0.78 on compact maps
   (n 127/46) and 0.31 vs 0.76 on open maps (159/87); h2h death rate doubles in losses. Heartbreaker (62) alone
   causes 56 of 64 losses by elimination. *Build:* opening production and survival (rounds 0–100), measured with
   r25/r50 stage points added to the decoder (the record's first stage is r100 — too late). *Falsifier:* a seeded
   live-pool panel in which the r100 lead stops predicting the outcome (ahead − behind < 0.2).

4. **The local instruments do not transfer and must not order the queue (Q4, Q10).** Local share exceeds live
   share for 6 of 6 sources by 7–35 pp (unit: game; local n 18–68 on live maps, 0 on Portals/Slithery); the four
   screens have 0/0/4/1 common (map, opponent) cells in the 126k-game ledger, so paired calibration is impossible;
   no local opponent lies within 4.7 SD of Heartbreaker's or dev test 1's induced profile (17.5–23.5 units, 52–103
   total at r250 vs local 7–16 / 14–68). The campaign table's top 62 are all Sparse; the four live-tested sources it
   ranks 1/9/11/18 score 0.29–0.44 live; shrinkage leaves Spearman vs live at ≈ 0 (+0.10 → −0.20, n = 5). *Build:*
   the live-pool panel with swarm-heavy references first (m01 mimic, gavroche-v32, clones of 62/545) and a 10-dragon
   dilemma map. *Falsifier:* five sources with residual SD < 8 pp on live = a + b·local.

5. **Runtime is not the loss mechanism, and the judge's message stream is (still) not what we rebuild (Q6, Q8).**
   Only the teammate incumbent 9508 is at the cap (69/143 games, 1,096 TLE turns, Portals 37 per game); its faults
   correlate *positively* with winning (survivorship); executor uploads peak at 77.5–82.5 M except yuna-v02's 97.5 M on
   never-probed Slithery Fight — add Slithery A and Trauma to the probe fixtures. Separately, all 121 replay-driven
   live games of two unrelated bots agree with the recorded commands at 92.2 % / 92.4 % (965,412 commands), first
   mismatch at round 6–7, and dropping all messages lowers agreement in 29/29 games — the divergence is a subset of
   messages. *Test:* the one-dev-game tap build (Q8 spec) — authorise it. *Falsifier:* a post-change game that
   replay-drives exactly, or a tap whose logged stdin equals the rebuilt block.

## Three lineage claims that did not reproduce

- **D-010 (director decisions):** "the first four comparable sources disagree by −2, −5, −16 and −32 pp (local
  overstates live in three of four)". Re-derived on the same ledger with the fingerprint join: −12, −7, −14, −14,
  −35, −11 pp for 9508, 8540, 9639, 9663, 9980, 10013 — six of six overstate, none within 5 pp. The band-mean rule
  stands; the "three of four" and the −2/−5 magnitudes do not.
- **Registry hypothesis for local-tidus-t02-spread-only (9980, D-002):** "fewer ally-body collisions and more units
  by r100 on compact maps". Live: body-collision deaths 2.7 per 1k on compact maps (9508 2.3, 9663 3.4), self
  collisions 10.0 per 1k (9508 5.2), units r100 median 10 unpaired (9508 6, 9663 8.5) but −1 in the 17 exact pairs
  against 9663; compact share 0.20, the lowest of the five sources. Neither mechanism appears.
- **D-008 / handoff §3.3:** "layout assignment is not under our control and not random-looking". It is deterministic
  (finding 1) and controllable through the request shape; the v1 analysis's "unresolved" is superseded.

Also not reproduced in the form stated: HANDOFF §1's "a stdout write costs 2.5 M + 4 k/byte" — per SONAR line the
sandbox charges nothing measurable (−0.6 … +1.2 ± 0.5 M per ray, R² 0.02), so writes are batched and rays are free.

## Authorisations requested

(a) The tap-build dev game (finding 5); (b) a refetch of the four 9663 ranked series to book their Elo change
(Q9: null in the cache; 8 of 27 ranked series today were requested by other teams at arbitrary times, so the
even-hour blackout is half the story); (c) the band replay download (≤ 60 per team for 790, 133, 977, 75, 19, 406,
534, 875, 473, 241) — no data on the ranks that decide our rating exists locally.
