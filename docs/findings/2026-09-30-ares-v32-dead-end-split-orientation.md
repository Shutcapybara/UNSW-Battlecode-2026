---
id: 2026-09-30-ares-v32-dead-end-split-orientation
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V32 fixes the Autarky dead-end split and beats V19 11–9
task: Correct the child orientation reported in the V31 A-side replay
supersedes: ""
evidence:
  - Public match replay 658569 and decoded review at build/match-658569/review/658569.decoded.json
  - V32 A-side Autarky replay against V28, seed 0x84ed9bbaf7053078
  - Synthetic exact-observation action check for V29 through V32
---

# Ares V32 — dead-end split orientation

## Change

V31 delayed its split until after the last pearl but still issued `SPLIT 2` at
length 5. That preserved a length-3 parent at the endpoint, where it wall-died,
and left a length-2 child alive. V32 retains V31's feeding guards and adds an
endpoint rescue choice: when the body-aware reach is critical and every
one-step head move is fatal, search child sizes from largest to smallest and
choose the largest tail child with a free exit and at least the configured
forecast room. On the target length-5 state this is `SPLIT 3`, leaving a
length-2 trapped parent.

## Reproduced replay

The decoded match 658569 trace showed dragon 27 with body head-first
`[(35,0),(35,1),(35,2),(35,3)]` at round 24. It split 2 at round 25 before
collecting the final pearl. After moving onto `(34,0)` at round 26, the
length-3 parent wall-died there at round 27 with no free exits.

In the V32 Autarky A-side replay, dragon 61 was length 4 at `(35,0)` and moved
west onto the final pearl at round 65. At round 66 it issued `SPLIT 3`; the
split event records parent length 2 and child 76 length 3. Child 76 moved south
out of the endpoint, while parent 61 wall-died at `(34,0)` at round 67 with no
free exits. Child 76 later died in a head-to-head at round 102, away from the
dead end. The orientation and initial escape behavior match the requested
correction; continued child survival is not established by this replay.

## Screens and limits

For the target case, V32, Team A, defeated V28, Team B, on Autarky in 233
rounds using seed `0x84ed9bbaf7053078`. The runner reported no errors. This
replay verifies that dragon 61 collects the final pearl before issuing
`SPLIT 3`; the length-3 child exits and the trapped parent wall-dies. The child
later dies in a separate head-to-head at round 102.

A direct panel against V19 used unswbc 1.2.2, sandbox execution, seed 1, ten
maps, and both sides (20 games). V32 won **11–9**, with no runner errors. All
20 replay files decoded, and their winners and round counts matched the saved
results.

| Map | V32 wins–losses |
|---|---:|
| Autarky | 2–0 |
| Default | 2–0 |
| Devil | 1–1 |
| Prisoners Dilemma | 1–1 |
| Portals | 1–1 |
| Queen of Spades | 1–1 |
| Schooltime | 0–2 |
| Slithery Fight | 1–1 |
| Trauma | 1–1 |
| Trophy | 1–1 |

V28 scored 12–8 on the same panel, so V32 retains a positive V19 result but
loses one more game than V28. This is one deterministic seed, not the broader
promotion gate. V32 remains experimental and has not been admitted to the local frontier.

Target-case replay: `build/ares-v32-dead-end-screen-658569-seed1/replays/autarky_A.replay`

Target-case review: `build/ares-v32-dead-end-screen-658569-seed1/review/autarky_A.json`

Target-case transcripts: `build/ares-v32-dead-end-screen-658569-seed1/v32_A_transcripts.json`

V19 panel games: `build/ares-v32-vs-v19-all10-seed1-20260930/`

Decoded V19 panel reviews: `build/ares-v32-vs-v19-replay-review-20260930/`


## Contest submission

The requested upload completed as **submission v88 (ID 12501)**, named
`ares-v32-save-long-child-at-dead-end-ai`, on 2026-09-30 at 04:05 UTC. A
read-only query to the authenticated submissions endpoint reported its status
as `active`; the platform auto-activated the upload. The API source hash is
`6779c69eb216900659402429bf967c571f6ee3680fcc0339a7a905f3f498d9f8`. This
server deployment does not change V32's local experimental status.
