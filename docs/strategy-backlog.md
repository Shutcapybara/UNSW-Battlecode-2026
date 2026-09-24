# Strategy Backlog

This file tracks active Hunter work, promotion criteria, and the current version
lineage. Detailed Python-era measurements live in
[Hunter results](hunter-python-results.md).

## Current decision

`hunter-v16-boost-traps` remains the measured benchmark from the earlier
11-map, three-bot round robin, where it finished one win ahead of V15 and won
their direct matchup. V20 now beats V19 head-to-head, pending a wider-pool
comparison. V17 did not improve on V16 and remains experimental.
V18 adds self-trap avoidance based on one replay. Its all-map result ties V17
and V16, so it remains experimental.
V19 scored highest in a four-bot pool, but tied V18 head-to-head 11–11; it
remains experimental pending a direct improvement over V18 and validation of
the self-trap behavior.
V20 addresses the Trauma replay where hotspot saturation prevented portal
discovery: distant spawn timers no longer count as hotspots, hotspot reports
expire after eight rounds, and local food demand controls a bounded scout
claim. Length-3-to-6 scouts can start with four survivors; boards of at most
625 tiles skip scouting because replays showed the exits were too contested.
In the final 11-map, both-side comparison with V19, V20 went 13W/9L with no
errors. It won 11–3 across all portal maps and 8–2 on the priority set
(`default`, `queen_of_spades`, `schooltime`, `stronghold`, `trauma`). It remains
experimental pending validation against the wider field. Results:
[`V19 vs V20`](../build/hunter-v19-v20-hunter20-verified-all-maps/results.json).

### V16 evidence

The first V15/V16-vs-latest-five run used V10 through V14 on all 11 maps, both
side assignments. It completed with no errors after longer-timeout retries:
V15 scored 65W/45L, while the original V16 source scored 59W/51L. V16's largest
regressions were `help` (3–7 versus V15's 8–2) and `big_empty` (4–6 versus
5–5). The V16 source has since changed, so these results are historical for the
pre-fix source. Artifacts: [V15](../build/hunter-v15-vs-latest5/) and
[original V16](../build/hunter-v16-vs-latest5/).

Replay and source review found that V16's surround planner compared direction
numbers with tile IDs, preventing the three-side check from working on almost
all tiles. Iteration 1 now tracks route positions. In a three-bot, 11-map
round robin (V14, V15, V16), it tied V15 overall at 24W/20L and won the direct
matchup 12–10. It still trailed V15 against V14 (12–10 versus 14–8). Diagnostic
help matches observed 6 and 18 surround boosts, plus 19 and 24 shorter cutoffs,
depending on side; one ended with V16 behind by 123 total segments, while the
side-swapped game ended 20 segments ahead. Artifacts: [results and replays](../build/hunter-v16-iter1-surround-fixed/) and
[tactic diagnostics](../build/hunter-v16-iter1-tactic-diagnostics/).

Iteration 2 raised the minimum post-boost size lead to three segments. V15 and
V16 both scored 25W/19L; their direct matchup split 11–11, and both went 14–8
against V14. Iteration 3 required a four-segment lead for the longer surround
route while retaining three for a two-step cutoff. Its 66 outcomes exactly
matched iteration 2.

Iteration 4 capped surround routes at six steps. V16 scored 25W/19L (75 points)
versus V15's 24W/20L (72 points) and V14's 17W/27L. V16 beat V15 directly
12–10, winning both `big_empty` games while splitting 1–1 on each other map.
Against V14 it scored 13–9; V15 scored 14–8. There were no runner errors.
Artifacts: [results and replays](../build/hunter-v16-iter4-compact-surround/).

### V17: portal-first boosts

V17 is a V16 fork that lets a planned portal move run before boost attacks. In
the same 11-map, both-sides pool, V16 and V17 each scored 23W/21L; V15 scored
20W/24L. V17 tied V16 directly 11–11 and beat V15 12–10. Both V16 and V17
beat V15 in both `big_empty` side assignments; on the remaining maps their
direct results split 1–1. Direct V16/V17 logs show collisions dominate the
500-round maps, with no broad outcome gain from changing action priority.
Artifacts: [results and replays](../build/hunter-v17-vs-v16-v15-small/).

### V18: self-trap lookahead

