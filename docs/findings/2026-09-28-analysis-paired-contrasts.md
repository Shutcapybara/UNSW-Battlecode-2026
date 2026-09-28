---
id: 2026-09-28-analysis-paired-contrasts
author: glm/analysis/a1
kind: observation
title: "Rejected screens 8540 and 9639 moved nothing structural: stage-profile deltas were ~0 where outcomes held, and the score flips that decided them carried small negative t250 deltas"
task: "A1 §3.2 — candidate-minus-control contrasts"
superses: []
evidence: "Exact (block, map, side, opponent submission) pairs from the four screen experiments: a01aee66 (8540 vs 9508, 3 blocks, 31 pairs), 8b12ae55 (9639 vs 9508, 3 blocks, 32 pairs incl. 3 Dilemma fill pairs), 02356998 (9663 vs 9508, 2 blocks, 20 pairs), 88a5b9be (9980 vs 9663, 2 blocks, 20 pairs, incl. the layout-mismatched ca5af1bf). Unit = pair; unpaired games excluded and counted. Script: tools/analysis/a2_paired_contrasts.py."
---

# Per-experiment summary (candidate − control, median over pairs)

| experiment | pairs | flips (cand/ctrl) | flipped-pair medians: length, units r100, total r250 | held-pair median t250 |
|---|---|---|---|---|
| a01aee66 8540 vs 9508 | 31 | 5/6 | length −8, u100 +0, t250 −15 | 0 |
| 8b12ae55 9639 vs 9508 | 32 | 4/6 | length −6, u100 −0, t250 −2 | 0 |
| 02356998 9663 vs 9508 | 20 | 3/3 | length +4, u100 +2, t250 −10 | +6 |
| 88a5b9be 9980 vs 9663 | 20 | 1/2 | length −33*, t250 −69* | −6 |

*88a5b9be's single flipped pair (Default, −1) carries almost all of its signal; ca5af1bf (the block where the arms ran on opposite layouts) contributed 10 pairs whose deltas are confounded by layout — excluded from mechanism reading, kept in the pair counts with that flag.

# What changed when the outcome changed

- Where outcomes FLIPPED, the median paired t250 delta was negative for both rejected candidates (−15, −2) — they lost games by producing less total length by mid-game, not by late conversions or death-cause changes (wall/h2h per-1k deltas on flipped pairs are noisy, |median| < 2 in three of four experiments).
- Where outcomes HELD, stage deltas are indistinguishable from zero across the board (median t250 0/+6) — these mechanisms were inert, not partially-good.
- No experiment showed a positive-median stage delta on flipped pairs; there is no "worked but unlucky" candidate in this set.

# Mechanisms to stop re-testing (the lineage ledger entries)

- **bifrost-v01-recovery-reference (8540)**: recovery-oriented changes bought +13 units r100 on one Schooltime pair but −15 median t250 on flipped pairs → the recovery mechanism does not convert openings into length. Rejection stands.
- **ein-dog-v02 (9639)**: eindog momentum changes were inert (held pairs exactly 0); its compact-map collapse (A1) is the opener, not momentum. Stop screening eindog momentum variants against 9508 on field blocks; fix the opener locally first.
- **9663 (yuna-v02) vs 9508**: genuinely close (3/3 flips, +4 length median) — consistent with it being externally activated later; its residual deficit is t250 on flipped pairs (−10).
- **9980 (tidus spread-only)**: one-map signal, wrong direction. Stop re-testing spread-only variants.

**Decision fed**: the screen protocol is working (both rejections re-derived here are supported by paired stage evidence, not just score noise); the queue should stop re-screening these four mechanisms, and layout-confounded blocks (like ca5af1bf) should be flagged at decision time — the hub contrast now has the layout-parity detector to do so.

**Falsifier**: re-running any of these pairs under deliberately opposite layouts showing the flipped-pair stage deltas reverse sign (would mean layout, not mechanism, decided the screen).
