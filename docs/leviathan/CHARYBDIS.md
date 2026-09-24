# Leviathan Charybdis: adversarial local games

The user requested a new family and new ideas, prioritizing exploration now
and reserving exploitation for phase end. Charybdis tests a chess-inspired
approach to local combat. It is a fresh policy, not a Riptide refinement or a
claim that a trained actor-critic exists.

## Identity and provenance

**`leviathan-x04-charybdis-replies`** is the only new source version.
The initial screen, no-search control and first judge run were snapshotted as
`leviathan-x03-charybdis-replies`; a concurrent Estuary fork occupied x03, so
Charybdis moved to x04. That rename changed no decision logic. Its first full
gauntlet and orientation runs already use x04.

Borrowed from Riptide x01: input parsing, observed terrain/portal geometry,
own-body history and food-memory helpers. The planner and production policy
are replaced. No Riptide beam, escape-capacity gate, colony funding test or
sonar protocol remains in the decision policy. Other lineages and shared
coordination documents are untouched.

## The new hypothesis

Riptide forecasts its own route against stationary bodies. Charybdis instead
constructs a small game in which both sides choose actions and can lose units.
The hypothesis is that explicitly anticipating an opponent's best reply makes
body blocking, forced trades and sacrifices available as deliberate decisions.

| Decision | Charybdis |
|---|---|
| Tactical state | Own dragon, nearest completely observed enemy within five graph steps, and their simulated children |
| Clock | Actual ascending ID order, wrapping into the next round; newborns act in their birth round |
| Actions | One/two-step movement, head collision, and two-segment split; configurable third sprint step |
| Transitions | Occupied tails collide before release; sprint payment precedes growth; head collisions kill both; dynamic carcasses drop alternate pearls |
| Opponent | Minimizes our local team value; friendly actors maximize it |
| Search | Three additional half-turns, alpha-beta pruning, ordered interior width six, equal nominal node allowance per root action |
| Economy | Per-unit production value plus material, with a timed-food/frontier routing field |
| Growth reserves | A deterministic hash designates about one in seven IDs as a grower; after round 90 and length six it stops splitting |
| Communication | None; local visible teammate positions discount food targets |

The local value includes material, a phase-dependent value per producer,
mobility, routing potential, a late quadratic length term, and a reach penalty
from enemies outside the selected duel. It can prefer losing a short dragon to
remove a more valuable enemy. Losing our last known unit has a large penalty.
There is no elected crown, feeding system, learned policy, or online training.

## What is exact, and what is approximate

The transition tests follow the checked-in engine in
`unswbc/engine/src/actions.cc`, `game.cc`, `pearls.cc`, and `protocol.cc`.
Newborn timing is particularly important: new IDs join the current round.
Scheduled observed beds tick at round boundaries and do not spawn under bodies.
Only confirmed current pearls fund the actual action.

This is not a complete game solver. One visible enemy is dynamic. Other dragons
are stationary obstacles with a separate head-reach penalty. Incomplete enemy
bodies are not assigned guessed tails or lengths; they remain outside the duel.
An enemy tail is considered complete only when its visible chain is continuous
and all possible incoming tail neighbours are observed. Unknown portal partners
stay blocked. Unknown terrain edges are blocked for both players: a modeled
trap may be false if the opponent can escape into unseen terrain. Future unseen
food and future random respawn intervals are not
invented. Static victims yield only observed-length credit and no invented
carcass pattern.

The enemy's population count is unavailable, so the local model allows up to
two simulated enemy births even if the real enemy may be at its population
limit. Our own observed population limit is enforced conservatively. Unmodeled
dragon movement, hidden bodies, teammate assistance and global terminal wins
can invalidate a local tactical prediction. Simulated newborn IDs preserve
relative turn order but cannot predict their actual future grower hash.
Move-width and expansion limits
can omit decisive replies. Generating candidate children adds work beyond
recursive node visits; `node_budget` is not an instruction counter. At most one
cutoff evaluation per root can overshoot its nominal allowance.

## Experiment design

The original prototype used `node_budget=1800`. Its judge run peaked at 99.8M
CPU points, too close to the 100M limit. The final default is **450**. This was
a compute correction; the strategic model and evaluation weights were frozen.
An intermediate 450-budget version still peaked at 94.9M because it counted
interior expansions but skipped leaf charges. The final version fixes that
accounting and tests leaf consumption explicitly. Both earlier implementations
remain in frozen run snapshots, not additional source folders.

The main causal control sets **`reply_plies=0`**. It preserves geometry, opponent
selection, scoring, production, growers and all root candidates, but selects
the immediate evaluation without searching replies. Its original 1800 budget
and old leaf-accounting code are unused when search is off. Each active search decision records
whether it changes the immediate evaluator's chosen action, and its explored
node count. Trace coverage is reported because engine indicator retention can
be capped.

- Discovery screen: arena, default_small, devil and default × Hunter v14,
  Hunter v20 and Leviathan v09 × both sides (24).
- G: all eleven original maps × the five ACTIVE references × both sides (110).
- Orientation check: transpose/flip of queen_of_spades, stronghold and trauma
  × Hunter v20/v09 × both sides (24). These maps were used by prior families;
  the reduced-budget check also follows the deeper prototype's use of them.
  It is validation, not globally untouched holdout data or full G+V.
- Judge: arena, big_empty and trauma × Hunter v20 × both sides (6).

Final results, controls, failure evidence and CPU are in
[CHARYBDIS_RESULTS.md](CHARYBDIS_RESULTS.md). Local deterministic fixtures are
not independent random samples. A weak result is preserved as evidence about
this hypothesis; exploration does not require promotion.

## Reproduction

```sh
python3 tools/leviathan/lab.py run leviathan-x04-charybdis-replies \
  --vs hunter-v14-cpp-hybrid-route-spacing hunter-v20-portal-scouts leviathan-v09-arrival \
  --maps arena,default_small,devil,default --jobs 4 \
  --cycle charybdis-1 --output build/leviathan/my-charybdis-screen

# Add --set reply_plies=0 for the control.
# The old prototype also used different budget accounting; use its saved source snapshot to reproduce it.
# Parameters modify private snapshots only; output folders must be new.
PYTHONPYCACHEPREFIX=/tmp/leviathan-pycache python3 -m unittest \
  discover -s tools/leviathan -p 'test_*.py'
```

Focused tests cover ID ordering in both directions, newborn turns, simultaneous
head deaths, tail occupancy, sprint funding, bed timing/occupancy, incomplete
enemy bodies, and a tactic where minimax rejects the greedy food move.
