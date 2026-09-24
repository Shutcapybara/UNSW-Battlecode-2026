# Ouroboros design framework

Ouroboros is Claude's bot series (`bots/ouroboros-vNN-*`). This document is
the contract every version follows: what the game reduces to, the per-turn
loop, the roles, the evaluation function, and the iteration method. The
tooling lives in `tools/ouroboros/` (see its README).

## 1. What the game reduces to

Facts that drive every design decision (engine source + docs + our replays):

- **One process per dragon.** No shared memory. A split child is a new,
  blank process. The only channel is sonar: up to four uint64 rays per turn
  (N/E/S/W), each stopping at the first dragon it hits (either team).
- **Parent -> child hand-off.** A ray fired back into our own body exits at
  the tail and lands on the newborn's head (it sits right behind the tail).
  So on the split turn the parent can hand the child 64 bits: role, target,
  anything. Verified in-engine (`/tmp/sonartest`, see git history).
- **Combat is symmetric.** Head onto head kills both, regardless of length.
  Head onto a body kills only the mover. So every kill we make by striking is
  a 1:1 unit trade; the only *free* kills are enemies that die on walls,
  bodies or themselves. Length is not armour.
- **Initiative.** After our move, every enemy gets exactly one action before
  our next one. Ending a turn inside an enemy head's sprint reach hands it the
  choice to trade. Whoever blunders into reach gives the other side the
  option.
- **Economy.** Pearls are the only income; units multiply income (vision,
  parallel foraging, one action each). The strongest bots in the pool
  (hunter-v04, hunter-v03, hydra-v06, fry-v12) are swarms of 2-4 segment
  dragons that split at every opportunity: on devil, hydra-v06 split 384
  times in one game.
- **Two win conditions.** Elimination (most games on small maps), or at
  round 500 the longest single dragon, then total length. A swarm wins the
  first, a crown wins the second; the transition matters.
- **Terrain.** Kelp corridors (devil, default_small) make 1-wide tunnels; two
  dragons meeting head-on in a tunnel means at least one dies. Our own
  traffic is a real killer.
- **CPU.** 100M points per dragon per turn under the judge; Python is
  expensive (kraken-v03 p50 37M). Every search is capped; one stdout write
  per turn (a write costs 2.5M).

## 2. The core loop

```
SENSE     parse wire -> world model (edges, portals, pearls, beds + spawn
          predictions, sightings, zone heat)
LISTEN    sonar packets -> allies, enemy sightings, portals, beds, hand-off
ASSESS    threat map (every visible enemy head's sprint reach), contested
          tiles (next to any head), goal target (role-weighted target search)
SEARCH    candidate actions: 4 single steps always; 2-3 step sprints only when
          an enemy head is near or step one eats a pearl; SPLIT when legal
EVALUATE  one scalar evaluation per candidate (section 4)
ACT       argmax -> MOVE/SPLIT, then sonar (gossip or child hand-off)
```

SENSE/LISTEN/ACT are infrastructure. The product is ASSESS + EVALUATE, and
all of it is parameterised in `P` / `RP` at the top of `main.py`.

## 3. Roles

A role is not separate logic; it is a slice of the evaluation weights (`RP`).
The parent picks the child's role at split time (team mix by phase, from
gossip counts) and hands it over by sonar.

| role | purpose | risk | target weights |
| --- | --- | --- | --- |
| gather | income: pearls, predicted spawns, safe zones | high aversion | pearl/spawn high, zone danger negative |
| hunt | contest: enemy sightings, hot zones, borders | low aversion, trades even | enemy sightings, hot zones |
| scout | information: stale zones, frontier, gossip | medium | frontier, staleness |
| crown | endgame length race | maximal aversion | pearls only, refuses trades |

Specialisation axes (all parameters): risk multiplier, trade margin, target
weights, spread, zone danger sign. Phase mix: early = many scouts/hunters,
mid = hunters/gatherers, late = gatherers, end = crown.

## 4. The evaluation function

Everything is in *length units* (one segment = 1 at the start, ramping to
`len_value_end` in the endgame so the length race dominates late).

