# Kraken macro spec — the bot, decomposed

2026-09-24. This is the build specification for the kraken line going
forward: what the subsystems are, what each must do, what the evidence
says, and in what order to build. It supersedes "iterate randomly" — every
experiment should map to one subsystem and one validation signal below.

## 0. What the four reviews establish (the evidence base)

Sources: `docs/family-comparison.md` (Kimi, rr1 + replay profiles),
`docs/cross-line-review.md` (GLM, rr2 clean 260-game RR + forensics),
`docs/leviathan/DESIGN.md` + `RESULTS.md` (GPT, method + measured deltas),
`docs/ouroboros-design.md` + Claude's status note (97-15 cross-series pool;
sandbox p50 29M / p99 48M / max 62M — judge-safe, refuting my earlier
"untested at the meter" criticism).

Points of **agreement** across all reviews:

1. Ouroboros wins by *not dying*: fewest deaths/game (111 vs 180-210),
   zero wall deaths, while splitting *less* than the field. The game is a
   deaths-war as much as a births-war.
2. Two win conditions = two games: swarm/attrition war for ~450 rounds,
   then a longest-dragon race. Kraken is already the length-race
   specialist (most length wins, best tiebreak rate 16/46 in rr2) but
   loses elimination races (61% of deaths are body collisions).
3. Architecture has converged: world model → candidate enumeration →
   single weighted evaluation → argmax; roles as weight slices; all
   constants swept by tooling.
4. 2-segment children are the meta; Python is fast enough if the meter is
   engineered (all three Python lines are judge-safe when disciplined).
5. Determinism: side-swapped map cases are exact matchup measurements,
   not statistical samples. Small-map results generalise poorly.

Points where the reviews **complement** each other:

- GLM: kraken's one-sonar-per-turn policy is self-imposed (the field now
  broadcasts 2-4 slots); ouroboros's side-B fragility (13/14 losses as
  side B) shows initiative modelling matters; fry/hunter/hydra C++ family
  self-harms at ~1/3 of deaths — structural tax of the priority ladder.
- GPT: net-material accounting (sprint cost vs gross pearls) was their
  biggest single win; equivalence testing catches silent behaviour drift.
- Claude (status): known weak spots — small maps vs C++ swarms decided by
  round-50 unit count; corridor-map farming tradeoffs; untried: opponent
  strike-propensity learning, 2-ply contact search, map-type detection.

## 1. Subsystem breakdown

Each subsystem: purpose → design decision → key parameters → validation
signal (the replay/log metric that proves it works).

### S1. Objective & phase model

