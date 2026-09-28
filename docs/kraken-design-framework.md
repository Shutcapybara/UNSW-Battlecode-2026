# Kraken design framework

How kraken bots are designed, evaluated, and iterated. Read this before
changing any kraken bot. The tooling that operationalises this lives in
`tools/kraken/kbench.py`; the method below is what the tooling enforces.

## 1. The game, reduced to what matters

From `unswbc/engine/docs.md` and `unswbc/engine/src/scoring.cc`:

- **Snakes on a torus.** Move 1 step: free (tail follows unless a pearl is
  eaten). Sprint k steps: costs k-1 extra segments. Length L allows at most
  L-1 steps. Split n: rear n segments become a new dragon (child head = old
  tail); 64 units per team max; 500 rounds.
- **Combat is symmetric.** Head onto head kills BOTH dragons regardless of
  length. Head onto a body kills only the mover. So length is never a
  combat shield; combat value is purely positional — threat zones, who must
  move first, and trading up (a 2-segment stub killing a 20-segment dragon
  is the best exchange in the game).
- **Death recycles.** A dead dragon drops ceil(L/2) pearls along its body.
  Kills feed the local economy; dying where your gatherers can hoover the
  corpse is worth half a refund.
- **Win conditions.** Elimination, or at round 500 the team with the
  longest single dragon wins, ties broken by total length. Two completely
  different games: a *numbers/combat* game for 480 rounds, then a *length*
  game. Bots that confuse the two lose winnable matches (fry-v05's kamikaze
  habit) or get out-turtled (hydra-v03's crown insight).
- **Economy.** Pearls spawn on fixed fertile tiles with drawable countdowns
  (observable). Length is both health (sprint fuel, split fuel) and the
  endgame score. Splitting converts length into map coverage, parallel
  actions, and — critically — parallel CPU budgets (each dragon gets its
  own 100M points/turn; the swarm scales compute linearly).
- **Information.** Each dragon sees a 7x7 window plus edge rows; sonar is
  one ray per turn per dragon along its post-action facing, doubles as a
  one-value gossip channel to whatever dragon it hits; protocol 3 returns
  per-direction ECHO counts. The team knowledge is the union of 7x7
  windows relayed over sonar gossip — a distributed map with staleness.

## 2. The core loop

Every kraken dragon runs the same loop each turn:

```
SENSE      parse window -> fold into persistent world model
           (terrain edges, portal pairs, pearl beds + spawn predictions,
            remembered pearls, enemy sightings, ally self-reports)
DECIDE     in strict priority order:
           1. SPLIT   if production evaluation says the team needs units
           2. STRIKE  if a trade evaluation says a visible head is worth it
           3. MOVE    argmax over candidate steps of the move evaluation
           4. ESCAPE/EMERGENCY  fallbacks when the eval says all options die
ACT        emit action + one sonar (radar sweep + gossip carrier)
```

The decision layer is the product; SENSE and ACT are infrastructure and
should change only when the protocol or judge budget forces it.

## 3. Roles and specialisation

Roles are fixed at birth, encoded in split size (2=scout, 3=hunter,
larger=gatherer; map spawns are gatherers). A role is **not** separate
logic — it is a *parameter slice* of the same evaluation functions:

| role | risk tolerance | target weights | spread |
| --- | --- | --- | --- |
| scout (2) | trades vs enemies len >= mine+2 | frontier high, pearls low | max |
| hunter (3) | trades vs enemies len >= mine | sightings + radar rays high | mid |
| gatherer (4+) | never initiates (until endgame) | pearls + spawn predictions high | low |
| crown (endgame, planned) | refuses all trades | longest-dragon growth only | allies are shields |

Specialisation happens along four axes, all parameterised: trade margin,
target weight set, danger aversion, spread distance. New behaviours should
almost always be new parameter values or new *features*, not new branches.

## 4. Evaluation functions (the chess-bot layer)

Three scalar evaluations, each a weighted sum of features, each weight in
`CFG` so sweeps never touch logic:

- **Move eval** (per candidate step):
  `w_danger * lethal + w_soft * soft_threat + w_space * flood_space +
   trap_pen * (space < len) + w_pearl_here * pearl + w_compass * agrees_with_BFS
   + visit_score + w_spread * ally_distance + tiebreak_jitter`
- **Target eval** (BFS compass, per cell): `w_dist * steps + w_pearl *
  remembered + w_spawn * prediction_decay + w_frontier * unknown_border +
  w_hunt * sighting_heat + w_ray * radar_heat`
- **Production eval** (split): phase-scheduled team-size targets
  (early/mid/late × small/big map), child size encoding role; endgame
  freeze converts all income to crown length.
- **Trade eval** (strike): exchange value `their_len - my_len` gated by
  role margin, desperation (units <= 2), and phase (endgame only trades
  up; brawl mode trades anything not strictly shorter).

Design rules:

1. **Every tunable lives in `CFG`.** If a decision contains a number, the
   number is in `CFG` with a comment. Sweep tooling (`kbench variant`)
   rewrites only that dict.
2. **Features are pure functions of the world model.** No feature reads
   global decision state; that keeps them composable and testable.
3. **Judge budget is a hard constraint, not a feature.** p99 per-turn CPU
   must stay under ~70M in screening; a variant that wins and blows the
   budget is a loss, recorded as such.
4. **Fallbacks are rated X.** Escape/emergency paths exist so the eval's
   mistakes are survivable; a match where emergency paths fire a lot is a
   signal the eval is wrong, and the analyzer counts it.

## 5. The iteration loop

```
OBSERVE    kbench analyze <run-dir>     -> death causes, phase of losses,
                                           CPU safety, per-opponent splits
HYPOTHESIZE one sentence, one mechanism ("hunters suicide into body walls
            on portal maps because danger ignores portal exits")
ADAPT      kbench variant kraken-v04-eval my-hypo --set w_hunt=90 ...
SCREEN     kbench run screen --bots my-hypo      (~8 min, non-sandbox,
           4 maps x 3 opponents x both sides)  -> kill bad ideas fast
BENCHMARK  kbench run bench --bots my-hypo       (sandbox, fixed pool:
           fry-v03/v07/v09, hunter-v03, kraken-v03, hydra-v03)
PROMOTE    only if bench beats the baseline matchup AND CPU p99 < 70M;
           snapshot as kraken-vNN-name, commit with the numbers
REGRESS    full pool run (13 maps x pool) before believing any claim
```

Rules of the loop:

- One hypothesis per variant. Multi-change variants make results
  unattributable; if two ideas are both promising, run both separately.
- Never edit a bot that a running tournament has copied; variants are new
  directories.
- Screening is allowed to be non-sandbox (fast); every claimed win needs a
  sandbox confirmation. Wall-clock timeouts in Python mirrors are harness
  artifacts, not judge deaths — retry them at a longer timeout.
- Determinism cuts both ways: identical bots on identical maps replay
  identical games, so small sample sizes are meaningful for exact matchups
  but say nothing about generality. The full pool is the generality check.
- The standings number to beat is always the previous kraken's number
  against the *same* pool, never an absolute.

## 6. What the data said (v03 pool run, 520 matches, sandbox)

- 325W-3D-192L, 0 judge errors; worst CPU max 96.0M/100M (single match,
  `help`), worst p99 69.5M. Judge-safe.
- **73% of losses (141/192) are eliminations, median round 234** — a
  mid-game combat collapse, not an endgame scoring problem.
- Death mix in losses is dominated by `hit another dragon` and
  `lost a head-to-head` (~80% combined) — traffic and trades, not walls.
  Danger-map accuracy and trade discipline are the leverage, not
  pathfinding.
- Hardest matchups: fry-v07/fry-v09 (9W-17L; same code), fry-v12 (12-14),
  hunter-v01/v02 (12-14). All are swarm-of-equals bots that cap unit size
  at 4 and win the numbers war — mirroring hydra-v03's "stay a crowd of
  equals" insight, which kraken's role system concedes by feeding them
  2-3 segment children one at a time.

Open hypotheses for v04+, in priority order:

1. **Numbers war**: mid-phase team target scales too late; fry reaches 40+
   units while kraken sits at 28. Sweep `team_target_mid`, `hunter_until`.
2. **Trade discipline**: hunters trade 3-segment bodies into 4-segment
   fry units (even trade, but fry out-produces). Try `hunter_trade=1`.
3. **Endgame crown**: no designated non-splitting grower; round-limit
   losses (51) need a crown role that banks length early (round ~380).
"""
