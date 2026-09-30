id: 2026-09-30-ares-v35-crown-clipped-dash-threat
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V35 extends crown threat coverage to clipped enemy dashes and adjacent head contact
task: Preserve the length leader in live match 669722 by avoiding a dash suicide at round 477
supersedes: ""
evidence:
  - Public match replay 669722
  - V33 and V35 replay drives from the saved match observations
  - Seed-1 V35-versus-V33 screen on the ten-map live roster
---

# Ares V35 — crown clipped-dash threat

## Live loss

In [match 669722](https://game.battlecode.au/visualiser?match=669722), Ares Team A's dragon 20 was the 24-length crown. At round 477 it started at `(20,10)` and V33 moved south to `(20,11)`. Enemy dragon 414 had length 4 and head `(22,12)`, but its chain extended beyond the crown's view. The replay records the enemy's `NWW` dash. After its second step its head was `(21,11)`, one cell from dragon 20; both heads died head-to-head and Team A was eliminated.

V33's `mark_danger` sizes the enemy horizon from the visible chain plus a one-segment clipped-tail allowance. Here that estimated three segments and a two-step horizon. Its threat cost covered only cells the enemy head could occupy. The crown's candidate at `(20,11)` sat adjacent to a predicted endpoint, so it received no threat penalty and target progress led it toward the enemy.

## Iterations

V34 added a broad crown-separation reward, assumed clipped enemies could dash the full three cells, expanded head threats to adjacent cells, and disabled attacks by crowns. Its matched seed-1 screen against V33 was 7–13 over the ten live maps and both seats, with no runner errors. V34 lost both games on Portals, Queen of Spades, and Slithery Fight. The broad retreat term was rejected.

V35 branches directly from V33 and keeps the edit narrow. Only a crowned dragon treats a clipped enemy chain as the full three-cell dash horizon. Its existing threat penalty also checks all cells within one Chebyshev step of each predicted enemy endpoint. V35 keeps V33's general target scoring, retreat behavior, and trade rule.

For the round-477 decision check, V35 was run against the recorded observations with the new feature disabled through round 476. It then chose `WN` from the recorded `(20,10)` head instead of V33's `S`. On Autarky's map those steps end at `(19,9)`. The recorded enemy reaches its fatal contact cell `(21,11)` after two dash steps; the two heads would be two cells apart, so the same head-to-head contact does not occur. The local replay driver differs from the live V33 action at round 473; this is a replay-state decision check, not a full counterfactual match.

## Live-map screen

The V35-versus-V33 screen used unswbc 1.2.2, seed 1, sandbox execution, all ten live maps, and both seats. V35 scored **10–10**, with zero draws and runner errors.

| Map | V35 wins–losses |
|---|---:|
| Autarky | 1–1 |
| Default | 1–1 |
| Devil | 1–1 |
| Dilemma | 1–1 |
| Portals | 2–0 |
| Queen of Spades | 1–1 |
| Schooltime | 0–2 |
| Slithery Fight | 1–1 |
| Trauma | 1–1 |
| Trophy | 1–1 |

A follow-up seed-1 sandbox screen compared V35 with V19, V28, and V32 on
the same ten maps and both seats; it had no runner errors:

| Opponent | V35 wins–losses |
|---|---:|
| V33 | 10–10 |
| V32 | 6–14 |
| V28 | 9–11 |
| V19 | 13–7 |

Across all four pairings V35 went **38–42** in 80 games. The corresponding
five-bot, one-seed round-robin records were V32 46–34, V33 43–37, V28 41–39,
V35 38–42, and V19 32–48. This small deterministic screen shows no aggregate
strength gain. V35 remains an experimental issue fix, not a promotion result,
and stays outside `FRONTIER.md`. It was uploaded as
`ares-v35-crown-clipped-dash-threat-ai`, submission v90 (ID 12675); the API
reports it active as of 2026-09-30 06:23 UTC. Its API source hash is
`870f4bbb1b20371e472728363fe05479ecf92c0a9d260ce70c4c21106eb04c1d`. The
new 60-game manifest, results, standings, and logs are in the ignored
`build/ares-v35-vs-v19-v28-v32-live10-seed1-20260930/`; the V33 games are in
`build/ares-v35-vs-v33-live10-seed1-20260930/`. No replays were saved.