Replay `M140513` showed Team A's largest dragon reaching length 32 before a
self-collision at round 495. It entered a closing loop in round 490: the east
route had only five safe moves ahead, while west had at least six. V18 forks
V17 and uses a six-move survival lookahead to reject growth routes into such
short pockets; its survival fallback ranks moves by safe continuation depth.
In an 11-map, both-sides pool against V15 and V16, V18 scored 23W/21L, matching
V17's record. It went 12–10 against V15 and 11–11 against V16, the same
pairwise records as V17; all 44 games completed without errors. Map results
shifted: V18 swept V15 on `help` and both opponents on `queen_of_spades`, but
lost both games against each opponent on `queen_of_spades_but_she_ages`; V17
split those pairings. V18 also split `big_empty` against V15, where V17 won both
games. This pool shows no aggregate improvement over V17 or V16, so V18 remains
experimental. Artifacts: [results and logs](../build/hunter-v18-vs-v15-v16-all-maps/).

### V19: safe growth-route selection

V19 forks V18. It checks the six-move continuation from every legal first step
before searching for pearls, so one unsafe best-scoring route cannot suppress
other viable growth routes. When survival moves have the same continuation
depth, V19 prefers the move with more paths at that depth. This remains
experimental. In an 11-map, both-sides, four-bot pool, V19 scored 37W/29L with
no errors. It tied V18 11–11, beat V15 13–9, and beat V16 13–9. V19 swept V18
on `big_empty` but lost both `queen_of_spades` games; the other nine maps split
1–1. Its stronger total came from its baseline pairings, not its direct V18
matchup. Artifacts: [results and logs](../build/hunter-v19-vs-v15-v16-v18-all-maps/).

Keep V16 as incumbent until an iteration demonstrates an improvement over it.
V16 and V15 share weak aggregate records on `default` and `queen_of_spades`;
both lose those pairings against V14, while V16/V15 split their direct matches
on each map. Portal-first priority alone did not fix this weakness. Local
tournaments do not establish judge CPU safety, so sandbox checks remain required
before submission.

## Prioritized work

### P0: improve V16 combat and route selection

1. [ ] Target the inherited `default` and `queen_of_spades` losses. Compare pearl
   growth, route choices, and surviving total length against V14/V15.
2. [ ] Explain the side-sensitive outcomes on `help` with final team lengths,
   portal-trip completion, boost counts, and collision deaths on both sides.
3. [ ] Add a focused regression fixture for the surround route's three occupied
   sides, body-segment retention after boost cost, and two safe exits.
4. [ ] Measure whether offensive boosts reduce pearl growth enough to outweigh
   the trapped enemies. Gate boosts by tactical value as well as size margin.
5. [ ] Keep reporting head-to-head, body, self, and wall deaths by map. They
   dominate many long matches and clarify side-sensitive tournament results.

### P1: team state and combat decisions

6. [ ] Improve enemy team-size confidence before allowing trades based on a
   team-wide lead. Visible heads and sonar echoes do not prove a global count.
7. [ ] Extend shared state with roles and useful pearl/portal observations while
   preserving safety messages such as `MOVE_ASIDE`.
8. [ ] Tune growth transitions using round, team size, largest dragon, pearl
   availability, visible threats, and map type.
9. [ ] Add endgame routing that feeds the largest friendly dragon or protects
   its growth corridor when no nearby threat requires a response.

### P2: routes and map coverage

10. [ ] Compare portal-trip reward per move with ordinary pearl routes before
    committing to a portal journey.
11. [ ] Add a sonar scout handshake: announce the scout, target portal, and
    expected return before entry, then share safe-return/status reports so
    portal knowledge propagates. Treat missing reports as uncertain evidence
    of danger, update a decaying per-portal risk estimate, and gradually raise
    the scout cooldown/threshold as estimated lethality rises; successful
    reports should lower that estimate.
12. [ ] Use remembered pearl observations with age/confidence decay; unseen or
    stale pearls must not be treated as guaranteed food.
13. [ ] Improve territory ownership on segmented maps, especially `schooltime`,
    without suppressing safe exploration by smaller dragons.

### P3: release checks

14. [ ] Run judge-sandbox checks across maps for the selected C++ candidate and
    inspect CPU-limit and invalid-action deaths.
15. [ ] Before submission, rerun a wider tournament with the selected candidate
    against V14, V15, and the strongest older baselines; report map-specific
    records, draws, errors, and replay locations.

## Iteration workflow

- Keep measured bot snapshots unchanged. Make each experiment in a new directory
  and record the hypothesis before editing.
- Compile with C++ warnings enabled, then run the three-bot V15/V16/newest pool on
  all 11 maps, both team assignments (`66` matches), with four workers and a
  600-second timeout. Save replays in a fresh `build/` directory.
- After each iteration, compare total and per-map standings, inspect every
  newest-versus-incumbent match, scan logs for invalid actions and collision reasons,
  and update this backlog with the decision and artifact links.
- Promote a version only when it beats the incumbent in the shared pool and
  does not lose their direct matchup. If a change ties or regresses, retain the
  incumbent and use weak-map replays to choose the next hypothesis.

