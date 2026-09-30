---
id: 2026-09-30-ares-v28-minimum-sacrifice-enclosure-split
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V28 beats V19 by minimizing the critical enclosure split
task: Iterate Ares V19 from version 21 to correct suboptimal dead-end splitting
supersedes: ""
evidence:
  - Seed-1 sandbox games against a matched Ares V19 opponent
  - Decoded public replay split-size counts
---

# Ares V28 — minimum-sacrifice enclosure split

## Hypothesis and change

The live-loss review identifies dead-end feeding cases where the bot should
sacrifice two tail segments and let the longer dragon move out, rather than
splitting off a much larger child. Ares V19's critical-enclosure fallback uses
`SPLIT (length - 2)`, which leaves a two-segment head parent. V28 preserves
V19's reach probe, ordinary movement and split scoring, and opening behavior;
only the fallback split size changes to `Params::split_child` (two segments).

## Development screens

All games used unswbc 1.2.2, seed 1, sandbox execution, and direct matches
against Ares V19. The diagnostic covered Autarky, Prisoners Dilemma, Portals,
and Slithery Fight in both seats: V28 won **6–2**, with zero runner errors.

The full panel covered all ten active maps and both seats (20 games). V28 won
**12–8**, with no draws or runner errors. The Ares V19 self-play mirror
baseline was 10–10. The map results were:

| Map | V28 wins–losses |
|---|---:|
| Autarky | 1–1 |
| Default | 2–0 |
| Devil | 1–1 |
| Prisoners Dilemma | 1–1 |
| Portals | 2–0 |
| Queen of Spades | 1–1 |
| Schooltime | 1–1 |
| Slithery Fight | 2–0 |
| Trauma | 0–2 |
| Trophy | 1–1 |

The mirror seat outcomes flipped favorably on Default A, Portals B, and
Slithery Fight B; Trauma A flipped adversely. All 20 replays decoded
successfully. The replay summary counted 5,016 two-segment children among
5,026 V28 splits, compared with 4,590 among 4,897 V19 splits; V19 also made 22
splits of size 10 or larger, while V28 made four. These are whole-game counts,
not counts restricted to the critical fallback. Maximum recorded sandbox usage
across either bot was 9.14M points.

## Iteration history

The first four iterations were each screened over all ten maps and both seats:
V21 scored 9–11, V22 10–10, V23 10–10, and V24 10–10 against V19. Narrowed
Portal/Slithery diagnostics then scored V25 2–2, V26 2–2, and V27 0–4. These
versions either generalized the largest-child upgrade too broadly or gated it
without improving the direct result. V28 instead changes only the critical
fallback's split size, and it is the first iteration to beat V19 in the full
panel.

## Limits and status

This is one deterministic seed against a single bot, not the repository's
broader fixed-roster promotion gate. V28 remains experimental and is not listed
in `FRONTIER.md`. Results, manifest, and 20 replays are in the ignored
`build/ares-v28-vs-v19-all10-seed1-20260930/` directory; decoded replay data is
in `build/ares-v28-vs-v19-replay-review-20260930/`.

## Contest submission

The requested upload completed as **submission v87 (ID 12440)**, named
`ares-v28-minimum-sacrifice-enclosure-split-ai`, at 2026-09-30 03:01:47 UTC.
A read-only query to the authenticated submissions endpoint reported its status
as `active`; the platform auto-activated the upload. The API source hash is
`782fec21f7d2cb4f924e0a68e886f8e8a1c2c2b8a5d33095ca6b367817059e0c`. This
contest status does not change the local experimental/frontier decision.
