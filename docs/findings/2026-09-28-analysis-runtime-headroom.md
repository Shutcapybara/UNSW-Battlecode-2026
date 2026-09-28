---
id: A1-Q6-runtime-headroom
author: gpt-6/analysis/codex-session
kind: observation
title: Runtime maxima separate the current A-side sources sharply
task: A1 statistics analysis
supersedes: none
evidence: LIVE/state/state.json selected verified controlled field result rows; 2026-09-28 workspace snapshot
---

Unit is game. Among 265 verified controlled field games, 9508 (n=123) reached 100,000,000 CPU points at least once at the game maximum; 9663 (n=50) had a maximum of 97,457,737; 8540 (n=31), 9639 (n=32), and 9980 (n=29) had maxima 77,387,763, 79,719,935, and 77,478,070 respectively. The current selected rows have `cpu_recorded == turns` in all 265 games, indicating complete recorded counts, not absence of near-cap turns. The game-level max field cannot reveal p99 dragon-turn runtime or which round/map condition caused the spike.

**Decision:** Keep runtime as a gate for 9508 and 9663; do not infer a general Python-host degradation threshold from game maxima alone. Probe-level points and map/round windows are needed before changing the 80/60 M local thresholds.

**Falsifier:** Probe logs show that the apparent maxima are decoder or record artifacts, or sufficiently powered per-turn probes establish that the lines remain below the operational budget at high-unit/sonar peaks.
