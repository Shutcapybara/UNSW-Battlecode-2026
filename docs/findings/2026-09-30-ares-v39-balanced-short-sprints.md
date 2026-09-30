id: 2026-09-30-ares-v39-balanced-short-sprints
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V39 reduces the length-3 dash reimbursement
task: Test whether a break-even short-sprint payoff reduces V38's frequent dashes
supersedes: ""
evidence:
  - Match 686866 review and V38 replay action counts
  - Focused C++ policy regression and V37 control
  - C++20 full-bot compile
  - Seed-1 ten-map direct comparison against V37
---

# Ares V39 — balanced short-sprint payoff

V39 branches from V38 and lowers its length-3 dash payoff from 4.0 to 2.5,
matching the extra 1.5 score cost plus the existing 1.0 sprint cost. It also
stops refunding dashes that reach an escape-plan target. The intent was to keep
real pickup and target dashes while discouraging routine defensive dashes.

The focused C++ regression passed for the three enemy heads visible near the
dragon in match 686866, the dense-threat case, and second-step pearl and ripe
bed arrivals. This fixture omits persistent policy state and radio inputs, so
it does not reproduce the recorded match decision exactly.

The seed-1 panel used the same ten live maps and both seats as V38. V37 won
**13–7** over 20 games, with zero runner errors. By map, V37 swept Autarky,
Portals, Schooltime, and Trauma; V39 swept Queen of Spades. Dilemma, Default,
Slithery Fight, Devil, and Trophy split. V39 therefore did not improve on
V38's panel result. This is a
development screen, not the broader promotion benchmark.

Verification:

- `g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -I. tests/test_ares_v39_balanced_short_sprints.cpp -o /tmp/test_ares_v39_balanced_short_sprints && /tmp/test_ares_v39_balanced_short_sprints`
- `g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -DARES_TEST_V37_CONTROL -I. tests/test_ares_v39_balanced_short_sprints.cpp -o /tmp/test_ares_v37_sprint_control && /tmp/test_ares_v37_sprint_control`
- `g++ -std=c++20 -O2 -Wall -Wextra -I bots/ares-v39-balanced-short-sprints bots/ares-v39-balanced-short-sprints/main.cpp -o /tmp/ares-v39-balanced-short-sprints`
- `unswbc 1.2.2`, seed 1, 10 maps, both seats; replays are in `build/ares-v37-v39-live10-seed1/`
