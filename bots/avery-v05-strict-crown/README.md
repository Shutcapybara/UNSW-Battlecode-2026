# avery-v05-strict-crown — current lineage tip

**Lineage:** avery · **Parent:** avery-v03-swarm-spacing (v04's broad crown
module was measured and rejected; see its README).

## Hypothesis

The round-500 longest-dragon tiebreak (19 of v03's 20 r500 losses) is worth
attacking, but the crown must be strictly singular and late so it cannot
freeze the swarm economy the way v04's did.

## Changes vs v03

- Crown role from round **300** (v04: 200), only for dragons already
  **len ≥ 8** (v04: 4), demote margin **2** (v04: 3). CROWN beacons relayed
  3 hops; self packet carries a crown flag (bit 50).
- Crown skips voluntary splits; head-risk ×1.5.
- Crown-kill from round 380: strikes vs enemies ≥ longest known ally +60.
- **No feeding** (v04's feed-die machinery dropped as too risky).

## Results

Run `experiment_data/avery-v05-strict-crown_20260925062900090323` (242 games,
11 opponents — gauntlet-5 plus six tew-line bots, native, both sides,
11 maps).

| Opponent | W–L–D | v03 | v04 (rejected) |
|---|---|---|---|
| ouroboros-v10-beacon | 15–7 | 16–6 | 10–12 |
| hunter-v14-cpp | 12–10 | 12–10 | 16–6 |
| hunter-v20-portal-scouts | **14–8** | 13–9 | 13–9 |
| fry-v14 | 16–6 | 15–7 | 17–5 |
| kraken-v04-eval | 18–3–1 | 18–3–1 | 18–3–1 |
| **gauntlet-5 total** | **75–34–1 (68.6%)** | 74–35–1 (67.7%) | 74–35–1 |
| tew v07–v12 (each) | 8–9 wins | 9 (v07–v09) | 6–7 |

r500 losses: 19, still 18 on the longest tiebreak — the strict crown banks
without economic damage but still does not outgrow enemy crowns; crown
**survival** (escorts, safe farming grounds, fight avoidance) is the open
problem, not crown production.

## Open questions for v06+

1. Crown survival: escorted crown / farm-in-dead-end (ouroboros-style) /
   stronger late-game risk aversion. Target: flip the ~18 r500 longest
   losses, 13 of which were within 6 segments in v03.
2. tew matchup (~40% score): undiagnosed; their names suggest coordinated
   hunting. Needs replay review of big_empty/arena losses
   (`enemy` deaths 1904 on big_empty in the v02 run).
3. Remaining convergence deaths (team_kills still ~46% of deaths):
   target-claim packets (hydra-v08-style reservations) untried.
4. Sandbox CPU checks on big_empty never performed (all runs native;
   3 whole-game 600 s wall timeouts in the v01 run were machine contention,
   runtime_faults = 0).
