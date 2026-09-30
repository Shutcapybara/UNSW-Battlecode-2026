id: 2026-09-30-ares-v40-length-priced-sprints
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V40 prices dash moves through segment loss
task: Align dash and pearl scoring with the body segments actually gained or spent
supersedes: ""
evidence:
  - Public match replay 686866
  - Focused C++ pearl-contest policy regression
  - C++20 full-bot compile
  - Seed-1 ten-map direct comparison against V37, with replay action counts
  - Contest API submission v93 (ID 13010), active
---

# Ares V40 — length-priced sprints

The movement simulator already removes one tail segment for each move after
the first. V37's successful-move score also subtracted `sprint_cost` per extra
move, so it charged the same segment loss twice. V40 removes that duplicate
charge and prices the simulated body-length change once at `lv_now`. Its
head-to-head scoring also uses one current segment value per extra move.

The generic `0.5 * eaten` bonus is removed because body growth already values a
pearl collected with a one-step move. A pearl collected on a dash offsets the
extra segment spent, leaving current length unchanged. When no enemy head is
within two tiles, V40 applies a small `0.25` segment-value opportunity cost to
a pearl collected after the first move: consuming it on a dash gives up the
chance to use it for later growth. When an enemy is within two tiles, V40
instead adds one segment value for denying that pearl.

The focused regression passes: with no nearby enemies, the length-3 dragon
moves one step toward the pearl; with a nearby enemy able to contest it, the
dragon dashes to collect it. This is a compact state fixture, not a complete
reconstruction of match 686866; replay inputs omit persistent policy and radio
state.

The seed-1 panel used Autarky, Dilemma, Portals, Queen of Spades, Schooltime,
Default, Slithery Fight, Trauma, Devil, and Trophy, with both seats (20 games).
V40 won **11–9** against V37, with no draws or runner errors. It swept
Schooltime, Slithery Fight, and Trophy; V37 swept Portals and Queen of Spades;
the other five maps split. In the same panel, V40 length-3 dragons dashed on
1,170 of 48,092 turns (2.43%), while V37 dashed on 998 of 51,467 turns
(1.94%). The result is a positive one-seed development screen, not a
promotion benchmark; V40 remains experimental and outside FRONTIER.md.

The contest API accepted the V40 source as submission v93 (ID 13010) and
reports it active. Its API source hash is
`1a4ee3dc7148ef7b8c2488879d09c75d8b9cfbc32364d8c03e96e35013597737`. This
server activation does not change the local experimental status.

Verification:

- `g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -I. tests/test_ares_v40_length_priced_dashes.cpp -o /tmp/test_ares_v40_length_priced_dashes && /tmp/test_ares_v40_length_priced_dashes`
- `g++ -std=c++20 -O2 -Wall -Wextra -I bots/ares-v40-length-priced-sprints bots/ares-v40-length-priced-sprints/main.cpp -o /tmp/ares-v40-length-priced-sprints`
- `unswbc 1.2.2`, seed 1, 10 maps, both seats; results and replays are in `build/ares-v37-v40-live10-seed1/`
