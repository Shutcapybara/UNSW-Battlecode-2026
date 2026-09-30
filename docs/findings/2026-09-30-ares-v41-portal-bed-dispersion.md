---
id: 2026-09-30-ares-v41-portal-bed-dispersion
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V41 disperses dragons after portal exits
task: Reduce portal-exit congestion reported in match 700279
supersedes: ""
evidence:
  - Decoded public replay 700279 on Queen of Spades
  - Focused paired-portal target-selection regression
  - C++20 full-bot compile
  - Ten-map, both-seat parent/child tournament screen (20 generated-seed games)
  - Contest API active submission v94 (ID 13086)
---

# Ares V41 — portal-bed dispersion

## Replay diagnosis

The decoded [match 700279 replay](https://game.battlecode.au/visualiser?match=700279)
is Queen of Spades, 206 rounds, with Ares V40 as side A. Its movement trace
shows repeated P0 crossings into the `(20,31)` / `(21,31)` bed cluster, then
back to the opposite exit at `(15,1)`. Dragon 3 returned after four rounds
(rounds 30–34); dragon 18 returned after five (rounds 51–56). Child 82 entered
the same cluster at round 169 while three allied heads were clustered around
the landing area, then crossed back at round 180. That last return came eleven
rounds after exit, so V01's two-round return window would not cover the observed
churn.

The replay records movement and splits, not the policy's internal target or
visibility state. The trace therefore confirms the congestion and return
pattern, while the focused regression below checks target choice in a
constructed observation. In V40, allied target yield depends on a comparison
between Manhattan distance and portal-aware route length. A portal can make a
bed one route step away even when an ally beside it does not strictly win that
comparison.

## V41 change

V41 branches from V40 and retains its length-priced sprint policy. For pearl
and viable bed targets, it counts visible allied heads within two torus-
Manhattan tiles. Each ally compounds a 0.12 value discount on the target, in
addition to V40's nearest-ally yield.

V41 also records the landing cell and portal pair of the last crossing. During
the next 12 rounds, while within two tiles of that landing, it discounts any
target whose route crosses the same pair and subtracts 8 points from a move
that crosses back through it. This soft penalty leaves exploration, uncovered
resources, and valid hunts available to win movement selection.

## Focused regression

The regression uses a paired portal with a ripe bed one portal step away and
an unseen cell beside the dragon. With no ally or recent exit, it selects the
bed. When an ally covers that bed, V41 selects the unseen cell. It also selects
the unseen cell with no ally when the dragon has recently exited the same
portal pair; the test checks that the first move does not cross back through
that pair.

## Verification

- `g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -I. tests/test_ares_v41_portal_bed_dispersion.cpp -o /tmp/test_ares_v41_portal_bed_dispersion && /tmp/test_ares_v41_portal_bed_dispersion` — passed.
- `g++ -std=c++20 -O2 -Wextra -I bots/ares-v41-portal-bed-dispersion bots/ares-v41-portal-bed-dispersion/main.cpp -o /tmp/ares-v41-portal-bed-dispersion` — passed.
- Parent/child screen: Ares V40 vs V41, both seats on Autarky, Default, Devil, Dilemma, Portals, Queen of Spades, Schooltime, Slithery Fight, Trauma, and Trophy. `unswbc` generated each game's seed; each seed is recorded in its log. V41 won **11–9** with zero runner errors. It swept Dilemma, Portals, and Slithery Fight; V40 swept Default and Devil; the other five maps split 1–1. Logs and results: `build/ares-v40-v41-live10-20260930/`.

This is a single unseeded development screen and replay-informed behavior
change, not a promotion result. V41 remains experimental outside `FRONTIER.md`.

The contest accepted the upload as active submission v94 (ID 13086) on
2026-09-30 11:49 UTC. Its API source hash is
`1c1f1fa7bd0b672ab3f6641373ba532514d5ecaca2a6c267832ae4b79cab9088`. The
server's automatic activation does not change V41's local experimental status.
