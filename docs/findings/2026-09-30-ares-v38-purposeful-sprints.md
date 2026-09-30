id: 2026-09-30-ares-v38-purposeful-sprints
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V38 charges length-3 dragons for routine dashes
task: Reduce short defensive sprints that spend a segment without a concrete payoff
supersedes: ""
evidence:
  - Public match replay 686866
  - Focused C++ policy regression and V37 control
  - C++20 full-bot compile
  - Seed-1 ten-map direct comparison against V37, with replay action counts
---

# Ares V38 — purposeful short sprints

In match 686866, Ares V37 dragon 25 is length 3 and dashes EN at UI round 16,
ending length 2 without collecting a pearl. V37 enables two-step candidates
when an enemy head is within Chebyshev distance 4. Its ordinary movement score
can then prefer an endpoint for target progress, safety, or map-specific
bonuses, even when the second step has no direct material payoff. Dragon 25's
assigned scouting lane is row `y=3`; the inherited `+0.75` lane progress bonus
can contribute when a dash endpoint reaches that row, but it does not itself
require or directly reward a dash.

V38 adds a 1.5 score cost to every two-step move made by a length-3 dragon,
including head-to-head attack scoring. A dash earns a 4.0 offset only when its
extra step collects a pearl or reaches the selected pearl, bed, portal, prey,
escape, or crown target. Other score terms remain active, so an exceptional
tactical safety gain can still overcome the added cost. Dragons of length 4 or
more retain V37's scoring.

The focused C++ regression models the three nearby enemy heads visible around
dragon 25 and checks that its exploratory move stays one step. A dense-threat
stress fixture adds two synthetic nearby heads: V37 chooses EN, while V38
chooses E, with no pearl pickup or selected target at the dash endpoint. Two
separate cases verify that V38 still chooses a two-step move when it collects a
pearl or reaches a selected ripe bed. This is a policy fixture, not a complete
replay reconstruction. The replay does not preserve the bot's persistent
policy state or radio inputs; when those are omitted, a local reconstruction
chooses one step under both V37 and V38, so it cannot establish that the exact
recorded decision changes under V38.

The seed-1 panel covered Autarky, Dilemma, Portals, Queen of Spades,
Schooltime, Default, Slithery Fight, Trauma, Devil, and Trophy, with both seats
(20 games). V37 won **13–7**, with zero runner errors. Replay action counts
showed V37 dash on 639 of 56,962 length-3 turns (1.12%); V38 dashed on 1,816
of 46,741 such turns (3.89%). The 4.0 reimbursement made length-3 dashes more
common despite the added score cost, so V38 is rejected as a fix.

Verification passed:

- `g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -I. tests/test_ares_v38_purposeful_sprints.cpp -o /tmp/test_ares_v38_purposeful_sprints && /tmp/test_ares_v38_purposeful_sprints`
- `g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -DARES_TEST_V37_CONTROL -I. tests/test_ares_v38_purposeful_sprints.cpp -o /tmp/test_ares_v37_sprint_control && /tmp/test_ares_v37_sprint_control`
- `g++ -std=c++20 -O2 -Wall -Wextra -I bots/ares-v38-purposeful-sprints bots/ares-v38-purposeful-sprints/main.cpp -o /tmp/ares-v38-purposeful-sprints`
- `unswbc 1.2.2`, seed 1, 10 maps, both seats; replays are in `build/ares-v37-v38-live10-seed1/`

V38 remains an experimental control only. The single-seed direct panel is a
development screen, not a promotion benchmark.