**Purpose:** every decision must know which game it is playing.
**Design:** four phases with explicit boundaries: `early` (land grab,
production-heavy), `mid` (swarm war, trade discipline), `late`
(consolidation, split freeze), `end` (crown race, length value ramps).
Phase is a function of round AND state (team units, known beds, enemy
contact), not round alone — big_empty's economy runs 100 rounds behind
arena's. Length value ramps from 1.0 to ~3.0 per segment across the end
phase so the eval smoothly converts from war to race.
**Parameters:** phase boundaries per map class, `len_value_end` ramp.
**Signal:** length-tiebreak win rate (keep kraken's 16/46-class rate);
elimination losses before round 300 (drive down).

### S2. Control flow (per-turn pipeline)

```
PARSE     wire -> world model diff            (fixed cost ~10M)
LISTEN    sonar packets -> memory             (cheap)
ASSESS    phase, threat field, doom map, goal field   (capped)
ENUMERATE candidates: 4 steps + gated sprints + strikes + split
EVALUATE  one scalar per candidate, length units
ACT       argmax -> MOVE/SPLIT + sonar out    (ONE stdout write)
```

Hard rules: exact legality simulation before scoring (collision is
checked before the tail vacates; sprints pay per step; stale pearls cannot
*fund* a sprint — Leviathan v06's lesson); a least-bad fallback ladder
when everything dies, tagged `trapped` so autopsies can separate "bad last
move" from "bad decision three turns ago" (GPT's insight); cheap boot turn
for split children (interpreter boot eats the first-turn budget).
**Signal:** zero noaction deaths; `trapped`-tagged deaths counted in
autopsy, trend down.

### S3. Production & specialisation

**Design decisions:**
- **All children are 2 segments.** Role-at-birth by size (kraken's
  current scheme) pays 50% more per hunter for a label the parent→child
  sonar hand-off delivers for free (Ouroboros verified the back-ray lands
  on the newborn). Cornered "shed the body" splits stay as an escape
  hatch but are not the production mechanism.
- **Roles are weight slices over one eval**, assigned at split time from
  a phase-scheduled mix (Ouroboros's early 45/25/30 gather/hunt/scout is
  a proven starting point), handed over by sonar. Roles: gather, hunt,
  scout (only on maps > 600 cells), crown.
- **Team-size target scales with map class and phase**, and production is
  an *evaluation* (split value = marginal unit value − risk here −
  crowding), not a fixed ladder. Small-map weakness is decided by
  round-50 unit count (Claude's data): early production must be near-
  maximal on small maps.
- **Crown**: from ~round 200 the longest known dragon stops splitting,
  refuses trades, loads survival weights (Ouroboros's crown_memory=40
  staleness caveat applies: dead crowns must expire fast).
**Parameters:** role mixes per phase per map class, team targets, crown
start/freeze rounds.
**Signal:** round-50 unit count vs opponent (from replay curves); splits/
game ~130-210 range; final longest ≥ opponent's in round-limit games.

### S4. World model & information propagation

**Memory layers:** static terrain + portal pairings (learned once,
local cache invalidation — v02/v07 lesson), pearl beds with spawn
predictions from observed countdowns, remembered pearls with staleness,
enemy sightings with decay, ally self-reports, and a **persistent doom
map** (corridors that killed allies stay marked ~200 rounds —
Ouroboros's zero-wall-death module).

**Sonar budget (4 slots, not 1):** GLM is right that kraken's single
rotating cast is self-imposed austerity. Allocation: one rotating radar
sweep (echo attribution requires a single cast per direction per turn —
keep this discipline *per direction*), one status/self-report, one enemy
sighting or doom report, one relay (TTL 2). Trust horizons from hydra:
gossip sightings stale after ~15 rounds, chase horizon ~6 path steps —
far chases starve.

**Pearl density tracking:** maintain a census — beds discovered, observed
spawn countdowns, pearl field integral over explored area — yielding an
economy estimate (pearls/round accessible). This feeds S3 (how much
production the map supports) and S6 (camping value of fertile ground) and
S7 (whether a corpse-economy brawl is sustainable).
**Signal:** pearls eaten per game vs opponent (ouroboros eats ~2x its
opponents; kraken currently loses this 1398 vs ouro's 1528 with MORE
splits — conversion gap).

### S5. Threat & safety (the deaths-war module — build first)

Kraken's measured leak: 100.5 body-crash deaths/game, 29.4 wall
deaths/game. Design:
- **Probabilistic strike model** replacing binary danger: an enemy head
  at distance 1/2/3 prices p≈0.75/0.35/0.15 × my value (Ouroboros's
  constants, sweepable). Split-able enemies add a newborn-strike term.
- **Initiative accounting:** move order alternates within a round; side
  B loses more across the field (ouroboros 13/14 losses as B). Track
  whether each visible enemy has already moved this round where the wire
  allows; price accordingly rather than treating all enemies as
  pre-move (kraken's current conservative approximation).
- **Doom memory:** corridors that killed an ally (observed or gossiped)
  are marked; entering one requires the exit to be verified open.
- **Exit counting:** 0 or 1 uncontested free neighbours at the
  destination costs points (w_exit0, w_exit1).
- **Traffic terms:** ally head/body adjacency and crowding penalties —
  kraken's swarm kills itself more than any opponent does in dense games.
**Signal:** deaths/game mix — target: body < 40/game, wall < 5/game,
self < 10/game at equal unit volume; elimination-loss rate.

### S6. Targeting: exploration vs exploitation

One target field, not modes: `value(cell) = w_pearl·confirmed +
w_spawn·prediction_decay + w_frontier·unexplored + w_hunt·sighting_heat +
w_ray·echo_heat − w_dist·steps`, role-weighted. Reverse BFS from the
chosen target gives per-candidate goal progress (Ouroboros), replacing
kraken's single-direction compass. Explore/exploit balance is emergent:
frontier weight high for scouts and early phase, decaying as the census
(S4) completes; pearl weights dominate once beds are mapped. Spread term
from gossip positions with a crowding cap (fry-v14's pearl-ownership
deconfliction is table stakes; keep it vision-local — hydra's map-wide
yielding starved big_empty).
**Parameters:** all field weights, BFS caps (CPU-gated), spread cap.
**Signal:** pearls/game; frontier completion time (round when <5% edges
unknown); idle-turn rate in autopsy.

### S7. Aggression policy

**Trade evaluation in length units:** `V(trade) = their_len·len_value −
my_len·len_value − unit_value·(1 + scarcity/units) + role_bonus`, gated
by phase (endgame: only trade up; brawl: trade anything not strictly
shorter — kraken's corpse-economy mode, keep it) and refused entirely by
the crown. Strike paths: ≤3 steps, every intermediate tile verified clear
NOW, MOVE resolves atomically so the target cannot dodge (kraken's
existing strike correctness is good; keep it).
**Pack hunting:** gossip enemy sightings (2 slots) with 15-round trust
and 6-step chase horizon; hunters within horizon bias target field
toward the sighting (hydra-v06's one proven combat win).
**Untried, scheduled for later:** opponent strike-propensity learning
(adjust p_strike per opponent family via observed trades), 2-ply contact
search (Claude's list — CPU-permitting only).
**Signal:** h2h up/even/down ratio (kraken currently 6/16/10 in the
deep-dive loss — too many down-trades); deaths inflicted per death taken.

### S8. Compute budget architecture

- Hard gates at promotion: sandbox p99 < 60M, max < 85M, zero
  over-budget turns (kraken-v03 worst: 96M — too close).
- Per-subsystem caps: BFS expansions, threat layers, doom search,
  reverse BFS — all stamped/capped (existing kraken pattern, keep).
- One stdout write per turn (2.5M per write); `gc.disable()` (Ouroboros).
- Local wall-clock is NOT the judge budget, but >180s Python games break
  fast harnesses: pool runs use `--timeout 1200`, screen stays native.

### S9. Validation plan (the loop, formalised)

```
1. Hypothesis maps to ONE subsystem above. State it in the variant note.
2. Equivalence check where applicable (Leviathan contract): refactors
   must reproduce the parent action stream on fixed cases.
3. screen  (kbench): 4 maps x 3 opponents, native — kill bad ideas.
4. bench   (kbench): 6 maps x 6 opponents, sandbox — confirm + CPU gate.
5. autopsy (replaystats/family_report): the subsystem's signal metric
   must move; no regression in deaths/game mix.
6. pool    (kbench): full 13 maps x field — generality check.
7. Promote: beats predecessor on the same pool; commit with numbers.
```

Anti-goals: no multi-subsystem variants; no promotion on native-only
data; no "improvements" that move no autopsy metric.

## 2. Build order

| version | subsystem | hypothesis | kill/promote metric |
| --- | --- | --- | --- |
| kraken-v05 | S5 threat & safety | probabilistic threat + doom memory + exit terms cut body/wall deaths | deaths/game 179→<140; wall <5 |
| kraken-v06 | S3 production | 2-segment children + sonar role hand-off + crown from r200 | round-50 units up; final longest up; 13-13 vs fry14 becomes >15-11 |
| kraken-v07 | S7 aggression | pack hunting + trade-eval scarcity pricing | h2h up-trades exceed down-trades |
| kraken-v08 | S4/S6 economy | census-driven production and camping | pearls/game ≥ opponent median +20% |
| each | S9 | sandbox CPU gate + equivalence where refactor-only | p99 < 60M, 0 errors |

First concrete step: kraken-v05 = v04-eval + S5 (probabilistic strike
pricing, persistent doom map, exit counting, traffic terms), all weights
in CFG, screened then benched against fry-v14, ouroboros-v05,
kraken-v03.
"""
