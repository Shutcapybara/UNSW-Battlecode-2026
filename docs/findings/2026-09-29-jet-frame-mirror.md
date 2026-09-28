---
id: F-20260929-jet-frame-mirror
author: claude/jet/cowork-01618tfq
kind: observation
title: Seat advantage on symmetric live maps is bias inside the bots; a frame wrapper recovers it for seat B
task: Jet cohort research cycles 22-23
supersedes:
evidence: ["experiment_data/cohort_research_20260927T011500Z_jet/cycle_22_seat_asymmetry/REPORT.md", "experiment_data/cohort_research_20260927T011500Z_jet/cycle_23_frame_choice/REPORT.md", "bots/jet-v05-frame-mirror/"]
---

Unit is game; local, unswbc 1.0.0 native.

**Seat bias.** v32 was played against 6 opponents on autarky, queen_of_spades, trauma and trophy. The side at seat A's
spawn positions won 32/48, and the maps are exactly symmetric (tiles, spawns, every kelp and portal edge).
- Swapping team labels reproduced every per-map count.
- Giving the other side the lower ids (first move) left the P1-position share at 32/48. Move order mattered on
  queen (9 -> 5 of 12) and trophy (5 -> 8).
- The advantage therefore comes from coordinate-order tie-breaks in the bots. The same code plays a different game
  from mirrored spawns.

**Wrapper.** `bots/jet-v05-frame-mirror` is v32 with a protocol-level frame transform.
- Transformed on input: tiles (coordinates and row order), bodies, edge rows and facing. MOVE and SONAR directions
  are inverted on output.
- The frame is keyed on (W, H, team), so every dragon of a team agrees and sonar stays consistent.
- Seat B plays in seat A's frame: 180 degrees on the 180-degree maps, x-mirror on trophy and schooltime. Seat A is
  unchanged.
- It is exact: rotated-frame self-play on position-swapped maps reproduces the original self-play games' 500-round
  curves.

**Result.** Fresh opponents (newton-x10, tew-v12, fafnir-v01, scholze-v03, von_neumann-x07, ouroboros-v10) x 10 live
maps x 2 seats, paired with v32 on identical fixtures:
- 99 vs 86 of 120 (up 16, down 3). No map is worse; queen_of_spades 12 vs 7, schooltime 12 vs 9.
- A registered per-cell frame selection scored 92, and its seat-A picks did not replicate. The symmetry-derived
  rule generalises; cell maxima overfit.

**Decision:** jet-v05-frame-mirror is a local candidate with a CANDIDATE.toml (activation marker `ACT:frame`).
The wrapper code is host-independent, but the gain depends on the host's bias. Before wrapping another host
(e.g. the live incumbent), check its seat-B record with the P table.

**Falsifier:** a seeded (unswbc 1.2.x) or live paired panel where wrapped seat-B games do not beat the host's seat-B
games on the 180-degree maps (autarky, queen_of_spades, trauma, default, portals, dilemma, slithery_fight).

**Addendum (cycle 24, other hosts).** `tools/jet/make_frame.py HOST OUT` applies the same wrapper at the text level to
any protocol.py-family bot (exact: reproduces jet-v05 on test fixtures). Seat-B games, paired vs the unwrapped host,
4 opponents x 8 live maps: bifrost-v29 21 vs 12 of 32 (transfers); tidus-t02 14 vs 15; yuna-v02 19 vs 19 (default
0/4 vs 4/4). The value is host-specific: run a seat-B check before wrapping a host.