```
V(move)   =  material        lv * (len_after - len_now)           sprint cost, pearls eaten
           - sprint          w_sprint * (steps - 1)                 sprints burn production
           - risk            P(struck before next turn) * loss      threat map, per enemy head
           - trap            w_trap * missing escape space         flood fill from the new head
           - exits           w_exit0 / w_exit1                      0 or ~1 free neighbour after move
           - dead end        w_doom * V(me), or w_doom_farm when    region enclosed & too small/acyclic;
                             len + pearls inside >= farm_len       a farm if we can grow and split out
           - tunnel          w_tunnel_head / _body / _unknown       a head or body in the 1-wide tunnel ahead
           + goal            w_goal * (dist_now - dist_after)       reverse BFS from the chosen target
           - traffic         ally head / body adjacency, w_crowd * ally segments within 2
           - dither          w_visit * visits
           + spread          role-weighted distance to gossip allies
V(strike) =  V(enemy) - V(me) + role bonus, gated by the role's trade margin
             (crown-kill: any enemy at least as long as our longest, late)
V(dive)   =  w_dive - dive_risk (+ w_dive_idle with nothing to chase)   unpaired portal
V(split)  =  w_split * (1.2 - units/target) - 0.5 * risk_here
             only if the newborn has a way out, units < target, window not crowded,
             no crown; an emergency split (all but 2 segments) when every move is fatal
V(dragon) =  unit_value + lv * length

target    =  argmax over BFS cells of  role weights x (pearl, predicted spawn,
             frontier, unpaired portal, enemy sighting, zone danger) - w_dist * steps,
             pearls discounted (own_disc) when another head is clearly closer;
             else a strategic waypoint (zone scan: stale / hot / rich-safe / uncrowded)
```

Rules:

1. **Every number is a parameter.** New behaviour = new feature with a weight
   (default neutral), not a new branch.
2. **Features are pure functions of the world model**, computed once per turn
   where possible (threat map, contested set, target, reverse distances).
3. **Exact safety first.** Candidate paths are simulated with engine rules
   (collision before tail move, sprint payment, pearls). Illegal = never
   chosen unless every option dies (then least-bad fallback, logged).
4. **Judge budget is a constraint, not a feature.** Caps on every search;
   sandbox-check every promoted version.

## 5. The iteration loop

```
OBSERVE     ouro.py report / autopsy     -> where and why we lose
HYPOTHESISE one mechanism, one sentence
ADAPT       param override (name@k=v) or a code change in a new version dir
SCREEN      ouro.py run CAND --pool <3-4 strong> --maps quick   (fast, non-sandbox)
BENCHMARK   ouro.py run CAND --pool <bench pool> --maps full
PROMOTE     beats the previous version on the same pool, sandbox CPU p99 < 60M
            -> copy to bots/ouroboros-vNN-name, note numbers in its README
```

- One hypothesis per variant. Parameter variants never touch committed bots
  (they are generated under `build/ouro-variants/`).
- The number to beat is always the previous ouroboros against the same pool.
- Determinism: identical bots on identical maps replay identically, so small
  samples are exact for that matchup but say nothing about generality; the
  full map set and several opponents are the generality check.

## 6. What the data taught us (v01 -> v10)

Every number below is from `ouro.py compare` on identical matchups.

| lesson | evidence |
| --- | --- |
| Non-combat deaths are mostly **our own traffic**: len-2 dragons meeting head-on in 1-wide tunnels, and packed bases where allies box each other in. | `deaths.py`: devil 100 forced deaths/game in v01, all with an ally head in front; stronghold 43 body deaths, all against our own bodies. |
| **Sprinting burns production.** | arena: 37% of pearls went into sprint costs before `w_sprint`. |
| **Leave pearls to a clearly closer head** (ownership). | small-map screen 5-7 -> 7-5; with the traffic fixes, 24-24 -> 40-8. |
| **Walled bases need portal exploration**: stepping through an unpaired portal is the only way to learn where it goes. | stronghold/trauma: units never left home; v05 dives: trauma 2-12 (v01) -> 13-0. |
| **Crown = stop splitting, not stop fighting.** A passive crown (risk 3, refuses trades) lost whole teams; "no split once a crown is known" works. | v02 first try 146-46; fixed 159-36; trauma 2-8 -> 7-3. |
| **Stop splitting earlier on length-race maps** (380 not 420). | help/stronghold/schooltime/qos-ages/trauma 19-11 -> 23-7. |
| **Dead-end corridors with pearls are farms**: go in, grow, split, the child walks out. Plus an emergency split whenever every move is fatal. | devil family (x3 variants, 4 opponents) 3-21 -> 10-14. |
| Small maps are decided by round 50 (units 12.7 vs 4.2 in wins, 5.9 vs 12.6 in losses), and by then the pearl race is what differs (rounds 0-30: 27.6 vs 11.5 pearls in wins, 21.8 vs 23.0 in losses). The C++ opponents play identical openings, so a (map, side) is won or lost against all of them alike. | `sw-small` curves, `phase.py` |
| **Don't leave pearls to enemy heads**: the ownership discount must count allies only. | arena frames: 30+ uneaten pearls beside our dragons; v08 vs C++ swarms 141-57 -> 156-42 (widefast). |
| **At round 500 only the longest dragon counts**: small dragons should die beside the crown (their corpse is pearls it eats). | v09-feed: 219-42 -> 234-27 (widefast x cross-series). |
| **One crown, located**: crowns chosen from local hearing multiply (5 crowns of length 2-6 at round 480); a relayed crown beacon + demotion + crown hand-off on emergency splits make it one big crown, and feeding can find it. | v10-beacon: 238-23; vs kraken-v04's 36-41 length crowns 56-7 -> 60-3. |
| Many "obvious" fixes are map trade-offs: commitment bonus, sticky waypoints, stale-spawn beds, blind-portal penalty each won one map family and lost another. | v03 rejected (111-33 vs 118-26); blind portal 97-15 -> 90-22. |

