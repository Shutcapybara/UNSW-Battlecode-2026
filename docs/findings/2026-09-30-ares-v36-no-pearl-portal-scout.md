id: 2026-09-30-ares-v36-no-pearl-portal-scout
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V36 prioritizes an unpaired portal when no fresh pearl target exists
task: Fix V35's turn away from a visible portal in live match 674727
supersedes: ""
evidence:
  - Public match replay 674727
  - V35 target-selection source and replay event timeline
---

# Ares V36 — no-pearl portal scout

## Live replay

In [match 674727](https://game.battlecode.au/visualiser?match=674727), Team A
was Ares V35 on Queen of Spades. Dragon 1 moved from `(6,16)` to `(5,16)` on
round 51, beside the unpaired portal edge at `(6,17)`, then moved north to
`(5,15)` on round 52. The replay records its prior pearl eat on round 33 and
its next pearl eat on round 86. It had no useful current pearl lead when it
turned away from the portal.

V35 assigns an unpaired portal target value 3 and ordinary unseen ground value
5. The `dive_cost` parameter's comment describes an extra step cost, but the
parameter is unused; the active comparison is directly between those target
values. This lets a route toward unexplored ground outrank a portal even when
there is no fresh pearl to chase.

## V36 change

V36 branches from V35. After a dragon's first three rounds, it values an
unpaired portal at 8 when it has no fresh remembered pearl. This lets a
reachable portal outrank ordinary unseen ground. Fresh pearl targets retain
the existing portal value of 3, and bed targets keep their existing value.
The pearl check uses the existing 40-round memory limit, so an expired pearl
sighting does not suppress portal scouting. V35's crown threat behavior and
newborn split-time portal handoff are unchanged.

## Live-map screen

The seed-1 sandbox panel used unswbc 1.2.2, the ten live maps, both seats,
and had zero runner errors. V36 scored **13–7 vs V35** and **9–11 vs V19**
across 40 games. V35's saved comparison was 13–7 vs V19, so the stronger
portal value did not preserve its V19 result. V36 remains unsubmitted. The
panel results are in the ignored
`build/ares-v36-vs-v35-vs-v19-live10-seed1-20260930/` directory. This is a
full-game screen; the saved V35 replay has not yet been counterfactually
replayed with V36.