## Version lineage

| Version | Strategy |
| --- | --- |
| `fry-v01-danger-levels` – `fry-v10-pearl-seeker-center` | Early defense, hunting, portal, and pearl-seeking variants |
| `fry-v11-size-aware-hunters` | Size-aware attacks |
| `fry-v12-stateful-size-aware-hunters` | Persistent map, pearl, and enemy memory |
| `fry-v13-stateful-size-aware-2` | Sonar pearl claims |
| `fry-v14-stateful-size-aware-3` | Closest-teammate pearl ownership |
| `hunter-v01-team-growth` | Team-length estimates and endgame growth, based on fry-v14 |
| `hunter-v02-team-growth` | Adaptive largest-dragon growth with an enemy-size safety buffer |
| `hunter-v03-team-growth` | Portal exploration by smaller dragons when the team can spare scouts |
| `hunter-v04-team-state-sonar` | Directional 64-bit shared dragon state |
| `hunter-v05-safe-attack-routes` | Python port with conservative reachable attacks |
| `hunter-v06-pearl-routing` | Route-based pearl ownership and shorter food routes |
| `hunter-v07-wide-team-state` | Wider sonar IDs and ordered message updates |
| `hunter-v08-pearl-wide-sonar` | V06 pearl routing with V07 sonar |
| `hunter-v09-confidence-team-state` | Freshness-aware teammate lengths |
| `hunter-v10-confidence-enemy-state` | Timestamped enemy-size lower bounds |
| `hunter-v11-route-distance-exploration` | Route-aware teammate spacing |
| `hunter-v12-static-map-spacing` | Static terrain routes for exploration spacing |
| `hunter-v13-hybrid-route-spacing` | Body-aware, static-route, then Manhattan spacing |
| `hunter-v14-cpp-hybrid-route-spacing` | C++ port of V13; experimental due to map-specific losses |
| `hunter-v15-shared-territory` | Shared hotspots, safe portals, and territory exploration |
| `hunter-v16-boost-traps` | V15 plus size-gated boost cutoffs and a compact three-side surround; current measured candidate |
| `hunter-v17-portal-first-traps` | V16 boost attacks yield to planned portal moves; experimental, tied V16 |
| `hunter-v18-self-trap-lookahead` | V17 with six-move safe-continuation checks for growth and survival routes; experimental, tied V17 at 23W/21L in the V15/V16 all-map pool |
| `hunter-v19-safe-growth-lookahead` | V18 with survival-aware pearl-route selection and wider equal-depth survival choices; experimental, 37W/29L in the four-bot pool, tied V18 11–11 |
| `hunter-v20-portal-scouts` | V19 with fresh, near-term hotspot scoring, demand-based single-scout claims, and an eight-step unmatched-portal approach cap; skips scouting on compact boards; experimental, 13W/9L vs V19, 11W/3L on portal maps |
| `kraken-v01-roles` | Fixed-role scouts, hunters, and gatherers relaying map memory over sonar |
| `kraken-v02-bigmap` | Big-map production, brawl-mode small maps, ally-head collision guards, and metered BFS with portal-local cache invalidation |

## Kraken family learnings (2026-09-24)

- The judge sandbox is the source of truth: the same bot/native-opponent mix can diverge from local runs, so every final claim needs a `--sandbox` tournament.
- Portal-rich maps exposed the worst CPU spikes because completing a portal pairing invalidated the whole destination cache. Invalidate only the cells touching that portal edge.
- Reusable BFS stamps and a 450-cell normal-map cap keep kraken-v02 below the 100M turn budget while preserving the full 26–0 sweep over fry-v03.

## Hydra family learnings (2026-09-24)

- Judge budget: every stdout write costs 2.5M CPU points and the sandbox runs Python unbuffered, so a turn's output must leave in one write, including the per-turn `PROTOCOL 3` handshake line.
- A fresh split child's first metered turn must be a cheap boot turn: interpreter boot and imports consume most of the 100M budget; full logic on turn one exceeded it and the kill-restart cascade took out parents too.
- Collision is checked before movement: stepping onto our own tail is always fatal. The body trail must record the midway cell of sprints and must not append on split (no-move) turns.
- The boot turn must check the edge on our side of the neighbour tile (`get_opposite`), not the far side.
- Portal gossip cannot hash portal ids: portal-mesh maps carry about 1500 ids, and 16-bit hashes collide into poisoned pairings.
- fry-v03 does not sprint broadly (95% single steps); its economy edge on big maps is the `plan_trip` beam-search harvest plus constant splitting (children form even under threat). Hydra still loses the length race there about 2:1; porting the trip planner is the main hydra-v03 item.