| **Compact maps are a production race the evaluator cannot win**: its gatherers eat 0.12 pearls per dragon-turn to hunter's 0.17; 40% of decisions with a pearl within 3 steps chased a predicted spawn or an enemy sighting, and the pearl step lost to crowd / ally-head / risk penalties. Every single evaluator knob stayed within noise; playing hunter's ladder (attack up, split at 4, nearest owned pearl, spaced exploration) on compact maps only is +34 net. | v13-ladder: compact 65-1-54 -> 99-1-20; hold-out 43-1-36 -> 61-1-18; `econ.py`, `explain.py`. |
| **Half of all hand-offs never arrive**: the refracted ray leaves the tail in the direction it came, so it reaches the child only when the last three segments are straight. The resulting "orphan hunters" are load-bearing on compact maps (making them gatherers: 36-54 -> 25-65). | `explain.py` role census; `orphan_role` screen. |

Method lessons: one mechanism per version; judge on the full map set *and*
the transposed/flipped variants (`--maps wide`), since a change routinely
moves one map +4 and another -4; screen fast on the maps where the mechanism
shows, then confirm broadly.

## 7. Benchmark pool

From the 540-match round robin on the quick map set (`baseline-rr`):

| bot | score | language |
| --- | --- | --- |
| hunter-v04-team-state-sonar | 0.713 | C++ |
| hunter-v03-team-growth | 0.685 | C++ |
| hydra-v06-echo | 0.648 | C++ |
| fry-v12-stateful-size-aware-hunters | 0.639 | C++ |
| fry-v14-stateful-size-aware-3 | 0.620 | C++ |
| kraken-v03-judge-safe | 0.472 | Python |
| fry-v07-two-children | 0.444 | C++ |
| fry-v03-portal-hunters | 0.435 | C++ |
| hydra-v03-grower | 0.343 | Python |
| leviathan-v01-evaluator | 0.000 | Python |

Bench pool (older, saturates near 0.82): the top five plus kraken-v03 and
fry-v03. Cross-series pool (the other AI series' latest, the one that
discriminates now): hydra-v10-farmclean, hydra-v09-lanchester,
kraken-v04-eval, leviathan-v07-local-cache.

## 8. Version history

| version | idea | bench (7 old bots, 14 maps) | cross-series |
| --- | --- | --- | --- |
| v01-eval | evaluation function, roles, hand-off, traffic/tunnel/doom checks | 158-38 | - |
| v02-crown | crown stops splitting from round 200 | 159-36 | - |
| v03-forage | commitment / sticky waypoint / stale spawns (rejected) | 111-33* | - |
| v04-race | splits stop at 380; small maps all-gatherer early | 158-37 | 85-27 |
| **v05-spread** | crowd terms, split crowd cap, portal dives, CPU trims | **162-32** | **97-15** |
| v06-lanchester | local head-count trade bias, incentive-aware strike odds (rejected) | - | - |
| v07-forage2 | dead-end farming, emergency split, spawn window 25 | 142-38* | 49-14* |
| v08-contest | ownership counts ally heads only; farming only for small dragons | 156-42 (C++ swarms, widefast) | 219-42 (widefast) |
| v09-feed | endgame: small dragons die beside the crown | 164-34 (C++ swarms, widefast) | 234-27 (widefast) |
| **v10-beacon** | relayed crown beacon, crown demotion / hand-off, stronger feeding | see README | **238-23** (widefast) |

| v11-opening | split spawn window (null result) | - | - |
| v12-core | v10 split into modules; doctrine per map class; ladder / hotspot / orphan knobs (all off) | action-stream equivalent to v10 (16/16) | - |
| **v13-ladder** | compact maps: hunter-v20's ladder + our vetoes + K_HOT hotspots | gauntlet G+V **214-1-25** (v10 180-1-59); compact 99-1-20 (v10 65-1-54); compact hold-out 61-1-18 (43-1-36) | - |

\* on the common subset of a partial run. "widefast" = 33 maps (originals
+ transposed + flipped, without the two 64x64 maps), both sides.
v13-ladder is the current Ouroboros candidate (cycle 1); v10-beacon is its open-map behaviour.
