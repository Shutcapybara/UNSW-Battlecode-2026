# Macro spec — the next bot, designed rather than drifted

2026-09-25. Inputs: four family reviews (`docs/cross-line-review.md` GLM,
`docs/family-comparison.md` Kimi, `docs/leviathan/` GPT, Claude's ouroboros
status report), the round-robin replay data in `build/crossline-rr2`, and
each line's own ledgers. This document is the build spec for a new bot that
incorporates every mechanism the evidence supports, with acceptance gates so
implementation proceeds by measurement, not by mood. It supersedes
`docs/design-framework.md` (its own author retired the stale parts).

## 0. What the evidence actually says (design-shaking facts)

1. **The winner wins by not dying.** ouroboros-v05: 111 deaths/game vs
   192-210 for the field, 11% self-harm, **0.0 wall deaths** (persistent
   doom memory), while eating ~2x the pearls of each opponent — and it
   splits LESS than everyone (127/g). Field rank order == deaths-avoidance
   rank order, almost exactly.
2. **The ladder is the liability.** The fry/hunter/hydra C++ priority
   ladder self-harms on ~31% of all deaths. A single evaluation function
   over simulated candidates (ouroboros) or enumerated paths (leviathan)
   eliminates most of it.
3. **The two-game structure decides.** ouroboros wins eliminations (65)
   AND length tiebreaks (25; final longest 8 vs field's 3-6). A bot that
   only wins one game loses the format.
4. **Roles are cheap; role-carrying material is not.** Everyone splits
   2-segment children except kraken, whose 3-segment hunters cost 50%
   more per unit for a label that sonar hand-off carries for free
   (parent's back-ray lands on the newborn — engine-verified by ouroboros).
5. **Information propagation matters less than information discipline.**
   Gossip-chasing beyond a short horizon starves (hydra v07, kraken's own
   finding); ouroboros gossips modestly and still wins; leviathan uses no
   radio and loses on attrition, not on information. The radio's proven
   value: status (production parity), doom reports (survival), hand-off
   (roles), enemy sightings (pack hunting, with a hard chase horizon).
6. **Small-map games are decided by round ~50 on unit count** (Claude's
   own weak-spot note; consistent with my Colloseum curves: fry 22 units
   vs hydra 2 at r51). Production schedule is a first-order system, not a
   parameter.
7. **Determinism is an asset**: the engine replays (map, botA, botB)
   identically — one both-sides pass is an exact measurement; variance
   comes only from opponent pool and map set. Generated map variants
   (Claude's mapgen transpose/flip) are the only true holdout test.

## 1. Objective

Lexicographic, from the rules:
1. never be eliminated (unit count is life — every mutual kill is 1:1 but
   proportional damage differs),
2. at round 500 win the longest-single-dragon tiebreak,
3. then maximise total team length.

Everything below serves that: a swarm engine for game 1, a crown engine for
game 2, and an explicit switch between them.

## 2. Architecture (per dragon, per turn)

```
SENSE      wire -> world model (terrain edges, portal pairs, pearl beds +
           countdowns, sightings, ally reports, doom memory)
LISTEN     sonar packets -> fold (status, gossip, doom, hand-off)
ASSESS     phase; threat map (probabilistic); target field per role;
           contested/crowding sets; pearl-density field
GENERATE   candidates: 4 single steps; gated 2-3 step sprints (enemy head
           near, or step 1 eats); strikes; portal dives; SPLIT as candidate
EVALUATE   one linear evaluation in LENGTH UNITS over simulated end-states
ACT        argmax -> emit action; then sonar (4 slots, channel policy)
```

No priority ladder for movement. The only preemptions are the boot turn
(turn-1 children: one cheap step + hello) and the emergency fallback when
no candidate survives (least-bad, logged via INDICATOR).

Rationale: ladder bots self-harm at 31% (fact 2); the eval must price every
action against the same survival terms so "greedy pearl" and "safe" are
never decided by code order.

## 3. The evaluation function

`E(a) = Σ wᵢ·fᵢ(a)` in length units (a segment is the currency; unit value
`unit_value` ≈ 4 segments early, ramping so length dominates late —
ouroboros's `len_value_end` trick, validated by its length-tiebreak record).

**Material** (net, per leviathan's correction — the field's best accounting):
- `pearl_eaten` minus `segments_spent` (sprints pay; three pearls in three
  steps = one net segment),
- `trade`: V(enemy) − V(me) + scarcity term (−k/units), gated by role
  margin; last-unit never volunteers.

**Risk** (probabilistic — the validated core of ouroboros's win):
- `P(struck)·V(me)` per enemy head within sprint reach, with strike
  propensity by distance (p≈.75/.35/.15) and a learned per-opponent
  propensity (see §6); newborn-at-tail probability for splittable enemies;
- `doom`: corridor dead-end memory, persistent ~200 rounds, shared over
  sonar (this alone took ouroboros to zero wall deaths);
- `exits`/`crowding`: 0/1-free-neighbour penalties; ally-head adjacency;
  ally segments within 2.

**Space**: flood-fill freedom capped at length+slack with trap cliff.

**Goal**: reverse-BFS distance gradient to the role's chosen target
(forward BFS caps: ~180 cells target search, ~320 reverse).

**Tempo**: visit decay, facing momentum, id-seeded jitter (anti-lockstep).

Hard rules: every feature bounded; every weight in one params block with a
one-file override mechanism; features are pure functions of the world
model; adding a feature never changes movegen.

## 4. Specialisation (roles)

**Roles are weight slices + a hand-off, never size and never code paths.**
Children are always 2 segments (fact 4). On the split turn the parent's
back-ray hands the child 64 bits: role id + target hint (channel §6).

- `gather` — income: pearl/spawn weights high, zone-danger aversion.
- `hunt` — contest: sighting heat, pack targets, trade margin 0.
- `scout` — information: frontier weight, staleness attraction; only
  spawned on maps above a cell threshold (small maps: no scouts —
  ouroboros's `scout_min_cells`, correct by round-50 evidence).
- `crown` — elected, not born: from `crown_start` (~round 200) the longest
  healthy dragon stops splitting, refuses trades, farms predicted beds;
  `crown_kill_round` (~380): everyone strikes an enemy that out-lengthens
  our crown. Crown loss is gossiped immediately (fix ouroboros's
  40-round haunting).

Phase schedule (weight interpolation, no code branches): early
gather/hunt/scout ≈ 45/25/30 (big maps) or 100/0/0 (small); mid ≈ 45/45/10;
late ≈ 70/30/0. **Split-size identity: all children 2.**

## 5. Production schedule (the numbers war, first-class)

The round-50 collapse is a scheduling bug in every losing bot. Make the
team-size trajectory explicit:

- `team_target(t, map_cells)`: piecewise target curve; small maps must hit
  ~20+ units before round 50 (production peaks EARLY), big maps ramp to
  60+ by round 120. Hydra-v06 peaked at 14; ouroboros 25-33; that delta is
  the numbers war.
- Split gating (already validated): parent length ≥ 4, no voluntary split
  under head-risk > threshold or ally-crowding > threshold.
- **Reproduction beats replacement**: eat-to-4 then split-2 keeps the
  parent at breeding length; the forage loop must prefer breeding-length
  restoration after splitting (my v06-v10 dragons sat at 2-3 pearls
  eaten/game — the exact starvation signature).
- Freeze: voluntary splits stop at `split_stop` (~380), earlier if the
  crown is fat and the enemy cannot contest it.

## 6. Information propagation (protocol 3, four slots)

Channel allocation per turn (priority order):
1. **hand-off** (split turns only) — role + target to the newborn;
2. **status** — id, head, length, crown-flag (drives production parity and
   crown election; hydra proved the status channel is load-bearing);
3. **gossip** — biggest 1-2 fresh enemy sightings, **chased only within a
   6-path-step horizon** (far chases starve: hydra v07 + kraken concur);
4. **doom reports** — corridor deaths, TTL ~10 (ouroboros localises it;
   sharing it is free survival for the swarm);
5. **bed discoveries** — low priority, relay with TTL and dedup
   (kraken's protocol is the reference implementation).

Untried, spec'd for phase 5: **strike-propensity gossip** — when a dragon
observes an enemy take (or refuse) a strike, pack the observation into the
gossip slot; the threat model's p_strike becomes per-opponent learned
instead of global constants. Cheap, bounded, and directly addresses the
"model aggression probabilistically" insight that is currently fed by
hand-picked constants.

Anti-pattern to avoid (v10's lesson): a locally-sensible flee/avoid term
applied swarm-wide becomes a map-wide reflex that abandons contested food.
Any avoidance term must be gated by role and phase.

## 7. Economy — tracking pearl density

- **Bed model**: every observed countdown seeds a spawn prediction
  (countdown -> expected round); predictions decay (`spawn_horizon`);
  fertility remembered forever (terrain, static).
- **Density field**: the target search scores beds by (predicted time-to-
  pearl, distance, local density) — gatherers camp high-density regions we
  control (the user's original space-control idea, kept).
- **Ownership/deconfliction**: a pearl is pursued only if no visibly
  closer teammate wants it (`owns_pearl`, fry-v14; ouroboros's own_disc);
  duplicate chasing is pure waste in a food race.
- **Corpse economy**: on countdown-poor maps, deaths ARE the food; after a
  nearby death, corpses outrank distant beds for ~20 rounds. Map-type
  detection (fraction of countdown tiles below threshold → "arena/corpse
  mode") switches farming emphasis — Claude's v07 farming helped devil but
  must be conditional, not global.
- **Leviathan's stale-pearl rule**: remembered pearls are targets but
  never fund sprint payment; only this-turn-observed pearls fund legality.

## 8. Aggression & combat doctrine

- Default posture: **trade only bigger** (table stakes), and only at
  production parity — while behind on units, strikes are disabled and
  movement biases away from fresh enemy positions (v09's mechanism,
  refined: it flipped default both sides but must NOT run on maps where
  our income is ahead — gate it on the production schedule, not on fear).
- **Pack hunting**: gossip sightings converge the pack within the 6-step
  horizon (hydra's one proven superior behaviour: it took 3 of
  ouroboros's 14 losses).
- **Contact discipline**: strikes require exact simulation of the path
  (ouroboros's atomic-resolution insight: our MOVE resolves first, the
  target cannot dodge a head-tile landing).
- **Crown killing**: after `crown_kill_round`, an enemy dragon at least as
  long as our crown is struck on sight regardless of size gates — the
  length tiebreak is the game.

## 9. Safety & judge budget (engineering constraints, not features)

- Exact candidate-path simulation (collision before tail-vacate, sprint
  payment, mid-step pearls); illegal paths filtered, never scored.
- One stdout write per turn including the `PROTOCOL 3` line; `gc.disable()`;
  boot turn for children; every search capped and stamped.
- Promotion gate: sandbox p99 < 60M on big_empty + a corridor map + an
  arena (ouroboros measured 29/48/62M p50/p99/max — that is the bar);
  wall-clock: python pools need `--timeout 1200` locally (180s default
  DNFs help-map games and corrupts comparisons).

## 10. Exploration vs exploitation

- Frontier value decays with map coverage fraction; `visit` penalties and
  id-jitter break lockstep loops.
- Exploitation gradient: predicted spawns > live pearls > fertile camping
  > frontier. Scouts buy information only while `coverage < ~70%` and only
  on maps above the scout threshold; afterwards they re-role to gather.
- Radar (echoes) is free exploration: one cast/turn doubles as a sweep and
  the gossip carrier (kraken's trick) — but 4-slot protocol 3 status is
  worth more than echo attribution; cast for echo only when no gossip is
  queued.

## 11. Measurement protocol (what makes this non-random)

1. Benchmark = fry-v14 + all four line champions, all 13 maps, both sides
   (`--timeout 1200`). That fixture is the number to beat; nothing
   single-map counts.
2. Generalisation check on generated map variants (Claude's mapgen
   transpose/flip) before promoting anything tuned on the 13.
3. One hypothesis per variant; variants are new directories; ablate
   stacked changes (the v07-v10 cycle's failure mode).
4. Replay forensics on every loss: deaths/game, self-harm %, pearls vs
   opponent, splits, win type (elim/length), side. The four style metrics
   to hold fixed while tuning anything else: deaths ≤ 130/g, self-harm
   ≤ 15%, pearl ratio ≥ 1.5x opponent, both win types present.
5. Written claims only from run artifacts; deterministic engine = exact
   matchup numbers, pool = the generality check.

## 12. Build plan (phases with acceptance gates)

- **P0 skeleton**: world model, exact simulation, candidate eval with
  gather-only weights, no radio. Gate: survives to r500 on all maps,
  self-harm < 20%, CPU p99 < 60M sandbox.
- **P1 survival**: threat map + doom memory + exits/crowding + exact
  strike pricing. Gate: deaths/game ≤ 130 vs fry-v14 and ouroboros;
  ≥ 8-18 combined vs them (not losing every matchup).
- **P2 economy**: bed model, ownership deconfliction, corpse mode,
  production schedule (§5). Gate: pearl ratio ≥ 1.5x opponents; beats
  fry-v14 head-to-head (≥ 16-10 of 26).
- **P3 roles & radio**: hand-off, status, gossip pack hunting, doom
  relay. Gate: ≥ parity vs kraken-v04 and leviathan-v07 on the full
  fixture; side-B record within 4 wins of side-A.
- **P4 endgame**: crown election, crown-kill, freeze schedule. Gate:
  length tiebreaks won ≥ 40% of length games vs the fixture.
- **P5 polish**: strike-propensity learning, map-type detection tuning,
  holdout validation, final sandbox audit.

Target: the finished bot should sit ≥ 240 pts in the five-bot fixture
(ouroboros-v05's 270 is the bar; 240 = clearly second, competitive first).

## 13. Open questions (explicit, not drift)

- Does a learned per-opponent p_strike beat the fixed (.75/.35/.15)? (P5)
- Is the doom report channel worth its sonar slot vs sightings? (A/B in P3)
- Optimal `crown_start` per map size: 200 (ouroboros) vs 340 (hydra-v03's
  freeze) — sweep in P4.
- When behind on a big map, is retreat-while-outnumbered net positive if
  gated on income parity? (v09 was +default −big_empty; the gate is the
  hypothesis.)

## 14. Addendum (2026-09-25): hunter-line evidence reshapes priorities

The user's hunter line (v14/v20, C++ ladder + encirclement traps + 6-ply
survival lookahead + five-tag radio) measured against the fixture on the
new 11-map set (see `docs/cross-line-review.md` §7):

- **hunter-v14 is the current strongest bot** (2.01 pts/g on shared
  opposition, 12-10 vs ouroboros-v05); v20 1.81; fry-v14 base 1.57.
- It wins by **churn + economy** (51-54% head-to-head death share,
  ~2:1 split ratio) — the opposite of ouroboros's low-death style. Two
  winning styles exist; P1's survival gate must not be read as "match
  ouroboros's death count" but as "don't lose addressable deaths": the
  hunter still gives away 36% of deaths to walls/self.
- **Length concentration is the confirmed #1 leak of the best non-crown
  bot**: v20/v14 lose ~30 games each on the round-500 longest-dragon
  tiebreak while WINNING total length (677 vs 607). This upgrades P4
  (crown) from "one phase among six" to the highest-value item in the
  plan: a crown bolted onto hunter-v14's economy would likely clear the
  whole field. Same conclusion, independent evidence: ouroboros (crown
  from r200) and kraken (length specialist) hold the top length records.
- **Within-line wins do not justify field regressions** (v20 13-9 over
  v19, then -0.2 pts/g vs the field): the promotion gate in §11 already
  requires the full fixture; the hunter line is the fresh proof.
- Richer radio ≠ better (v20's five tags vs v14's one tag, v14 ahead):
  every sonar slot needs a named consumer before it ships.
